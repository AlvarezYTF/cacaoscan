"""
Advanced hybrid trainer with uncertainty-based loss, feature gating, and comprehensive logging.
"""
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
import numpy as np
from scipy.stats import pearsonr

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir
from ..utils.metrics import calculate_metrics_per_target, print_metrics_summary
from ..utils.losses import UncertaintyWeightedLoss
from ..utils.early_stopping import IntelligentEarlyStopping

logger = get_ml_logger("cacaoscan.ml.regression.hybrid_trainer")


class HybridTrainer:
    """
    Advanced trainer for hybrid cacao regression.
    
    Features:
    - Uncertainty-based multi-task loss (Kendall et al.)
    - Feature gating fusion
    - CosineAnnealingWarmRestarts scheduler
    - Intelligent early stopping with rollback
    - Comprehensive logging (R², σ_i, Pearson, gradients, gating %)
    - Multiple checkpoint saving (best_loss, best_avg_r2, last_epoch)
    """
    
    TARGETS = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: torch.device,
        config: Dict,
        save_dir: Optional[Path] = None,
        use_mixed_precision: bool = True
    ):
        """
        Initialize the trainer.
        
        Args:
            model: Hybrid model instance
            train_loader: Training data loader
            val_loader: Validation data loader
            device: Device to use (cuda/cpu)
            config: Training configuration
            save_dir: Directory to save checkpoints
            use_mixed_precision: Use mixed precision training
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.config = config
        self.save_dir = Path(save_dir) if save_dir else None
        self.use_mixed_precision = use_mixed_precision and device.type == 'cuda'
        
        # Optimizer: AdamW(lr=1e-4, weight_decay=0.01)
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config.get('learning_rate', 1e-4),
            weight_decay=0.01
        )
        
        # Uncertainty-weighted loss (Kendall et al.)
        logger.info("Initializing UncertaintyWeightedLoss with initial_sigma=0.3")
        self.criterion = UncertaintyWeightedLoss(initial_sigma=0.3)
        self.criterion = self.criterion.to(device)
        logger.info("UncertaintyWeightedLoss moved to device and ready")
        
        # Scheduler: CosineAnnealingWarmRestarts(T=10)
        self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=10,
            T_mult=1,
            eta_min=1e-6
        )
        
        # Intelligent early stopping
        early_stopping_patience = config.get('early_stopping_patience', 15)
        self.early_stopping = IntelligentEarlyStopping(
            patience=early_stopping_patience,  # Usa config
            min_delta_percent=0.005,  # Reducido de 1% a 0.5% para detectar mejoras pequeñas
            r2_threshold=-2.0,
            r2_consecutive=2,
            val_loss_increase_epochs=3
        )
        
        # Mixed precision scaler
        if self.use_mixed_precision:
            self.scaler = GradScaler()
            logger.info("Mixed precision training enabled")
        else:
            self.scaler = None
        
        # Training history
        self.history: Dict[str, List[float]] = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': [],
            'avg_r2': [],
            'max_gradient': [],
            'gating_percentage': []
        }
        
        for target in self.TARGETS:
            self.history[f'val_r2_{target}'] = []
            self.history[f'val_mae_{target}'] = []
            self.history[f'val_rmse_{target}'] = []
            self.history[f'pearson_{target}'] = []
            self.history[f'sigma_{target}'] = []
        
        # Best model tracking
        self.best_val_loss = float('inf')
        self.best_avg_r2 = -float('inf')
        self.best_epoch_loss = 0
        self.best_epoch_r2 = 0
        
        # Rollback checkpoint
        self.rollback_checkpoint = None
        
        logger.info("Hybrid trainer initialized with uncertainty-based loss and feature gating")
    
    def train_epoch(self) -> Tuple[float, float, float]:
        """
        Train for one epoch.
        
        Returns:
            Tuple of (avg_loss, max_gradient, avg_gating_percentage)
        """
        self.model.train()
        train_loss = 0.0
        n_batches = 0
        max_grad = 0.0
        gating_values_list = []
        
        for batch_idx, batch_data in enumerate(self.train_loader):
            # Unpack batch: (images, pixel_features, targets)
            if len(batch_data) != 3:
                logger.error(f"Expected 3 tensors, got {len(batch_data)}")
                continue
            
            images, pixel_features, targets = batch_data
            images = images.to(self.device, non_blocking=True)
            pixel_features = pixel_features.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            # Forward pass with mixed precision
            self.optimizer.zero_grad()
            
            if self.use_mixed_precision:
                with autocast():
                    outputs, gating_values = self.model(images, pixel_features)  # [batch, 4], [batch, 1]
                    
                    # Compute uncertainty-weighted loss
                    loss, _ = self.criterion(outputs, targets)
                
                # Backward pass with gradient scaling
                self.scaler.scale(loss).backward()
                
                # Track max gradient
                self.scaler.unscale_(self.optimizer)
                grad_norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=10.0)
                max_grad = max(max_grad, grad_norm.item())
                
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs, gating_values = self.model(images, pixel_features)
                
                # Compute uncertainty-weighted loss
                loss, _ = self.criterion(outputs, targets)
                
                # Backward pass
                loss.backward()
                
                # Track max gradient
                grad_norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=10.0)
                max_grad = max(max_grad, grad_norm.item())
                
                self.optimizer.step()
            
            # Track gating values
            gating_values_list.extend(gating_values.detach().cpu().numpy().flatten())
            
            # Validate loss
            if not torch.isfinite(loss):
                logger.error(f"Non-finite loss at batch {batch_idx}: {loss.item()}")
                continue
            
            train_loss += loss.item()
            n_batches += 1
        
        avg_loss = train_loss / max(n_batches, 1)
        avg_gating = np.mean(gating_values_list) if gating_values_list else 0.0
        
        return avg_loss, max_grad, avg_gating
    
    def validate_epoch(self) -> Tuple[float, Dict[str, Dict[str, float]], Dict[str, float]]:
        """
        Validate for one epoch.
        
        Returns:
            Tuple of (avg_loss, metrics_per_target, sigmas_dict)
        """
        self.model.eval()
        val_loss = 0.0
        n_batches = 0
        
        all_predictions = {target: [] for target in self.TARGETS}
        all_targets = {target: [] for target in self.TARGETS}
        
        with torch.no_grad():
            for batch_data in self.val_loader:
                if len(batch_data) != 3:
                    continue
                
                images, pixel_features, targets = batch_data
                images = images.to(self.device, non_blocking=True)
                pixel_features = pixel_features.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                
                # Forward pass
                if self.use_mixed_precision:
                    with autocast():
                        outputs, _ = self.model(images, pixel_features)
                        loss, _ = self.criterion(outputs, targets)
                else:
                    outputs, _ = self.model(images, pixel_features)
                    loss, _ = self.criterion(outputs, targets)
                
                val_loss += loss.item()
                n_batches += 1
                
                # Store predictions and targets for metrics
                outputs_np = outputs.cpu().numpy()
                targets_np = targets.cpu().numpy()
                
                for i, target in enumerate(self.TARGETS):
                    all_predictions[target].extend(outputs_np[:, i])
                    all_targets[target].extend(targets_np[:, i])
        
        avg_loss = val_loss / max(n_batches, 1)
        
        # Calculate metrics per target
        metrics = calculate_metrics_per_target(all_targets, all_predictions)
        
        # Calculate Pearson correlations
        pearson_corrs = {}
        for target in self.TARGETS:
            try:
                corr, _ = pearsonr(all_targets[target], all_predictions[target])
                pearson_corrs[target] = float(corr)
            except Exception:
                pearson_corrs[target] = 0.0
        
        # Get sigmas
        sigmas = self.criterion.get_sigmas()
        
        return avg_loss, metrics, sigmas, pearson_corrs
    
    def train(self, epochs: int) -> Dict[str, List[float]]:
        """
        Train the model for multiple epochs.
        
        Args:
            epochs: Number of epochs to train
            
        Returns:
            Training history
        """
        logger.info(f"Starting training for {epochs} epochs")
        start_time = time.time()
        
        for epoch in range(epochs):
            epoch_start = time.time()
            
            # Train
            train_loss, max_grad, avg_gating = self.train_epoch()
            
            # Validate
            val_loss, metrics, sigmas, pearson_corrs = self.validate_epoch()
            
            # Update scheduler
            self.scheduler.step()
            current_lr = self.optimizer.param_groups[0]['lr']
            
            # Calculate average R²
            avg_r2 = np.mean([metrics[target]['r2'] for target in self.TARGETS])
            
            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['learning_rate'].append(current_lr)
            self.history['avg_r2'].append(avg_r2)
            self.history['max_gradient'].append(max_grad)
            self.history['gating_percentage'].append(avg_gating * 100)
            
            for target in self.TARGETS:
                self.history[f'val_r2_{target}'].append(metrics[target]['r2'])
                self.history[f'val_mae_{target}'].append(metrics[target]['mae'])
                self.history[f'val_rmse_{target}'].append(metrics[target]['rmse'])
                self.history[f'pearson_{target}'].append(pearson_corrs[target])
                self.history[f'sigma_{target}'].append(sigmas[target])
            
            # Log comprehensive metrics
            epoch_time = time.time() - epoch_start
            logger.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                f"Avg R²: {avg_r2:.4f}, LR: {current_lr:.2e}, Time: {epoch_time:.2f}s"
            )
            
            # Print detailed metrics
            print_metrics_summary(metrics, epoch=epoch+1)
            
            # Log sigmas
            logger.info(f"  Sigmas: {sigmas}")
            
            # Log Pearson correlations
            logger.info(f"  Pearson: {pearson_corrs}")
            
            # Log gradient and gating
            logger.info(f"  Max Gradient: {max_grad:.4f}, Gating %: {avg_gating*100:.2f}%")
            
            # Check early stopping
            r2_scores = {target: metrics[target]['r2'] for target in self.TARGETS}
            should_stop, is_best_loss, should_reduce_lr, should_rollback = self.early_stopping(
                epoch + 1,
                val_loss,
                r2_scores,
                self.optimizer
            )
            
            # Save checkpoints
            if is_best_loss:
                self.best_val_loss = val_loss
                self.best_epoch_loss = epoch + 1
                self._save_checkpoint(epoch + 1, "best_loss.pt", is_best=True)
                logger.info(f"New best loss model saved (val_loss={val_loss:.4f})")
            
            if avg_r2 > self.best_avg_r2:
                self.best_avg_r2 = avg_r2
                self.best_epoch_r2 = epoch + 1
                self._save_checkpoint(epoch + 1, "best_avg_r2.pt", is_best=True)
                logger.info(f"New best R² model saved (avg_r2={avg_r2:.4f})")
            
            # Save last epoch
            self._save_checkpoint(epoch + 1, "last_epoch.pt", is_best=False)
            
            # Rollback if needed
            if should_rollback and self.rollback_checkpoint is not None:
                logger.warning("Rolling back to best checkpoint")
                self._load_checkpoint(self.rollback_checkpoint)
            
            # Update rollback checkpoint
            if is_best_loss:
                self.rollback_checkpoint = self.save_dir / "best_loss.pt" if self.save_dir else None
            
            # Early stopping
            if should_stop:
                logger.info(f"Early stopping triggered at epoch {epoch+1}")
                break
        
        total_time = time.time() - start_time
        logger.info(f"Training completed in {total_time:.2f}s")
        logger.info(f"Best validation loss: {self.best_val_loss:.4f} at epoch {self.best_epoch_loss}")
        logger.info(f"Best average R²: {self.best_avg_r2:.4f} at epoch {self.best_epoch_r2}")
        
        return self.history
    
    def _save_checkpoint(
        self,
        epoch: int,
        filename: str,
        is_best: bool = False
    ) -> None:
        """
        Save model checkpoint.
        
        Args:
            epoch: Current epoch number
            filename: Filename for checkpoint
            is_best: Whether this is the best model so far
        """
        if self.save_dir is None:
            return
        
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'criterion_state_dict': self.criterion.state_dict(),
            'val_loss': self.history['val_loss'][-1] if self.history['val_loss'] else float('inf'),
            'avg_r2': self.history['avg_r2'][-1] if self.history['avg_r2'] else -float('inf'),
            'history': self.history,
            'config': self.config
        }
        
        if self.scaler is not None:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()
        
        checkpoint_path = self.save_dir / filename
        torch.save(checkpoint, checkpoint_path)
        logger.debug(f"Saved checkpoint: {checkpoint_path}")
    
    def _load_checkpoint(self, checkpoint_path: Path) -> None:
        """Load checkpoint for rollback."""
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_path}")
            return
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.criterion.load_state_dict(checkpoint['criterion_state_dict'])
        
        if self.scaler is not None and 'scaler_state_dict' in checkpoint:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
        
        logger.info(f"Loaded checkpoint from {checkpoint_path}")
