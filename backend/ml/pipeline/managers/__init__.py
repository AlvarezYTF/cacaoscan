"""
Utilidades de gestión de artefactos de entrenamiento.

Este módulo proporciona clases para gestionar artefactos de entrenamiento
(modelos, scalers, checkpoints), siguiendo principios SOLID.
"""

from .gestor_artefactos import GestorArtefactos
from .artifact_manager import ArtifactManager  # Compatibilidad hacia atrás
from .interfaces import IGestorArtefactos

# Compatibilidad hacia atrás
ArtifactManager = GestorArtefactos

__all__ = [
    # Nombres en español
    'GestorArtefactos',
    'IGestorArtefactos',
    # Compatibilidad hacia atrás
    'ArtifactManager'
]

