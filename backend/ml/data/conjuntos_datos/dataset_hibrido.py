"""
Dataset híbrido para regresión de cacao con features de píxeles normalizados.

Este módulo maneja la carga de datos para modelos híbridos,
siguiendo el principio de Responsabilidad Única.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms

from ...utils.logs import get_ml_logger
from ..cargadores import CargadorFeaturesPixel
from ..datasets.validators.structure_validator import StructureValidator
from ..datasets.loaders.image_loader import ImageLoader

logger = get_ml_logger("cacaoscan.ml.data.conjuntos_datos")


class DatasetHibrido(Dataset):
    """
    Dataset para modelo híbrido de regresión de cacao.
    
    Retorna:
        tensor_imagen: Tensor de imagen [3, H, W]
        tensor_targets: Tensor de targets [4] en orden: [alto_mm, ancho_mm, grosor_mm, peso_g]
        tensor_pixel: Tensor de features de píxeles [10] en orden: [height_mm_est, width_mm_est, area_mm2_est, perimeter_mm, aspect_ratio, bbox_ratio, background_ratio, avg_mm_per_pixel, compactness, roundness]
    """
    
    ORDEN_TARGETS = ["alto", "ancho", "grosor", "peso"]
    ORDEN_FEATURES_PIXEL = [
        "height_mm_est",
        "width_mm_est",
        "area_mm2_est",
        "perimeter_mm",
        "aspect_ratio",
        "bbox_ratio",
        "background_ratio",
        "avg_mm_per_pixel",
        "compactness",
        "roundness"
    ]
    
    def __init__(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        transform: transforms.Compose,
        pixel_features_loader: Optional[CargadorFeaturesPixel] = None,
        record_ids: Optional[List[int]] = None,
        validate: bool = True
    ):
        """
        Inicializa el dataset híbrido.
        
        Args:
            image_paths: Lista de rutas de imágenes
            targets: Diccionario de arrays de targets {target: array}
            transform: Transformaciones de imagen
            pixel_features_loader: Instancia de PixelFeaturesLoader (opcional)
            record_ids: Lista de IDs de registros correspondientes a image_paths (requerido si pixel_features_loader se proporciona)
            validate: Si validar consistencia de datos
        """
        self.image_paths = image_paths
        self.targets = targets
        self.transform = transform
        self.pixel_features_loader = pixel_features_loader
        self.record_ids = record_ids
        
        # Inicializar validadores y loaders
        self.structure_validator = StructureValidator()
        self.image_loader = ImageLoader(transform)
        
        # Validar estructura
        if validate:
            self._validar_estructura()
        
        logger.info(f"Dataset híbrido inicializado con {len(image_paths)} muestras")
    
    def _validar_estructura(self) -> None:
        """
        Valida consistencia de estructura de datos.
        
        Raises:
            ValueError: Si hay inconsistencias
        """
        # Validar targets
        missing_targets = set(self.ORDEN_TARGETS) - set(self.targets.keys())
        if missing_targets:
            raise ValueError(f"Targets faltantes: {missing_targets}")
        
        # Validar longitudes usando StructureValidator
        self.structure_validator.validate(
            self.image_paths,
            self.targets,
            pixel_features=None  # Features de píxeles se cargan bajo demanda
        )
        
        # Validar features de píxeles si se proporciona loader
        if self.pixel_features_loader is not None:
            if self.record_ids is None:
                raise ValueError("record_ids requerido cuando se proporciona pixel_features_loader")
            
            if len(self.record_ids) != len(self.image_paths):
                raise ValueError(
                    f"Longitudes inconsistentes: imágenes={len(self.image_paths)}, "
                    f"record_ids={len(self.record_ids)}"
                )
            
            # Verificar que todos los registros tengan features de píxeles
            missing_features = []
            for idx, record_id in enumerate(self.record_ids):
                features = self.pixel_features_loader.get_features_by_id(record_id)
                if features is None:
                    missing_features.append((idx, record_id))
            
            if missing_features:
                logger.warning(
                    f"Faltan features de píxeles para {len(missing_features)} registros. "
                    f"Primeros 5: {missing_features[:5]}"
                )
        
        logger.debug("Estructura del dataset validada")
    
    def __len__(self) -> int:
        """
        Retorna el tamaño del dataset.
        
        Returns:
            Número de imágenes
        """
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Obtiene una muestra del dataset.
        
        Args:
            idx: Índice de la muestra
            
        Returns:
            Tupla (tensor_imagen, tensor_targets, tensor_pixel)
        """
        # Cargar imagen usando ImageLoader
        image_path = self.image_paths[idx]
        img_tensor = self.image_loader.load(image_path)
        
        # Obtener targets en orden: [alto_mm, ancho_mm, grosor_mm, peso_g]
        target_tensor = torch.tensor([
            float(self.targets["alto"][idx]),
            float(self.targets["ancho"][idx]),
            float(self.targets["grosor"][idx]),
            float(self.targets["peso"][idx])
        ], dtype=torch.float32)
        
        # Obtener features de píxeles en orden
        if self.pixel_features_loader is not None and self.record_ids is not None:
            record_id = self.record_ids[idx]
            pixel_features = self.pixel_features_loader.get_features_by_id(record_id)
            
            if pixel_features is None:
                # Usar ceros si no se encuentran features
                logger.warning(f"Features de píxeles no encontradas para record_id {record_id}, usando ceros")
                pixel_features = np.zeros(10, dtype=np.float32)
            
            pixel_tensor = torch.tensor(pixel_features, dtype=torch.float32)
        else:
            # Usar ceros si no hay loader de features de píxeles
            pixel_tensor = torch.zeros(10, dtype=torch.float32)
        
        return img_tensor, target_tensor, pixel_tensor

