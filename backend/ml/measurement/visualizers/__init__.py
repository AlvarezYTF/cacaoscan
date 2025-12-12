"""
Utilidades de visualización de calibración para granos de cacao.

Este módulo proporciona visualización de calibración siguiendo
principios SOLID con separación de responsabilidades.
"""

from .visualizador_calibracion import VisualizadorCalibracion

# Compatibilidad hacia atrás
CalibrationVisualizer = VisualizadorCalibracion

__all__ = [
    'VisualizadorCalibracion',
    'CalibrationVisualizer'  # Alias para compatibilidad
]

