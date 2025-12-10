"""
Transform validator for datasets.

This module validates image transformations,
following Single Responsibility Principle.
"""
import torchvision.transforms as transforms

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.datasets.validators")


class TransformValidator:
    """
    Validator for image transformations.
    
    This class is responsible for:
    - Validating ImageNet normalization
    - Checking transform parameters
    
    Following Single Responsibility Principle.
    """
    
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]
    
    def validate(self, transform: transforms.Compose | None) -> None:
        """
        Validate that transformations include ImageNet normalization.
        
        Args:
            transform: Image transformation pipeline
        """
        if transform is None:
            logger.warning(
                "No transform provided. ImageNet normalization recommended."
            )
            return
        
        normalize_transform = self._find_normalize_transform(transform)
        
        if normalize_transform is None:
            logger.warning(
                "Transformations do not include ImageNet normalization. "
                "Recommended: transforms.Normalize with "
                f"mean={self.IMAGENET_MEAN}, std={self.IMAGENET_STD}"
            )
            return
        
        if not self._validate_normalization_params(normalize_transform):
            logger.warning(
                f"Normalization parameters differ from ImageNet standard. "
                f"Expected: mean={self.IMAGENET_MEAN}, std={self.IMAGENET_STD}. "
                f"Got: mean={normalize_transform.mean}, std={normalize_transform.std}"
            )
        else:
            logger.debug("ImageNet normalization validated correctly")
    
    def _find_normalize_transform(
        self,
        transforms_list: transforms.Compose
    ) -> transforms.Normalize | None:
        """Find Normalize transform in transformation pipeline."""
        transform_items = (
            transforms_list.transforms
            if hasattr(transforms_list, 'transforms')
            else [transforms_list]
        )
        
        for t in transform_items:
            if isinstance(t, transforms.Compose):
                found = self._find_normalize_transform(t)
                if found is not None:
                    return found
            elif isinstance(t, transforms.Normalize):
                return t
        
        return None
    
    def _validate_normalization_params(
        self,
        normalize_transform: transforms.Normalize
    ) -> bool:
        """Validate that normalization parameters match ImageNet standard."""
        mean_match = all(
            abs(m - e) < 0.01
            for m, e in zip(normalize_transform.mean, self.IMAGENET_MEAN)
        )
        std_match = all(
            abs(s - e) < 0.01
            for s, e in zip(normalize_transform.std, self.IMAGENET_STD)
        )
        
        return mean_match and std_match

