"""
Path generator for dataset images.

This module generates image paths for dataset records,
following Single Responsibility Principle.
"""
import pandas as pd

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.loaders.generators")


class PathGenerator:
    """
    Generator for image paths in dataset.
    
    This class is responsible for:
    - Generating image paths from IDs
    - Creating relative paths to MEDIA_ROOT
    - Adding path columns to DataFrame
    
    Following Single Responsibility Principle.
    """
    
    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add image path columns to DataFrame.
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with image paths
        """
        df = df.copy()
        
        # Generate relative paths to MEDIA_ROOT
        df['image_path'] = df['id'].apply(
            lambda x: f"cacao_images/raw/{x}.bmp"
        )
        df['crop_image_path'] = df['id'].apply(
            lambda x: f"cacao_images/crops/{x}.png"
        )
        
        logger.debug(f"Generated image paths for {len(df)} records")
        return df

