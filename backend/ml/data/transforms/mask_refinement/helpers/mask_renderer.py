"""
Renderizador de máscaras.

Este módulo maneja el renderizado de máscaras desde contornos,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np

from .....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.mask_refinement.helpers")


class MaskRenderer:
    """
    Renderizador de máscaras.
    
    Esta clase es responsable de:
    - Renderizar máscaras desde contornos
    - Crear máscaras rellenas
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    @staticmethod
    def render_primary(mask_refined: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """
        Renderiza una máscara rellena para el contorno seleccionado.
        
        Args:
            mask_refined: Máscara refinada
            contour: Contorno a renderizar
            
        Returns:
            Máscara renderizada
        """
        final_mask = np.zeros(mask_refined.shape, dtype=np.uint8)
        cv2.drawContours(final_mask, [contour], -1, 255, thickness=-1)
        return final_mask

