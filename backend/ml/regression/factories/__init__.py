"""
Factory pattern for model creation.

This module provides a factory pattern implementation for creating
regression models, following SOLID principles:
- Open/Closed: Easy to add new model types without modifying existing code
- Single Responsibility: Each factory handles one model type
- Dependency Inversion: Depends on abstractions (nn.Module)
"""

from .model_factory import (
    FabricaModelo,
    obtener_fabrica,
    create_model
)
from .creadores import (
    CreadorModeloBase,
    CreadorModeloHibrido,
    CreadorModeloMultiHead,
    CreadorModeloOptimizado,
    CreadorModeloEstandar
)
from .interfaces import ICreadorModelo
from .selectores import SelectorCreador

# Compatibilidad hacia atrás
from .model_factory import (
    ModelFactory,
    get_factory
)
from .creadores import (
    ModelCreator,
    HybridModelCreator,
    MultiHeadModelCreator,
    OptimizedModelCreator,
    StandardModelCreator
)

# Aliases
ModelFactory = FabricaModelo
ModelCreator = CreadorModeloBase
HybridModelCreator = CreadorModeloHibrido
MultiHeadModelCreator = CreadorModeloMultiHead
OptimizedModelCreator = CreadorModeloOptimizado
StandardModelCreator = CreadorModeloEstandar
get_factory = obtener_fabrica

__all__ = [
    # Nombres en español
    'FabricaModelo',
    'CreadorModeloBase',
    'CreadorModeloHibrido',
    'CreadorModeloMultiHead',
    'CreadorModeloOptimizado',
    'CreadorModeloEstandar',
    'ICreadorModelo',
    'SelectorCreador',
    'obtener_fabrica',
    'create_model',
    # Compatibilidad hacia atrás
    'ModelFactory',
    'ModelCreator',
    'HybridModelCreator',
    'MultiHeadModelCreator',
    'OptimizedModelCreator',
    'StandardModelCreator',
    'get_factory'
]

