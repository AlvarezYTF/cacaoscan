"""
Image validator for cacao dataset.

This module handles validation of image files,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import List, Tuple
import pandas as pd

from ...utils.logs import get_ml_logger
from .loggers import MissingImageLogger

logger = get_ml_logger("cacaoscan.ml.data.loaders.validator")


class ImageValidator:
    """
    Validator for image files in dataset.
    
    This class is responsible for:
    - Validating image file existence
    - Logging missing images
    - Filtering valid records
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, media_root: Path):
        """
        Initialize image validator.
        
        Args:
            media_root: Root directory for media files
        """
        self.media_root = media_root
        self.missing_logger = MissingImageLogger()
        
        logger.info(f"ImageValidator initialized (media_root={media_root})")
    
    def validate_images_exist(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[int]]:
        """
        Validate that images corresponding to IDs exist.
        
        Args:
            df: DataFrame with image_path column
            
        Returns:
            Tuple of (valid_dataframe, missing_ids)
        """
        logger.info("Validating image existence...")
        
        missing_ids: List[int] = []
        valid_indices: List[int] = []
        
        for index, row in df.iterrows():
            image_id = row['id']
            # Build absolute path correctly
            image_path = self.media_root / row['image_path']
            
            if image_path.exists():
                valid_indices.append(index)
            else:
                missing_ids.append(int(image_id))
                logger.debug(
                    f"Missing image for ID {image_id}: {image_path}"
                )
        
        if missing_ids:
            self.missing_logger.log_missing_ids(missing_ids)
        
        valid_df = df.loc[valid_indices].copy()
        
        logger.info(
            f"Validation completed: {len(valid_df)} valid images / "
            f"{len(missing_ids)} missing"
        )
        
        return valid_df, missing_ids
    
    def validate_single_image(self, image_path: Path) -> bool:
        """
        Validate a single image file exists.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image exists, False otherwise
        """
        if isinstance(image_path, str):
            image_path = Path(image_path)
        
        # Convert to absolute path if relative
        if not image_path.is_absolute():
            image_path = self.media_root / image_path
        
        return image_path.exists()

