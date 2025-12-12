"""
Creator for hybrid models.

This module provides the creator for hybrid models,
following Single Responsibility principle (SOLID).
"""
from typing import Optional
import torch.nn as nn

from ....utils.logs import get_ml_logger
from .creador_base import CreadorModeloBase

logger = get_ml_logger("cacaoscan.ml.regression.factories.creadores")


class CreadorModeloHibrido(CreadorModeloBase):
    """Creator for hybrid models (ResNet18 + ConvNeXt + Pixel features)."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """Create a hybrid model."""
        from ...models import _create_hybrid_model
        
        logger.info("Creating hybrid model via CreadorModeloHibrido")
        return _create_hybrid_model(
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features
        )

