"""
CSV loader for cacao dataset.

This module orchestrates CSV file detection and loading,
following Single Responsibility and Dependency Inversion principles.
"""
from pathlib import Path
from typing import Optional
import pandas as pd

from ...utils.logs import get_ml_logger
from .detectors.csv_detector import CSVDetector
from .handlers.encoding_handler import EncodingHandler
from .validators.column_validator import ColumnValidator
from .converters.type_converter import TypeConverter
from .normalizers.name_normalizer import NameNormalizer
from .filters.duplicate_filter import DuplicateFilter
from .generators.path_generator import PathGenerator

logger = get_ml_logger("cacaoscan.ml.data.loaders.csv")


class CSVLoader:
    """
    Loader for CSV dataset files.
    
    This class orchestrates CSV loading by delegating to specialized classes,
    following Single Responsibility and Dependency Inversion principles.
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize CSV loader.
        
        Args:
            csv_path: Specific path to CSV file (optional)
        """
        # Initialize specialized components
        self.csv_detector = CSVDetector()
        self.encoding_handler = EncodingHandler()
        self.column_validator = ColumnValidator()
        self.type_converter = TypeConverter()
        self.name_normalizer = NameNormalizer(
            self.column_validator.get_column_mapping()
        )
        self.duplicate_filter = DuplicateFilter()
        self.path_generator = PathGenerator()
        
        # Resolve CSV path
        self.csv_path: Optional[Path] = None
        
        if csv_path is None:
            detected_path = self.csv_detector.detect()
            if detected_path is None:
                self.csv_path = None  # Will be handled as mock
                return
            self.csv_path = detected_path
        else:
            self.csv_path = Path(csv_path)
        
        if self.csv_path and not self.csv_path.exists():
            raise FileNotFoundError(
                f"Dataset CSV not found: {self.csv_path}"
            )
        
        logger.info(f"CSVLoader initialized with CSV: {self.csv_path}")
    
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Load dataset CSV and validate data types.
        
        Returns:
            DataFrame with validated and normalized data
            
        Raises:
            ValueError: If CSV structure is invalid
        """
        if self.csv_path is None:
            raise ValueError("CSV path not set. Cannot load dataset.")
        
        logger.info(f"Loading dataset from {self.csv_path}")
        
        # Load CSV with encoding handling
        df = self.encoding_handler.load_csv(self.csv_path)
        
        logger.info(
            f"CSV loaded: {len(df)} rows, {len(df.columns)} columns"
        )
        logger.info(f"Columns found: {list(df.columns)}")
        
        # Validate required columns
        self.column_validator.validate(df)
        
        # Convert data types and handle nulls
        df = self.type_converter.convert(df)
        
        # Normalize column names
        df = self.name_normalizer.normalize(df)
        
        # Generate image paths
        df = self.path_generator.generate(df)
        
        # Remove duplicates
        df = self.duplicate_filter.filter(df)
        
        logger.info(
            f"Dataset loaded successfully: {len(df)} valid records"
        )
        logger.info(f"Final columns: {list(df.columns)}")
        
        return df
    
    
    def get_csv_path(self) -> Optional[Path]:
        """
        Get the CSV file path.
        
        Returns:
            Path to CSV file or None
        """
        return self.csv_path

