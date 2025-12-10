"""
Validador de canal alpha para recortes RGBA.

Responsabilidad única: validar canal alpha de imágenes RGBA,
siguiendo el principio de Single Responsibility (SOLID).
"""
import numpy as np

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.validators.validadores")


class ValidadorCanalAlpha:
    """
    Validador de canal alpha para recortes RGBA.
    
    Valida que el ratio de píxeles visibles en imágenes RGBA
    cumpla con el requisito mínimo.
    """
    
    def __init__(self, min_visible_ratio: float = 0.1):
        """
        Inicializa el validador de canal alpha.
        
        Args:
            min_visible_ratio: Ratio mínimo de píxeles visibles
        """
        self.min_visible_ratio = min_visible_ratio
    
    def validar(self, imagen_rgb: np.ndarray, crop_path: str) -> bool:
        """
        Valida el canal alpha de una imagen RGBA.
        
        Args:
            imagen_rgb: Array de imagen RGB o RGBA
            crop_path: Nombre del archivo para logging
            
        Returns:
            True si el canal alpha es válido, False en caso contrario
        """
        if imagen_rgb is None:
            return False
        
        # Verificar si es imagen RGBA
        if imagen_rgb.shape[2] != 4:
            return True  # No es RGBA, no necesita validación de alpha
        
        alpha = imagen_rgb[:, :, 3]
        visible_pixels = np.sum(alpha > 128)
        total_pixels = imagen_rgb.shape[0] * imagen_rgb.shape[1]
        visible_ratio = visible_pixels / total_pixels if total_pixels > 0 else 0
        
        if visible_ratio < self.min_visible_ratio:
            logger.warning(
                f"Recorte con muy poco contenido visible ({visible_ratio:.2%}) "
                f"para {crop_path}"
            )
            return False
        
        return True


