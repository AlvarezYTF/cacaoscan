"""
Pipeline completo de entrenamiento para modelos de regresión de cacao.
"""
import argparse
import json
import logging
import os
import sys
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import time
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import QuantileTransformer, StandardScaler
from PIL import Image
import torchvision.transforms as transforms

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cacaoscan.settings")
import django

try:
    django.setup()
    from django.conf import settings

    DJANGO_LOADED = True
except Exception as e:
    print(
        f"Warning: Django setup failed (normal if not in Django context). Error: {e}"
    )

    class DummySettings:
        MEDIA_ROOT = str(project_root / "media")
        BASE_DIR = project_root

    settings = DummySettings()

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.regression.models import (
    create_model,
    TARGETS,
    TARGET_NAMES,
    HybridCacaoRegression,
)
from ml.regression.scalers import create_scalers_from_data, save_scalers
from ml.regression.train import train_single_model, train_multi_head_model, get_device
from ml.regression.evaluate import RegressionEvaluator
from ml.utils.paths import (
    get_regressors_artifacts_dir,
    get_artifacts_dir,
    get_datasets_dir,
)
from ml.utils.io import save_json, load_json, save_pickle
from ml.utils.logs import get_ml_logger
from ml.regression.augmentation import (
    create_advanced_train_transform,
    create_advanced_val_transform,
)
from ml.segmentation.cropper import create_cacao_cropper


logger = get_ml_logger("cacaoscan.ml.pipeline")

# Constantes de Features de Píxeles (pipeline existente)
PIXEL_FEATURE_KEYS = [
    "pixel_width",
    "pixel_height",
    "pixel_area",
    "scale_factor",
    "aspect_ratio",
]

# Targets para el nuevo modo single_dimension_training (valores reales en mm / g)
SINGLE_DIM_TARGETS = ["alto_mm", "ancho_mm", "grosor_mm", "peso_g"]

# Features extendidos obligatorios provenientes de pixel_calibration.json
CALIB_PIXEL_FEATURE_KEYS = [
    "grain_area_pixels",
    "width_pixels",
    "height_pixels",
    "bbox_area_pixels",
    "aspect_ratio",
    "original_total_pixels",
    "background_pixels",
    "background_ratio",
    "alto_mm_per_pixel",
    "ancho_mm_per_pixel",
    "average_mm_per_pixel",
    "segmentation_confidence",
]


class CacaoDataset(Dataset):
    """
    Dataset personalizado para entrenamiento de modelos de cacao.
    (Modo multi-head / individual clásico del pipeline existente)
    
    MEJORADO:
    - Validación de formato de imágenes (RGB, normalización ImageNet)
    - Verificación de mezclas entre .bmp y .png
    - Labels en orden correcto: [alto, ancho, grosor, peso]
    - Validación automática de estructura de datos
    """
    
    # Orden correcto de targets
    TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]

    def __init__(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        transform: Any,
        pixel_features: Optional[Dict[str, np.ndarray]] = None,
        is_multi_head: bool = False,
        is_hybrid: bool = False,
        validate_structure: bool = True,
    ):
        self.image_paths = image_paths
        self.targets = targets
        self.transform = transform
        self.pixel_features = pixel_features
        self.is_multi_head = is_multi_head
        self.is_hybrid = is_hybrid
        
        # Paso 2: Normalizar pixel_features antes de fusionar
        self.pixel_means = None
        self.pixel_stds = None
        if pixel_features is not None and is_hybrid:
            # Determinar qué features usar
            available_keys = list(pixel_features.keys())
            if all(k in available_keys for k in CALIB_PIXEL_FEATURE_KEYS):
                feature_keys = CALIB_PIXEL_FEATURE_KEYS
            else:
                feature_keys = PIXEL_FEATURE_KEYS
            
            # Crear DataFrame con los features
            pixel_df = pd.DataFrame({k: pixel_features[k] for k in feature_keys})
            self.pixel_means = pixel_df.mean().values
            self.pixel_stds = pixel_df.std().values
            # Evitar división por cero
            self.pixel_stds = np.where(self.pixel_stds < 1e-8, 1.0, self.pixel_stds)
            logger.debug(f"Pixel features normalizados: mean shape={self.pixel_means.shape}, std shape={self.pixel_stds.shape}")

        # Validar estructura si se solicita
        if validate_structure:
            self._validate_structure()

        lengths: List[int] = [len(image_paths)] + [len(v) for v in targets.values()]
        if pixel_features is not None and is_hybrid:
            # Verificar features disponibles (pueden ser básicos o extendidos)
            available_keys = list(pixel_features.keys())
            if all(k in available_keys for k in CALIB_PIXEL_FEATURE_KEYS):
                feature_keys = CALIB_PIXEL_FEATURE_KEYS
            else:
                feature_keys = PIXEL_FEATURE_KEYS
            
            missing_keys = [k for k in feature_keys if k not in pixel_features]
            if missing_keys:
                raise ValueError(
                    f"Faltan las siguientes features de píxeles: {missing_keys}"
                )
            lengths.extend(len(pixel_features[feat]) for feat in feature_keys)

        if len(set(lengths)) > 1:
            mismatched: Dict[str, int] = {
                "images": len(image_paths),
                **{f"target_{k}": len(v) for k, v in targets.items()},
                **(
                    {f"pixel_{k}": len(v) for k, v in pixel_features.items()}
                    if pixel_features is not None and is_hybrid
                    else {}
                ),
            }
            logger.error(
                f"Error: Longitudes de datos inconsistentes: {mismatched}"
            )
            raise ValueError(
                f"Longitudes inconsistentes en los datos del dataset: {mismatched}"
            )
    
    def _validate_structure(self) -> None:
        """Valida la estructura de datos."""
        # Validar que todos los targets estén presentes
        missing_targets = set(self.TARGET_ORDER) - set(self.targets.keys())
        if missing_targets:
            raise ValueError(f"Targets faltantes: {missing_targets}")
        
        # Validar orden de targets
        target_keys = list(self.targets.keys())
        if target_keys != self.TARGET_ORDER:
            logger.warning(
                f"Orden de targets no es el esperado. Esperado: {self.TARGET_ORDER}, "
                f"Obtenido: {target_keys}. Reordenando..."
            )
            # Reordenar targets
            self.targets = {k: self.targets[k] for k in self.TARGET_ORDER}
        
        # Validar formato de imágenes
        self._validate_image_paths()
        
        logger.debug("✅ Estructura de datos validada correctamente")
    
    def _validate_image_paths(self) -> None:
        """Valida que las rutas de imágenes sean consistentes."""
        bmp_count = 0
        png_count = 0
        other_count = 0
        
        for img_path in self.image_paths:
            suffix = img_path.suffix.lower()
            if suffix == '.bmp':
                bmp_count += 1
            elif suffix == '.png':
                png_count += 1
            else:
                other_count += 1
        
        if other_count > 0:
            logger.warning(f"Encontradas {other_count} imágenes con formato no estándar (.bmp/.png)")
        
        # El dataset debe usar crops (.png) para entrenamiento
        if bmp_count > 0 and png_count > 0:
            logger.warning(
                f"Mezcla de formatos detectada: {bmp_count} .bmp y {png_count} .png. "
                f"Se recomienda usar solo .png (crops) para entrenamiento."
            )
        
        logger.debug(f"Formato de imágenes: {bmp_count} .bmp, {png_count} .png, {other_count} otros")

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        image_path = self.image_paths[idx]
        
        try:
            # Abrir imagen y convertir a RGB explícitamente
            image = Image.open(image_path)
            
            # Validar que la imagen sea válida
            if image is None:
                raise ValueError(f"Imagen no se pudo cargar: {image_path}")
            
            # Convertir a RGB (asegura 3 canales)
            if image.mode != 'RGB':
                logger.debug(f"Convirtiendo imagen {image_path.name} de {image.mode} a RGB")
                image = image.convert('RGB')
            
            # Aplicar transformaciones
            image_tensor = self.transform(image)
            
            # Validar formato del tensor
            if image_tensor.shape[0] != 3:
                raise ValueError(
                    f"Imagen debe tener 3 canales RGB, obtuvo {image_tensor.shape[0]} canales"
                )
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            raise

        available_targets = list(self.targets.keys())

        # Caso simple: un solo target
        if not self.is_multi_head and not self.is_hybrid:
            target_name = available_targets[0]
            target_value = float(self.targets[target_name][idx])

            if self.pixel_features is not None:
                # Detectar dinámicamente qué features están disponibles
                pixel_feat_values = []
                # Intentar usar features extendidos primero
                if all(k in self.pixel_features for k in CALIB_PIXEL_FEATURE_KEYS):
                    for key in CALIB_PIXEL_FEATURE_KEYS:
                        pixel_feat_values.append(float(self.pixel_features[key][idx]))
                else:
                    # Fallback a features básicos
                    for key in PIXEL_FEATURE_KEYS:
                        if key in self.pixel_features:
                            pixel_feat_values.append(float(self.pixel_features[key][idx]))
                
                pixel_feat = torch.tensor(pixel_feat_values, dtype=torch.float32)
                # Para compatibilidad con RegressionTrainer, se omite metadata aquí
                return (
                    image_tensor,
                    torch.tensor(target_value, dtype=torch.float32),
                    pixel_feat,
                )

            return image_tensor, torch.tensor(target_value, dtype=torch.float32)

        # Modelo multi‑head / híbrido: devolver los 4 targets en orden correcto
        # Orden: [alto, ancho, grosor, peso]
        targets_tensor = torch.tensor(
            [
                float(self.targets["alto"][idx]),
                float(self.targets["ancho"][idx]),
                float(self.targets["grosor"][idx]),
                float(self.targets["peso"][idx]),
            ],
            dtype=torch.float32,
        )

        if self.pixel_features is not None:
            # Usar todos los features disponibles (pueden ser 5 básicos o 12 extendidos)
            pixel_feat_values = []
            # Intentar usar features extendidos primero
            if all(k in self.pixel_features for k in CALIB_PIXEL_FEATURE_KEYS):
                for key in CALIB_PIXEL_FEATURE_KEYS:
                    pixel_feat_values.append(float(self.pixel_features[key][idx]))
            else:
                # Fallback a features básicos
                for key in PIXEL_FEATURE_KEYS:
                    if key in self.pixel_features:
                        pixel_feat_values.append(float(self.pixel_features[key][idx]))
            
            pixel_feat = np.array(pixel_feat_values, dtype=np.float32)
            
            # Normalizar pixel_features
            if self.pixel_means is not None and self.pixel_stds is not None:
                pixel_feat = (pixel_feat - self.pixel_means) / self.pixel_stds
            
            pixel_feat = torch.tensor(pixel_feat, dtype=torch.float32)
            return image_tensor, targets_tensor, pixel_feat

        return image_tensor, targets_tensor


