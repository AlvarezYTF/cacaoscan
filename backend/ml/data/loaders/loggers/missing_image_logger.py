"""
Missing image logger for validation results.

This module handles logging missing image IDs,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import List

from ....utils.logs import get_ml_logger
from ....utils.io import write_log
from ....utils.paths import get_missing_ids_log_path

logger = get_ml_logger("cacaoscan.ml.data.loaders.loggers")


class MissingImageLogger:
    """
    Logger for missing image IDs.
    
    This class is responsible for:
    - Logging missing image IDs
    - Writing logs to file
    - Formatting log messages
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, log_path: Path | None = None):
        """
        Initialize missing image logger.
        
        Args:
            log_path: Path to log file (default: from get_missing_ids_log_path())
        """
        self.log_path = log_path or get_missing_ids_log_path()
        logger.debug(f"MissingImageLogger initialized (log_path={self.log_path})")
    
    def log_missing_ids(self, missing_ids: List[int]) -> None:
        """
        Log missing image IDs to file.
        
        Args:
            missing_ids: List of missing image IDs
        """
        if not missing_ids:
            return
        
        log_message = f"IDs with missing images: {sorted(missing_ids)}"
        write_log(self.log_path, log_message)
        logger.warning(
            f"Saved log of {len(missing_ids)} missing IDs to {self.log_path}"
        )

