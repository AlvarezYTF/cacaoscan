"""
Validador de calidad de crops.

Este módulo maneja la validación de calidad de crops basada en
relación de aspecto y área,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.validators")


class CropValidator:
    """
    Validador de calidad de crops.
    
    Esta clase es responsable de:
    - Validar relación de aspecto
    - Validar área mínima
    - Validar dimensiones mínimas
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    @staticmethod
    def validate(
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
        if image_rgb is None or mask is None:
            return False
        
        # Convertir máscara a binaria si es necesario
        if mask.dtype != np.uint8 or mask.max() > 1:
            mask_binary = (mask > 128).astype(np.uint8)
        else:
            mask_binary = mask
        
        # Encontrar bounding box del objeto
        contours, _ = cv2.findContours(
            mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return False
        
        # Usar contorno más grande
        largest_contour = max(contours, key=cv2.contourArea)
        _, _, w, h = cv2.boundingRect(largest_contour)
        
        # Validar área mínima
        area = w * h
        if area < min_area:
            return False
        
        # Validar dimensiones mínimas
        if w < 5 or h < 5:
            return False
        
        # Calcular relación de aspecto
        aspect_ratio = w / h if h > 0 else 0
        
        # Validar relación de aspecto
        if aspect_ratio < min_aspect_ratio or aspect_ratio > max_aspect_ratio:
            return False
        
        return True

