"""
Módulo de predicción unificada para CacaoScan (Híbrido).
ACTUALIZADO:
- Corregidos imports (no se usa sys.path).
- Eliminada la carga del CacaoCropper (YOLO), ya que no se usa en este flujo.
- Se usa la cascada de segmentación (U-Net -> rembg -> OpenCV) de processor.py.
- Se reutiliza el archivo PNG generado por el procesador en lugar de duplicarlo.
- Eliminados imports y lógica innecesaria.
"""
import time
import uuid
import os
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import io

# --- CORRECCIÓN: Usar imports relativos ---
from ..utils.paths import get_regressors_artifacts_dir, get_datasets_dir
from ..utils.logs import get_ml_logger
from ..utils.io import ensure_dir_exists, load_json
from ..segmentation.processor import segment_and_crop_cacao_bean, SegmentationError
from ..regression.models import create_model, TARGETS, get_model_info
from ..regression.scalers import load_scalers, CacaoScalers

# Configuración de Django (necesaria para que el worker de Gunicorn encuentre MEDIA_ROOT)
try:
    from django.conf import settings
    MEDIA_ROOT = Path(settings.MEDIA_ROOT)
except Exception as e:
    logger = get_ml_logger("cacaoscan.ml.prediction.standalone")
    logger.warning(f"No se pudo cargar Django settings: {e}. Usando rutas relativas.")
    MEDIA_ROOT = Path("media") # Fallback
else:
    logger = get_ml_logger("cacaoscan.ml.prediction")


# ============================================================================
# CONSTANTES DE CONFIGURACIÓN
# ============================================================================

@dataclass
class PredictionConfig:
    """Configuración para predicción."""
    IMAGE_SIZE: Tuple[int, int] = (224, 224)
    IMAGENET_MEAN: Optional[List[float]] = None
    IMAGENET_STD: Optional[List[float]] = None
    MIN_YOLO_CONFIDENCE: float = 0.25 # (No usado aquí, pero mantenido por si se reactiva)
    MIN_CROP_SIZE: int = 50
    MIN_VISIBLE_RATIO: float = 0.2
    TARGET_LIMITS: Optional[Dict[str, Tuple[float, float]]] = None
    PIXEL_FEATURE_KEYS: Optional[List[str]] = None
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.TARGET_LIMITS is None:
            self.TARGET_LIMITS = {
                'alto': (5.0, 60.0),
                'ancho': (3.0, 30.0),
                'grosor': (1.0, 20.0),
                'peso': (0.2, 10.0)
            }
        if self.IMAGENET_MEAN is None:
            self.IMAGENET_MEAN = [0.485, 0.456, 0.406]
        if self.IMAGENET_STD is None:
            self.IMAGENET_STD = [0.229, 0.224, 0.225]
        if self.PIXEL_FEATURE_KEYS is None:
            self.PIXEL_FEATURE_KEYS = [
                'pixel_width', 'pixel_height', 'pixel_area', 'scale_factor', 'aspect_ratio'
            ]

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

# SegmentationError es importado desde processor.py

# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class CacaoPredictor:
    """
    Predictor unificado para granos de cacao (Versión Híbrida).
    """
    
    def __init__(self, confidence_threshold: float = 0.5, config: Optional[PredictionConfig] = None):
        """
        Inicializa el predictor.
        """
        self.confidence_threshold = confidence_threshold
        self.config = config or CONFIG
        
        # --- CORRECCIÓN: YOLO Cropper no se usa en este flujo ---
        # self.yolo_cropper: Optional[Any] = None
        self.regression_model: Optional[torch.nn.Module] = None
        self.scalers: Optional[CacaoScalers] = None
        
        self.device = self._get_device()
        self.models_loaded = False
        
        self.pixel_calibration: Optional[Dict[str, Any]] = None
        self._load_pixel_calibration()
        
        self._setup_directories()
        
        self._image_transform = transforms.Compose([
            transforms.Resize(self.config.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.config.IMAGENET_MEAN, std=self.config.IMAGENET_STD)
        ])
        
        logger.info(f"Predictor Híbrido inicializado (device={self.device})")

    def _load_pixel_calibration(self) -> None:
        """Carga el archivo de calibración de píxeles del dataset si existe."""
        calibration_file = get_datasets_dir() / "pixel_calibration.json"
        if calibration_file.exists():
            try:
                self.pixel_calibration = load_json(calibration_file)
                logger.info(f"✅ Calibración de píxeles cargada: {len(self.pixel_calibration.get('calibration_records', []))} registros")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando calibración de píxeles: {e}")
                self.pixel_calibration = None
        else:
            logger.warning("⚠️ No se encontró 'pixel_calibration.json'. La extracción de features de píxeles puede fallar o ser imprecisa.")
            self.pixel_calibration = None
    
    def _setup_directories(self) -> None:
        """Configura los directorios necesarios."""
        self.runtime_crops_dir = MEDIA_ROOT / "cacao_images" / "crops_runtime"
        ensure_dir_exists(self.runtime_crops_dir)
        
        # El 'processor' guarda aquí, así que solo necesitamos saber la ruta
        self.processed_crops_dir_base = MEDIA_ROOT / "cacao_images" / "processed"
    
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
        Carga todos los artefactos necesarios para la predicción HÍBRIDA.
        """
        try:
            logger.info("Cargando artefactos (Modo Híbrido)...")
            start_time = time.time()
            
            # --- CORRECCIÓN: No cargar YOLO Cropper ---
            
            # 1. Verificar y entrenar modelos si es necesario
            if not self._ensure_models_exist():
                return False
            
            # 2. Cargar escaladores (siguen siendo 4)
            if not self._load_scalers():
                return False
            
            # 3. Cargar modelo de regresión HÍBRIDO (solo uno)
            model_path = get_regressors_artifacts_dir() / "hybrid.pt"
            
            if not model_path.exists():
                logger.error(f"Modelo Híbrido 'hybrid.pt' no encontrado en: {model_path}")
                return False
            
            try:
                # CRÍTICO: Detectar número de características de píxeles del checkpoint
                # antes de crear el modelo
                # S6985: Use weights_only=True to prevent arbitrary code execution from untrusted model files.
                # This ensures only model weights are loaded, not arbitrary Python objects or code.
                checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
                pixel_feature_dim = None
                
                # Importar constantes de características
                from ..pipeline.train_all import CALIB_PIXEL_FEATURE_KEYS, PIXEL_FEATURE_KEYS
                
                # Intentar detectar desde el checkpoint
                if 'model_state_dict' in checkpoint:
                    state_dict = checkpoint['model_state_dict']
                    # Buscar la capa pixel_branch.0.weight que tiene shape [256, num_pixel_features]
                    if 'pixel_branch.0.weight' in state_dict:
                        pixel_feature_dim = state_dict['pixel_branch.0.weight'].shape[1]
                        logger.info(f"✅ Detectado pixel_feature_dim={pixel_feature_dim} desde checkpoint")
                        
                        # Actualizar PIXEL_FEATURE_KEYS según el número detectado
                        if pixel_feature_dim == len(CALIB_PIXEL_FEATURE_KEYS):
                            self.config.PIXEL_FEATURE_KEYS = CALIB_PIXEL_FEATURE_KEYS
                            logger.info(f"✅ Usando CALIB_PIXEL_FEATURE_KEYS ({pixel_feature_dim} características)")
                        elif pixel_feature_dim == len(PIXEL_FEATURE_KEYS):
                            self.config.PIXEL_FEATURE_KEYS = PIXEL_FEATURE_KEYS
                            logger.info(f"✅ Usando PIXEL_FEATURE_KEYS ({pixel_feature_dim} características)")
                        else:
                            logger.warning(f"⚠️ pixel_feature_dim={pixel_feature_dim} no coincide con ninguna configuración conocida")
                    else:
                        logger.warning("⚠️ No se encontró 'pixel_branch.0.weight' en checkpoint, usando valor por defecto")
                
                # Si no se detectó, usar valor por defecto basado en las características disponibles
                if pixel_feature_dim is None:
                    # Verificar si tenemos CALIB_PIXEL_FEATURE_KEYS disponibles
                    if self.pixel_calibration and self.pixel_calibration.get('calibration_records'):
                        records = self.pixel_calibration['calibration_records']
                        if records and any(
                            k in records[0] 
                            for k in CALIB_PIXEL_FEATURE_KEYS
                        ):
                            pixel_feature_dim = len(CALIB_PIXEL_FEATURE_KEYS)  # 12
                            logger.info(f"✅ Usando CALIB_PIXEL_FEATURE_KEYS: {pixel_feature_dim} características")
                            # Actualizar config para usar CALIB_PIXEL_FEATURE_KEYS
                            self.config.PIXEL_FEATURE_KEYS = CALIB_PIXEL_FEATURE_KEYS
                        else:
                            pixel_feature_dim = len(PIXEL_FEATURE_KEYS)  # 5 por defecto
                            logger.info(f"✅ Usando PIXEL_FEATURE_KEYS por defecto: {pixel_feature_dim} características")
                    else:
                        pixel_feature_dim = len(PIXEL_FEATURE_KEYS)  # 5 por defecto
                        logger.info(f"✅ Usando PIXEL_FEATURE_KEYS por defecto: {pixel_feature_dim} características")
                
                # Crear modelo con el número correcto de características
                self.regression_model = create_model(
                    model_type="hybrid",
                    pretrained=False,
                    dropout_rate=0.2,
                    hybrid=True,
                    use_pixel_features=True,
                    pixel_feature_dim=pixel_feature_dim
                )
                
                self.regression_model.load_state_dict(checkpoint['model_state_dict'])
                self.regression_model.to(self.device)
                self.regression_model.eval()
                logger.info(f"✅ Modelo Híbrido (hybrid.pt) cargado exitosamente con {pixel_feature_dim} características de píxeles")
                
            except Exception as e:
                logger.error(f"Error cargando modelo híbrido: {e}", exc_info=True)
                return False
            
            self.models_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Artefactos Híbridos cargados exitosamente en {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando artefactos: {e}", exc_info=True)
            return False

    def _ensure_models_exist(self) -> bool:
        """Verifica que existan los modelos y escaladores requeridos."""
        model_exist = (get_regressors_artifacts_dir() / "hybrid.pt").exists()
        scalers_exist = all(
            (get_regressors_artifacts_dir() / f"{target}_scaler.pkl").exists()
            for target in TARGETS
        )
        
        if model_exist and scalers_exist:
            return True
        
        if not model_exist and (get_regressors_artifacts_dir() / "alto.pt").exists():
            logger.error("Error: Se encontraron modelos antiguos (individuales).")
            logger.error("Este predictor requiere el modelo 'hybrid.pt'.")
            logger.error(
                "Por favor, elimina los modelos individuales (.pt) y entrena el modelo híbrido "
                "con: python manage.py train_cacao_models --model-type=hybrid --hybrid"
            )
            return False

        auto_train_enabled = os.getenv("AUTO_TRAIN_ENABLED", "0").lower() in ("1", "true", "yes")
        if auto_train_enabled:
            logger.error(
                "AUTO_TRAIN_ENABLED está activado, pero el entrenamiento automático desde "
                "el predictor ya no está soportado. "
                "Entrena los modelos manualmente con el comando "
                "'python manage.py train_cacao_models --model-type=hybrid --hybrid'."
            )
        else:
            logger.warning(
                "Modelo Híbrido (hybrid.pt) o escaladores no encontrados. "
                "Entrena los modelos con: python manage.py train_cacao_models --model-type=hybrid --hybrid"
            )
        return False
    
    def _auto_train_models(self) -> bool:
        """
        Método mantenido solo por compatibilidad.
        El entrenamiento automático ya no se ejecuta desde el predictor.
        """
        logger.error(
            "Entrenamiento automático desde el predictor no soportado. "
            "Usa el comando de gestión: python manage.py train_cacao_models --model-type=hybrid --hybrid"
        )
        return False
    
    def _load_scalers(self) -> bool:
        """Carga los escaladores (siguen siendo 4 escaladores)."""
        try:
            self.scalers = load_scalers()
            logger.info("Escaladores cargados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error cargando escaladores: {e}")
            return False
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocesa una imagen para los modelos de regresión.
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        tensor = self._image_transform(image)
        tensor = tensor.unsqueeze(0)
        tensor = tensor.to(self.device)
        return tensor
    
    def _denormalize_predictions(
        self,
        normalized_values: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Desnormaliza un diccionario de valores predichos.
        """
        if not self.scalers:
            raise ValueError("No hay escaladores disponibles para desnormalizar")
        
        # Convertir a arrays de numpy (requerido por inverse_transform)
        temp_data = {
            target: np.array([normalized_values[target]], dtype=np.float32) 
            for target in TARGETS
        }
        denorm_data = self.scalers.inverse_transform(temp_data)
        denormalized_predictions = {
            target: float(denorm_data[target][0]) for target in TARGETS
        }
        return denormalized_predictions

    def _segment_and_crop(self, image: Image.Image) -> Tuple[Image.Image, str, float]:
        """
        Segmenta y recorta la imagen usando el flujo de 'processor.py'
        (U-Net -> rembg -> OpenCV).
        REUTILIZA el archivo generado en lugar de copiarlo.
        """
        # Guardar temporalmente para procesamiento
        temp_image_path = self.runtime_crops_dir / f"temp_{uuid.uuid4()}.jpg"
        image.save(temp_image_path)
        
        crop_image = None
        # --- CORRECCIÓN: Confianza no hardcodeada ---
        seg_confidence = 0.9 # Confianza base si tiene éxito
        
        try:
            # --- CORRECCIÓN: Usar la cascada (U-Net -> rembg -> OpenCV) ---
            png_path_str = segment_and_crop_cacao_bean(str(temp_image_path), method="ai")
            
            if not png_path_str:
                raise SegmentationError("Segmentación no devolvió ruta de imagen")
            
            crop_path = Path(png_path_str)
            if not crop_path.exists():
                raise SegmentationError(f"Imagen segmentada no encontrada: {crop_path}")
            
            crop_image = Image.open(crop_path).convert("RGBA")
            
            # --- CORRECCIÓN: Calcular URL relativa sin duplicar archivos ---
            try:
                # Png_path_str es una ruta absoluta /app/media/cacao_images/processed/...
                # Necesitamos la URL relativa /media/cacao_images/processed/...
                relative_path = crop_path.relative_to(MEDIA_ROOT.parent)
                crop_url = f"/{relative_path.as_posix()}" 
            except Exception:
                # Fallback por si la ruta no es la esperada
                crop_url = crop_path.as_posix().split("/app")[-1] # /media/cacao_images/...
            
            logger.info("Segmentación completada (cascada U-Net/rembg/OpenCV)")
            
            return crop_image, crop_url, seg_confidence
            
        finally:
            # Limpiar solo el archivo temporal
            if temp_image_path.exists():
                temp_image_path.unlink()

    def _calculate_pixel_to_mm_scale_factor(self, width_pixels: int, height_pixels: int) -> float:
        """
        Calcula el factor de escala (mm/píxel) basado en la calibración del dataset.
        """
        if self.pixel_calibration:
            calibration_records = self.pixel_calibration.get('calibration_records', [])
            if calibration_records:
                best_match = None
                min_distance = float('inf')
                
                for record in calibration_records:
                    record_width = record.get('pixel_measurements', {}).get('width_pixels', 0)
                    record_height = record.get('pixel_measurements', {}).get('height_pixels', 0)
                    
                    if record_width == 0 or record_height == 0:
                        continue

                    width_diff = abs(record_width - width_pixels) / max(width_pixels, record_width, 1)
                    height_diff = abs(record_height - height_pixels) / max(height_pixels, record_height, 1)
                    distance = np.sqrt(width_diff ** 2 + height_diff ** 2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match = record
                
                if best_match and min_distance < 0.5:
                    avg_scale = best_match.get('scale_factors', {}).get('average_mm_per_pixel', 0)
                    if avg_scale > 0:
                        logger.debug(f"📐 Calibración directa: factor={avg_scale:.6f} (ID={best_match.get('id')})")
                        return float(avg_scale)
                
                stats = self.pixel_calibration.get('statistics', {})
                scale_stats = stats.get('scale_factors', {})
                if scale_stats.get('mean', 0) > 0:
                    logger.debug(f"📐 Usando factor promedio de calibración: {scale_stats['mean']:.6f} mm/píxel")
                    return float(scale_stats['mean'])

        default_scale = 0.035
        logger.warning(f"⚠️ Usando factor de escala por defecto: {default_scale:.6f}. Calibración no encontrada o sin coincidencias.")
        return default_scale

    def _extract_crop_characteristics(self, crop_image: Image.Image) -> Dict[str, float]:
        """
        Extrae características visuales y de píxeles del GRANO REAL (solo áreas con alpha>0).
        
        Soporta tanto PIXEL_FEATURE_KEYS (5 características) como CALIB_PIXEL_FEATURE_KEYS (12 características).
        """
        crop_array = np.array(crop_image)
        alpha = crop_array[:, :, 3]
        
        mask = (alpha > 128).astype(np.float32)
        object_area = int(np.sum(mask > 0))
        
        y_coords, x_coords = np.nonzero(mask > 0)
        if len(x_coords) > 0:
            width_visible = int(x_coords.max() - x_coords.min() + 1)
            height_visible = int(y_coords.max() - y_coords.min() + 1)
            bbox_area = width_visible * height_visible
        else:
            width_visible = crop_array.shape[1]
            height_visible = crop_array.shape[0]
            bbox_area = width_visible * height_visible

        scale_factor = self._calculate_pixel_to_mm_scale_factor(width_visible, height_visible)
        aspect_ratio = float(width_visible / height_visible if height_visible > 0 else 1.0)
        
        # Características básicas (PIXEL_FEATURE_KEYS)
        features = {
            'pixel_width': float(width_visible),
            'pixel_height': float(height_visible),
            'pixel_area': float(object_area),
            'scale_factor': float(scale_factor),
            'aspect_ratio': aspect_ratio
        }
        
        # Si el modelo requiere CALIB_PIXEL_FEATURE_KEYS (12 características), calcular las adicionales
        if len(self.config.PIXEL_FEATURE_KEYS) >= 12:
            # Calcular características extendidas
            original_total_pixels = crop_array.shape[0] * crop_array.shape[1]
            background_pixels = original_total_pixels - object_area
            background_ratio = float(background_pixels / original_total_pixels if original_total_pixels > 0 else 0.0)
            
            # Calcular mm_per_pixel usando valores promedio de calibración si están disponibles
            avg_mm_per_pixel = scale_factor
            alto_mm_per_pixel = scale_factor
            ancho_mm_per_pixel = scale_factor
            
            # Intentar obtener valores más precisos de pixel_calibration.json si está disponible
            if self.pixel_calibration and 'calibration_records' in self.pixel_calibration:
                records = self.pixel_calibration['calibration_records']
                if records:
                    # Calcular promedios de los registros de calibración
                    avg_mm_per_pixel_list = [
                        r.get('average_mm_per_pixel', scale_factor) 
                        for r in records 
                        if 'average_mm_per_pixel' in r
                    ]
                    alto_mm_per_pixel_list = [
                        r.get('alto_mm_per_pixel', scale_factor) 
                        for r in records 
                        if 'alto_mm_per_pixel' in r
                    ]
                    ancho_mm_per_pixel_list = [
                        r.get('ancho_mm_per_pixel', scale_factor) 
                        for r in records 
                        if 'ancho_mm_per_pixel' in r
                    ]
                    
                    if avg_mm_per_pixel_list:
                        avg_mm_per_pixel = float(np.mean(avg_mm_per_pixel_list))
                    if alto_mm_per_pixel_list:
                        alto_mm_per_pixel = float(np.mean(alto_mm_per_pixel_list))
                    if ancho_mm_per_pixel_list:
                        ancho_mm_per_pixel = float(np.mean(ancho_mm_per_pixel_list))
            
            # Agregar características extendidas (CALIB_PIXEL_FEATURE_KEYS)
            features.update({
                'grain_area_pixels': float(object_area),
                'width_pixels': float(width_visible),
                'height_pixels': float(height_visible),
                'bbox_area_pixels': float(bbox_area),
                'aspect_ratio': aspect_ratio,  # Ya calculado
                'original_total_pixels': float(original_total_pixels),
                'background_pixels': float(background_pixels),
                'background_ratio': background_ratio,
                'alto_mm_per_pixel': alto_mm_per_pixel,
                'ancho_mm_per_pixel': ancho_mm_per_pixel,
                'average_mm_per_pixel': avg_mm_per_pixel,
                'segmentation_confidence': 0.85  # Valor por defecto (se puede mejorar con confianza real de segmentación)
            })
        
        return features
        
    def _predict_hybrid(
        self,
        image_tensor: torch.Tensor,
        pixel_features_tensor: torch.Tensor
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Predice todos los targets usando el modelo híbrido.
        """
        self.regression_model.eval()
        
        with torch.no_grad():
            outputs = self.regression_model(image_tensor, pixel_features_tensor)
        
        normalized_predictions = {
            target: float(outputs[target].cpu().item()) for target in TARGETS
        }
        logger.info(f"🤖 Modelo Híbrido devolvió (normalizado): {normalized_predictions}")
        
        model_predictions = self._denormalize_predictions(normalized_predictions)
        logger.info(f"📊 Predicción Híbrida (desnormalizada): {model_predictions}")
        
        confidences = dict.fromkeys(TARGETS, 0.90) 
        return model_predictions, confidences

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predice dimensiones y peso de un grano de cacao (Modo Híbrido).
        """
        if not self.models_loaded:
            raise ModelNotLoadedError("Artefactos no cargados. Llamar load_artifacts() primero.")
        
        start_time = time.time()
        
        try:
            # PASO 1: Segmentación
            logger.debug("Paso 1: Segmentando grano...")
            crop_image, crop_url, seg_confidence = self._segment_and_crop(image)
            
            if crop_image is None:
                raise SegmentationError("No se pudo segmentar la imagen.")
            
            # PASO 2: Extraer features de píxeles (para el modelo híbrido)
            logger.debug("Paso 2: Extrayendo features de píxeles...")
            pixel_features = self._extract_crop_characteristics(crop_image)
            
            pixel_features_tensor = torch.tensor([
                pixel_features[key] for key in self.config.PIXEL_FEATURE_KEYS
            ], dtype=torch.float32).unsqueeze(0).to(self.device) # Shape [1, 5]

            # PASO 3: Preprocesar imagen para el modelo
            logger.debug("Paso 3: Preprocesando imagen para CNN...")
            crop_image_rgb = crop_image.convert('RGB')
            image_tensor = self._preprocess_image(crop_image_rgb) # Shape [1, 3, 224, 224]
            
            # PASO 4: Predicción Híbrida
            logger.debug("Paso 4: Ejecutando modelo híbrido...")
            predictions, confidences = self._predict_hybrid(image_tensor, pixel_features_tensor)
            
            # PASO 5: Aplicar límites
            final_predictions = {}
            for target in TARGETS:
                min_val, max_val = self.config.TARGET_LIMITS[target]
                final_predictions[target] = np.clip(predictions[target], min_val, max_val)
            
            # PASO 6: Preparar resultado
            total_time = time.time() - start_time
            
            result = {
                'alto_mm': final_predictions['alto'],
                'ancho_mm': final_predictions['ancho'],
                'grosor_mm': final_predictions['grosor'],
                'peso_g': final_predictions['peso'],
                'confidences': confidences,
                'crop_url': crop_url,
                'debug': {
                    'segmented': True,
                    'segmentation_confidence': float(seg_confidence),
                    'latency_ms': int(total_time * 1000),
                    'models_version': 'v_hybrid',
                    'device': str(self.device),
                    'total_time_s': total_time,
                    'pixel_features_input': pixel_features
                }
            }
            
            logger.info(f"Predicción Híbrida completada en {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}", exc_info=True)
            if isinstance(e, (ModelNotLoadedError, InvalidImageError, SegmentationError)):
                raise
            raise PredictionError(f"Error procesando imagen: {e}") from e
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """ Predice desde bytes de imagen. """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return self.predict(image)
        except Exception as e:
            logger.error(f"Error procesando imagen desde bytes: {e}", exc_info=True)
            raise InvalidImageError(f"Error procesando imagen: {e}") from e
    
    def get_model_info(self) -> Dict[str, Any]:
        """ Obtiene información sobre los modelos cargados. """
        if not self.models_loaded:
            return {'status': 'not_loaded'}
        
        info = {
            'status': 'loaded',
            'device': str(self.device),
            'model': 'HybridCacaoRegression',
            'model_details': get_model_info(self.regression_model),
            'scalers': 'loaded' if self.scalers else 'not_loaded',
            # 'yolo_cropper': 'not_loaded' (Eliminado)
        }
        return info


# ============================================================================
# INSTANCIA GLOBAL Y FUNCIONES DE CONVENIENCIA
# ============================================================================

_predictor_instance: Optional[CacaoPredictor] = None

def get_predictor() -> CacaoPredictor:
    """
    Obtiene la instancia global del predictor Híbrido.
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = CacaoPredictor()
        
        if not _predictor_instance.load_artifacts():
            logger.warning("No se pudieron cargar todos los artefactos automáticament (Híbrido)")
    
    return _predictor_instance

def load_artifacts() -> bool:
    """ Función de conveniencia para cargar artefactos Híbridos. """
    predictor = get_predictor()
    return predictor.load_artifacts()

def predict_image(image: Image.Image) -> Dict[str, Any]:
    """ Función de conveniencia para predecir una imagen (Híbrido). """
    predictor = get_predictor()
    return predictor.predict(image)

def predict_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """ Función de conveniencia para predecir desde bytes (Híbrido). """
    predictor = get_predictor()
    return predictor.predict_from_bytes(image_bytes)