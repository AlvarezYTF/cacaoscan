"""
Compatibilidad hacia atrás para ArtifactManager.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en gestor_artefactos.py.
"""

from .gestor_artefactos import GestorArtefactos

# Alias para compatibilidad hacia atrás
ArtifactManager = GestorArtefactos
