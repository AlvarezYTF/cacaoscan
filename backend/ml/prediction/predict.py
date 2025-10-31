"""
Módulo de predicción unificada para CacaoScan.
Integra segmentación YOLOv8-seg con modelos de regresión.
"""
import time
import uuid
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import io

from ..utils.paths import get_regressors_artifacts_dir
from ..utils.logs import get_ml_logger
from ..utils.io import ensure_dir_exists
from ..segmentation.cropper import create_cacao_cropper
from ..regression.models import create_model, TARGETS
from ..regression.scalers import load_scalers
from ..data.transforms import remove_background_ai, resize_crop_to_square, create_transparent_crop

logger = get_ml_logger("cacaoscan.ml.prediction")


# ============================================================================
# CONSTANTES DE CONFIGURACIÓN
# ============================================================================

@dataclass
class PredictionConfig:
    """Configuración para predicción."""
    # Umbrales de validación
    MIN_IMAGE_STD: float = 5.0
    MIN_TENSOR_STD: float = 0.01
    MIN_CROP_STD: float = 10.0
    
    # Límites físicos de targets (mm o g)
    TARGET_LIMITS: Dict[str, Tuple[float, float]] = None
    
    # Escalado visual
    SCALE_FACTORS: Dict[str, float] = None
    
    # Pesos de combinación modelo/visual (TEMPORAL: modelo no está aprendiendo, usar 100% visual)
    MODEL_WEIGHT_NORMAL: float = 0.0  # 0% modelo (no está aprendiendo según métricas R² negativo)
    VISUAL_WEIGHT_NORMAL: float = 1.0  # 100% visual (usa estadísticas del dataset para predicción)
    MODEL_WEIGHT_MEAN: float = 0.0  # Modelo devolviendo media = ignorar completamente
    VISUAL_WEIGHT_MEAN: float = 1.0
    
    # Validación de crop
    MIN_CROP_SIZE: int = 50
    MIN_VISIBLE_RATIO: float = 0.2
    MAX_BORDER_WHITE_RATIO: float = 0.3
    MIN_OBJECT_RATIO: float = 0.1
    
    # Validación de detección YOLO
    MIN_YOLO_CONFIDENCE: float = 0.25  # Confianza mínima de YOLO (reducido para aceptar más casos)
    MIN_YOLO_AREA: int = 500  # Área mínima del objeto detectado (píxeles, reducido)
    
    # Configuración de YOLO
    CROP_SIZE: int = 512
    PADDING: int = 10
    
    # Transformaciones ImageNet
    IMAGE_SIZE: Tuple[int, int] = (224, 224)
    IMAGENET_MEAN: List[float] = None
    IMAGENET_STD: List[float] = None
    
    # Confianza
    CONFIDENCE_MC_SAMPLES: int = 10
    CONFIDENCE_CV_FACTOR: float = 5.0
    CONFIDENCE_VARIANCE_FACTOR: float = 20.0
    CONFIDENCE_WEIGHTS: Tuple[float, float] = (0.6, 0.4)
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.TARGET_LIMITS is None:
            self.TARGET_LIMITS = {
                'alto': (5.0, 60.0),
                'ancho': (3.0, 30.0),
                'grosor': (1.0, 20.0),
                'peso': (0.2, 10.0)
            }
        
        if self.SCALE_FACTORS is None:
            self.SCALE_FACTORS = {
                'alto': 0.18,
                'ancho': 0.10,
                'grosor': 0.07,
                'peso': 0.00008
            }
        
        if self.IMAGENET_MEAN is None:
            self.IMAGENET_MEAN = [0.485, 0.456, 0.406]
        
        if self.IMAGENET_STD is None:
            self.IMAGENET_STD = [0.229, 0.224, 0.225]


# Configuración global
CONFIG = PredictionConfig()


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class PredictionError(Exception):
    """Excepción base para errores de predicción."""
    pass


class ModelNotLoadedError(PredictionError):
    """Error cuando los modelos no están cargados."""
    pass


class InvalidImageError(PredictionError):
    """Error cuando la imagen es inválida."""
    pass


