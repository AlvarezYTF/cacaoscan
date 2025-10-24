"""
Utilidades para manejo de rutas del proyecto.
"""
import os
from pathlib import Path
from django.conf import settings


def get_project_root():
    """Obtiene la ruta raíz del proyecto."""
    return Path(settings.BASE_DIR)


def get_media_root():
    """Obtiene la ruta del directorio media."""
    return Path(settings.MEDIA_ROOT)


def get_datasets_dir():
    """Obtiene la ruta del directorio de datasets."""
    return get_media_root() / "datasets"


def get_cacao_images_dir():
    """Obtiene la ruta del directorio de imágenes de cacao."""
    return get_media_root() / "cacao_images"


def get_raw_images_dir():
    """Obtiene la ruta del directorio de imágenes raw."""
    return get_cacao_images_dir() / "raw"


def get_crops_dir():
    """Obtiene la ruta del directorio de crops."""
    return get_cacao_images_dir() / "crops"


def get_masks_dir():
    """Obtiene la ruta del directorio de máscaras."""
    return get_cacao_images_dir() / "masks"


def get_artifacts_dir():
    """Obtiene la ruta del directorio de artefactos ML."""
    return get_project_root() / "ml" / "artifacts"


def get_yolo_artifacts_dir():
    """Obtiene la ruta del directorio de artefactos YOLO."""
    return get_artifacts_dir() / "yolov8-seg"


def get_regressors_artifacts_dir():
    """Obtiene la ruta del directorio de artefactos de regresores."""
    return get_artifacts_dir() / "regressors"


def ensure_dir_exists(path: Path):
    """Asegura que un directorio existe."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_dataset_csv_path():
    """Obtiene la ruta del archivo CSV del dataset."""
    return get_datasets_dir() / "dataset.csv"


def get_missing_ids_log_path():
    """Obtiene la ruta del archivo de log de IDs faltantes."""
    return get_datasets_dir() / "missing_ids.log"


def get_raw_image_path(image_id: int):
    """Obtiene la ruta de una imagen raw por ID."""
    return get_raw_images_dir() / f"{image_id}.bmp"


def get_crop_image_path(image_id: int):
    """Obtiene la ruta de una imagen crop por ID."""
    return get_crops_dir() / f"{image_id}.png"


def get_mask_image_path(image_id: int):
    """Obtiene la ruta de una máscara por ID."""
    return get_masks_dir() / f"{image_id}.png"
