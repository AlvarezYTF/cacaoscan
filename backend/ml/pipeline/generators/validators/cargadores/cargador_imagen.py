"""
Cargador de imágenes para validación de recortes.

Responsabilidad única: cargar imágenes desde archivos,
siguiendo el principio de Single Responsibility (SOLID).
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.validators.cargadores")


class CargadorImagen:
    """
    Cargador de imágenes para validación.
    
    Maneja la carga de imágenes desde archivos usando OpenCV.
    """
    
    @staticmethod
    def cargar_imagen_rgb(crop_path: Path) -> Optional[np.ndarray]:
        """
        Carga una imagen en formato RGB desde un archivo.
        
        Args:
            crop_path: Ruta al archivo de imagen
            
        Returns:
            Array de imagen RGB o None si hay error
        """
        try:
            if not crop_path.exists():
                logger.warning(f"Archivo de recorte no encontrado: {crop_path}")
                return None
            
            crop_img = cv2.imread(str(crop_path))
            if crop_img is None:
                logger.warning(f"No se pudo cargar imagen: {crop_path}")
                return None
            
            # Convertir BGR a RGB
            crop_img_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
            return crop_img_rgb
            
        except Exception as e:
            logger.error(f"Error cargando imagen {crop_path}: {e}")
            return None


