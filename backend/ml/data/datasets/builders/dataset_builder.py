"""
Dataset builder for cacao datasets.

This module builds dataset records from valid records and calibration data,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

from ....utils.logs import get_ml_logger
from .pixel_feature_builder import PixelFeatureBuilder
from .path_resolver import PathResolver

logger = get_ml_logger("cacaoscan.ml.data.datasets.builders")


class DatasetBuilder:
    """
    Builder for dataset records.
    
    This class is responsible for:
    - Building dataset records from valid records and calibration
    - Resolving crop paths
    - Filtering valid records
    
    Following Single Responsibility Principle.
    """
    
    TARGETS = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(self, crops_dir: Path):
        """
        Initialize dataset builder.
        
        Args:
            crops_dir: Directory for crop images
        """
        self.crops_dir = crops_dir
        self.pixel_feature_builder = PixelFeatureBuilder()
        self.path_resolver = PathResolver(crops_dir)
        
        logger.debug(f"DatasetBuilder initialized (crops_dir={crops_dir})")
    
    def build(
        self,
        valid_records: List[Dict],
        calibration_by_id: Dict[int, Dict]
    ) -> Dict[str, object]:
        """
        Build dataset records from valid records and calibration.
        
        Args:
            valid_records: List of valid records from CSV
            calibration_by_id: Dictionary of calibration records by ID
            
        Returns:
            Dictionary with dataset data
        """
        records: List[Dict] = []
        record_ids: List[int] = []
        image_paths: List[Path] = []
        target_values = {target: [] for target in self.TARGETS}
        pixel_features: List[np.ndarray] = []
        missing_calibration: List[int] = []
        missing_images: List[Tuple[int, Path]] = []
        
        for record in valid_records:
            crop_path = self.path_resolver.resolve(record)
            
            if not self.path_resolver.exists(crop_path):
                missing_images.append((record["id"], crop_path))
                continue
            
            calibration_entry = calibration_by_id.get(record["id"])
            if calibration_entry is None:
                missing_calibration.append(record["id"])
                continue
            
            feature_vector = self.pixel_feature_builder.build(calibration_entry)
            
            if not np.all(np.isfinite(feature_vector)):
                logger.warning(f"Invalid pixel features for ID {record['id']}")
                continue
            
            self._append_record_data(
                record,
                crop_path,
                feature_vector,
                records,
                record_ids,
                image_paths,
                target_values,
                pixel_features
            )
        
        return {
            "records": records,
            "record_ids": record_ids,
            "image_paths": image_paths,
            "target_values": {
                target: np.array(values, dtype=np.float32)
                for target, values in target_values.items()
            },
            "pixel_features": np.array(pixel_features, dtype=np.float32),
            "missing_calibration": missing_calibration,
            "missing_images": missing_images
        }
    
    def _append_record_data(
        self,
        record: Dict,
        crop_path: Path,
        pixel_feature_vector: np.ndarray,
        records: List[Dict],
        record_ids: List[int],
        image_paths: List[Path],
        target_values: Dict[str, List[float]],
        pixel_features: List[np.ndarray]
    ) -> None:
        """Append record data to lists."""
        if not records:
            logger.info(
                f"First record pixel features (10 dims): "
                f"area_mm2={pixel_feature_vector[0]:.2f}, "
                f"perimeter_mm={pixel_feature_vector[3]:.2f}, "
                f"compactness={pixel_feature_vector[8]:.2f}, "
                f"roundness={pixel_feature_vector[9]:.2f}"
            )
        
        records.append(record)
        record_ids.append(record["id"])
        image_paths.append(crop_path)
        
        for target in self.TARGETS:
            target_values[target].append(float(record[target]))
        
        pixel_features.append(pixel_feature_vector)