class SingleDimensionDataset(Dataset):
    """
    Dataset para el modo single_dimension_training.

    Cada entrada devuelve:
        image_tensor,
        target_scalar (escalado),
        pixel_features_vector (11 features),
        extra_metadata
    """

    def __init__(
        self,
        image_paths: List[Path],
        targets: np.ndarray,
        transform: Any,
        pixel_features_matrix: np.ndarray,
        metadata: List[Dict[str, Any]],
    ):
        if len(image_paths) != len(targets):
            raise ValueError("Longitudes inconsistentes entre imágenes y targets")
        if len(image_paths) != len(pixel_features_matrix):
            raise ValueError(
                "Longitudes inconsistentes entre imágenes y pixel_features"
            )
        if len(image_paths) != len(metadata):
            raise ValueError("Longitudes inconsistentes entre imágenes y metadata")

        self.image_paths = image_paths
        self.targets = targets.astype(np.float32)
        self.transform = transform
        self.pixel_features_matrix = pixel_features_matrix.astype(np.float32)
        self.metadata = metadata

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image)

        target_scalar = float(self.targets[idx])
        pixel_vector = torch.tensor(
            self.pixel_features_matrix[idx], dtype=torch.float32
        )
        extra_metadata = self.metadata[idx]

        return (
            image_tensor,
            torch.tensor(target_scalar, dtype=torch.float32),
            pixel_vector,
            extra_metadata,
        )