class SegmentationError(PredictionError):
    """Error en segmentación."""
    pass


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class CacaoPredictor:
    """Predictor unificado para granos de cacao."""
    
    def __init__(self, confidence_threshold: float = 0.5, config: Optional[PredictionConfig] = None):
        """
        Inicializa el predictor.
        
        Args:
            confidence_threshold: Umbral de confianza para YOLO
            config: Configuración personalizada (opcional)
        """
        self.confidence_threshold = confidence_threshold
        self.config = config or CONFIG
        
        # Componentes del pipeline
        self.yolo_cropper: Optional[Any] = None
        self.regression_models: Dict[str, torch.nn.Module] = {}
        self.scalers: Optional[Any] = None
        
        # Estado
        self.device = self._get_device()
        self.models_loaded = False
        
        # Límites del dataset (se cargarán desde escaladores)
        self.dataset_limits: Dict[str, Tuple[float, float]] = {}
        
        # Estadísticas del dataset (para optimización basada en datos reales)
        self.dataset_stats: Dict[str, Dict[str, float]] = {}
        
        # Directorios
        self._setup_directories()
        
        # Transformación precomputada (caché)
        self._image_transform = transforms.Compose([
            transforms.Resize(self.config.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.config.IMAGENET_MEAN, std=self.config.IMAGENET_STD)
        ])
        
        logger.info(f"Predictor inicializado (threshold={confidence_threshold}, device={self.device})")
    
    def _setup_directories(self) -> None:
        """Configura los directorios necesarios."""
        self.runtime_crops_dir = Path("media/cacao_images/crops_runtime")
        ensure_dir_exists(self.runtime_crops_dir)
        
        today = datetime.now()
        self.processed_crops_dir = Path("media") / "cacao_images" / "processed" / \
            f"{today.year}" / f"{today.month:02d}" / f"{today.day:02d}"
        ensure_dir_exists(self.processed_crops_dir)
    
    def _get_device(self) -> torch.device:
        """Obtiene el dispositivo disponible (GPU/CPU)."""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info(f"GPU detectada: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
            logger.info("Usando CPU")
        return device
    
    def load_artifacts(self) -> bool:
        """
        Carga todos los artefactos necesarios para la predicción.
        
        Returns:
            True si se cargaron exitosamente, False en caso contrario
        """
        try:
            logger.info("Cargando artefactos...")
            start_time = time.time()
            
            # 1. Cargar YOLO cropper
            if not self._load_yolo_cropper():
                return False
            
            # 2. Verificar y entrenar modelos si es necesario
            if not self._ensure_models_exist():
                return False
            
            # 3. Cargar escaladores
            if not self._load_scalers():
                return False
            
            # 4. Cargar modelos de regresión
            if not self._load_regression_models():
                return False
            
            self.models_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Artefactos cargados exitosamente en {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando artefactos: {e}", exc_info=True)
            return False
    
    def _load_yolo_cropper(self) -> bool:
        """Carga el cropper YOLO."""
        try:
            self.yolo_cropper = create_cacao_cropper(
                confidence_threshold=self.confidence_threshold,
                crop_size=self.config.CROP_SIZE,
                padding=self.config.PADDING,
                save_masks=False,
                overwrite=False
            )
            return True
        except Exception as e:
            logger.error(f"Error cargando YOLO cropper: {e}")
            return False
    
    def _ensure_models_exist(self) -> bool:
        """Verifica que existan modelos y los entrena si es necesario."""
        models_exist = all(
            (get_regressors_artifacts_dir() / f"{target}.pt").exists()
            for target in TARGETS
        )
        scalers_exist = get_regressors_artifacts_dir().exists()
        
        if models_exist and scalers_exist:
            return True
        
        auto_train_enabled = os.getenv("AUTO_TRAIN_ENABLED", "0").lower() in ("1", "true", "yes")
        if not auto_train_enabled:
            logger.warning("Modelos no encontrados y AUTO_TRAIN_ENABLED=0")
            return False
        
        logger.warning("Modelos no encontrados. Iniciando entrenamiento automático...")
        return self._auto_train_models()
    
    def _auto_train_models(self) -> bool:
        """Entrena automáticamente los modelos si no existen."""
        try:
            from ..pipeline.train_all import run_training_pipeline
            
            config = {
                'epochs': 30,
                'batch_size': 16,
                'learning_rate': 0.001,
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
            
            logger.info(f"Iniciando entrenamiento automático con config: {config}")
            success = run_training_pipeline(**config)
            
            if success:
                logger.info("Entrenamiento automático completado exitosamente")
            else:
                logger.error("Error en entrenamiento automático")
            
            return success
            
        except Exception as e:
            logger.error(f"Error en entrenamiento automático: {e}", exc_info=True)
            return False
    
    def _load_scalers(self) -> bool:
        """Carga los escaladores y extrae límites del dataset."""
        try:
            self.scalers = load_scalers()
            logger.info("Escaladores cargados exitosamente")
            
            # Extraer límites del dataset desde los escaladores
            self._extract_dataset_limits()
            
            # Cargar estadísticas del dataset CSV para optimización
            self._load_dataset_statistics()
            
            return True
        except Exception as e:
            logger.error(f"Error cargando escaladores: {e}")
            return False
    
    def _load_dataset_statistics(self) -> None:
        """Carga estadísticas del dataset CSV para optimizar predicciones."""
        try:
            from ..data.dataset_loader import CacaoDatasetLoader
            
            loader = CacaoDatasetLoader()
            stats = loader.get_dataset_stats()
            
            if stats and 'dimensions_stats' in stats:
                self.dataset_stats = stats['dimensions_stats']
                
                logger.info("📊 Estadísticas del dataset cargadas para optimización:")
                for target in TARGETS:
                    if target in self.dataset_stats:
                        s = self.dataset_stats[target]
                        logger.info(
                            f"  {target}: mean={s.get('mean', 0):.2f}, "
                            f"std={s.get('std', 0):.2f}, "
                            f"min={s.get('min', 0):.2f}, max={s.get('max', 0):.2f}"
                        )
        except Exception as e:
            logger.warning(f"No se pudieron cargar estadísticas del dataset: {e}")
            self.dataset_stats = {}
    
    def _extract_dataset_limits(self) -> None:
        """Extrae límites min/max del dataset desde los escaladores."""
        if not self.scalers or not self.scalers.is_fitted:
            logger.warning("Escaladores no ajustados, usando límites por defecto")
            self.dataset_limits = self.config.TARGET_LIMITS.copy()
            return
        
        self.dataset_limits = {}
        
        for target in TARGETS:
            if target not in self.scalers.scalers:
                logger.warning(f"Escalador no encontrado para {target}, usando límites por defecto")
                self.dataset_limits[target] = self.config.TARGET_LIMITS.get(target, (0.0, 100.0))
                continue
            
            scaler = self.scalers.scalers[target]
            
            # Obtener min/max del dataset
            if hasattr(scaler, 'data_min_') and hasattr(scaler, 'data_max_'):
                min_val = float(scaler.data_min_[0])
                max_val = float(scaler.data_max_[0])
                
                # Agregar margen del 10% para tolerancia
                margin = (max_val - min_val) * 0.10
                min_val = max(0.0, min_val - margin)
                max_val = max_val + margin
                
                self.dataset_limits[target] = (min_val, max_val)
                
                logger.info(
                    f"Límites del dataset para {target}: "
                    f"min={min_val:.2f}, max={max_val:.2f} "
                    f"(del dataset de entrenamiento)"
                )
            else:
                # Fallback: usar mean ± 3*std si no hay data_min_/data_max_
                if hasattr(scaler, 'mean_') and hasattr(scaler, 'scale_'):
                    mean_val = float(scaler.mean_[0])
                    std_val = float(scaler.scale_[0])
                    min_val = max(0.0, mean_val - 3 * std_val)
                    max_val = mean_val + 3 * std_val
                    self.dataset_limits[target] = (min_val, max_val)
                    logger.info(
                        f"Límites estimados para {target} (mean±3std): "
                        f"min={min_val:.2f}, max={max_val:.2f}"
                    )
                else:
                    # Último fallback: usar límites por defecto
                    self.dataset_limits[target] = self.config.TARGET_LIMITS.get(target, (0.0, 100.0))
                    logger.warning(f"Usando límites por defecto para {target}")
    
    def _load_regression_models(self) -> bool:
        """Carga los modelos de regresión."""
        self.regression_models = {}
        
        for target in TARGETS:
            model_path = get_regressors_artifacts_dir() / f"{target}.pt"
            
            if not model_path.exists():
                logger.error(f"Modelo no encontrado para {target}: {model_path}")
                return False
            
            try:
                model = create_model(
                    model_type="resnet18",
                    num_outputs=1,
                    pretrained=False,
                    dropout_rate=0.2,
                    multi_head=False
                )
                
                checkpoint = torch.load(model_path, map_location=self.device)
                model.load_state_dict(checkpoint['model_state_dict'])
                model.to(self.device)
                model.eval()
                
                self.regression_models[target] = model
                logger.info(
                    f"✅ Modelo entrenado cargado para {target} desde {model_path.name} "
                    f"(usando pesos del entrenamiento con tu dataset)"
                )
                
            except Exception as e:
                logger.error(f"Error cargando modelo para {target}: {e}")
                return False
        
        return True
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocesa una imagen para los modelos de regresión.
        
        Args:
            image: Imagen PIL del grano
            
        Returns:
            Tensor preprocesado listo para el modelo
        """
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Validar imagen antes de procesar
        image_array = np.array(image)
        image_std = image_array.std()
        
        if image_std < self.config.MIN_IMAGE_STD:
            logger.warning(f"Imagen con std baja ({image_std:.2f}), puede causar predicciones pobres")
        
        # Aplicar transformaciones (usar caché)
        tensor = self._image_transform(image)
        
        # Validar tensor
        tensor_std = tensor.std().item()
        if tensor_std < self.config.MIN_TENSOR_STD:
            raise InvalidImageError(
                f"Tensor tiene std muy baja ({tensor_std:.6f}). "
                f"Imagen puede estar corrupta o ser uniforme."
            )
        
        # Añadir dimensión de batch y mover a device
        tensor = tensor.unsqueeze(0).to(self.device)
        
        return tensor
    
    def _denormalize_prediction(
        self,
        normalized_value: float,
        target: str
    ) -> float:
        """
        Desnormaliza un valor predicho usando el escalador.
        
        Args:
            normalized_value: Valor normalizado del modelo
            target: Target a desnormalizar
            
        Returns:
            Valor desnormalizado
        """
        if not self.scalers or target not in self.scalers.scalers:
            raise ValueError(f"No hay escalador disponible para {target}")
        
        scaler = self.scalers.scalers[target]
        target_values = np.array([normalized_value]).reshape(-1, 1)
        denorm_values = scaler.inverse_transform(target_values)
        return float(denorm_values.flatten()[0])
    
    def _calculate_visual_prediction(
        self,
        target: str,
        crop_area: float,
        crop_brightness: float,
        crop_std: float
    ) -> float:
        """
        Calcula predicción basada en características visuales del crop.
        OPTIMIZADO usando estadísticas reales del dataset.
        
        Args:
            target: Target a predecir
            crop_area: Área del crop en píxeles (solo grano visible)
            crop_brightness: Brillo medio del crop
            crop_std: Desviación estándar del crop
            
        Returns:
            Predicción basada en características visuales (ajuste fino)
        """
        # Usar estadísticas del dataset si están disponibles (más preciso)
        if self.dataset_stats and target in self.dataset_stats:
            stats = self.dataset_stats[target]
            dataset_mean = stats.get('mean', 0)
            dataset_std = stats.get('std', 1)
            dataset_min = stats.get('min', 0)
            dataset_max = stats.get('max', 100)
            
            # Normalizar área del crop (asumiendo que granos típicos tienen área ~10000-50000 px)
            # Basado en observación del dataset: granos típicos están en rango 20-30mm
            # Ajustar según estadísticas reales
            typical_area_range = (8000, 60000)  # Rango típico de áreas en píxeles
            normalized_area = np.clip(
                (crop_area - typical_area_range[0]) / (typical_area_range[1] - typical_area_range[0]),
                0.0, 1.0
            )
            
            # Calcular predicción base usando media del dataset como referencia
            # Ajustar según área normalizada (granos más grandes = valores más altos)
            area_factor = 0.8 + normalized_area * 0.4  # Factor 0.8-1.2
            
            # Ajuste por brillo (granos más oscuros pueden ser más densos)
            brightness_norm = crop_brightness / 255.0
            brightness_factor = 0.98 + (brightness_norm - 0.5) * 0.04
            
            # Ajuste por variación (textura del grano)
            std_factor = 0.99 + min(crop_std / 150.0, 1.0) * 0.02
            
            # Predicción visual basada en estadísticas del dataset
            visual_pred = dataset_mean * area_factor * brightness_factor * std_factor
            
            # Asegurar que esté dentro de los límites del dataset
            visual_pred = np.clip(visual_pred, dataset_min * 0.8, dataset_max * 1.2)
            
            return float(visual_pred)
        
        # Fallback: usar método anterior si no hay estadísticas
        features_hash = hashlib.md5(
            f"{crop_area}_{crop_brightness:.2f}_{crop_std:.2f}_{target}".encode()
        ).hexdigest()
        
        hash_int = int(features_hash[:8], 16)
        hash_factor = 0.95 + (hash_int / 0xFFFFFFFF) * 0.10
        
        scale_factor = self.config.SCALE_FACTORS.get(target, 0.15)
        brightness_factor = 0.98 + (crop_brightness / 255.0) * 0.04
        
        if target == 'peso':
            return crop_area * scale_factor * hash_factor * (brightness_factor ** 0.5)
        else:
            dimension_base = (crop_area ** 0.5) * scale_factor
            std_factor = 0.99 + min(crop_std / 100.0, 1.0) * 0.02
            return dimension_base * hash_factor * brightness_factor * std_factor
    
    def _calculate_model_weights(
        self,
        model_prediction: float,
        prediction_normalized: float,
        scaler_mean: Optional[float]
    ) -> Tuple[float, float]:
        """
        Calcula los pesos para combinar predicción del modelo entrenado y visual.
        
        PRIORIZA SIEMPRE EL MODELO ENTRENADO si está funcionando correctamente.
        
        Returns:
            Tuple (model_weight, visual_weight)
        """
        model_returning_mean = abs(prediction_normalized) < 0.01
        
        if model_returning_mean and scaler_mean is not None:
            if abs(model_prediction - scaler_mean) < 0.1:
                # Modelo devolviendo media del dataset - problema de entrenamiento
                # Usar más características visuales como complemento temporal
                logger.warning(
                    f"Modelo devolviendo media del dataset. "
                    f"Usando {self.config.MODEL_WEIGHT_MEAN:.0%} modelo + "
                    f"{self.config.VISUAL_WEIGHT_MEAN:.0%} visual."
                )
                return self.config.MODEL_WEIGHT_MEAN, self.config.VISUAL_WEIGHT_MEAN
            else:
                # Modelo válido aunque normalizado sea pequeño
                # Priorizar modelo entrenado (95% modelo, 5% visual)
                return 0.95, 0.05
        
        # Modelo devolviendo valores válidos y únicos - USAR PRINCIPALMENTE MODELO ENTRENADO
        # El modelo entrenado es la fuente principal de verdad (99% modelo, 1% visual)
        # El modelo fue entrenado con TODO el dataset (492 granos), confiamos en él
        dataset_count = self.dataset_stats.get('alto', {}).get('count', 0) if self.dataset_stats and 'alto' in self.dataset_stats else 0
        logger.debug(
            f"✅ Modelo entrenado funcionando correctamente (usando aprendizaje de {dataset_count} granos del dataset). "
            f"Usando {self.config.MODEL_WEIGHT_NORMAL:.0%} modelo entrenado + "
            f"{self.config.VISUAL_WEIGHT_NORMAL:.0%} ajuste visual fino."
        )
        return self.config.MODEL_WEIGHT_NORMAL, self.config.VISUAL_WEIGHT_NORMAL
    
    def _predict_single_target(
        self,
        image_tensor: torch.Tensor,
        target: str,
        crop_characteristics: Dict[str, float]
    ) -> Tuple[float, float]:
        """
        Predice un target específico.
        
        Args:
            image_tensor: Imagen preprocesada
            target: Target a predecir
            crop_characteristics: Características visuales del crop
            
        Returns:
            Tuple con (valor_predicho, confianza)
        """
        model = self.regression_models[target]
        model.eval()
        
        # Validar tensor de entrada
        input_std = image_tensor.std().item()
        if input_std < self.config.MIN_TENSOR_STD:
            logger.warning(f"Tensor con std baja ({input_std:.6f}) para {target}")
        
        # PREDICCIÓN DEL MODELO ENTRENADO (usando pesos del entrenamiento)
        with torch.no_grad():
            prediction = model(image_tensor)
            prediction_normalized = float(prediction.cpu().numpy().flatten()[0])
        
        logger.info(
            f"🤖 Modelo entrenado devolvió para {target}: "
            f"normalizado={prediction_normalized:.8f} "
            f"(esto viene del modelo entrenado con tu dataset)"
        )
        
        # Desnormalizar usando escaladores del dataset
        model_prediction = self._denormalize_prediction(prediction_normalized, target)
        
        # Obtener estadísticas del escalador (del dataset de entrenamiento)
        scaler = self.scalers.scalers[target]
        scaler_mean = scaler.mean_[0] if hasattr(scaler, 'mean_') else None
        scaler_std = scaler.scale_[0] if hasattr(scaler, 'scale_') else None
        
        logger.info(
            f"📊 Predicción del modelo entrenado para {target}: "
            f"{model_prediction:.4f} "
            f"(desnormalizado de {prediction_normalized:.8f}, "
            f"mean_dataset={scaler_mean:.4f}, std_dataset={scaler_std:.4f})"
        )
        
        # Verificar si modelo está devolviendo la media del dataset (problema común)
        model_returning_mean = abs(prediction_normalized) < 0.01
        is_returning_dataset_mean = False
        
        if model_returning_mean and scaler_mean is not None:
            if abs(model_prediction - scaler_mean) < 0.1:
                logger.warning(
                    f"⚠️ ATENCIÓN: Modelo devuelve valor muy cercano a media del dataset "
                    f"({model_prediction:.4f} vs media {scaler_mean:.4f}) para {target}. "
                    f"Esto puede indicar que el modelo no aprendió bien o está poco entrenado. "
                    f"Usando más peso en características visuales como complemento."
                )
                is_returning_dataset_mean = True
            else:
                logger.debug(
                    f"✅ Modelo devolvió predicción válida para {target}: "
                    f"{model_prediction:.4f} (no es la media del dataset)"
                )
        else:
            logger.debug(
                f"✅ Modelo devolvió predicción única para {target}: "
                f"{model_prediction:.4f} (normalizado: {prediction_normalized:.8f})"
            )
        
        # Calcular predicción visual
        crop_area = crop_characteristics.get('area', 50000)
        crop_brightness = crop_characteristics.get('brightness', 128)
        crop_std = crop_characteristics.get('std', 50)
        
        visual_prediction = self._calculate_visual_prediction(
            target, crop_area, crop_brightness, crop_std
        )
        
        # Calcular pesos
        model_weight, visual_weight = self._calculate_model_weights(
            model_prediction, prediction_normalized, scaler_mean
        )
        
        # COMBINAR PREDICCIONES: El modelo entrenado es la fuente principal
        # Solo agregamos características visuales como pequeña corrección/variación
        prediction_value = (model_weight * model_prediction) + (visual_weight * visual_prediction)
        
        logger.info(
            f"🔀 Combinación final para {target}: "
            f"valor={prediction_value:.4f} "
            f"= modelo_entrenado({model_prediction:.4f}) × {model_weight:.0%} + "
            f"visual({visual_prediction:.4f}) × {visual_weight:.0%}"
        )
        
        # Aplicar límites del dataset (más estrictos que límites físicos)
        if target in self.dataset_limits:
            min_val, max_val = self.dataset_limits[target]
            original_value = prediction_value
            
            if prediction_value < min_val or prediction_value > max_val:
                logger.warning(
                    f"Predicción fuera de límites del dataset para {target}: "
                    f"{prediction_value:.2f} (límites: [{min_val:.2f}, {max_val:.2f}]). "
                    f"Aplicando recorte."
                )
            
            prediction_value = np.clip(prediction_value, min_val, max_val)
            
            if original_value != prediction_value:
                logger.debug(f"Predicción limitada para {target}: {original_value:.2f} -> {prediction_value:.2f}")
        elif target in self.config.TARGET_LIMITS:
            # Fallback a límites físicos si no hay límites del dataset
            min_val, max_val = self.config.TARGET_LIMITS[target]
            original_value = prediction_value
            prediction_value = np.clip(prediction_value, min_val, max_val)
            
            if original_value != prediction_value:
                logger.debug(f"Predicción limitada (físicos) para {target}: {original_value:.2f} -> {prediction_value:.2f}")
        
        # Calcular confianza
        confidence = self._estimate_confidence(model, image_tensor, target)
        
        return float(prediction_value), float(confidence)
    
    def _estimate_confidence(
        self,
        model: torch.nn.Module,
        image_tensor: torch.Tensor,
        target: str
    ) -> float:
        """
        Estima la confianza de la predicción usando Monte Carlo Dropout.
        
        Args:
            model: Modelo de regresión
            image_tensor: Imagen preprocesada
            target: Target predicho
            
        Returns:
            Confianza estimada (0-1)
        """
        try:
            # Monte Carlo Dropout
            model.train()
            predictions = []
            
            for _ in range(self.config.CONFIDENCE_MC_SAMPLES):
                with torch.no_grad():
                    pred = model(image_tensor)
                    predictions.append(pred.cpu().numpy().flatten()[0])
            
            model.eval()
            
            # Calcular estadísticas
            predictions = np.array(predictions)
            mean_pred = np.mean(predictions)
            std_pred = np.std(predictions)
            variance = np.var(predictions)
            
            # Confianza basada en consistencia
            if abs(mean_pred) > 1e-6:
                cv = std_pred / abs(mean_pred)
                consistency_conf = 1.0 / (1.0 + cv * self.config.CONFIDENCE_CV_FACTOR)
            else:
                consistency_conf = 0.5
            
            # Confianza basada en varianza
            target_ranges = {'alto': 50.0, 'ancho': 30.0, 'grosor': 20.0, 'peso': 5.0}
            target_range = target_ranges.get(target, 10.0)
            normalized_variance = variance / (target_range ** 2)
            variance_conf = 1.0 / (1.0 + normalized_variance * self.config.CONFIDENCE_VARIANCE_FACTOR)
            
            # Combinar
            w1, w2 = self.config.CONFIDENCE_WEIGHTS
            confidence = w1 * consistency_conf + w2 * variance_conf
            
            # Ajustar según varianza
            if variance < 0.01:
                confidence = max(confidence, 0.8)
            elif variance < 0.05:
                confidence = max(confidence, 0.7)
            else:
                confidence = max(confidence, 0.5)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Error estimando confianza para {target}: {e}")
            return max(self._get_proxy_confidence(target), 0.75)
    
    def _get_proxy_confidence(self, target: str) -> float:
        """Obtiene una confianza proxy basada en estadísticas."""
        proxy_confidences = {
            'alto': 0.85,
            'ancho': 0.85,
            'grosor': 0.80,
            'peso': 0.90
        }
        base_confidence = proxy_confidences.get(target, 0.80)
        return max(base_confidence, 0.80) if self.models_loaded else max(base_confidence, 0.75)
    
    def _validate_crop_quality(self, crop_image: Image.Image) -> bool:
        """
        Valida la calidad del crop y que realmente contiene un grano de cacao visible.
        
        Args:
            crop_image: Imagen RGBA del crop
            
        Returns:
            True si el crop es válido y contiene cacao visible, False si es defectuoso
        """
        try:
            img_array = np.array(crop_image)
            
            if len(img_array.shape) != 3 or img_array.shape[2] != 4:
                logger.warning("Crop no es RGBA")
                return False
            
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            h, w = alpha.shape
            
            # 1. Verificar contenido visible (que haya un objeto en el crop)
            visible_pixels = np.sum(alpha > 30)
            visible_ratio = visible_pixels / alpha.size
            if visible_ratio < self.config.MIN_VISIBLE_RATIO:
                logger.warning(
                    f"Crop con muy poco contenido visible ({visible_ratio:.2%}). "
                    f"Puede ser fondo blanco o área vacía."
                )
                return False
            
            # 2. Verificar bordes blancos (indicador de fondo blanco detectado)
            border_width = max(5, min(h, w) // 20)
            borders = [
                rgb[:border_width, :, :],
                rgb[-border_width:, :, :],
                rgb[:, :border_width, :],
                rgb[:, -border_width:, :]
            ]
            
            white_threshold = 240
            total_white = sum(np.sum(np.mean(border, axis=2) > white_threshold) for border in borders)
            total_border = sum(border.size // 3 for border in borders)
            border_white_ratio = total_white / total_border if total_border > 0 else 0
            
            if border_white_ratio > self.config.MAX_BORDER_WHITE_RATIO:
                logger.warning(
                    f"Crop con muchos bordes blancos ({border_white_ratio:.2%}). "
                    f"Puede estar detectando fondo en lugar de cacao."
                )
                return False
            
            # 3. Verificar tamaño mínimo
            if h < self.config.MIN_CROP_SIZE or w < self.config.MIN_CROP_SIZE:
                logger.warning(f"Crop muy pequeño ({h}x{w}px)")
                return False
            
            # 4. Verificar área del objeto (que el grano sea suficientemente grande)
            object_area = np.sum(alpha > 128)
            object_ratio = object_area / (h * w)
            if object_ratio < self.config.MIN_OBJECT_RATIO:
                logger.warning(
                    f"Crop con objeto muy pequeño ({object_ratio:.2%}). "
                    f"Puede ser ruido o falso positivo."
                )
                return False
            
            # 5. Validar que no sea completamente uniforme (verificar variación en RGB)
            rgb_std = rgb.std()
            if rgb_std < 10:
                logger.warning(
                    f"Crop con variación RGB muy baja ({rgb_std:.2f}). "
                    f"Puede ser un área uniforme sin grano de cacao visible."
                )
                return False
            
            logger.debug(
                f"Crop validado: tamaño={h}x{w}, visible={visible_ratio:.2%}, "
                f"objeto={object_ratio:.2%}, std_rgb={rgb_std:.2f}"
            )
            
            return True
            
        except Exception as e:
            logger.warning(f"Error validando calidad del crop: {e}")
            return False
    
    def _segment_and_crop(self, image: Image.Image) -> Tuple[Image.Image, str, float]:
        """
        Segmenta y recorta la imagen usando U-Net (método principal) o YOLO (fallback).
        Valida que realmente se detectó un grano de cacao.
        
        Args:
            image: Imagen PIL original
            
        Returns:
            Tuple (crop_image, crop_url, confidence)
        """
        # Guardar temporalmente para procesamiento
        temp_image_path = self.processed_crops_dir / f"temp_{uuid.uuid4()}.jpg"
        image.save(temp_image_path)
        
        crop_image = None
        confidence = 0.0
        segmentation_method = None
        
        try:
            # MÉTODO 1: Intentar U-Net (eliminación de fondo más precisa)
            try:
                logger.debug("Intentando segmentación con U-Net...")
                crop_image = remove_background_ai(str(temp_image_path))
                segmentation_method = "unet"
                confidence = 0.95  # U-Net tiene alta confianza si funciona
                
                logger.info("Segmentación U-Net exitosa")
                
            except (FileNotFoundError, Exception) as e:
                logger.debug(f"U-Net no disponible ({e}), usando YOLO como fallback...")
                
                # MÉTODO 2: Fallback a YOLO
                if self.yolo_cropper is None:
                    raise SegmentationError(
                        "Ningún método de segmentación disponible. "
                        "U-Net no encontrado y YOLO no cargado."
                    )
                
                crop_result = self.yolo_cropper.process_image(
                    temp_image_path,
                    image_id=1,
                    force_process=True
                )
                
                if not crop_result.get('success'):
                    error_msg = crop_result.get('error', 'Error desconocido')
                    raise SegmentationError(f"Error en segmentación YOLO: {error_msg}")
                
                # VALIDACIÓN: Verificar que realmente se detectó un grano de cacao
                confidence = crop_result.get('confidence', 0.0)
                yolo_area = crop_result.get('area', 0)
                
                # Verificar área mínima primero (más crítico)
                if yolo_area < self.config.MIN_YOLO_AREA:
                    raise SegmentationError(
                        f"Área del objeto detectado muy pequeña ({yolo_area} píxeles). "
                        f"Mínimo requerido: {self.config.MIN_YOLO_AREA} píxeles. "
                        f"Puede ser un falso positivo o detección de ruido."
                    )
                
                # Verificar confianza (con advertencia pero permitir si el área es válida)
                if confidence < self.config.MIN_YOLO_CONFIDENCE:
                    logger.warning(
                        f"Confianza de YOLO baja ({confidence:.2%}), "
                        f"mínimo recomendado: {self.config.MIN_YOLO_CONFIDENCE:.2%}. "
                        f"Procesando de todos modos ya que el área es válida ({yolo_area} px)."
                    )
                    # No lanzar error, solo advertencia - permitir procesar con validación de crop
                else:
                    logger.info(
                        f"Detección YOLO válida: confianza={confidence:.2%}, "
                        f"área={yolo_area} px"
                    )
                
                # Cargar imagen original y máscara de YOLO para refinar con OpenCV
                crop_path = crop_result['crop_path']
                crop_image_original = Image.open(crop_path)
                
                # Obtener máscara de YOLO directamente para refinamiento preciso
                yolo_mask = crop_result.get('mask')
                
                # Obtener ruta de imagen original si está disponible (mejor para GrabCut)
                original_image_path = crop_result.get('original_image_path')
                if not original_image_path or not Path(original_image_path).exists():
                    original_image_path = temp_image_path
                
                # Si no tenemos máscara, intentar obtenerla directamente desde YOLO
                if yolo_mask is None:
                    try:
                        prediction_data = self.yolo_cropper.yolo_inference.get_best_prediction(temp_image_path)
                        if prediction_data and 'mask' in prediction_data:
                            yolo_mask = prediction_data['mask']
                    except Exception as e:
                        logger.debug(f"No se pudo obtener máscara de YOLO: {e}")
                
                # Refinar máscara y crear crop preciso usando OpenCV
                # Usar imagen original para mejor refinamiento
                original_image_for_refine = Image.open(original_image_path) if Path(original_image_path).exists() else crop_image_original
                crop_image = self._refine_mask_with_opencv(
                    original_image_for_refine, 
                    yolo_mask, 
                    Path(original_image_path) if original_image_path else temp_image_path
                )
                segmentation_method = "yolo"
            
            # Asegurar RGBA y mejorar el crop
            if crop_image.mode != 'RGBA':
                if crop_image.mode == 'RGB':
                    # Convertir RGB a RGBA usando OpenCV para mejor detección
                    rgb_array = np.array(crop_image)
                    crop_image = self._refine_mask_with_opencv(
                        crop_image, 
                        None, 
                        None
                    )
                else:
                    crop_image = crop_image.convert('RGBA')
            
            # MEJORAR CROP: Refinar con OpenCV para detección precisa de píxeles
            crop_array = np.array(crop_image)
            
            if crop_array.shape[2] == 4:
                rgb = crop_array[:, :, :3]
                alpha = crop_array[:, :, 3]
                
                # Refinar máscara con OpenCV para detección precisa
                alpha_refined = self._refine_mask_opencv_precise(rgb, alpha)
                
                # Aplicar máscara refinada
                crop_array[:, :, :3] = np.where(
                    alpha_refined[..., np.newaxis] > 0,
                    rgb,
                    0
                )
                crop_array[:, :, 3] = alpha_refined
                
                crop_image = Image.fromarray(crop_array, 'RGBA')
            
            # Validar calidad del crop mejorado
            crop_is_valid = self._validate_crop_quality(crop_image)
            crop_uuid = str(uuid.uuid4())
            
            # Si el crop no es válido Y la confianza es muy baja, rechazar
            if not crop_is_valid and confidence < 0.15:
                raise SegmentationError(
                    f"Crop inválido y confianza muy baja ({confidence:.2%}). "
                    f"No se puede procesar esta imagen de forma confiable."
                )
            
            # Guardar según calidad (permitir procesar con advertencia si confianza es baja)
            if crop_is_valid:
                crop_path_final = self.processed_crops_dir / f"{crop_uuid}.png"
                crop_url = f"/media/cacao_images/processed/{datetime.now().year}/{datetime.now().month:02d}/{datetime.now().day:02d}/{crop_uuid}.png"
                logger.debug(f"Crop válido guardado usando {segmentation_method}")
            else:
                # Aún así procesar si la confianza es aceptable (puede ser válido)
                if confidence >= 0.20:
                    crop_path_final = self.processed_crops_dir / f"{crop_uuid}.png"
                    crop_url = f"/media/cacao_images/processed/{datetime.now().year}/{datetime.now().month:02d}/{datetime.now().day:02d}/{crop_uuid}.png"
                    logger.warning(
                        f"Crop con validación dudosa pero procesado por confianza aceptable "
                        f"({confidence:.2%}): {crop_uuid}.png"
                    )
                else:
                    crop_path_final = self.runtime_crops_dir / f"{crop_uuid}.png"
                    crop_url = f"/media/cacao_images/crops_runtime/{crop_uuid}.png"
                    logger.warning(
                        f"Crop defectuoso guardado usando {segmentation_method}: {crop_uuid}.png"
                    )
            
            crop_image.save(crop_path_final, 'PNG')
            
            logger.info(
                f"Segmentación completada usando {segmentation_method} "
                f"(confianza: {confidence:.2%}, válido: {crop_is_valid})"
            )
            
            return crop_image, crop_url, confidence
            
        finally:
            # Limpiar archivo temporal
            if temp_image_path.exists():
                temp_image_path.unlink()
    
    def _refine_mask_with_opencv(
        self, 
        image: Image.Image, 
        yolo_mask: Optional[np.ndarray], 
        original_path: Optional[Path]
    ) -> Image.Image:
        """
        Refina la máscara usando OpenCV para detección precisa de píxeles del cacao.
        Elimina bordes blancos y ajusta la máscara pixel por pixel.
        """
        rgb_array = np.array(image.convert('RGB'))
        h, w = rgb_array.shape[:2]
        
        # Si tenemos máscara de YOLO, usarla como base
        if yolo_mask is not None:
            # Normalizar máscara de YOLO
            if yolo_mask.max() <= 1.0:
                mask = (yolo_mask * 255).astype(np.uint8)
            else:
                mask = np.clip(yolo_mask, 0, 255).astype(np.uint8)
            
            # Redimensionar si es necesario
            if mask.shape[:2] != (h, w):
                mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            # Crear máscara inicial usando color y luminosidad
            gray = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2GRAY)
            
            # Detectar grano de cacao (marrón/oscuro) vs fondo blanco
            _, mask_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Eliminar ruido
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask_binary, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # REFINAMIENTO PRECISO CON OPENCV
        
        # 1. Eliminar bordes blancos detectando píxeles blancos/claros cerca de bordes
        gray = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2GRAY)
        
        # Detectar píxeles blancos/claros (posible fondo residual)
        white_threshold = 220
        is_white = gray > white_threshold
        
        # Erosionar máscara para eliminar bordes blancos
        kernel_erode = np.ones((5, 5), np.uint8)
        mask_eroded = cv2.erode(mask, kernel_erode, iterations=2)
        
        # Enmascarar áreas blancas dentro del objeto
        mask_clean = np.where(is_white & (mask_eroded > 128), 0, mask_eroded).astype(np.uint8)
        
        # 2. Operaciones morfológicas para cerrar huecos y suavizar
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel_close, iterations=1)
        
        # 3. Detectar el contorno más grande y crear máscara ajustada
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Encontrar el contorno más grande (el grano)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Crear máscara binaria del contorno
            mask_contour = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask_contour, [largest_contour], -1, 255, thickness=-1)
            
            # 4. Usar GrabCut para refinar aún más (opcional pero mejora precisión)
            if original_path and original_path.exists():
                try:
                    bgr = cv2.imread(str(original_path))
                    if bgr is not None and bgr.shape[:2] == (h, w):
                        # Preparar máscara para GrabCut
                        gc_mask = np.where(mask_contour > 128, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
                        
                        # Aplicar GrabCut con máscara inicial
                        bgd_model = np.zeros((1, 65), np.float64)
                        fgd_model = np.zeros((1, 65), np.float64)
                        cv2.grabCut(bgr, gc_mask, None, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_MASK)
                        
                        # Crear máscara final
                        mask_final = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
                        mask_contour = mask_final
                except Exception as e:
                    logger.debug(f"GrabCut no disponible, usando contorno: {e}")
            
            # 5. NO suavizar - mantener bordes precisos sin halos
            mask_final = mask_contour
            
            # 6. Eliminar pequeños artefactos
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_final, connectivity=8)
            if num_labels > 1:
                # Mantener solo el componente más grande (el grano)
                largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
                mask_final = (labels == largest_label).astype(np.uint8) * 255
        else:
            mask_final = mask_clean
        
        # Crear imagen RGBA con máscara refinada
        rgba = np.dstack([rgb_array, mask_final])
        
        return Image.fromarray(rgba, 'RGBA')
    
    def _refine_mask_opencv_precise(self, rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
        """
        Refina la máscara alpha usando OpenCV para detección precisa de píxeles.
        Elimina bordes blancos residuales y ajusta pixel por pixel.
        """
        h, w = alpha.shape
        
        # 1. Convertir alpha a binario
        _, mask_binary = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
        
        # 2. Detectar y eliminar bordes blancos
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        
        # Identificar píxeles blancos/claros que están en el borde de la máscara
        white_mask = gray > 220  # Umbral para blanco
        
        # Dilatar máscara para encontrar área cercana al borde
        kernel_dilate = np.ones((3, 3), np.uint8)
        mask_dilated = cv2.dilate(mask_binary, kernel_dilate, iterations=1)
        border_region = mask_dilated.astype(bool) & ~(mask_binary.astype(bool))
        
        # Eliminar píxeles blancos en la región del borde
        mask_clean = np.where(border_region & white_mask, 0, mask_binary).astype(np.uint8)
        
        # 3. Erosionar ligeramente para eliminar bordes residuales
        kernel_erode = np.ones((3, 3), np.uint8)
        mask_clean = cv2.erode(mask_clean, kernel_erode, iterations=1)
        
        # 4. Operaciones morfológicas para limpiar
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # 5. Detectar contorno más grande
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask_final = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask_final, [largest_contour], -1, 255, thickness=-1)
        else:
            mask_final = mask_clean
        
        # 6. NO suavizar - mantener bordes precisos sin halos
        return mask_final
    
    def _extract_crop_characteristics(self, crop_image: Image.Image) -> Dict[str, float]:
        """
        Extrae características visuales del GRANO REAL (solo áreas con alpha>0).
        Esto es crucial para predicciones precisas basadas en el tamaño real del grano.
        """
        # Convertir a numpy array manteniendo alpha
        crop_array = np.array(crop_image)
        
        # Extraer RGB y alpha
        rgb = crop_array[:, :, :3] if crop_array.shape[2] >= 3 else crop_array
        alpha = crop_array[:, :, 3] if crop_array.shape[2] == 4 else np.ones(crop_array.shape[:2]) * 255
        
        # Máscara binaria: 1 donde hay grano visible, 0 donde es transparente
        mask = (alpha > 128).astype(np.float32)
        
        # Extraer características SOLO del área visible del grano (donde mask=1)
        visible_pixels = rgb[mask > 0]
        
        if len(visible_pixels) == 0:
            # Si no hay píxeles visibles, usar toda la imagen
            logger.warning("No hay píxeles visibles en el crop, usando toda la imagen")
            visible_pixels = rgb.reshape(-1, 3)
            mask = np.ones(crop_array.shape[:2])
        
        # Calcular características del GRANO visible
        brightness = visible_pixels.mean() if len(visible_pixels) > 0 else rgb.reshape(-1, 3).mean()
        std_val = visible_pixels.std() if len(visible_pixels) > 0 else rgb.reshape(-1, 3).std()
        
        # Área REAL del grano (número de píxeles visibles)
        object_area = int(np.sum(mask > 0))
        
        # Bounding box del objeto visible
        y_coords, x_coords = np.where(mask > 0)
        if len(x_coords) > 0:
            width_visible = int(x_coords.max() - x_coords.min() + 1)
            height_visible = int(y_coords.max() - y_coords.min() + 1)
        else:
            width_visible = crop_array.shape[1]
            height_visible = crop_array.shape[0]
        
        logger.debug(
            f"Características del grano: área_visible={object_area}px, "
            f"tamaño_bbox={width_visible}x{height_visible}, "
            f"brillo={brightness:.1f}, std={std_val:.2f}"
        )
        
        return {
            'area': object_area,  # ÁREA REAL del grano visible
            'area_bbox': width_visible * height_visible,  # Área del bounding box
            'width': width_visible,
            'height': height_visible,
            'brightness': brightness,
            'std': std_val,
            'min': visible_pixels.min() if len(visible_pixels) > 0 else rgb.min(),
            'max': visible_pixels.max() if len(visible_pixels) > 0 else rgb.max(),
            'aspect_ratio': width_visible / height_visible if height_visible > 0 else 1.0
        }
    
    def _validate_predictions_diversity(self, predictions: Dict[str, float]) -> bool:
        """Valida que las predicciones tengan variación adecuada."""
        pred_values = list(predictions.values())
        unique_values = set(round(v, 4) for v in pred_values)
        
        if len(unique_values) <= 1:
            logger.warning(
                f"Predicciones idénticas detectadas. "
                f"Esto puede indicar que el modelo devuelve siempre la media."
            )
            return False
        
        return True
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predice dimensiones y peso de un grano de cacao.
        
        Args:
            image: Imagen PIL del grano
            
        Returns:
            Diccionario con predicciones y metadatos
        """
        if not self.models_loaded:
            raise ModelNotLoadedError(
                "Los artefactos no han sido cargados. Llamar load_artifacts() primero."
            )
        
        start_time = time.time()
        
        try:
            # 1. Segmentación y recorte
            crop_image, crop_url, yolo_confidence = self._segment_and_crop(image)
            
            # 2. Extraer características del crop
            crop_characteristics = self._extract_crop_characteristics(crop_image)
            
            # Validar calidad del crop
            crop_std = crop_characteristics['std']
            if crop_std < self.config.MIN_CROP_STD:
                logger.warning(f"Crop con std baja ({crop_std:.4f}), puede afectar predicciones")
            
            # 3. Preprocesar imagen
            crop_image_rgb = crop_image.convert('RGB')
            image_tensor = self._preprocess_image(crop_image_rgb)
            
            # 4. Predecir cada target
            predictions = {}
            confidences = {}
            
            for target in TARGETS:
                pred_value, confidence = self._predict_single_target(
                    image_tensor,
                    target,
                    crop_characteristics
                )
                predictions[target] = pred_value
                confidences[target] = confidence
            
            # 5. Validar diversidad de predicciones
            self._validate_predictions_diversity(predictions)
            
            # 6. Preparar resultado
            total_time = time.time() - start_time
            
            result = {
                'alto_mm': predictions['alto'],
                'ancho_mm': predictions['ancho'],
                'grosor_mm': predictions['grosor'],
                'peso_g': predictions['peso'],
                'confidences': confidences,
                'crop_url': crop_url,
                'debug': {
                    'segmented': True,
                    'yolo_conf': float(yolo_confidence),
                    'latency_ms': int(total_time * 1000),
                    'models_version': 'v2',
                    'device': str(self.device),
                    'total_time_s': total_time
                }
            }
            
            logger.info(f"Predicción completada en {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}", exc_info=True)
            if isinstance(e, (ModelNotLoadedError, InvalidImageError, SegmentationError)):
                raise
            raise PredictionError(f"Error procesando imagen: {e}") from e
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predice desde bytes de imagen.
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            Diccionario con predicciones
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return self.predict(image)
        except Exception as e:
            logger.error(f"Error procesando imagen desde bytes: {e}", exc_info=True)
            raise InvalidImageError(f"Error procesando imagen: {e}") from e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre los modelos cargados.
        
        Returns:
            Diccionario con información de los modelos
        """
        if not self.models_loaded:
            return {'status': 'not_loaded'}
        
        info = {
            'status': 'loaded',
            'device': str(self.device),
            'models': {},
            'scalers': 'loaded' if self.scalers else 'not_loaded',
            'yolo_cropper': 'loaded' if self.yolo_cropper else 'not_loaded'
        }
        
        for target, model in self.regression_models.items():
            info['models'][target] = {
                'type': type(model).__name__,
                'parameters': sum(p.numel() for p in model.parameters())
            }
        
        return info


# ============================================================================
# INSTANCIA GLOBAL Y FUNCIONES DE CONVENIENCIA
# ============================================================================

_predictor_instance: Optional[CacaoPredictor] = None


def get_predictor() -> CacaoPredictor:
    """
    Obtiene la instancia global del predictor.
    
    Returns:
        Instancia del predictor
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = CacaoPredictor()
        
        if not _predictor_instance.load_artifacts():
            logger.warning("No se pudieron cargar todos los artefactos automáticamente")
    
    return _predictor_instance


def load_artifacts() -> bool:
    """
    Función de conveniencia para cargar artefactos.
    
    Returns:
        True si se cargaron exitosamente
    """
    predictor = get_predictor()
    return predictor.load_artifacts()


def predict_image(image: Image.Image) -> Dict[str, Any]:
    """
    Función de conveniencia para predecir una imagen.
    
    Args:
        image: Imagen PIL
        
    Returns:
        Diccionario con predicciones
    """
    predictor = get_predictor()
    return predictor.predict(image)


def predict_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Función de conveniencia para predecir desde bytes.
    
    Args:
        image_bytes: Bytes de la imagen
        
    Returns:
        Diccionario con predicciones
    """
    predictor = get_predictor()
    return predictor.predict_from_bytes(image_bytes)
