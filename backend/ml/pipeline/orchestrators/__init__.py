"""
Utilidades de orquestación de entrenamiento.

Este módulo proporciona clases para orquestar el pipeline de entrenamiento,
siguiendo principios SOLID.
"""

from .orquestador_entrenamiento import OrquestadorEntrenamiento
from .training_orchestrator import TrainingOrchestrator  # Compatibilidad hacia atrás
from .interfaces import IOrquestadorEntrenamiento

# Compatibilidad hacia atrás
TrainingOrchestrator = OrquestadorEntrenamiento

__all__ = [
    # Nombres en español
    'OrquestadorEntrenamiento',
    'IOrquestadorEntrenamiento',
    # Compatibilidad hacia atrás
    'TrainingOrchestrator'
]

