"""
Utilidades de transformación de imágenes.

Este módulo orquesta el redimensionamiento, normalización y validación de calidad,
siguiendo los principios de Responsabilidad Única e Inversión de Dependencias.
"""
import numpy as np
from typing import Tuple, Optional

from ...utils.logs import get_ml_logger
from .resizers import SquareResizer, PaddedResizer
from .normalizers import ImageNormalizer
from .validators import CropValidator
from .mask_refinement import MaskRefiner
from .mask_refinement.helpers import (
    MaskAligner, BBoxComputer, MaskRenderer, RGBABuilder
)

logger = get_ml_logger("cacaoscan.ml.data.transforms.image")


# Funciones de conveniencia para compatibilidad hacia atrás
def resize_crop_to_square(
    image_rgba: np.ndarray,
    target_size: int = 512,
    fill_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
) -> np.ndarray:
    """
    Redimensiona una imagen RGBA manteniendo relación de aspecto y la centra
    en un canvas cuadrado target_size x target_size con fill_color.
    
    Args:
        image_rgba: Array de imagen RGBA
        target_size: Tamaño del canvas cuadrado
        fill_color: Color de relleno (R, G, B, A)
        
    Returns:
        Imagen RGBA redimensionada y centrada
    """
    return SquareResizer.resize(image_rgba, target_size, fill_color)


def resize_with_padding(
    image: np.ndarray,
    target_size: Tuple[int, int] = (640, 640),
    fill_color: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """
    Redimensiona manteniendo relación de aspecto y aplica padding
    al tamaño objetivo (height, width).
    Acepta imágenes GRAY/RGB/RGBA.
    
    Args:
        image: Array de imagen
        target_size: Tamaño objetivo (height, width)
        fill_color: Color de relleno (R, G, B)
        
    Returns:
        Imagen redimensionada y con padding
    """
    return PaddedResizer.resize(image, target_size, fill_color)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normaliza imagen al rango [0, 1].
    
    Args:
        image: Array de imagen
        
    Returns:
        Imagen normalizada
    """
    return ImageNormalizer.normalize(image)


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """
    Desnormaliza imagen del rango [0, 1] a [0, 255].
    
    Args:
        image: Array de imagen normalizada
        
    Returns:
        Imagen desnormalizada
    """
    return ImageNormalizer.denormalize(image)


def validate_crop_quality(
    image_rgb: np.ndarray,
    mask: np.ndarray,
    min_aspect_ratio: float = 0.1,
    max_aspect_ratio: float = 10.0,
    min_area: int = 100
) -> bool:
    """
    Valida calidad del crop basado en relación de aspecto y área.
    
    Args:
        image_rgb: Array de imagen RGB
        mask: Array de máscara binaria
        min_aspect_ratio: Relación de aspecto mínima
        max_aspect_ratio: Relación de aspecto máxima
        min_area: Área mínima en píxeles
        
    Returns:
        True si la calidad del crop es válida, False en caso contrario
    """
    return CropValidator.validate(
        image_rgb, mask, min_aspect_ratio, max_aspect_ratio, min_area
    )


def create_transparent_crop(
    image_rgb: np.ndarray,
    mask: np.ndarray,
    padding: int = 10,
    crop_only: bool = False
) -> np.ndarray:
    """
    Crea crop transparente desde imagen RGB y máscara.
    
    Args:
        image_rgb: Array de imagen RGB
        mask: Array de máscara binaria
        padding: Padding alrededor del crop
        crop_only: Si es True, solo recorta sin transparencia
        
    Returns:
        Array de imagen RGBA
    """
    if image_rgb is None or mask is None:
        raise ValueError("image_rgb y mask no pueden ser None")
    
    import cv2
    
    # Alinear máscara con imagen
    mask_aligned = MaskAligner.align(mask, image_rgb)
    
    # Refinar máscara
    mask_refiner = MaskRefiner()
    mask_refined = mask_refiner.refine(image_rgb, mask_aligned)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(
        mask_refined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return RGBABuilder.stack(image_rgb, mask_refined)
    
    # Obtener contorno más grande
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = BBoxComputer.compute_padded(
        largest_contour, padding, image_rgb.shape
    )
    final_mask = MaskRenderer.render_primary(mask_refined, largest_contour)
    
    if not crop_only:
        return RGBABuilder.create_refined(image_rgb, final_mask, x, y, w, h)
    
    # Ajustar bbox
    adjusted_bbox = BBoxComputer.validate_and_adjust(
        image_rgb=image_rgb,
        final_mask=final_mask,
        bbox=(x, y, w, h),
        padding=padding
    )
    x_adj, y_adj, w_adj, h_adj = adjusted_bbox
    return RGBABuilder.create_from_crop(
        image_rgb, final_mask, x_adj, y_adj, w_adj, h_adj
    )
