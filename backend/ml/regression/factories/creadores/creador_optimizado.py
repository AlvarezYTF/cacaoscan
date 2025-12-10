"""
Creator for optimized models.

This module provides the creator for optimized models,
following Single Responsibility principle (SOLID).
"""
from typing import Optional
import torch.nn as nn

from ....utils.logs import get_ml_logger
from .creador_base import CreadorModeloBase

logger = get_ml_logger("cacaoscan.ml.regression.factories.creadores")


class CreadorModeloOptimizado(CreadorModeloBase):
    """Creator for optimized models."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> Optional[nn.Module]:
        """Create an optimized model if available."""
        from ....models import _create_optimized_model
        
        logger.info("Creating optimized model via CreadorModeloOptimizado")
        return _create_optimized_model(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate
        )

