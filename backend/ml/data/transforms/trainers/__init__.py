"""
Entrenadores para modelos de segmentación.

Este módulo proporciona funciones de entrenamiento,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .background_trainer import BackgroundTrainer, train_background_ai

__all__ = ['BackgroundTrainer', 'train_background_ai']

