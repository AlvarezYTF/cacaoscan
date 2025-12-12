"""
Utilidades de validación de calibración para granos de cacao.

Este módulo proporciona validación de calibración siguiendo
principios SOLID con separación de responsabilidades.
"""

from .validador_calibracion import ValidadorCalibracion

# Compatibilidad hacia atrás
CalibrationValidator = ValidadorCalibracion

__all__ = [
    'ValidadorCalibracion',
    'CalibrationValidator'  # Alias para compatibilidad
]

