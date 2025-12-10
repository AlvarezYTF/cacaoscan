"""
Encoding handler for CSV file reading.

This module handles multiple encoding detection and decoding,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import List
import pandas as pd

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.handlers")


class EncodingHandler:
    """
    Handler for CSV file encoding detection and decoding.
    
    This class is responsible for:
    - Detecting file encodings
    - Loading CSV with multiple encoding attempts
    - Providing fallback decoding strategies
    
    Following Single Responsibility Principle.
    """
    
    DEFAULT_ENCODINGS: List[str] = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def __init__(self, encodings: List[str] | None = None):
        """
        Initialize encoding handler.
        
        Args:
            encodings: List of encodings to try (default: utf-8, latin-1, cp1252, iso-8859-1)
        """
        self.encodings = encodings or self.DEFAULT_ENCODINGS
        logger.debug(f"EncodingHandler initialized with {len(self.encodings)} encodings")
    
    def load_csv(self, csv_path: Path) -> pd.DataFrame:
        """
        Load CSV file trying multiple encodings.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Loaded DataFrame
        """
        for encoding in self.encodings:
            try:
                df = pd.read_csv(csv_path, sep=',', encoding=encoding)
                logger.debug(f"Successfully loaded CSV with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                continue
        
        # Last resort: use utf-8 with errors='replace'
        logger.warning(
            f"Using utf-8 with error replacement for {csv_path}"
        )
        return pd.read_csv(
            csv_path,
            sep=',',
            encoding='utf-8',
            errors='replace'
        )

