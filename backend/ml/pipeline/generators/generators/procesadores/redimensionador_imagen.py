"""
Redimensionador de imágenes para generación de recortes.

Responsabilidad única: redimensionar imágenes,
siguiendo el principio de Single Responsibility (SOLID).
"""
from typing import Tuple
from PIL import Image

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.generators.procesadores")


class RedimensionadorImagen:
    """
    Redimensionador de imágenes para generación de recortes.
    
    Maneja el redimensionamiento de imágenes a tamaños específicos.
    """
    
    @staticmethod
    def redimensionar(
        imagen: Image.Image,
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Redimensiona una imagen a un tamaño objetivo.
        
        Args:
            imagen: Imagen PIL a redimensionar
            target_size: Tamaño objetivo (ancho, alto)
            
        Returns:
            Imagen redimensionada
        """
        return imagen.resize(target_size, Image.Resampling.LANCZOS)

