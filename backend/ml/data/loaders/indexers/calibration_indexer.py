"""
Calibration indexer for organizing calibration records.

This module handles indexing calibration records by ID,
following Single Responsibility Principle.
"""
from typing import Dict, Any, List

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.indexers")


class CalibrationIndexer:
    """
    Indexer for calibration records.
    
    This class is responsible for:
    - Indexing calibration records by ID
    - Validating record IDs
    - Handling invalid records
    
    Following Single Responsibility Principle.
    """
    
    def index_by_id(
        self,
        calibration_records: List[Dict[str, Any]]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Index calibration records by ID.
        
        Args:
            calibration_records: List of calibration record dictionaries
            
        Returns:
            Dictionary mapping record_id -> calibration_record
        """
        indexed: Dict[int, Dict[str, Any]] = {}
        
        for record in calibration_records:
            try:
                record_id = int(record["id"])
                indexed[record_id] = record
            except (KeyError, TypeError, ValueError):
                logger.warning(
                    "Calibration record without valid 'id' field, skipping"
                )
                continue
        
        logger.debug(f"Indexed {len(indexed)} calibration records")
        return indexed

