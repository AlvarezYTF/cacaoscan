"""
Utilidades de transformación de imágenes.

Este módulo proporciona clases y funciones para transformaciones de imágenes,
siguiendo principios SOLID para separación de responsabilidades.
"""

# Re-exportar funciones principales para compatibilidad hacia atrás
from .image_transforms import (
    resize_crop_to_square,
    resize_with_padding,
    normalize_image,
    denormalize_image,
    validate_crop_quality,
    create_transparent_crop
)

from .mask_refinement import (
    refine_mask_opencv_precise
)

from .segmentation_models import (
    DoubleConv,
    UNet
)

from .segmentation_training import (
    train_background_ai,
    remove_background_ai,
    CacaoDataset
)

__all__ = [
    'resize_crop_to_square',
    'resize_with_padding',
    'normalize_image',
    'denormalize_image',
    'validate_crop_quality',
    'create_transparent_crop',
    'refine_mask_opencv_precise',
    'DoubleConv',
    'UNet',
    'train_background_ai',
    'remove_background_ai',
    'CacaoDataset'
]

