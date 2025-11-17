"""
Loader for pixel calibration features from pixel_calibration.json.

Generates normalized features:
- height_mm_est = height_pixels * avg_mm_per_px
- width_mm_est = width_pixels * avg_mm_per_px
- area_mm2_est = grain_area_pixels * (avg_mm_per_px²)
- log_height = log1p(height_mm_est)
- log_width = log1p(width_mm_est)
- log_area = log1p(area_mm2_est)
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
from numpy import log1p

from ..utils.logs import get_ml_logger
from ..utils.paths import get_datasets_dir
from ..utils.io import load_json

logger = get_ml_logger("cacaoscan.ml.data.pixel_features")


class PixelFeaturesLoader:
    """
    Loader that maps ID → normalized pixel features from pixel_calibration.json.
    
    Features generated:
    1. height_mm_est: height_pixels * avg_mm_per_pixel
    2. width_mm_est: width_pixels * avg_mm_per_pixel
    3. area_mm2_est: grain_area_pixels * (avg_mm_per_pixel²)
    4. log_height: log1p(height_mm_est)
    5. log_width: log1p(width_mm_est)
    6. log_area: log1p(area_mm2_est)
    """
    
    FEATURE_NAMES = [
        "height_mm_est",
        "width_mm_est",
        "area_mm2_est",
        "perimeter_mm",
        "aspect_ratio",
        "bbox_ratio",
        "background_ratio",
        "avg_mm_per_pixel",
        "compactness",
        "roundness"
    ]
    
    def __init__(self, calibration_file: Optional[Path] = None):
        """
        Initialize the loader.
        
        Args:
            calibration_file: Path to pixel_calibration.json. If None, uses default path.
        """
        if calibration_file is None:
            calibration_file = get_datasets_dir() / "pixel_calibration.json"
        
        self.calibration_file = Path(calibration_file)
        self.features_by_id: Dict[int, np.ndarray] = {}
        self.features_by_filename: Dict[str, np.ndarray] = {}
        self._loaded = False
        
    def load(self) -> bool:
        """
        Load pixel calibration and generate features.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.calibration_file.exists():
            logger.warning(f"Pixel calibration file not found: {self.calibration_file}")
            return False
        
        try:
            calibration_data = load_json(self.calibration_file)
            calibration_records = calibration_data.get("calibration_records", [])
            
            if not calibration_records:
                logger.warning("No calibration records found in pixel_calibration.json")
                return False
            
            logger.info(f"Loading {len(calibration_records)} calibration records")
            
            for record in calibration_records:
                try:
                    record_id = int(record["id"])
                    filename = record.get("filename", "")
                    
                    # Extract pixel measurements
                    pixel_meas = record.get("pixel_measurements", {})
                    height_pixels = float(pixel_meas.get("height_pixels", 0.0))
                    width_pixels = float(pixel_meas.get("width_pixels", 0.0))
                    grain_area_pixels = float(pixel_meas.get("grain_area_pixels", 0.0))
                    bbox_area_pixels = float(pixel_meas.get("bbox_area_pixels", 0.0))
                    aspect_ratio = float(pixel_meas.get("aspect_ratio", 0.0))
                    
                    # Extract scale factors
                    scale_factors = record.get("scale_factors", {})
                    avg_mm_per_px = float(scale_factors.get("average_mm_per_pixel", 0.0))
                    
                    # Extract background info
                    bg_info = record.get("background_info", {})
                    background_ratio = float(bg_info.get("background_ratio", 0.0))
                    
                    # Validate data
                    if avg_mm_per_px <= 0:
                        logger.warning(f"Invalid avg_mm_per_pixel for ID {record_id}: {avg_mm_per_px}")
                        continue
                    
                    if height_pixels <= 0 or width_pixels <= 0 or grain_area_pixels <= 0:
                        logger.warning(f"Invalid pixel measurements for ID {record_id}")
                        continue
                    
                    # Calculate features
                    height_mm_est = height_pixels * avg_mm_per_px
                    width_mm_est = width_pixels * avg_mm_per_px
                    area_mm2_est = grain_area_pixels * (avg_mm_per_px ** 2)
                    perimeter_mm = 2 * (width_pixels + height_pixels) * avg_mm_per_px
                    bbox_ratio = grain_area_pixels / bbox_area_pixels if bbox_area_pixels > 0 else 0.0
                    
                    # New features: compactness and roundness
                    compactness = (perimeter_mm ** 2) / (4 * np.pi * area_mm2_est) if area_mm2_est > 0 else 0.0
                    roundness = (4 * np.pi * area_mm2_est) / (perimeter_mm ** 2) if perimeter_mm > 0 else 0.0
                    
                    # Create feature vector (10 features)
                    features = np.array([
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
                    
                    # Store by ID and filename
                    self.features_by_id[record_id] = features
                    if filename:
                        # Remove extension for matching
                        filename_base = Path(filename).stem
                        self.features_by_filename[filename_base] = features
                    
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Error processing calibration record {record.get('id', 'unknown')}: {e}")
                    continue
            
            self._loaded = True
            logger.info(f"Loaded pixel features for {len(self.features_by_id)} records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading pixel calibration: {e}")
            return False
    
    def get_features_by_id(self, record_id: int) -> Optional[np.ndarray]:
        """
        Get features for a record ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            Feature array (6 features) or None if not found
        """
        if not self._loaded:
            self.load()
        
        return self.features_by_id.get(record_id)
    
    def get_features_by_filename(self, filename: str) -> Optional[np.ndarray]:
        """
        Get features for a filename (without extension).
        
        Args:
            filename: Filename (e.g., "510" or "510.bmp")
            
        Returns:
            Feature array (6 features) or None if not found
        """
        if not self._loaded:
            self.load()
        
        # Remove extension if present
        filename_base = Path(filename).stem
        return self.features_by_filename.get(filename_base)
    
    def get_all_features(self) -> Tuple[Dict[int, np.ndarray], Dict[str, np.ndarray]]:
        """
        Get all loaded features.
        
        Returns:
            Tuple of (features_by_id, features_by_filename)
        """
        if not self._loaded:
            self.load()
        
        return self.features_by_id, self.features_by_filename
    
    def validate_record(self, record_id: int, filename: Optional[str] = None) -> bool:
        """
        Validate that a record exists in the calibration data.
        
        Args:
            record_id: Record ID to validate
            filename: Optional filename to validate
            
        Returns:
            True if record exists, False otherwise
        """
        if not self._loaded:
            self.load()
        
        has_id = record_id in self.features_by_id
        
        if filename:
            filename_base = Path(filename).stem
            has_filename = filename_base in self.features_by_filename
            return has_id and has_filename
        
        return has_id
    
    def get_missing_records(self, record_ids: list[int]) -> list[int]:
        """
        Get list of record IDs that are missing from calibration data.
        
        Args:
            record_ids: List of record IDs to check
            
        Returns:
            List of missing record IDs
        """
        if not self._loaded:
            self.load()
        
        missing = [rid for rid in record_ids if rid not in self.features_by_id]
        return missing

