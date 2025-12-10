"""
Factory pattern for creating regression models.

This module implements the Factory Method pattern to create different types
of regression models, improving code organization and extensibility.
"""
from typing import Optional
import torch.nn as nn

from .inicializadores import InicializadorCreadores


class FabricaModelo:
    """
    Factory for creating regression models.
    
    This factory uses the Strategy pattern to delegate model creation
    to specific creators based on the model configuration.
    """
    
    def __init__(self):
        """Initialize the factory with model creators."""
        inicializador = InicializadorCreadores()
        self._selector = inicializador.crear_selector()
    
    def create_model(
        self,
        model_type: str = "resnet18",
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        multi_head: bool = False,
        hybrid: bool = False,
        use_pixel_features: bool = True,
        pixel_feature_dim: Optional[int] = None,
        use_optimized: bool = True
    ) -> nn.Module:
        """
        Create a regression model based on configuration.
        
        Args:
            model_type: Type of model backbone ("resnet18", "convnext_tiny", etc.)
            num_outputs: Number of output values (ignored if multi_head=True or hybrid=True)
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate
            multi_head: Whether to create a multi-head model
            hybrid: Whether to create a hybrid model
            use_pixel_features: Whether to use pixel features (only if hybrid=True)
            pixel_feature_dim: Dimension of pixel features
            use_optimized: Whether to try optimized models first
            
        Returns:
            Created model instance
        """
        return self._selector.crear_modelo(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features,
            hybrid=hybrid,
            multi_head=multi_head,
            use_optimized=use_optimized
        )


# Singleton instance
_factory_instance: Optional[FabricaModelo] = None


def obtener_fabrica() -> FabricaModelo:
    """Get the singleton factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = FabricaModelo()
    return _factory_instance

# Re-export creators for backward compatibility
from .creadores import (
    CreadorModeloBase,
    CreadorModeloHibrido,
    CreadorModeloMultiHead,
    CreadorModeloOptimizado,
    CreadorModeloEstandar,
    ModelCreator,
    HybridModelCreator,
    MultiHeadModelCreator,
    OptimizedModelCreator,
    StandardModelCreator
)

# Compatibilidad hacia atrás
ModelFactory = FabricaModelo
get_factory = obtener_fabrica


def create_model(
    model_type: str = "resnet18",
    num_outputs: int = 1,
    pretrained: bool = True,
    dropout_rate: float = 0.3,
    multi_head: bool = False,
    hybrid: bool = False,
    use_pixel_features: bool = True,
    pixel_feature_dim: Optional[int] = None,
    use_optimized: bool = True
) -> nn.Module:
    """
    Convenience function to create a model using the factory.
    
    This function maintains backward compatibility with the original
    create_model function signature.
    
    Args:
        model_type: Type of model backbone
        num_outputs: Number of output values
        pretrained: Whether to use pretrained weights
        dropout_rate: Dropout rate
        multi_head: Whether to create a multi-head model
        hybrid: Whether to create a hybrid model
        use_pixel_features: Whether to use pixel features
        pixel_feature_dim: Dimension of pixel features
        use_optimized: Whether to try optimized models first
        
    Returns:
        Created model instance
    """
    factory = obtener_fabrica()
    return factory.create_model(
        model_type=model_type,
        num_outputs=num_outputs,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
        multi_head=multi_head,
        hybrid=hybrid,
        use_pixel_features=use_pixel_features,
        pixel_feature_dim=pixel_feature_dim,
        use_optimized=use_optimized
    )

