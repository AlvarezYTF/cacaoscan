"""
Calibration data loader for pixel features.

This module handles loading and parsing of pixel calibration JSON files,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict, Optional, Any, Sequence
import numpy as np

from ...utils.logs import get_ml_logger
from ...utils.paths import get_datasets_dir
from ...utils.io import load_json
from .indexers import CalibrationIndexer

logger = get_ml_logger("cacaoscan.ml.data.loaders.calibration")


class CalibrationDataLoader:
    """
    Loader for pixel calibration JSON files.
    
    This class is responsible for:
    - Loading calibration JSON files
    - Parsing calibration records
    - Providing access to calibration data
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, calibration_file: Optional[Path] = None):
        """
        Initialize calibration loader.
        
        Args:
            calibration_file: Path to pixel_calibration.json (optional)
        """
        if calibration_file is None:
            calibration_file = get_datasets_dir() / "pixel_calibration.json"
        
        self.calibration_file = Path(calibration_file)
        self.calibration_data: Optional[Dict[str, Any]] = None
        self._loaded = False
        self.indexer = CalibrationIndexer()
        
        logger.info(f"CalibrationDataLoader initialized (file={self.calibration_file})")
    
    def load(self) -> Dict[int, Dict[str, Any]]:
        """
        Load calibration data and return indexed by ID.
        
        Returns:
            Dictionary mapping record_id -> calibration_record
        """
        if self._loaded and self.calibration_data is not None:
            return self._index_by_id(self.calibration_data)
        
        if not self.calibration_file.exists():
            logger.warning(
                f"Calibration file not found: {self.calibration_file}"
            )
            return {}
        
        try:
            self.calibration_data = load_json(self.calibration_file)
            self._loaded = True
            
            calibration_records = self.calibration_data.get(
                "calibration_records", []
            )
            
            if not calibration_records:
                logger.warning("No calibration records found")
                return {}
            
            logger.info(
                f"Loaded {len(calibration_records)} calibration records"
            )
            
            return self._index_by_id(self.calibration_data)
            
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")
            return {}
    
    def _index_by_id(
        self,
        calibration_data: Dict[str, Any]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Index calibration records by ID.
        
        Args:
            calibration_data: Calibration data dictionary
            
        Returns:
            Dictionary mapping record_id -> calibration_record
        """
        calibration_records = calibration_data.get("calibration_records", [])
        return self.indexer.index_by_id(calibration_records)
    
    def get_calibration_data(self) -> Optional[Dict[str, Any]]:
        """
        Get raw calibration data.
        
        Returns:
            Raw calibration data dictionary or None
        """
        if not self._loaded:
            self.load()
        
        return self.calibration_data

