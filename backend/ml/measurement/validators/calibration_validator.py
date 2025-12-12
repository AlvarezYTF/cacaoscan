"""
Compatibilidad hacia atrás para CalibrationValidator.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en validador_calibracion.py.
"""

from .validador_calibracion import ValidadorCalibracion

# Alias para compatibilidad hacia atrás
CalibrationValidator = ValidadorCalibracion

