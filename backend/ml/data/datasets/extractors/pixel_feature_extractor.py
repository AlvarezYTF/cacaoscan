"""
Pixel feature extractor for datasets.

This module extracts pixel features from pixel_features dictionary,
following Strategy Pattern and Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict, Optional
import torch

from ....utils.logs import get_ml_logger
from .strategies import (
    PathExtractionStrategy,
    ExtendedExtractionStrategy,
    BasicExtractionStrategy,
    FallbackExtractionStrategy
)

logger = get_ml_logger("cacaoscan.ml.data.datasets.extractors")


class PixelFeatureExtractor:
    """
    Extractor for pixel features from pixel_features dictionary.
    
    This class uses Strategy Pattern to try different extraction methods,
    following Single Responsibility Principle and Open/Closed Principle.
    """
    
    def __init__(self):
        """Initialize extractor with extraction strategies."""
        self.strategies = [
            PathExtractionStrategy(),
            ExtendedExtractionStrategy(),
            BasicExtractionStrategy(),
            FallbackExtractionStrategy()
        ]
        logger.debug(f"PixelFeatureExtractor initialized with {len(self.strategies)} strategies")
    
    def extract(
        self,
        idx: int,
        image_paths: list[Path],
        pixel_features: Dict[str, any] | None
    ) -> Optional[torch.Tensor]:
        """
        Extract pixel features using appropriate strategy.
        
        Args:
            idx: Sample index
            image_paths: List of image paths
            pixel_features: Dictionary of pixel feature arrays
            
        Returns:
            Pixel feature tensor or None
        """
        if pixel_features is None:
            return None
        
        for strategy in self.strategies:
            try:
                result = strategy.extract(idx, image_paths, pixel_features)
                if result is not None:
                    logger.debug(f"Extraction successful using {strategy.__class__.__name__}")
                    return result
            except Exception as e:
                logger.warning(
                    f"Strategy {strategy.__class__.__name__} failed: {e}, trying next strategy"
                )
                continue
        
        logger.error("All extraction strategies failed")
        return None

