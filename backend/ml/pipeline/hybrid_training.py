"""
Hybrid training pipeline for cacao regression.

Integrates:
- PixelFeaturesLoader for normalized pixel features
- HybridCacaoDataset for hybrid data loading
- HybridCacaoRegressionModel for hybrid model
- HybridTrainer for improved training loop
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import torchvision.transforms as transforms

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir
from ..data.pixel_features_loader import PixelFeaturesLoader
from ..data.hybrid_dataset import HybridCacaoDataset
from ..regression.hybrid_model import create_hybrid_model
from ..regression.hybrid_trainer import HybridTrainer
from ..regression.augmentation import create_advanced_train_transform, create_advanced_val_transform
from ..data.dataset_loader import CacaoDatasetLoader
from ..regression.train import get_device

logger = get_ml_logger("cacaoscan.ml.pipeline.hybrid_training")
EXPECTED_PIXEL_FEATURES = 6


def train_hybrid_model(
    config: Dict,
    calibration_file: Optional[Path] = None
) -> Dict:
    """
    Train hybrid cacao regression model.
    
    Args:
        config: Training configuration
        calibration_file: Path to pixel_calibration.json (optional)
        
    Returns:
        Training results dictionary
    """
    logger.info("Starting hybrid training pipeline")
    
    pixel_loader = _load_pixel_features(calibration_file)
    
    dataset_loader = CacaoDatasetLoader()
    valid_records = dataset_loader.get_valid_records()
    if not valid_records:
        raise ValueError("No valid records found")
    logger.info(f"Found {len(valid_records)} valid records")
    
    (
        crop_records,
        record_ids,
        missing_crops,
        missing_features
    ) = _collect_records_with_features(valid_records, pixel_loader)
    
    _log_missing_data(missing_crops, missing_features)
    _validate_record_counts(crop_records, missing_crops, missing_features)
    _validate_dataset_integrity(crop_records, record_ids, pixel_loader)
    
    image_paths = [Path(record["crop_image_path"]) for record in crop_records]
    targets = _build_targets(crop_records)
    
    train_indices, val_indices, test_indices = _split_dataset_indices(len(crop_records))
    train_images = [image_paths[i] for i in train_indices]
    val_images = [image_paths[i] for i in val_indices]
    test_images = [image_paths[i] for i in test_indices]
    
    train_targets = {k: v[train_indices] for k, v in targets.items()}
    val_targets = {k: v[val_indices] for k, v in targets.items()}
    test_targets = {k: v[test_indices] for k, v in targets.items()}
    
    train_record_ids = [record_ids[i] for i in train_indices]
    val_record_ids = [record_ids[i] for i in val_indices]
    test_record_ids = [record_ids[i] for i in test_indices]
    
    logger.info(f"Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")
    
    # Create transforms
    img_size = config.get('img_size', 224)
    train_transform = create_advanced_train_transform(img_size)
    val_transform = create_advanced_val_transform(img_size)
    
    # Create datasets
    train_dataset = HybridCacaoDataset(
        image_paths=train_images,
        targets=train_targets,
        transform=train_transform,
        pixel_features_loader=pixel_loader,
        record_ids=train_record_ids,
        validate=True
    )
    
    val_dataset = HybridCacaoDataset(
        image_paths=val_images,
        targets=val_targets,
        transform=val_transform,
        pixel_features_loader=pixel_loader,
        record_ids=val_record_ids,
        validate=True
    )
    
    test_dataset = HybridCacaoDataset(
        image_paths=test_images,
        targets=test_targets,
        transform=val_transform,
        pixel_features_loader=pixel_loader,
        record_ids=test_record_ids,
        validate=True
    )
    
    # Create data loaders
    batch_size = config.get('batch_size', 32)
    num_workers = config.get('num_workers', 0)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    # Create model
    device = get_device()
    model = create_hybrid_model(
        pretrained=config.get('pretrained', True),
        dropout_rate=config.get('dropout_rate', 0.2)
    )
    
    # Create trainer
    save_dir = get_regressors_artifacts_dir() / "checkpoints"
    trainer = HybridTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        config=config,
        save_dir=save_dir
    )
    
    # Train
    epochs = config.get('epochs', 50)
    history = trainer.train(epochs)
    
    # Save final model
    model_save_path = get_regressors_artifacts_dir() / "models" / "hybrid_latest.pt"
    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': config,
        'history': history
    }, model_save_path)
    logger.info(f"Saved final model: {model_save_path}")
    
    # Evaluate on test set
    model.eval()
    all_predictions = {target: [] for target in ["alto", "ancho", "grosor", "peso"]}
    all_targets = {target: [] for target in ["alto", "ancho", "grosor", "peso"]}
    
    with torch.no_grad():
        for batch_data in test_loader:
            images, targets_batch, pixel_features = batch_data
            images = images.to(device)
            targets_batch = targets_batch.to(device)
            pixel_features = pixel_features.to(device)
            
            outputs = model(images, pixel_features)
            trainer.criterion(outputs, targets_batch)
            
            outputs_np = outputs.cpu().numpy()
            targets_np = targets_batch.cpu().numpy()
            
            for i, target in enumerate(["alto", "ancho", "grosor", "peso"]):
                all_predictions[target].extend(outputs_np[:, i])
                all_targets[target].extend(targets_np[:, i])
    
    # Calculate test metrics
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    
    test_metrics = {}
    for target in ["alto", "ancho", "grosor", "peso"]:
        pred = np.array(all_predictions[target])
        true = np.array(all_targets[target])
        
        test_metrics[target] = {
            'r2': float(r2_score(true, pred)),
            'mae': float(mean_absolute_error(true, pred)),
            'rmse': float(np.sqrt(mean_squared_error(true, pred)))
        }
    
    results = {
        'history': history,
        'test_metrics': test_metrics,
        'best_epoch': trainer.best_epoch,
        'best_val_loss': trainer.best_val_loss,
        'model_path': str(model_save_path)
    }
    
    logger.info("Hybrid training completed")
    return results


def _load_pixel_features(calibration_file: Optional[Path]) -> PixelFeaturesLoader:
    """Load pixel features ensuring calibration data is available."""
    pixel_loader = PixelFeaturesLoader(calibration_file)
    if not pixel_loader.load():
        raise ValueError("Failed to load pixel calibration features")
    logger.info(f"Loaded pixel features for {len(pixel_loader.features_by_id)} records")
    return pixel_loader


def _collect_records_with_features(
    valid_records: List[Dict[str, Any]],
    pixel_loader: PixelFeaturesLoader
) -> Tuple[List[Dict[str, Any]], List[int], List[Tuple[Any, str]], List[Tuple[Any, str]]]:
    """Filter records ensuring crops and pixel features exist."""
    crop_records: List[Dict[str, Any]] = []
    record_ids: List[int] = []
    missing_crops: List[Tuple[Any, str]] = []
    missing_features: List[Tuple[Any, str]] = []
    
    for record in valid_records:
        crop_path = Path(record.get("crop_image_path", ""))
        record_id = record.get("id")
        filename = str(record.get("filename", "") or "")
        
        if not crop_path.exists():
            missing_crops.append((record_id, filename))
            continue
        if record_id is None:
            continue
        
        pixel_features = pixel_loader.get_features_by_id(record_id)
        if pixel_features is None:
            missing_features.append((record_id, filename))
            continue
        
        converted = _ensure_float32_features(record_id, pixel_features, pixel_loader)
        if converted is None:
            continue
        
        if converted.shape[0] != EXPECTED_PIXEL_FEATURES:
            logger.warning(
                f"Pixel features for ID {record_id} have wrong shape: {converted.shape[0]}, expected {EXPECTED_PIXEL_FEATURES}"
            )
            continue
        
        crop_records.append(record)
        record_ids.append(record_id)
    
    return crop_records, record_ids, missing_crops, missing_features


def _ensure_float32_features(
    record_id: int,
    features: np.ndarray,
    pixel_loader: PixelFeaturesLoader
) -> Optional[np.ndarray]:
    """Guarantee feature vectors are stored as float32."""
    if features.dtype == np.float32:
        return features
    
    logger.warning(f"Pixel features for ID {record_id} are not float32, converting...")
    converted = features.astype(np.float32)
    pixel_loader.features_by_id[record_id] = converted
    return converted


def _log_missing_data(
    missing_crops: List[Tuple[Any, str]],
    missing_features: List[Tuple[Any, str]]
) -> None:
    """Log missing crop and feature stats."""
    if missing_crops:
        logger.warning(f"Missing crops for {len(missing_crops)} records. First 5: {missing_crops[:5]}")
    if missing_features:
        logger.warning(f"Missing pixel features for {len(missing_features)} records. First 5: {missing_features[:5]}")


def _validate_record_counts(
    crop_records: List[Dict[str, Any]],
    missing_crops: List[Tuple[Any, str]],
    missing_features: List[Tuple[Any, str]]
) -> None:
    """Ensure there are enough records to continue training."""
    if len(crop_records) < 10:
        raise ValueError(
            f"Not enough records with crops and pixel features: {len(crop_records)}. "
            f"Missing crops: {len(missing_crops)}, Missing features: {len(missing_features)}"
        )
    if not crop_records:
        raise ValueError("No records available after filtering crops and pixel features")
    logger.info(f"Using {len(crop_records)} records with crops and pixel features")


def _validate_dataset_integrity(
    crop_records: List[Dict[str, Any]],
    record_ids: List[int],
    pixel_loader: PixelFeaturesLoader
) -> None:
    """Validate that each record has consistent assets before training."""
    if len(crop_records) != len(record_ids):
        raise ValueError(f"Inconsistent data: {len(crop_records)} records but {len(record_ids)} IDs")
    
    for idx, (record, record_id) in enumerate(zip(crop_records, record_ids)):
        crop_path = Path(record.get("crop_image_path", ""))
        if not crop_path.exists():
            raise ValueError(f"Image path does not exist at index {idx}: {crop_path}")
        
        features = pixel_loader.get_features_by_id(record_id)
        if features is None:
            raise ValueError(f"Pixel features not found for record_id {record_id} at index {idx}")
        if features.dtype != np.float32:
            raise ValueError(f"Pixel features for record_id {record_id} are not float32: {features.dtype}")
        if features.shape[0] != EXPECTED_PIXEL_FEATURES:
            raise ValueError(
                f"Pixel features for record_id {record_id} have wrong shape: {features.shape[0]}"
            )
    
    logger.info("All validations passed")


def _build_targets(crop_records: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
    """Construct target tensors from records."""
    return {
        "alto": np.array([record["alto"] for record in crop_records], dtype=np.float32),
        "ancho": np.array([record["ancho"] for record in crop_records], dtype=np.float32),
        "grosor": np.array([record["grosor"] for record in crop_records], dtype=np.float32),
        "peso": np.array([record["peso"] for record in crop_records], dtype=np.float32)
    }


def _split_dataset_indices(num_records: int) -> Tuple[List[int], List[int], List[int]]:
    """Create reproducible train/val/test splits."""
    if num_records < 2:
        raise ValueError("At least two records are required to split the dataset")
    
    indices = list(range(num_records))
    train_indices, temp_indices = train_test_split(
        indices,
        test_size=0.3,
        random_state=42
    )
    val_indices, test_indices = train_test_split(
        temp_indices,
        test_size=0.5,
        random_state=42
    )
    return train_indices, val_indices, test_indices

