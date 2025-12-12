"""
Compatibilidad hacia atrás para CalibrationVisualizer.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en visualizador_calibracion.py.
"""

from .visualizador_calibracion import VisualizadorCalibracion

# Alias para compatibilidad hacia atrás
CalibrationVisualizer = VisualizadorCalibracion

