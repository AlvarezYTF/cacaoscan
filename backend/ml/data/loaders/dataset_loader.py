"""
Main dataset loader for cacao regression.

This module orchestrates CSV loading and image validation,
following Single Responsibility and Dependency Inversion principles.
"""
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
import os
import sys

# Configure Django
project_root = Path(__file__).resolve().parents[3]  # data/loaders/ml/backend
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
import django
try:
    django.setup()
    from django.conf import settings
    MEDIA_ROOT = Path(settings.MEDIA_ROOT)
except Exception as e:
    print(f"Warning: Django setup failed (normal if not in Django context). Error: {e}")
    MEDIA_ROOT = project_root / "media"

from ...utils.logs import get_ml_logger
from .csv_loader import CSVLoader
from .image_validator import ImageValidator
from .builders import RecordBuilder

logger = get_ml_logger("cacaoscan.ml.data.loaders")


class CacaoDatasetLoader:
    """
    Main loader and validator for cacao dataset.
    
    This class orchestrates CSV loading and image validation,
    following Single Responsibility Principle by delegating to
    specialized classes (CSVLoader, ImageValidator).
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize dataset loader.
        
        Args:
            csv_path: Specific path to CSV (optional)
        """
        # Initialize specialized loaders
        self.csv_loader = CSVLoader(csv_path)
        self.image_validator = ImageValidator(MEDIA_ROOT)
        self.record_builder = RecordBuilder(MEDIA_ROOT)
        
        logger.info("CacaoDatasetLoader initialized")
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Load the dataset CSV and validate data types.
        
        Returns:
            DataFrame with validated data
        """
        return self.csv_loader.load_dataset()
    
    def validate_images_exist(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[int]]:
        """
        Validate that images corresponding to IDs exist.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (valid_dataframe, missing_ids)
        """
        return self.image_validator.validate_images_exist(df)
    
    def get_valid_records(self) -> List[Dict]:
        """
        Get list of valid records with image paths.
        
        Returns:
            List of valid record dictionaries
        """
        df = self.load_dataset()
        valid_df, _ = self.validate_images_exist(df)
        
        valid_records = self.record_builder.build_from_dataframe(valid_df)
        
        logger.info(f"Generated {len(valid_records)} valid records")
        return valid_records
    
    def get_dataset_stats(self) -> Dict:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary with dataset statistics
        """
        try:
            df = self.load_dataset()
            valid_df, missing_ids = self.validate_images_exist(df)
            
            stats = {
                'total_records': len(df),
                'valid_records': len(valid_df),
                'missing_images': len(missing_ids),
                'missing_ids': sorted(missing_ids),
                'dimensions_stats': {}
            }
            
            if len(valid_df) > 0:
                for target in ['alto', 'ancho', 'grosor', 'peso']:
                    stats['dimensions_stats'][target] = {
                        'min': float(valid_df[target].min()),
                        'max': float(valid_df[target].max()),
                        'mean': float(valid_df[target].mean()),
                        'std': float(valid_df[target].std()),
                        'median': float(valid_df[target].median()),
                        'count': int(valid_df[target].count())
                    }
            else:
                logger.warning("No valid data to calculate statistics")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dataset statistics: {e}")
            return {}
    
    def filter_by_target(
        self,
        df: pd.DataFrame,
        target: str
    ) -> pd.DataFrame:
        """
        Filter dataset by specific target.
        
        Args:
            df: DataFrame to filter
            target: Target to filter by ('alto', 'ancho', 'grosor', 'peso')
            
        Returns:
            Filtered DataFrame
            
        Raises:
            ValueError: If target is invalid
        """
        if target not in ['alto', 'ancho', 'grosor', 'peso']:
            raise ValueError(
                f"Invalid target: {target}. "
                f"Must be one of: alto, ancho, grosor, peso"
            )
        
        filtered_df = df[df[target].notna()]
        logger.info(
            f"Dataset filtered by {target}: {len(filtered_df)} records"
        )
        return filtered_df
    
    def get_target_data(
        self,
        target: str
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Get data for specific target with valid records.
        
        Args:
            target: Target to get data for
            
        Returns:
            Tuple of (target_values_array, records_list)
        """
        df = self.load_dataset()
        valid_df, _ = self.validate_images_exist(df)
        filtered_df = self.filter_by_target(valid_df, target)
        
        records = []
        target_values = []
        
        for _, row in filtered_df.iterrows():
            record = self.record_builder.build_target_record(row, target)
            records.append(record)
            target_values.append(float(row[target]))
        
        return np.array(target_values, dtype=np.float32), records


# Convenience functions for backward compatibility
def load_cacao_dataset(
    csv_path: Optional[str] = None
) -> Tuple[pd.DataFrame, List[int]]:
    """
    Convenience function to load dataset and validate images.
    """
    loader = CacaoDatasetLoader(csv_path)
    df = loader.load_dataset()
    return loader.validate_images_exist(df)


def get_valid_cacao_records(
    csv_path: Optional[str] = None
) -> List[Dict]:
    """
    Convenience function to get valid records.
    """
    loader = CacaoDatasetLoader(csv_path)
    return loader.get_valid_records()


def get_target_data(
    target: str,
    csv_path: Optional[str] = None
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Convenience function to get data for specific target.
    """
    loader = CacaoDatasetLoader(csv_path)
    return loader.get_target_data(target)

