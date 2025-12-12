"""
Alineador de máscaras con imágenes.

Este módulo maneja la alineación de máscaras con imágenes,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np

from .....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.mask_refinement.helpers")


class MaskAligner:
    """
    Alineador de máscaras con imágenes.
    
    Esta clase es responsable de:
    - Redimensionar máscaras para alinearlas con imágenes
    - Normalizar valores de máscaras
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    @staticmethod
    def align(mask: np.ndarray, image_rgb: np.ndarray) -> np.ndarray:
        """
        Redimensiona y normaliza valores de máscara para alinearla con la forma de la imagen.
        
        Args:
            mask: Array de máscara
            image_rgb: Array de imagen RGB
            
        Returns:
            Máscara alineada
        """
        if mask.shape[:2] != image_rgb.shape[:2]:
            mask = cv2.resize(
                mask,
                (image_rgb.shape[1], image_rgb.shape[0]),
                interpolation=cv2.INTER_LINEAR
            )
        if mask.max() <= 1.0:
            return (mask * 255).astype(np.uint8)
        return np.clip(mask, 0, 255).astype(np.uint8)

