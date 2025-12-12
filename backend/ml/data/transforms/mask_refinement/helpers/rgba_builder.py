"""
Constructor de imágenes RGBA.

Este módulo maneja la construcción de imágenes RGBA desde RGB y máscaras,
siguiendo el principio de Responsabilidad Única.
"""
import numpy as np

from .....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.mask_refinement.helpers")


class RGBABuilder:
    """
    Constructor de imágenes RGBA.
    
    Esta clase es responsable de:
    - Crear imágenes RGBA desde RGB y máscaras
    - Apilar canales RGB con canal alpha
    - Crear crops RGBA refinados
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    @staticmethod
    def stack(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
        """
        Apila datos RGB con un canal alpha.
        
        Args:
            rgb: Array RGB
            alpha: Array de canal alpha
            
        Returns:
            Array RGBA
        """
        rgba = np.zeros((rgb.shape[0], rgb.shape[1], 4), dtype=np.uint8)
        rgba[:, :, :3] = rgb
        rgba[:, :, 3] = alpha
        return rgba
    
    @staticmethod
    def create_refined(
        image_rgb: np.ndarray,
        final_mask: np.ndarray,
        x: int,
        y: int,
        w: int,
        h: int
    ) -> np.ndarray:
        """
        Genera crop RGBA con refinamiento adicional.
        
        Args:
            image_rgb: Array de imagen RGB
            final_mask: Máscara final
            x: Coordenada x del crop
            y: Coordenada y del crop
            w: Ancho del crop
            h: Alto del crop
            
        Returns:
            Array RGBA refinado
        """
        region_rgb = image_rgb[y:y+h, x:x+w].copy()
        region_mask = final_mask[y:y+h, x:x+w].copy()
        # Importar aquí para evitar dependencia circular
        from ..mask_refiner import MaskRefiner
        mask_refiner = MaskRefiner()
        region_mask_refined = mask_refiner.refine(region_rgb, region_mask)
        return RGBABuilder.stack(region_rgb, region_mask_refined)
    
    @staticmethod
    def create_from_crop(
        image_rgb: np.ndarray,
        final_mask: np.ndarray,
        x: int,
        y: int,
        w: int,
        h: int
    ) -> np.ndarray:
        """
        Construye tensor RGBA desde el crop ajustado.
        
        Args:
            image_rgb: Array de imagen RGB
            final_mask: Máscara final
            x: Coordenada x del crop
            y: Coordenada y del crop
            w: Ancho del crop
            h: Alto del crop
            
        Returns:
            Array RGBA del crop
        """
        crop_rgb = image_rgb[y:y+h, x:x+w].copy()
        crop_alpha = final_mask[y:y+h, x:x+w].copy()
        return RGBABuilder.stack(crop_rgb, crop_alpha)

