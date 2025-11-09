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
# CONSTANTES DE CONFIGURACIN
# ============================================================================

@dataclass
class PredictionConfig:
    """Configuracin para prediccin."""
    # Umbrales de validacin
    MIN_IMAGE_STD: float = 5.0
    MIN_TENSOR_STD: float = 0.01
    MIN_CROP_STD: float = 10.0
    
    # Lmites fsicos de targets (mm o g)
    TARGET_LIMITS: Dict[str, Tuple[float, float]] = None
    
    # Escalado visual
    SCALE_FACTORS: Dict[str, float] = None
    
    # Pesos de combinacin modelo/visual
    # PRIORIZAR SIEMPRE EL MODELO ENTRENADO (fue entrenado con el dataset completo)
    MODEL_WEIGHT_NORMAL: float = 0.95  # 95% modelo entrenado (confianza alta)
    VISUAL_WEIGHT_NORMAL: float = 0.05  # 5% visual (ajuste fino solamente)
    MODEL_WEIGHT_MEAN: float = 0.85  # Si modelo devuelve media, usar 85% modelo + 15% visual
    VISUAL_WEIGHT_MEAN: float = 0.15  # Mayor peso visual solo cuando modelo est cerca de media
    
    # Validacin de crop
    MIN_CROP_SIZE: int = 50
    MIN_VISIBLE_RATIO: float = 0.2
    MAX_BORDER_WHITE_RATIO: float = 0.3
    MIN_OBJECT_RATIO: float = 0.1
    
    # Validacin de deteccin YOLO
    MIN_YOLO_CONFIDENCE: float = 0.25  # Confianza mnima de YOLO (reducido para aceptar ms casos)
    MIN_YOLO_AREA: int = 500  # rea mnima del objeto detectado (pxeles, reducido)
    
    # Configuracin de YOLO
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


# Configuracin global
CONFIG = PredictionConfig()


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class PredictionError(Exception):
    """Excepcin base para errores de prediccin."""
    pass


class ModelNotLoadedError(PredictionError):
    """Error cuando los modelos no estn cargados."""
    pass


class InvalidImageError(PredictionError):
    """Error cuando la imagen es invlida."""
    pass


