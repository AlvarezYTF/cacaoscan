"""
Intelligent early stopping with variance and R² monitoring.
"""
from typing import Dict, Tuple, Optional
import numpy as np

from .logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.utils.early_stopping")


class IntelligentEarlyStopping:
    """
    Early stopping with advanced rules:
    - Patience = 8
    - Minimum improvement in Val Loss: 1%
    - If any R² < -2 for 2 consecutive epochs → reduce LR by half
    - If Val Loss increases 3 consecutive epochs → rollback to best checkpoint
    """
    
    TARGETS = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(
        self,
        patience: int = 8,
        min_delta_percent: float = 0.01,  # 1%
        r2_threshold: float = -2.0,
        r2_consecutive: int = 2,
        val_loss_increase_epochs: int = 3
    ):
        """
        Initialize early stopping.
        
        Args:
            patience: Number of epochs to wait
            min_delta_percent: Minimum improvement percentage (1% = 0.01)
            r2_threshold: R² threshold for triggering LR reduction
            r2_consecutive: Consecutive epochs with R² < threshold to trigger action
            val_loss_increase_epochs: Consecutive epochs with increasing val_loss to trigger rollback
        """
        self.patience = patience
        self.min_delta_percent = min_delta_percent
        self.r2_threshold = r2_threshold
        self.r2_consecutive = r2_consecutive
        self.val_loss_increase_epochs = val_loss_increase_epochs
        
        self.best_val_loss = float('inf')
        self.best_epoch = 0
        self.counter = 0
        
        # Track consecutive epochs with low R²
        self.low_r2_count: Dict[str, int] = {target: 0 for target in self.TARGETS}
        
        # Track consecutive epochs with increasing val_loss
        self.val_loss_increase_count = 0
        self.last_val_loss = float('inf')
        
        logger.info(
            f"IntelligentEarlyStopping initialized: "
            f"patience={patience}, min_delta={min_delta_percent*100}%, "
            f"r2_threshold={r2_threshold}, r2_consecutive={r2_consecutive}, "
            f"val_loss_increase_epochs={val_loss_increase_epochs}"
        )
    
    def __call__(
        self,
        epoch: int,
        val_loss: float,
        r2_scores: Dict[str, float],
        optimizer: Optional[object] = None
    ) -> Tuple[bool, bool, bool, bool]:
        """
        Check if training should stop or take action.
        
        Args:
            epoch: Current epoch
            val_loss: Validation loss
            r2_scores: R² scores per target
            optimizer: Optimizer instance (for LR reduction)
            
        Returns:
            Tuple of (should_stop, is_best, should_reduce_lr, should_rollback)
        """
        should_reduce_lr = False
        should_rollback = False
        
        # Check minimum improvement (1%)
        min_delta = self.best_val_loss * self.min_delta_percent
        is_best = val_loss < self.best_val_loss - min_delta
        
        # Check for low R² (consecutive epochs)
        for target in self.TARGETS:
            r2 = r2_scores.get(target, -float('inf'))
            if r2 < self.r2_threshold:
                self.low_r2_count[target] += 1
                if self.low_r2_count[target] >= self.r2_consecutive:
                    should_reduce_lr = True
                    logger.warning(
                        f"Target {target} has R² < {self.r2_threshold} for "
                        f"{self.low_r2_count[target]} consecutive epochs. "
                        f"Triggering LR reduction."
                    )
            else:
                self.low_r2_count[target] = 0
        
        # Check for increasing val_loss
        if val_loss > self.last_val_loss:
            self.val_loss_increase_count += 1
            if self.val_loss_increase_count >= self.val_loss_increase_epochs:
                should_rollback = True
                logger.warning(
                    f"Val loss increased for {self.val_loss_increase_count} consecutive epochs. "
                    f"Triggering rollback to best checkpoint."
                )
        else:
            self.val_loss_increase_count = 0
        
        self.last_val_loss = val_loss
        
        # Update best model
        if is_best:
            self.best_val_loss = val_loss
            self.best_epoch = epoch
            self.counter = 0
            logger.info(
                f"Epoch {epoch}: New best model (val_loss={val_loss:.4f}, "
                f"improvement={min_delta:.4f})"
            )
        else:
            self.counter += 1
            logger.debug(
                f"Epoch {epoch}: No improvement (counter={self.counter}/{self.patience})"
            )
        
        # Reduce LR if needed
        if should_reduce_lr and optimizer is not None:
            current_lr = optimizer.param_groups[0]['lr']
            new_lr = current_lr * 0.5
            for param_group in optimizer.param_groups:
                param_group['lr'] = new_lr
            logger.info(f"LR reduced from {current_lr:.2e} to {new_lr:.2e}")
        
        # Check if should stop
        should_stop = self.counter >= self.patience
        
        if should_stop:
            logger.info(
                f"Early stopping triggered at epoch {epoch}. "
                f"Best model was at epoch {self.best_epoch} "
                f"(val_loss={self.best_val_loss:.4f})"
            )
        
        return should_stop, is_best, should_reduce_lr, should_rollback
    
    def reset(self) -> None:
        """Reset early stopping state."""
        self.best_val_loss = float('inf')
        self.best_epoch = 0
        self.counter = 0
        self.low_r2_count = {target: 0 for target in self.TARGETS}
        self.val_loss_increase_count = 0
        self.last_val_loss = float('inf')
        logger.info("Early stopping state reset")
