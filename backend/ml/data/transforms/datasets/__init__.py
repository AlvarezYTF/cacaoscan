"""
Datasets para entrenamiento de segmentación.

Este módulo proporciona datasets para entrenamiento,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .cacao_dataset import CacaoDataset

__all__ = ['CacaoDataset']

