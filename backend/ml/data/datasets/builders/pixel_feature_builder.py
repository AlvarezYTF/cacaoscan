"""
Pixel feature builder for calibration data.

This module builds pixel feature vectors from calibration records,
following Single Responsibility Principle.
"""
from typing import Dict
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.builders")


class PixelFeatureBuilder:
    """
    Builder for pixel feature vectors from calibration data.
    
    This class is responsible for:
    - Extracting pixel measurements
    - Calculating derived features (area, perimeter, compactness, roundness)
    - Building feature vectors
    
    Following Single Responsibility Principle.
    """
    
    def build(self, calibration_entry: Dict) -> np.ndarray:
        """
        Build pixel feature vector from calibration entry.
        
        Args:
            calibration_entry: Calibration record dictionary
            
        Returns:
            Feature vector array (10 features)
        """
        pixel_meas = calibration_entry.get("pixel_measurements", {})
        scale_factors = calibration_entry.get("scale_factors", {})
        bg_info = calibration_entry.get("background_info", {})
        
        # Extract raw values
        avg_mm_per_pixel = float(scale_factors.get("average_mm_per_pixel", 0.0))
        width_pixels = float(pixel_meas.get("width_pixels", 0.0))
        height_pixels = float(pixel_meas.get("height_pixels", 0.0))
        grain_area_pixels = float(pixel_meas.get("grain_area_pixels", 0.0))
        bbox_area_pixels = float(pixel_meas.get("bbox_area_pixels", 0.0))
        aspect_ratio = float(pixel_meas.get("aspect_ratio", 0.0))
        background_ratio = float(bg_info.get("background_ratio", 0.0))
        
        # Calculate derived features
        area_mm2 = grain_area_pixels * (avg_mm_per_pixel ** 2)
        width_mm = width_pixels * avg_mm_per_pixel
        height_mm = height_pixels * avg_mm_per_pixel
        perimeter_mm = 2 * (width_pixels + height_pixels) * avg_mm_per_pixel
        bbox_ratio = (
            grain_area_pixels / bbox_area_pixels
            if bbox_area_pixels > 0 else 0.0
        )
        compactness = (
            (perimeter_mm ** 2) / (4 * np.pi * area_mm2)
            if area_mm2 > 0 else 0.0
        )
        roundness = (
            (4 * np.pi * area_mm2) / (perimeter_mm ** 2)
            if perimeter_mm > 0 else 0.0
        )
        
        return np.array([
            area_mm2,
            width_mm,
            height_mm,
            perimeter_mm,
            aspect_ratio,
            bbox_ratio,
            background_ratio,
            avg_mm_per_pixel,
            compactness,
            roundness
        ], dtype=np.float32)

