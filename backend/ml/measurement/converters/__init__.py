"""
Utilidades de conversión de unidades para calibración de granos de cacao.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: validadores, convertidores específicos, orquestador
- Enfocado exclusivamente en granos de cacao
"""

from .unit_converter import ConvertidorUnidades, UnitConverter
from .pixels_to_mm_converter import ConvertidorPixelesAMm, PixelsToMillimetersConverter
from .mm_to_pixels_converter import ConvertidorMmAPixeles, MillimetersToPixelsConverter
from .base_converter import ConvertidorBase, BaseConverter, IConvertidor, IConverter
from .validators import ValidadorCalibracion, CalibrationValidator

__all__ = [
    # Nombres en español
    'ConvertidorUnidades',
    'ConvertidorPixelesAMm',
    'ConvertidorMmAPixeles',
    'ConvertidorBase',
    'IConvertidor',
    'ValidadorCalibracion',
    # Compatibilidad hacia atrás
    'UnitConverter',
    'PixelsToMillimetersConverter',
    'MillimetersToPixelsConverter',
    'BaseConverter',
    'IConverter',
    'CalibrationValidator'
]

