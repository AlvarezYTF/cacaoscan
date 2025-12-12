"""
Utilidades de almacenamiento para parámetros de calibración.

Este módulo proporciona almacenamiento de calibración siguiendo
principios SOLID con separación de responsabilidades.
"""

from .almacenamiento_calibracion import AlmacenamientoCalibracion

# Compatibilidad hacia atrás
CalibrationStorage = AlmacenamientoCalibracion

__all__ = [
    'AlmacenamientoCalibracion',
    'CalibrationStorage'  # Alias para compatibilidad
]

