"""
Duplicate filter for dataset records.

This module handles duplicate record removal,
following Single Responsibility Principle.
"""
import pandas as pd

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.filters")


class DuplicateFilter:
    """
    Filter for removing duplicate records.
    
    This class is responsible for:
    - Detecting duplicate IDs
    - Removing duplicates
    - Logging removal statistics
    
    Following Single Responsibility Principle.
    """
    
    def filter(self, df: pd.DataFrame, id_column: str = 'id') -> pd.DataFrame:
        """
        Remove duplicate IDs.
        
        Args:
            df: DataFrame to process
            id_column: Name of ID column
            
        Returns:
            DataFrame without duplicates
        """
        duplicates = df[id_column].duplicated().sum()
        
        if duplicates > 0:
            logger.warning(
                f"Found {duplicates} duplicate IDs. Removing duplicates..."
            )
            df = df.drop_duplicates(subset=[id_column], keep='first')
        
        return df

