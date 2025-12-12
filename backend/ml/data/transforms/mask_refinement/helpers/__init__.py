"""
Helpers para refinamiento de máscaras.

Este módulo proporciona funciones helper para operaciones de máscaras,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .mask_aligner import MaskAligner
from .bbox_computer import BBoxComputer
from .mask_renderer import MaskRenderer
from .rgba_builder import RGBABuilder

__all__ = [
    'MaskAligner',
    'BBoxComputer',
    'MaskRenderer',
    'RGBABuilder'
]

