"""
Almacenamiento de parámetros de calibración.

Este módulo maneja la persistencia de parámetros de calibración,
siguiendo principios SOLID:
- Single Responsibility: solo persistencia, no serialización
- Dependency Inversion: implementa IAlmacenamientoCalibracion
"""
from pathlib import Path
from typing import Optional

from ...utils.logs import get_ml_logger
from ...utils.io import save_json, load_json
from ..models import CalibrationParams
from .serializadores import SerializadorCalibracion

logger = get_ml_logger("cacaoscan.ml.measurement.storage")


class AlmacenamientoCalibracion:
    """
    Almacenamiento de parámetros de calibración.
    
    Responsabilidad única: persistencia de archivos.
    La serialización está delegada a SerializadorCalibracion (SRP).
    """
    
    def __init__(self, calibration_dir: Path):
        """
        Inicializa el almacenamiento de calibración.
        
        Args:
            calibration_dir: Directorio para archivos de calibración
        """
        self.calibration_dir = calibration_dir
        self.calibration_file = calibration_dir / "current_calibration.json"
        self.serializador = SerializadorCalibracion()
    
    def save(self, calibration_params: CalibrationParams) -> None:
        """
        Guarda parámetros de calibración.
        
        Args:
            calibration_params: Parámetros de calibración a guardar
        """
        calibration_data = self.serializador.serializar(calibration_params)
        save_json(calibration_data, self.calibration_file)
        logger.info(f"Calibración guardada: {calibration_params.pixels_per_mm:.3f} pixels/mm")
    
    def load(self) -> Optional[CalibrationParams]:
        """
        Carga parámetros de calibración guardados.
        
        Returns:
            Parámetros de calibración o None si no existen
        """
        if not self.calibration_file.exists():
            logger.warning("Archivo de calibración no encontrado")
            return None
        
        try:
            calibration_data = load_json(self.calibration_file)
            calibration_params = self.serializador.deserializar(calibration_data)
            
            if calibration_params:
                logger.info(f"Calibración cargada: {calibration_params.pixels_per_mm:.3f} pixels/mm")
            
            return calibration_params
            
        except Exception as e:
            logger.error(f"Error cargando calibración: {e}")
            return None

