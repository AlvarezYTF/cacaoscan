"""
Módulo de datos para CacaoScan.

Este módulo proporciona datasets, loaders y extractores,
siguiendo principios SOLID para separación de responsabilidades.
"""

# Re-exportar clases principales para compatibilidad hacia atrás
from .cacao_dataset import CacaoDataset
from .hybrid_dataset import HybridCacaoDataset
from .improved_dataloader import ImprovedCacaoDataset, normalize_targets, denormalize_predictions, create_improved_dataloader
from .pixel_feature_extractor import PixelFeatureExtractor
from .pixel_features_loader import PixelFeaturesLoader

__all__ = [
    'CacaoDataset',
    'HybridCacaoDataset',
    'ImprovedCacaoDataset',
    'normalize_targets',
    'denormalize_predictions',
    'create_improved_dataloader',
    'PixelFeatureExtractor',
    'PixelFeaturesLoader'
]

