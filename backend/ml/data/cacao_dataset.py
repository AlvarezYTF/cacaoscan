"""
Dataset unificado para regresión de cacao con features de píxeles.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: CalibrationLoader, PixelFeatureBuilder, DatasetBuilder
- Mantiene compatibilidad hacia atrás con la API original
"""
from .conjuntos_datos import DatasetCacao

# Re-export para compatibilidad hacia atrás
CacaoDataset = DatasetCacao

__all__ = ['CacaoDataset']
