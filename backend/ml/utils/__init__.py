"""
Módulo de utilidades para ML.

REFACTORIZADO: Aplicando principios SOLID
- Proporciona utilidades para logging, I/O, paths, scalers, losses y early stopping.
- Mantiene compatibilidad hacia atrás con la API original.
"""

from .logs import (
    setup_logger,
    get_ml_logger,
    log_processing_stats
)
from .io import (
    save_json,
    load_json,
    save_pickle,
    load_pickle,
    save_csv,
    load_csv,
    save_image,
    load_image,
    write_log,
    get_file_timestamp,
    file_exists_and_newer,
    ensure_dir_exists
)
from .paths import (
    get_project_root,
    get_media_root,
    get_datasets_dir,
    get_cacao_images_dir,
    get_raw_images_dir,
    get_crops_dir,
    get_masks_dir,
    get_processed_images_dir,
    get_converted_jpg_dir,
    get_artifacts_dir,
    get_yolo_artifacts_dir,
    get_regressors_artifacts_dir,
    get_dataset_csv_path,
    get_missing_ids_log_path,
    get_raw_image_path,
    get_crop_image_path,
    get_mask_image_path
)
from .scalers import (
    CacaoRobustScaler,
    load_scalers
)
from .losses import (
    UncertaintyWeightedLoss
)
from .early_stopping import (
    IntelligentEarlyStopping
)

__all__ = [
    # Logs
    'setup_logger',
    'get_ml_logger',
    'log_processing_stats',
    # I/O
    'save_json',
    'load_json',
    'save_pickle',
    'load_pickle',
    'save_csv',
    'load_csv',
    'save_image',
    'load_image',
    'write_log',
    'get_file_timestamp',
    'file_exists_and_newer',
    'ensure_dir_exists',
    # Paths
    'get_project_root',
    'get_media_root',
    'get_datasets_dir',
    'get_cacao_images_dir',
    'get_raw_images_dir',
    'get_crops_dir',
    'get_masks_dir',
    'get_processed_images_dir',
    'get_converted_jpg_dir',
    'get_artifacts_dir',
    'get_yolo_artifacts_dir',
    'get_regressors_artifacts_dir',
    'get_dataset_csv_path',
    'get_missing_ids_log_path',
    'get_raw_image_path',
    'get_crop_image_path',
    'get_mask_image_path',
    # Scalers
    'CacaoRobustScaler',
    'load_scalers',
    # Losses
    'UncertaintyWeightedLoss',
    # Early Stopping
    'IntelligentEarlyStopping'
]

