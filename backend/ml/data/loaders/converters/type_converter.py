"""
Type converter for CSV data.

This module handles data type conversion and cleaning,
following Single Responsibility Principle.
"""
import pandas as pd
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.converters")


class TypeConverter:
    """
    Converter for CSV data types.
    
    This class is responsible for:
    - Converting columns to numeric types
    - Handling null values
    - Cleaning invalid data
    
    Following Single Responsibility Principle.
    """
    
    NUMERIC_COLUMNS = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO']
    
    def convert(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert data types and remove nulls.
        
        Args:
            df: DataFrame to process
            
        Returns:
            Cleaned DataFrame
        """
        initial_count = len(df)
        df = df.copy()
        
        # Convert to numeric types
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').astype('Int64')
        df['ALTO'] = pd.to_numeric(df['ALTO'], errors='coerce').astype(np.float32)
        df['ANCHO'] = pd.to_numeric(df['ANCHO'], errors='coerce').astype(np.float32)
        df['GROSOR'] = pd.to_numeric(df['GROSOR'], errors='coerce').astype(np.float32)
        df['PESO'] = pd.to_numeric(df['PESO'], errors='coerce').astype(np.float32)
        
        # Remove nulls
        df = df.dropna()
        final_count = len(df)
        
        if initial_count != final_count:
            logger.warning(
                f"Removed {initial_count - final_count} rows with null values"
            )
        
        return df

