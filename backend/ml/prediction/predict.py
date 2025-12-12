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
from ..segmentation.processor import SegmentationError
from ..segmentation.cacao_segmentation_model import CacaoSegmentationModel
from ..regression.models import create_model, TARGETS, get_model_info
from ..regression.scalers import load_scalers, CacaoScalers
from .base_predictor import PredictorBase

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

class PredictorCacao(PredictorBase):
    """
    Predictor unificado para granos de cacao (Versión Híbrida).
    
    Hereda de BasePredictor y añade funcionalidad específica para modelos híbridos
    que combinan ResNet18, ConvNeXt y features de píxeles.
    """
    
    def __init__(self, confidence_threshold: float = 0.5, config: Optional[PredictionConfig] = None):
        """
        Inicializa el predictor híbrido.
        
        Migrado a YOLO-Seg para segmentación más precisa y reducción de falsos positivos.
        """
        self.config = config or CONFIG
        
        # Initialize base predictor with config values
        super().__init__(
            confidence_threshold=confidence_threshold,
            image_size=self.config.IMAGE_SIZE,
            imagenet_mean=self.config.IMAGENET_MEAN,
            imagenet_std=self.config.IMAGENET_STD
        )
        
        # Specific to hybrid predictor
        self.pixel_calibration: Optional[Dict[str, Any]] = None
        self._load_pixel_calibration()
        
        # Inicializar modelo de segmentación YOLO-Seg (lazy loading)
        self.segmentation_model: Optional[CacaoSegmentationModel] = None
        
        self._setup_directories()
        
        logger.info(f"PredictorCacao initialized (device={self.device})")

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
    
    # _get_device() is now inherited from BasePredictor
    
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
            
            if not self._load_regression_model():
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

    def _load_regression_model(self) -> bool:
        """Carga el modelo híbrido desde disco."""
        model_path = get_regressors_artifacts_dir() / "hybrid.pt"
        if not model_path.exists():
            logger.error(f"Modelo Híbrido 'hybrid.pt' no encontrado en: {model_path}")
            return False
        
        try:
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
            pixel_feature_dim, pixel_feature_keys = self._resolve_pixel_feature_dim(checkpoint)
            self.config.PIXEL_FEATURE_KEYS = pixel_feature_keys
            
            self.regression_model = create_model(
                model_type="hybrid",
                pretrained=False,
                dropout_rate=0.2,
                hybrid=True,
                use_pixel_features=True,
                pixel_feature_dim=pixel_feature_dim
            )
            state_dict = checkpoint.get('model_state_dict')
            if not state_dict:
                raise ValueError("Checkpoint no contiene 'model_state_dict'")
            
            self.regression_model.load_state_dict(state_dict)
            self.regression_model.to(self.device)
            self.regression_model.eval()
            logger.info(
                f"✅ Modelo Híbrido (hybrid.pt) cargado exitosamente con {pixel_feature_dim} características de píxeles"
            )
            return True
        except Exception as exc:
            logger.error(f"Error cargando modelo híbrido: {exc}", exc_info=True)
            return False

    def _resolve_pixel_feature_dim(self, checkpoint: Dict[str, Any]) -> Tuple[int, List[str]]:
        """Determina la dimensionalidad de features de píxeles."""
        from ..pipeline.train_all import CALIB_PIXEL_FEATURE_KEYS, PIXEL_FEATURE_KEYS
        
        detected_dim = self._detect_dim_from_checkpoint(checkpoint)
        if detected_dim == len(CALIB_PIXEL_FEATURE_KEYS):
            logger.info(f"✅ Usando CALIB_PIXEL_FEATURE_KEYS ({detected_dim} características)")
            return detected_dim, CALIB_PIXEL_FEATURE_KEYS
        if detected_dim == len(PIXEL_FEATURE_KEYS):
            logger.info(f"✅ Usando PIXEL_FEATURE_KEYS ({detected_dim} características)")
            return detected_dim, PIXEL_FEATURE_KEYS
        
        fallback_keys = self._fallback_pixel_feature_keys(CALIB_PIXEL_FEATURE_KEYS, PIXEL_FEATURE_KEYS)
        return len(fallback_keys), fallback_keys

    def _detect_dim_from_checkpoint(self, checkpoint: Dict[str, Any]) -> Optional[int]:
        """Detecta el número de características de píxeles a partir del checkpoint."""
        state_dict = checkpoint.get('model_state_dict')
        if not state_dict:
            return None
        pixel_weight = state_dict.get('pixel_branch.0.weight')
        if pixel_weight is None:
            logger.warning("⚠️ No se encontró 'pixel_branch.0.weight' en checkpoint, usando valor por defecto")
            return None
        detected_dim = pixel_weight.shape[1]
        logger.info(f"✅ Detectado pixel_feature_dim={detected_dim} desde checkpoint")
        return detected_dim

    def _fallback_pixel_feature_keys(
        self,
        calib_keys: List[str],
        default_keys: List[str]
    ) -> List[str]:
        """Selecciona las llaves de píxeles basadas en la calibración disponible."""
        if self.pixel_calibration and self.pixel_calibration.get('calibration_records'):
            records = self.pixel_calibration['calibration_records']
            if records and any(key in records[0] for key in calib_keys):
                logger.info(f"✅ Usando CALIB_PIXEL_FEATURE_KEYS: {len(calib_keys)} características")
                return calib_keys
        logger.info(f"✅ Usando PIXEL_FEATURE_KEYS por defecto: {len(default_keys)} características")
        return default_keys
    
    # _preprocess_image() is now inherited from BasePredictor
    
    # _denormalize_predictions() is now inherited from BasePredictor

    def _get_segmentation_model(self) -> CacaoSegmentationModel:
        """
        Obtiene el modelo de segmentación YOLO-Seg (lazy loading).
        
        Returns:
            Instancia de CacaoSegmentationModel
        """
        if self.segmentation_model is None:
            logger.info("Inicializando modelo YOLO-Seg para segmentación...")
            self.segmentation_model = CacaoSegmentationModel(
                model_path=None,
                confidence_threshold=0.75
            )
        return self.segmentation_model
    
    def _segment_and_crop(self, image: Image.Image) -> Tuple[Image.Image, str, float]:
        """
        Segmenta y recorta la imagen usando YOLO-Seg.
        
        Migrado a YOLO-Seg para segmentación más precisa y reducción de falsos positivos.
        Las validaciones se realizan dentro de CacaoSegmentationModel.
        
        Args:
            image: Imagen PIL a segmentar
            
        Returns:
            Tupla de (crop_image, crop_url, seg_confidence)
            
        Raises:
            SegmentationError: Si no se detecta un grano válido
        """
        # Obtener modelo de segmentación
        seg_model = self._get_segmentation_model()
        
        # Realizar segmentación y recorte con YOLO-Seg
        crop_image, seg_metadata = seg_model.segment_and_crop(image)
        
        # Extraer confianza de segmentación
        seg_confidence = seg_metadata['confidence']
        
        # Guardar imagen procesada en el directorio estándar
        today = datetime.now()
        output_dir = MEDIA_ROOT / "cacao_images" / "processed" / \
                     f"{today.year}" / f"{today.month:02d}" / f"{today.day:02d}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo único
        output_filename = f"cacao_{uuid.uuid4().hex}.png"
        output_path = output_dir / output_filename
        
        # Guardar imagen
        crop_image.save(output_path, format='PNG')
        
        # Calcular URL relativa
        try:
            relative_path = output_path.relative_to(MEDIA_ROOT.parent)
            crop_url = f"/{relative_path.as_posix()}"
        except Exception:
            crop_url = output_path.as_posix().split("/app")[-1] if "/app" in str(output_path) else f"/{output_path.relative_to(MEDIA_ROOT)}"
        
        logger.info(
            f"[YOLO-Seg] Segmentación completada: "
            f"confidence={seg_confidence:.3f}, "
            f"area={seg_metadata['area_pixels']} píxeles, "
            f"aspect_ratio={seg_metadata['aspect_ratio']:.2f}, "
            f"crop_size={seg_metadata['crop_width']}x{seg_metadata['crop_height']}, "
            f"guardado en: {output_path}"
        )
        
        return crop_image, crop_url, seg_confidence

    def _calculate_pixel_to_mm_scale_factor(self, width_pixels: int, height_pixels: int) -> float:
        """
        Calcula el factor de escala (mm/píxel) basado en la calibración del dataset.
        """
        match_scale = self._find_calibration_match(width_pixels, height_pixels)
        if match_scale is not None:
            return match_scale
        
        stats_scale = self._scale_from_statistics()
        if stats_scale is not None:
            return stats_scale
        
        return self._default_scale_factor()

    def _extract_crop_characteristics(self, crop_image: Image.Image) -> Dict[str, float]:
        """
        Extrae características visuales y de píxeles del GRANO REAL (solo áreas con alpha>0).
        
        Soporta tanto PIXEL_FEATURE_KEYS (5 características) como CALIB_PIXEL_FEATURE_KEYS (12 características).
        """
        crop_array = np.array(crop_image)
        mask = (crop_array[:, :, 3] > 128).astype(np.float32)
        dimensions = self._compute_visible_dimensions(mask, crop_array)
        
        scale_factor = self._calculate_pixel_to_mm_scale_factor(
            dimensions['width_visible'],
            dimensions['height_visible']
        )
        features = self._build_basic_pixel_features(dimensions, scale_factor)
        
        if len(self.config.PIXEL_FEATURE_KEYS) >= 12:
            extended_features = self._build_extended_pixel_features(dimensions, scale_factor)
            features.update(extended_features)
        
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

    def _find_calibration_match(self, width_pixels: int, height_pixels: int) -> Optional[float]:
        """Busca un registro de calibración cercano a las dimensiones detectadas."""
        if not self.pixel_calibration:
            return None
        
        calibration_records = self.pixel_calibration.get('calibration_records', [])
        if not calibration_records:
            return None
        
        best_match = None
        min_distance = float('inf')
        for record in calibration_records:
            measurements = record.get('pixel_measurements', {})
            record_width = measurements.get('width_pixels', 0)
            record_height = measurements.get('height_pixels', 0)
            if record_width <= 0 or record_height <= 0:
                continue
            
            width_diff = abs(record_width - width_pixels) / max(width_pixels, record_width, 1)
            height_diff = abs(record_height - height_pixels) / max(height_pixels, record_height, 1)
            distance = np.sqrt(width_diff ** 2 + height_diff ** 2)
            if distance < min_distance:
                min_distance = distance
                best_match = record
        
        if best_match and min_distance < 0.5:
            scale_factors = best_match.get('scale_factors', {})
            avg_scale = scale_factors.get('average_mm_per_pixel', 0)
            if avg_scale and avg_scale > 0:
                logger.debug(f"📐 Calibración directa: factor={avg_scale:.6f} (ID={best_match.get('id')})")
                return float(avg_scale)
        return None

    def _scale_from_statistics(self) -> Optional[float]:
        """Obtiene el factor de escala promedio desde las estadísticas."""
        if not self.pixel_calibration:
            return None
        
        stats = self.pixel_calibration.get('statistics', {})
        scale_stats = stats.get('scale_factors', {})
        mean_value = scale_stats.get('mean', 0)
        if mean_value and mean_value > 0:
            logger.debug(f"📐 Usando factor promedio de calibración: {mean_value:.6f} mm/píxel")
            return float(mean_value)
        return None

    def _default_scale_factor(self) -> float:
        """Devuelve el factor de escala por defecto con log de advertencia."""
        default_scale = 0.035
        logger.warning(
            f"⚠️ Usando factor de escala por defecto: {default_scale:.6f}. "
            "Calibración no encontrada o sin coincidencias."
        )
        return default_scale

    def _compute_visible_dimensions(self, mask: np.ndarray, crop_array: np.ndarray) -> Dict[str, int]:
        """Calcula dimensiones visibles y áreas a partir del alfa."""
        object_area = int(np.sum(mask > 0))
        y_coords, x_coords = np.nonzero(mask > 0)
        if x_coords.size > 0:
            width_visible = int(x_coords.max() - x_coords.min() + 1)
            height_visible = int(y_coords.max() - y_coords.min() + 1)
        else:
            width_visible = crop_array.shape[1]
            height_visible = crop_array.shape[0]
        bbox_area = width_visible * height_visible
        total_pixels = crop_array.shape[0] * crop_array.shape[1]
        return {
            'width_visible': width_visible,
            'height_visible': height_visible,
            'object_area': object_area,
            'bbox_area': bbox_area,
            'total_pixels': total_pixels
        }

    def _build_basic_pixel_features(
        self,
        dimensions: Dict[str, int],
        scale_factor: float
    ) -> Dict[str, float]:
        """Construye las características básicas de píxeles."""
        width_visible = dimensions['width_visible']
        height_visible = max(dimensions['height_visible'], 1)
        aspect_ratio = float(width_visible / height_visible)
        return {
            'pixel_width': float(width_visible),
            'pixel_height': float(dimensions['height_visible']),
            'pixel_area': float(dimensions['object_area']),
            'scale_factor': float(scale_factor),
            'aspect_ratio': aspect_ratio
        }

    def _build_extended_pixel_features(
        self,
        dimensions: Dict[str, int],
        scale_factor: float
    ) -> Dict[str, float]:
        """Agrega características extendidas para modelos calibrados."""
        original_total_pixels = dimensions['total_pixels']
        object_area = dimensions['object_area']
        background_pixels = original_total_pixels - object_area
        background_ratio = float(
            background_pixels / original_total_pixels if original_total_pixels > 0 else 0.0
        )
        
        avg_mm_per_pixel = self._calibration_average('average_mm_per_pixel', scale_factor)
        alto_mm_per_pixel = self._calibration_average('alto_mm_per_pixel', scale_factor)
        ancho_mm_per_pixel = self._calibration_average('ancho_mm_per_pixel', scale_factor)
        aspect_ratio = float(
            dimensions['width_visible'] / max(dimensions['height_visible'], 1)
        )
        
        return {
            'grain_area_pixels': float(object_area),
            'width_pixels': float(dimensions['width_visible']),
            'height_pixels': float(dimensions['height_visible']),
            'bbox_area_pixels': float(dimensions['bbox_area']),
            'aspect_ratio': aspect_ratio,
            'original_total_pixels': float(original_total_pixels),
            'background_pixels': float(background_pixels),
            'background_ratio': background_ratio,
            'alto_mm_per_pixel': alto_mm_per_pixel,
            'ancho_mm_per_pixel': ancho_mm_per_pixel,
            'average_mm_per_pixel': avg_mm_per_pixel,
            'segmentation_confidence': 0.85
        }

    def _calibration_average(self, key: str, default: float) -> float:
        """Calcula el promedio de un campo de calibración si existe."""
        if not self.pixel_calibration:
            return default
        records = self.pixel_calibration.get('calibration_records', [])
        values = [
            float(record.get(key, default))
            for record in records
            if key in record
        ]
        if not values:
            return default
        return float(np.mean(values))

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predice dimensiones y peso de un grano de cacao (Modo Híbrido).
        """
        self._validate_models_loaded()
        
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
    
    # predict_from_bytes() is now inherited from BasePredictor
    
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

_predictor_instance: Optional[PredictorCacao] = None

def obtener_predictor() -> PredictorCacao:
    """
    Obtiene la instancia global del predictor Híbrido.
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = PredictorCacao()
        
        if not _predictor_instance.load_artifacts():
            logger.warning("No se pudieron cargar todos los artefactos automáticament (Híbrido)")
    
    return _predictor_instance

def load_artifacts() -> bool:
    """ Función de conveniencia para cargar artefactos Híbridos. """
    predictor = obtener_predictor()
    return predictor.load_artifacts()

def predict_image(image: Image.Image) -> Dict[str, Any]:
    """ Función de conveniencia para predecir una imagen (Híbrido). """
    predictor = obtener_predictor()
    return predictor.predict(image)

def predict_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """ Función de conveniencia para predecir desde bytes (Híbrido). """
    predictor = obtener_predictor()
    return predictor.predict_from_bytes(image_bytes)

# Compatibilidad hacia atrás
BasePredictor = PredictorBase
CacaoPredictor = PredictorCacao
get_predictor = obtener_predictor