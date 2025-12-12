"""
Basic extraction strategy for pixel features.

This module implements extraction using basic feature keys,
following Strategy Pattern and SOLID principles.
"""
from pathlib import Path
from typing import Dict, Optional
import torch

from .....utils.logs import get_ml_logger
from .base_strategy import ExtractionStrategy

logger = get_ml_logger("cacaoscan.ml.data.datasets.extractors.strategies")


class BasicExtractionStrategy(ExtractionStrategy):
    """
    Extraction strategy using basic feature keys (5 features).
    
    This strategy extracts features from basic pixel feature keys.
    """
    
    BASIC_KEYS = [
        "pixel_width", "pixel_height", "pixel_area",
        "scale_factor", "aspect_ratio"
    ]
    
    def extract(
        self,
        idx: int,
        image_paths: list[Path],
        pixel_features: Dict[str, any]
    ) -> Optional[torch.Tensor]:
        """Extract basic pixel features (5 features)."""
        if not all(k in pixel_features for k in self.BASIC_KEYS):
            return None
        
        pixel_feat_values = [
            float(pixel_features["pixel_width"][idx]),
            float(pixel_features["pixel_height"][idx]),
            float(pixel_features["pixel_area"][idx]),
            float(pixel_features["scale_factor"][idx]),
            float(pixel_features["aspect_ratio"][idx]),
        ]
        
        return torch.tensor(pixel_feat_values, dtype=torch.float32)

