"""
Unified dataset for cacao regression with pixel features from pixel_calibration.json.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms
from sklearn.preprocessing import StandardScaler

from ..utils.logs import get_ml_logger
from ..utils.paths import get_datasets_dir, get_crops_dir, get_media_root
from .dataset_loader import CacaoDatasetLoader

logger = get_ml_logger("cacaoscan.ml.data.cacao_dataset")


class CacaoDataset(Dataset):
    """
    Unified dataset for cacao regression.
    
    Reads:
    - Images from /app/media/cacao_images/crops/*.png
    - CSV from dataset_cacao.clean.csv
    - Pixel features from pixel_calibration.json
    
    Returns:
        (image_tensor, pixel_feature_vector, target_vector)
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
        Initialize the dataset.
        """
        paths = self._resolve_paths(csv_path, calibration_file, crops_dir)
        self.csv_path = paths["csv"]
        self.calibration_file = paths["calibration"]
        self.crops_dir = paths["crops"]
        self.transform = transform

        valid_records = self._load_valid_records(self.csv_path)
        calibration_by_id = self._load_calibration_records(self.calibration_file)

        dataset_data = self._build_dataset_records(
            valid_records,
            calibration_by_id,
            self.crops_dir
        )

        self.records = dataset_data["records"]
        self.record_ids = dataset_data["record_ids"]
        self.image_paths = dataset_data["image_paths"]
        self.target_values = dataset_data["target_values"]
        self.pixel_features_raw = dataset_data["pixel_features"]

        self._log_missing_data(
            dataset_data["missing_calibration"],
            dataset_data["missing_images"]
        )

        self._validate_min_records(
            len(self.records),
            len(dataset_data["missing_calibration"]),
            len(dataset_data["missing_images"])
        )

        self.pixel_scaler = pixel_scaler or StandardScaler()
        self._fit_pixel_scaler(pixel_scaler)

        self.pixel_features = self.pixel_scaler.transform(self.pixel_features_raw)

        if validate:
            self._validate_consistency()

    def _resolve_paths(
        self,
        csv_path: Optional[Path],
        calibration_file: Optional[Path],
        crops_dir: Optional[Path]
    ) -> Dict[str, Path]:
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

    def _load_valid_records(self, csv_path: Path) -> List[Dict]:
        loader = CacaoDatasetLoader(csv_path=str(csv_path))
        valid_records = loader.get_valid_records()

        if not valid_records:
            raise ValueError("No valid records found in CSV")

        logger.info("Loaded %s valid records from CSV", len(valid_records))
        return valid_records

    def _load_calibration_records(self, calibration_file: Path) -> Dict[int, Dict]:
        if not calibration_file.exists():
            raise FileNotFoundError(
                f"Pixel calibration file not found: {calibration_file}"
            )

        with open(calibration_file, 'r', encoding='utf-8') as file:
            calibration_data = json.load(file)

        calibration_records = calibration_data.get("calibration_records", [])
        calibration_by_id = {rec["id"]: rec for rec in calibration_records}
        
        logger.info("Loaded %s calibration records", len(calibration_by_id))
        return calibration_by_id

    def _build_dataset_records(
        self,
        valid_records: List[Dict],
        calibration_by_id: Dict[int, Dict],
        crops_dir: Path
    ) -> Dict[str, object]:
        records: List[Dict] = []
        record_ids: List[int] = []
        image_paths: List[Path] = []
        target_values = {target: [] for target in self.TARGETS}
        pixel_features: List[np.ndarray] = []
        missing_calibration: List[int] = []
        missing_images: List[Tuple[int, Path]] = []

        for record in valid_records:
            crop_path = self._resolve_crop_path(record, crops_dir)

            if not crop_path.exists():
                missing_images.append((record["id"], crop_path))
                continue

            calibration_entry = calibration_by_id.get(record["id"])
            if calibration_entry is None:
                missing_calibration.append(record["id"])
                continue

            feature_vector = self._build_pixel_feature_vector(
                calibration_entry
            )

            if not np.all(np.isfinite(feature_vector)):
                logger.warning("Invalid pixel features for ID %s", record["id"])
                continue

            self._append_record_data(
                record,
                crop_path,
                feature_vector,
                records,
                record_ids,
                image_paths,
                target_values,
                pixel_features
            )

        return {
            "records": records,
            "record_ids": record_ids,
            "image_paths": image_paths,
            "target_values": {
                target: np.array(values, dtype=np.float32)
                for target, values in target_values.items()
            },
            "pixel_features": np.array(pixel_features, dtype=np.float32),
            "missing_calibration": missing_calibration,
            "missing_images": missing_images
        }

    @staticmethod
    def _resolve_crop_path(record: Dict, crops_dir: Path) -> Path:
        crop_path = Path(record.get("crop_image_path", ""))
        if not crop_path.is_absolute():
            return crops_dir / crop_path
        return crop_path

    def _build_pixel_feature_vector(self, calibration_entry: Dict) -> np.ndarray:
        pixel_meas = calibration_entry.get("pixel_measurements", {})
        scale_factors = calibration_entry.get("scale_factors", {})
        bg_info = calibration_entry.get("background_info", {})
        
        avg_mm_per_pixel = float(scale_factors.get("average_mm_per_pixel", 0.0))
        width_pixels = float(pixel_meas.get("width_pixels", 0.0))
        height_pixels = float(pixel_meas.get("height_pixels", 0.0))
        grain_area_pixels = float(pixel_meas.get("grain_area_pixels", 0.0))
        bbox_area_pixels = float(pixel_meas.get("bbox_area_pixels", 0.0))
        aspect_ratio = float(pixel_meas.get("aspect_ratio", 0.0))
        background_ratio = float(bg_info.get("background_ratio", 0.0))

        area_mm2 = grain_area_pixels * (avg_mm_per_pixel ** 2)
        width_mm = width_pixels * avg_mm_per_pixel
        height_mm = height_pixels * avg_mm_per_pixel
        perimeter_mm = 2 * (width_pixels + height_pixels) * avg_mm_per_pixel
        bbox_ratio = (grain_area_pixels / bbox_area_pixels) if bbox_area_pixels > 0 else 0.0

        compactness = ((perimeter_mm ** 2) / (4 * np.pi * area_mm2)) if area_mm2 > 0 else 0.0
        roundness = ((4 * np.pi * area_mm2) / (perimeter_mm ** 2)) if perimeter_mm > 0 else 0.0

        return np.array([
            area_mm2,
            width_mm,
            height_mm,
            perimeter_mm,
            aspect_ratio,
            bbox_ratio,
            background_ratio,
            avg_mm_per_pixel,
            compactness,
            roundness
        ], dtype=np.float32)

    def _append_record_data(
        self,
        record: Dict,
        crop_path: Path,
        pixel_feature_vector: np.ndarray,
        records: List[Dict],
        record_ids: List[int],
        image_paths: List[Path],
        target_values: Dict[str, List[float]],
        pixel_features: List[np.ndarray]
    ) -> None:
        if not records:
            logger.info(
                "First record pixel features (10 dims): "
                "area_mm2=%.2f, perimeter_mm=%.2f, compactness=%.2f, roundness=%.2f",
                pixel_feature_vector[0],
                pixel_feature_vector[3],
                pixel_feature_vector[8],
                pixel_feature_vector[9]
            )

        records.append(record)
        record_ids.append(record["id"])
        image_paths.append(crop_path)

        for target in self.TARGETS:
            target_values[target].append(float(record[target]))

        pixel_features.append(pixel_feature_vector)

    def _log_missing_data(
        self,
        missing_calibration: List[int],
        missing_images: List[Tuple[int, Path]]
    ) -> None:
        if missing_calibration:
            logger.warning(
                "Missing calibration for %s records. First 5: %s",
                len(missing_calibration),
                missing_calibration[:5]
            )

        if missing_images:
            logger.warning(
                "Missing images for %s records. First 5: %s",
                len(missing_images),
                missing_images[:5]
            )

    @staticmethod
    def _validate_min_records(
        record_count: int,
        missing_calibration_count: int,
        missing_images_count: int
    ) -> None:
        if record_count < 10:
            raise ValueError(
                "Not enough valid records: %s. Missing calibration: %s, Missing images: %s"
                % (record_count, missing_calibration_count, missing_images_count)
            )

    def _fit_pixel_scaler(self, provided_scaler: Optional[StandardScaler]) -> None:
        if provided_scaler is None:
            self.pixel_scaler.fit(self.pixel_features_raw)
            logger.info("Pixel features scaler fitted (StandardScaler)")
    
    def _validate_consistency(self) -> None:
        """Validate data consistency."""
        # Check lengths
        lengths = [
            len(self.records),
            len(self.record_ids),
            len(self.image_paths),
            len(self.pixel_features)
        ]
        lengths.extend([len(self.target_values[target]) for target in self.TARGETS])
        
        if len(set(lengths)) > 1:
            raise ValueError(f"Inconsistent data lengths: {lengths}")
        
        # Check image paths exist
        for i, img_path in enumerate(self.image_paths):
            if not img_path.exists():
                raise ValueError(f"Image path does not exist at index {i}: {img_path}")
        
        logger.info("Data consistency validated")
    
    def __len__(self) -> int:
        return len(self.records)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Get a sample from the dataset.
        
        Returns:
            (image_tensor, pixel_feature_vector, target_vector)
        """
        # Load image
        image_path = self.image_paths[idx]
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            if self.transform is not None:
                image_tensor = self.transform(image)
            else:
                # Default transform
                transform_default = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    )
                ])
                image_tensor = transform_default(image)
            
            # Validate image tensor
            if image_tensor.shape[0] != 3:
                raise ValueError(f"Image must have 3 channels, got {image_tensor.shape[0]}")
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise
        
        # Get pixel features
        pixel_feature_vector = torch.tensor(
            self.pixel_features[idx],
            dtype=torch.float32
        )
        
        # Get targets in order: [alto, ancho, grosor, peso]
        target_vector = torch.tensor([
            self.target_values["alto"][idx],
            self.target_values["ancho"][idx],
            self.target_values["grosor"][idx],
            self.target_values["peso"][idx]
        ], dtype=torch.float32)
        
        return image_tensor, pixel_feature_vector, target_vector
    
    def get_pixel_scaler(self) -> StandardScaler:
        """Get the pixel features scaler."""
        return self.pixel_scaler

