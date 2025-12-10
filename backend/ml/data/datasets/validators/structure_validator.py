"""
Structure validator for datasets.

This module validates dataset structure consistency,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict, List
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.validators")


class StructureValidator:
    """
    Validator for dataset structure consistency.
    
    This class is responsible for:
    - Validating data lengths
    - Validating target presence
    - Validating pixel features consistency
    
    Following Single Responsibility Principle.
    """
    
    TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]
    
    def validate(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        pixel_features: Dict[str, np.ndarray] | None = None
    ) -> None:
        """
        Validate dataset structure.
        
        Args:
            image_paths: List of image paths
            targets: Dictionary of target arrays
            pixel_features: Optional dictionary of pixel feature arrays
            
        Raises:
            ValueError: If structure is invalid
        """
        self._validate_lengths(image_paths, targets, pixel_features)
        self._validate_targets(targets)
        if pixel_features is not None:
            self._validate_pixel_features(image_paths, pixel_features)
        
        logger.info("Dataset structure validated successfully")
    
    def _validate_lengths(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        pixel_features: Dict[str, np.ndarray] | None
    ) -> None:
        """Validate that all arrays have consistent lengths."""
        n_images = len(image_paths)
        n_targets = {k: len(v) for k, v in targets.items()}
        
        if not all(n == n_images for n in n_targets.values()):
            raise ValueError(
                f"Inconsistent lengths: images={n_images}, targets={n_targets}"
            )
        
        if pixel_features is not None:
            n_pixel = {k: len(v) for k, v in pixel_features.items()}
            if not all(n == n_images for n in n_pixel.values()):
                raise ValueError(
                    f"Inconsistent lengths in pixel_features: {n_pixel}"
                )
    
    def _validate_targets(self, targets: Dict[str, np.ndarray]) -> None:
        """Validate that all required targets are present."""
        missing_targets = set(self.TARGET_ORDER) - set(targets.keys())
        if missing_targets:
            raise ValueError(f"Missing targets: {missing_targets}")
        
        # Reorder targets if needed
        target_keys = list(targets.keys())
        if target_keys != self.TARGET_ORDER:
            logger.warning(
                f"Target order is not as expected. Expected: {self.TARGET_ORDER}, "
                f"Got: {target_keys}. Reordering..."
            )
    
    def _validate_pixel_features(
        self,
        image_paths: List[Path],
        pixel_features: Dict[str, np.ndarray]
    ) -> None:
        """Validate pixel features consistency."""
        n_images = len(image_paths)
        n_pixel = {k: len(v) for k, v in pixel_features.items()}
        
        if not all(n == n_images for n in n_pixel.values()):
            raise ValueError(
                f"Inconsistent lengths in pixel_features: {n_pixel}"
            )

