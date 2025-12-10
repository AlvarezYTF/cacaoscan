"""
Base abstract trainer class for regression models.

This module provides a base class that extracts common functionality
from different trainer implementations, following SOLID principles:
- Single Responsibility: Each trainer handles one type of model
- Open/Closed: Base class is open for extension, closed for modification
- Liskov Substitution: All trainers can be used interchangeably
- Interface Segregation: Abstract methods define minimal required interface
- Dependency Inversion: Depends on abstractions (nn.Module, DataLoader)
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np

from ..utils.logs import get_ml_logger
from .scalers import CacaoScalers

logger = get_ml_logger("cacaoscan.ml.regression.base_trainer")


def _crear_scheduler_reduce_on_plateau(
    optimizer: optim.Optimizer,
    min_lr: float
) -> optim.lr_scheduler.ReduceLROnPlateau:
    """Crea un scheduler ReduceLROnPlateau."""
    return optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=5,
        verbose=True,
        min_lr=min_lr
    )


def _crear_scheduler_onecycle(
    optimizer: optim.Optimizer,
    learning_rate: float,
    epochs: int,
    steps_per_epoch: int
) -> optim.lr_scheduler.OneCycleLR:
    """Crea un scheduler OneCycleLR."""
    return optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=learning_rate * 10,
        epochs=epochs,
        steps_per_epoch=steps_per_epoch,
        pct_start=0.3
    )


def _crear_scheduler_cosine_warmup(
    optimizer: optim.Optimizer,
    epochs: int,
    min_lr: float
) -> optim.lr_scheduler.CosineAnnealingWarmRestarts:
    """Crea un scheduler CosineAnnealingWarmRestarts."""
    return optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer,
        T_0=max(1, epochs // 4),
        T_mult=2,
        eta_min=min_lr
    )


def _crear_scheduler_cosine(
    optimizer: optim.Optimizer,
    epochs: int,
    min_lr: float
) -> optim.lr_scheduler.CosineAnnealingLR:
    """Crea un scheduler CosineAnnealingLR."""
    return optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=epochs,
        eta_min=min_lr
    )


def _crear_criterion(loss_type: str) -> nn.Module:
    """Crea una función de pérdida según el tipo especificado."""
    if loss_type == 'mse':
        return nn.MSELoss()
    elif loss_type == 'huber':
        return nn.HuberLoss(delta=1.0)
    else:  # 'smooth_l1' (default)
        return nn.SmoothL1Loss()


class BaseTrainer(ABC):
    """
    Abstract base class for regression trainers.
    
    This class provides common functionality for:
    - Optimizer setup
    - Scheduler setup
    - Loss function setup
    - Batch preparation
    - Basic training/validation loops structure
    
    Subclasses must implement:
    - train_epoch() - Training logic for one epoch
    - validate_epoch() - Validation logic for one epoch
    - train() - Main training loop
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        scalers: Optional[CacaoScalers],
        device: torch.device,
        config: Dict[str, Any]
    ):
        """
        Initialize base trainer.
        
        Args:
            model: PyTorch model to train
            train_loader: Training data loader
            val_loader: Validation data loader
            scalers: Optional scalers for denormalization
            device: Device to use (cuda/cpu)
            config: Training configuration dictionary
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.scalers = scalers
        self.device = device
        self.config = config
        
        # Setup training components
        self.optimizer = self._setup_optimizer()
        self.scheduler = self._setup_scheduler()
        self.criterion = self._setup_loss_function()
        
        # Training state
        self.history: Dict[str, List[float]] = {}
        self.best_val_loss = float('inf')
        self.best_model_state: Optional[Dict] = None
        self.patience_counter = 0
        
        logger.info(f"BaseTrainer initialized for {type(model).__name__}")
    
    def _validate_learning_rate(self, learning_rate: float) -> float:
        """Validate and adjust learning rate if necessary."""
        if learning_rate > 5e-4:
            logger.warning(f"Learning rate {learning_rate} may be too high. Reducing to 5e-4")
            return 5e-4
        if learning_rate < 1e-7:
            logger.warning(f"Learning rate {learning_rate} may be too low. Increasing to 1e-7")
            return 1e-7
        return learning_rate
    
    def _setup_optimizer(self) -> optim.Optimizer:
        """
        Setup optimizer based on configuration.
        
        Returns:
            Configured optimizer (AdamW by default)
        """
        learning_rate = self._validate_learning_rate(
            self.config.get('learning_rate', 1e-4)
        )
        
        weight_decay = self.config.get('weight_decay', 1e-4)
        
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.999),
            eps=1e-8
        )
        
        logger.info(f"Optimizer: AdamW (lr={learning_rate:.2e}, weight_decay={weight_decay:.2e})")
        return optimizer
    
    def _setup_scheduler(self) -> optim.lr_scheduler._LRScheduler:
        """
        Setup learning rate scheduler based on configuration.
        
        Returns:
            Configured scheduler
        """
        scheduler_type = self.config.get('scheduler_type', 'reduce_on_plateau')
        epochs = self.config.get('epochs', 50)
        learning_rate = self.config.get('learning_rate', 1e-4)
        min_lr = self.config.get('min_lr', 1e-7)
        
        if scheduler_type == 'reduce_on_plateau':
            scheduler = _crear_scheduler_reduce_on_plateau(self.optimizer, min_lr)
        elif scheduler_type == 'onecycle':
            scheduler = _crear_scheduler_onecycle(
                self.optimizer, learning_rate, epochs, len(self.train_loader)
            )
        elif scheduler_type == 'cosine_warmup':
            scheduler = _crear_scheduler_cosine_warmup(self.optimizer, epochs, min_lr)
        else:  # 'cosine' or default
            scheduler = _crear_scheduler_cosine(self.optimizer, epochs, min_lr)
        
        logger.info(f"Scheduler: {scheduler_type}")
        return scheduler
    
    def _setup_loss_function(self) -> nn.Module:
        """
        Setup loss function based on configuration.
        
        Returns:
            Configured loss function
        """
        loss_type = self.config.get('loss_type', 'smooth_l1')
        criterion = _crear_criterion(loss_type)
        logger.info(f"Loss function: {loss_type}")
        return criterion
    
    def _prepare_batch_inputs(
        self,
        batch_data: Tuple,
        use_pixel_features: bool = False,
        non_blocking: bool = False
    ) -> Optional[Tuple[Tuple, Any]]:
        """
        Prepare batch inputs for model forward pass.
        
        Args:
            batch_data: Batch data from DataLoader
            use_pixel_features: Whether to use pixel features (hybrid models)
            non_blocking: Whether to use non-blocking transfer
            
        Returns:
            Tuple of (inputs_tuple, targets) or None if invalid
        """
        if use_pixel_features:
            if len(batch_data) != 3:
                logger.error(f"Expected 3 tensors for hybrid model, got {len(batch_data)}")
                return None
            images, targets_batch, pixel_features = batch_data
            images = images.to(self.device, non_blocking=non_blocking)
            pixel_features = pixel_features.to(self.device, non_blocking=non_blocking)
            return (images, pixel_features), targets_batch
        else:
            if len(batch_data) != 2:
                logger.error(f"Expected 2 tensors, got {len(batch_data)}")
                return None
            images, targets_batch = batch_data
            images = images.to(self.device, non_blocking=non_blocking)
            return (images,), targets_batch
    
    def _update_scheduler(self, val_loss: Optional[float] = None) -> float:
        """
        Update learning rate scheduler and return current LR.
        
        Args:
            val_loss: Validation loss (required for ReduceLROnPlateau)
            
        Returns:
            Current learning rate
        """
        if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            if val_loss is None:
                logger.warning("ReduceLROnPlateau requires val_loss, using current val_loss")
                val_loss = self.best_val_loss if self.best_val_loss != float('inf') else 1.0
            self.scheduler.step(val_loss)
            return self.optimizer.param_groups[0]['lr']
        elif isinstance(self.scheduler, optim.lr_scheduler.OneCycleLR):
            # OneCycleLR is updated in each optimizer step
            return self.optimizer.param_groups[0]['lr']
        else:
            self.scheduler.step()
            return (
                self.scheduler.get_last_lr()[0]
                if hasattr(self.scheduler, 'get_last_lr')
                else self.optimizer.param_groups[0]['lr']
            )
    
    def _check_early_stopping(
        self,
        val_loss: float,
        improvement_threshold: float = 1e-4
    ) -> Tuple[bool, bool]:
        """
        Check if early stopping should be triggered.
        
        Args:
            val_loss: Current validation loss
            improvement_threshold: Minimum improvement to reset patience
            
        Returns:
            Tuple of (should_stop, is_best)
        """
        early_stopping_patience = self.config.get('early_stopping_patience', 10)
        
        if val_loss < self.best_val_loss - improvement_threshold:
            self.best_val_loss = val_loss
            self.patience_counter = 0
            self.best_model_state = self.model.state_dict().copy()
            return False, True
        
        self.patience_counter += 1
        
        if self.patience_counter >= early_stopping_patience:
            return True, False
        
        return False, False
    
    def _save_model(self, file_path: Path, model_info: Optional[Dict] = None) -> None:
        """
        Save model to file.
        
        Args:
            file_path: Path to save model
            model_info: Additional model information to save
        """
        from datetime import datetime
        from ..utils.paths import ensure_dir_exists
        
        ensure_dir_exists(file_path.parent)
        
        save_dict = {
            'model_state_dict': self.model.state_dict(),
            'model_info': model_info or {},
            'config': self.config,
            'best_val_loss': self.best_val_loss,
            'training_history': self.history,
            'timestamp': datetime.now().isoformat()
        }
        
        torch.save(save_dict, file_path)
        
        if file_path.exists() and file_path.stat().st_size > 0:
            logger.info(f"Model saved successfully to {file_path}")
        else:
            raise IOError(f"Failed to save model to {file_path}")
    
    @abstractmethod
    def train_epoch(self) -> float:
        """
        Train model for one epoch.
        
        Returns:
            Average training loss for the epoch
        """
        pass
    
    @abstractmethod
    def validate_epoch(self) -> Tuple[float, ...]:
        """
        Validate model for one epoch.
        
        Returns:
            Tuple of validation metrics (loss, mae, rmse, r2, etc.)
        """
        pass
    
    @abstractmethod
    def train(self) -> Dict[str, List[float]]:
        """
        Main training loop.
        
        Returns:
            Training history dictionary
        """
        pass

