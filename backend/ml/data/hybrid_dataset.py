"""
Dataset híbrido para regresión de cacao con features de píxeles normalizados.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: validators, loaders, extractors
- Mantiene compatibilidad hacia atrás con la API original
"""
from .conjuntos_datos import DatasetHibrido

# Re-export para compatibilidad hacia atrás
HybridCacaoDataset = DatasetHibrido

__all__ = ['HybridCacaoDataset']
