"""
Dataset mejorado para CacaoScan con validaciones robustas.

Este módulo maneja la carga de datos con validaciones,
siguiendo el principio de Responsabilidad Única.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms

from ...utils.logs import get_ml_logger
from ..normalizers.target_normalizer import TargetNormalizer
from ..datasets.validators.structure_validator import StructureValidator
from ..datasets.validators.transform_validator import TransformValidator
from ..datasets.validators.image_validator import ImagePathValidator
from ..datasets.extractors.pixel_feature_extractor import PixelFeatureExtractor
from ..datasets.loaders.image_loader import ImageLoader

logger = get_ml_logger("cacaoscan.ml.data.conjuntos_datos")


class DatasetMejorado(Dataset):
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
    ORDEN_TARGETS = ["alto", "ancho", "grosor", "peso"]
    
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
        
        # Inicializar validadores y loaders
        self.structure_validator = StructureValidator()
        self.transform_validator = TransformValidator()
        self.image_path_validator = ImagePathValidator()
        self.pixel_feature_extractor = PixelFeatureExtractor()
        self.image_loader = ImageLoader(transform)
        
        # Validar estructura si se solicita
        if validate_structure:
            self._validar_estructura()
        
        # Validar transformaciones
        if transform is not None:
            self.transform_validator.validate(transform)
        
        logger.info(f"Dataset mejorado inicializado: {len(image_paths)} muestras")
    
    def _validar_estructura(self) -> None:
        """
        Valida estructura del dataset.
        
        Raises:
            ValueError: Si hay inconsistencias
        """
        self.structure_validator.validate(
            self.image_paths,
            self.targets,
            self.pixel_features
        )
        
        # Reordenar targets si es necesario
        target_keys = list(self.targets.keys())
        if target_keys != self.ORDEN_TARGETS:
            logger.warning(
                f"El orden de targets no es el esperado. Esperado: {self.ORDEN_TARGETS}, "
                f"Obtenido: {target_keys}. Reordenando..."
            )
            self.targets = {k: self.targets[k] for k in self.ORDEN_TARGETS}
        
        # Validar rutas de imágenes
        self.image_path_validator.validate(self.image_paths, self.use_crops)
    
    def __len__(self) -> int:
        """
        Retorna el tamaño del dataset.
        
        Returns:
            Número de imágenes
        """
        return len(self.image_paths)
    
    def _cargar_y_transformar_imagen(self, image_path: Path) -> torch.Tensor:
        """
        Carga y transforma imagen a tensor.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Tensor de imagen
        """
        return self.image_loader.load(image_path)
    
    def _obtener_tensor_targets(self, idx: int) -> torch.Tensor:
        """
        Obtiene tensor de targets en orden correcto.
        
        Args:
            idx: Índice de la muestra
            
        Returns:
            Tensor de targets
        """
        targets_list = [
            float(self.targets[target][idx])
            for target in self.ORDEN_TARGETS
        ]
        return torch.tensor(targets_list, dtype=torch.float32)
    
    def _obtener_features_pixel(self, idx: int) -> Optional[torch.Tensor]:
        """
        Obtiene features de píxeles usando método apropiado.
        
        Args:
            idx: Índice de la muestra
            
        Returns:
            Tensor de features de píxeles o None
        """
        return self.pixel_feature_extractor.extract(
            idx, self.image_paths, self.pixel_features
        )
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, ...]:
        """
        Obtiene un item del dataset.
        
        Args:
            idx: Índice del item
            
        Returns:
            Tupla con:
            - tensor_imagen: Tensor de imagen normalizada [C, H, W]
            - tensor_targets: Tensor de targets en orden [alto, ancho, grosor, peso]
            - features_pixel (opcional): Tensor de features de píxeles
        """
        image_path = self.image_paths[idx]
        image_tensor = self._cargar_y_transformar_imagen(image_path)
        targets_tensor = self._obtener_tensor_targets(idx)
        
        pixel_feat = self._obtener_features_pixel(idx)
        if pixel_feat is not None:
            return image_tensor, targets_tensor, pixel_feat
        
        return image_tensor, targets_tensor
    
    def obtener_rangos_targets(self) -> Dict[str, Dict[str, float]]:
        """
        Obtiene los rangos (min, max) de cada target.
        
        Returns:
            Diccionario con rangos por target en formato {'min': ..., 'max': ...}
        """
        ranges = {}
        for target in self.ORDEN_TARGETS:
            values = self.targets[target]
            ranges[target] = {
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }
        return ranges
    
    def validar_con_calibracion(
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
        calib_by_id = self._construir_mapa_calibracion(calibration_data)
        
        matches = 0
        mismatches: List[Dict[str, Union[int, float, str]]] = []
        
        for idx, img_path in enumerate(self.image_paths):
            image_id = self._extraer_id_imagen(img_path)
            if image_id is None or image_id not in calib_by_id:
                continue
            
            record_matches, record_mismatches = self._comparar_targets_con_calibracion(
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

    def _construir_mapa_calibracion(self, calibration_data: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        """
        Indexa registros de calibración por ID para búsqueda rápida.
        
        Args:
            calibration_data: Datos de calibración
            
        Returns:
            Mapa de ID -> registro de calibración
        """
        records = calibration_data.get("calibration_records", [])
        calibration_map: Dict[int, Dict[str, Any]] = {}
        for record in records:
            try:
                record_id = int(record["id"])
            except (KeyError, TypeError, ValueError):
                continue
            calibration_map[record_id] = record
        return calibration_map

    def _extraer_id_imagen(self, img_path: Path) -> Optional[int]:
        """
        Extrae el ID numérico de una ruta de imagen.
        
        Args:
            img_path: Ruta a la imagen
            
        Returns:
            ID numérico o None
        """
        try:
            return int(img_path.stem)
        except ValueError:
            logger.warning(f"No se pudo extraer ID de {img_path}")
            return None

    def _comparar_targets_con_calibracion(
        self,
        *,
        sample_index: int,
        image_id: int,
        calibration_record: Dict[str, Any]
    ) -> Tuple[int, List[Dict[str, Union[int, float, str]]]]:
        """
        Compara targets del dataset con datos de calibración.
        
        Args:
            sample_index: Índice de la muestra
            image_id: ID de la imagen
            calibration_record: Registro de calibración
            
        Returns:
            Tupla (número de coincidencias, lista de discrepancias)
        """
        matches = 0
        mismatches: List[Dict[str, Union[int, float, str]]] = []
        real_dims = self._como_mapa(calibration_record.get("real_dimensions"))
        
        for target in self.ORDEN_TARGETS:
            target_key = self._clave_calibracion_para_target(target)
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
    def _clave_calibracion_para_target(target: str) -> str:
        """
        Retorna la clave del diccionario de calibración para un target del dataset.
        
        Args:
            target: Nombre del target
            
        Returns:
            Clave de calibración
        """
        return f"{target}_g" if target == "peso" else f"{target}_mm"

    @staticmethod
    def _como_mapa(value: Optional[Any]) -> Dict[str, Any]:
        """
        Retorna una representación de diccionario para secciones anidadas de calibración.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Diccionario
        """
        if isinstance(value, dict):
            return value
        return {}

