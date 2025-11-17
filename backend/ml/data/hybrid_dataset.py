"""
Hybrid dataset for cacao regression with normalized pixel features.

Returns:
    img_tensor: [3, H, W] - Image tensor
    target_tensor: [4] - Targets in order: [alto_mm, ancho_mm, grosor_mm, peso_g]
    pixel_tensor: [10] - Pixel features in order: [height_mm_est, width_mm_est, area_mm2_est, perimeter_mm, aspect_ratio, bbox_ratio, background_ratio, avg_mm_per_pixel, compactness, roundness]
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms

from ..utils.logs import get_ml_logger
from .pixel_features_loader import PixelFeaturesLoader

logger = get_ml_logger("cacaoscan.ml.data.hybrid_dataset")


class HybridCacaoDataset(Dataset):
    """
    Dataset for hybrid cacao regression model.
    
    Returns:
        img_tensor: Image tensor [3, H, W]
        target_tensor: Targets tensor [4] in order: [alto_mm, ancho_mm, grosor_mm, peso_g]
        pixel_tensor: Pixel features tensor [10] in order: [height_mm_est, width_mm_est, area_mm2_est, perimeter_mm, aspect_ratio, bbox_ratio, background_ratio, avg_mm_per_pixel, compactness, roundness]
    """
    
    TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]
    PIXEL_FEATURE_ORDER = [
        "height_mm_est",
        "width_mm_est",
        "area_mm2_est",
        "perimeter_mm",
        "aspect_ratio",
        "bbox_ratio",
        "background_ratio",
        "avg_mm_per_pixel",
        "compactness",
        "roundness"
    ]
    
    def __init__(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        transform: transforms.Compose,
        pixel_features_loader: Optional[PixelFeaturesLoader] = None,
        record_ids: Optional[List[int]] = None,
        validate: bool = True
    ):
        """
        Initialize the hybrid dataset.
        
        Args:
            image_paths: List of image paths
            targets: Dictionary of target arrays {target: array}
            transform: Image transformations
            pixel_features_loader: PixelFeaturesLoader instance (optional)
            record_ids: List of record IDs corresponding to image_paths (required if pixel_features_loader is provided)
            validate: Whether to validate data consistency
        """
        self.image_paths = image_paths
        self.targets = targets
        self.transform = transform
        self.pixel_features_loader = pixel_features_loader
        self.record_ids = record_ids
        
        # Validate structure
        if validate:
            self._validate_structure()
        
        logger.info(f"Hybrid dataset initialized with {len(image_paths)} samples")
    
    def _validate_structure(self) -> None:
        """Validate data structure consistency."""
        # Validate targets
        missing_targets = set(self.TARGET_ORDER) - set(self.targets.keys())
        if missing_targets:
            raise ValueError(f"Missing targets: {missing_targets}")
        
        # Validate lengths
        lengths = [len(self.image_paths)] + [len(v) for v in self.targets.values()]
        if len(set(lengths)) > 1:
            raise ValueError(
                f"Inconsistent lengths: images={len(self.image_paths)}, "
                f"targets={[len(v) for v in self.targets.values()]}"
            )
        
        # Validate pixel features if loader is provided
        if self.pixel_features_loader is not None:
            if self.record_ids is None:
                raise ValueError("record_ids required when pixel_features_loader is provided")
            
            if len(self.record_ids) != len(self.image_paths):
                raise ValueError(
                    f"Inconsistent lengths: images={len(self.image_paths)}, "
                    f"record_ids={len(self.record_ids)}"
                )
            
            # Check that all records have pixel features
            missing_features = []
            for idx, record_id in enumerate(self.record_ids):
                features = self.pixel_features_loader.get_features_by_id(record_id)
                if features is None:
                    missing_features.append((idx, record_id))
            
            if missing_features:
                logger.warning(
                    f"Missing pixel features for {len(missing_features)} records. "
                    f"First 5: {missing_features[:5]}"
                )
        
        logger.debug("Dataset structure validated")
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Get a sample from the dataset.
        
        Args:
            idx: Sample index
            
        Returns:
            Tuple of (img_tensor, target_tensor, pixel_tensor)
        """
        # Load image
        image_path = self.image_paths[idx]
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_tensor = self.transform(image)
            
            # Validate image tensor
            if img_tensor.shape[0] != 3:
                raise ValueError(f"Image must have 3 channels, got {img_tensor.shape[0]}")
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise
        
        # Get targets in order: [alto_mm, ancho_mm, grosor_mm, peso_g]
        target_tensor = torch.tensor([
            float(self.targets["alto"][idx]),
            float(self.targets["ancho"][idx]),
            float(self.targets["grosor"][idx]),
            float(self.targets["peso"][idx])
        ], dtype=torch.float32)
        
        # Get pixel features in order: [height_mm_est, width_mm_est, area_mm2_est, perimeter_mm, aspect_ratio, bbox_ratio, background_ratio, avg_mm_per_pixel, compactness, roundness]
        if self.pixel_features_loader is not None and self.record_ids is not None:
            record_id = self.record_ids[idx]
            pixel_features = self.pixel_features_loader.get_features_by_id(record_id)
            
            if pixel_features is None:
                # Use zeros if features not found
                logger.warning(f"Pixel features not found for record_id {record_id}, using zeros")
                pixel_features = np.zeros(10, dtype=np.float32)
            
            pixel_tensor = torch.tensor(pixel_features, dtype=torch.float32)
        else:
            # Use zeros if no pixel features loader
            pixel_tensor = torch.zeros(10, dtype=torch.float32)
        
        return img_tensor, target_tensor, pixel_tensor

