"""
Path-based extraction strategy for pixel features.

This module implements extraction using image paths as keys,
following Strategy Pattern and SOLID principles.
"""
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import torch

from .....utils.logs import get_ml_logger
from .base_strategy import ExtractionStrategy

logger = get_ml_logger("cacaoscan.ml.data.datasets.extractors.strategies")


class PathExtractionStrategy(ExtractionStrategy):
    """
    Extraction strategy using image paths as keys.
    
    This strategy is used when pixel_features dictionary uses
    image paths as keys (test format).
    """
    
    def extract(
        self,
        idx: int,
        image_paths: list[Path],
        pixel_features: Dict[str, any]
    ) -> Optional[torch.Tensor]:
        """Extract pixel features when using path as key."""
        image_path_str = str(image_paths[idx])
        if image_path_str not in pixel_features:
            return None
        
        pixel_feat_array = pixel_features[image_path_str]
        
        if isinstance(pixel_feat_array, np.ndarray):
            pixel_feat_values = pixel_feat_array.tolist()
        elif isinstance(pixel_feat_array, (list, tuple)):
            pixel_feat_values = list(pixel_feat_array)
        else:
            pixel_feat_values = [float(pixel_feat_array)]
        
        pixel_feat_values = self._normalize_length(pixel_feat_values)
        return torch.tensor(pixel_feat_values, dtype=torch.float32)

