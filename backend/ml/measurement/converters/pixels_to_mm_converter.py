"""
Convertidor de píxeles a milímetros para medición de granos de cacao.

Este módulo maneja la conversión de medidas en píxeles a dimensiones reales
en milímetros para granos de cacao,
siguiendo el principio de Responsabilidad Única.
"""
from ..models import CalibrationParams
from .base_converter import ConvertidorBase
from .validators.calibration_validator import ValidadorCalibracion
from ...utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.converters")


class ConvertidorPixelesAMm(ConvertidorBase):
    """Convertidor de píxeles a milímetros para granos de cacao."""
    
    def convert(self, pixels: float) -> float:
        """
        Convierte píxeles a milímetros para medición de granos de cacao.
        
        Args:
            pixels: Valor en píxeles (medidas de granos de cacao)
            
        Returns:
            Valor en milímetros (dimensiones reales de granos de cacao)
        """
        ValidadorCalibracion.validar_calibracion(self.calibration_params)
        
        if pixels < 0:
            logger.warning(f"Valor negativo en píxeles: {pixels}")
        
        result = pixels / self.pixels_per_mm
        logger.debug(f"Conversión: {pixels} px → {result:.3f} mm")
        return result


# Compatibilidad hacia atrás
PixelsToMillimetersConverter = ConvertidorPixelesAMm

