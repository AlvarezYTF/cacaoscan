"""
Procesador de imágenes para generación de recortes.

Responsabilidad única: procesar imágenes para recortes,
siguiendo el principio de Single Responsibility (SOLID).
"""
from pathlib import Path
from typing import Optional
from PIL import Image

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.generators.procesadores")


class ProcesadorImagen:
    """
    Procesador de imágenes para generación de recortes.
    
    Maneja la carga y procesamiento básico de imágenes.
    """
    
    @staticmethod
    def cargar_imagen(image_path: Path) -> Optional[Image.Image]:
        """
        Carga una imagen desde un archivo.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Imagen PIL o None si hay error
        """
        try:
            if not image_path.exists():
                logger.warning(f"Imagen no encontrada: {image_path}")
                return None
            
            return Image.open(image_path)
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            return None

