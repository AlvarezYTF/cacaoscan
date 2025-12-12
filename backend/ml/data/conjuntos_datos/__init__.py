"""
Conjuntos de datos para regresión de cacao.

Este módulo proporciona datasets para entrenamiento,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .dataset_cacao import DatasetCacao
from .dataset_hibrido import DatasetHibrido
from .dataset_mejorado import DatasetMejorado

__all__ = ['DatasetCacao', 'DatasetHibrido', 'DatasetMejorado']

