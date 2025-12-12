"""
Training loop mejorado para modelos de regresión de cacao.

Mejoras implementadas:
- Validación de normalización antes de entrenar
- Logging detallado (loss por batch, tiempo por epoch)
- Checkpoints automáticos cuando mejora val_loss
- Early stopping robusto
- Learning rate scheduler optimizado
- Validación de pérdidas razonables
- Integración con nueva normalización y métricas R²
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import time
from pathlib import Path
import logging

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from .models import TARGETS, TARGET_NAMES
from .scalers import CacaoScalers, save_scalers
from .metrics import (
    denormalize_and_calculate_metrics,
    validate_predictions_targets_alignment,
    robust_r2_score
)

logger = get_ml_logger("cacaoscan.ml.regression.train_improved")

# Separator constants
SEPARATOR_LINE = "=========================================="


def _split_targets(batch_targets: Any, device: torch.device) -> Dict[str, torch.Tensor]:
    """Normalize targets format to 1D tensors per target in device."""
    if isinstance(batch_targets, dict):
        return {k: v.to(device) for k, v in batch_targets.items()}
    if isinstance(batch_targets, torch.Tensor):
        t = batch_targets
        if t.ndim == 1:
            t = t.unsqueeze(0)
        if t.ndim > 2:
            t = t.view(-1, t.shape[-1])
        if t.shape[-1] < len(TARGETS):
            raise ValueError(f"Se esperaban al menos {len(TARGETS)} columnas en targets, obtuvo {t.shape[-1]}")
        t = t.to(device)
        return {
            "alto": t[:, 0],
            "ancho": t[:, 1],
            "grosor": t[:, 2],
            "peso": t[:, 3],
        }
    raise TypeError(f"Formato de targets no soportado: {type(batch_targets)}")


def _split_outputs(batch_outputs: Any) -> Dict[str, torch.Tensor]:
    """Normalize model output to dict of 2D tensors (batch,)."""
    if isinstance(batch_outputs, dict):
        return batch_outputs
    if isinstance(batch_outputs, torch.Tensor):
        out = batch_outputs
        if out.ndim == 1:
            out = out.unsqueeze(0)
        if out.ndim > 2:
            out = out.view(out.shape[0], -1)
        if out.ndim != 2:
            raise ValueError(f"_split_outputs: output must be 2D after processing, got ndim={out.ndim} shape={out.shape}")
        if out.shape[1] < len(TARGETS):
            raise ValueError(f"Se esperaban al menos {len(TARGETS)} columnas en outputs, obtuvo {out.shape[1]}")
        return {
            "alto": out[:, 0],
            "ancho": out[:, 1],
            "grosor": out[:, 2],
            "peso": out[:, 3],
        }
    raise TypeError(f"Formato de outputs no soportado: {type(batch_outputs)}")


def validate_targets_normalization(
    targets: Dict[str, np.ndarray],
    scalers: CacaoScalers,
    verbose: bool = True
) -> bool:
    """
    Valida que los targets estén correctamente normalizados.
    
    Args:
        targets: Diccionario de targets a validar
        scalers: Escaladores usados para normalización
        verbose: Si mostrar logs detallados
        
    Returns:
        True si están correctamente normalizados, False si hay problemas
    """
    if scalers is None or not scalers.is_fitted:
        logger.error("Scalers no disponibles o no ajustados")
        return False
    
    all_valid = True
    
    for target in TARGETS:
        if target not in targets:
            logger.warning(f"Target '{target}' no encontrado en targets")
            all_valid = False
            continue
        
        target_values = targets[target]
        
        # Verificar que no haya NaN/Inf
        if not np.all(np.isfinite(target_values)):
            n_invalid = np.sum(~np.isfinite(target_values))
            logger.error(f"{target}: {n_invalid} valores NaN/Inf encontrados")
            all_valid = False
        
        # Verificar rango (valores normalizados deberían estar en rango razonable)
        mean_val = np.mean(target_values)
        std_val = np.std(target_values)
        min_val = np.min(target_values)
        max_val = np.max(target_values)
        
        # Valores normalizados con StandardScaler deberían tener mean ~0, std ~1
        if abs(mean_val) > 5 or std_val > 10:
            logger.warning(
                f"{target}: Valores fuera de rango esperado para normalización. "
                f"mean={mean_val:.4f}, std={std_val:.4f}, "
                f"range=[{min_val:.4f}, {max_val:.4f}]"
            )
            all_valid = False
        
        if verbose:
            logger.info(
                f"{target}: mean={mean_val:.4f}, std={std_val:.4f}, "
                f"range=[{min_val:.4f}, {max_val:.4f}]"
            )
    
    return all_valid


def _setup_loss_function(
    use_uncertainty_loss: Optional[bool],
    config: Dict,
    device: torch.device
) -> Tuple[nn.Module, bool]:
    """
    Setup loss function based on configuration.
    
    Returns:
        Tuple of (criterion, use_uncertainty_loss_flag)
    """
    if use_uncertainty_loss is None:
        try:
            from ..utils.losses import UncertaintyWeightedLoss
            logger.info("Using UncertaintyWeightedLoss (Kendall et al.) with initial_sigma=0.3")
            criterion = UncertaintyWeightedLoss(initial_sigma=0.3)
            criterion = criterion.to(device)
            return criterion, True
        except ImportError:
            logger.warning("UncertaintyWeightedLoss not available, falling back to standard loss")
            return _create_standard_loss(config), False
    
    if use_uncertainty_loss:
        try:
            from ..utils.losses import UncertaintyWeightedLoss
            logger.info("Using UncertaintyWeightedLoss (Kendall et al.) with initial_sigma=0.3 (configurado explícitamente)")
            criterion = UncertaintyWeightedLoss(initial_sigma=0.3)
            criterion = criterion.to(device)
            return criterion, True
        except ImportError:
            logger.warning("UncertaintyWeightedLoss solicitado pero no disponible, usando loss estándar")
            return _create_standard_loss(config), False
    
    return _create_standard_loss(config), False


def _create_standard_loss(config: Dict) -> nn.Module:
    """Create standard loss function based on config."""
    loss_type = config.get('loss_type', 'smooth_l1')
    if loss_type == 'mse':
        return nn.MSELoss()
    elif loss_type == 'huber':
        return nn.HuberLoss(delta=1.0)
    else:
        return nn.SmoothL1Loss()


def _setup_optimizer(
    model: nn.Module,
    criterion: nn.Module,
    use_uncertainty_loss: bool,
    learning_rate: float,
    config: Dict
) -> optim.AdamW:
    """Setup optimizer with appropriate parameter groups."""
    if use_uncertainty_loss and criterion is not None:
        loss_params = list(criterion.parameters())
        if len(loss_params) > 0:
            model_lr = learning_rate
            sigma_lr = learning_rate * 100.0
            
            optimizer = optim.AdamW(
                [
                    {'params': model.parameters(), 'lr': model_lr},
                    {'params': criterion.parameters(), 'lr': sigma_lr}
                ],
                lr=learning_rate,
                weight_decay=config.get('weight_decay', 1e-4),
                betas=(0.9, 0.999),
                eps=1e-8
            )
            logger.info("✔ Optimizador incluye parámetros del modelo Y de la loss (log_sigmas)")
            logger.info(f"  Learning Rate del modelo: {model_lr:.2e}")
            logger.info(f"  Learning Rate de los sigmas: {sigma_lr:.2e} (100x más alto)")
            return optimizer
    
    optimizer = optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=config.get('weight_decay', 1e-4),
        betas=(0.9, 0.999),
        eps=1e-8
    )
    if use_uncertainty_loss:
        logger.error("✗ ERROR CRÍTICO: use_uncertainty_loss=True pero criterion es None o no tiene parámetros")
    return optimizer


def _setup_scheduler(
    optimizer: optim.AdamW,
    config: Dict,
    epochs: int
) -> optim.lr_scheduler._LRScheduler:
    """Setup learning rate scheduler."""
    scheduler_type = config.get('scheduler_type', 'reduce_on_plateau')
    
    if scheduler_type == 'reduce_on_plateau':
        return optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True,
            min_lr=config.get('min_lr', 1e-7)
        )
    elif scheduler_type == 'cosine':
        return optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=epochs,
            eta_min=config.get('min_lr', 1e-6)
        )
    else:
        return optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=max(1, epochs // 4),
            T_mult=2,
            eta_min=config.get('min_lr', 1e-7)
        )


def _prepare_batch_inputs(
    batch_data: Tuple,
    device: torch.device,
    use_pixel_features: bool
) -> Optional[Tuple[Tuple, Any]]:
    """Prepare batch inputs for model forward pass."""
    if use_pixel_features:
        if len(batch_data) != 3:
            return None
        images, targets_batch, pixel_features = batch_data
        images = images.to(device)
        pixel_features = pixel_features.to(device)
        return (images, pixel_features), targets_batch
    else:
        if len(batch_data) != 2:
            return None
        images, targets_batch = batch_data
        images = images.to(device)
        return (images,), targets_batch


def _compute_batch_loss(
    outputs_dict: Dict[str, torch.Tensor],
    targets_dict: Dict[str, torch.Tensor],
    criterion: nn.Module,
    use_uncertainty_loss: bool
) -> torch.Tensor:
    """Compute batch loss from outputs and targets."""
    if use_uncertainty_loss:
        outputs_tensor = torch.stack([
            outputs_dict[target].squeeze() for target in TARGETS
        ], dim=1)
        targets_tensor = torch.stack([
            targets_dict[target].squeeze() for target in TARGETS
        ], dim=1)
        return criterion(outputs_tensor, targets_tensor)
    else:
        batch_loss = 0.0
        for target in TARGETS:
            target_loss = criterion(
                outputs_dict[target].squeeze(),
                targets_dict[target].squeeze()
            )
            batch_loss += target_loss
        return batch_loss


def _log_initial_loss_validation(initial_val_loss: float, n_batches_checked: int) -> None:
    """Log initial loss validation results."""
    if n_batches_checked > 0:
        logger.info(f"Pérdida inicial (promedio de {n_batches_checked} batches): {initial_val_loss:.4f}")
        
        if initial_val_loss > 1000:
            logger.error(
                f"PÉRDIDA INICIAL EXTREMADAMENTE ALTA: {initial_val_loss:.4f}. "
                f"Esto indica un problema grave:\n"
                f"  - Targets pueden no estar normalizados\n"
                f"  - Modelo puede estar mal inicializado\n"
                f"  - Learning rate puede ser muy alto\n"
                f"  - Loss function puede ser incorrecta"
            )
        elif initial_val_loss > 100:
            logger.warning(
                f"Pérdida inicial alta: {initial_val_loss:.4f}. "
                f"Considerar reducir learning rate o verificar normalización."
            )


def _validate_initial_loss(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_pixel_features: bool,
    use_uncertainty_loss: bool
) -> None:
    """Validate initial loss before training."""
    logger.info("=== Validando pérdida inicial ===")
    model.eval()
    initial_val_loss = 0.0
    n_batches_checked = 0
    
    with torch.no_grad():
        for batch_data in val_loader:
            batch_result = _prepare_batch_inputs(batch_data, device, use_pixel_features)
            if batch_result is None:
                continue
            
            inputs, targets_batch = batch_result
            outputs = model(*inputs)
            outputs_dict = _split_outputs(outputs)
            targets_dict = _split_targets(targets_batch, device)
            
            batch_loss = _compute_batch_loss(outputs_dict, targets_dict, criterion, use_uncertainty_loss)
            initial_val_loss += batch_loss.item()
            n_batches_checked += 1
            
            if n_batches_checked >= 5:
                break
    
    if n_batches_checked > 0:
        initial_val_loss = initial_val_loss / n_batches_checked
    
    _log_initial_loss_validation(initial_val_loss, n_batches_checked)
    logger.info("=================================")


def _prepare_train_batch_inputs(
    batch_data: Tuple,
    device: torch.device,
    use_pixel_features: bool
) -> Optional[Tuple[Tuple, Any]]:
    """Prepare batch inputs for training with non_blocking transfer."""
    if use_pixel_features:
        if len(batch_data) != 3:
            logger.error(f"Error: Se esperaban 3 tensores, se obtuvieron {len(batch_data)}")
            return None
        images, targets_batch, pixel_features = batch_data
        images = images.to(device, non_blocking=True)
        pixel_features = pixel_features.to(device, non_blocking=True)
        return (images, pixel_features), targets_batch
    else:
        if len(batch_data) != 2:
            logger.error(f"Error: Se esperaban 2 tensores, se obtuvieron {len(batch_data)}")
            return None
        images, targets_batch = batch_data
        images = images.to(device, non_blocking=True)
        return (images,), targets_batch


def _process_train_batch(
    model: nn.Module,
    inputs: Tuple,
    targets_batch: Any,
    criterion: nn.Module,
    optimizer: optim.AdamW,
    device: torch.device,
    use_uncertainty_loss: bool,
    config: Dict,
    batch_idx: int
) -> Optional[float]:
    """Process a single training batch and return loss value."""
    optimizer.zero_grad()
    outputs = model(*inputs)
    outputs_dict = _split_outputs(outputs)
    targets_dict = _split_targets(targets_batch, device)
    
    loss = _compute_batch_loss(outputs_dict, targets_dict, criterion, use_uncertainty_loss)
    
    if not torch.isfinite(loss):
        logger.error(f"Batch {batch_idx}: Pérdida no finita: {loss.item()}")
        return None
    
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), config.get('max_grad_norm', 1.0))
    optimizer.step()
    
    return loss.item()


def _train_one_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.AdamW,
    device: torch.device,
    use_pixel_features: bool,
    use_uncertainty_loss: bool,
    config: Dict
) -> float:
    """Train model for one epoch."""
    model.train()
    train_loss = 0.0
    n_batches = 0
    
    for batch_idx, batch_data in enumerate(train_loader):
        batch_result = _prepare_train_batch_inputs(batch_data, device, use_pixel_features)
        if batch_result is None:
            continue
        
        inputs, targets_batch = batch_result
        batch_loss = _process_train_batch(
            model, inputs, targets_batch, criterion, optimizer,
            device, use_uncertainty_loss, config, batch_idx
        )
        
        if batch_loss is not None:
            train_loss += batch_loss
            n_batches += 1
    
    return train_loss / (n_batches + 1e-6)


def _accumulate_validation_metrics(
    outputs_dict: Dict[str, torch.Tensor],
    targets_dict: Dict[str, torch.Tensor],
    val_metrics_epoch: Dict[str, Dict[str, List[float]]]
) -> None:
    """Accumulate predictions and targets for validation metrics."""
    for target in TARGETS:
        val_metrics_epoch[target]['preds'].extend(
            outputs_dict[target].cpu().numpy().flatten()
        )
        val_metrics_epoch[target]['targets'].extend(
            targets_dict[target].cpu().numpy().flatten()
        )


def _process_validation_batch(
    model: nn.Module,
    inputs: Tuple,
    targets_batch: Any,
    criterion: nn.Module,
    device: torch.device,
    use_uncertainty_loss: bool,
    val_metrics_epoch: Dict[str, Dict[str, List[float]]]
) -> float:
    """Process a single validation batch and return loss value."""
    outputs = model(*inputs)
    outputs_dict = _split_outputs(outputs)
    targets_dict = _split_targets(targets_batch, device)
    
    batch_loss = _compute_batch_loss(outputs_dict, targets_dict, criterion, use_uncertainty_loss)
    _accumulate_validation_metrics(outputs_dict, targets_dict, val_metrics_epoch)
    
    return batch_loss.item()


def _calculate_validation_metrics(
    val_metrics_epoch: Dict[str, Dict[str, List[float]]],
    scalers: CacaoScalers
) -> Tuple[Dict[str, Dict[str, float]], float]:
    """Calculate final validation metrics from accumulated predictions and targets."""
    pred_dict_norm = {t: np.array(val_metrics_epoch[t]['preds']) for t in TARGETS}
    targ_dict_norm = {t: np.array(val_metrics_epoch[t]['targets']) for t in TARGETS}
    
    if not validate_predictions_targets_alignment(pred_dict_norm, targ_dict_norm):
        logger.error("Problema de alineación entre predicciones y targets")
    
    metrics_per_target, avg_r2 = denormalize_and_calculate_metrics(
        predictions_norm=pred_dict_norm,
        targets_norm=targ_dict_norm,
        scalers=scalers,
        target_names=TARGETS,
        verbose=False
    )
    
    return metrics_per_target, avg_r2


def _validate_one_epoch(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    scalers: CacaoScalers,
    device: torch.device,
    use_pixel_features: bool,
    use_uncertainty_loss: bool
) -> Tuple[float, Dict[str, Dict[str, float]], float]:
    """Validate model for one epoch and return loss and metrics."""
    model.eval()
    val_loss = 0.0
    val_metrics_epoch = {target: {'preds': [], 'targets': []} for target in TARGETS}
    n_val_batches = 0
    
    with torch.no_grad():
        for batch_data in val_loader:
            batch_result = _prepare_batch_inputs(batch_data, device, use_pixel_features)
            if batch_result is None:
                continue
            
            inputs, targets_batch = batch_result
            batch_loss = _process_validation_batch(
                model, inputs, targets_batch, criterion, device,
                use_uncertainty_loss, val_metrics_epoch
            )
            
            val_loss += batch_loss
            n_val_batches += 1
    
    avg_val_loss = val_loss / (n_val_batches + 1e-6)
    metrics_per_target, avg_r2 = _calculate_validation_metrics(val_metrics_epoch, scalers)
    
    return avg_val_loss, metrics_per_target, avg_r2


def _validate_model_output_range(
    model: nn.Module,
    train_loader: DataLoader,
    device: torch.device,
    use_pixel_features: bool
) -> None:
    """Validate model output range before training."""
    logger.info("=== Validando rango de salida del modelo ===")
    model.eval()
    with torch.no_grad():
        sample = next(iter(train_loader))
        if use_pixel_features:
            if len(sample) == 3:
                images = sample[0].to(device)
                pixel_features = sample[2].to(device)
                out = model(images, pixel_features)
            else:
                logger.warning("Batch no tiene la estructura esperada para logging")
                out = None
        else:
            if len(sample) == 2:
                images = sample[0].to(device)
                out = model(images)
            else:
                logger.warning("Batch no tiene la estructura esperada para logging")
                out = None
        
        if out is not None:
            if isinstance(out, dict):
                all_values = torch.cat([v.flatten() for v in out.values()])
                out_min = all_values.min().item()
                out_max = all_values.max().item()
            else:
                out_min = out.min().item()
                out_max = out.max().item()
            logger.info(f"Rango salida modelo: min={out_min:.4f}, max={out_max:.4f}")
            if abs(out_min) > 100 or abs(out_max) > 100:
                logger.error(
                    f"⚠️ EXPLOSIÓN EN LA RED DETECTADA: Rango extremo [{out_min:.2f}, {out_max:.2f}]. "
                    f"Esto indica problemas de inicialización o gradientes explosivos."
                )
    logger.info(SEPARATOR_LINE)


def _log_epoch_metrics(
    epoch: int,
    epochs: int,
    avg_train_loss: float,
    avg_val_loss: float,
    current_lr: float,
    epoch_time: float,
    metrics_per_target: Dict[str, Dict[str, float]],
    avg_r2: float,
    use_uncertainty_loss: bool,
    criterion: Optional[nn.Module],
    initial_sigmas: Optional[Dict[str, float]],
    start_time_total: float
) -> None:
    """Log epoch metrics."""
    log_str = (
        f"Epoch {epoch+1}/{epochs} | "
        f"Train Loss: {avg_train_loss:.4f} | "
        f"Val Loss: {avg_val_loss:.4f} | "
        f"LR: {current_lr:.2e} | "
        f"Time: {epoch_time:.2f}s"
    )
    
    for target in TARGETS:
        if target in metrics_per_target:
            r2 = metrics_per_target[target]['r2']
            log_str += f" | {target} R²: {r2:.4f}"
    
    log_str += f" | Avg R²: {avg_r2:.4f}"
    
    if use_uncertainty_loss and criterion is not None:
        sigmas = criterion.get_sigmas()
        if initial_sigmas is not None:
            sigma_changes = {k: f"{sigmas[k]:.4f} (Δ{((sigmas[k] - initial_sigmas.get(k, 0.3)) / 0.3 * 100):+.1f}%)" 
                           for k in sigmas}
            log_str += f" | Sigmas: {sigma_changes}"
        else:
            log_str += f" | Sigmas: {sigmas}"
    
    logger.info(log_str)
    
    if (epoch + 1) % 5 == 0 or any(
        metrics_per_target.get(t, {}).get('r2', 0) < -100
        for t in TARGETS
    ) or avg_val_loss > 1000:
        logger.info("=== Métricas detalladas por componente ===")
        for target in TARGETS:
            if target in metrics_per_target:
                m = metrics_per_target[target]
                logger.info(
                    f"{target.upper()}: MAE={m['mae']:.4f}, "
                    f"RMSE={m['rmse']:.4f}, R²={m['r2']:.4f}, "
                    f"n={m['n_samples']}"
                )
        logger.info(f"R² Promedio: {avg_r2:.4f}")
        logger.info(f"Tiempo total: {time.time() - start_time_total:.2f}s")
        logger.info(SEPARATOR_LINE)


def _save_checkpoint(
    checkpoint_path: Path,
    epoch: int,
    model_state_dict: Dict,
    optimizer: optim.AdamW,
    scheduler: optim.lr_scheduler._LRScheduler,
    val_loss: float,
    metrics_per_target: Dict[str, Dict[str, float]],
    avg_r2: float,
    config: Dict,
    message: str
) -> None:
    """Save checkpoint to disk."""
    torch.save({
        'epoch': epoch + 1,
        'model_state_dict': model_state_dict,
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict(),
        'val_loss': val_loss,
        'metrics': metrics_per_target,
        'avg_r2': avg_r2,
        'config': config
    }, checkpoint_path)
    logger.info(message)


def _handle_intelligent_early_stopping(
    epoch: int,
    current_metrics: Dict[str, Any],
    best_state: Dict[str, Any],
    training_components: Dict[str, Any],
    checkpoint_config: Dict[str, Any],
    early_stopping: Any,
    patience_counter: int
) -> Tuple[bool, float, int, Optional[Dict], int]:
    """Handle intelligent early stopping logic."""
    avg_val_loss = current_metrics['avg_val_loss']
    avg_r2 = current_metrics['avg_r2']
    metrics_per_target = current_metrics['metrics_per_target']
    
    best_val_loss = best_state['best_val_loss']
    best_epoch = best_state['best_epoch']
    best_model_state = best_state['best_model_state']
    
    model = training_components['model']
    optimizer = training_components['optimizer']
    scheduler = training_components['scheduler']
    
    checkpoint_dir = checkpoint_config['checkpoint_dir']
    config = checkpoint_config['config']
    history = checkpoint_config['history']
    
    r2_scores = {target: metrics_per_target.get(target, {}).get('r2', 0.0) for target in TARGETS}
    should_stop, is_best_loss, _, should_rollback = early_stopping(
        epoch + 1,
        avg_val_loss,
        r2_scores,
        optimizer
    )
    
    if is_best_loss:
        best_val_loss = avg_val_loss
        best_epoch = epoch + 1
        best_model_state = model.state_dict().copy()
        
        checkpoint_path = checkpoint_dir / "best_loss.pt"
        _save_checkpoint(
            checkpoint_path, epoch, best_model_state, optimizer, scheduler,
            best_val_loss, metrics_per_target, avg_r2, config,
            f"✓ Best loss checkpoint guardado: {checkpoint_path} (Val Loss: {best_val_loss:.4f})"
        )
    
    best_avg_r2 = max(history.get('val_r2_avg', [0.0])) if history.get('val_r2_avg') else -float('inf')
    if avg_r2 > best_avg_r2:
        checkpoint_path = checkpoint_dir / "best_avg_r2.pt"
        _save_checkpoint(
            checkpoint_path, epoch, model.state_dict(), optimizer, scheduler,
            avg_val_loss, metrics_per_target, avg_r2, config,
            f"✓ Best R² checkpoint guardado: {checkpoint_path} (Avg R²: {avg_r2:.4f})"
        )
    
    if should_rollback and best_model_state is not None:
        logger.warning("Rolling back to best checkpoint")
        model.load_state_dict(best_model_state)
    
    if should_stop:
        logger.info(f"Early stopping en época {epoch+1} (mejor época: {best_epoch}, Val Loss: {best_val_loss:.4f})")
        return True, best_val_loss, best_epoch, best_model_state, patience_counter
    
    return False, best_val_loss, best_epoch, best_model_state, patience_counter


def _handle_basic_early_stopping(
    epoch: int,
    current_metrics: Dict[str, Any],
    best_state: Dict[str, Any],
    training_components: Dict[str, Any],
    checkpoint_config: Dict[str, Any],
    improvement_threshold: float,
    patience_counter: int,
    early_stopping_patience: int
) -> Tuple[bool, float, int, Optional[Dict], int]:
    """Handle basic early stopping logic."""
    avg_val_loss = current_metrics['avg_val_loss']
    avg_r2 = current_metrics['avg_r2']
    metrics_per_target = current_metrics['metrics_per_target']
    
    best_val_loss = best_state['best_val_loss']
    best_epoch = best_state['best_epoch']
    best_model_state = best_state['best_model_state']
    
    model = training_components['model']
    optimizer = training_components['optimizer']
    scheduler = training_components['scheduler']
    
    checkpoint_dir = checkpoint_config['checkpoint_dir']
    config = checkpoint_config['config']
    
    if avg_val_loss < best_val_loss - improvement_threshold:
        best_val_loss = avg_val_loss
        best_epoch = epoch + 1
        patience_counter = 0
        best_model_state = model.state_dict().copy()
        
        checkpoint_path = checkpoint_dir / f"best_model_epoch_{epoch+1}.pt"
        _save_checkpoint(
            checkpoint_path, epoch, best_model_state, optimizer, scheduler,
            best_val_loss, metrics_per_target, avg_r2, config,
            f"✓ Checkpoint guardado: {checkpoint_path} (Val Loss: {best_val_loss:.4f})"
        )
    else:
        patience_counter += 1
    
    if patience_counter >= early_stopping_patience:
        logger.info(f"Early stopping en época {epoch+1} (mejor época: {best_epoch}, Val Loss: {best_val_loss:.4f})")
        return True, best_val_loss, best_epoch, best_model_state, patience_counter
    
    return False, best_val_loss, best_epoch, best_model_state, patience_counter


def _handle_early_stopping(
    epoch: int,
    current_metrics: Dict[str, Any],
    best_state: Dict[str, Any],
    training_components: Dict[str, Any],
    checkpoint_config: Dict[str, Any],
    use_intelligent_early_stopping: bool,
    early_stopping: Optional[Any],
    improvement_threshold: float,
    patience_counter: int,
    early_stopping_patience: int
) -> Tuple[bool, float, int, Optional[Dict], int]:
    """Handle early stopping logic and return updated state."""
    if use_intelligent_early_stopping and early_stopping is not None:
        return _handle_intelligent_early_stopping(
            epoch, current_metrics, best_state, training_components,
            checkpoint_config, early_stopping, patience_counter
        )
    else:
        return _handle_basic_early_stopping(
            epoch, current_metrics, best_state, training_components,
            checkpoint_config, improvement_threshold, patience_counter, early_stopping_patience
        )


def _validate_targets_normalization_setup(
    train_loader: DataLoader,
    scalers: CacaoScalers
) -> None:
    """Validate targets normalization before training."""
    logger.info("=== Validando normalización de targets ===")
    if train_loader.dataset.targets is not None:
        train_targets_dict = {}
        for target in TARGETS:
            if hasattr(train_loader.dataset, 'targets') and target in train_loader.dataset.targets:
                train_targets_dict[target] = np.array(train_loader.dataset.targets[target])
        
        if train_targets_dict:
            is_normalized = validate_targets_normalization(
                train_targets_dict,
                scalers,
                verbose=True
            )
            if not is_normalized:
                logger.warning("Targets pueden no estar correctamente normalizados")
        else:
            logger.warning("No se pudieron extraer targets del dataset para validación")
    logger.info(SEPARATOR_LINE)


def _setup_learning_rate(config: Dict) -> float:
    """Setup and validate learning rate."""
    learning_rate = config.get('learning_rate', 1e-5)
    if learning_rate > 1e-3:
        logger.warning(f"Learning rate {learning_rate} puede ser muy alto. Reduciendo a 1e-3")
        learning_rate = 1e-3
    elif learning_rate < 1e-6:
        logger.warning(f"Learning rate {learning_rate} puede ser muy bajo. Aumentando a 1e-6")
        learning_rate = 1e-6
    return learning_rate


def _setup_early_stopping(config: Dict) -> Tuple[bool, Optional[Any], int]:
    """Setup early stopping mechanism."""
    try:
        from ..utils.early_stopping import IntelligentEarlyStopping
        early_stopping_patience = config.get('early_stopping_patience', 15)
        early_stopping = IntelligentEarlyStopping(
            patience=early_stopping_patience,
            min_delta_percent=0.005,
            r2_threshold=-2.0,
            r2_consecutive=2,
            val_loss_increase_epochs=3
        )
        use_intelligent_early_stopping = True
        logger.info(f"Using IntelligentEarlyStopping (patience={early_stopping_patience}, min_delta=0.5%)")
        return use_intelligent_early_stopping, early_stopping, early_stopping_patience
    except ImportError:
        logger.warning("IntelligentEarlyStopping not available, using basic early stopping")
        use_intelligent_early_stopping = False
        early_stopping_patience = config.get('early_stopping_patience', 10)
        return use_intelligent_early_stopping, None, early_stopping_patience


def _initialize_training_state(config: Dict) -> Dict[str, Any]:
    """Initialize training state variables."""
    return {
        'best_val_loss': float('inf'),
        'patience_counter': 0,
        'best_model_state': None,
        'best_epoch': 0,
        'improvement_threshold': config.get('improvement_threshold', 1e-4),
        'history': {
            'train_loss': [], 'val_loss': [], 'learning_rate': [],
            **{f'val_mae_{t}': [] for t in TARGETS},
            **{f'val_rmse_{t}': [] for t in TARGETS},
            **{f'val_r2_{t}': [] for t in TARGETS},
            'val_r2_avg': [],
            'epoch_time': [],
        }
    }


def _update_scheduler(
    scheduler: optim.lr_scheduler._LRScheduler,
    optimizer: optim.AdamW,
    avg_val_loss: float
) -> float:
    """Update learning rate scheduler and return current LR."""
    if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
        scheduler.step(avg_val_loss)
        return optimizer.param_groups[0]['lr']
    else:
        scheduler.step()
        return scheduler.get_last_lr()[0] if hasattr(scheduler, 'get_last_lr') else optimizer.param_groups[0]['lr']


def _save_metrics_to_history(
    history: Dict[str, List[float]],
    metrics_per_target: Dict[str, Dict[str, float]],
    avg_r2: float
) -> None:
    """Save validation metrics to history."""
    for target in TARGETS:
        if target in metrics_per_target:
            m = metrics_per_target[target]
            history[f'val_mae_{target}'].append(m['mae'])
            history[f'val_rmse_{target}'].append(m['rmse'])
            history[f'val_r2_{target}'].append(m['r2'])
        else:
            history[f'val_mae_{target}'].append(0.0)
            history[f'val_rmse_{target}'].append(0.0)
            history[f'val_r2_{target}'].append(0.0)
    history['val_r2_avg'].append(avg_r2)


def _run_training_loop(
    training_data: Dict[str, Any],
    training_config: Dict[str, Any],
    epochs: int
) -> Tuple[Dict[str, List[float]], float, int, Optional[Dict]]:
    """Run the main training loop."""
    model = training_data['model']
    train_loader = training_data['train_loader']
    val_loader = training_data['val_loader']
    criterion = training_data['criterion']
    optimizer = training_data['optimizer']
    scheduler = training_data['scheduler']
    scalers = training_data['scalers']
    device = training_data['device']
    use_pixel_features = training_data['use_pixel_features']
    use_uncertainty_loss = training_data['use_uncertainty_loss']
    config = training_config['config']
    checkpoint_dir = training_config['checkpoint_dir']
    use_intelligent_early_stopping = training_config['use_intelligent_early_stopping']
    early_stopping = training_config['early_stopping']
    improvement_threshold = training_config['improvement_threshold']
    initial_sigmas = training_config['initial_sigmas']
    
    training_state = _initialize_training_state(config)
    history = training_state['history']
    best_val_loss = training_state['best_val_loss']
    best_epoch = training_state['best_epoch']
    best_model_state = training_state['best_model_state']
    patience_counter = training_state['patience_counter']
    early_stopping_patience = config.get('early_stopping_patience', 10)
    
    start_time_total = time.time()
    
    for epoch in range(epochs):
        epoch_start_time = time.time()
        
        avg_train_loss = _train_one_epoch(
            model, train_loader, criterion, optimizer, device,
            use_pixel_features, use_uncertainty_loss, config
        )
        
        avg_val_loss, metrics_per_target, avg_r2 = _validate_one_epoch(
            model, val_loader, criterion, scalers, device,
            use_pixel_features, use_uncertainty_loss
        )
        
        current_lr = _update_scheduler(scheduler, optimizer, avg_val_loss)
        epoch_time = time.time() - epoch_start_time
        
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['learning_rate'].append(current_lr)
        history['epoch_time'].append(epoch_time)
        
        _save_metrics_to_history(history, metrics_per_target, avg_r2)
        
        _log_epoch_metrics(
            epoch, epochs, avg_train_loss, avg_val_loss, current_lr, epoch_time,
            metrics_per_target, avg_r2, use_uncertainty_loss, criterion,
            initial_sigmas, start_time_total
        )
        
        current_metrics = {
            'avg_val_loss': avg_val_loss,
            'avg_r2': avg_r2,
            'metrics_per_target': metrics_per_target
        }
        best_state = {
            'best_val_loss': best_val_loss,
            'best_epoch': best_epoch,
            'best_model_state': best_model_state
        }
        training_components = {
            'model': model,
            'optimizer': optimizer,
            'scheduler': scheduler
        }
        checkpoint_config_dict = {
            'checkpoint_dir': checkpoint_dir,
            'config': config,
            'history': history
        }
        
        should_stop, best_val_loss, best_epoch, best_model_state, patience_counter = _handle_early_stopping(
            epoch, current_metrics, best_state, training_components, checkpoint_config_dict,
            use_intelligent_early_stopping, early_stopping, improvement_threshold,
            patience_counter, early_stopping_patience
        )
        
        if should_stop:
            break
    
    return history, best_val_loss, best_epoch, best_model_state


def _save_final_model(
    model: nn.Module,
    is_hybrid: bool,
    config: Dict,
    best_val_loss: float,
    best_epoch: int,
    history: Dict[str, List[float]]
) -> None:
    """Save final model to artifacts directory."""
    artifacts_dir = get_regressors_artifacts_dir()
    model_name = "hybrid.pt" if is_hybrid else "multihead.pt"
    final_path = artifacts_dir / model_name
    
    ensure_dir_exists(artifacts_dir)
    
    model_to_save = model.module if hasattr(model, "module") else model
    original_device = next(model_to_save.parameters()).device
    model_to_save_cpu = model_to_save.cpu()
    
    torch.save({
        'model_state_dict': model_to_save_cpu.state_dict(),
        'model_info': {
            'model_type': 'HybridCacaoRegression' if is_hybrid else 'MultiHeadRegression',
            'config': config,
            'best_val_loss': best_val_loss,
            'best_epoch': best_epoch,
            'training_history': history,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }, final_path)
    
    if not final_path.exists():
        raise IOError(f"El archivo {final_path} no se creó después de torch.save")
    if final_path.stat().st_size == 0:
        raise IOError(f"El archivo {final_path} está vacío")
    
    model_to_save.to(original_device)
    logger.info(f"[OK] Modelo final guardado en: {final_path}")
    logger.info(f"[OK] Tamaño del archivo: {final_path.stat().st_size / 1024 / 1024:.2f} MB")


def train_multi_head_model_improved(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    config: Dict,
    device: torch.device,
    save_dir: Optional[Path] = None,
    training_job: Optional[Any] = None,
    dataset_info: Optional[Dict] = None,
    save_metrics: bool = True,
    use_uncertainty_loss: Optional[bool] = None
) -> Dict[str, List[float]]:
    """
    Entrena un modelo multi-head o híbrido con mejoras completas.
    
    Mejoras:
    - Validación de normalización antes de entrenar
    - Logging detallado (loss por batch, tiempo por epoch)
    - Checkpoints automáticos
    - Early stopping robusto
    - Validación de pérdidas razonables
    - Integración con métricas R² mejoradas
    
    Args:
        training_job: Parámetro reservado para futuras integraciones (no usado actualmente)
        dataset_info: Parámetro reservado para futuras integraciones (no usado actualmente)
        save_metrics: Parámetro reservado para futuras integraciones (no usado actualmente)
    """
    # Suppress unused parameter warnings - these are part of the public API
    _ = training_job
    _ = dataset_info
    _ = save_metrics
    """
    Entrena un modelo multi-head o híbrido con mejoras completas.
    
    Mejoras:
    - Validación de normalización antes de entrenar
    - Logging detallado (loss por batch, tiempo por epoch)
    - Checkpoints automáticos
    - Early stopping robusto
    - Validación de pérdidas razonables
    - Integración con métricas R² mejoradas
    """
    is_hybrid = config.get('hybrid', False) or config.get('model_type') == 'hybrid'
    use_pixel_features = config.get('use_pixel_features', False) and is_hybrid
    
    if is_hybrid:
        logger.info(f"Entrenando modelo HÍBRIDO (use_pixel_features={use_pixel_features})")
    else:
        logger.info("Entrenando modelo MULTI-HEAD")
    
    model = model.to(device)
    
    _validate_targets_normalization_setup(train_loader, scalers)
    
    learning_rate = _setup_learning_rate(config)
    criterion, use_uncertainty_loss = _setup_loss_function(use_uncertainty_loss, config, device)
    optimizer = _setup_optimizer(model, criterion, use_uncertainty_loss, learning_rate, config)
    
    epochs = config.get('epochs', 50)
    scheduler = _setup_scheduler(optimizer, config, epochs)
    
    loss_type = config.get('loss_type', 'smooth_l1') if not use_uncertainty_loss else 'UncertaintyWeighted'
    scheduler_type = config.get('scheduler_type', 'reduce_on_plateau')
    logger.info(f"Optimizador: AdamW (lr={learning_rate:.2e}), Loss: {loss_type}, Scheduler: {scheduler_type}")
    
    use_intelligent_early_stopping, early_stopping, _ = _setup_early_stopping(config)
    training_state = _initialize_training_state(config)
    improvement_threshold = training_state['improvement_threshold']
    
    initial_sigmas = None
    if use_uncertainty_loss:
        initial_sigmas = criterion.get_sigmas().copy()
        logger.info(f"Sigmas iniciales: {initial_sigmas}")
    
    if save_dir is None:
        save_dir = get_regressors_artifacts_dir()
    checkpoint_dir = save_dir / "checkpoints"
    ensure_dir_exists(checkpoint_dir)
    
    _validate_initial_loss(model, val_loader, criterion, device, use_pixel_features, use_uncertainty_loss)
    
    logger.info(f"=== Iniciando entrenamiento ({epochs} épocas) ===")
    _validate_model_output_range(model, train_loader, device, use_pixel_features)
    
    training_data = {
        'model': model,
        'train_loader': train_loader,
        'val_loader': val_loader,
        'criterion': criterion,
        'optimizer': optimizer,
        'scheduler': scheduler,
        'scalers': scalers,
        'device': device,
        'use_pixel_features': use_pixel_features,
        'use_uncertainty_loss': use_uncertainty_loss
    }
    training_config = {
        'config': config,
        'checkpoint_dir': checkpoint_dir,
        'use_intelligent_early_stopping': use_intelligent_early_stopping,
        'early_stopping': early_stopping,
        'improvement_threshold': improvement_threshold,
        'initial_sigmas': initial_sigmas
    }
    
    history, best_val_loss, best_epoch, best_model_state = _run_training_loop(
        training_data, training_config, epochs
    )
    
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info(f"Mejor modelo cargado (Época {best_epoch}, Val Loss: {best_val_loss:.4f})")
    else:
        logger.warning("No se encontró best_model_state, guardando modelo actual")
        best_val_loss = history['val_loss'][-1] if history['val_loss'] else float('inf')
        best_epoch = epochs
    
    logger.info("=== Entrenamiento completado ===")
    
    try:
        _save_final_model(model, is_hybrid, config, best_val_loss, best_epoch, history)
    except Exception as e:
        logger.error(f"[ERROR] No se pudo guardar modelo final: {e}", exc_info=True)
        raise
    
    return history

