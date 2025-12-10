"""
Cargador y validador del dataset de cacao para CacaoScan.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: CSVLoader, ImageValidator, CacaoDatasetLoader
- Mantiene compatibilidad hacia atrás con la API original
"""
from .loaders.dataset_loader import (
    CacaoDatasetLoader as _CacaoDatasetLoader,
    load_cacao_dataset,
    get_valid_cacao_records,
    get_target_data
)

# Re-export for backward compatibility
CacaoDatasetLoader = _CacaoDatasetLoader

__all__ = [
    'CacaoDatasetLoader',
    'load_cacao_dataset',
    'get_valid_cacao_records',
    'get_target_data'
]
