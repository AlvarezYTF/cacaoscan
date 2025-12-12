"""
Selector for choosing the appropriate model creator.

This module handles the selection logic for model creators,
following Single Responsibility principle (SOLID).
"""
from typing import Optional
import torch.nn as nn

from ....utils.logs import get_ml_logger
from ..interfaces import ICreadorModelo

logger = get_ml_logger("cacaoscan.ml.regression.factories.selectores")


class SelectorCreador:
    """
    Selector for choosing the appropriate model creator.
    
    Single Responsibility: Only handles selection logic.
    """
    
    def __init__(
        self,
        hybrid_creator: ICreadorModelo,
        multi_head_creator: ICreadorModelo,
        optimized_creator: ICreadorModelo,
        standard_creator: ICreadorModelo
    ):
        """
        Initialize the selector with creators.
        
        Args:
            hybrid_creator: Creator for hybrid models
            multi_head_creator: Creator for multi-head models
            optimized_creator: Creator for optimized models
            standard_creator: Creator for standard models
        """
        self.hybrid_creator = hybrid_creator
        self.multi_head_creator = multi_head_creator
        self.optimized_creator = optimized_creator
        self.standard_creator = standard_creator
    
    def seleccionar_creador(
        self,
        hybrid: bool,
        multi_head: bool,
        use_optimized: bool
    ) -> Optional[ICreadorModelo]:
        """
        Select the appropriate creator based on configuration.
        
        Args:
            hybrid: Whether to create a hybrid model
            multi_head: Whether to create a multi-head model
            use_optimized: Whether to try optimized models first
            
        Returns:
            Selected creator or None
        """
        # Priority 1: Hybrid models
        if hybrid:
            return self.hybrid_creator
        
        # Priority 2: Multi-head models
        if multi_head:
            return self.multi_head_creator
        
        # Priority 3: Optimized models (if enabled)
        if use_optimized:
            return self.optimized_creator
        
        # Priority 4: Standard models
        return self.standard_creator
    
    def crear_modelo(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool,
        hybrid: bool,
        multi_head: bool,
        use_optimized: bool
    ) -> nn.Module:
        """
        Create a model using the selected creator.
        
        Args:
            model_type: Type of model backbone
            num_outputs: Number of output values
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate
            pixel_feature_dim: Dimension of pixel features
            use_pixel_features: Whether to use pixel features
            hybrid: Whether to create a hybrid model
            multi_head: Whether to create a multi-head model
            use_optimized: Whether to try optimized models first
            
        Returns:
            Created model instance
        """
        creator = self.seleccionar_creador(hybrid, multi_head, use_optimized)
        
        if creator is None:
            raise ValueError("No creator selected")
        
        # For optimized models, check if creation was successful
        if use_optimized and creator == self.optimized_creator:
            model = creator.create(
                model_type=model_type,
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate,
                pixel_feature_dim=pixel_feature_dim,
                use_pixel_features=use_pixel_features
            )
            if model is not None:
                return model
            # Fallback to standard if optimized fails
            creator = self.standard_creator
            logger.info(f"Creating individual model (Backbone: {model_type}, Outputs: {num_outputs})")
        
        return creator.create(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features
        )

