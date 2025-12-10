"""
Extended extraction strategy for pixel features.

This module implements extraction using extended feature keys,
following Strategy Pattern and SOLID principles.
"""
from pathlib import Path
from typing import Dict, Optional
import torch

from .....utils.logs import get_ml_logger
from .base_strategy import ExtractionStrategy

logger = get_ml_logger("cacaoscan.ml.data.datasets.extractors.strategies")


class ExtendedExtractionStrategy(ExtractionStrategy):
    """
    Extraction strategy using extended feature keys (12 features).
    
    This strategy extracts features from extended pixel feature keys.
    """
    
    EXTENDED_KEYS = [
        "grain_area_pixels", "width_pixels", "height_pixels",
        "bbox_area_pixels", "aspect_ratio", "original_total_pixels",
        "background_pixels", "background_ratio", "alto_mm_per_pixel",
        "ancho_mm_per_pixel", "average_mm_per_pixel", "segmentation_confidence"
    ]
    
    REQUIRED_KEYS = [
        "grain_area_pixels", "width_pixels", "height_pixels",
        "bbox_area_pixels", "aspect_ratio", "original_total_pixels",
        "background_pixels", "background_ratio", "alto_mm_per_pixel",
        "ancho_mm_per_pixel"
    ]
    
    def extract(
        self,
        idx: int,
        image_paths: list[Path],
        pixel_features: Dict[str, any]
    ) -> Optional[torch.Tensor]:
        """Extract extended pixel features (12 features)."""
        if not all(k in pixel_features for k in self.REQUIRED_KEYS):
            return None
        
        pixel_feat_values = [
            float(pixel_features[key][idx])
            for key in self.REQUIRED_KEYS
        ]
        
        return torch.tensor(pixel_feat_values, dtype=torch.float32)