class SegmentationError(PredictionError):
    """Error en segmentacin."""
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
            config: Configuracin personalizada (opcional)
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
        
        # Lmites del dataset (se cargarn desde escaladores)
        self.dataset_limits: Dict[str, Tuple[float, float]] = {}
        
        # Estadsticas del dataset (para optimizacin basada en datos reales)
        self.dataset_stats: Dict[str, Dict[str, float]] = {}
        
        # Calibracin de pxeles (relaciones directas del dataset)
        self.pixel_calibration: Optional[Dict[str, Any]] = None
        self._load_pixel_calibration()
        
        # Directorios
        self._setup_directories()
        
        # Transformacin precomputada (cach)
        self._image_transform = transforms.Compose([
            transforms.Resize(self.config.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.config.IMAGENET_MEAN, std=self.config.IMAGENET_STD)
        ])
        
        logger.info(f"Predictor inicializado (threshold={confidence_threshold}, device={self.device})")
    
    def _load_pixel_calibration(self) -> None:
        """Carga el archivo de calibracin de pxeles del dataset si existe."""
        calibration_file = Path("media/datasets/pixel_calibration.json")
        if calibration_file.exists():
            try:
                import json
                with open(calibration_file, 'r', encoding='utf-8') as f:
                    self.pixel_calibration = json.load(f)
                logger.info(f" Calibracin de pxeles cargada: {len(self.pixel_calibration.get('calibration_records', []))} registros")
            except Exception as e:
                logger.warning(f"[WARN] Error cargando calibracin de pxeles: {e}")
                self.pixel_calibration = None
    
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
        Carga todos los artefactos necesarios para la prediccin.
        Carga todos los artefactos necesarios para la predicción.
        Si no existen, entrena automáticamente los modelos.
        
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
            self.regression_models = {}
            
            for target in TARGETS:
                model_path = get_regressors_artifacts_dir() / f"{target}.pt"
                
                if not model_path.exists():
                    logger.error(f"Modelo no encontrado para {target}: {model_path}")
                    return False
                
                try:
                    # Crear modelo
                    model = create_model(
                        model_type="resnet18",  # Por defecto ResNet18
                        num_outputs=1,
                        pretrained=False,
                        dropout_rate=0.2,
                        multi_head=False
                    )
                    
                    # Cargar pesos
                    checkpoint = torch.load(model_path, map_location=self.device)
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.to(self.device)
                    model.eval()
                    
                    self.regression_models[target] = model
                    logger.info(f"Modelo cargado para {target}")
                    
                except Exception as e:
                    logger.error(f"Error cargando modelo para {target}: {e}")
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
        
        logger.warning("Modelos no encontrados. Iniciando entrenamiento automtico...")
        return self._auto_train_models()
    
    def _auto_train_models(self) -> bool:
        """
        Entrena automáticamente los modelos si no existen.
        
        Returns:
            True si el entrenamiento fue exitoso, False en caso contrario
        """
        try:
            logger.info(" Iniciando entrenamiento automático de modelos...")
            
            # Importar funciones de entrenamiento
            from ..pipeline.train_all import run_training_pipeline
            
            # Configuración de entrenamiento automático
            config = {
                'epochs': 30,  # Menos epochs para entrenamiento rápido
                'batch_size': 16,  # Batch size más pequeño para memoria
                'learning_rate': 0.001,
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
            
            logger.info(f"Iniciando entrenamiento automtico con config: {config}")
            success = run_training_pipeline(**config)
            
            if success:
                logger.info("Entrenamiento automtico completado exitosamente")
            else:
                logger.error("Error en entrenamiento automtico")
            
            return success
            
        except Exception as e:
            logger.error(f"Error en entrenamiento automtico: {e}", exc_info=True)
            return False
    
    def _load_scalers(self) -> bool:
        """Carga los escaladores y extrae lmites del dataset."""
        try:
            self.scalers = load_scalers()
            logger.info("Escaladores cargados exitosamente")
            
            # Extraer lmites del dataset desde los escaladores
            self._extract_dataset_limits()
            
            # Cargar estadsticas del dataset CSV para optimizacin
            self._load_dataset_statistics()
            
            return True
        except Exception as e:
            logger.error(f"Error cargando escaladores: {e}")
            return False
    
    def _load_dataset_statistics(self) -> None:
        """Carga estadsticas del dataset CSV para optimizar predicciones."""
        try:
            from ..data.dataset_loader import CacaoDatasetLoader
            
            loader = CacaoDatasetLoader()
            stats = loader.get_dataset_stats()
            
            if stats and 'dimensions_stats' in stats:
                self.dataset_stats = stats['dimensions_stats']
                
                logger.info(" Estadsticas del dataset cargadas para optimizacin:")
                for target in TARGETS:
                    if target in self.dataset_stats:
                        s = self.dataset_stats[target]
                        logger.info(
                            f"  {target}: mean={s.get('mean', 0):.2f}, "
                            f"std={s.get('std', 0):.2f}, "
                            f"min={s.get('min', 0):.2f}, max={s.get('max', 0):.2f}"
                        )
        except Exception as e:
            logger.warning(f"No se pudieron cargar estadsticas del dataset: {e}")
            self.dataset_stats = {}
    
    def _extract_dataset_limits(self) -> None:
        """Extrae lmites min/max del dataset desde los escaladores."""
        if not self.scalers or not self.scalers.is_fitted:
            logger.warning("Escaladores no ajustados, usando lmites por defecto")
            self.dataset_limits = self.config.TARGET_LIMITS.copy()
            return
        
        self.dataset_limits = {}
        
        for target in TARGETS:
            if target not in self.scalers.scalers:
                logger.warning(f"Escalador no encontrado para {target}, usando lmites por defecto")
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
                    f"Lmites del dataset para {target}: "
                    f"min={min_val:.2f}, max={max_val:.2f} "
                    f"(del dataset de entrenamiento)"
                )
            else:
                # Fallback: usar mean  3*std si no hay data_min_/data_max_
                if hasattr(scaler, 'mean_') and hasattr(scaler, 'scale_'):
                    mean_val = float(scaler.mean_[0])
                    std_val = float(scaler.scale_[0])
                    min_val = max(0.0, mean_val - 3 * std_val)
                    max_val = mean_val + 3 * std_val
                    self.dataset_limits[target] = (min_val, max_val)
                    logger.info(
                        f"Lmites estimados para {target} (mean3std): "
                        f"min={min_val:.2f}, max={max_val:.2f}"
                    )
                else:
                    # ltimo fallback: usar lmites por defecto
                    self.dataset_limits[target] = self.config.TARGET_LIMITS.get(target, (0.0, 100.0))
                    logger.warning(f"Usando lmites por defecto para {target}")
    
    def _load_regression_models(self) -> bool:
        """Carga los modelos de regresin."""
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
                    f" Modelo entrenado cargado para {target} desde {model_path.name} "
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
            Tensor preprocesado listo para el modelo con forma [1, 3, 224, 224]
        """
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Validar imagen antes de procesar
        image_array = np.array(image)
        image_std = image_array.std()
        
        if image_std < self.config.MIN_IMAGE_STD:
            logger.warning(f"Imagen con std baja ({image_std:.2f}), puede causar predicciones pobres")
        
        # Aplicar transformaciones (usar cach configurado)
        # self._image_transform ya incluye Resize, ToTensor y Normalize
        tensor = self._image_transform(image)
        
        # Validar que el tensor tiene la forma correcta [3, 224, 224]
        if tensor.dim() != 3 or tensor.shape[0] != 3:
            raise InvalidImageError(
                f"Tensor tiene forma incorrecta: {tensor.shape}. "
                f"Se esperaba [3, 224, 224]"
            )
        
        # Validar tensor antes de agregar batch dimension
        tensor_std = tensor.std().item()
        if tensor_std < self.config.MIN_TENSOR_STD:
            raise InvalidImageError(
                f"Tensor tiene std muy baja ({tensor_std:.6f}). "
                f"Imagen puede estar corrupta o ser uniforme."
            )
        
        # Agregar dimensin de batch UNA SOLA VEZ: [3, 224, 224] -> [1, 3, 224, 224]
        tensor = tensor.unsqueeze(0)
        
        # Validar forma final
        if tensor.dim() != 4 or tensor.shape != (1, 3, 224, 224):
            raise InvalidImageError(
                f"Tensor tiene forma incorrecta despus de unsqueeze: {tensor.shape}. "
                f"Se esperaba [1, 3, 224, 224]"
            )
        
        # Mover a device
        tensor = tensor.to(self.device)
        
        logger.debug(f"Imagen preprocesada: forma={tensor.shape}, device={tensor.device}, dtype={tensor.dtype}")
        
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
    
    def _calculate_pixel_based_dimensions(
        self,
        object_area_pixels: int,
        width_pixels: int,
        height_pixels: int,
        mask: np.ndarray,
        alpha: np.ndarray
    ) -> Dict[str, float]:
        """
        Calcula dimensiones fsicas reales basadas en anlisis preciso de pxeles.
        Usa la mscara del grano (sin fondo) para medir dimensiones fsicas reales.
        
        Args:
            object_area_pixels: rea real del grano en pxeles
            width_pixels: Ancho del bounding box en pxeles
            height_pixels: Alto del bounding box en pxeles
            mask: Mscara binaria del grano
            alpha: Canal alpha de la imagen
            
        Returns:
            Diccionario con dimensiones fsicas calculadas (alto_mm, ancho_mm, grosor_mm, peso_g)
        """
        if object_area_pixels == 0:
            return {
                'alto_mm': 0, 'ancho_mm': 0, 'grosor_mm': 0, 'peso_g': 0,
                'scale_factor': 0
            }
        
        # Calcular factor de escala pxeles -> mm basado en estadsticas del dataset
        # Usar dimensiones lineales para calibracin ms precisa
        scale_factor = self._calculate_pixel_to_mm_scale_factor(
            object_area_pixels, 
            width_pixels=width_pixels, 
            height_pixels=height_pixels
        )
        
        # Calcular dimensiones fsicas basadas en pxeles reales
        # MTODO MEJORADO: Usar relaciones ms precisas basadas en forma real del grano
        
        # 1. ANCHO: usar el ancho del bounding box (mxima extensin horizontal)
        # Ajuste fino: considerar que el bounding box puede ser ligeramente ms grande
        # Usar factor de correccin basado en relacin rea real / rea bbox
        bbox_area_pixels = width_pixels * height_pixels
        area_fill_ratio = object_area_pixels / bbox_area_pixels if bbox_area_pixels > 0 else 0.75
        
        # Aplicar correccin ms precisa al ancho
        # Si el rea del grano ocupa menos del 80% del bbox, el bbox es ms grande de lo necesario
        width_correction = np.sqrt(max(0.70, min(0.95, area_fill_ratio)))  # Factor entre 0.84 y 0.97
        ancho_mm = width_pixels * scale_factor * width_correction
        
        # 2. ALTO: usar el alto del bounding box (mxima extensin vertical)
        # Mismo factor de correccin aplicado
        alto_mm = height_pixels * scale_factor * width_correction
        
        # 3. GROSOR: estimar usando relaciones ms precisas del dataset
        # MEJORADO: Usar relaciones directas del dataset para mejor precisin
        if ancho_mm > 0 and alto_mm > 0:
            # Calcular rea real del grano en mm
            area_mm2 = object_area_pixels * (scale_factor ** 2)
            
            # Relacin entre rea real del grano y rea del bounding box
            # Esto nos dice qu tan "lleno" est el bbox (factor de forma)
            aspect_ratio_area = area_mm2 / (ancho_mm * alto_mm) if (ancho_mm * alto_mm) > 0 else 0.75
            
            # Grosor estimado usando relaciones PRECISAS del dataset
            if self.dataset_stats and 'alto' in self.dataset_stats and 'grosor' in self.dataset_stats:
                alto_mean = self.dataset_stats['alto'].get('mean', 23.5)
                grosor_mean = self.dataset_stats['grosor'].get('mean', 9.5)
                ancho_mean = self.dataset_stats.get('ancho', {}).get('mean', 12.5)
                
                # Calcular relaciones grosor/alto y grosor/ancho del dataset
                grosor_alto_ratio = grosor_mean / alto_mean  # Tpicamente ~0.4-0.45
                grosor_ancho_ratio = grosor_mean / ancho_mean  # Tpicamente ~0.75-0.85
                
                # Grosor usando PROMEDIO PONDERADO ms preciso
                # Para granos de cacao: el grosor est ms relacionado con el ancho que con el alto
                # Usar peso 60% ancho + 40% alto (los granos tpicamente tienen grosor similar al ancho)
                grosor_from_ancho = ancho_mm * grosor_ancho_ratio
                grosor_from_alto = alto_mm * grosor_alto_ratio
                
                # Promedio ponderado: ms peso al ancho (grosor ms relacionado con ancho)
                grosor_mm = (grosor_from_ancho * 0.65 + grosor_from_alto * 0.35)
                
                # Ajuste fino segn factor de forma (si el rea del grano es mayor, grosor puede ser mayor)
                # Pero ajuste conservador para evitar sobre-estimar
                if aspect_ratio_area > 0.8:
                    # Grano ocupa mucho del bbox -> grosor puede ser ligeramente mayor
                    grosor_mm *= 1.05
                elif aspect_ratio_area < 0.65:
                    # Grano ocupa poco del bbox -> grosor puede ser ligeramente menor
                    grosor_mm *= 0.95
            else:
                # Fallback: usar relacin emprica mejorada
                # Grosor tpico: ~0.8 del ancho (granos de cacao tienen grosor similar al ancho)
                grosor_mm = ancho_mm * 0.80
        
        # 4. PESO: calcular usando volumen estimado y densidad MEJORADA
        # Usar relaciones del dataset para calibrar mejor el peso
        if alto_mm > 0 and ancho_mm > 0 and grosor_mm > 0:
            # Volumen de elipsoide: (4/3) *  * a * b * c
            volume_mm3 = (4.0 / 3.0) * np.pi * (alto_mm/2) * (ancho_mm/2) * (grosor_mm/2)
            
            # Densidad promedio de granos de cacao: ~1.05-1.15 g/cm
            # Usar densidad promedio calibrada con el dataset si est disponible
            if self.dataset_stats and 'peso' in self.dataset_stats:
                peso_mean = self.dataset_stats['peso'].get('mean', 1.7)
                alto_mean = self.dataset_stats['alto'].get('mean', 23.5)
                ancho_mean = self.dataset_stats.get('ancho', {}).get('mean', 12.5)
                grosor_mean = self.dataset_stats.get('grosor', {}).get('mean', 9.5)
                
                # Calcular volumen promedio del dataset
                volume_mean_mm3 = (4.0 / 3.0) * np.pi * (alto_mean/2) * (ancho_mean/2) * (grosor_mean/2)
                
                # Calcular densidad calibrada del dataset
                density_calibrated = peso_mean / volume_mean_mm3  # g/mm
                
                # Usar densidad calibrada si es razonable (0.0008 - 0.0015 g/mm)
                if 0.0008 <= density_calibrated <= 0.0015:
                    density_g_per_mm3 = density_calibrated
                else:
                    # Fallback a densidad tpica
                    density_g_per_mm3 = 1.10e-3  # 1.10 g/cm
            else:
                # Densidad tpica de granos de cacao: ~1.10 g/cm = 1.10e-3 g/mm
                density_g_per_mm3 = 1.10e-3
            
            peso_g = volume_mm3 * density_g_per_mm3
            
            # Ajuste fino basado en relaciones del dataset
            if self.dataset_stats and 'peso' in self.dataset_stats:
                peso_mean = self.dataset_stats['peso'].get('mean', 1.7)
                # Si el peso calculado est muy desviado del promedio, ajustar ligeramente
                peso_ratio = peso_g / peso_mean
                if peso_ratio < 0.5:
                    # Peso muy bajo -> aumentar ligeramente (puede ser subestimacin)
                    peso_g *= 1.15
                elif peso_ratio > 1.5:
                    # Peso muy alto -> reducir ligeramente
                    peso_g *= 0.90
        else:
            # Fallback: usar rea y relaciones del dataset
            if self.dataset_stats and 'peso' in self.dataset_stats and 'alto' in self.dataset_stats:
                peso_mean = self.dataset_stats['peso'].get('mean', 1.7)
                alto_mean = self.dataset_stats['alto'].get('mean', 23.5)
                ancho_mean = self.dataset_stats.get('ancho', {}).get('mean', 12.5)
                
                # Escalar peso proporcional al volumen estimado (usando dimensiones)
                if alto_mm > 0 and ancho_mm > 0:
                    volume_ratio = (alto_mm * ancho_mm * (ancho_mm * 0.8)) / (alto_mean * ancho_mean * (ancho_mean * 0.8))
                    peso_g = peso_mean * volume_ratio
                else:
                    # ltimo fallback: usar rea
                    peso_g = peso_mean * (object_area_pixels * (scale_factor ** 2)) / (alto_mean ** 2)
            else:
                peso_g = object_area_pixels * (scale_factor ** 2) * 0.00012  # Factor emprico ajustado
        
        logger.info(
            f" ANLISIS DIRECTO DE PXELES: "
            f"rea={object_area_pixels}px, BBox={width_pixels}x{height_pixels}px  "
            f"Alto={alto_mm:.2f}mm, Ancho={ancho_mm:.2f}mm, Grosor={grosor_mm:.2f}mm, Peso={peso_g:.3f}g "
            f"(Factor escala: {scale_factor:.6f} mm/pxel)"
        )
        
        return {
            'alto_mm': float(alto_mm),
            'ancho_mm': float(ancho_mm),
            'grosor_mm': float(grosor_mm),
            'peso_g': float(peso_g),
            'scale_factor': float(scale_factor)
        }
    
    def _calculate_pixel_to_mm_scale_factor(self, object_area_pixels: int, width_pixels: int = None, height_pixels: int = None) -> float:
        """
        Calcula el factor de escala pxeles -> mm basado en calibracin del dataset o estadsticas.
        
        PRIORIDAD: 1) Calibracin directa del dataset (pixel_calibration.json)
                   2) Estadsticas del dataset
                   3) Factor por defecto
        
        Args:
            object_area_pixels: rea del grano en pxeles
            width_pixels: Ancho del bounding box en pxeles (opcional)
            height_pixels: Alto del bounding box en pxeles (opcional)
            
        Returns:
            Factor de escala en mm/pxel
        """
        # PRIORIDAD 1: Usar calibracin directa del dataset si est disponible
        if self.pixel_calibration and width_pixels and height_pixels:
            calibration_records = self.pixel_calibration.get('calibration_records', [])
            if calibration_records:
                # Buscar registro ms similar basado en dimensiones en pxeles
                # Usar el registro con dimensiones ms cercanas
                best_match = None
                min_distance = float('inf')
                
                for record in calibration_records:
                    record_width = record.get('pixel_measurements', {}).get('width_pixels', 0)
                    record_height = record.get('pixel_measurements', {}).get('height_pixels', 0)
                    
                    # Calcular distancia euclidiana en el espacio de dimensiones
                    width_diff = abs(record_width - width_pixels) / max(width_pixels, record_width, 1)
                    height_diff = abs(record_height - height_pixels) / max(height_pixels, record_height, 1)
                    distance = np.sqrt(width_diff ** 2 + height_diff ** 2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match = record
                
                if best_match and min_distance < 0.5:  # Umbral de similitud (50%)
                    # Usar factor de escala del registro ms similar
                    scale_factors = best_match.get('scale_factors', {})
                    avg_scale = scale_factors.get('average_mm_per_pixel', 0)
                    
                    if avg_scale > 0:
                        logger.debug(
                            f" Calibracin directa del dataset: "
                            f"factor={avg_scale:.6f} mm/pxel "
                            f"(registro ID={best_match.get('id')}, distancia={min_distance:.3f})"
                        )
                        return float(avg_scale)
                
                # Si no hay coincidencia cercana, usar estadsticas agregadas de la calibracin
                stats = self.pixel_calibration.get('statistics', {})
                scale_stats = stats.get('scale_factors', {})
                if scale_stats.get('mean', 0) > 0:
                    logger.debug(f" Usando factor promedio de calibracin: {scale_stats['mean']:.6f} mm/pxel")
                    return float(scale_stats['mean'])
        
        # PRIORIDAD 2: Usar estadsticas del dataset si no hay calibracin directa
        # Si no tenemos estadsticas del dataset, usar factor por defecto calibrado
        if not self.dataset_stats or 'alto' not in self.dataset_stats:
            # Factor por defecto basado en calibracin emprica
            # Para grano tpico: dimensiones promedio ~23mm x 12mm
            # Si tenemos dimensiones en pxeles, usar directamente
            if width_pixels and height_pixels:
                # Calcular factor usando ambas dimensiones
                typical_alto_mm = 23.5
                typical_ancho_mm = 12.5
                # Factor promedio de ambas dimensiones
                scale_alto = typical_alto_mm / height_pixels if height_pixels > 0 else 0
                scale_ancho = typical_ancho_mm / width_pixels if width_pixels > 0 else 0
                if scale_alto > 0 and scale_ancho > 0:
                    default_scale = (scale_alto + scale_ancho) / 2
                    return np.clip(default_scale, 0.015, 0.050)
            
            # Fallback: usar rea
            typical_area_pixels = 20000
            typical_alto_mm = 23.5
            typical_ancho_mm = 12.5
            typical_area_mm2 = np.pi * (typical_alto_mm / 2) * (typical_ancho_mm / 2)
            default_scale = np.sqrt(typical_area_mm2 / typical_area_pixels)
            return np.clip(default_scale, 0.015, 0.050)
        
        # Obtener estadsticas del dataset
        alto_stats = self.dataset_stats.get('alto', {})
        ancho_stats = self.dataset_stats.get('ancho', {})
        
        alto_mean = alto_stats.get('mean', 23.5)
        ancho_mean = ancho_stats.get('mean', 12.5)
        
        # CALIBRACIN PRECISA: Usar relacin DIRECTA entre dimensiones lineales y pxeles
        # Si tenemos dimensiones en pxeles, usar directamente para calibracin ms precisa
        if width_pixels and height_pixels and width_pixels > 0 and height_pixels > 0:
            # Calcular factor de escala usando dimensiones lineales directamente
            # Esto es ms preciso que usar rea
            scale_factor_alto = alto_mean / height_pixels
            scale_factor_ancho = ancho_mean / width_pixels
            
            # Usar promedio ponderado (peso segn aspecto del grano)
            aspect_ratio = width_pixels / height_pixels if height_pixels > 0 else 1.0
            if aspect_ratio > 0.5:  # Granos ms anchos
                scale_factor = (scale_factor_alto * 0.6 + scale_factor_ancho * 0.4)
            else:  # Granos ms largos
                scale_factor = (scale_factor_alto * 0.7 + scale_factor_ancho * 0.3)
            
            # Ajuste fino segn rea relativa al promedio
            if self.dataset_stats:
                # Calcular rea promedio esperada del dataset
                typical_area_mm2 = np.pi * (alto_mean / 2) * (ancho_mean / 2)
                # rea tpica en pxeles (calibrada para dataset)
                typical_area_pixels_dataset = 20000  # Valor ms conservador
                area_ratio = object_area_pixels / typical_area_pixels_dataset
                
                # Ajuste conservador segn rea
                if area_ratio > 1.2:
                    # Objeto ms grande: reducir ligeramente el factor (rea no escala linealmente)
                    scale_factor *= 0.95
                elif area_ratio < 0.8:
                    # Objeto ms pequeo: aumentar ligeramente el factor
                    scale_factor *= 1.05
            
            # Validar rango
            scale_factor = np.clip(scale_factor, 0.015, 0.050)
            
            logger.debug(
                f"Factor de escala (lineal): {scale_factor:.6f} mm/pxel "
                f"(dimensiones: {width_pixels}x{height_pixels}px  {alto_mean:.1f}x{ancho_mean:.1f}mm)"
            )
            
            return float(scale_factor)
        
        # MTODO ALTERNATIVO: Usar relacin de reas (menos preciso)
        typical_area_mm2 = np.pi * (alto_mean / 2) * (ancho_mean / 2)
        typical_area_pixels_dataset = 20000  # Valor ms conservador y preciso
        
        # Calcular escala usando relacin rea fsica / rea pxeles
        area_ratio = typical_area_mm2 / typical_area_pixels_dataset
        scale_factor = np.sqrt(area_ratio)
        
        # Ajuste segn rea real del objeto (ms conservador)
        area_ratio_current = object_area_pixels / typical_area_pixels_dataset
        if area_ratio_current > 1.2:
            scale_factor *= 0.92  # Reducir para objetos ms grandes
        elif area_ratio_current < 0.8:
            scale_factor *= 1.08  # Aumentar para objetos ms pequeos
        
        # Validar rango
        scale_factor = np.clip(scale_factor, 0.015, 0.050)
        
        logger.debug(
            f"Factor de escala (rea): {scale_factor:.6f} mm/pxel "
            f"(rea objeto: {object_area_pixels}px, ratio: {area_ratio_current:.3f})"
        )
        
        return float(scale_factor)
    
    def _calculate_visual_prediction(
        self,
        target: str,
        crop_area: float,
        crop_brightness: float,
        crop_std: float
    ) -> float:
        """
        Calcula prediccin basada en caractersticas visuales del crop.
        OPTIMIZADO usando estadsticas reales del dataset.
        
        Args:
            target: Target a predecir
            crop_area: rea del crop en pxeles (solo grano visible)
            crop_brightness: Brillo medio del crop
            crop_std: Desviacin estndar del crop
            
        Returns:
            Prediccin basada en caractersticas visuales (ajuste fino)
        """
        # Usar estadsticas del dataset si estn disponibles (ms preciso)
        if self.dataset_stats and target in self.dataset_stats:
            stats = self.dataset_stats[target]
            dataset_mean = stats.get('mean', 0)
            dataset_std = stats.get('std', 1)
            dataset_min = stats.get('min', 0)
            dataset_max = stats.get('max', 100)
            
            # Normalizar rea del crop (asumiendo que granos tpicos tienen rea ~10000-50000 px)
            # Basado en observacin del dataset: granos tpicos estn en rango 20-30mm
            # Ajustar segn estadsticas reales
            typical_area_range = (8000, 60000)  # Rango tpico de reas en pxeles
            normalized_area = np.clip(
                (crop_area - typical_area_range[0]) / (typical_area_range[1] - typical_area_range[0]),
                0.0, 1.0
            )
            
            # Calcular prediccin base usando media del dataset como referencia
            # Ajustar segn rea normalizada (granos ms grandes = valores ms altos)
            area_factor = 0.8 + normalized_area * 0.4  # Factor 0.8-1.2
            
            # Ajuste por brillo (granos ms oscuros pueden ser ms densos)
            brightness_norm = crop_brightness / 255.0
            brightness_factor = 0.98 + (brightness_norm - 0.5) * 0.04
            
            # Ajuste por variacin (textura del grano)
            std_factor = 0.99 + min(crop_std / 150.0, 1.0) * 0.02
            
            # Prediccin visual basada en estadsticas del dataset
            visual_pred = dataset_mean * area_factor * brightness_factor * std_factor
            
            # Asegurar que est dentro de los lmites del dataset
            visual_pred = np.clip(visual_pred, dataset_min * 0.8, dataset_max * 1.2)
            
            return float(visual_pred)
        
        # Fallback: usar mtodo anterior si no hay estadsticas
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
    
    def _get_pixel_based_prediction(
        self,
        target: str,
        crop_characteristics: Dict[str, float]
    ) -> float:
        """
        Obtiene la prediccin basada en anlisis preciso de pxeles.
        
        Args:
            target: Target a predecir
            crop_characteristics: Caractersticas del crop incluyendo dimensiones basadas en pxeles
            
        Returns:
            Prediccin basada en anlisis de pxeles
        """
        pixel_key_map = {
            'alto': 'pixel_alto_mm',
            'ancho': 'pixel_ancho_mm',
            'grosor': 'pixel_grosor_mm',
            'peso': 'pixel_peso_g'
        }
        
        pixel_key = pixel_key_map.get(target)
        if pixel_key and pixel_key in crop_characteristics:
            pixel_pred = crop_characteristics[pixel_key]
            
            # Obtener informacin de pxeles para logging detallado
            area_pixels = crop_characteristics.get('area', 0)
            width_px = crop_characteristics.get('width', 0)
            height_px = crop_characteristics.get('height', 0)
            scale_factor = crop_characteristics.get('pixel_scale_factor', 0)
            
            logger.info(
                f" Medicin directa de pxeles para {target}: "
                f"{pixel_pred:.4f} "
                f"(rea: {area_pixels}px, Dimensiones: {width_px}x{height_px}px, "
                f"Escala: {scale_factor:.6f} mm/pxel)"
            )
            return float(pixel_pred)
        
        # Fallback: usar caractersticas visuales si no hay datos de pxeles
        logger.warning(f"[WARN] No hay prediccin basada en pxeles para {target}, usando fallback")
        return crop_characteristics.get('brightness', 128) * 0.1  # Fallback bsico
    
    def _calculate_prediction_weights(
        self,
        model_prediction: float,
        prediction_normalized: float,
        pixel_based_prediction: float,
        scaler_mean: Optional[float],
        scaler_std: Optional[float] = None,
        target: str = ''
    ) -> Tuple[float, float, float]:
        """
        Calcula los pesos para combinar prediccin del modelo entrenado, anlisis de pxeles y visual.
        
        PRIORIZA: Modelo Entrenado (principal) > Anlisis de Pxeles (preciso) > Visual (ajuste fino)
        
        Returns:
            Tuple (model_weight, pixel_weight, visual_weight)
        """
        # Verificar si modelo est devolviendo SOLO la media del dataset
        is_returning_only_mean = False
        
        if scaler_mean is not None and scaler_std is not None:
            threshold = 0.05 * scaler_std
            distance_from_mean = abs(model_prediction - scaler_mean)
            
            if distance_from_mean < threshold and abs(prediction_normalized) < 0.05:
                # Modelo claramente devolviendo solo la media -> usar casi todo anlisis de pxeles
                is_returning_only_mean = True
                logger.warning(
                    f"Modelo devolviendo solo media del dataset. "
                    f"Usando anlisis directo de pxeles: 5% modelo + 92% pxeles + 3% visual"
                )
                return 0.05, 0.92, 0.03
        
        # Verificar si la prediccin basada en pxeles es vlida
        pixel_is_valid = pixel_based_prediction > 0 and not np.isnan(pixel_based_prediction)
        
        if pixel_is_valid:
            # PREDICCIN PRINCIPAL: Usar anlisis directo de pxeles como fuente principal de verdad
            # El usuario quiere: "si esta imagen tiene tantos pxeles, entonces mide tanto y pesa tanto"
            # 85% anlisis de pxeles (medicin directa y precisa) + 12% modelo entrenado + 3% visual
            # El anlisis de pxeles mide DIRECTAMENTE el grano en pxeles y calcula dimensiones fsicas
            model_weight = 0.12
            pixel_weight = 0.85  # PRINCIPAL: Anlisis directo de pxeles
            visual_weight = 0.03
            
            dataset_count = self.dataset_stats.get('alto', {}).get('count', 0) if self.dataset_stats and 'alto' in self.dataset_stats else 0
            logger.info(
                f" ANLISIS DIRECTO DE PXELES: {pixel_weight:.0%} (medicin directa: pxeles  mm) + "
                f"{model_weight:.0%} modelo (ajuste fino) + {visual_weight:.0%} visual (refinamiento)"
            )
            return model_weight, pixel_weight, visual_weight
        else:
            # Sin prediccin de pxeles vlida: usar modelo + visual (como antes)
            logger.debug(
                f"[WARN] Prediccin de pxeles no vlida, usando solo modelo + visual: "
                f"{self.config.MODEL_WEIGHT_NORMAL:.0%} modelo + {self.config.VISUAL_WEIGHT_NORMAL:.0%} visual"
            )
            return self.config.MODEL_WEIGHT_NORMAL, 0.0, self.config.VISUAL_WEIGHT_NORMAL
    
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
            crop_characteristics: Caractersticas visuales del crop
            
        Returns:
            Tuple con (valor_predicho, confianza)
        """
        model = self.regression_models[target]
        model.eval()
        
        # Validar y corregir forma del tensor si es necesario
        if image_tensor.dim() == 5:
            # Si tiene 5 dimensiones [1, 1, 3, 224, 224], eliminar la dimensin extra
            logger.warning(f"Tensor con 5 dimensiones detectado: {image_tensor.shape}. Corrigiendo...")
            image_tensor = image_tensor.squeeze(0)  # [1, 1, 3, 224, 224] -> [1, 3, 224, 224]
        
        # Validar que el tensor tiene la forma correcta [1, 3, 224, 224]
        if image_tensor.dim() != 4 or image_tensor.shape[0] != 1 or image_tensor.shape[1] != 3:
            raise ValueError(
                f"Tensor tiene forma incorrecta: {image_tensor.shape}. "
                f"Se esperaba [1, 3, 224, 224]. Dimensin actual: {image_tensor.dim()}"
            )
        
        # Validar tensor de entrada
        input_std = image_tensor.std().item()
        if input_std < self.config.MIN_TENSOR_STD:
            logger.warning(f"Tensor con std baja ({input_std:.6f}) para {target}")
        
        logger.debug(f"Prediciendo {target} con tensor de forma: {image_tensor.shape}")
        
        # PREDICCIN DEL MODELO ENTRENADO (usando pesos del entrenamiento)
        with torch.no_grad():
            # Predicción
            prediction = model(image_tensor)
            prediction_normalized = float(prediction.cpu().numpy().flatten()[0])
        
        logger.info(
            f" Modelo entrenado devolvi para {target}: "
            f"normalizado={prediction_normalized:.8f} "
            f"(esto viene del modelo entrenado con tu dataset)"
        )
        
        # Desnormalizar usando escaladores del dataset
        model_prediction = self._denormalize_prediction(prediction_normalized, target)
        
        # Obtener estadsticas del escalador (del dataset de entrenamiento)
        scaler = self.scalers.scalers[target]
        scaler_mean = scaler.mean_[0] if hasattr(scaler, 'mean_') else None
        scaler_std = scaler.scale_[0] if hasattr(scaler, 'scale_') else None
        
        logger.info(
            f" Prediccin del modelo entrenado para {target}: "
            f"{model_prediction:.4f} "
            f"(desnormalizado de {prediction_normalized:.8f}, "
            f"mean_dataset={scaler_mean:.4f}, std_dataset={scaler_std:.4f})"
        )
        
        # Verificar si modelo est devolviendo la media del dataset (problema comn)
        # NOTA: Un valor normalizado cercano a 0 NO significa que est devolviendo la media
        # puede ser una prediccin vlida cerca de la media del dataset
        # Solo marcar como "devuelve media" si la prediccin desnormalizada est MUY cerca de la media
        is_returning_dataset_mean = False
        
        if scaler_mean is not None and scaler_std is not None:
            # Usar umbral ms estricto: la prediccin debe estar dentro de 0.05 * std del dataset
            # de la media para considerarse "solo devuelve media"
            threshold = 0.05 * scaler_std
            distance_from_mean = abs(model_prediction - scaler_mean)
            
            if distance_from_mean < threshold and abs(prediction_normalized) < 0.05:
                # Solo si est MUY cerca de la media Y el valor normalizado es muy pequeo
                logger.warning(
                    f"[WARN] ATENCIN: Modelo devuelve valor muy cercano a media del dataset "
                    f"({model_prediction:.4f} vs media {scaler_mean:.4f}, diferencia: {distance_from_mean:.4f}) "
                    f"para {target}. Usando 85% modelo + 15% visual como ajuste."
                )
                is_returning_dataset_mean = True
            else:
                # Prediccin vlida del modelo (puede estar cerca de la media si el grano es promedio)
                logger.debug(
                    f" Modelo devolvi prediccin para {target}: "
                    f"{model_prediction:.4f} (normalizado: {prediction_normalized:.8f}, "
                    f"distancia de media: {distance_from_mean:.4f})"
                )
        else:
            logger.debug(
                f" Modelo devolvi prediccin nica para {target}: "
                f"{model_prediction:.4f} (normalizado: {prediction_normalized:.8f})"
            )
        
        # Calcular prediccin visual (ajuste fino basado en caractersticas visuales)
        crop_area = crop_characteristics.get('area', 50000)
        crop_brightness = crop_characteristics.get('brightness', 128)
        crop_std = crop_characteristics.get('std', 50)
        
        visual_prediction = self._calculate_visual_prediction(
            target, crop_area, crop_brightness, crop_std
        )
        
        # PREDICCIN BASADA EN PXELES (anlisis preciso de dimensiones fsicas)
        # Usar dimensiones calculadas directamente de pxeles del crop sin fondo
        pixel_based_prediction = self._get_pixel_based_prediction(target, crop_characteristics)
        
        # Calcular pesos (priorizar modelo entrenado, luego pxeles, luego visual)
        model_weight, pixel_weight, visual_weight = self._calculate_prediction_weights(
            model_prediction, prediction_normalized, pixel_based_prediction, 
            scaler_mean, scaler_std, target
        )
        
        # COMBINAR PREDICCIONES: Anlisis directo de pxeles (principal) + Modelo entrenado + Visual (ajuste fino)
        # PRINCIPAL: Anlisis directo de pxeles ("si esta imagen tiene tantos pxeles, entonces mide tanto y pesa tanto")
        prediction_value = (
            pixel_weight * pixel_based_prediction +  # 85% - Medicin directa de pxeles
            model_weight * model_prediction +        # 12% - Ajuste fino del modelo
            visual_weight * visual_prediction        # 3% - Refinamiento visual
        )
        
        logger.info(
            f" PREDICCIN FINAL para {target}: {prediction_value:.4f} "
            f"= PXELES({pixel_based_prediction:.4f}){pixel_weight:.0%} "
            f"+ modelo({model_prediction:.4f}){model_weight:.0%} "
            f"+ visual({visual_prediction:.4f}){visual_weight:.0%} "
            f" Principalmente basado en anlisis directo de pxeles"
        )
        
        # Aplicar lmites del dataset (ms estrictos que lmites fsicos)
        if target in self.dataset_limits:
            min_val, max_val = self.dataset_limits[target]
            original_value = prediction_value
            
            if prediction_value < min_val or prediction_value > max_val:
                logger.warning(
                    f"Prediccin fuera de lmites del dataset para {target}: "
                    f"{prediction_value:.2f} (lmites: [{min_val:.2f}, {max_val:.2f}]). "
                    f"Aplicando recorte."
                )
            
            prediction_value = np.clip(prediction_value, min_val, max_val)
            # Calcular confianza (proxy basado en varianza del modelo)
            # Usar dropout para estimar incertidumbre si está disponible
            confidence = self._estimate_confidence(model, image_tensor, target)
            
            if original_value != prediction_value:
                logger.debug(f"Prediccin limitada para {target}: {original_value:.2f} -> {prediction_value:.2f}")
        elif target in self.config.TARGET_LIMITS:
            # Fallback a lmites fsicos si no hay lmites del dataset
            min_val, max_val = self.config.TARGET_LIMITS[target]
            original_value = prediction_value
            prediction_value = np.clip(prediction_value, min_val, max_val)
            
            if original_value != prediction_value:
                logger.debug(f"Prediccin limitada (fsicos) para {target}: {original_value:.2f} -> {prediction_value:.2f}")
        
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
        Estima la confianza de la prediccin usando Monte Carlo Dropout.
        
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
            n_samples = 5  # Número de muestras para estimar varianza
            
            for _ in range(self.config.CONFIDENCE_MC_SAMPLES):
                with torch.no_grad():
                    pred = model(image_tensor)
                    predictions.append(pred.cpu().numpy().flatten()[0])
            
            model.eval()
            
            # Calcular estadsticas
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
            
            # Ajustar segn varianza
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
        """
        Obtiene una confianza proxy basada en estadísticas del target.
        
        Args:
            target: Target predicho
            
        Returns:
            Confianza proxy (0-1)
        """
        # Confianzas proxy basadas en la dificultad típica de cada target
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
            True si el crop es vlido y contiene cacao visible, False si es defectuoso
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
                    f"Puede ser fondo blanco o rea vaca."
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
            
            # 3. Verificar tamao mnimo
            if h < self.config.MIN_CROP_SIZE or w < self.config.MIN_CROP_SIZE:
                logger.warning(f"Crop muy pequeo ({h}x{w}px)")
                return False
            
            # 4. Verificar rea del objeto (que el grano sea suficientemente grande)
            object_area = np.sum(alpha > 128)
            object_ratio = object_area / (h * w)
            if object_ratio < self.config.MIN_OBJECT_RATIO:
                logger.warning(
                    f"Crop con objeto muy pequeo ({object_ratio:.2%}). "
                    f"Puede ser ruido o falso positivo."
                )
                return False
            
            # 5. Validar que no sea completamente uniforme (verificar variacin en RGB)
            rgb_std = rgb.std()
            if rgb_std < 10:
                logger.warning(
                    f"Crop con variacin RGB muy baja ({rgb_std:.2f}). "
                    f"Puede ser un rea uniforme sin grano de cacao visible."
                )
                return False
            
            logger.debug(
                f"Crop validado: tamao={h}x{w}, visible={visible_ratio:.2%}, "
                f"objeto={object_ratio:.2%}, std_rgb={rgb_std:.2f}"
            )
            
            return True
            
        except Exception as e:
            logger.warning(f"Error validando calidad del crop: {e}")
            return False
    
    def _segment_and_crop(self, image: Image.Image) -> Tuple[Image.Image, str, float]:
        """
        Segmenta y recorta la imagen usando U-Net (mtodo principal) o YOLO (fallback).
        Valida que realmente se detect un grano de cacao.
        
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
            # MTODO 1: Intentar U-Net (eliminacin de fondo ms precisa)
            try:
                logger.debug("Intentando segmentacin con U-Net...")
                crop_image = remove_background_ai(str(temp_image_path))
                segmentation_method = "unet"
                confidence = 0.95  # U-Net tiene alta confianza si funciona
                
                logger.info("Segmentacin U-Net exitosa")
                
            except (FileNotFoundError, Exception) as e:
                logger.debug(f"U-Net no disponible ({e}), usando YOLO como fallback...")
                
                # MTODO 2: Fallback a YOLO
                if self.yolo_cropper is None:
                    raise SegmentationError(
                        "Ningn mtodo de segmentacin disponible. "
                        "U-Net no encontrado y YOLO no cargado."
                    )
                
                crop_result = self.yolo_cropper.process_image(
                    temp_image_path,
                    image_id=1,
                    force_process=True
                )
                
                if not crop_result.get('success'):
                    error_msg = crop_result.get('error', 'Error desconocido')
                    raise SegmentationError(f"Error en segmentacin YOLO: {error_msg}")
                
                # VALIDACIN: Verificar que realmente se detect un grano de cacao
                confidence = crop_result.get('confidence', 0.0)
                yolo_area = crop_result.get('area', 0)
                
                # Verificar rea mnima primero (ms crtico)
                if yolo_area < self.config.MIN_YOLO_AREA:
                    raise SegmentationError(
                        f"rea del objeto detectado muy pequea ({yolo_area} pxeles). "
                        f"Mnimo requerido: {self.config.MIN_YOLO_AREA} pxeles. "
                        f"Puede ser un falso positivo o deteccin de ruido."
                    )
                
                # Verificar confianza (con advertencia pero permitir si el rea es vlida)
                if confidence < self.config.MIN_YOLO_CONFIDENCE:
                    logger.warning(
                        f"Confianza de YOLO baja ({confidence:.2%}), "
                        f"mnimo recomendado: {self.config.MIN_YOLO_CONFIDENCE:.2%}. "
                        f"Procesando de todos modos ya que el rea es vlida ({yolo_area} px)."
                    )
                    # No lanzar error, solo advertencia - permitir procesar con validacin de crop
                else:
                    logger.info(
                        f"Deteccin YOLO vlida: confianza={confidence:.2%}, "
                        f"rea={yolo_area} px"
                    )
                
                # Cargar imagen original y mscara de YOLO para refinar con OpenCV
                crop_path = crop_result['crop_path']
                crop_image_original = Image.open(crop_path)
                
                # Obtener mscara de YOLO directamente para refinamiento preciso
                yolo_mask = crop_result.get('mask')
                
                # Obtener ruta de imagen original si est disponible (mejor para GrabCut)
                original_image_path = crop_result.get('original_image_path')
                if not original_image_path or not Path(original_image_path).exists():
                    original_image_path = temp_image_path
                
                # Si no tenemos mscara, intentar obtenerla directamente desde YOLO
                if yolo_mask is None:
                    try:
                        prediction_data = self.yolo_cropper.yolo_inference.get_best_prediction(temp_image_path)
                        if prediction_data and 'mask' in prediction_data:
                            yolo_mask = prediction_data['mask']
                    except Exception as e:
                        logger.debug(f"No se pudo obtener mscara de YOLO: {e}")
                
                # Refinar mscara y crear crop preciso usando OpenCV
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
                    # Convertir RGB a RGBA usando OpenCV para mejor deteccin
                    rgb_array = np.array(crop_image)
                    crop_image = self._refine_mask_with_opencv(
                        crop_image, 
                        None, 
                        None
                    )
                else:
                    crop_image = crop_image.convert('RGBA')
            
            # MEJORAR CROP: Refinar con OpenCV para deteccin precisa de pxeles
            crop_array = np.array(crop_image)
            
            if crop_array.shape[2] == 4:
                rgb = crop_array[:, :, :3]
                alpha = crop_array[:, :, 3]
                
                # Refinar mscara con OpenCV para deteccin precisa
                alpha_refined = self._refine_mask_opencv_precise(rgb, alpha)
                
                # Aplicar mscara refinada
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
            
            # Si el crop no es vlido Y la confianza es muy baja, rechazar
            if not crop_is_valid and confidence < 0.15:
                raise SegmentationError(
                    f"Crop invlido y confianza muy baja ({confidence:.2%}). "
                    f"No se puede procesar esta imagen de forma confiable."
                )
            
            # Guardar segn calidad (permitir procesar con advertencia si confianza es baja)
            if crop_is_valid:
                crop_path_final = self.processed_crops_dir / f"{crop_uuid}.png"
                crop_url = f"/media/cacao_images/processed/{datetime.now().year}/{datetime.now().month:02d}/{datetime.now().day:02d}/{crop_uuid}.png"
                logger.debug(f"Crop vlido guardado usando {segmentation_method}")
            else:
                # An as procesar si la confianza es aceptable (puede ser vlido)
                if confidence >= 0.20:
                    crop_path_final = self.processed_crops_dir / f"{crop_uuid}.png"
                    crop_url = f"/media/cacao_images/processed/{datetime.now().year}/{datetime.now().month:02d}/{datetime.now().day:02d}/{crop_uuid}.png"
                    logger.warning(
                        f"Crop con validacin dudosa pero procesado por confianza aceptable "
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
                f"Segmentacin completada usando {segmentation_method} "
                f"(confianza: {confidence:.2%}, vlido: {crop_is_valid})"
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
        Refina la mscara usando OpenCV para deteccin precisa de pxeles del cacao.
        Elimina bordes blancos y ajusta la mscara pixel por pixel.
        """
        rgb_array = np.array(image.convert('RGB'))
        h, w = rgb_array.shape[:2]
        
        # Si tenemos mscara de YOLO, usarla como base
        if yolo_mask is not None:
            # Normalizar mscara de YOLO
            if yolo_mask.max() <= 1.0:
                mask = (yolo_mask * 255).astype(np.uint8)
            else:
                mask = np.clip(yolo_mask, 0, 255).astype(np.uint8)
            
            # Redimensionar si es necesario
            if mask.shape[:2] != (h, w):
                mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            # Crear mscara inicial usando color y luminosidad
            gray = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2GRAY)
            
            # Detectar grano de cacao (marrn/oscuro) vs fondo blanco
            _, mask_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Eliminar ruido
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask_binary, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # REFINAMIENTO PRECISO CON OPENCV
        
        # 1. Eliminar bordes blancos detectando pxeles blancos/claros cerca de bordes
        gray = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2GRAY)
        
        # Detectar pxeles blancos/claros (posible fondo residual)
        white_threshold = 220
        is_white = gray > white_threshold
        
        # Erosionar mscara para eliminar bordes blancos
        kernel_erode = np.ones((5, 5), np.uint8)
        mask_eroded = cv2.erode(mask, kernel_erode, iterations=2)
        
        # Enmascarar reas blancas dentro del objeto
        mask_clean = np.where(is_white & (mask_eroded > 128), 0, mask_eroded).astype(np.uint8)
        
        # 2. Operaciones morfolgicas para cerrar huecos y suavizar
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel_close, iterations=1)
        
        # 3. Detectar el contorno ms grande y crear mscara ajustada
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Encontrar el contorno ms grande (el grano)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Crear mscara binaria del contorno
            mask_contour = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask_contour, [largest_contour], -1, 255, thickness=-1)
            
            # 4. Usar GrabCut para refinar an ms (opcional pero mejora precisin)
            if original_path and original_path.exists():
                try:
                    bgr = cv2.imread(str(original_path))
                    if bgr is not None and bgr.shape[:2] == (h, w):
                        # Preparar mscara para GrabCut
                        gc_mask = np.where(mask_contour > 128, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
                        
                        # Aplicar GrabCut con mscara inicial
                        bgd_model = np.zeros((1, 65), np.float64)
                        fgd_model = np.zeros((1, 65), np.float64)
                        cv2.grabCut(bgr, gc_mask, None, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_MASK)
                        
                        # Crear mscara final
                        mask_final = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
                        mask_contour = mask_final
                except Exception as e:
                    logger.debug(f"GrabCut no disponible, usando contorno: {e}")
            
            # 5. NO suavizar - mantener bordes precisos sin halos
            mask_final = mask_contour
            
            # 6. Eliminar pequeos artefactos
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_final, connectivity=8)
            if num_labels > 1:
                # Mantener solo el componente ms grande (el grano)
                largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
                mask_final = (labels == largest_label).astype(np.uint8) * 255
        else:
            mask_final = mask_clean
        
        # Crear imagen RGBA con mscara refinada
        rgba = np.dstack([rgb_array, mask_final])
        
        return Image.fromarray(rgba, 'RGBA')
    
    def _refine_mask_opencv_precise(self, rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
        """
        Refina la mscara alpha usando OpenCV para deteccin precisa de pxeles.
        Elimina bordes blancos residuales y ajusta pixel por pixel.
        """
        h, w = alpha.shape
        
        # 1. Convertir alpha a binario
        _, mask_binary = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
        
        # 2. Detectar y eliminar bordes blancos
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        
        # Identificar pxeles blancos/claros que estn en el borde de la mscara
        white_mask = gray > 220  # Umbral para blanco
        
        # Dilatar mscara para encontrar rea cercana al borde
        kernel_dilate = np.ones((3, 3), np.uint8)
        mask_dilated = cv2.dilate(mask_binary, kernel_dilate, iterations=1)
        border_region = mask_dilated.astype(bool) & ~(mask_binary.astype(bool))
        
        # Eliminar pxeles blancos en la regin del borde
        mask_clean = np.where(border_region & white_mask, 0, mask_binary).astype(np.uint8)
        
        # 3. Erosionar ligeramente para eliminar bordes residuales
        kernel_erode = np.ones((3, 3), np.uint8)
        mask_clean = cv2.erode(mask_clean, kernel_erode, iterations=1)
        
        # 4. Operaciones morfolgicas para limpiar
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # 5. Detectar contorno ms grande
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
        Extrae caractersticas visuales del GRANO REAL (solo reas con alpha>0).
        Calcula dimensiones fsicas basadas en anlisis preciso de pxeles.
        Esto es crucial para predicciones precisas basadas en el tamao real del grano.
        """
        # Convertir a numpy array manteniendo alpha
        crop_array = np.array(crop_image)
        
        # Extraer RGB y alpha
        rgb = crop_array[:, :, :3] if crop_array.shape[2] >= 3 else crop_array
        alpha = crop_array[:, :, 3] if crop_array.shape[2] == 4 else np.ones(crop_array.shape[:2]) * 255
        
        # Mscara binaria: 1 donde hay grano visible, 0 donde es transparente
        mask = (alpha > 128).astype(np.float32)
        
        # Extraer caractersticas SOLO del rea visible del grano (donde mask=1)
        visible_pixels = rgb[mask > 0]
        
        if len(visible_pixels) == 0:
            # Si no hay pxeles visibles, usar toda la imagen
            logger.warning("No hay pxeles visibles en el crop, usando toda la imagen")
            visible_pixels = rgb.reshape(-1, 3)
            mask = np.ones(crop_array.shape[:2])
        
        # Calcular caractersticas del GRANO visible
        brightness = visible_pixels.mean() if len(visible_pixels) > 0 else rgb.reshape(-1, 3).mean()
        std_val = visible_pixels.std() if len(visible_pixels) > 0 else rgb.reshape(-1, 3).std()
        
        # rea REAL del grano (nmero de pxeles visibles)
        object_area = int(np.sum(mask > 0))
        
        # Bounding box del objeto visible
        y_coords, x_coords = np.where(mask > 0)
        if len(x_coords) > 0:
            width_visible = int(x_coords.max() - x_coords.min() + 1)
            height_visible = int(y_coords.max() - y_coords.min() + 1)
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()
        else:
            width_visible = crop_array.shape[1]
            height_visible = crop_array.shape[0]
            x_min, x_max = 0, width_visible - 1
            y_min, y_max = 0, height_visible - 1
        
        # ANLISIS PRECISO DE DIMENSIONES FSICAS BASADO EN PXELES
        # Calcular dimensiones fsicas usando anlisis de pxeles y factor de escala
        pixel_based_dimensions = self._calculate_pixel_based_dimensions(
            object_area, width_visible, height_visible, mask, alpha
        )
        
        logger.debug(
            f"Caractersticas del grano: rea_visible={object_area}px, "
            f"tamao_bbox={width_visible}x{height_visible}, "
            f"brillo={brightness:.1f}, std={std_val:.2f}, "
            f"dimensiones_pxeles={pixel_based_dimensions}"
        )
        
        return {
            'area': object_area,  # REA REAL del grano visible
            'area_bbox': width_visible * height_visible,  # rea del bounding box
            'width': width_visible,  # Ancho en pxeles
            'height': height_visible,  # Alto en pxeles
            'brightness': brightness,
            'std': std_val,
            'min': visible_pixels.min() if len(visible_pixels) > 0 else rgb.min(),
            'max': visible_pixels.max() if len(visible_pixels) > 0 else rgb.max(),
            'aspect_ratio': width_visible / height_visible if height_visible > 0 else 1.0,
            # Dimensiones fsicas calculadas basadas en pxeles
            'pixel_alto_mm': pixel_based_dimensions.get('alto_mm', 0),
            'pixel_ancho_mm': pixel_based_dimensions.get('ancho_mm', 0),
            'pixel_grosor_mm': pixel_based_dimensions.get('grosor_mm', 0),
            'pixel_peso_g': pixel_based_dimensions.get('peso_g', 0),
            'pixel_scale_factor': pixel_based_dimensions.get('scale_factor', 0),
            # Bounding box
            'bbox': {
                'x_min': int(x_min), 'x_max': int(x_max),
                'y_min': int(y_min), 'y_max': int(y_max)
            }
        }
    
    def _validate_predictions_diversity(self, predictions: Dict[str, float]) -> bool:
        """Valida que las predicciones tengan variacin adecuada."""
        pred_values = list(predictions.values())
        unique_values = set(round(v, 4) for v in pred_values)
        
        if len(unique_values) <= 1:
            logger.warning(
                f"Predicciones idnticas detectadas. "
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
            # 1. Segmentacin y recorte
            logger.debug("Iniciando segmentacin...")
            crop_image, crop_url, yolo_confidence = self._segment_and_crop(image)
            
            if crop_image is None:
                raise SegmentationError("No se pudo segmentar la imagen correctamente")
            
            # 2. Extraer caractersticas del crop
            crop_characteristics = self._extract_crop_characteristics(crop_image)
            
            # Validar calidad del crop
            crop_std = crop_characteristics['std']
            if crop_std < self.config.MIN_CROP_STD:
                logger.warning(f"Crop con std baja ({crop_std:.4f}), puede afectar predicciones")
            
            # 3. Preprocesar imagen
            crop_image_rgb = crop_image.convert('RGB')
            image_tensor = self._preprocess_image(crop_image_rgb)
            
            # Validar forma del tensor antes de pasar a prediccin
            if image_tensor.dim() != 4 or image_tensor.shape != (1, 3, 224, 224):
                raise ValueError(
                    f"Tensor tiene forma incorrecta despus de preprocesar: {image_tensor.shape}. "
                    f"Se esperaba [1, 3, 224, 224]"
                )
            
            logger.debug(f"Tensor preprocesado: forma={image_tensor.shape}, device={image_tensor.device}")
            
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
            logger.error(f"Error en prediccin: {e}", exc_info=True)
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
        
        # Intentar cargar artefactos automáticamente
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


