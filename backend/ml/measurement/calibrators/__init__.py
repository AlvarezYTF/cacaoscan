"""
Calibradores para diferentes métodos de calibración de granos de cacao.

Este módulo proporciona calibradores para establecer la escala píxeles/mm
usando métodos específicos para granos de cacao, siguiendo principios SOLID.
"""

from .calibrador_manual import CalibradorManual

# Re-export para compatibilidad hacia atrás
ManualCalibrator = CalibradorManual

__all__ = [
    'CalibradorManual',
    # Compatibilidad hacia atrás
    'ManualCalibrator'
]
