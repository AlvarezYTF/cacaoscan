"""
Image transformation utilities.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: image_transforms, mask_refinement, segmentation_models, segmentation_training
- Mantiene compatibilidad hacia atrás con la API original
"""
# Re-export all functions and classes for backward compatibility
from .transforms.image_transforms import (
    resize_crop_to_square,
    resize_with_padding,
    normalize_image,
    denormalize_image,
    validate_crop_quality,
    create_transparent_crop
)

from .transforms.mask_refinement import (
    refine_mask_opencv_precise as _refine_mask_opencv_precise
)

from .transforms.segmentation_models import (
    DoubleConv,
    UNet
)

from .transforms.segmentation_training import (
    train_background_ai,
    remove_background_ai,
    CacaoDataset
)

# Export for backward compatibility
__all__ = [
    'resize_crop_to_square',
    'resize_with_padding',
    'normalize_image',
    'denormalize_image',
    'validate_crop_quality',
    'create_transparent_crop',
    '_refine_mask_opencv_precise',
    'DoubleConv',
    'UNet',
    'train_background_ai',
    'remove_background_ai',
    'CacaoDataset'
]
