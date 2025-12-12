"""
Generadores de recortes para diferentes métodos.

Este módulo proporciona generadores de recortes siguiendo
principios SOLID con separación de responsabilidades.
"""

from .generador_recorte_segmentado import GeneradorRecorteSegmentado, SegmentedCropGenerator
from .generador_recorte_simple import GeneradorRecorteSimple, SimpleCropGenerator
from .base_generador import GeneradorRecorteBase
from .interfaces import IGeneradorRecorte

__all__ = [
    # Nombres en español
    'GeneradorRecorteSegmentado',
    'GeneradorRecorteSimple',
    'GeneradorRecorteBase',
    'IGeneradorRecorte',
    # Compatibilidad hacia atrás
    'SegmentedCropGenerator',
    'SimpleCropGenerator'
]

