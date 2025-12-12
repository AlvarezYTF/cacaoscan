"""
Convertidor de milímetros a píxeles para medición de granos de cacao.

Este módulo maneja la conversión de dimensiones reales en milímetros
a medidas en píxeles para granos de cacao,
siguiendo el principio de Responsabilidad Única.
"""
from ..models import CalibrationParams
from .base_converter import ConvertidorBase
from .validators.calibration_validator import ValidadorCalibracion
from ...utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.converters")


class ConvertidorMmAPixeles(ConvertidorBase):
    """Convertidor de milímetros a píxeles para granos de cacao."""
    
    def convert(self, mm: float) -> float:
        """
        Convierte milímetros a píxeles para medición de granos de cacao.
        
        Args:
            mm: Valor en milímetros (dimensiones reales de granos de cacao)
            
        Returns:
            Valor en píxeles (medidas de granos de cacao)
        """
        ValidadorCalibracion.validar_calibracion(self.calibration_params)
        
        if mm < 0:
            logger.warning(f"Valor negativo en milímetros: {mm}")
        
        result = mm * self.pixels_per_mm
        logger.debug(f"Conversión: {mm} mm → {result:.3f} px")
        return result


# Compatibilidad hacia atrás
MillimetersToPixelsConverter = ConvertidorMmAPixeles

