"""
Módulo principal de Machine Learning para CacaoScan.

REFACTORIZADO: Aplicando principios SOLID
- Proporciona acceso centralizado a las APIs principales de los sub-módulos.
- Facilita imports desde la raíz del módulo ml.
- Mantiene compatibilidad con imports directos desde sub-módulos.
"""

# Utils - Funciones más comunes
from .utils.logs import get_ml_logger
from .utils.paths import (
    get_regressors_artifacts_dir,
    get_artifacts_dir,
    get_datasets_dir,
    get_cacao_images_dir,
    get_crops_dir,
    ensure_dir_exists
)
from .utils.io import save_json, load_json, save_pickle, load_pickle

# Regression - APIs principales
from .regression.models import (
    create_model,
    get_model_info,
    count_parameters,
    TARGETS,
    TARGET_NAMES
)
from .regression.scalers import (
    CacaoScalers,
    load_scalers,
    save_scalers,
    create_scalers_from_data
)
from .regression.train import (
    train_single_model,
    train_multi_head_model,
    get_device
)
from .regression.evaluate import (
    RegressionEvaluator,
    compute_regression_metrics
)
from .regression.metrics import (
    robust_r2_score,
    calculate_metrics_per_target,
    calculate_average_r2
)

# Prediction - APIs principales
from .prediction.predict import get_predictor, obtener_predictor
from .prediction.calibrated_predict import get_calibrated_predictor, obtener_predictor_calibrado

# Measurement - APIs principales
from .measurement import (
    GestorCalibracion,
    CalibrationManager,  # Alias para compatibilidad
    CalibrationMethod,
    CalibrationParams,
    CalibrationResult
)

# Losses y Early Stopping
from .utils.losses import UncertaintyWeightedLoss
from .utils.early_stopping import IntelligentEarlyStopping

__all__ = [
    # Utils
    'get_ml_logger',
    'get_regressors_artifacts_dir',
    'get_artifacts_dir',
    'get_datasets_dir',
    'get_cacao_images_dir',
    'get_crops_dir',
    'ensure_dir_exists',
    'save_json',
    'load_json',
    'save_pickle',
    'load_pickle',
    # Regression
    'create_model',
    'get_model_info',
    'count_parameters',
    'TARGETS',
    'TARGET_NAMES',
    'CacaoScalers',
    'load_scalers',
    'save_scalers',
    'create_scalers_from_data',
    'train_single_model',
    'train_multi_head_model',
    'get_device',
    'RegressionEvaluator',
    'compute_regression_metrics',
    'robust_r2_score',
    'calculate_metrics_per_target',
    'calculate_average_r2',
    # Prediction
    'get_predictor',
    'obtener_predictor',
    'get_calibrated_predictor',
    'obtener_predictor_calibrado',
    # Measurement
    'GestorCalibracion',
    'CalibrationManager',
    'CalibrationMethod',
    'CalibrationParams',
    'CalibrationResult',
    # Losses y Early Stopping
    'UncertaintyWeightedLoss',
    'IntelligentEarlyStopping'
]

