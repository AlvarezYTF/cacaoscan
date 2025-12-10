"""
DataLoader mejorado para CacaoScan con validaciones y normalización robusta.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: TargetNormalizer, validators, extractors, loaders
- Mantiene compatibilidad hacia atrás con la API original
"""
import torch
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import torchvision.transforms as transforms

from ..utils.logs import get_ml_logger
from .normalizers.target_normalizer import TargetNormalizer
from .conjuntos_datos import DatasetMejorado

logger = get_ml_logger("cacaoscan.ml.data.dataloader")


# Funciones de conveniencia para compatibilidad hacia atrás
def normalize_targets(
    targets: Dict[str, np.ndarray],
    scaler_type: str = "standard"
) -> Tuple[Dict[str, np.ndarray], TargetNormalizer]:
    """
    Normaliza targets y retorna normalizador.
    
    Args:
        targets: Diccionario con arrays de targets
        scaler_type: Tipo de escalador ("standard" o "minmax")
        
    Returns:
        Tupla de (targets normalizados, normalizador)
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
    Desnormaliza predicciones usando normalizador.
    
    Args:
        predictions: Diccionario con arrays de predicciones normalizadas
        normalizer: Normalizador ajustado
        
    Returns:
        Diccionario con predicciones desnormalizadas
    """
    return normalizer.denormalize(predictions)


# Re-export para compatibilidad hacia atrás
ImprovedCacaoDataset = DatasetMejorado


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
        Tupla de (DataLoader, normalizador)
    """
    # Crear dataset
    dataset = DatasetMejorado(
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
