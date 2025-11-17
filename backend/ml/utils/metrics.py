"""
Metrics utilities for regression evaluation.
"""
import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import logging

from .logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.utils.metrics")


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_name: str = ""
) -> Dict[str, float]:
    """
    Calculate regression metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        target_name: Name of target (for logging)
        
    Returns:
        Dictionary with metrics
    """
    # Flatten arrays
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    
    # Remove any NaN or Inf values
    valid_mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if not np.all(valid_mask):
        logger.warning(f"Found {np.sum(~valid_mask)} invalid values for {target_name}")
        y_true = y_true[valid_mask]
        y_pred = y_pred[valid_mask]
    
    if len(y_true) == 0:
        logger.error(f"No valid values for {target_name}")
        return {
            "r2": 0.0,
            "mae": 0.0,
            "rmse": 0.0
        }
    
    # Calculate metrics
    r2 = float(r2_score(y_true, y_pred))
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    
    return {
        "r2": r2,
        "mae": mae,
        "rmse": rmse
    }


def calculate_metrics_per_target(
    y_true: Dict[str, np.ndarray],
    y_pred: Dict[str, np.ndarray]
) -> Dict[str, Dict[str, float]]:
    """
    Calculate metrics for each target.
    
    Args:
        y_true: Dictionary with true values per target
        y_pred: Dictionary with predicted values per target
        
    Returns:
        Dictionary with metrics per target
    """
    metrics = {}
    
    for target in y_true.keys():
        if target not in y_pred:
            logger.warning(f"Target {target} not found in predictions")
            continue
        
        metrics[target] = calculate_metrics(
            y_true[target],
            y_pred[target],
            target_name=target
        )
    
    return metrics


def print_metrics_summary(
    metrics: Dict[str, Dict[str, float]],
    epoch: Optional[int] = None
) -> None:
    """
    Print metrics summary.
    
    Args:
        metrics: Dictionary with metrics per target
        epoch: Current epoch (optional)
    """
    if epoch is not None:
        logger.info(f"=== Metrics Epoch {epoch} ===")
    else:
        logger.info("=== Metrics Summary ===")
    
    for target, target_metrics in metrics.items():
        logger.info(
            f"{target.upper()}: "
            f"R²={target_metrics['r2']:.4f}, "
            f"MAE={target_metrics['mae']:.4f}, "
            f"RMSE={target_metrics['rmse']:.4f}"
        )

