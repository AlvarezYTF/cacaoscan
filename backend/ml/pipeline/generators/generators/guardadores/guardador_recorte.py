"""
Guardador de recortes para generación de recortes.

Responsabilidad única: guardar imágenes recortadas,
siguiendo el principio de Single Responsibility (SOLID).
"""
from pathlib import Path
from PIL import Image

from ml.utils.logs import get_ml_logger
from ml.utils.paths import ensure_dir_exists

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.generators.guardadores")


class GuardadorRecorte:
    """
    Guardador de recortes.
    
    Maneja el guardado de imágenes recortadas en el sistema de archivos.
    """
    
    @staticmethod
    def guardar(
        imagen: Image.Image,
        crop_path: Path,
        formato: str = "PNG"
    ) -> bool:
        """
        Guarda una imagen recortada en el sistema de archivos.
        
        Args:
            imagen: Imagen PIL a guardar
            crop_path: Ruta donde guardar el recorte
            formato: Formato de imagen (PNG, JPEG, etc.)
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            ensure_dir_exists(crop_path.parent)
            imagen.save(crop_path, formato)
            logger.debug(f"Recorte guardado: {crop_path}")
            return True
        except Exception as e:
            logger.error(f"Error guardando recorte {crop_path}: {e}")
            return False

