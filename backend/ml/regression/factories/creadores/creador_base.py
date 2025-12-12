"""
Base abstract creator for models.

This module defines the abstract base class for model creators,
following Open/Closed principle (SOLID).
"""
from abc import ABC, abstractmethod
from typing import Optional
import torch.nn as nn

from ..interfaces import ICreadorModelo


class CreadorModeloBase(ABC, ICreadorModelo):
    """
    Abstract base class for model creators.
    
    Each concrete creator handles the creation of a specific model type.
    This follows the Factory Method pattern and Open/Closed Principle.
    """
    
    @abstractmethod
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
        pass