class CacaoTrainingPipeline:
    """Pipeline completo de entrenamiento."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = get_device()
        self.scalers = None
        self.train_loader: Optional[DataLoader] = None
        self.val_loader: Optional[DataLoader] = None
        self.test_loader: Optional[DataLoader] = None
        # Flags principales de configuración de modelo
        self.is_multi_head = bool(self.config.get("multi_head", False))
        self.is_hybrid = bool(self.config.get("hybrid", False))
        # Flag para controlar si se usan features de píxeles en los splits y datasets
        self.use_pixel_features = bool(self.config.get("use_pixel_features", False))
        # Nuevo flag: modo single_dimension_training
        self.single_dimension_training = bool(
            self.config.get("single_dimension_training", False)
        )

        # Buffers para modo single-dimension (se rellenan en load_data / run_pipeline)
        self.single_dim_real_dimensions: Optional[Dict[str, np.ndarray]] = None
        self.single_dim_pixel_features: Optional[Dict[str, np.ndarray]] = None
        self.single_dim_metadata: Optional[List[Dict[str, Any]]] = None

        self.train_images: Optional[List[Path]] = None
        self.val_images: Optional[List[Path]] = None
        self.test_images: Optional[List[Path]] = None

        self.train_targets: Optional[Dict[str, np.ndarray]] = None
        self.val_targets: Optional[Dict[str, np.ndarray]] = None
        self.test_targets: Optional[Dict[str, np.ndarray]] = None

        self.train_targets_original: Optional[Dict[str, np.ndarray]] = None
        self.val_targets_original: Optional[Dict[str, np.ndarray]] = None
        self.test_targets_original: Optional[Dict[str, np.ndarray]] = None

        self.pixel_features: Optional[Dict[str, np.ndarray]] = None
        self.train_pixel_features: Optional[Dict[str, np.ndarray]] = None
        self.val_pixel_features: Optional[Dict[str, np.ndarray]] = None
        self.test_pixel_features: Optional[Dict[str, np.ndarray]] = None

        self.train_real_dimensions: Optional[Dict[str, np.ndarray]] = None
        self.val_real_dimensions: Optional[Dict[str, np.ndarray]] = None
        self.test_real_dimensions: Optional[Dict[str, np.ndarray]] = None

        self.train_single_dim_pixel_features: Optional[Dict[str, np.ndarray]] = None
        self.val_single_dim_pixel_features: Optional[Dict[str, np.ndarray]] = None
        self.test_single_dim_pixel_features: Optional[Dict[str, np.ndarray]] = None

        self.train_single_dim_metadata: Optional[List[Dict[str, Any]]] = None
        self.val_single_dim_metadata: Optional[List[Dict[str, Any]]] = None
        self.test_single_dim_metadata: Optional[List[Dict[str, Any]]] = None

        logger.info(f"Pipeline inicializado con configuración: {config}")

    def load_data(
        self,
    ) -> Tuple[List[Path], Dict[str, np.ndarray], Optional[Dict[str, np.ndarray]]]:
        """
        Carga y prepara los datos, incluyendo features de píxeles si están disponibles.
        """
        logger.info("Cargando datos...")

        # Intentar cargar calibración de píxeles (pixel_calibration.json)
        pixel_calibration: Optional[Dict[str, Any]] = None
        calibration_file = get_datasets_dir() / "pixel_calibration.json"
        if calibration_file.exists():
            try:
                pixel_calibration = load_json(calibration_file)
                num_calib = len(pixel_calibration.get("calibration_records", []))
                logger.info(
                    f"Calibración de píxeles cargada: {num_calib} registros desde {calibration_file}"
                )
            except Exception as e:
                logger.warning(
                    f"Error cargando pixel_calibration.json ({calibration_file}): {e}"
                )

        # Cargar registros válidos
        loader = CacaoDatasetLoader()
        valid_records = loader.get_valid_records()

        if not valid_records:
            raise ValueError("No se encontraron registros válidos")

        logger.info(f"Encontrados {len(valid_records)} registros válidos")

        # Filtrar registros que tienen crops
        crop_records: List[Dict[str, Any]] = []
        missing_crop_records: List[Dict[str, Any]] = []

        for record in valid_records:
            crop_path_value = record["crop_image_path"]
            if crop_path_value:
                crop_path = (
                    crop_path_value
                    if isinstance(crop_path_value, Path)
                    else Path(crop_path_value)
                )
            else:
                crop_path = None
            record["crop_image_path"] = crop_path
            if crop_path and crop_path.exists():
                crop_records.append(record)
            else:
                missing_crop_records.append(record)

        logger.info(f"Registros con crops disponibles: {len(crop_records)}")
        logger.info(f"Registros sin crops: {len(missing_crop_records)}")

        # Validar y regenerar crops de mala calidad si está configurado
        validate_crops = self.config.get("validate_crops_quality", True)
        regenerate_bad = self.config.get("regenerate_bad_crops", True)
        seg_backend = self.config.get("segmentation_backend", "auto")

        if seg_backend == "opencv":
            validate_crops = False
            regenerate_bad = False

        if validate_crops and crop_records:
            logger.info("Validando calidad de crops existentes...")
            bad_crop_records: List[Dict[str, Any]] = []
            good_crop_records: List[Dict[str, Any]] = []

            from ..segmentation.cropper import create_cacao_cropper as _create_c
            from ..data.transforms import validate_crop_quality  # noqa: F401
            import cv2

            cropper = _create_c(  # noqa: F841
                confidence_threshold=0.3,
                crop_size=512,
                padding=10,
            )

            for record in crop_records:
                try:
                    crop_path = record["crop_image_path"]
                    _original_path = record["image_path"]

                    crop_img = cv2.imread(str(crop_path))
                    if crop_img is None:
                        bad_crop_records.append(record)
                        continue

                    crop_img_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)

                    h, w = crop_img_rgb.shape[:2]
                    if h < 100 or w < 100:
                        logger.warning(
                            f"Crop demasiado pequeño ({w}x{h}) para {crop_path.name}"
                        )
                        bad_crop_records.append(record)
                        continue

                    if crop_img_rgb.shape[2] == 4:
                        alpha = crop_img_rgb[:, :, 3]
                        if np.sum(alpha > 128) < (h * w * 0.1):
                            logger.warning(
                                f"Crop con muy poco contenido visible para {crop_path.name}"
                            )
                            bad_crop_records.append(record)
                            continue

                    good_crop_records.append(record)

                except Exception as e:
                    logger.warning(
                        f"Error validando crop {record.get('id', 'unknown')}: {e}"
                    )
                    bad_crop_records.append(record)

            logger.info(
                "Crops válidos: %d, crops inválidos: %d",
                len(good_crop_records),
                len(bad_crop_records),
            )

            if regenerate_bad and bad_crop_records:
                logger.info(
                    "Regenerando %d crops de mala calidad...", len(bad_crop_records)
                )
                for record in bad_crop_records:
                    crop_path = record["crop_image_path"]
                    if crop_path.exists():
                        crop_path.unlink()

                new_crop_records = self._generate_crops_for_missing(bad_crop_records)
                good_crop_records.extend(new_crop_records)

            crop_records = good_crop_records

        if missing_crop_records:
            if seg_backend == "opencv":
                logger.info(
                    "Modo sólo-crops-existentes "
                    "(segmentation_backend=opencv): se omiten %d registros sin PNG.",
                    len(missing_crop_records),
                )
                if len(crop_records) < 10:
                    raise ValueError(
                        "Muy pocos registros con crops existentes: "
                        f"{len(crop_records)}. Se necesitan al menos 10 para entrenamiento."
                    )
            else:
                logger.info(
                    "Generando crops para %d imágenes faltantes...",
                    len(missing_crop_records),
                )
                new_crop_records = self._generate_crops_for_missing(
                    missing_crop_records
                )
                crop_records.extend(new_crop_records)

                logger.info(
                    "Total de registros con crops después de generación: %d",
                    len(crop_records),
                )

                if len(crop_records) < 10:
                    raise ValueError(
                        "Muy pocos registros con crops después de generación: "
                        f"{len(crop_records)}"
                    )
        else:
            logger.info("[OK] Todos los crops ya existen y están validados.")

        # Extraer rutas de imágenes y targets clásicos
        image_paths: List[Path] = [record["crop_image_path"] for record in crop_records]
        targets: Dict[str, np.ndarray] = {
            target: np.array([record[target] for record in crop_records])
            for target in TARGETS
        }

        # Extraer features de píxeles base y extendidos
        pixel_features: Optional[Dict[str, np.ndarray]] = None

        self.single_dim_real_dimensions = None
        self.single_dim_pixel_features = None
        self.single_dim_metadata = None

        if pixel_calibration is not None:
            calibration_records = pixel_calibration.get("calibration_records", [])
            if calibration_records:
                calibration_by_id: Dict[int, Dict[str, Any]] = {
                    rec["id"]: rec for rec in calibration_records
                }

                pixel_features = {
                    "pixel_width": [],
                    "pixel_height": [],
                    "pixel_area": [],
                    "scale_factor": [],
                    "aspect_ratio": [],
                }

                real_dimensions: Dict[str, List[float]] = {
                    "alto_mm": [],
                    "ancho_mm": [],
                    "grosor_mm": [],
                    "peso_g": [],
                }
                extended_features: Dict[str, List[float]] = {
                    k: [] for k in CALIB_PIXEL_FEATURE_KEYS
                }
                metadata_list: List[Dict[str, Any]] = []

                for record in crop_records:
                    image_id = record["id"]
                    calib_record = calibration_by_id.get(image_id)

                    if calib_record:
                        pixel_meas = calib_record.get("pixel_measurements", {})
                        scale_factors = calib_record.get("scale_factors", {})
                        bg_info = calib_record.get("background_info", {})
                        real_dims = calib_record.get("real_dimensions", {})

                        pixel_features["pixel_width"].append(
                            float(pixel_meas.get("width_pixels", 0.0))
                        )
                        pixel_features["pixel_height"].append(
                            float(pixel_meas.get("height_pixels", 0.0))
                        )
                        pixel_features["pixel_area"].append(
                            float(pixel_meas.get("grain_area_pixels", 0.0))
                        )
                        pixel_features["scale_factor"].append(
                            float(scale_factors.get("average_mm_per_pixel", 0.0))
                        )
                        pixel_features["aspect_ratio"].append(
                            float(pixel_meas.get("aspect_ratio", 0.0))
                        )

                        real_dimensions["alto_mm"].append(
                            float(real_dims.get("alto_mm", 0.0))
                        )
                        real_dimensions["ancho_mm"].append(
                            float(real_dims.get("ancho_mm", 0.0))
                        )
                        real_dimensions["grosor_mm"].append(
                            float(real_dims.get("grosor_mm", 0.0))
                        )
                        real_dimensions["peso_g"].append(
                            float(real_dims.get("peso_g", 0.0))
                        )

                        extended_features["grain_area_pixels"].append(
                            float(pixel_meas.get("grain_area_pixels", 0.0))
                        )
                        extended_features["width_pixels"].append(
                            float(pixel_meas.get("width_pixels", 0.0))
                        )
                        extended_features["height_pixels"].append(
                            float(pixel_meas.get("height_pixels", 0.0))
                        )
                        extended_features["bbox_area_pixels"].append(
                            float(pixel_meas.get("bbox_area_pixels", 0.0))
                        )
                        extended_features["aspect_ratio"].append(
                            float(pixel_meas.get("aspect_ratio", 0.0))
                        )
                        extended_features["original_total_pixels"].append(
                            float(bg_info.get("original_total_pixels", 0.0))
                        )
                        extended_features["background_pixels"].append(
                            float(bg_info.get("background_pixels", 0.0))
                        )
                        extended_features["background_ratio"].append(
                            float(bg_info.get("background_ratio", 0.0))
                        )
                        extended_features["alto_mm_per_pixel"].append(
                            float(scale_factors.get("alto_mm_per_pixel", 0.0))
                        )
                        extended_features["ancho_mm_per_pixel"].append(
                            float(scale_factors.get("ancho_mm_per_pixel", 0.0))
                        )
                        extended_features["average_mm_per_pixel"].append(
                            float(scale_factors.get("average_mm_per_pixel", 0.0))
                        )
                        extended_features["segmentation_confidence"].append(
                            float(calib_record.get("segmentation_confidence", 0.0))
                        )

                        metadata_list.append(
                            {
                                "id": image_id,
                                "filename": calib_record.get("filename"),
                                "original_image_path": calib_record.get(
                                    "original_image_path"
                                ),
                                "processed_image_path": calib_record.get(
                                    "processed_image_path"
                                ),
                                "real_dimensions": real_dims,
                                "pixel_measurements": pixel_meas,
                                "background_info": bg_info,
                                "scale_factors": scale_factors,
                                "segmentation_confidence": calib_record.get(
                                    "segmentation_confidence", 0.0
                                ),
                            }
                        )
                    else:
                        pixel_features["pixel_width"].append(0.0)
                        pixel_features["pixel_height"].append(0.0)
                        pixel_features["pixel_area"].append(0.0)
                        pixel_features["scale_factor"].append(0.0)
                        pixel_features["aspect_ratio"].append(1.0)

                        for k in SINGLE_DIM_TARGETS:
                            real_dimensions[k].append(0.0)

                        for k in CALIB_PIXEL_FEATURE_KEYS:
                            extended_features[k].append(0.0)

                        metadata_list.append(
                            {
                                "id": image_id,
                                "real_dimensions": {},
                                "pixel_measurements": {},
                                "background_info": {},
                                "scale_factors": {},
                                "segmentation_confidence": 0.0,
                            }
                        )

                # Guardar features básicos en pixel_features (para compatibilidad con dataset)
                pixel_features = {
                    k: np.array(v, dtype=np.float32) for k, v in pixel_features.items()
                }
                
                # También agregar features extendidos a pixel_features si están disponibles
                # Esto permite que el dataset use los features extendidos cuando estén disponibles
                for key in CALIB_PIXEL_FEATURE_KEYS:
                    if key not in pixel_features and key in extended_features:
                        pixel_features[key] = np.array(extended_features[key], dtype=np.float32)
                
                self.single_dim_real_dimensions = {
                    k: np.array(v, dtype=np.float32) for k, v in real_dimensions.items()
                }
                self.single_dim_pixel_features = {
                    k: np.array(v, dtype=np.float32)
                    for k, v in extended_features.items()
                }
                self.single_dim_metadata = metadata_list

                logger.info(
                    " Features de píxeles cargadas para %d/%d registros",
                    len(
                        [
                            r
                            for r in crop_records
                            if calibration_by_id.get(r["id"]) is not None
                        ]
                    ),
                    len(crop_records),
                )
            else:
                logger.warning(
                    "[WARN] pixel_calibration.json existe pero no tiene registros"
                )
        else:
            logger.info(
                " Calibración de píxeles no disponible. Entrenando sin features de píxeles."
            )

        if self.single_dimension_training and (
            self.single_dim_real_dimensions is None
            or self.single_dim_pixel_features is None
            or self.single_dim_metadata is None
        ):
            raise ValueError(
                "single_dimension_training requiere pixel_calibration.json completo. "
                "No se pudieron cargar real_dimensions / pixel_features extendidos."
            )

        return image_paths, targets, pixel_features
    
    def create_stratified_split(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        pixel_features: Optional[Dict[str, np.ndarray]],
        test_size: float = 0.2,
        val_size: float = 0.1
    ) -> Tuple[List[Path], List[Path], List[Path], Dict, Dict, Dict]:
        """
        Crea split estratificado basado en cuantiles de peso y dimensiones.
        
        Args:
            image_paths: Rutas de imágenes
            targets: Targets
            test_size: Proporción para test
            val_size: Proporción para validación
            
        Returns:
            Tuples con splits de imágenes y targets
        """
        logger.info("Creando split estratificado...")
        
        n_samples = len(image_paths)
        indices = np.arange(n_samples)
        
        peso_values = targets['peso']
        n_quantiles = min(5, n_samples // 10)  # Ajustar número de cuantiles
        
        if n_quantiles < 2:
            logger.warning("Muy pocos muestras para estratificación, usando split aleatorio")
            # Split aleatorio simple
            train_idx, test_idx = train_test_split(
                range(n_samples), test_size=test_size, random_state=42
            )
            train_idx, val_idx = train_test_split(
                train_idx, test_size=val_size/(1-test_size), random_state=42
            )
        else:
            try:
                # Estratificación por cuantiles de peso
                quantile_transformer = QuantileTransformer(n_quantiles=n_quantiles, random_state=42)
                peso_quantiles = quantile_transformer.fit_transform(peso_values.reshape(-1, 1)).flatten()
                
                # Convertir a bins para estratificación
                strata = pd.cut(peso_quantiles, bins=n_quantiles, labels=False)
                
                # Verificar que todos los estratos tengan al menos 2 muestras
                strata_counts = pd.Series(strata).value_counts()
                min_strata_count = strata_counts.min()
                
                if min_strata_count < 2:
                    logger.warning(f"Algunos estratos tienen menos de 2 muestras (mínimo: {min_strata_count}). Usando split aleatorio.")
                    raise ValueError("Estratificación no viable")
                
                # Split estratificado
                train_idx, test_idx = train_test_split(
                    range(n_samples), test_size=test_size, random_state=42, stratify=strata
                )
                
                # Crear estratos para el conjunto de entrenamiento
                train_strata = strata[train_idx]
                train_strata_counts = pd.Series(train_strata).value_counts()
                
                # Verificar que los estratos del train también tengan al menos 2 muestras
                if train_strata_counts.min() < 2:
                    logger.warning("Estratificación no viable para validación. Usando split aleatorio para validación.")
                    train_idx, val_idx = train_test_split(
                        train_idx, test_size=val_size/(1-test_size), random_state=42
                    )
                else:
                    train_idx, val_idx = train_test_split(
                        train_idx, test_size=val_size/(1-test_size), random_state=42, stratify=train_strata
                    )
                    
            except (ValueError, Exception) as e:
                logger.warning(f"Error en estratificación: {e}. Usando split aleatorio.")
                # Fallback a split aleatorio
                train_idx, test_idx = train_test_split(
                    range(n_samples), test_size=test_size, random_state=42
                )
                train_idx, val_idx = train_test_split(
                    train_idx, test_size=val_size/(1-test_size), random_state=42
                )
        
        # Crear splits de imágenes
        train_images = [image_paths[i] for i in train_idx]
        val_images = [image_paths[i] for i in val_idx]
        test_images = [image_paths[i] for i in test_idx]
        
        train_targets = {target: targets[target][train_idx] for target in TARGETS}
        val_targets = {target: targets[target][val_idx] for target in TARGETS}
        test_targets = {target: targets[target][test_idx] for target in TARGETS}
        
        train_pixel_features = None
        val_pixel_features = None
        test_pixel_features = None
        
        if self.use_pixel_features and pixel_features is not None:
            # Determinar qué features usar (básicos o extendidos)
            # Si tenemos single_dim_pixel_features, significa que usamos features extendidos
            if self.single_dim_pixel_features is not None and len(self.single_dim_pixel_features) == len(CALIB_PIXEL_FEATURE_KEYS):
                # Usar features extendidos de pixel_calibration.json
                feature_keys = CALIB_PIXEL_FEATURE_KEYS
                logger.info(f"✅ Usando {len(feature_keys)} features extendidos de pixel_calibration.json")
            else:
                # Usar features básicos
                feature_keys = PIXEL_FEATURE_KEYS
                logger.info(f"✅ Usando {len(feature_keys)} features básicos de píxeles")
            
            # Verificar que todos los keys existen en pixel_features
            available_keys = [k for k in feature_keys if k in pixel_features]
            if len(available_keys) != len(feature_keys):
                missing = set(feature_keys) - set(available_keys)
                logger.warning(f"Algunos features faltantes: {missing}. Usando solo los disponibles.")
                feature_keys = available_keys
            
            if feature_keys:
                train_pixel_features = {key: pixel_features[key][train_idx] for key in feature_keys}
                val_pixel_features = {key: pixel_features[key][val_idx] for key in feature_keys}
                test_pixel_features = {key: pixel_features[key][test_idx] for key in feature_keys}
                logger.info(f"✅ Features de píxeles divididas por splits ({len(feature_keys)} features)")
            else:
                logger.warning("No hay features de píxeles disponibles después de validación")
        
        logger.info(f"Split creado: Train={len(train_images)}, Val={len(val_images)}, Test={len(test_images)}")
        
        return (
            train_images, val_images, test_images,
            train_targets, val_targets, test_targets,
            train_pixel_features, val_pixel_features, test_pixel_features
        )

    def create_data_loaders(
        self,
        train_images: List[Path], val_images: List[Path], test_images: List[Path],
        train_targets: Dict, val_targets: Dict, test_targets: Dict,
        train_pixel_features: Optional[Dict], val_pixel_features: Optional[Dict], test_pixel_features: Optional[Dict]
    ) -> None:
        """
        Crea los data loaders, incluyendo features de pxeles si estn disponibles.
        """
        logger.info("Creando data loaders...")
        
        import torchvision.transforms as transforms
        
        # Transformaciones de entrenamiento avanzadas
        from ..regression.augmentation import create_advanced_train_transform, create_advanced_val_transform
        
        # Usar augmentation avanzado si est configurado
        use_advanced_aug = self.config.get('use_advanced_augmentation', True)
        
        if use_advanced_aug:
            train_transform = create_advanced_train_transform(self.config['img_size'])
            logger.info("Usando augmentation avanzado para entrenamiento")
        else:
            # Transformaciones de entrenamiento moderadas (fallback)
            train_transform = transforms.Compose([
                transforms.Resize((self.config['img_size'], self.config['img_size'])),
                transforms.RandomRotation(degrees=5),
                transforms.ColorJitter(brightness=0.1, contrast=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        # Transformaciones de validacin/test avanzadas
        if use_advanced_aug:
            val_transform = create_advanced_val_transform(self.config['img_size'])
        else:
            # Transformaciones de validacin/test estndar (fallback)
            val_transform = transforms.Compose([
                transforms.Resize((self.config['img_size'], self.config['img_size'])),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        # Determinar si es modelo multi-head o híbrido
        is_multi_head = self.is_multi_head
        is_hybrid = self.is_hybrid or (train_pixel_features is not None and len(train_pixel_features) > 0)
        
        # Crear datasets con pixel_features si están disponibles
        train_dataset = CacaoDataset(
            train_images,
            train_targets,
            train_transform,
            train_pixel_features,
            is_multi_head=is_multi_head,
            is_hybrid=is_hybrid
        )
        val_dataset = CacaoDataset(
            val_images,
            val_targets,
            val_transform,
            val_pixel_features,
            is_multi_head=is_multi_head,
            is_hybrid=is_hybrid
        )
        test_dataset = CacaoDataset(
            test_images,
            test_targets,
            val_transform,
            test_pixel_features,
            is_multi_head=is_multi_head,
            is_hybrid=is_hybrid
        )
        
        # Detectar Windows y ajustar num_workers (multiprocessing en Windows causa MemoryError)
        is_windows = platform.system() == 'Windows'
        num_workers = self.config.get('num_workers', 2)
        if is_windows and num_workers > 0:
            logger.warning("Windows detectado: forzando num_workers=0 para evitar MemoryError.")
            num_workers = 0
        
        pin_memory = (not is_windows) and (self.device.type == 'cuda')
        
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config['batch_size'],
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=num_workers > 0 if num_workers > 0 else False,
            drop_last=True 
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config['batch_size'] * 2, 
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=num_workers > 0 if num_workers > 0 else False
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config['batch_size'] * 2,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory
        )
        
        logger.info("Data loaders creados exitosamente")
    
    def prepare_scalers(self, train_targets: Dict[str, np.ndarray]) -> None:
        """
        Prepara y ajusta los escaladores.
        
        NOTA: Este mtodo ahora es redundante ya que los escaladores se preparan
        antes de normalizar los targets en run_pipeline(). Se mantiene por compatibilidad.
        """
        if self.scalers is None:
            logger.info("Preparando escaladores...")
            # Crear DataFrame para escaladores
            train_df = pd.DataFrame(train_targets)
            self.scalers = create_scalers_from_data(train_df, scaler_type="standard")
            logger.info("Escaladores preparados")
        else:
            logger.debug("Escaladores ya preparados, omitiendo")
    
    def train_models(self) -> Dict[str, Union[Dict, List]]:
        """
        Entrena los modelos (individuales o multi-head/híbrido).
        """
        logger.info(f"Iniciando entrenamiento (multi_head={self.is_multi_head}, hybrid={self.is_hybrid})...")
        
        if self.is_multi_head or self.is_hybrid:
            return self._train_multi_head_model()
        else:
            return self._train_individual_models()

    def _train_individual_models(self) -> Dict[str, Dict]:
        """Entrena modelos individuales para cada target."""
        histories = {}
        
        for target in TARGETS:
            logger.info(f"Entrenando modelo individual para {target}...")
            
            model = create_model(
                model_type=self.config['model_type'],
                num_outputs=1,
                pretrained=self.config.get('pretrained', True),
                dropout_rate=self.config.get('dropout_rate', 0.2),
                multi_head=False,
                hybrid=False
            )
            
            train_targets_single = {target: self.train_targets[target]}
            val_targets_single = {target: self.val_targets[target]}
            
            # Crear datasets individuales
            is_windows = platform.system() == 'Windows'
            num_workers_single = 0 if is_windows else self.config.get('num_workers', 0)
            pin_memory_single = (not is_windows) and (self.device.type == 'cuda')
            
            train_dataset_single = CacaoDataset(
                self.train_images, 
                train_targets_single, 
                self.train_loader.dataset.transform, 
                is_multi_head=False, 
                is_hybrid=False
            )
            val_dataset_single = CacaoDataset(
                self.val_images,
                val_targets_single,
                self.val_loader.dataset.transform,
                is_multi_head=False,
                is_hybrid=False
            )
            
            train_loader_single = DataLoader(
                train_dataset_single,
                batch_size=self.config['batch_size'], 
                shuffle=True, 
                num_workers=num_workers_single,
                pin_memory=pin_memory_single
            )
            val_loader_single = DataLoader(
                val_dataset_single,
                batch_size=self.config['batch_size'],
                shuffle=False,
                num_workers=num_workers_single,
                pin_memory=pin_memory_single
            )
            
            # Preparar información del dataset
            dataset_info = {
                'train_size': len(train_loader_single.dataset),
                'val_size': len(val_loader_single.dataset),
                'test_size': len(self.test_loader.dataset) if self.test_loader else 0
            }
            
            # Entrenar modelo
            history = train_single_model(
                model=model,
                train_loader=train_loader_single,
                val_loader=val_loader_single,
                scalers=self.scalers,
                target=target,
                config=self.config,
                device=self.device
            )
            histories[target] = history
        
        return histories

    def _train_multi_head_model(self) -> Dict[str, Union[Dict, List]]:
        """Entrena modelo multi-head o híbrido."""
        # Verificar si es modelo híbrido nuevo (usando el sistema híbrido mejorado)
        is_hybrid = self.config.get('hybrid', False) or self.config.get('model_type') == 'hybrid'
        use_pixel_features = self.config.get('use_pixel_features', True)
        use_hybrid_v2 = self.config.get('hybrid_v2', False)
        
        # Check if using new hybrid v2 system (optimized)
        if (is_hybrid or use_hybrid_v2) and use_pixel_features:
            try:
                from .hybrid_v2_training import train_hybrid_v2
                logger.info("Using optimized hybrid v2 training system")
                results = train_hybrid_v2(self.config)
                return {
                    'hybrid': results,
                    'history': results.get('history', {}),
                    'test_metrics': results.get('test_metrics', {})
                }
            except ImportError as e:
                logger.warning(f"Hybrid v2 training not available: {e}. Trying hybrid v1.")
            except Exception as e:
                logger.error(f"Error in hybrid v2 training: {e}. Trying hybrid v1.")
        
        # Check if using hybrid v1 system
        if is_hybrid and use_pixel_features:
            try:
                from .hybrid_training import train_hybrid_model
                logger.info("Using hybrid v1 training system with normalized pixel features")
                results = train_hybrid_model(self.config)
                return {
                    'hybrid': results,
                    'history': results.get('history', {}),
                    'test_metrics': results.get('test_metrics', {})
                }
            except ImportError as e:
                logger.warning(f"Hybrid v1 training not available: {e}. Falling back to legacy hybrid.")
            except Exception as e:
                logger.error(f"Error in hybrid v1 training: {e}. Falling back to legacy hybrid.")
        
        # Legacy hybrid/multi-head training
        if is_hybrid:
            logger.info("Entrenando modelo HÍBRIDO (ResNet18 + ConvNeXt + Píxeles)...")
        else:
            logger.info("Entrenando modelo multi-head...")
        
        # Determinar número de features de píxeles
        pixel_feature_dim = None
        if is_hybrid and use_pixel_features:
            # Verificar si se están usando features extendidos de pixel_calibration.json
            if self.train_pixel_features is not None:
                # Contar cuántas keys hay en pixel_features
                num_keys = len(self.train_pixel_features.keys())
                if num_keys == len(CALIB_PIXEL_FEATURE_KEYS):
                    pixel_feature_dim = len(CALIB_PIXEL_FEATURE_KEYS)  # 12 features extendidos
                    logger.info(f"Usando {pixel_feature_dim} features de píxeles extendidos de pixel_calibration.json")
                elif num_keys == len(PIXEL_FEATURE_KEYS):
                    pixel_feature_dim = len(PIXEL_FEATURE_KEYS)  # 5 features básicos
                    logger.info(f"Usando {pixel_feature_dim} features de píxeles básicos")
                else:
                    logger.warning(f"Número inesperado de features de píxeles: {num_keys}. Usando 5 por defecto.")
                    pixel_feature_dim = 5
            else:
                pixel_feature_dim = 5  # Por defecto
        
        # Crear modelo multi-head o hbrido
        model = create_model(
            model_type=self.config['model_type'],
            num_outputs=4, 
            pretrained=self.config.get('pretrained', True),
            dropout_rate=self.config.get('dropout_rate', 0.2),
            multi_head=not is_hybrid,  # Si es hbrido, no usar multi_head (usa hybrid=True)
            hybrid=is_hybrid,
            use_pixel_features=use_pixel_features,
            pixel_feature_dim=pixel_feature_dim
        )
        
        # Preparar información del dataset
        dataset_info = {
            'train_size': len(self.train_loader.dataset),
            'val_size': len(self.val_loader.dataset),
            'test_size': len(self.test_loader.dataset) if self.test_loader else 0
        }
        
        # Determinar si usar UncertaintyWeightedLoss
        # Se puede configurar explícitamente o se detecta automáticamente
        use_uncertainty_loss = self.config.get('use_uncertainty_loss', None)
        
        # Entrenar modelo
        history = train_multi_head_model(
            model=model,
            train_loader=self.train_loader,
            val_loader=self.val_loader,
            scalers=self.scalers,
            config=self.config,
            device=self.device,
            use_uncertainty_loss=use_uncertainty_loss
        )
        
        return {'multihead': history}
    
    def evaluate_models(self, multi_head: bool = False) -> Dict[str, Union[Dict, List]]:
        """
        Evalúa los modelos entrenados.
        
        Args:
            multi_head: Si evaluar modelo multi-head o individuales
            
        Returns:
            Resultados de evaluación
        """
        logger.info(f"Evaluando modelos (multi_head={multi_head})...")
        
        if self.is_multi_head or self.is_hybrid:
            return self._evaluate_multi_head_model()
        else:
            return self._evaluate_individual_models()

    def _evaluate_individual_models(self) -> Dict[str, Dict]:
        """Evalúa modelos individuales."""
        results = {}
        
        for target in TARGETS:
            logger.info(f"Evaluando modelo para {target}...")
            model_path = get_regressors_artifacts_dir() / f"{target}.pt"
            if not model_path.exists():
                logger.warning(f"Modelo no encontrado para {target}: {model_path}")
                continue
            
            model = create_model(
                model_type=self.config['model_type'], num_outputs=1, pretrained=False,
                multi_head=False, hybrid=False
            )
            checkpoint = torch.load(model_path, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # Crear un DataLoader especfico para este target
            # El dataset devuelve (image, tensor) para modelos individuales
            from torch.utils.data import DataLoader
            from ml.pipeline.train_all import CacaoDataset
            import torchvision.transforms as transforms
            
            # Transformaciones de test
            test_transform = transforms.Compose([
                transforms.Resize((self.config['img_size'], self.config['img_size'])),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # Crear dataset con solo este target usando los splits guardados
            # NOTA: self.test_targets contiene valores NORMALIZADOS (el modelo predice valores normalizados)
            target_only_dataset = CacaoDataset(
                self.test_images,
                {target: self.test_targets[target]},
                test_transform
            )
            
            # Crear loader especfico para este target
            is_windows = platform.system() == 'Windows'
            num_workers = 0 if is_windows else self.config.get('num_workers', 2)
            test_loader_single = DataLoader(
                target_only_dataset,
                batch_size=self.config['batch_size'],
                shuffle=False,
                num_workers=num_workers,
                pin_memory=not is_windows
            )
            
            # Crear evaluador con el loader especfico
            evaluator = RegressionEvaluator(
                model=model, test_loader=test_loader_single,
                scalers=self.scalers, device=self.device
            )
            target_results = evaluator.evaluate_single_model(target, denormalize=True)
            results[target] = target_results
        
        return results

    def _evaluate_multi_head_model(self) -> Dict[str, Dict]:
        """Evalúa modelo multi-head."""
        logger.info("Evaluando modelo multi-head...")
        
        model_name = "hybrid.pt" if self.is_hybrid else "multihead.pt"
        model_path = get_regressors_artifacts_dir() / model_name
        
        if not model_path.exists():
            if self.is_hybrid and (get_regressors_artifacts_dir() / "multihead.pt").exists():
                model_path = get_regressors_artifacts_dir() / "multihead.pt"
                logger.warning(f"Usando 'multihead.pt' para el modelo híbrido.")
            else:
                 logger.warning(f"Modelo {model_name} no encontrado: {model_path}")
                 return {}

        # Cargar checkpoint para detectar pixel_feature_dim
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Determinar pixel_feature_dim de la misma manera que en entrenamiento
        pixel_feature_dim = None
        if self.is_hybrid and self.use_pixel_features:
            # Método 1: Intentar detectar desde el checkpoint (shape de pixel_branch.0.weight)
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
                if 'pixel_branch.0.weight' in state_dict:
                    # El shape es [256, num_pixel_features]
                    pixel_feature_dim = state_dict['pixel_branch.0.weight'].shape[1]
                    logger.info(f"Detectado pixel_feature_dim={pixel_feature_dim} desde checkpoint (pixel_branch.0.weight.shape)")
            
            # Método 2: Intentar desde model_info si está disponible
            if pixel_feature_dim is None and 'model_info' in checkpoint:
                model_info = checkpoint.get('model_info', {})
                config = model_info.get('config', {})
                if 'pixel_feature_dim' in config:
                    pixel_feature_dim = config['pixel_feature_dim']
                    logger.info(f"Detectado pixel_feature_dim={pixel_feature_dim} desde model_info.config")
            
            # Método 3: Inferir desde pixel_features disponibles (igual que en entrenamiento)
            if pixel_feature_dim is None:
                if self.test_pixel_features is not None:
                    num_keys = len(self.test_pixel_features.keys())
                    if num_keys == len(CALIB_PIXEL_FEATURE_KEYS):
                        pixel_feature_dim = len(CALIB_PIXEL_FEATURE_KEYS)  # 12 features extendidos
                        logger.info(f"Inferido pixel_feature_dim={pixel_feature_dim} desde test_pixel_features (12 features extendidos)")
                    elif num_keys == len(PIXEL_FEATURE_KEYS):
                        pixel_feature_dim = len(PIXEL_FEATURE_KEYS)  # 5 features básicos
                        logger.info(f"Inferido pixel_feature_dim={pixel_feature_dim} desde test_pixel_features (5 features básicos)")
                    else:
                        logger.warning(f"Número inesperado de features de píxeles: {num_keys}. Usando 10 por defecto.")
                        pixel_feature_dim = 10
                elif self.train_pixel_features is not None:
                    num_keys = len(self.train_pixel_features.keys())
                    if num_keys == len(CALIB_PIXEL_FEATURE_KEYS):
                        pixel_feature_dim = len(CALIB_PIXEL_FEATURE_KEYS)  # 12 features extendidos
                        logger.info(f"Inferido pixel_feature_dim={pixel_feature_dim} desde train_pixel_features (12 features extendidos)")
                    elif num_keys == len(PIXEL_FEATURE_KEYS):
                        pixel_feature_dim = len(PIXEL_FEATURE_KEYS)  # 5 features básicos
                        logger.info(f"Inferido pixel_feature_dim={pixel_feature_dim} desde train_pixel_features (5 features básicos)")
                    else:
                        logger.warning(f"Número inesperado de features de píxeles: {num_keys}. Usando 10 por defecto.")
                        pixel_feature_dim = 10
                else:
                    # Fallback: usar 10 por defecto (pero advertir)
                    pixel_feature_dim = 10
                    logger.warning(
                        f"No se pudo detectar pixel_feature_dim. Usando default={pixel_feature_dim}. "
                        f"Si el modelo fue entrenado con 12 features, esto causará un error de size mismatch."
                    )
        
        # Crear modelo con el pixel_feature_dim detectado
        model = create_model(
            model_type=self.config['model_type'], num_outputs=4, pretrained=False,
            multi_head=self.is_multi_head, hybrid=self.is_hybrid,
            use_pixel_features=self.use_pixel_features,
            pixel_feature_dim=pixel_feature_dim  # CRÍTICO: pasar pixel_feature_dim detectado
        )
        
        model.load_state_dict(checkpoint['model_state_dict'])
        
        evaluator = RegressionEvaluator(
            model=model, test_loader=self.test_loader,
            scalers=self.scalers, device=self.device
        )
        
        results = evaluator.evaluate_multi_head_model(denormalize=True)
        return {'multihead': results}

    def save_scalers(self) -> None:
        """Guarda los escaladores."""
        if self.scalers is None:
            logger.warning("No hay escaladores para guardar")
            return
        
        save_scalers(self.scalers)
        logger.info("Escaladores guardados")
    
    def _verify_artifacts_saved(self) -> None:
        """Verifica que todos los artefactos se guardaron correctamente."""
        logger.info("Verificando que todos los artefactos se guardaron correctamente...")
        artifacts_dir = get_regressors_artifacts_dir()
        missing_files = []

        if self.is_multi_head or self.is_hybrid:
            model_name = "hybrid.pt" if self.is_hybrid else "multihead.pt"
            model_path = artifacts_dir / model_name
            if not model_path.exists():
                missing_files.append(f"Modelo {model_name}: {model_path}")
            elif model_path.stat().st_size == 0:
                missing_files.append(f"Modelo {model_name} está vacío: {model_path}")
        
        for target in TARGETS:
            scaler_path = artifacts_dir / f"{target}_scaler.pkl"
            if not scaler_path.exists():
                missing_files.append(f"Escalador {target}: {scaler_path}")
            elif scaler_path.stat().st_size == 0:
                missing_files.append(f"Escalador {target} está vacío: {scaler_path}")
        
        if missing_files:
            error_msg = f"[ERROR] Archivos faltantes o vacos: {missing_files}"
            logger.error(error_msg)
            raise IOError(error_msg)
        else:
            logger.info("[OK] Todos los artefactos se guardaron correctamente")
            
            # Mostrar resumen de archivos guardados
            # Calcular tamaño total según el tipo de modelo
            if self.is_multi_head or self.is_hybrid:
                # Modelo híbrido o multi-head: solo hay un archivo de modelo
                model_name = "hybrid.pt" if self.is_hybrid else "multihead.pt"
                model_path = artifacts_dir / model_name
                model_size = model_path.stat().st_size
                
                # Sumar tamaños de escaladores (4 escaladores)
                scaler_size = sum(
                    (artifacts_dir / f"{target}_scaler.pkl").stat().st_size
                    for target in TARGETS
                )
                
                total_size = model_size + scaler_size
                total_files = 1 + len(TARGETS)  # 1 modelo + 4 escaladores
                logger.info(f"[OK] Total de artefactos guardados: {total_files} archivos, {total_size / 1024 / 1024:.2f} MB")
                logger.info(f"  - Modelo: {model_name} ({model_size / 1024 / 1024:.2f} MB)")
                logger.info(f"  - Escaladores: {len(TARGETS)} archivos ({scaler_size / 1024 / 1024:.2f} MB)")
            else:
                # Modelos individuales: un archivo por target
                total_size = sum(
                    (artifacts_dir / f"{target}.pt").stat().st_size + 
                    (artifacts_dir / f"{target}_scaler.pkl").stat().st_size
                    for target in TARGETS
                )
                logger.info(f"[OK] Total de artefactos guardados: {len(TARGETS) * 2} archivos, {total_size / 1024 / 1024:.2f} MB")
    
    def generate_reports(self, evaluation_results: Dict, save_dir: Optional[Path] = None) -> None:
        """
        Genera reportes y gráficos.
        
        Args:
            evaluation_results: Resultados de evaluación
            save_dir: Directorio para guardar reportes
        """
        if save_dir is None:
            save_dir = get_artifacts_dir() / "reports"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = save_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        native_results = json.loads(pd.Series(evaluation_results).to_json(default_handler=str))
        
        save_json(native_results, report_path)
        logger.info(f"Reporte guardado en {report_path}")
    
    def run_incremental_training(self, new_data: List[Dict], target: str = "alto") -> Dict:
        """
        Ejecuta entrenamiento incremental con nuevos datos.
        
        Args:
            new_data: Nuevos datos para entrenamiento incremental
            target: Target específico a entrenar
            
        Returns:
            Resultados del entrenamiento incremental
        """
        logger.info(f"Iniciando entrenamiento incremental para {target}")
        
        # Configuración para entrenamiento incremental
        incremental_config = {
            'strategy_type': 'elastic_weight_consolidation',
            'learning_rate': self.config.get('learning_rate', 1e-5),  # REDUCIDO de 1e-4 a 1e-5
            'epochs': self.config.get('incremental_epochs', 20),
            'batch_size': self.config.get('batch_size', 16),
            'ewc_lambda': self.config.get('ewc_lambda', 1000.0),
            'replay_ratio': self.config.get('replay_ratio', 0.3),
            'img_size': self.config.get('img_size', 224),
            'num_workers': self.config.get('num_workers', 2),
            'weight_decay': self.config.get('weight_decay', 1e-4),
            'min_lr': self.config.get('min_lr', 1e-6)
        }
        
        # Ejecutar entrenamiento incremental
        results = run_incremental_training(new_data, incremental_config, target)
        
        logger.info(f"Entrenamiento incremental completado para {target}")
        return results
    
    def get_incremental_status(self) -> Dict:
        """
        Obtiene el estado del sistema de entrenamiento incremental.
        
        Returns:
            Estado del sistema incremental
        """
        try:
            from ml.regression.incremental_train import IncrementalDataManager, IncrementalModelManager
            
            data_manager = IncrementalDataManager()
            model_manager = IncrementalModelManager()
            
            return {
                "data_versions": data_manager.list_versions(),
                "model_versions": model_manager.list_model_versions(),
                "current_data_version": data_manager.current_version,
                "current_model_version": model_manager.current_version,
                "total_data_samples": data_manager.dataset_metadata.get("total_samples", 0),
                "best_performance": model_manager.model_metadata.get("best_performance", {})
            }
        except Exception as e:
            logger.error(f"Error obteniendo estado incremental: {e}")
            return {
                "error": str(e),
                "status": "not_available"
            }
    
    def run_pipeline(self, multi_head: bool = False) -> Dict[str, Union[Dict, List]]:
        """
        Ejecuta el pipeline completo.
        """
        logger.info("=== INICIANDO PIPELINE DE ENTRENAMIENTO MEJORADO ===")
        start_time = time.time()
        
        # Si está activado el modo de entrenamiento por dimensión separada
        if self.config.get('train_separate_dimensions', False):
            return self._run_separate_dimensions_pipeline()
        
        try:
            logger.info("="*60)
            logger.info("PASO 1: Cargando y validando dataset...")
            image_paths, targets_original, pixel_features = self.load_data()
            
            logger.info("="*60)
            logger.info("PASO 2: Preparando escaladores...")
            targets_df = pd.DataFrame(targets_original)
            self.scalers = create_scalers_from_data(targets_df, scaler_type="standard")
            logger.info("Escaladores preparados")
            
            # 3. Normalizar targets antes de crear splits
            logger.info("Paso 3: Normalizando targets...")
            # Usar el mismo DataFrame para transformar (mayor consistencia)
            normalized_targets_df = self.scalers.transform(targets_df)
            # Convertir de vuelta a diccionario de arrays 1D para compatibilidad
            normalized_targets = {target: normalized_targets_df[target] for target in TARGETS}
            logger.info("Targets normalizados")
            
            # 4. Crear splits con targets normalizados
            logger.info("Paso 4: Creando splits de datos...")
            (
                train_images,
                val_images,
                test_images,
                train_targets,
                val_targets,
                test_targets,
                train_pixel_features,
                val_pixel_features,
                test_pixel_features,
            ) = self.create_stratified_split(
                image_paths, normalized_targets, pixel_features
            )
            
            logger.info(f"Splits creados - Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")
            
            # Guardar splits para evaluacin posterior (valores originales sin normalizar)
            self.train_images = train_images
            self.val_images = val_images
            self.test_images = test_images
            
            # Guardar targets originales sin normalizar para evaluacin
            train_images_indices = [image_paths.index(img) for img in train_images]
            val_images_indices = [image_paths.index(img) for img in val_images]
            test_images_indices = [image_paths.index(img) for img in test_images]
            
            self.train_targets_original = {t: targets_original[t][train_images_indices] for t in TARGETS}
            self.val_targets_original = {t: targets_original[t][val_images_indices] for t in TARGETS}
            self.test_targets_original = {t: targets_original[t][test_images_indices] for t in TARGETS}
            
            # Guardar targets normalizados para usar en datasets
            self.train_targets = train_targets
            self.val_targets = val_targets
            self.test_targets = test_targets
            
            # Guardar pixel_features para usar en datasets
            self.pixel_features = pixel_features
            self.train_pixel_features = train_pixel_features
            self.val_pixel_features = val_pixel_features
            self.test_pixel_features = test_pixel_features
            
            # 5. Crear data loaders
            self.create_data_loaders(
                self.train_images, self.val_images, self.test_images,
                self.train_targets, self.val_targets, self.test_targets,
                self.train_pixel_features, self.val_pixel_features, self.test_pixel_features
            )
            
            logger.info("="*60)
            logger.info("PASO 6: Entrenando modelos...")
            training_histories = self.train_models()
            
            logger.info("="*60)
            logger.info("PASO 7: Guardando escaladores...")
            self.save_scalers()
            
            logger.info("="*60)
            logger.info("PASO 8: Verificando artefactos guardados...")
            self._verify_artifacts_saved()
            
            logger.info("="*60)
            logger.info("PASO 9: Evaluando modelos con conjunto de prueba...")
            evaluation_results = self.evaluate_models()
            
            logger.info("="*60)
            logger.info("PASO 10: Generando reportes...")
            self.generate_reports(evaluation_results)
            
            total_time = time.time() - start_time
            logger.info(f"=== PIPELINE COMPLETADO EN {total_time:.2f}s ===")
            
            return {
                'training_histories': training_histories,
                'evaluation_results': evaluation_results,
                'total_time': total_time,
                'config': self.config
            }
            
        except ValueError as e:
            logger.error(f"Error de validación en pipeline: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fatal en pipeline: {e}", exc_info=True)
            raise

    def _run_separate_dimensions_pipeline(self) -> Dict[str, Union[Dict, List]]:
        """
        Ejecuta el pipeline entrenando cada dimensión por separado.
        Cada dimensión usa sus propios datos de pixel_calibration.json.
        """
        logger.info("=== INICIANDO PIPELINE DE ENTRENAMIENTO POR DIMENSIÓN SEPARADA ===")
        start_time = time.time()
        
        try:
            # 1. Cargar datos con pixel_calibration.json
            logger.info("PASO 1: Cargando datos con pixel_calibration.json...")
            image_paths, targets_original, pixel_features = self.load_data()
            
            # Verificar que tenemos los datos de calibración necesarios
            if self.single_dim_real_dimensions is None or self.single_dim_pixel_features is None:
                raise ValueError(
                    "train_separate_dimensions requiere pixel_calibration.json completo. "
                    "Ejecuta primero: python manage.py calibrate_dataset_pixels"
                )
            
            results = {}
            training_histories = {}
            evaluation_results = {}
            
            # 2. Entrenar cada dimensión por separado
            for dim_name, dim_key in [
                ('alto', 'alto_mm'),
                ('ancho', 'ancho_mm'),
                ('grosor', 'grosor_mm'),
                ('peso', 'peso_g')
            ]:
                logger.info(f"\n{'='*60}")
                logger.info(f"ENTRENANDO MODELO PARA: {dim_name.upper()}")
                logger.info(f"{'='*60}")
                
                # Extraer targets y features para esta dimensión
                dim_targets = self.single_dim_real_dimensions[dim_key]
                dim_pixel_features = self.single_dim_pixel_features
                
                # Crear escalador solo para esta dimensión
                from sklearn.preprocessing import StandardScaler
                target_scaler = StandardScaler()
                dim_targets_scaled = target_scaler.fit_transform(dim_targets.reshape(-1, 1)).flatten()
                
                # Crear split estratificado para esta dimensión
                from sklearn.model_selection import train_test_split
                train_idx, test_idx = train_test_split(
                    range(len(image_paths)),
                    test_size=0.2,
                    random_state=42,
                    stratify=pd.qcut(dim_targets, q=min(5, len(dim_targets)//10), duplicates='drop') if len(dim_targets) > 10 else None
                )
                train_idx, val_idx = train_test_split(
                    train_idx,
                    test_size=0.1/(1-0.2),
                    random_state=42
                )
                
                # Preparar datos para esta dimensión
                train_images_dim = [image_paths[i] for i in train_idx]
                val_images_dim = [image_paths[i] for i in val_idx]
                test_images_dim = [image_paths[i] for i in test_idx]
                
                train_targets_dim = dim_targets_scaled[train_idx]
                val_targets_dim = dim_targets_scaled[val_idx]
                test_targets_dim = dim_targets_scaled[test_idx]
                
                # Preparar features de píxeles extendidos
                pixel_features_matrix = np.array([
                    [dim_pixel_features[k][i] for k in CALIB_PIXEL_FEATURE_KEYS]
                    for i in range(len(image_paths))
                ])
                
                train_pixel_features_dim = pixel_features_matrix[train_idx]
                val_pixel_features_dim = pixel_features_matrix[val_idx]
                test_pixel_features_dim = pixel_features_matrix[test_idx]
                
                # Preparar metadata
                metadata = self.single_dim_metadata
                train_metadata_dim = [metadata[i] for i in train_idx]
                val_metadata_dim = [metadata[i] for i in val_idx]
                test_metadata_dim = [metadata[i] for i in test_idx]
                
                # Crear datasets
                from ..regression.augmentation import create_advanced_train_transform, create_advanced_val_transform
                train_transform = create_advanced_train_transform(self.config['img_size'])
                val_transform = create_advanced_val_transform(self.config['img_size'])
                
                train_dataset = SingleDimensionDataset(
                    train_images_dim,
                    train_targets_dim,
                    train_transform,
                    train_pixel_features_dim,
                    train_metadata_dim
                )
                val_dataset = SingleDimensionDataset(
                    val_images_dim,
                    val_targets_dim,
                    val_transform,
                    val_pixel_features_dim,
                    val_metadata_dim
                )
                test_dataset = SingleDimensionDataset(
                    test_images_dim,
                    test_targets_dim,
                    val_transform,
                    test_pixel_features_dim,
                    test_metadata_dim
                )
                
                # Crear data loaders
                is_windows = platform.system() == 'Windows'
                num_workers = 0 if is_windows else self.config.get('num_workers', 0)
                
                train_loader = DataLoader(
                    train_dataset,
                    batch_size=self.config['batch_size'],
                    shuffle=True,
                    num_workers=num_workers,
                    pin_memory=(not is_windows) and (self.device.type == 'cuda'),
                    drop_last=True
                )
                val_loader = DataLoader(
                    val_dataset,
                    batch_size=self.config['batch_size'] * 2,
                    shuffle=False,
                    num_workers=num_workers,
                    pin_memory=(not is_windows) and (self.device.type == 'cuda')
                )
                test_loader = DataLoader(
                    test_dataset,
                    batch_size=self.config['batch_size'] * 2,
                    shuffle=False,
                    num_workers=num_workers,
                    pin_memory=(not is_windows) and (self.device.type == 'cuda')
                )
                
                # Crear modelo híbrido para esta dimensión
                model = create_model(
                    model_type='hybrid',
                    num_outputs=1,
                    pretrained=self.config.get('pretrained', True),
                    dropout_rate=self.config.get('dropout_rate', 0.2),
                    multi_head=False,
                    hybrid=True,
                    use_pixel_features=True,
                    pixel_feature_dim=len(CALIB_PIXEL_FEATURE_KEYS)
                )
                
                # Crear escaladores para esta dimensión
                from ml.regression.scalers import CacaoScalers
                dim_scalers = CacaoScalers()
                dim_scalers.scalers = {dim_name: target_scaler}
                
                # Entrenar modelo
                logger.info(f"Entrenando modelo para {dim_name}...")
                history = train_single_model(
                    model=model,
                    train_loader=train_loader,
                    val_loader=val_loader,
                    scalers=dim_scalers,
                    target=dim_name,
                    config=self.config,
                    device=self.device
                )
                training_histories[dim_name] = history
                
                # Guardar escalador específico para esta dimensión
                from ml.regression.scalers import save_scalers
                save_scalers(dim_scalers)
                
                # Evaluar modelo
                logger.info(f"Evaluando modelo para {dim_name}...")
                from ml.regression.evaluate import RegressionEvaluator
                evaluator = RegressionEvaluator(
                    model=model,
                    test_loader=test_loader,
                    scalers=dim_scalers,
                    device=self.device
                )
                dim_results = evaluator.evaluate_single_model(dim_name, denormalize=True)
                evaluation_results[dim_name] = dim_results
                
                logger.info(f"✅ Modelo para {dim_name} completado")
                logger.info(f"   MAE: {dim_results['mae']:.4f}, RMSE: {dim_results['rmse']:.4f}, R²: {dim_results['r2']:.4f}")
            
            total_time = time.time() - start_time
            logger.info(f"\n=== PIPELINE POR DIMENSIÓN SEPARADA COMPLETADO EN {total_time:.2f}s ===")
            
            return {
                'training_histories': training_histories,
                'evaluation_results': evaluation_results,
                'total_time': total_time,
                'config': self.config
            }
            
        except Exception as e:
            logger.error(f"Error en pipeline por dimensión separada: {e}", exc_info=True)
            raise

    def _generate_crops_for_missing(self, missing_records: List[Dict]) -> List[Dict]:
        """
        Genera crops solo para los registros que no tienen crops.
        
        Args:
            missing_records: Lista de registros que no tienen crops
            
        Returns:
            Lista de registros con crops generados exitosamente
        """
        logger.info(f"[INICIO] Generando crops para {len(missing_records)} imgenes faltantes...")
        
        from pathlib import Path
        from PIL import Image
        import os
        
        # Crear directorio de crops si no existe
        crops_dir = Path("media/cacao_images/crops")
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        crop_records = []
        successful = 0
        failed = 0
        
        for i, record in enumerate(missing_records):
            try:
                image_id = record['id']
                image_path = Path(record['image_path'])
                crop_path = Path(record['crop_image_path'])
                
                # Verificar si la imagen original existe
                if not image_path.exists():
                    logger.warning(f"Imagen original no existe: {image_path}")
                    failed += 1
                    continue
                
                # Verificar si el crop ya existe (doble verificación)
                if crop_path.exists():
                    logger.debug(f"Crop ya existe (saltando): {crop_path}")
                    crop_records.append(record)
                    successful += 1
                    continue
                
                # Generar crop simple (redimensionar imagen original)
                img = Image.open(image_path)
                img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
                img_resized.save(crop_path, "PNG")
                
                logger.debug(f"Crop generado: {crop_path}")
                crop_records.append(record)
                successful += 1
                
                # Log de progreso cada 10 imágenes
                if (i + 1) % 10 == 0:
                    logger.info(f"Generados {i + 1}/{len(missing_records)} crops faltantes...")
                    
            except Exception as e:
                logger.error(f"Error generando crop para ID {record['id']}: {e}")
                failed += 1
        
        logger.info(f"[OK] Generacin de crops faltantes completada: {successful} exitosos, {failed} fallidos")
        return crop_records
    
    def _generate_crops_automatically(self, valid_records: List[Dict]) -> List[Dict]:
        """
        Genera crops automáticamente para los registros válidos (método legacy).
        
        Args:
            valid_records: Lista de registros válidos
            
        Returns:
            Lista de registros con crops generados
        """
        logger.info("[INICIO] Generando crops automticamente (mtodo legacy)...")
        
        from pathlib import Path
        from PIL import Image
        import os
        
        # Crear directorio de crops si no existe
        crops_dir = Path("media/cacao_images/crops")
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        crop_records = []
        successful = 0
        failed = 0
        
        for i, record in enumerate(valid_records):
            try:
                image_id = record['id']
                image_path = Path(record['image_path'])
                crop_path = Path(record['crop_image_path'])
                
                # Verificar si la imagen original existe
                if not image_path.exists():
                    logger.warning(f"Imagen original no existe: {image_path}")
                    failed += 1
                    continue
                
                # Verificar si el crop ya existe
                if crop_path.exists() and not self.config.get('overwrite', False):
                    logger.debug(f"Crop ya existe: {crop_path}")
                    crop_records.append(record)
                    successful += 1
                    continue
                
                # Generar crop simple (redimensionar imagen original)
                img = Image.open(image_path)
                img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
                img_resized.save(crop_path, "PNG")
                
                logger.debug(f"Crop generado: {crop_path}")
                crop_records.append(record)
                successful += 1
                
                # Log de progreso cada 50 imágenes
                if (i + 1) % 50 == 0:
                    logger.info(f"Generados {i + 1}/{len(valid_records)} crops...")
                    
            except Exception as e:
                logger.error(f"Error generando crop para ID {record['id']}: {e}")
                failed += 1
        
        logger.info(f"[OK] Generacin de crops completada: {successful} exitosos, {failed} fallidos")
        return crop_records


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Pipeline de entrenamiento para modelos de cacao')
    
    # Argumentos del modelo
    parser.add_argument('--multihead', type=str, default='false', choices=['true', 'false'],
                       help='Usar modelo multi-head (default: false)')
    parser.add_argument('--model-type', type=str, default='resnet18', choices=['resnet18', 'convnext_tiny'],
                       help='Tipo de modelo (default: resnet18)')
    
    # Argumentos de entrenamiento
    parser.add_argument('--epochs', type=int, default=50,
                       help='Número de épocas (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Tamaño de batch (default: 32)')
    parser.add_argument('--img-size', type=int, default=224,
                       help='Tamaño de imagen (default: 224)')
    parser.add_argument('--learning-rate', type=float, default=1e-5,
                       help='Learning rate (default: 1e-5, reducido para estabilidad con Uncertainty Loss)')
    
    # Argumentos adicionales
    parser.add_argument('--num-workers', type=int, default=2,
                       help='Número de workers para data loading (default: 2)')
    parser.add_argument('--early-stopping-patience', type=int, default=10,
                       help='Paciencia para early stopping (default: 10)')
    
    # Nuevo argumento para entrenamiento por dimensión separada
    parser.add_argument(
        '--train-separate-dimensions',
        action='store_true',
        help='Entrenar cada dimensión (alto, ancho, grosor, peso) por separado usando pixel_calibration.json'
    )
    
    args = parser.parse_args()
    
    # Crear configuración
    config = {
        'multi_head': args.multihead.lower() == 'true',
        'model_type': args.model_type,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'img_size': args.img_size,
        'learning_rate': args.learning_rate,
        'num_workers': args.num_workers,
        'early_stopping_patience': args.early_stopping_patience,
        'pretrained': True,
        'dropout_rate': 0.2,
        'weight_decay': 1e-4,
        'min_lr': 1e-6,
        'train_separate_dimensions': args.train_separate_dimensions,
    }
    
    # Crear y ejecutar pipeline
    pipeline = CacaoTrainingPipeline(config)
    results = pipeline.run_pipeline(config['multi_head'])
    
    print("Pipeline completado exitosamente!")
    print(f"Tiempo total: {results['total_time']:.2f}s")
    
    # Mostrar resultados de evaluación
    if 'evaluation_results' in results:
        eval_results = results['evaluation_results']
        print("\n=== RESULTADOS DE EVALUACIÓN ===")
        
        if config['multi_head'] and 'multihead' in eval_results:
            multihead_results = eval_results['multihead']
            for target in TARGETS:
                if target in multihead_results:
                    metrics = multihead_results[target]
                    print(f"{target.upper()}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
        else:
            for target in TARGETS:
                if target in eval_results:
                    metrics = eval_results[target]
                    print(f"{target.upper()}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")


def run_training_pipeline(
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 1e-5,  # REDUCIDO de 1e-4 a 1e-5 para estabilidad con Uncertainty Loss
    multi_head: bool = False,
    model_type: str = 'resnet18',
    img_size: int = 224,
    early_stopping_patience: int = 10,
    save_best_only: bool = True,
    **kwargs
) -> bool:
    """
    Función para ejecutar el pipeline de entrenamiento desde otros módulos.
    
    Args:
        epochs: Número de épocas
        batch_size: Tamaño de batch
        learning_rate: Learning rate
        multi_head: Si usar modelo multi-head
        model_type: Tipo de modelo
        img_size: Tamaño de imagen
        early_stopping_patience: Paciencia para early stopping
        save_best_only: Solo guardar el mejor modelo
        
    Returns:
        bool: True si el entrenamiento fue exitoso, False en caso contrario
    """
    try:
        logger.info("[INICIO] Iniciando pipeline de entrenamiento...")
        
        # Detectar Windows y ajustar num_workers automticamente (multiprocessing en Windows causa MemoryError)
        is_windows = platform.system() == 'Windows'
        default_num_workers = 0 if is_windows else 2
        
        # Determinar si es modelo híbrido
        is_hybrid = kwargs.get('hybrid', False) or model_type == 'hybrid'
        
        # Crear configuracin mejorada con todas las optimizaciones avanzadas
        config = {
            'multi_head': multi_head or is_hybrid,
            'model_type': model_type,
            'hybrid': is_hybrid,
            'use_pixel_features': kwargs.get('use_pixel_features', False) and is_hybrid,
            'use_raw_images': kwargs.get('use_raw_images', False),
            'segmentation_backend': kwargs.get('segmentation_backend', 'auto'),
            'epochs': epochs,
            'batch_size': batch_size,
            'img_size': img_size,
            'learning_rate': learning_rate,
            'num_workers': default_num_workers,
            'early_stopping_patience': early_stopping_patience,
            'pretrained': True,
            'dropout_rate': 0.2,
            'weight_decay': 1e-4,
            'min_lr': 1e-7,
            'save_best_only': save_best_only,
            'scheduler_type': 'cosine_warmup',
            'warmup_epochs': 5,
            'loss_type': 'huber',  # 'mse', 'huber', 'smooth_l1' - Huber es ms robusto a outliers
            'max_grad_norm': 1.0,  # Gradient clipping para estabilidad
            'use_amp': False,  # Mixed precision (requiere GPU NVIDIA)
            'use_advanced_augmentation': True,  # Usar augmentation avanzado
            'improvement_threshold': 1e-4,  # Umbral mnimo de mejora para early stopping
        }
        
        pipeline = CacaoTrainingPipeline(config)
        results = pipeline.run_pipeline()
        
        logger.info("[OK] Pipeline de entrenamiento completado exitosamente!")
        logger.info(f"Tiempo total: {results['total_time']:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Error en pipeline de entrenamiento: {e}", exc_info=True)
        return False


def run_incremental_training_pipeline(
    new_data: List[Dict],
    target: str = "alto",
    epochs: int = 20,
    batch_size: int = 16,
    learning_rate: float = 1e-5,  # REDUCIDO de 1e-4 a 1e-5 para estabilidad
    strategy_type: str = "elastic_weight_consolidation",
    ewc_lambda: float = 1000.0,
    replay_ratio: float = 0.3
) -> bool:
    """
    Función para ejecutar entrenamiento incremental desde otros módulos.
    
    Args:
        new_data: Nuevos datos para entrenamiento
        target: Target específico a entrenar
        epochs: Número de épocas para entrenamiento incremental
        batch_size: Tamaño de batch
        learning_rate: Learning rate
        strategy_type: Estrategia de aprendizaje incremental
        ewc_lambda: Peso del término EWC
        replay_ratio: Proporción de datos de replay
        
    Returns:
        bool: True si el entrenamiento fue exitoso, False en caso contrario
    """
    try:
        logger.info("[INICIO] Iniciando entrenamiento incremental...")
        
        # Configuración para entrenamiento incremental
        config = {
            'strategy_type': strategy_type,
            'learning_rate': learning_rate,
            'epochs': epochs,
            'batch_size': batch_size,
            'ewc_lambda': ewc_lambda,
            'replay_ratio': replay_ratio,
            'img_size': 224,
            'num_workers': 0 if platform.system() == 'Windows' else 2,
            'weight_decay': 1e-4,
            'min_lr': 1e-6
        }
        
        # Ejecutar entrenamiento incremental
        results = run_incremental_training(new_data, config, target)
        
        logger.info("[OK] Entrenamiento incremental completado exitosamente!")
        logger.info(f"Modelo versin: {results['model_version']}")
        logger.info(f"Mtricas de rendimiento: {results['performance_metrics']}")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Error en entrenamiento incremental: {e}")
        return False


def get_incremental_training_status() -> Dict:
    """
    Obtiene el estado del sistema de entrenamiento incremental.
    
    Returns:
        Estado del sistema incremental
    """
    try:
        from ml.regression.incremental_train import IncrementalDataManager, IncrementalModelManager
        
        data_manager = IncrementalDataManager()
        model_manager = IncrementalModelManager()
        
        return {
            "data_versions": data_manager.list_versions(),
            "model_versions": model_manager.list_model_versions(),
            "current_data_version": data_manager.current_version,
            "current_model_version": model_manager.current_version,
            "total_data_samples": data_manager.dataset_metadata.get("total_samples", 0),
            "best_performance": model_manager.model_metadata.get("best_performance", {}),
            "status": "available"
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado incremental: {e}")
        return {
            "error": str(e),
            "status": "not_available"
        }


if __name__ == "__main__":
    main()