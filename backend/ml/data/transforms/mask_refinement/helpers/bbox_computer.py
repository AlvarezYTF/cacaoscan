"""
Computador de bounding boxes.

Este módulo maneja el cálculo de bounding boxes con padding,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np
from typing import Tuple

from .....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.mask_refinement.helpers")


class BBoxComputer:
    """
    Computador de bounding boxes.
    
    Esta clase es responsable de:
    - Calcular bounding boxes con padding
    - Validar y ajustar bounding boxes
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    @staticmethod
    def compute_padded(
        contour: np.ndarray,
        padding: int,
        image_shape: Tuple[int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Calcula el bounding box con padding para el contorno principal.
        
        Args:
            contour: Contorno
            padding: Padding a aplicar
            image_shape: Forma de la imagen (height, width, channels)
            
        Returns:
            Tupla (x, y, w, h) del bounding box
        """
        x, y, w, h = cv2.boundingRect(contour)
        height, width = image_shape[:2]
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(width - x, w + 2 * padding)
        h = min(height - y, h + 2 * padding)
        return x, y, w, h
    
    @staticmethod
    def validate_and_adjust_simple(
        bbox: Tuple[int, int, int, int],
        image_shape: Tuple[int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Validación y ajuste simple de bounding box.
        
        Args:
            bbox: Bounding box (x, y, w, h)
            image_shape: Forma de la imagen (height, width, channels)
            
        Returns:
            Bounding box ajustado (x, y, w, h)
        """
        x, y, w, h = bbox
        height, width = image_shape[:2]
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        w = min(w, width - x)
        h = min(h, height - y)
        return x, y, w, h
    
    @staticmethod
    def validate_and_adjust(
        image_rgb: np.ndarray,
        final_mask: np.ndarray,
        bbox: Tuple[int, int, int, int],
        padding: int
    ) -> Tuple[int, int, int, int]:
        """
        Valida ratios de crop y ajusta el bounding box si es necesario.
        
        Args:
            image_rgb: Array de imagen RGB
            final_mask: Máscara final
            bbox: Bounding box (x, y, w, h)
            padding: Padding a aplicar
            
        Returns:
            Bounding box ajustado (x, y, w, h)
            
        Raises:
            ValueError: Si el objeto detectado ocupa más del 80% de la imagen
        """
        _, _, w, h = bbox
        original_area = image_rgb.shape[0] * image_rgb.shape[1]
        crop_area = w * h
        if crop_area <= 0:
            return bbox
        
        crop_ratio = crop_area / original_area
        if crop_ratio <= 0.80:
            return bbox
        
        object_area = np.sum(final_mask > 128)
        object_ratio = object_area / original_area
        if object_ratio > 0.80:
            raise ValueError(
                f"Objeto detectado ocupa más del 80% de la imagen ({object_ratio:.1%}). "
                f"Esto sugiere que el grano no fue detectado correctamente o la segmentación falló. "
                f"Área del objeto: {object_area}px, Área de la imagen: {original_area}px"
            )
        
        coords = np.nonzero(final_mask > 128)
        if coords[0].size == 0:
            return bbox
        
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        width = image_rgb.shape[1]
        height = image_rgb.shape[0]
        x_new = max(0, x_min - padding)
        y_new = max(0, y_min - padding)
        w_new = min(width - x_new, (x_max - x_min) + 2 * padding)
        h_new = min(height - y_new, (y_max - y_min) + 2 * padding)
        return x_new, y_new, w_new, h_new

