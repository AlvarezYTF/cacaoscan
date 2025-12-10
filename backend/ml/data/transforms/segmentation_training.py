"""
Utilidades de entrenamiento de segmentación.

Este módulo proporciona funciones de conveniencia para compatibilidad hacia atrás,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .datasets import CacaoDataset
from .trainers import train_background_ai
from .inference import remove_background_ai

__all__ = ['CacaoDataset', 'train_background_ai', 'remove_background_ai']
