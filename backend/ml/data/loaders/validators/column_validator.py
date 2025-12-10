"""
Column validator for CSV datasets.

This module validates CSV column structure,
following Single Responsibility Principle.
"""
from typing import Dict, List
import pandas as pd

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.validators")


class ColumnValidator:
    """
    Validator for CSV column structure.
    
    This class is responsible for:
    - Validating required columns exist
    - Checking column presence
    - Reporting missing columns
    
    Following Single Responsibility Principle.
    """
    
    REQUIRED_COLUMNS = {
        'ID': 'id',
        'ALTO': 'alto',
        'ANCHO': 'ancho',
        'GROSOR': 'grosor',
        'PESO': 'peso'
    }
    
    def validate(self, df: pd.DataFrame) -> None:
        """
        Validate that all required columns exist.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            ValueError: If required columns are missing
        """
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS.keys()
            if col not in df.columns
        ]
        
        if missing_columns:
            raise ValueError(
                f"Missing columns in dataset: {missing_columns}"
            )
        
        logger.info(f"Columns validated: {list(df.columns)}")
    
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Get column name mapping (uppercase -> lowercase).
        
        Returns:
            Dictionary mapping uppercase to lowercase column names
        """
        return self.REQUIRED_COLUMNS.copy()

