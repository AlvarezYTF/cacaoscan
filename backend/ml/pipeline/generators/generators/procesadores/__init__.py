"""
Procesadores de imágenes para generación de recortes.

Este módulo maneja el procesamiento de imágenes,
siguiendo el principio de Single Responsibility (SOLID).
"""

from .procesador_imagen import ProcesadorImagen
from .redimensionador_imagen import RedimensionadorImagen

__all__ = [
    'ProcesadorImagen',
    'RedimensionadorImagen'
]

