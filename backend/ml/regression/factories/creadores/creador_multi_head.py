"""
Creator for multi-head models.

This module provides the creator for multi-head models,
following Single Responsibility principle (SOLID).
"""
from typing import Optional
import torch.nn as nn

from ....utils.logs import get_ml_logger
from .creador_base import CreadorModeloBase

logger = get_ml_logger("cacaoscan.ml.regression.factories.creadores")


class CreadorModeloMultiHead(CreadorModeloBase):
    """Creator for multi-head models."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """Create a multi-head model."""
        from ....models import _create_multi_head_model
        
        logger.info("Creating multi-head model via CreadorModeloMultiHead")
        return _create_multi_head_model(
            model_type=model_type,
            pretrained=pretrained,
            dropout_rate=dropout_rate
        )

