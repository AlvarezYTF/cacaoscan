"""
Validadores para transformaciones de imágenes.

Este módulo proporciona clases para validar calidad de crops,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .crop_validator import CropValidator

__all__ = ['CropValidator']

