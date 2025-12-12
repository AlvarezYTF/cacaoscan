"""
Inferencia para modelos de segmentación.

Este módulo proporciona funciones de inferencia,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .background_remover import BackgroundRemover, remove_background_ai

__all__ = ['BackgroundRemover', 'remove_background_ai']

