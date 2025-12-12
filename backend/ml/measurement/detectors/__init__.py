"""
Detectores para calibración de granos de cacao.

Este módulo proporciona la estructura base para detectores de granos de cacao,
siguiendo principios SOLID para separación de responsabilidades.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: base, interfaces, validators
- Enfocado exclusivamente en granos de cacao

NOTA: Actualmente el sistema usa pixel_calibration.json para calibración
basada en datos históricos. Esta estructura está preparada para futuras
funcionalidades de detección de granos de cacao.
"""

from .base_detector import BaseDetector
from .interfaces import IDetector
from .validators import DetectionValidator

__all__ = [
    'BaseDetector',
    'IDetector',
    'DetectionValidator'
]

