"""
Módulo de pipeline de entrenamiento para modelos de regresión de granos de cacao.

Este módulo proporciona pipelines y utilidades de entrenamiento,
siguiendo principios SOLID con separación de responsabilidades.
"""

from .train_all import (
    PipelineEntrenamientoCacao,
    ejecutar_pipeline_entrenamiento,
    run_incremental_training_pipeline,
    get_incremental_training_status,
    CacaoDataset,
    SingleDimensionDataset,
    # Constantes
    PIXEL_FEATURE_KEYS,
    CALIB_PIXEL_FEATURE_KEYS,
    SINGLE_DIM_TARGETS,
    MODEL_HYBRID,
    MODEL_MULTIHEAD
)
from .hybrid_training import entrenar_modelo_hibrido
from .hybrid_v2_training import entrenar_modelo_hibrido_v2

# Compatibilidad hacia atrás
from .train_all import (
    CacaoTrainingPipeline,
    run_training_pipeline
)
from .hybrid_training import train_hybrid_model
from .hybrid_v2_training import train_hybrid_v2

__all__ = [
    # Nombres en español
    'PipelineEntrenamientoCacao',
    'ejecutar_pipeline_entrenamiento',
    'run_incremental_training_pipeline',
    'get_incremental_training_status',
    'CacaoDataset',
    'SingleDimensionDataset',
    'entrenar_modelo_hibrido',
    'entrenar_modelo_hibrido_v2',
    # Constantes
    'PIXEL_FEATURE_KEYS',
    'CALIB_PIXEL_FEATURE_KEYS',
    'SINGLE_DIM_TARGETS',
    'MODEL_HYBRID',
    'MODEL_MULTIHEAD',
    # Compatibilidad hacia atrás
    'CacaoTrainingPipeline',
    'run_training_pipeline',
    'train_hybrid_model',
    'train_hybrid_v2'
]

