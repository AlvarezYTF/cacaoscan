"""
Image path validator for datasets.

This module validates image paths and formats,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import List

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.validators")


class ImagePathValidator:
    """
    Validator for image paths and formats.
    
    This class is responsible for:
    - Validating image path formats
    - Checking for format consistency
    - Warning about format mismatches
    
    Following Single Responsibility Principle.
    """
    
    def validate(
        self,
        image_paths: List[Path],
        use_crops: bool = True
    ) -> None:
        """
        Validate image paths and formats.
        
        Args:
            image_paths: List of image paths
            use_crops: Whether dataset should use crops (.png) or raw (.bmp)
        """
        bmp_count = 0
        png_count = 0
        other_count = 0
        
        for img_path in image_paths:
            suffix = img_path.suffix.lower()
            if suffix == '.bmp':
                bmp_count += 1
            elif suffix == '.png':
                png_count += 1
            else:
                other_count += 1
        
        if other_count > 0:
            logger.warning(
                f"Found {other_count} images with non-standard format (.bmp/.png)"
            )
        
        if use_crops:
            if bmp_count > 0:
                logger.warning(
                    f"Dataset configured to use crops (.png) but found {bmp_count} "
                    f".bmp images. This may cause problems."
                )
        else:
            if png_count > 0:
                logger.warning(
                    f"Dataset configured to use raw (.bmp) but found {png_count} "
                    f".png images. This may cause problems."
                )
        
        logger.info(
            f"Image format: {bmp_count} .bmp, {png_count} .png, {other_count} others"
        )

