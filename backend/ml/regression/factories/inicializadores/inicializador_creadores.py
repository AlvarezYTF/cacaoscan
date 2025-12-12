"""
Initializer for model creators.

This module handles the initialization of model creators,
following Single Responsibility principle (SOLID).
"""
from ..creadores import (
    CreadorModeloHibrido,
    CreadorModeloMultiHead,
    CreadorModeloOptimizado,
    CreadorModeloEstandar
)
from ..interfaces import ICreadorModelo
from ..selectores import SelectorCreador


class InicializadorCreadores:
    """
    Initializer for model creators.
    
    Single Responsibility: Only handles initialization of creators and selector.
    """
    
    def __init__(self):
        """Initialize creators."""
        self.hybrid_creator = CreadorModeloHibrido()
        self.multi_head_creator = CreadorModeloMultiHead()
        self.optimized_creator = CreadorModeloOptimizado()
        self.standard_creator = CreadorModeloEstandar()
    
    def crear_selector(self) -> SelectorCreador:
        """
        Create and configure the selector with all creators.
        
        Returns:
            Configured selector instance
        """
        return SelectorCreador(
            hybrid_creator=self.hybrid_creator,
            multi_head_creator=self.multi_head_creator,
            optimized_creator=self.optimized_creator,
            standard_creator=self.standard_creator
        )
    
    def obtener_creadores(self) -> tuple[
        ICreadorModelo,
        ICreadorModelo,
        ICreadorModelo,
        ICreadorModelo
    ]:
        """
        Get all creators as a tuple.
        
        Returns:
            Tuple of (hybrid, multi_head, optimized, standard) creators
        """
        return (
            self.hybrid_creator,
            self.multi_head_creator,
            self.optimized_creator,
            self.standard_creator
        )

