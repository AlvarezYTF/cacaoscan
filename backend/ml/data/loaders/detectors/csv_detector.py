"""
CSV file detector for dataset loading.

This module handles CSV file detection,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Optional

from ....utils.paths import get_datasets_dir
from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.detectors")


class CSVDetector:
    """
    Detector for CSV files in datasets directory.
    
    This class is responsible for:
    - Detecting CSV files
    - Prioritizing preferred file names
    - Returning the best match
    
    Following Single Responsibility Principle.
    """
    
    PREFERRED_NAMES = [
        "dataset_cacao.clean.csv",
        "dataset_cacao.csv",
        "dataset_sin_comillas.csv",
        "dataset.csv"
    ]
    
    def __init__(self, datasets_dir: Optional[Path] = None):
        """
        Initialize CSV detector.
        
        Args:
            datasets_dir: Directory to search (default: from get_datasets_dir())
        """
        self.datasets_dir = datasets_dir or get_datasets_dir()
        logger.debug(f"CSVDetector initialized (dir={self.datasets_dir})")
    
    def detect(self) -> Optional[Path]:
        """
        Detect CSV file in datasets directory.
        
        Returns:
            Path to detected CSV file, or None if not found
        """
        if not self.datasets_dir.exists():
            logger.warning(f"Datasets directory not found: {self.datasets_dir}")
            return None
        
        csv_files = list(self.datasets_dir.glob("*.csv"))
        
        if not csv_files:
            logger.warning(f"No CSV files found in {self.datasets_dir}")
            return None
        
        # Prioritize preferred names
        for preferred_name in self.PREFERRED_NAMES:
            for csv_file in csv_files:
                if csv_file.name == preferred_name:
                    logger.info(f"Preferred CSV file detected: {csv_file}")
                    return csv_file
        
        # If no preferred file, use the first one
        csv_file = csv_files[0]
        logger.warning(
            f"Multiple CSV files found. Using: {csv_file}"
        )
        return csv_file

