"""
Resizer con padding para imágenes.

Este módulo maneja el redimensionamiento de imágenes manteniendo
la relación de aspecto y aplicando padding,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np
from typing import Tuple

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.resizers")


class PaddedResizer:
    """
    Resizer con padding para imágenes.
    
    Esta clase es responsable de:
    - Redimensionar imágenes manteniendo relación de aspecto
    - Aplicar padding al tamaño objetivo
    - Manejar diferentes formatos (GRAY/RGB/RGBA)
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    ERROR_IMAGE_CANNOT_BE_NONE = "image cannot be None"
    
    @staticmethod
    def resize(
        image: np.ndarray,
        target_size: Tuple[int, int] = (640, 640),
        fill_color: Tuple[int, int, int] = (0, 0, 0)
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
        if image is None:
            raise ValueError(PaddedResizer.ERROR_IMAGE_CANNOT_BE_NONE)
        
        h, w = image.shape[:2]
        th, tw = target_size
        scale = min(th / h, tw / w)
        new_h, new_w = int(round(h * scale)), int(round(w * scale))
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        if image.ndim == 2:
            canvas = np.full((th, tw), fill_color[0], dtype=resized.dtype)
            y0 = (th - new_h) // 2
            x0 = (tw - new_w) // 2
            canvas[y0:y0+new_h, x0:x0+new_w] = resized
            return canvas
        
        c = image.shape[2]
        if c == 3:
            canvas = np.zeros((th, tw, 3), dtype=resized.dtype)
            canvas[:, :, 0] = fill_color[0]
            canvas[:, :, 1] = fill_color[1]
            canvas[:, :, 2] = fill_color[2]
        else:
            # RGBA
            canvas = np.zeros((th, tw, 4), dtype=resized.dtype)
            canvas[:, :, 0] = fill_color[0]
            canvas[:, :, 1] = fill_color[1]
            canvas[:, :, 2] = fill_color[2]
            canvas[:, :, 3] = fill_color[3] if len(fill_color) == 4 else 0
        
        y0 = (th - new_h) // 2
        x0 = (tw - new_w) // 2
        canvas[y0:y0+new_h, x0:x0+new_w] = resized
        return canvas

