"""
Cargador de features de calibración de píxeles desde pixel_calibration.json.

Este módulo maneja la carga de features de píxeles,
siguiendo el principio de Responsabilidad Única.
"""
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, Sequence
import numpy as np

from ...utils.logs import get_ml_logger
from ...utils.paths import get_datasets_dir
from ...utils.io import load_json
from ..processors.feature_builder import PixelFeatureBuilder

logger = get_ml_logger("cacaoscan.ml.data.cargadores")


class CargadorFeaturesPixel:
    """
    Cargador que mapea ID → features de píxeles normalizados desde pixel_calibration.json.
    
    Features generadas:
    1. height_mm_est: height_pixels * avg_mm_per_pixel
    2. width_mm_est: width_pixels * avg_mm_per_pixel
    3. area_mm2_est: grain_area_pixels * (avg_mm_per_pixel²)
    4. perimeter_mm
    5. aspect_ratio
    6. bbox_ratio
    7. background_ratio
    8. avg_mm_per_pixel
    9. compactness
    10. roundness
    """
    
    NOMBRES_FEATURES = [
        "height_mm_est",
        "width_mm_est",
        "area_mm2_est",
        "perimeter_mm",
        "aspect_ratio",
        "bbox_ratio",
        "background_ratio",
        "avg_mm_per_pixel",
        "compactness",
        "roundness"
    ]
    
    def __init__(self, calibration_file: Optional[Path] = None):
        """
        Inicializa el cargador.
        
        Args:
            calibration_file: Ruta a pixel_calibration.json. Si es None, usa ruta por defecto.
        """
        if calibration_file is None:
            calibration_file = get_datasets_dir() / "pixel_calibration.json"
        
        self.calibration_file = Path(calibration_file)
        self.features_by_id: Dict[int, np.ndarray] = {}
        self.features_by_filename: Dict[str, np.ndarray] = {}
        self._loaded = False
        
        # Inicializar constructor de features
        self.feature_builder = PixelFeatureBuilder()
        
    def load(self) -> bool:
        """
        Carga calibración de píxeles y genera features.
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        if not self.calibration_file.exists():
            logger.warning(f"Archivo de calibración de píxeles no encontrado: {self.calibration_file}")
            return False
        
        try:
            calibration_data = load_json(self.calibration_file)
            calibration_records = calibration_data.get("calibration_records", [])
            if not calibration_records:
                logger.warning("No se encontraron registros de calibración en pixel_calibration.json")
                return False
            
            logger.info(f"Cargando {len(calibration_records)} registros de calibración")
            self._reiniciar_mapas_features()
            self._procesar_registros(calibration_records)
            
            self._loaded = True
            logger.info(f"Features de píxeles cargadas para {len(self.features_by_id)} registros")
            return True
        except Exception as exc:
            logger.error(f"Error cargando calibración de píxeles: {exc}")
            return False
    
    def get_features_by_id(self, record_id: int) -> Optional[np.ndarray]:
        """
        Obtiene features para un ID de registro.
        
        Args:
            record_id: ID de registro
            
        Returns:
            Array de features (10 features) o None si no se encuentra
        """
        if not self._loaded:
            self.load()
        
        return self.features_by_id.get(record_id)
    
    def get_features_by_filename(self, filename: str) -> Optional[np.ndarray]:
        """
        Obtiene features para un nombre de archivo (sin extensión).
        
        Args:
            filename: Nombre de archivo (ej: "510" o "510.bmp")
            
        Returns:
            Array de features (10 features) o None si no se encuentra
        """
        if not self._loaded:
            self.load()
        
        # Remover extensión si está presente
        filename_base = Path(filename).stem
        return self.features_by_filename.get(filename_base)
    
    def get_all_features(self) -> Tuple[Dict[int, np.ndarray], Dict[str, np.ndarray]]:
        """
        Obtiene todas las features cargadas.
        
        Returns:
            Tupla de (features_by_id, features_by_filename)
        """
        if not self._loaded:
            self.load()
        
        return self.features_by_id, self.features_by_filename
    
    def validate_record(self, record_id: int, filename: Optional[str] = None) -> bool:
        """
        Valida que un registro exista en los datos de calibración.
        
        Args:
            record_id: ID de registro a validar
            filename: Nombre de archivo opcional a validar
            
        Returns:
            True si el registro existe, False en caso contrario
        """
        if not self._loaded:
            self.load()
        
        has_id = record_id in self.features_by_id
        
        if filename:
            filename_base = Path(filename).stem
            has_filename = filename_base in self.features_by_filename
            return has_id and has_filename
        
        return has_id
    
    def get_missing_records(self, record_ids: list[int]) -> list[int]:
        """
        Obtiene lista de IDs de registros que faltan en los datos de calibración.
        
        Args:
            record_ids: Lista de IDs de registros a verificar
            
        Returns:
            Lista de IDs de registros faltantes
        """
        if not self._loaded:
            self.load()
        
        missing = [rid for rid in record_ids if rid not in self.features_by_id]
        return missing

    def _reiniciar_mapas_features(self) -> None:
        """Limpia mapas de features en caché antes de recargar."""
        self.features_by_id.clear()
        self.features_by_filename.clear()

    def _procesar_registros(self, calibration_records: Sequence[Dict[str, Any]]) -> None:
        """
        Procesa cada registro de calibración independientemente.
        
        Args:
            calibration_records: Secuencia de registros de calibración
        """
        for record in calibration_records:
            self._procesar_registro_unico(record)

    def _procesar_registro_unico(self, record: Dict[str, Any]) -> None:
        """
        Transforma un registro único en vectores de features.
        
        Args:
            record: Registro de calibración
        """
        try:
            record_id = int(record["id"])
        except (KeyError, TypeError, ValueError):
            logger.warning("Registro de calibración sin campo 'id' válido")
            return
        
        filename = str(record.get("filename", "") or "")
        pixel_meas = self._como_dict(record.get("pixel_measurements"))
        scale_factors = self._como_dict(record.get("scale_factors"))
        bg_info = self._como_dict(record.get("background_info"))
        
        # Usar constructor de features para calcular features
        features = self.feature_builder.build_features(
            pixel_measurements=pixel_meas,
            scale_factors=scale_factors,
            background_info=bg_info,
            record_id=record_id
        )
        
        if features is not None:
            self._almacenar_features(record_id, filename, features)

    @staticmethod
    def _como_dict(value: Optional[Any]) -> Dict[str, Any]:
        """
        Asegura que objetos anidados se traten como diccionarios.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Diccionario
        """
        if isinstance(value, dict):
            return value
        return {}

    def _almacenar_features(self, record_id: int, filename: str, features: np.ndarray) -> None:
        """
        Persiste las features calculadas para ID y nombre de archivo.
        
        Args:
            record_id: ID de registro
            filename: Nombre de archivo
            features: Array de features
        """
        self.features_by_id[record_id] = features
        if not filename:
            return
        filename_base = Path(filename).stem
        self.features_by_filename[filename_base] = features

