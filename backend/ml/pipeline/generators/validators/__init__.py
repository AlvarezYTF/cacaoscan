"""
Validadores de calidad de recortes para granos de cacao.

Este módulo proporciona validadores de recortes siguiendo
principios SOLID con separación de responsabilidades.
"""

from .validador_recorte import ValidadorRecorte
from .crop_validator import CropValidator  # Compatibilidad hacia atrás
from .interfaces import IValidadorRecorte
from .cargadores import CargadorImagen
from .validadores import ValidadorDimensiones, ValidadorCanalAlpha

# Compatibilidad hacia atrás
CropValidator = ValidadorRecorte

__all__ = [
    # Nombres en español
    'ValidadorRecorte',
    'IValidadorRecorte',
    'CargadorImagen',
    'ValidadorDimensiones',
    'ValidadorCanalAlpha',
    # Compatibilidad hacia atrás
    'CropValidator'
]

