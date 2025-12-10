"""
Interfaces para orquestadores de entrenamiento.

Este módulo define las interfaces (Protocols) para orquestadores,
siguiendo el principio de Dependency Inversion (SOLID).
"""

from .orquestador_interface import IOrquestadorEntrenamiento

__all__ = ['IOrquestadorEntrenamiento']

