"""
Record builder for dataset records.

This module handles building record dictionaries from DataFrame rows,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Dict, List
import pandas as pd

from ....utils.logs import get_ml_logger
from ....utils.io import get_file_timestamp

logger = get_ml_logger("cacaoscan.ml.data.loaders.builders")


class RecordBuilder:
    """
    Builder for dataset records.
    
    This class is responsible for:
    - Building record dictionaries from DataFrame rows
    - Resolving image paths
    - Adding metadata (timestamps)
    
    Following Single Responsibility Principle.
    """
    
    TARGETS = ['alto', 'ancho', 'grosor', 'peso']
    
    def __init__(self, media_root: Path):
        """
        Initialize record builder.
        
        Args:
            media_root: Root directory for media files
        """
        self.media_root = media_root
        logger.debug(f"RecordBuilder initialized (media_root={media_root})")
    
    def build_from_dataframe(
        self,
        df: pd.DataFrame
    ) -> List[Dict]:
        """
        Build records from DataFrame.
        
        Args:
            df: DataFrame with dataset columns
            
        Returns:
            List of record dictionaries
        """
        records: List[Dict] = []
        
        for _, row in df.iterrows():
            record = self._build_single_record(row)
            records.append(record)
        
        logger.info(f"Built {len(records)} records from DataFrame")
        return records
    
    def _build_single_record(self, row: pd.Series) -> Dict:
        """
        Build a single record from DataFrame row.
        
        Args:
            row: DataFrame row
            
        Returns:
            Record dictionary
        """
        raw_path = self.media_root / row['image_path']
        crop_path = self.media_root / row['crop_image_path']
        
        record = {
            'id': int(row['id']),
            'alto': float(row['alto']),
            'ancho': float(row['ancho']),
            'grosor': float(row['grosor']),
            'peso': float(row['peso']),
            'image_path': str(raw_path),
            'raw_image_path': str(raw_path),
            'crop_image_path': str(crop_path),
            'mask_image_path': None,
            'timestamp': (
                get_file_timestamp(raw_path)
                if raw_path.exists() else None
            )
        }
        
        return record
    
    def build_target_record(
        self,
        row: pd.Series,
        target: str
    ) -> Dict:
        """
        Build a record for specific target.
        
        Args:
            row: DataFrame row
            target: Target name ('alto', 'ancho', 'grosor', 'peso')
            
        Returns:
            Record dictionary with target value
        """
        image_path = self.media_root / row['image_path']
        
        return {
            'id': int(row['id']),
            'image_path': str(image_path),
            target: float(row[target])
        }

