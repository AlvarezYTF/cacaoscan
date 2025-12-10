"""
Resizer para imágenes cuadradas.

Este módulo maneja el redimensionamiento de imágenes RGBA manteniendo
la relación de aspecto y centrándolas en un canvas cuadrado,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np
from typing import Tuple

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.resizers")


class SquareResizer:
    """
    Resizer para imágenes RGBA en canvas cuadrados.
    
    Esta clase es responsable de:
    - Redimensionar imágenes RGBA manteniendo relación de aspecto
    - Centrar imágenes en canvas cuadrado
    - Aplicar color de relleno
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    ERROR_IMAGE_CANNOT_BE_NONE = "image cannot be None"
    
    @staticmethod
    def resize(
        image_rgba: np.ndarray,
        target_size: int = 512,
        fill_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
    ) -> np.ndarray:
        """
        Redimensiona una imagen RGBA manteniendo relación de aspecto y
        centrándola en un canvas cuadrado target_size x target_size con fill_color.
        
        Args:
            image_rgba: Array de imagen RGBA
            target_size: Tamaño del canvas cuadrado
            fill_color: Color de relleno (R, G, B, A)
            
        Returns:
            Imagen RGBA redimensionada y centrada
        """
        if image_rgba is None:
            raise ValueError(SquareResizer.ERROR_IMAGE_CANNOT_BE_NONE)
        
        h, w = image_rgba.shape[:2]
        scale = min(target_size / w, target_size / h)
        new_w = int(round(w * scale))
        new_h = int(round(h * scale))
        resized = cv2.resize(image_rgba, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        canvas = np.zeros((target_size, target_size, 4), dtype=np.uint8)
        canvas[:, :, 0] = fill_color[0]
        canvas[:, :, 1] = fill_color[1]
        canvas[:, :, 2] = fill_color[2]
        canvas[:, :, 3] = fill_color[3]
        
        y_off = (target_size - new_h) // 2
        x_off = (target_size - new_w) // 2
        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
        return canvas

