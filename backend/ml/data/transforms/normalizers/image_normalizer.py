"""
Normalizador de imágenes.

Este módulo maneja la normalización y desnormalización de imágenes,
siguiendo el principio de Responsabilidad Única.
"""
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.normalizers")


class ImageNormalizer:
    """
    Normalizador de imágenes.
    
    Esta clase es responsable de:
    - Normalizar imágenes al rango [0, 1]
    - Desnormalizar imágenes del rango [0, 1] a [0, 255]
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    ERROR_IMAGE_CANNOT_BE_NONE = "image cannot be None"
    
    @staticmethod
    def normalize(image: np.ndarray) -> np.ndarray:
        """
        Normaliza imagen al rango [0, 1].
        
        Args:
            image: Array de imagen
            
        Returns:
            Imagen normalizada
        """
        if image is None:
            raise ValueError(ImageNormalizer.ERROR_IMAGE_CANNOT_BE_NONE)
        img = image.astype(np.float32)
        if img.max() > 1.0:
            img = img / 255.0
        return img
    
    @staticmethod
    def denormalize(image: np.ndarray) -> np.ndarray:
        """
        Desnormaliza imagen del rango [0, 1] a [0, 255].
        
        Args:
            image: Array de imagen normalizada
            
        Returns:
            Imagen desnormalizada
        """
        if image is None:
            raise ValueError(ImageNormalizer.ERROR_IMAGE_CANNOT_BE_NONE)
        img = np.clip(image, 0.0, 1.0)
        return (img * 255.0).astype(np.uint8)

