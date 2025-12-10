"""
Dataset unificado para regresión de cacao con features de píxeles.

Este módulo maneja la carga de datos para entrenamiento,
siguiendo el principio de Responsabilidad Única.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from sklearn.preprocessing import StandardScaler

from ...utils.logs import get_ml_logger
from ...utils.paths import get_datasets_dir, get_crops_dir
from ..dataset_loader import CacaoDatasetLoader
from ..datasets.builders.calibration_loader import CalibrationLoader
from ..datasets.builders.dataset_builder import DatasetBuilder
from ..datasets.loaders.image_loader import ImageLoader

logger = get_ml_logger("cacaoscan.ml.data.conjuntos_datos")


class DatasetCacao(Dataset):
    """
    Dataset unificado para regresión de cacao.
    
    Lee:
    - Imágenes de /app/media/cacao_images/crops/*.png
    - CSV de dataset_cacao.clean.csv
    - Features de píxeles de pixel_calibration.json
    
    Retorna:
        (tensor_imagen, vector_features_pixel, vector_targets)
    """
    
    TARGETS = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(
        self,
        csv_path: Optional[Path] = None,
        calibration_file: Optional[Path] = None,
        crops_dir: Optional[Path] = None,
        transform: Optional[transforms.Compose] = None,
        pixel_scaler: Optional[StandardScaler] = None,
        validate: bool = True
    ):
        """
        Inicializa el dataset.
        
        Args:
            csv_path: Ruta al archivo CSV
            calibration_file: Ruta al archivo de calibración
            crops_dir: Directorio de crops
            transform: Transformaciones de imagen
            pixel_scaler: Escalador de features de píxeles
            validate: Si validar consistencia de datos
        """
        paths = self._resolver_rutas(csv_path, calibration_file, crops_dir)
        self.csv_path = paths["csv"]
        self.calibration_file = paths["calibration"]
        self.crops_dir = paths["crops"]
        self.transform = transform

        # Inicializar builders y loaders
        self.calibration_loader = CalibrationLoader(self.calibration_file)
        self.dataset_builder = DatasetBuilder(self.crops_dir)
        self.image_loader = ImageLoader(transform)

        valid_records = self._cargar_registros_validos(self.csv_path)
        calibration_by_id = self.calibration_loader.load()

        dataset_data = self.dataset_builder.build(
            valid_records,
            calibration_by_id
        )

        self.records = dataset_data["records"]
        self.record_ids = dataset_data["record_ids"]
        self.image_paths = dataset_data["image_paths"]
        self.target_values = dataset_data["target_values"]
        self.pixel_features_raw = dataset_data["pixel_features"]

        self._registrar_datos_faltantes(
            dataset_data["missing_calibration"],
            dataset_data["missing_images"]
        )

        self._validar_min_registros(
            len(self.records),
            len(dataset_data["missing_calibration"]),
            len(dataset_data["missing_images"])
        )

        self.pixel_scaler = pixel_scaler or StandardScaler()
        self._ajustar_escalador_pixel(pixel_scaler)

        self.pixel_features = self.pixel_scaler.transform(self.pixel_features_raw)

        if validate:
            self._validar_consistencia()

    def _resolver_rutas(
        self,
        csv_path: Optional[Path],
        calibration_file: Optional[Path],
        crops_dir: Optional[Path]
    ) -> Dict[str, Path]:
        """
        Resuelve rutas de archivos.
        
        Args:
            csv_path: Ruta al CSV (opcional)
            calibration_file: Ruta a calibración (opcional)
            crops_dir: Directorio de crops (opcional)
            
        Returns:
            Diccionario con rutas resueltas
        """
        dataset_loader = CacaoDatasetLoader() if csv_path is None else None
        resolved_csv = Path(
            csv_path or dataset_loader.csv_path  # type: ignore[arg-type]
        )
        resolved_calibration = Path(
            calibration_file or (get_datasets_dir() / "pixel_calibration.json")
        )
        resolved_crops = Path(crops_dir or get_crops_dir())

        return {
            "csv": resolved_csv,
            "calibration": resolved_calibration,
            "crops": resolved_crops
        }

    def _cargar_registros_validos(self, csv_path: Path) -> List[Dict]:
        """
        Carga registros válidos del CSV.
        
        Args:
            csv_path: Ruta al archivo CSV
            
        Returns:
            Lista de registros válidos
        """
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        valid_records = loader.get_valid_records()

        if not valid_records:
            raise ValueError("No se encontraron registros válidos en el CSV")

        logger.info("Cargados %s registros válidos del CSV", len(valid_records))
        return valid_records

    def _registrar_datos_faltantes(
        self,
        missing_calibration: List[int],
        missing_images: List[Tuple[int, Path]]
    ) -> None:
        """
        Registra datos faltantes en logs.
        
        Args:
            missing_calibration: Lista de IDs sin calibración
            missing_images: Lista de tuplas (ID, ruta) sin imágenes
        """
        if missing_calibration:
            logger.warning(
                "Falta calibración para %s registros. Primeros 5: %s",
                len(missing_calibration),
                missing_calibration[:5]
            )

        if missing_images:
            logger.warning(
                "Faltan imágenes para %s registros. Primeros 5: %s",
                len(missing_images),
                missing_images[:5]
            )

    @staticmethod
    def _validar_min_registros(
        record_count: int,
        missing_calibration_count: int,
        missing_images_count: int
    ) -> None:
        """
        Valida que haya suficientes registros.
        
        Args:
            record_count: Número de registros
            missing_calibration_count: Número sin calibración
            missing_images_count: Número sin imágenes
            
        Raises:
            ValueError: Si no hay suficientes registros
        """
        if record_count < 10:
            raise ValueError(
                "No hay suficientes registros válidos: %s. "
                "Falta calibración: %s, Faltan imágenes: %s"
                % (record_count, missing_calibration_count, missing_images_count)
            )

    def _ajustar_escalador_pixel(self, provided_scaler: Optional[StandardScaler]) -> None:
        """
        Ajusta el escalador de features de píxeles.
        
        Args:
            provided_scaler: Escalador proporcionado (opcional)
        """
        if provided_scaler is None:
            self.pixel_scaler.fit(self.pixel_features_raw)
            logger.info("Escalador de features de píxeles ajustado (StandardScaler)")
    
    def _validar_consistencia(self) -> None:
        """
        Valida consistencia de datos.
        
        Raises:
            ValueError: Si hay inconsistencias
        """
        # Verificar longitudes
        lengths = [
            len(self.records),
            len(self.record_ids),
            len(self.image_paths),
            len(self.pixel_features)
        ]
        lengths.extend([len(self.target_values[target]) for target in self.TARGETS])
        
        if len(set(lengths)) > 1:
            raise ValueError(f"Longitudes inconsistentes: {lengths}")
        
        # Verificar que las rutas de imágenes existan
        for i, img_path in enumerate(self.image_paths):
            if not img_path.exists():
                raise ValueError(f"La ruta de imagen no existe en índice {i}: {img_path}")
        
        logger.info("Consistencia de datos validada")
    
    def __len__(self) -> int:
        """
        Retorna el tamaño del dataset.
        
        Returns:
            Número de registros
        """
        return len(self.records)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Obtiene una muestra del dataset.
        
        Args:
            idx: Índice de la muestra
            
        Returns:
            Tupla (tensor_imagen, vector_features_pixel, vector_targets)
        """
        # Cargar imagen usando ImageLoader
        image_path = self.image_paths[idx]
        image_tensor = self.image_loader.load(image_path)
        
        # Obtener features de píxeles
        pixel_feature_vector = torch.tensor(
            self.pixel_features[idx],
            dtype=torch.float32
        )
        
        # Obtener targets en orden: [alto, ancho, grosor, peso]
        target_vector = torch.tensor([
            self.target_values["alto"][idx],
            self.target_values["ancho"][idx],
            self.target_values["grosor"][idx],
            self.target_values["peso"][idx]
        ], dtype=torch.float32)
        
        return image_tensor, pixel_feature_vector, target_vector
    
    def get_pixel_scaler(self) -> StandardScaler:
        """
        Obtiene el escalador de features de píxeles.
        
        Returns:
            Escalador ajustado
        """
        return self.pixel_scaler

