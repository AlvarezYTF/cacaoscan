"""
Hybrid v2 training pipeline with improved features.
"""
import logging
from pathlib import Path
from typing import Dict, Optional
import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import torchvision.transforms as transforms

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir
from ..data.cacao_dataset import CacaoDataset
from ..regression.hybrid_model import create_hybrid_model
from ..regression.hybrid_trainer import HybridTrainer
from ..regression.augmentation import create_advanced_train_transform, create_advanced_val_transform
from ..regression.train import get_device
from ..utils.scalers import CacaoRobustScaler

logger = get_ml_logger("cacaoscan.ml.pipeline.hybrid_v2_training")


def train_hybrid_v2(config: Dict) -> Dict:
    """
    Train hybrid v2 model with improved features.
    
    Args:
        config: Training configuration
        
    Returns:
        Training results dictionary
    """
    logger.info("Starting hybrid v2 training pipeline")
    
    # Create dataset
    dataset = CacaoDataset(
        transform=None,  # Will set transforms later
        validate=True
    )
    
    logger.info(f"Dataset loaded: {len(dataset)} samples")
    
    # Verify pixel features dimension
    if len(dataset) > 0:
        sample_pixel_features = dataset[0][1]
        logger.info(f"Pixel features dimension: {len(sample_pixel_features)} (expected: 10)")
        if len(sample_pixel_features) != 10:
            logger.warning(f"Expected 10 pixel features but got {len(sample_pixel_features)}!")
    
    # Get pixel scaler from dataset
    pixel_scaler = dataset.get_pixel_scaler()
    
    # Split data
    indices = list(range(len(dataset)))
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
    
    logger.info(f"Train: {len(train_indices)}, Val: {len(val_indices)}, Test: {len(test_indices)}")
    
    # Create transforms
    img_size = config.get('img_size', 224)
    train_transform = create_advanced_train_transform(img_size)
    val_transform = create_advanced_val_transform(img_size)
    
    # Create subset datasets using indices
    # We need to create a custom dataset class that supports indexing
    from torch.utils.data import Subset
    
    # Set transforms on original dataset
    dataset.transform = train_transform
    
    # Create subsets
    train_subset = Subset(dataset, train_indices)
    val_subset = Subset(dataset, val_indices)
    test_subset = Subset(dataset, test_indices)
    
    # Create wrapper to apply different transforms
    class TransformDataset:
        def __init__(self, subset, transform):
            self.subset = subset
            self.transform = transform
            self.dataset = subset.dataset
        
        def __len__(self):
            return len(self.subset)
        
        def __getitem__(self, idx):
            image, pixel_features, targets = self.subset[idx]
            # Re-apply transform if needed (for validation/test)
            if self.transform != self.dataset.transform:
                # Need to reload image with new transform
                original_idx = self.subset.indices[idx]
                image_path = self.dataset.image_paths[original_idx]
                from PIL import Image
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image = self.transform(image)
            return image, pixel_features, targets
    
    train_dataset = TransformDataset(train_subset, train_transform)
    val_dataset = TransformDataset(val_subset, val_transform)
    test_dataset = TransformDataset(test_subset, val_transform)
    
    # Extract targets for normalization
    train_targets = {target: dataset.targets[target][train_indices] for target in dataset.TARGETS}
    val_targets = {target: dataset.targets[target][val_indices] for target in dataset.TARGETS}
    test_targets = {target: dataset.targets[target][test_indices] for target in dataset.TARGETS}
    
    # Normalize targets with RobustScaler (with selective log-transform)
    logger.info("Creating target scaler with SELECTIVE LOG-TRANSFORM (grosor, peso only)")
    target_scaler = CacaoRobustScaler()
    logger.info(f"Target scaler LOG_TARGETS: {target_scaler.LOG_TARGETS}")
    train_targets_normalized = target_scaler.fit_transform(train_targets)
    logger.info("Target normalization completed with log-transform applied to grosor and peso")
    val_targets_normalized = target_scaler.transform(val_targets)
    test_targets_normalized = target_scaler.transform(test_targets)
    
    # Update dataset targets in the wrapper
    class NormalizedDataset:
        def __init__(self, transform_dataset, normalized_targets, subset_indices):
            self.transform_dataset = transform_dataset
            self.normalized_targets = normalized_targets
            self.subset_indices = subset_indices
        
        def __len__(self):
            return len(self.transform_dataset)
        
        def __getitem__(self, idx):
            image, pixel_features, _ = self.transform_dataset[idx]
            # Get normalized target using subset index mapping
            subset_idx = self.subset_indices[idx]
            target_vector = torch.tensor([
                self.normalized_targets["alto"][subset_idx],
                self.normalized_targets["ancho"][subset_idx],
                self.normalized_targets["grosor"][subset_idx],
                self.normalized_targets["peso"][subset_idx]
            ], dtype=torch.float32)
            return image, pixel_features, target_vector
    
    # Create normalized datasets
    train_dataset_norm = NormalizedDataset(train_dataset, train_targets_normalized, train_indices)
    val_dataset_norm = NormalizedDataset(val_dataset, val_targets_normalized, val_indices)
    test_dataset_norm = NormalizedDataset(test_dataset, test_targets_normalized, test_indices)
    
    # Store original targets for denormalization later
    test_targets_original = test_targets
    
    # Save scalers
    target_scaler.save()
    logger.info("Target scalers saved")
    
    # Create data loaders
    batch_size = config.get('batch_size', 32)
    num_workers = config.get('num_workers', 0)
    
    train_loader = DataLoader(
        train_dataset_norm,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    val_loader = DataLoader(
        val_dataset_norm,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    test_loader = DataLoader(
        test_dataset_norm,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    # Create model
    device = get_device()
    # Get actual pixel dim from dataset (should be 10 with compactness and roundness)
    pixel_dim = len(dataset[0][1]) if len(dataset) > 0 else 10
    logger.info(f"Creating hybrid model with pixel_dim={pixel_dim} and FEATURE GATING")
    model = create_hybrid_model(
        backbone_name="convnext_tiny",
        pixel_dim=pixel_dim,  # 10 pixel features
        pretrained=config.get('pretrained', True),
        dropout_rate=config.get('dropout_rate', 0.1)
    )
    
    # Verify model architecture
    logger.info("Model architecture verification:")
    logger.info(f"  - Model has feature gating: {hasattr(model, 'gating')}")
    logger.info(f"  - Model forward returns tuple: {hasattr(model, 'forward')}")
    
    # Create trainer
    save_dir = get_regressors_artifacts_dir() / "checkpoints"
    trainer = HybridTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        config=config,
        save_dir=save_dir,
        use_mixed_precision=config.get('use_mixed_precision', False)
    )
    
    # Train
    epochs = config.get('epochs', 50)
    history = trainer.train(epochs)
    
    # Save final model
    model_save_path = get_regressors_artifacts_dir() / "models" / "hybrid_v2_latest.pt"
    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': config,
        'history': history,
        'pixel_scaler': pixel_scaler
    }, model_save_path)
    logger.info(f"Saved final model: {model_save_path}")
    
    # Evaluate on test set
    model.eval()
    test_loss = 0.0
    all_predictions_normalized = {target: [] for target in ["alto", "ancho", "grosor", "peso"]}
    all_targets_normalized = {target: [] for target in ["alto", "ancho", "grosor", "peso"]}
    
    with torch.no_grad():
        for batch_data in test_loader:
            images, pixel_features, targets = batch_data
            images = images.to(device)
            pixel_features = pixel_features.to(device)
            targets = targets.to(device)
            
            # Model returns (outputs, gating_values) with feature gating
            outputs, _ = model(images, pixel_features)
            # Use uncertainty-weighted loss from trainer
            loss, _ = trainer.criterion(outputs, targets)
            test_loss += loss.item()
            
            outputs_np = outputs.cpu().numpy()
            targets_np = targets.cpu().numpy()
            
            for i, target in enumerate(["alto", "ancho", "grosor", "peso"]):
                all_predictions_normalized[target].extend(outputs_np[:, i])
                all_targets_normalized[target].extend(targets_np[:, i])
    
    # Denormalize predictions and targets
    all_predictions_denorm = target_scaler.inverse_transform(all_predictions_normalized)
    all_targets_denorm = target_scaler.inverse_transform(all_targets_normalized)
    
    # Calculate test metrics on denormalized values
    from ..utils.metrics import calculate_metrics_per_target
    
    test_metrics = calculate_metrics_per_target(all_targets_denorm, all_predictions_denorm)
    
    results = {
        'history': history,
        'test_metrics': test_metrics,
        'best_epoch': trainer.best_epoch,
        'best_val_loss': trainer.best_val_loss,
        'model_path': str(model_save_path),
        'test_loss': test_loss / len(test_loader)
    }
    
    logger.info("Hybrid v2 training completed")
    return results

