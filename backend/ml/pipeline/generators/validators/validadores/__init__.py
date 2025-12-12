"""
Validadores específicos para recortes.

Este módulo maneja validaciones específicas de recortes,
siguiendo el principio de Single Responsibility (SOLID).
"""

from .validador_dimensiones import ValidadorDimensiones
from .validador_canal_alpha import ValidadorCanalAlpha

__all__ = [
    'ValidadorDimensiones',
    'ValidadorCanalAlpha'
]


