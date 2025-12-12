"""
Extractor de features de píxeles con area_mm2 y perimeter_mm.

Este módulo maneja la extracción y normalización de features de píxeles,
siguiendo el principio de Responsabilidad Única.
"""
from pathlib import Path
from typing import Dict, Optional
import numpy as np
from sklearn.preprocessing import RobustScaler
import json

from ...utils.logs import get_ml_logger
from ...utils.paths import get_datasets_dir
from ..processors.feature_builder import PixelFeatureBuilder

logger = get_ml_logger("cacaoscan.ml.data.extractores")


class ExtractorFeaturesPixel:
    """
    Extrae y normaliza features de píxeles incluyendo area_mm2 y perimeter_mm.
    
    Features extraídas:
    1. area_mm2 = grain_area_pixels * (average_mm_per_pixel ** 2)
    2. width_mm = width_pixels * average_mm_per_pixel
    3. height_mm = height_pixels * average_mm_per_pixel
    4. perimeter_mm = (width_pixels + height_pixels) * average_mm_per_pixel * 2
    5. aspect_ratio
    6. bbox_to_area_ratio = grain_area_pixels / bbox_area_pixels
    7. background_ratio
    8. average_mm_per_pixel
    """
    
    NOMBRES_FEATURES = [
        "area_mm2",
        "width_mm",
        "height_mm",
        "perimeter_mm",
        "aspect_ratio",
        "bbox_to_area_ratio",
        "background_ratio",
        "average_mm_per_pixel"
    ]
    
    def __init__(
        self,
        calibration_file: Optional[Path] = None,
        quantile_range: tuple[float, float] = (0.1, 0.9)
    ):
        """
        Inicializa el extractor.
        
        Args:
            calibration_file: Ruta a pixel_calibration.json
            quantile_range: Rango de cuantiles para RobustScaler (por defecto: percentil 10-90)
        """
        if calibration_file is None:
            calibration_file = get_datasets_dir() / "pixel_calibration.json"
        
        self.calibration_file = Path(calibration_file)
        self.quantile_range = quantile_range
        self.scaler = RobustScaler(quantile_range=quantile_range)
        self.features_by_id: Dict[int, np.ndarray] = {}
        self._loaded = False
        self._fitted = False
        
        # Inicializar constructor de features
        self.feature_builder = PixelFeatureBuilder()
    
    def _extraer_valores_registro(self, record: dict) -> tuple:
        """
        Extrae y retorna valores crudos del registro de calibración.
        
        Args:
            record: Registro de calibración
            
        Returns:
            Tupla de valores extraídos
        """
        pixel_meas = record.get("pixel_measurements", {})
        scale_factors = record.get("scale_factors", {})
        bg_info = record.get("background_info", {})
        
        return (
            float(scale_factors.get("average_mm_per_pixel", 0.0)),
            float(pixel_meas.get("width_pixels", 0.0)),
            float(pixel_meas.get("height_pixels", 0.0)),
            float(pixel_meas.get("grain_area_pixels", 0.0)),
            float(pixel_meas.get("bbox_area_pixels", 0.0)),
            float(pixel_meas.get("aspect_ratio", 0.0)),
            float(bg_info.get("background_ratio", 0.0))
        )
    
    def _calcular_features(
        self,
        avg_mm_per_pixel: float,
        width_pixels: float,
        height_pixels: float,
        grain_area_pixels: float,
        bbox_area_pixels: float,
        aspect_ratio: float,
        background_ratio: float
    ) -> np.ndarray:
        """
        Calcula y retorna vector de features a partir de mediciones de píxeles.
        
        Args:
            avg_mm_per_pixel: Promedio de mm por píxel
            width_pixels: Ancho en píxeles
            height_pixels: Alto en píxeles
            grain_area_pixels: Área del grano en píxeles
            bbox_area_pixels: Área del bounding box en píxeles
            aspect_ratio: Relación de aspecto
            background_ratio: Ratio de fondo
            
        Returns:
            Array de features
        """
        area_mm2 = grain_area_pixels * (avg_mm_per_pixel ** 2)
        width_mm = width_pixels * avg_mm_per_pixel
        height_mm = height_pixels * avg_mm_per_pixel
        perimeter_mm = (width_pixels + height_pixels) * avg_mm_per_pixel * 2
        bbox_to_area_ratio = (
            grain_area_pixels / bbox_area_pixels
            if bbox_area_pixels > 0 else 0.0
        )
        
        return np.array([
            area_mm2,
            width_mm,
            height_mm,
            perimeter_mm,
            aspect_ratio,
            bbox_to_area_ratio,
            background_ratio,
            avg_mm_per_pixel
        ], dtype=np.float32)
    
    def _procesar_registro_calibracion(self, record: dict) -> tuple:
        """
        Procesa un registro de calibración individual.
        Retorna (record_id, features) o (None, None) si es inválido.
        
        Args:
            record: Registro de calibración
            
        Returns:
            Tupla (record_id, features) o (None, None)
        """
        try:
            record_id = int(record["id"])
            
            avg_mm_per_pixel, width_pixels, height_pixels, grain_area_pixels, \
                bbox_area_pixels, aspect_ratio, background_ratio = self._extraer_valores_registro(record)
            
            if avg_mm_per_pixel <= 0 or width_pixels <= 0 or height_pixels <= 0:
                return None, None
            
            features = self._calcular_features(
                avg_mm_per_pixel, width_pixels, height_pixels,
                grain_area_pixels, bbox_area_pixels, aspect_ratio, background_ratio
            )
            
            if not np.all(np.isfinite(features)):
                logger.warning(f"Features inválidas para ID {record_id}")
                return None, None
            
            return record_id, features
            
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Error procesando registro {record.get('id', 'unknown')}: {e}")
            return None, None
    
    def load(self) -> bool:
        """
        Carga datos de calibración y extrae features.
        
        Returns:
            True si se cargó exitosamente
        """
        if not self.calibration_file.exists():
            logger.warning(f"Archivo de calibración de píxeles no encontrado: {self.calibration_file}")
            return False
        
        try:
            # Cargar JSON con múltiples codificaciones
            with open(self.calibration_file, 'rb') as f:
                raw_content = f.read()
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                text_content = None
                for encoding in encodings:
                    try:
                        text_content = raw_content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if text_content is None:
                    text_content = raw_content.decode('utf-8', errors='ignore')
                calibration_data = json.loads(text_content)
            
            calibration_records = calibration_data.get("calibration_records", [])
            
            if not calibration_records:
                logger.warning("No se encontraron registros de calibración")
                return False
            
            logger.info(f"Cargando {len(calibration_records)} registros de calibración")
            
            all_features = []
            valid_ids = []
            
            for record in calibration_records:
                record_id, features = self._procesar_registro_calibracion(record)
                if record_id is not None and features is not None:
                    self.features_by_id[record_id] = features
                    all_features.append(features)
                    valid_ids.append(record_id)
            
            # Ajustar escalador
            if all_features:
                all_features_array = np.array(all_features, dtype=np.float32)
                self.scaler.fit(all_features_array)
                self._fitted = True
                
                # Normalizar features
                for record_id, features in zip(valid_ids, all_features):
                    normalized = self.scaler.transform(features.reshape(1, -1))[0]
                    self.features_by_id[record_id] = normalized
                
                logger.info(
                    f"Features de píxeles cargadas y normalizadas para {len(self.features_by_id)} registros"
                )
                self._loaded = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cargando calibración de píxeles: {e}")
            return False
    
    def get_features(self, record_id: int) -> Optional[np.ndarray]:
        """
        Obtiene features normalizadas para un ID de registro.
        
        Args:
            record_id: ID de registro
            
        Returns:
            Array de features normalizadas (8 features) o None
        """
        if not self._loaded:
            self.load()
        
        return self.features_by_id.get(record_id)
    
    def get_feature_dim(self) -> int:
        """
        Obtiene la dimensión de features.
        
        Returns:
            Número de features
        """
        return len(self.NOMBRES_FEATURES)

