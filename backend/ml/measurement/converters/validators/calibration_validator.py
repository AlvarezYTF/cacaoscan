"""
Validador de calibración para conversión de unidades de granos de cacao.

Este módulo valida que exista calibración antes de realizar conversiones,
siguiendo el principio de Responsabilidad Única.
"""
from typing import Optional

from ...models import CalibrationParams
from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.converters.validators")


class ValidadorCalibracion:
    """Validador de parámetros de calibración para granos de cacao."""
    
    @staticmethod
    def validar_calibracion(calibration_params: Optional[CalibrationParams]) -> None:
        """
        Valida que existan parámetros de calibración.
        
        Args:
            calibration_params: Parámetros de calibración a validar
            
        Raises:
            ValueError: Si no hay calibración cargada
        """
        if not calibration_params:
            logger.error("Intento de conversión sin calibración cargada")
            raise ValueError("No hay calibración cargada")
        
        if calibration_params.pixels_per_mm <= 0:
            logger.error(f"Parámetro de calibración inválido: pixels_per_mm={calibration_params.pixels_per_mm}")
            raise ValueError(f"Parámetro de calibración inválido: pixels_per_mm debe ser mayor que 0")
    
    @staticmethod
    def validate_calibration(calibration_params: Optional[CalibrationParams]) -> None:
        """Alias de compatibilidad hacia atrás para validar_calibracion."""
        return ValidadorCalibracion.validar_calibracion(calibration_params)


# Compatibilidad hacia atrás
CalibrationValidator = ValidadorCalibracion

