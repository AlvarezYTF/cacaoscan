"""
DataLoader mejorado para CacaoScan con validaciones y normalización robusta.

Características:
- Validación de formato de imágenes (RGB, normalización ImageNet)
- Verificación de mezclas entre .bmp y .png
- Labels en orden correcto: [alto, ancho, grosor, peso]
- Normalización de targets integrada
- Funciones para revertir normalización
- Validación automática de estructura de datos
"""
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from PIL import Image
import torchvision.transforms as transforms
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging

from ..utils.logs import get_ml_logger
from .dataset_loader import CacaoDatasetLoader

logger = get_ml_logger("cacaoscan.ml.data.dataloader")


class TargetNormalizer:
    """
    Normalizador de targets con funciones para normalizar y desnormalizar.
    """
    
    def __init__(self, scaler_type: str = "standard"):
        """
        Args:
            scaler_type: Tipo de escalador ("standard" o "minmax")
        """
        self.scaler_type = scaler_type
        self.scalers: Dict[str, Union[StandardScaler, MinMaxScaler]] = {}
        self.is_fitted = False
        self.target_order = ["alto", "ancho", "grosor", "peso"]
    
    def fit(self, targets: Dict[str, np.ndarray]) -> None:
        """
        Ajusta los escaladores a los datos de entrenamiento.
        
        Args:
            targets: Diccionario con arrays de targets {target: array}
        """
        logger.info(f"Ajustando normalizadores {self.scaler_type} para targets")
        
        for target in self.target_order:
            if target not in targets:
                raise ValueError(f"Target '{target}' no encontrado en datos")
            
            target_array = np.array(targets[target])
            if target_array.ndim == 1:
                target_array = target_array.reshape(-1, 1)
            
            if self.scaler_type == "standard":
                scaler = StandardScaler()
            else:  # minmax
                scaler = MinMaxScaler()
            
            scaler.fit(target_array)
            self.scalers[target] = scaler
            
            if hasattr(scaler, 'mean_'):
                logger.debug(
                    f"Escalador ajustado para {target}: "
                    f"mean={scaler.mean_[0]:.3f}, std={scaler.scale_[0]:.3f}"
                )
            else:
                logger.debug(
                    f"Escalador ajustado para {target}: "
                    f"min={scaler.data_min_[0]:.3f}, max={scaler.data_max_[0]:.3f}"
                )
        
        self.is_fitted = True
        logger.info("Normalizadores ajustados exitosamente")
    
    def normalize(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Normaliza los targets.
        
        Args:
            targets: Diccionario con arrays de targets
            
        Returns:
            Diccionario con targets normalizados
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben ser ajustados antes de normalizar")
        
        normalized = {}
        for target in self.target_order:
            if target not in targets:
                raise ValueError(f"Target '{target}' no encontrado")
            
            target_array = np.array(targets[target])
            if target_array.ndim == 1:
                target_array = target_array.reshape(-1, 1)
            
            normalized_array = self.scalers[target].transform(target_array)
            normalized[target] = normalized_array.flatten()
        
        return normalized
    
    def denormalize(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Desnormaliza los targets.
        
        Args:
            targets: Diccionario con arrays de targets normalizados
            
        Returns:
            Diccionario con targets en escala original
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben ser ajustados antes de desnormalizar")
        
        denormalized = {}
        for target in self.target_order:
            if target not in targets:
                raise ValueError(f"Target '{target}' no encontrado")
            
            target_array = np.array(targets[target])
            if target_array.ndim == 1:
                target_array = target_array.reshape(-1, 1)
            
            denormalized_array = self.scalers[target].inverse_transform(target_array)
            denormalized[target] = denormalized_array.flatten()
        
        return denormalized
    
    def normalize_single(self, target_name: str, value: float) -> float:
        """
        Normaliza un único valor de target.
        
        Args:
            target_name: Nombre del target
            value: Valor a normalizar
            
        Returns:
            Valor normalizado
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben ser ajustados antes de normalizar")
        
        if target_name not in self.scalers:
            raise ValueError(f"Target '{target_name}' no encontrado en normalizadores")
        
        value_array = np.array([[value]])
        normalized = self.scalers[target_name].transform(value_array)
        return float(normalized[0, 0])
    
    def denormalize_single(self, target_name: str, value: float) -> float:
        """
        Desnormaliza un único valor de target.
        
        Args:
            target_name: Nombre del target
            value: Valor normalizado a desnormalizar
            
        Returns:
            Valor en escala original
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben ser ajustados antes de desnormalizar")
        
        if target_name not in self.scalers:
            raise ValueError(f"Target '{target_name}' no encontrado en normalizadores")
        
        value_array = np.array([[value]])
        denormalized = self.scalers[target_name].inverse_transform(value_array)
        return float(denormalized[0, 0])


def normalize_targets(
    targets: Dict[str, np.ndarray],
    scaler_type: str = "standard"
) -> Tuple[Dict[str, np.ndarray], TargetNormalizer]:
    """
    Normaliza targets y retorna el normalizador.
    
    Args:
        targets: Diccionario con arrays de targets
        scaler_type: Tipo de escalador ("standard" o "minmax")
        
    Returns:
        Tuple de (targets normalizados, normalizador)
    """
    normalizer = TargetNormalizer(scaler_type=scaler_type)
    normalizer.fit(targets)
    normalized = normalizer.normalize(targets)
    return normalized, normalizer


def denormalize_predictions(
    predictions: Dict[str, np.ndarray],
    normalizer: TargetNormalizer
) -> Dict[str, np.ndarray]:
    """
    Desnormaliza predicciones usando el normalizador.
    
    Args:
        predictions: Diccionario con arrays de predicciones normalizadas
        normalizer: Normalizador ajustado
        
    Returns:
        Diccionario con predicciones en escala original
    """
    return normalizer.denormalize(predictions)


class ImprovedCacaoDataset(Dataset):
    """
    Dataset mejorado para CacaoScan con validaciones robustas.
    
    Características:
    - Validación de formato de imágenes (RGB, normalización ImageNet)
    - Verificación de mezclas entre .bmp y .png
    - Labels en orden correcto: [alto, ancho, grosor, peso]
    - Normalización de targets integrada
    - Validación automática de estructura de datos
    """
    
    # Orden correcto de targets
    TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        transform: Optional[transforms.Compose] = None,
        pixel_features: Optional[Dict[str, np.ndarray]] = None,
        normalizer: Optional[TargetNormalizer] = None,
        validate_structure: bool = True,
        use_crops: bool = True,
    ):
        """
        Inicializa el dataset mejorado.
        
        Args:
            image_paths: Lista de rutas de imágenes
            targets: Diccionario con arrays de targets {target: array}
            transform: Transformaciones de imagen (debe incluir normalización ImageNet)
            pixel_features: Features de píxeles opcionales
            normalizer: Normalizador de targets (opcional, si None los targets deben estar normalizados)
            validate_structure: Si validar la estructura de datos
            use_crops: Si usar imágenes procesadas (.png) en lugar de raw (.bmp)
        """
        self.image_paths = image_paths
        self.targets = targets
        self.transform = transform
        self.pixel_features = pixel_features
        self.normalizer = normalizer
        self.use_crops = use_crops
        
        # Validar estructura si se solicita
        if validate_structure:
            self._validate_structure()
        
        # Validar que las transformaciones incluyan normalización ImageNet
        if transform is not None:
            self._validate_transform()
        
        logger.info(f"Dataset mejorado inicializado: {len(image_paths)} muestras")
    
    def _validate_structure(self) -> None:
        """Valida la estructura de datos."""
        # Validar longitudes
        n_images = len(self.image_paths)
        n_targets = {k: len(v) for k, v in self.targets.items()}
        
        if not all(n == n_images for n in n_targets.values()):
            raise ValueError(
                f"Longitudes inconsistentes: imágenes={n_images}, targets={n_targets}"
            )
        
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
        
        # Validar pixel_features si están presentes
        if self.pixel_features is not None:
            n_pixel = {k: len(v) for k, v in self.pixel_features.items()}
            if not all(n == n_images for n in n_pixel.values()):
                raise ValueError(
                    f"Longitudes inconsistentes en pixel_features: {n_pixel}"
                )
        
        logger.info("✅ Estructura de datos validada correctamente")
    
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
        
        if self.use_crops:
            if bmp_count > 0:
                logger.warning(
                    f"Dataset configurado para usar crops (.png) pero se encontraron {bmp_count} "
                    f"imágenes .bmp. Esto puede causar problemas."
                )
        else:
            if png_count > 0:
                logger.warning(
                    f"Dataset configurado para usar raw (.bmp) pero se encontraron {png_count} "
                    f"imágenes .png. Esto puede causar problemas."
                )
        
        logger.info(f"Formato de imágenes: {bmp_count} .bmp, {png_count} .png, {other_count} otros")
    
    def _find_normalize_transform(self, transforms_list) -> Optional[transforms.Normalize]:
        """Busca una transformación Normalize en la lista de transformaciones."""
        transform_items = transforms_list.transforms if hasattr(transforms_list, 'transforms') else [transforms_list]
        
        for t in transform_items:
            if isinstance(t, transforms.Compose):
                found = self._find_normalize_transform(t)
                if found is not None:
                    return found
            elif isinstance(t, transforms.Normalize):
                return t
        
        return None
    
    def _validate_normalization_params(self, normalize_transform: transforms.Normalize) -> bool:
        """Valida que los parámetros de normalización coincidan con ImageNet estándar."""
        expected_mean = [0.485, 0.456, 0.406]
        expected_std = [0.229, 0.224, 0.225]
        
        mean_match = all(abs(m - e) < 0.01 for m, e in zip(normalize_transform.mean, expected_mean))
        std_match = all(abs(s - e) < 0.01 for s, e in zip(normalize_transform.std, expected_std))
        
        return mean_match and std_match
    
    def _validate_transform(self) -> None:
        """Valida que las transformaciones incluyan normalización ImageNet."""
        normalize_transform = self._find_normalize_transform(self.transform)
        
        if normalize_transform is None:
            logger.warning(
                "⚠️ Las transformaciones no incluyen normalización ImageNet. "
                "Se recomienda agregar transforms.Normalize con mean=[0.485, 0.456, 0.406], "
                "std=[0.229, 0.224, 0.225]"
            )
            return
        
        if not self._validate_normalization_params(normalize_transform):
            logger.warning(
                f"⚠️ Parámetros de normalización diferentes a ImageNet estándar. "
                f"Esperado: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]. "
                f"Obtenido: mean={normalize_transform.mean}, std={normalize_transform.std}"
            )
        else:
            logger.debug("✅ Normalización ImageNet validada correctamente")
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, ...]:
        """
        Obtiene un item del dataset.
        
        Returns:
            Tuple con:
            - image_tensor: Tensor de imagen normalizada [C, H, W]
            - targets_tensor: Tensor de targets en orden [alto, ancho, grosor, peso]
            - pixel_features (opcional): Tensor de features de píxeles
        """
        # Cargar imagen
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
            
            # Aplicar transformaciones (deben incluir ToTensor y Normalize)
            if self.transform is not None:
                image_tensor = self.transform(image)
            else:
                # Transformación básica si no se proporciona
                transform_basic = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    )
                ])
                image_tensor = transform_basic(image)
            
            # Validar formato del tensor
            if image_tensor.shape[0] != 3:
                raise ValueError(
                    f"Imagen debe tener 3 canales RGB, obtuvo {image_tensor.shape[0]} canales"
                )
            
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            raise
        
        # Obtener targets en orden correcto
        targets_list = [
            float(self.targets[target][idx])
            for target in self.TARGET_ORDER
        ]
        targets_tensor = torch.tensor(targets_list, dtype=torch.float32)
        
        # Si hay pixel_features, agregarlos
        if self.pixel_features is not None:
            # Detectar el formato de pixel_features
            # Caso 1: dict con keys como str(path) -> array (test format)
            image_path_str = str(self.image_paths[idx])
            if image_path_str in self.pixel_features:
                # Features como array directo (10 features según test)
                pixel_feat_array = self.pixel_features[image_path_str]
                if isinstance(pixel_feat_array, np.ndarray):
                    pixel_feat_values = pixel_feat_array.tolist()
                elif isinstance(pixel_feat_array, (list, tuple)):
                    pixel_feat_values = list(pixel_feat_array)
                else:
                    pixel_feat_values = [float(pixel_feat_array)]
                # Asegurar que tenga 10 elementos
                if len(pixel_feat_values) == 10:
                    pixel_feat = torch.tensor(pixel_feat_values, dtype=torch.float32)
                    return image_tensor, targets_tensor, pixel_feat
                elif len(pixel_feat_values) == 5:
                    pixel_feat = torch.tensor(pixel_feat_values, dtype=torch.float32)
                    return image_tensor, targets_tensor, pixel_feat
                else:
                    # Padding o truncar a 10
                    if len(pixel_feat_values) < 10:
                        pixel_feat_values.extend([0.0] * (10 - len(pixel_feat_values)))
                    else:
                        pixel_feat_values = pixel_feat_values[:10]
                    pixel_feat = torch.tensor(pixel_feat_values, dtype=torch.float32)
                    return image_tensor, targets_tensor, pixel_feat
            
            # Caso 2: dict con keys específicos (features extendidos o básicos)
            if all(k in self.pixel_features for k in [
                "grain_area_pixels", "width_pixels", "height_pixels",
                "bbox_area_pixels", "aspect_ratio", "original_total_pixels",
                "background_pixels", "background_ratio", "alto_mm_per_pixel",
                "ancho_mm_per_pixel", "average_mm_per_pixel", "segmentation_confidence"
            ]):
                # Features extendidos (12) - tomar solo los primeros 10 para compatibilidad
                pixel_feat_values = [
                    float(self.pixel_features[key][idx])
                    for key in [
                        "grain_area_pixels", "width_pixels", "height_pixels",
                        "bbox_area_pixels", "aspect_ratio", "original_total_pixels",
                        "background_pixels", "background_ratio", "alto_mm_per_pixel",
                        "ancho_mm_per_pixel"
                    ]
                ]
            elif all(k in self.pixel_features for k in [
                "pixel_width", "pixel_height", "pixel_area", "scale_factor", "aspect_ratio"
            ]):
                # Features básicos (5)
                pixel_feat_values = [
                    float(self.pixel_features["pixel_width"][idx]),
                    float(self.pixel_features["pixel_height"][idx]),
                    float(self.pixel_features["pixel_area"][idx]),
                    float(self.pixel_features["scale_factor"][idx]),
                    float(self.pixel_features["aspect_ratio"][idx]),
                ]
            else:
                # Fallback: intentar obtener features básicos con defaults
                pixel_feat_values = [
                    float(self.pixel_features.get("pixel_width", [0.0] * len(self.image_paths))[idx]),
                    float(self.pixel_features.get("pixel_height", [0.0] * len(self.image_paths))[idx]),
                    float(self.pixel_features.get("pixel_area", [0.0] * len(self.image_paths))[idx]),
                    float(self.pixel_features.get("scale_factor", [0.0] * len(self.image_paths))[idx]),
                    float(self.pixel_features.get("aspect_ratio", [0.0] * len(self.image_paths))[idx]),
                ]
            
            pixel_feat = torch.tensor(pixel_feat_values, dtype=torch.float32)
            return image_tensor, targets_tensor, pixel_feat
        
        return image_tensor, targets_tensor
    
    def get_target_ranges(self) -> Dict[str, Dict[str, float]]:
        """
        Obtiene los rangos (min, max) de cada target.
        
        Returns:
            Diccionario con rangos por target en formato {'min': ..., 'max': ...}
        """
        ranges = {}
        for target in self.TARGET_ORDER:
            values = self.targets[target]
            ranges[target] = {
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }
        return ranges
    
    def validate_with_calibration(
        self,
        calibration_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida que los datos del dataset coincidan con pixel_calibration.json.
        
        Args:
            calibration_data: Datos de pixel_calibration.json
            
        Returns:
            Diccionario con resultados de validación
        """
        calib_by_id = self._build_calibration_map(calibration_data)
        
        matches = 0
        mismatches: List[Dict[str, Union[int, float, str]]] = []
        
        for idx, img_path in enumerate(self.image_paths):
            image_id = self._extract_image_id(img_path)
            if image_id is None or image_id not in calib_by_id:
                continue
            
            record_matches, record_mismatches = self._compare_targets_with_calibration(
                sample_index=idx,
                image_id=image_id,
                calibration_record=calib_by_id[image_id]
            )
            matches += record_matches
            mismatches.extend(record_mismatches)
        
        total_comparisons = matches + len(mismatches)
        match_rate = matches / total_comparisons if total_comparisons > 0 else 0.0
        return {
            "total_matches": matches,
            "total_mismatches": len(mismatches),
            "mismatches": mismatches[:10],  # Primeros 10
            "match_rate": match_rate
        }

    def _build_calibration_map(self, calibration_data: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        """Index calibration records by ID for quick lookup."""
        records = calibration_data.get("calibration_records", [])
        calibration_map: Dict[int, Dict[str, Any]] = {}
        for record in records:
            try:
                record_id = int(record["id"])
            except (KeyError, TypeError, ValueError):
                continue
            calibration_map[record_id] = record
        return calibration_map

    def _extract_image_id(self, img_path: Path) -> Optional[int]:
        """Extract the numeric ID from an image path."""
        try:
            return int(img_path.stem)
        except ValueError:
            logger.warning(f"No se pudo extraer ID de {img_path}")
            return None

    def _compare_targets_with_calibration(
        self,
        *,
        sample_index: int,
        image_id: int,
        calibration_record: Dict[str, Any]
    ) -> Tuple[int, List[Dict[str, Union[int, float, str]]]]:
        """Compare dataset targets against calibration data."""
        matches = 0
        mismatches: List[Dict[str, Union[int, float, str]]] = []
        real_dims = self._as_mapping(calibration_record.get("real_dimensions"))
        
        for target in self.TARGET_ORDER:
            target_key = self._calibration_key_for_target(target)
            if target_key not in real_dims:
                continue
            
            calib_value = float(real_dims[target_key])
            dataset_value = float(self.targets[target][sample_index])
            diff = abs(calib_value - dataset_value)
            if diff > 0.1:
                mismatches.append({
                    "id": image_id,
                    "target": target,
                    "calibration": calib_value,
                    "dataset": dataset_value,
                    "diff": diff
                })
            else:
                matches += 1
        
        return matches, mismatches

    @staticmethod
    def _calibration_key_for_target(target: str) -> str:
        """Return the calibration dictionary key for a dataset target."""
        return f"{target}_g" if target == "peso" else f"{target}_mm"

    @staticmethod
    def _as_mapping(value: Optional[Any]) -> Dict[str, Any]:
        """Return a dictionary representation for nested calibration sections."""
        if isinstance(value, dict):
            return value
        return {}


def create_improved_dataloader(
    image_paths: List[Path],
    targets: Dict[str, np.ndarray],
    transform: Optional[transforms.Compose] = None,
    pixel_features: Optional[Dict[str, np.ndarray]] = None,
    normalizer: Optional[TargetNormalizer] = None,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = False,
    use_crops: bool = True,
    validate_structure: bool = True,
) -> Tuple[DataLoader, Optional[TargetNormalizer]]:
    """
    Crea un DataLoader mejorado con validaciones.
    
    Args:
        image_paths: Lista de rutas de imágenes
        targets: Diccionario con arrays de targets
        transform: Transformaciones de imagen
        pixel_features: Features de píxeles opcionales
        normalizer: Normalizador de targets (opcional)
        batch_size: Tamaño de batch
        shuffle: Si mezclar los datos
        num_workers: Número de workers para carga de datos
        pin_memory: Si usar pin_memory para GPU
        use_crops: Si usar imágenes procesadas (.png)
        validate_structure: Si validar la estructura de datos
        
    Returns:
        Tuple de (DataLoader, normalizador)
    """
    # Crear dataset
    dataset = ImprovedCacaoDataset(
        image_paths=image_paths,
        targets=targets,
        transform=transform,
        pixel_features=pixel_features,
        normalizer=normalizer,
        validate_structure=validate_structure,
        use_crops=use_crops,
    )
    
    # Crear DataLoader
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=num_workers > 0,
        drop_last=shuffle,  # Drop last batch solo en entrenamiento
    )
    
    return dataloader, normalizer

