"""
Serializadores para parámetros de calibración.

Este módulo maneja la conversión entre objetos CalibrationParams
y representaciones serializables (dict, JSON), siguiendo SRP.
"""

from .serializador_calibracion import SerializadorCalibracion

__all__ = ['SerializadorCalibracion']

