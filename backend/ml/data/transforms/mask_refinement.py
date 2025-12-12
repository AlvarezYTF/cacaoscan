"""
Utilidades de refinamiento de máscaras.

Este módulo proporciona funciones de conveniencia para compatibilidad hacia atrás,
siguiendo principios SOLID para separación de responsabilidades.
"""
import numpy as np

from ...utils.logs import get_ml_logger
from .mask_refinement.mask_refiner import MaskRefiner

logger = get_ml_logger("cacaoscan.ml.data.transforms.mask")


# Función de conveniencia para compatibilidad hacia atrás
def refine_mask_opencv_precise(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Refina máscara usando OpenCV para detección precisa de píxeles.
    Remueve bordes blancos residuales y ajusta píxel por píxel.
    
    Args:
        rgb: Imagen RGB original (H, W, 3)
        mask: Máscara inicial del modelo (H, W) con valores 0-255
        
    Returns:
        Máscara refinada (H, W) con valores 0-255
    """
    mask_refiner = MaskRefiner()
    return mask_refiner.refine(rgb, mask)

