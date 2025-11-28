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
        
        Args:
            csv_path: Path to CSV file (default: auto-detect)
            calibration_file: Path to pixel_calibration.json (default: auto-detect)
            crops_dir: Directory with crop images (default: auto-detect)
            transform: Image transformations
            pixel_scaler: Scaler for pixel features (optional, will fit if None)
            validate: Whether to validate data consistency
        """
        # Auto-detect paths
        if csv_path is None:
            dataset_loader = CacaoDatasetLoader()
            csv_path = dataset_loader.csv_path
        
        if calibration_file is None:
            calibration_file = get_datasets_dir() / "pixel_calibration.json"
        
        if crops_dir is None:
            crops_dir = get_crops_dir()
        
        self.csv_path = Path(csv_path)
        self.calibration_file = Path(calibration_file)
        self.crops_dir = Path(crops_dir)
        self.transform = transform
        
        # Load CSV
        dataset_loader = CacaoDatasetLoader(csv_path=str(csv_path))
        valid_records = dataset_loader.get_valid_records()
        
        if not valid_records:
            raise ValueError("No valid records found in CSV")
        
        logger.info(f"Loaded {len(valid_records)} valid records from CSV")
        
        # Load pixel calibration
        if not self.calibration_file.exists():
            raise FileNotFoundError(f"Pixel calibration file not found: {self.calibration_file}")
        
        with open(self.calibration_file, 'r') as f:
            calibration_data = json.load(f)
        
        calibration_records = calibration_data.get("calibration_records", [])
        calibration_by_id = {rec["id"]: rec for rec in calibration_records}
        
        logger.info(f"Loaded {len(calibration_by_id)} calibration records")
        
        # Build dataset
        self.records = []
        self.record_ids = []
        self.image_paths = []
        self.target_values = {target: [] for target in self.TARGETS}
        self.pixel_features_raw = []
        
        missing_calibration = []
        missing_images = []
        
        for record in valid_records:
            record_id = record["id"]
            crop_path = Path(record.get("crop_image_path", ""))
            
            # Validate image exists
            if not crop_path.exists():
                missing_images.append((record_id, crop_path))
                continue
            
            # Validate calibration exists
            if record_id not in calibration_by_id:
                missing_calibration.append(record_id)
                continue
            
            calib_record = calibration_by_id[record_id]
            
            # Extract pixel features
            pixel_meas = calib_record.get("pixel_measurements", {})
            scale_factors = calib_record.get("scale_factors", {})
            bg_info = calib_record.get("background_info", {})
            
            # Calculate pixel features
            avg_mm_per_pixel = float(scale_factors.get("average_mm_per_pixel", 0.0))
            width_pixels = float(pixel_meas.get("width_pixels", 0.0))
            height_pixels = float(pixel_meas.get("height_pixels", 0.0))
            grain_area_pixels = float(pixel_meas.get("grain_area_pixels", 0.0))
            bbox_area_pixels = float(pixel_meas.get("bbox_area_pixels", 0.0))
            aspect_ratio = float(pixel_meas.get("aspect_ratio", 0.0))
            background_ratio = float(bg_info.get("background_ratio", 0.0))
            
            # Calculate derived features
            area_mm2 = grain_area_pixels * (avg_mm_per_pixel ** 2)
            width_mm = width_pixels * avg_mm_per_pixel
            height_mm = height_pixels * avg_mm_per_pixel
            perimeter_mm = 2 * (width_pixels + height_pixels) * avg_mm_per_pixel
            bbox_ratio = grain_area_pixels / bbox_area_pixels if bbox_area_pixels > 0 else 0.0
            
            # New features for grosor and peso
            # compactness = (perimeter²) / (4π·area)
            compactness = (perimeter_mm ** 2) / (4 * np.pi * area_mm2) if area_mm2 > 0 else 0.0
            
            # roundness = 4π·area / perimeter²
            roundness = (4 * np.pi * area_mm2) / (perimeter_mm ** 2) if perimeter_mm > 0 else 0.0
            
            # Build pixel feature vector (10 features)
            # Order: area_mm2, width_mm, height_mm, perimeter_mm, aspect_ratio, bbox_ratio, 
            #        background_ratio, avg_mm_per_pixel, compactness, roundness
            pixel_feature_vector = np.array([
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
            
            # Log first record to verify features
            if len(self.records) == 0:
                logger.info(
                    f"First record pixel features (10 dims): "
                    f"area_mm2={area_mm2:.2f}, perimeter_mm={perimeter_mm:.2f}, "
                    f"compactness={compactness:.2f}, roundness={roundness:.2f}"
                )
            
            # Validate pixel features
            if not np.all(np.isfinite(pixel_feature_vector)):
                logger.warning(f"Invalid pixel features for ID {record_id}")
                continue
            
            # Store data
            self.records.append(record)
            self.record_ids.append(record_id)
            self.image_paths.append(crop_path)
            
            for target in self.TARGETS:
                self.target_values[target].append(float(record[target]))
            
            self.pixel_features_raw.append(pixel_feature_vector)
        
        # Convert to numpy arrays
        for target in self.TARGETS:
            self.target_values[target] = np.array(self.target_values[target], dtype=np.float32)
        
        self.pixel_features_raw = np.array(self.pixel_features_raw, dtype=np.float32)
        
        # Log validation results
        if missing_calibration:
            logger.warning(f"Missing calibration for {len(missing_calibration)} records. First 5: {missing_calibration[:5]}")
        
        if missing_images:
            logger.warning(f"Missing images for {len(missing_images)} records. First 5: {missing_images[:5]}")
        
        if len(self.records) < 10:
            raise ValueError(
                f"Not enough valid records: {len(self.records)}. "
                f"Missing calibration: {len(missing_calibration)}, Missing images: {len(missing_images)}"
            )
        
        logger.info(f"Dataset initialized with {len(self.records)} valid records")
        
        # Fit pixel scaler if provided (StandardScaler as per requirements)
        if pixel_scaler is None:
            self.pixel_scaler = StandardScaler()
            self.pixel_scaler.fit(self.pixel_features_raw)
            logger.info("Pixel features scaler fitted (StandardScaler)")
        else:
            self.pixel_scaler = pixel_scaler
        
        # Transform pixel features
        self.pixel_features = self.pixel_scaler.transform(self.pixel_features_raw)
        
        # Validate final consistency
        if validate:
            self._validate_consistency()
    
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
    
    def get_pixel_scaler(self) -> RobustScaler:
        """Get the pixel features scaler."""
        return self.pixel_scaler

