"""
Validador de dimensiones para recortes.

Responsabilidad única: validar dimensiones de imágenes,
siguiendo el principio de Single Responsibility (SOLID).
"""
import numpy as np
from typing import Tuple

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.validators.validadores")


class ValidadorDimensiones:
    """
    Validador de dimensiones para recortes.
    
    Valida que las dimensiones de una imagen cumplan con los requisitos mínimos.
    """
    
    def __init__(self, min_crop_size: int = 100):
        """
        Inicializa el validador de dimensiones.
        
        Args:
            min_crop_size: Tamaño mínimo del recorte en píxeles
        """
        self.min_crop_size = min_crop_size
    
    def validar(self, imagen_rgb: np.ndarray, crop_path: str) -> bool:
        """
        Valida las dimensiones de una imagen.
        
        Args:
            imagen_rgb: Array de imagen RGB
            crop_path: Nombre del archivo para logging
            
        Returns:
            True si las dimensiones son válidas, False en caso contrario
        """
        if imagen_rgb is None:
            return False
        
        h, w = imagen_rgb.shape[:2]
        
        if h < self.min_crop_size or w < self.min_crop_size:
            logger.warning(
                f"Recorte muy pequeño ({w}x{h}) para {crop_path}"
            )
            return False
        
        return True
    
    def obtener_dimensiones(self, imagen_rgb: np.ndarray) -> Tuple[int, int]:
        """
        Obtiene las dimensiones de una imagen.
        
        Args:
            imagen_rgb: Array de imagen RGB
            
        Returns:
            Tupla de (alto, ancho)
        """
        if imagen_rgb is None:
            return (0, 0)
        
        return imagen_rgb.shape[:2]


