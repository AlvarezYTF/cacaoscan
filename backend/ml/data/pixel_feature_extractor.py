"""
Pixel feature extractor with area_mm2 and perimeter_mm.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.preprocessing import RobustScaler

from ..utils.logs import get_ml_logger
from ..utils.paths import get_datasets_dir

logger = get_ml_logger("cacaoscan.ml.data.pixel_feature_extractor")


class PixelFeatureExtractor:
    """
    Extracts and normalizes pixel features including area_mm2 and perimeter_mm.
    
    Features extracted:
    1. area_mm2 = grain_area_pixels * (average_mm_per_pixel ** 2)
    2. width_mm = width_pixels * average_mm_per_pixel
    3. height_mm = height_pixels * average_mm_per_pixel
    4. perimeter_mm = (width_pixels + height_pixels) * average_mm_per_pixel * 2
    5. aspect_ratio
    6. bbox_to_area_ratio = grain_area_pixels / bbox_area_pixels
    7. background_ratio
    8. average_mm_per_pixel
    """
    
    FEATURE_NAMES = [
        "area_mm2",
        "width_mm",
        "height_mm",
        "perimeter_mm",
        "aspect_ratio",
        "bbox_to_area_ratio",
        "background_ratio",
        "average_mm_per_pixel"
    ]
    
    def __init__(
        self,
        calibration_file: Optional[Path] = None,
        quantile_range: tuple[float, float] = (0.1, 0.9)
    ):
        """
        Initialize the extractor.
        
        Args:
            calibration_file: Path to pixel_calibration.json
            quantile_range: Quantile range for RobustScaler (default: 10-90 percentile)
        """
        if calibration_file is None:
            calibration_file = get_datasets_dir() / "pixel_calibration.json"
        
        self.calibration_file = Path(calibration_file)
        self.quantile_range = quantile_range
        self.scaler = RobustScaler(quantile_range=quantile_range)
        self.features_by_id: Dict[int, np.ndarray] = {}
        self._loaded = False
        self._fitted = False
    
    def load(self) -> bool:
        """
        Load calibration data and extract features.
        
        Returns:
            True if loaded successfully
        """
        if not self.calibration_file.exists():
            logger.warning(f"Pixel calibration file not found: {self.calibration_file}")
            return False
        
        try:
            with open(self.calibration_file, 'r') as f:
                calibration_data = json.load(f)
            
            calibration_records = calibration_data.get("calibration_records", [])
            
            if not calibration_records:
                logger.warning("No calibration records found")
                return False
            
            logger.info(f"Loading {len(calibration_records)} calibration records")
            
            all_features = []
            valid_ids = []
            
            for record in calibration_records:
                try:
                    record_id = int(record["id"])
                    
                    # Extract measurements
                    pixel_meas = record.get("pixel_measurements", {})
                    scale_factors = record.get("scale_factors", {})
                    bg_info = record.get("background_info", {})
                    
                    # Get raw values
                    avg_mm_per_pixel = float(scale_factors.get("average_mm_per_pixel", 0.0))
                    width_pixels = float(pixel_meas.get("width_pixels", 0.0))
                    height_pixels = float(pixel_meas.get("height_pixels", 0.0))
                    grain_area_pixels = float(pixel_meas.get("grain_area_pixels", 0.0))
                    bbox_area_pixels = float(pixel_meas.get("bbox_area_pixels", 0.0))
                    aspect_ratio = float(pixel_meas.get("aspect_ratio", 0.0))
                    background_ratio = float(bg_info.get("background_ratio", 0.0))
                    
                    # Validate
                    if avg_mm_per_pixel <= 0 or width_pixels <= 0 or height_pixels <= 0:
                        continue
                    
                    # Calculate features
                    area_mm2 = grain_area_pixels * (avg_mm_per_pixel ** 2)
                    width_mm = width_pixels * avg_mm_per_pixel
                    height_mm = height_pixels * avg_mm_per_pixel
                    perimeter_mm = (width_pixels + height_pixels) * avg_mm_per_pixel * 2
                    bbox_to_area_ratio = (
                        grain_area_pixels / bbox_area_pixels
                        if bbox_area_pixels > 0 else 0.0
                    )
                    
                    # Build feature vector (9 features)
                    features = np.array([
                        area_mm2,
                        width_mm,
                        height_mm,
                        perimeter_mm,
                        aspect_ratio,
                        bbox_to_area_ratio,
                        background_ratio,
                        avg_mm_per_pixel
                    ], dtype=np.float32)
                    
                    # Validate features
                    if not np.all(np.isfinite(features)):
                        logger.warning(f"Invalid features for ID {record_id}")
                        continue
                    
                    self.features_by_id[record_id] = features
                    all_features.append(features)
                    valid_ids.append(record_id)
                    
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Error processing record {record.get('id', 'unknown')}: {e}")
                    continue
            
            # Fit scaler
            if all_features:
                all_features_array = np.array(all_features, dtype=np.float32)
                self.scaler.fit(all_features_array)
                self._fitted = True
                
                # Normalize features
                for record_id, features in zip(valid_ids, all_features):
                    normalized = self.scaler.transform(features.reshape(1, -1))[0]
                    self.features_by_id[record_id] = normalized
                
                logger.info(
                    f"Loaded and normalized pixel features for {len(self.features_by_id)} records"
                )
                self._loaded = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading pixel calibration: {e}")
            return False
    
    def get_features(self, record_id: int) -> Optional[np.ndarray]:
        """
        Get normalized features for a record ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            Normalized feature array (9 features) or None
        """
        if not self._loaded:
            self.load()
        
        return self.features_by_id.get(record_id)
    
    def get_feature_dim(self) -> int:
        """Get feature dimension."""
        return len(self.FEATURE_NAMES)

