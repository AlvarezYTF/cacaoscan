"""
Name normalizer for CSV columns.

This module handles column name normalization,
following Single Responsibility Principle.
"""
from typing import Dict
import pandas as pd

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.normalizers")


class NameNormalizer:
    """
    Normalizer for CSV column names.
    
    This class is responsible for:
    - Normalizing column names to lowercase
    - Mapping uppercase to lowercase
    - Renaming columns
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, column_mapping: Dict[str, str]):
        """
        Initialize name normalizer.
        
        Args:
            column_mapping: Dictionary mapping uppercase to lowercase names
        """
        self.column_mapping = column_mapping
        logger.debug(f"NameNormalizer initialized with {len(column_mapping)} mappings")
    
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to lowercase.
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            DataFrame with normalized column names
        """
        return df.rename(columns=self.column_mapping)

