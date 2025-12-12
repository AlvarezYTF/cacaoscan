"""
Fallback extraction strategy for pixel features.

This module implements extraction with fallback defaults,
following Strategy Pattern and SOLID principles.
"""
from pathlib import Path
from typing import Dict
import torch

from .....utils.logs import get_ml_logger
from .base_strategy import ExtractionStrategy

logger = get_ml_logger("cacaoscan.ml.data.datasets.extractors.strategies")


class FallbackExtractionStrategy(ExtractionStrategy):
    """
    Fallback extraction strategy with default values.
    
    This strategy is used when other strategies fail,
    providing default values for missing features.
    """
    
    def extract(
        self,
        idx: int,
        image_paths: list[Path],
        pixel_features: Dict[str, any]
    ) -> torch.Tensor:
        """Extract pixel features with fallback defaults."""
        pixel_feat_values = [
            float(pixel_features.get("pixel_width", [0.0] * len(image_paths))[idx]),
            float(pixel_features.get("pixel_height", [0.0] * len(image_paths))[idx]),
            float(pixel_features.get("pixel_area", [0.0] * len(image_paths))[idx]),
            float(pixel_features.get("scale_factor", [0.0] * len(image_paths))[idx]),
            float(pixel_features.get("aspect_ratio", [0.0] * len(image_paths))[idx]),
        ]
        
        return torch.tensor(pixel_feat_values, dtype=torch.float32)

