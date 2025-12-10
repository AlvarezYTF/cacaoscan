"""
Pixel feature builder for calibration records.

This module handles building feature vectors from calibration data,
following Single Responsibility Principle.
"""
from typing import Dict, Optional, Any
import numpy as np

from ...utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.processors.feature_builder")


class PixelFeatureBuilder:
    """
    Builder for pixel features from calibration records.
    
    This class is responsible for:
    - Extracting values from calibration records
    - Validating measurement values
    - Building feature vectors
    
    Following Single Responsibility Principle.
    """
    
    @staticmethod
    def _get_float(source: Dict[str, Any], key: str, default: float = 0.0) -> float:
        """Read a float value from nested dictionaries."""
        try:
            return float(source.get(key, default))
        except (TypeError, ValueError):
            return default
    
    def _validate_measurements(
        self,
        record_id: Optional[int],
        avg_mm_per_px: float,
        height_pixels: float,
        width_pixels: float,
        grain_area_pixels: float
    ) -> bool:
        """Validate measurement values before feature computation."""
        if avg_mm_per_px <= 0:
            if record_id:
                logger.warning(f"Invalid avg_mm_per_pixel for ID {record_id}: {avg_mm_per_px}")
            return False
        if height_pixels <= 0 or width_pixels <= 0 or grain_area_pixels <= 0:
            if record_id:
                logger.warning(f"Invalid pixel measurements for ID {record_id}")
            return False
        return True
    
    def build_features(
        self,
        pixel_measurements: Dict[str, Any],
        scale_factors: Dict[str, Any],
        background_info: Dict[str, Any],
        record_id: Optional[int] = None
    ) -> Optional[np.ndarray]:
        """
        Build feature vector from calibration data.
        
        Args:
            pixel_measurements: Pixel measurements dictionary
            scale_factors: Scale factors dictionary
            background_info: Background info dictionary
            record_id: Optional record ID for logging
            
        Returns:
            Feature array or None if invalid
        """
        # Extract values
        height_pixels = self._get_float(pixel_measurements, "height_pixels")
        width_pixels = self._get_float(pixel_measurements, "width_pixels")
        grain_area_pixels = self._get_float(pixel_measurements, "grain_area_pixels")
        bbox_area_pixels = self._get_float(pixel_measurements, "bbox_area_pixels")
        aspect_ratio = self._get_float(pixel_measurements, "aspect_ratio")
        avg_mm_per_px = self._get_float(scale_factors, "average_mm_per_pixel")
        background_ratio = self._get_float(background_info, "background_ratio")
        
        # Validate measurements
        if not self._validate_measurements(
            record_id, avg_mm_per_px, height_pixels, width_pixels, grain_area_pixels
        ):
            return None
        
        # Calculate features
        height_mm_est = height_pixels * avg_mm_per_px
        width_mm_est = width_pixels * avg_mm_per_px
        area_mm2_est = grain_area_pixels * (avg_mm_per_px ** 2)
        perimeter_mm = 2 * (width_pixels + height_pixels) * avg_mm_per_px
        bbox_ratio = grain_area_pixels / bbox_area_pixels if bbox_area_pixels > 0 else 0.0
        compactness = (perimeter_mm ** 2) / (4 * np.pi * area_mm2_est) if area_mm2_est > 0 else 0.0
        roundness = (4 * np.pi * area_mm2_est) / (perimeter_mm ** 2) if perimeter_mm > 0 else 0.0
        
        return np.array([
            height_mm_est,
            width_mm_est,
            area_mm2_est,
            perimeter_mm,
            aspect_ratio,
            bbox_ratio,
            background_ratio,
            avg_mm_per_px,
            compactness,
            roundness
        ], dtype=np.float32)
