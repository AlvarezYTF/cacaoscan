"""
Advanced hybrid trainer with uncertainty-based loss, feature gating, and comprehensive logging.
"""
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
import numpy as np
from scipy.stats import pearsonr

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir
from ..utils.losses import UncertaintyWeightedLoss
from ..utils.early_stopping import IntelligentEarlyStopping
from .metrics import calculate_metrics_per_target, print_metrics_summary

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
    CHECKPOINT_BEST_LOSS = "best_loss.pt"
    
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
            # Handle 0D tensor (scalar) - convert to 1D array
            gating_np = gating_values.detach().cpu().numpy()
            if gating_np.ndim == 0:
                # 0D tensor (scalar) - convert to list
                gating_values_list.append(float(gating_np))
            else:
                # 1D or higher tensor - flatten and extend
                gating_values_list.extend(gating_np.flatten().tolist())
            
            # Validate loss
            if not torch.isfinite(loss):
                logger.error(f"Non-finite loss at batch {batch_idx}: {loss.item()}")
                continue
            
            train_loss += loss.item()
            n_batches += 1
        
        avg_loss = train_loss / max(n_batches, 1)
        avg_gating = np.mean(gating_values_list) if gating_values_list else 0.0
        
        return avg_loss, max_grad, avg_gating
    
    def _normalize_tensor_to_2d(self, tensor_np, tensor_original):
        """Normalize tensor to 2D shape for metrics calculation."""
        if tensor_np.ndim == 0:
            return tensor_np.reshape(1, -1) if hasattr(tensor_original, 'shape') else np.array([[tensor_np]])
        if tensor_np.ndim == 1:
            return tensor_np.reshape(1, -1)
        return tensor_np
    
    def _process_validation_batch(self, batch_data, all_predictions, all_targets):
        """Process a single validation batch and update predictions/targets."""
        if len(batch_data) != 3:
            return 0.0, False
        
        images, pixel_features, targets = batch_data
        images = images.to(self.device, non_blocking=True)
        pixel_features = pixel_features.to(self.device, non_blocking=True)
        targets = targets.to(self.device, non_blocking=True)
        
        if self.use_mixed_precision:
            with autocast():
                outputs, _ = self.model(images, pixel_features)
                loss, _ = self.criterion(outputs, targets)
        else:
            outputs, _ = self.model(images, pixel_features)
            loss, _ = self.criterion(outputs, targets)
        
        outputs_np = self._normalize_tensor_to_2d(outputs.cpu().numpy(), outputs)
        targets_np = self._normalize_tensor_to_2d(targets.cpu().numpy(), targets)
        
        for i, target in enumerate(self.TARGETS):
            if outputs_np.shape[1] > i and targets_np.shape[1] > i:
                all_predictions[target].extend(outputs_np[:, i].tolist())
                all_targets[target].extend(targets_np[:, i].tolist())
        
        return loss.item(), True
    
    def _calculate_pearson_correlations(self, all_targets, all_predictions):
        """Calculate Pearson correlations for all targets."""
        pearson_corrs = {}
        for target in self.TARGETS:
            try:
                corr, _ = pearsonr(all_targets[target], all_predictions[target])
                pearson_corrs[target] = float(corr)
            except Exception:
                pearson_corrs[target] = 0.0
        return pearson_corrs
    
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
                loss_value, processed = self._process_validation_batch(batch_data, all_predictions, all_targets)
                if processed:
                    val_loss += loss_value
                    n_batches += 1
        
        avg_loss = val_loss / max(n_batches, 1)
        metrics = calculate_metrics_per_target(all_targets, all_predictions)
        pearson_corrs = self._calculate_pearson_correlations(all_targets, all_predictions)
        sigmas = self.criterion.get_sigmas()
        
        return avg_loss, metrics, sigmas, pearson_corrs
    
    def _update_training_history(self, train_loss: float, val_loss: float, current_lr: float,
                                avg_r2: float, max_grad: float, avg_gating: float,
                                metrics: Dict[str, Dict[str, float]], pearson_corrs: Dict[str, float],
                                sigmas: Dict[str, float]):
        """Update training history with epoch metrics."""
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
    
    def _log_epoch_metrics(self, epoch: int, epochs: int, train_loss: float, val_loss: float,
                          avg_r2: float, current_lr: float, epoch_time: float,
                          metrics: Dict[str, Dict[str, float]], sigmas: Dict[str, float],
                          pearson_corrs: Dict[str, float], max_grad: float, avg_gating: float):
        """Log comprehensive epoch metrics."""
        logger.info(
            f"Epoch {epoch+1}/{epochs} - "
            f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
            f"Avg R²: {avg_r2:.4f}, LR: {current_lr:.2e}, Time: {epoch_time:.2f}s"
        )
        
        print_metrics_summary(metrics, epoch=epoch+1)
        logger.info(f"  Sigmas: {sigmas}")
        logger.info(f"  Pearson: {pearson_corrs}")
        logger.info(f"  Max Gradient: {max_grad:.4f}, Gating %: {avg_gating*100:.2f}%")
    
    def _resolve_epochs(self, max_epochs: int = None, epochs: int = None) -> int:
        """Resolve number of epochs from parameters."""
        if max_epochs is not None:
            return max_epochs
        if epochs is not None:
            return epochs
        return self.config.get('epochs', 50)
    
    def _save_best_loss_checkpoint(self, epoch: int, val_loss: float):
        """Save best loss checkpoint."""
        self.best_val_loss = val_loss
        self.best_epoch_loss = epoch
        self._save_checkpoint(epoch, self.CHECKPOINT_BEST_LOSS, is_best_loss=True)
        logger.info(f"New best loss model saved (val_loss={val_loss:.4f})")
        if self.save_dir:
            self.rollback_checkpoint = self.save_dir / self.CHECKPOINT_BEST_LOSS
    
    def _save_best_r2_checkpoint(self, epoch: int, avg_r2: float):
        """Save best R² checkpoint."""
        self.best_avg_r2 = avg_r2
        self.best_epoch_r2 = epoch
        self._save_checkpoint(epoch, "best_avg_r2.pt", is_best_r2=True)
        logger.info(f"New best R² model saved (avg_r2={avg_r2:.4f})")
    
    def _save_best_checkpoints(self, epoch: int, val_loss: float, avg_r2: float):
        """Save best loss and best R² checkpoints."""
        if val_loss < self.best_val_loss:
            self._save_best_loss_checkpoint(epoch, val_loss)
        
        if avg_r2 > self.best_avg_r2:
            self._save_best_r2_checkpoint(epoch, avg_r2)
    
    def _handle_early_stopping(self, epoch: int, val_loss: float, metrics: Dict[str, Dict[str, float]]) -> bool:
        """Handle early stopping logic and return True if should stop."""
        r2_scores = {target: metrics[target]['r2'] for target in self.TARGETS}
        should_stop, _, _, should_rollback = self.early_stopping(
            epoch, val_loss, r2_scores, self.optimizer
        )
        
        if should_rollback and self.rollback_checkpoint is not None:
            logger.warning("Rolling back to best checkpoint")
            self._load_checkpoint(self.rollback_checkpoint)
        
        if should_stop:
            logger.info(f"Early stopping triggered at epoch {epoch}")
        
        return should_stop
    
    def _train_single_epoch(self, epoch: int, epochs: int) -> bool:
        """
        Train and validate for a single epoch.
        
        Args:
            epoch: Current epoch index (0-based)
            epochs: Total number of epochs
            
        Returns:
            True if training should stop (early stopping), False otherwise
        """
        epoch_start = time.time()
        
        train_loss, max_grad, avg_gating = self.train_epoch()
        val_loss, metrics, sigmas, pearson_corrs = self.validate_epoch()
        
        self.scheduler.step()
        current_lr = self.optimizer.param_groups[0]['lr']
        avg_r2 = np.mean([metrics[target]['r2'] for target in self.TARGETS])
        
        self._update_training_history(
            train_loss, val_loss, current_lr, avg_r2, max_grad, avg_gating,
            metrics, pearson_corrs, sigmas
        )
        
        epoch_time = time.time() - epoch_start
        self._log_epoch_metrics(
            epoch, epochs, train_loss, val_loss, avg_r2, current_lr, epoch_time,
            metrics, sigmas, pearson_corrs, max_grad, avg_gating
        )
        
        self._save_best_checkpoints(epoch + 1, val_loss, avg_r2)
        self._save_checkpoint(epoch + 1, "last_epoch.pt")
        
        return self._handle_early_stopping(epoch + 1, val_loss, metrics)
    
    def train(self, max_epochs: int = None, epochs: int = None) -> Dict[str, List[float]]:
        """
        Train the model for multiple epochs.
        
        Args:
            max_epochs: Number of epochs to train (preferred parameter name)
            epochs: Number of epochs to train (backward compatibility)
            
        Returns:
            Training history
        """
        epochs = self._resolve_epochs(max_epochs, epochs)
        logger.info(f"Starting training for {epochs} epochs")
        start_time = time.time()
        
        for epoch in range(epochs):
            if self._train_single_epoch(epoch, epochs):
                break
        
        total_time = time.time() - start_time
        logger.info(f"Training completed in {total_time:.2f}s")
        logger.info(f"Best validation loss: {self.best_val_loss:.4f} at epoch {self.best_epoch_loss}")
        logger.info(f"Best average R²: {self.best_avg_r2:.4f} at epoch {self.best_epoch_r2}")
        
        return self.history
    
    def _save_checkpoint(
        self,
        epoch: int,
        filename: str = None,
        is_best_loss: bool = False,
        is_best_r2: bool = False
    ) -> Optional[Path]:
        """
        Save model checkpoint.
        
        Args:
            epoch: Current epoch number
            filename: Filename for checkpoint (if None, auto-generate based on flags)
            is_best_loss: Whether this is the best loss model so far
            is_best_r2: Whether this is the best R² model so far
            
        Returns:
            Path to saved checkpoint or None if save_dir is not set
        """
        if self.save_dir is None:
            return None
        
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-generate filename if not provided
        if filename is None:
            if is_best_loss:
                filename = self.CHECKPOINT_BEST_LOSS
            elif is_best_r2:
                filename = "best_avg_r2.pt"
            else:
                filename = "last_epoch.pt"
        
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
        return checkpoint_path
    
    def _validate_checkpoint_structure(self, checkpoint: dict, required_keys: list) -> None:
        """Validate checkpoint structure and content."""
        if not all(key in checkpoint for key in required_keys):
            raise ValueError(f"Invalid checkpoint structure. Missing required keys: {required_keys}")
        
        for key in required_keys:
            if not isinstance(checkpoint[key], dict):
                raise ValueError(f"Invalid checkpoint: {key} is not a dictionary")
            if checkpoint[key] and not all(isinstance(k, str) for k in checkpoint[key].keys()):
                raise ValueError(f"Invalid checkpoint: {key} has non-string keys")
            for subkey, value in checkpoint[key].items():
                if not isinstance(value, torch.Tensor):
                    raise ValueError(f"Invalid checkpoint: {key}[{subkey}] is not a tensor")
    
    def _load_state_dicts(self, checkpoint: dict) -> None:
        """Load all state dicts from checkpoint."""
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.criterion.load_state_dict(checkpoint['criterion_state_dict'])
        
        if self.scaler is not None and 'scaler_state_dict' in checkpoint:
            if isinstance(checkpoint['scaler_state_dict'], dict):
                self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
            else:
                logger.warning("Invalid scaler_state_dict in checkpoint, skipping")
    
    def _load_checkpoint(self, checkpoint_path: Path) -> None:
        """
        Load checkpoint for rollback.
        
        Security note: This function loads checkpoints created by this trainer.
        Checkpoints should only be loaded from trusted sources (same training system).
        The checkpoint structure is validated after loading to detect tampering.
        
        SECURITY: Uses weights_only=True to prevent arbitrary code execution (S6985).
        This ensures only model weights and state_dicts are loaded, not arbitrary Python objects.
        """
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_path}")
            return
        
        try:
            # SECURITY: Use weights_only=True to prevent arbitrary code execution (S6985)
            # This is the safest way to load PyTorch checkpoints (available in PyTorch 2.1+)
            # Checkpoints are created by our own _save_checkpoint method which only saves
            # state_dicts (dictionaries of tensors), not arbitrary Python objects
            try:
                # Try to load with weights_only=True (safest method, PyTorch 2.1+)
                # SECURITY: weights_only=True prevents arbitrary code execution (S6985)
                checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
            except TypeError as exc:
                raise RuntimeError(
                    "La versión de PyTorch instalada no soporta weights_only=True. "
                    "Actualiza a PyTorch 2.1 o superior para cargar checkpoints de forma segura "
                    f"(archivo: {checkpoint_path})."
                ) from exc
            
            # Validate checkpoint structure to ensure it's a valid checkpoint from our trainer
            # This helps detect if a checkpoint was tampered with
            required_keys = ['model_state_dict', 'optimizer_state_dict', 
                           'scheduler_state_dict', 'criterion_state_dict']
            self._validate_checkpoint_structure(checkpoint, required_keys)
            self._load_state_dicts(checkpoint)
            
            logger.info(f"Loaded checkpoint safely from {checkpoint_path}")
        except Exception as e:
            logger.error(f"Error loading checkpoint from {checkpoint_path}: {e}")
            raise
