"""
Utilidades de refinamiento de máscaras.

Este módulo proporciona clases para refinar máscaras,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .mask_refiner import MaskRefiner

# Función de conveniencia para compatibilidad hacia atrás
def refine_mask_opencv_precise(rgb, mask):
    """
    Refina máscara usando OpenCV para detección precisa de píxeles.
    
    Args:
        rgb: Imagen RGB original
        mask: Máscara inicial
        
    Returns:
        Máscara refinada
    """
    refiner = MaskRefiner()
    return refiner.refine(rgb, mask)

__all__ = ['MaskRefiner', 'refine_mask_opencv_precise']

