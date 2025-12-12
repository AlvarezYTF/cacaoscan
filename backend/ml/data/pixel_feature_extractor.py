"""
Extractor de features de píxeles con area_mm2 y perimeter_mm.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: FeatureCalculator, ScalerManager, RecordProcessor
- Mantiene compatibilidad hacia atrás con la API original
"""
from .extractores import ExtractorFeaturesPixel

# Re-export para compatibilidad hacia atrás
PixelFeatureExtractor = ExtractorFeaturesPixel

__all__ = ['PixelFeatureExtractor']
