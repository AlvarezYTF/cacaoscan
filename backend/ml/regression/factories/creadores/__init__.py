"""
Model creators.

This module provides concrete implementations of model creators,
following Single Responsibility principle (SOLID).
"""

from .creador_base import CreadorModeloBase
from .creador_hibrido import CreadorModeloHibrido
from .creador_multi_head import CreadorModeloMultiHead
from .creador_optimizado import CreadorModeloOptimizado
from .creador_estandar import CreadorModeloEstandar

# Compatibilidad hacia atrás
ModelCreator = CreadorModeloBase
HybridModelCreator = CreadorModeloHibrido
MultiHeadModelCreator = CreadorModeloMultiHead
OptimizedModelCreator = CreadorModeloOptimizado
StandardModelCreator = CreadorModeloEstandar

__all__ = [
    'CreadorModeloBase',
    'CreadorModeloHibrido',
    'CreadorModeloMultiHead',
    'CreadorModeloOptimizado',
    'CreadorModeloEstandar',
    # Compatibilidad hacia atrás
    'ModelCreator',
    'HybridModelCreator',
    'MultiHeadModelCreator',
    'OptimizedModelCreator',
    'StandardModelCreator'
]

