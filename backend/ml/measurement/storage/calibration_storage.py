"""
Compatibilidad hacia atrás para CalibrationStorage.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en almacenamiento_calibracion.py.
"""

from .almacenamiento_calibracion import AlmacenamientoCalibracion

# Alias para compatibilidad hacia atrás
CalibrationStorage = AlmacenamientoCalibracion

