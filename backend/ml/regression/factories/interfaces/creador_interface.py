"""
Interface for model creators.

Defines the contract that all model creator implementations must follow,
following Dependency Inversion principle.
"""
from typing import Protocol, Optional
import torch.nn as nn


class ICreadorModelo(Protocol):
    """
    Interface for model creators.
    
    Defines the methods that any model creator implementation must provide.
    """
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """
        Create a model instance.
        
        Args:
            model_type: Type of model backbone
            num_outputs: Number of output values
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate
            pixel_feature_dim: Dimension of pixel features (for hybrid models)
            use_pixel_features: Whether to use pixel features
            
        Returns:
            Created model instance
        """
        ...

