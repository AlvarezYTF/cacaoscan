"""
Image loader for datasets.

This module handles loading and transforming images,
following Single Responsibility Principle.
"""
from pathlib import Path
from typing import Optional
import torch
import torchvision.transforms as transforms
from PIL import Image

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.loaders")


class ImageLoader:
    """
    Loader for images with transformations.
    
    This class is responsible for:
    - Loading images from paths
    - Converting to RGB
    - Applying transformations
    - Validating image tensors
    
    Following Single Responsibility Principle.
    """
    
    def __init__(self, transform: Optional[transforms.Compose] = None):
        """
        Initialize image loader.
        
        Args:
            transform: Image transformation pipeline
        """
        self.transform = transform
        self._default_transform = self._create_default_transform()
        
        logger.debug("ImageLoader initialized")
    
    def load(self, image_path: Path) -> torch.Tensor:
        """
        Load and transform image to tensor.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image tensor [C, H, W]
            
        Raises:
            ValueError: If image cannot be loaded or has wrong shape
        """
        try:
            image = Image.open(image_path)
            
            if image is None:
                raise ValueError(f"Image could not be loaded: {image_path}")
            
            if image.mode != 'RGB':
                logger.debug(
                    f"Converting image {image_path.name} from {image.mode} to RGB"
                )
                image = image.convert('RGB')
            
            transform_to_use = self.transform or self._default_transform
            image_tensor = transform_to_use(image)
            
            if image_tensor.shape[0] != 3:
                raise ValueError(
                    f"Image must have 3 RGB channels, got {image_tensor.shape[0]} channels"
                )
            
            return image_tensor
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise
    
    @staticmethod
    def _create_default_transform() -> transforms.Compose:
        """Create default ImageNet normalization transform."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

