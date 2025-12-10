"""
Módulo de regresión para CacaoScan.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: modelos, entrenamiento, evaluación, métricas
- Mantiene compatibilidad hacia atrás con la API original.
"""

from .models import (
    ResNet18Regression,
    ConvNeXtTinyRegression,
    MultiHeadRegression,
    HybridCacaoRegression,
    create_model,
    get_model_info,
    count_parameters,
    TARGETS,
    TARGET_NAMES
)

from .scalers import (
    CacaoScalers,
    load_scalers,
    save_scalers,
    create_scalers_from_data,
    validate_scalers
)

from .metrics import (
    robust_r2_score,
    calculate_metrics_per_target,
    calculate_average_r2,
    denormalize_and_calculate_metrics,
    validate_predictions_targets_alignment,
    calculate_metrics,
    print_metrics_summary
)

from .base_trainer import BaseTrainer

from .train import (
    RegressionTrainer,
    train_single_model,
    train_multi_head_model,
    get_device,
    create_training_job,
    update_training_job_metrics
)

from .train_improved import train_multi_head_model_improved

from .hybrid_trainer import HybridTrainer

from .evaluate import (
    RegressionEvaluator,
    compute_regression_metrics,
    load_model_for_evaluation,
    evaluate_model_from_file
)

from .augmentation import (
    MixUp,
    CutMix,
    RandomErasing,
    create_advanced_train_transform,
    create_advanced_val_transform,
    AugmentedDataset
)

from .incremental_train import (
    IncrementalDataManager,
    IncrementalLearningStrategy,
    IncrementalModelManager,
    IncrementalTrainer,
    run_incremental_training
)

from .optimized_models import (
    OptimizedResNet18Regression,
    OptimizedHybridRegression,
    SimpleCacaoRegression,
    create_optimized_model,
    get_model_summary
)

__all__ = [
    # Models
    'ResNet18Regression',
    'ConvNeXtTinyRegression',
    'MultiHeadRegression',
    'HybridCacaoRegression',
    'create_model',
    'get_model_info',
    'count_parameters',
    'TARGETS',
    'TARGET_NAMES',
    # Scalers
    'CacaoScalers',
    'load_scalers',
    'save_scalers',
    'create_scalers_from_data',
    'validate_scalers',
    # Metrics
    'robust_r2_score',
    'calculate_metrics_per_target',
    'calculate_average_r2',
    'denormalize_and_calculate_metrics',
    'validate_predictions_targets_alignment',
    'calculate_metrics',
    'print_metrics_summary',
    # Trainers
    'BaseTrainer',
    'RegressionTrainer',
    'HybridTrainer',
    'train_single_model',
    'train_multi_head_model',
    'train_multi_head_model_improved',
    'get_device',
    'create_training_job',
    'update_training_job_metrics',
    # Evaluation
    'RegressionEvaluator',
    'compute_regression_metrics',
    'load_model_for_evaluation',
    'evaluate_model_from_file',
    # Augmentation
    'MixUp',
    'CutMix',
    'RandomErasing',
    'create_advanced_train_transform',
    'create_advanced_val_transform',
    'AugmentedDataset',
    # Incremental Learning
    'IncrementalDataManager',
    'IncrementalLearningStrategy',
    'IncrementalModelManager',
    'IncrementalTrainer',
    'run_incremental_training',
    # Optimized Models
    'OptimizedResNet18Regression',
    'OptimizedHybridRegression',
    'SimpleCacaoRegression',
    'create_optimized_model',
    'get_model_summary'
]

