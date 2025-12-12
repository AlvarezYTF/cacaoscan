"""
Creator for standard models.

This module provides the creator for standard models,
following Single Responsibility principle (SOLID).
"""
from typing import Optional
import torch.nn as nn

from ....utils.logs import get_ml_logger
from .creador_base import CreadorModeloBase

logger = get_ml_logger("cacaoscan.ml.regression.factories.creadores")


class CreadorModeloEstandar(CreadorModeloBase):
    """Creator for standard models (ResNet18, ConvNeXt, etc.)."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """Create a standard model."""
        from ...models import _create_standard_model
        
        logger.info("Creating standard model via CreadorModeloEstandar")
        return _create_standard_model(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features
        )

