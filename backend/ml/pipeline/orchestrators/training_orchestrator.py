"""
Compatibilidad hacia atrás para TrainingOrchestrator.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en orquestador_entrenamiento.py.
"""

from .orquestador_entrenamiento import OrquestadorEntrenamiento

# Alias para compatibilidad hacia atrás
TrainingOrchestrator = OrquestadorEntrenamiento
