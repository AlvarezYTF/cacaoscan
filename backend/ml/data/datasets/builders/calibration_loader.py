"""
Calibration loader for pixel calibration data.

This module handles loading calibration records from JSON files,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict, Optional
import json

from ....utils.logs import get_ml_logger
from .encoding_handler import EncodingHandler

logger = get_ml_logger("cacaoscan.ml.data.datasets.builders")


class CalibrationLoader:
    """
    Loader for pixel calibration records.
    
    This class is responsible for:
    - Loading calibration JSON files
    - Handling multiple encodings
    - Indexing records by ID
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, calibration_file: Optional[Path] = None):
        """
        Initialize calibration loader.
        
        Args:
            calibration_file: Path to pixel_calibration.json
        """
        self.calibration_file = calibration_file
        self.encoding_handler = EncodingHandler()
        
        logger.debug(f"CalibrationLoader initialized (file={calibration_file})")
    
    def load(self) -> Dict[int, Dict]:
        """
        Load calibration records from JSON file.
        
        Returns:
            Dictionary mapping record ID to calibration record
            
        Raises:
            FileNotFoundError: If calibration file doesn't exist
        """
        if self.calibration_file is None:
            raise ValueError("Calibration file path not set")
        
        if not self.calibration_file.exists():
            raise FileNotFoundError(
                f"Pixel calibration file not found: {self.calibration_file}"
            )
        
        calibration_data = self._load_json_with_encodings()
        calibration_records = calibration_data.get("calibration_records", [])
        calibration_by_id = {rec["id"]: rec for rec in calibration_records}
        
        logger.info(f"Loaded {len(calibration_by_id)} calibration records")
        return calibration_by_id
    
    def _load_json_with_encodings(self) -> Dict:
        """Load JSON file trying multiple encodings."""
        text_content = self.encoding_handler.decode_file(self.calibration_file)
        return json.loads(text_content)

