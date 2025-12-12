"""
Orquestador de conversión de unidades para medición de granos de cacao.

Este módulo orquesta los convertidores específicos para proporcionar
una interfaz unificada de conversión bidireccional,
siguiendo principios SOLID.
"""
from typing import Optional

from ..models import CalibrationParams
from .pixels_to_mm_converter import ConvertidorPixelesAMm
from .mm_to_pixels_converter import ConvertidorMmAPixeles
from ...utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.converters")


class ConvertidorUnidades:
    """
    Orquestador de conversión de unidades para granos de cacao.
    
    Esta clase coordina los convertidores específicos para proporcionar
    conversión bidireccional entre píxeles y milímetros.
    """
    
    def __init__(self, calibration_params: Optional[CalibrationParams] = None):
        """
        Inicializa el orquestador de conversión.
        
        Args:
            calibration_params: Parámetros de calibración para granos de cacao
        """
        self._calibration_params: Optional[CalibrationParams] = calibration_params
        self._pixels_to_mm_converter: Optional[ConvertidorPixelesAMm] = None
        self._mm_to_pixels_converter: Optional[ConvertidorMmAPixeles] = None
        
        if calibration_params:
            self._initialize_converters()
    
    def set_calibration(self, calibration_params: CalibrationParams) -> None:
        """
        Establece los parámetros de calibración y reinicializa convertidores.
        
        Args:
            calibration_params: Parámetros de calibración para granos de cacao
        """
        self._calibration_params = calibration_params
        self._initialize_converters()
        logger.info(f"Calibración actualizada: {calibration_params.pixels_per_mm:.3f} px/mm")
    
    def _initialize_converters(self) -> None:
        """Inicializa los convertidores específicos con la calibración actual."""
        if not self._calibration_params:
            return
        
        self._pixels_to_mm_converter = ConvertidorPixelesAMm(self._calibration_params)
        self._mm_to_pixels_converter = ConvertidorMmAPixeles(self._calibration_params)
    
    def convert_pixels_to_mm(self, pixels: float) -> float:
        """
        Convierte píxeles a milímetros para medición de granos de cacao.
        
        Args:
            pixels: Valor en píxeles (medidas de granos de cacao)
            
        Returns:
            Valor en milímetros (dimensiones reales de granos de cacao)
        """
        if not self._pixels_to_mm_converter:
            raise ValueError("No hay calibración cargada")
        
        return self._pixels_to_mm_converter.convert(pixels)
    
    def convert_mm_to_pixels(self, mm: float) -> float:
        """
        Convierte milímetros a píxeles para medición de granos de cacao.
        
        Args:
            mm: Valor en milímetros (dimensiones reales de granos de cacao)
            
        Returns:
            Valor en píxeles (medidas de granos de cacao)
        """
        if not self._mm_to_pixels_converter:
            raise ValueError("No hay calibración cargada")
        
        return self._mm_to_pixels_converter.convert(mm)
    
    @property
    def calibration_params(self) -> Optional[CalibrationParams]:
        """Obtiene los parámetros de calibración actuales."""
        return self._calibration_params


# Compatibilidad hacia atrás
UnitConverter = ConvertidorUnidades
