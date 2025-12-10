"""
Cargador de features de calibración de píxeles desde pixel_calibration.json.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: FeatureCalculator, FeatureStorage, FeatureLoader
- Mantiene compatibilidad hacia atrás con la API original
"""
from .cargadores import CargadorFeaturesPixel

# Re-export para compatibilidad hacia atrás
PixelFeaturesLoader = CargadorFeaturesPixel

__all__ = ['PixelFeaturesLoader']
