from __future__ import annotations

"""Utilidades para manejo de rutas del proyecto."""

import logging
import os
from pathlib import Path
from typing import Callable

from django.conf import settings


logger = logging.getLogger("cacaoscan.ml.paths")


def _resolve_path(
    env_var: str,
    default_factory: Callable[[], Path],
    *,
    require_exists: bool = False,
) -> Path:
    """Resuelve una ruta a partir de una variable de entorno o usa un valor por defecto."""

    env_value = os.environ.get(env_var)
    if env_value:
        candidate = Path(env_value).expanduser().resolve(strict=False)
        if candidate.exists() or not require_exists:
            logger.debug("Usando ruta personalizada para %s: %s", env_var, candidate)
            return candidate

        logger.warning(
            "Ruta configurada en %s no existe: %s. Se utilizará el valor por defecto.",
            env_var,
            candidate,
        )

    return default_factory()


def get_project_root() -> Path:
    """Obtiene la ruta raíz del proyecto."""

    return Path(settings.BASE_DIR)


def get_media_root() -> Path:
    """Obtiene la ruta del directorio media."""

    return _resolve_path("CACAO_MEDIA_ROOT", lambda: Path(settings.MEDIA_ROOT))


def get_datasets_dir() -> Path:
    """Obtiene la ruta del directorio de datasets."""

    return _resolve_path("CACAO_DATASETS_DIR", lambda: get_media_root() / "datasets")


def get_cacao_images_dir() -> Path:
    """Obtiene la ruta del directorio de imágenes de cacao."""

    return _resolve_path(
        "CACAO_IMAGES_DIR", lambda: get_media_root() / "cacao_images"
    )


def get_raw_images_dir() -> Path:
    """Obtiene la ruta del directorio de imágenes raw."""

    return _resolve_path("CACAO_RAW_IMAGES_DIR", lambda: get_cacao_images_dir() / "raw")


def get_crops_dir() -> Path:
    """Obtiene la ruta del directorio de crops."""

    return _resolve_path("CACAO_CROPS_DIR", lambda: get_cacao_images_dir() / "crops")


def get_masks_dir() -> Path:
    """Obtiene la ruta del directorio de máscaras."""

    return _resolve_path("CACAO_MASKS_DIR", lambda: get_cacao_images_dir() / "masks")


def get_processed_images_dir() -> Path:
    """Directorio para imágenes procesadas (PNG con transparencia)."""

    return _resolve_path(
        "CACAO_PROCESSED_IMAGES_DIR",
        lambda: get_cacao_images_dir() / "processed",
    )


def get_converted_jpg_dir() -> Path:
    """Directorio para JPG convertidos desde BMP (útil como paso intermedio)."""

    return _resolve_path(
        "CACAO_CONVERTED_JPG_DIR",
        lambda: get_cacao_images_dir() / "converted_jpg",
    )


def get_artifacts_dir() -> Path:
    """Obtiene la ruta del directorio de artefactos ML."""

    return get_project_root() / "ml" / "artifacts"


def get_yolo_artifacts_dir() -> Path:
    """Obtiene la ruta del directorio de artefactos YOLO."""

    return get_artifacts_dir() / "yolov8-seg"


def get_regressors_artifacts_dir() -> Path:
    """Obtiene la ruta del directorio de artefactos de regresores."""

    return get_artifacts_dir() / "regressors"


def ensure_dir_exists(path: Path) -> Path:
    """Asegura que un directorio existe."""

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_dataset_csv_path() -> Path:
    """Obtiene la ruta del archivo CSV del dataset."""

    dataset_env = os.environ.get("CACAO_DATASET_CSV")
    if dataset_env:
        dataset_path = Path(dataset_env).expanduser().resolve(strict=False)
        logger.debug("Usando archivo CSV personalizado: %s", dataset_path)
        return dataset_path

    return get_datasets_dir() / "dataset.csv"


def get_missing_ids_log_path() -> Path:
    """Obtiene la ruta del archivo de log de IDs faltantes."""

    return get_datasets_dir() / "missing_ids.log"


def get_raw_image_path(image_id: int) -> Path:
    """Obtiene la ruta de una imagen raw por ID."""

    return get_raw_images_dir() / f"{image_id}.bmp"


def get_crop_image_path(image_id: int) -> Path:
    """Obtiene la ruta de una imagen crop por ID."""

    return get_crops_dir() / f"{image_id}.png"


def get_mask_image_path(image_id: int) -> Path:
    """Obtiene la ruta de una máscara por ID."""

    return get_masks_dir() / f"{image_id}.png"


