"""
Base extraction strategy for pixel features.

This module defines the abstract base class for extraction strategies,
following Strategy Pattern and SOLID principles.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional
import torch

from .....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.extractors.strategies")


class ExtractionStrategy(ABC):
    """
    Abstract base class for pixel feature extraction strategies.
    
    This class defines the interface for different extraction methods,
    following Strategy Pattern and Single Responsibility Principle.
    """
    
    @abstractmethod
    def extract(
        self,
        idx: int,
        image_paths: list[Path],
        pixel_features: Dict[str, any]
    ) -> Optional[torch.Tensor]:
        """
        Extract pixel features using this strategy.
        
        Args:
            idx: Sample index
            image_paths: List of image paths
            pixel_features: Dictionary of pixel feature arrays
            
        Returns:
            Pixel feature tensor or None if this strategy cannot extract
        """
        pass
    
    @staticmethod
    def _normalize_length(pixel_feat_values: list) -> list:
        """Normalize pixel features to length 10."""
        if len(pixel_feat_values) == 10 or len(pixel_feat_values) == 5:
            return pixel_feat_values
        
        if len(pixel_feat_values) < 10:
            pixel_feat_values.extend([0.0] * (10 - len(pixel_feat_values)))
        else:
            pixel_feat_values = pixel_feat_values[:10]
        
        return pixel_feat_values

