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
    use_uncertainty_loss: Optional[bool] = None  # Si None, se detecta automáticamente
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
    """
    is_hybrid = config.get('hybrid', False) or config.get('model_type') == 'hybrid'
    use_pixel_features = config.get('use_pixel_features', False) and is_hybrid
    
    if is_hybrid:
        logger.info(f"Entrenando modelo HÍBRIDO (use_pixel_features={use_pixel_features})")
    else:
        logger.info("Entrenando modelo MULTI-HEAD")
    
    model = model.to(device)
    
    # Validar normalización de targets ANTES de entrenar
    logger.info("=== Validando normalización de targets ===")
    if train_loader.dataset.targets is not None:
        # Extraer targets del dataset
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
    
    # Optimizador mejorado con learning rate más conservador
    # REDUCIDO a 1e-5 por defecto para estabilidad con Uncertainty Loss
    learning_rate = config.get('learning_rate', 1e-5)
    
    # Si la pérdida inicial es muy alta, reducir LR
    # Validar LR antes de crear optimizador
    if learning_rate > 1e-3:
        logger.warning(f"Learning rate {learning_rate} puede ser muy alto. Reduciendo a 1e-3")
        learning_rate = 1e-3
    elif learning_rate < 1e-6:
        logger.warning(f"Learning rate {learning_rate} puede ser muy bajo. Aumentando a 1e-6")
        learning_rate = 1e-6
    
    # Loss function: Uncertainty-weighted loss (Kendall et al.)
    # DEFINIR use_uncertainty_loss y criterion ANTES de crear el optimizador
    # Si use_uncertainty_loss se pasa como parámetro, respetarlo; si no, detectar automáticamente
    if use_uncertainty_loss is None:
        # Detección automática: intentar usar UncertaintyWeightedLoss si está disponible
        use_uncertainty_loss_flag = False
        criterion = None
        try:
            from ..utils.losses import UncertaintyWeightedLoss
            logger.info("Using UncertaintyWeightedLoss (Kendall et al.) with initial_sigma=0.3")
            criterion = UncertaintyWeightedLoss(initial_sigma=0.3)
            criterion = criterion.to(device)
            use_uncertainty_loss_flag = True
        except ImportError:
            logger.warning("UncertaintyWeightedLoss not available, falling back to standard loss")
            loss_type = config.get('loss_type', 'smooth_l1')
            if loss_type == 'mse':
                criterion = nn.MSELoss()
            elif loss_type == 'huber':
                criterion = nn.HuberLoss(delta=1.0)
            else:  # 'smooth_l1' (default)
                criterion = nn.SmoothL1Loss()
            use_uncertainty_loss_flag = False
        use_uncertainty_loss = use_uncertainty_loss_flag
    else:
        # use_uncertainty_loss fue pasado explícitamente
        if use_uncertainty_loss:
            try:
                from ..utils.losses import UncertaintyWeightedLoss
                logger.info("Using UncertaintyWeightedLoss (Kendall et al.) with initial_sigma=0.3 (configurado explícitamente)")
                criterion = UncertaintyWeightedLoss(initial_sigma=0.3)
                criterion = criterion.to(device)
            except ImportError:
                logger.warning("UncertaintyWeightedLoss solicitado pero no disponible, usando loss estándar")
                use_uncertainty_loss = False
                loss_type = config.get('loss_type', 'smooth_l1')
                if loss_type == 'mse':
                    criterion = nn.MSELoss()
                elif loss_type == 'huber':
                    criterion = nn.HuberLoss(delta=1.0)
                else:
                    criterion = nn.SmoothL1Loss()
        else:
            # use_uncertainty_loss=False explícitamente
            loss_type = config.get('loss_type', 'smooth_l1')
            if loss_type == 'mse':
                criterion = nn.MSELoss()
            elif loss_type == 'huber':
                criterion = nn.HuberLoss(delta=1.0)
            else:  # 'smooth_l1' (default)
                criterion = nn.SmoothL1Loss()
    
    # CRÍTICO: Incluir parámetros del modelo Y de la loss (log_sigmas) en el optimizador
    # Si los log_sigmas no están en el optimizador, los sigmas nunca se actualizarán
    # IMPORTANTE: Los sigmas necesitan un LR más alto (100x) para actualizarse correctamente
    if use_uncertainty_loss and criterion is not None:
        # Verificar que la loss realmente tiene parámetros aprendibles
        loss_params = list(criterion.parameters())
        if len(loss_params) > 0:
            # Definir Learning Rates separados para modelo y sigmas
            # El modelo usa el LR bajo y estable (1e-5)
            model_lr = learning_rate
            
            # Los sigmas necesitan un LR 100 veces más alto para moverse y balancear las tareas
            # Esto es crítico: con LR=1e-5, los sigmas no se actualizan (Δ+0.0%)
            sigma_lr = learning_rate * 100.0  # 100x más alto (ej. 1e-5 * 100 = 1e-3)
            
            # Usar grupos de parámetros con LR separados
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
            model_params_count = sum(p.numel() for p in model.parameters())
            loss_params_count = sum(p.numel() for p in loss_params)
            logger.info(f"  Parámetros del modelo: {model_params_count}")
            logger.info(f"  Parámetros de la loss (log_sigmas): {loss_params_count}")
            logger.info(f"  Total parámetros optimizables: {model_params_count + loss_params_count}")
            
            # Verificar que los parámetros de la loss están realmente en el optimizador
            optimizer_param_ids = {id(p) for group in optimizer.param_groups for p in group['params']}
            loss_param_ids = {id(p) for p in loss_params}
            if loss_param_ids.issubset(optimizer_param_ids):
                logger.info("  ✓ Verificación: Parámetros de la loss están en el optimizador")
                # Verificar que tienen el LR correcto
                for i, group in enumerate(optimizer.param_groups):
                    if i == 0:
                        logger.info(f"  ✓ Grupo 0 (modelo): LR={group['lr']:.2e}, {len(group['params'])} grupos de parámetros")
                    elif i == 1:
                        logger.info(f"  ✓ Grupo 1 (sigmas): LR={group['lr']:.2e}, {len(group['params'])} grupos de parámetros")
            else:
                logger.error("  ✗ ERROR: Parámetros de la loss NO están en el optimizador")
        else:
            # Loss no tiene parámetros aprendibles (caso raro para UncertaintyWeightedLoss)
            optimizer = optim.AdamW(
                model.parameters(),
                lr=learning_rate,
                weight_decay=config.get('weight_decay', 1e-4),
                betas=(0.9, 0.999),
                eps=1e-8
            )
            logger.warning("⚠ UncertaintyWeightedLoss no tiene parámetros aprendibles (posible error de inicialización)")
    else:
        # Solo parámetros del modelo (loss estándar sin parámetros aprendibles)
        optimizer = optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=config.get('weight_decay', 1e-4),
            betas=(0.9, 0.999),
            eps=1e-8
        )
        if use_uncertainty_loss:
            logger.error("✗ ERROR CRÍTICO: use_uncertainty_loss=True pero criterion es None o no tiene parámetros")
    
    # Scheduler mejorado
    scheduler_type = config.get('scheduler_type', 'reduce_on_plateau')
    epochs = config.get('epochs', 50)
    
    if scheduler_type == 'reduce_on_plateau':
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True,
            min_lr=config.get('min_lr', 1e-7)
        )
    elif scheduler_type == 'cosine':
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=epochs,
            eta_min=config.get('min_lr', 1e-6)
        )
    else:
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=max(1, epochs // 4),
            T_mult=2,
            eta_min=config.get('min_lr', 1e-7)
        )
    
    # Logging de configuración de optimizador y loss
    loss_type = config.get('loss_type', 'smooth_l1') if not use_uncertainty_loss else 'UncertaintyWeighted'
    logger.info(f"Optimizador: AdamW (lr={learning_rate:.2e}), Loss: {loss_type}, Scheduler: {scheduler_type}")
    
    # Historial mejorado
    history = {
        'train_loss': [], 'val_loss': [], 'learning_rate': [],
        **{f'val_mae_{t}': [] for t in TARGETS},
        **{f'val_rmse_{t}': [] for t in TARGETS},
        **{f'val_r2_{t}': [] for t in TARGETS},
        'val_r2_avg': [],
        'epoch_time': [],  # Tiempo por epoch
    }
    
    # Early stopping inteligente
    try:
        from ..utils.early_stopping import IntelligentEarlyStopping
        early_stopping_patience = config.get('early_stopping_patience', 15)
        early_stopping = IntelligentEarlyStopping(
            patience=early_stopping_patience,  # Usa config en lugar de hardcodeado
            min_delta_percent=0.005,  # Reducido de 1% a 0.5% para detectar mejoras pequeñas
            r2_threshold=-2.0,
            r2_consecutive=2,
            val_loss_increase_epochs=3
        )
        use_intelligent_early_stopping = True
        logger.info(f"Using IntelligentEarlyStopping (patience={early_stopping_patience}, min_delta=0.5%)")
    except ImportError:
        logger.warning("IntelligentEarlyStopping not available, using basic early stopping")
        use_intelligent_early_stopping = False
    
    # Early stopping y checkpoints (fallback)
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None
    best_epoch = 0
    improvement_threshold = config.get('improvement_threshold', 1e-4)
    early_stopping_patience = config.get('early_stopping_patience', 10)
    
    # Guardar sigmas iniciales para comparación
    initial_sigmas = None
    if use_uncertainty_loss:
        initial_sigmas = criterion.get_sigmas().copy()
        logger.info(f"Sigmas iniciales: {initial_sigmas}")
    
    # Directorio para checkpoints
    if save_dir is None:
        save_dir = get_regressors_artifacts_dir()
    checkpoint_dir = save_dir / "checkpoints"
    ensure_dir_exists(checkpoint_dir)
    
    # Funciones auxiliares para manejar targets y outputs
    def _split_targets(batch_targets: Any, device: torch.device) -> Dict[str, torch.Tensor]:
        """Normaliza el formato de targets a tensores 1D por target en device."""
        if isinstance(batch_targets, dict):
            # suponer ya en device
            return {k: v.to(device) for k, v in batch_targets.items()}
        
        if isinstance(batch_targets, torch.Tensor):
            t = batch_targets
            
            # si es 1D -> convertir a (1, n_targets)
            if t.ndim == 1:
                t = t.unsqueeze(0)
            
            # si tiene >2 dims aplanar a (B, n_targets)
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
        """Normaliza la salida del modelo a dict de tensores 2D (batch,)."""
        if isinstance(batch_outputs, dict):
            return batch_outputs
        
        if isinstance(batch_outputs, torch.Tensor):
            out = batch_outputs
            
            # If output is 1D (no batch dim), add batch dim
            if out.ndim == 1:
                out = out.unsqueeze(0)
            
            # If output has extra spatial dims (e.g., [B, C, H, W]) flatten to [B, C_flat]
            if out.ndim > 2:
                out = out.view(out.shape[0], -1)
            
            # Now ensure we have at least 2 dims and enough columns
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
    
    # Validar pérdida inicial
    logger.info("=== Validando pérdida inicial ===")
    model.eval()
    initial_val_loss = 0.0
    n_batches_checked = 0
    with torch.no_grad():
        for batch_data in val_loader:
            if use_pixel_features:
                if len(batch_data) != 3:
                    continue
                images, targets_batch, pixel_features = batch_data
                images = images.to(device)
                pixel_features = pixel_features.to(device)
                inputs = (images, pixel_features)
            else:
                if len(batch_data) != 2:
                    continue
                images, targets_batch = batch_data
                images = images.to(device)
                inputs = (images,)
            
            outputs = model(*inputs)
            outputs_dict = _split_outputs(outputs)
            targets_dict = _split_targets(targets_batch, device)
            
            batch_loss = 0.0
            for target in TARGETS:
                target_loss = criterion(
                    outputs_dict[target].squeeze(),
                    targets_dict[target].squeeze()
                )
                batch_loss += target_loss
            
            initial_val_loss += batch_loss.item()
            n_batches_checked += 1
            if n_batches_checked >= 5:  # Solo verificar primeros 5 batches
                break
    
    if n_batches_checked > 0:
        initial_val_loss = initial_val_loss / n_batches_checked
        logger.info(f"Pérdida inicial (promedio de {n_batches_checked} batches): {initial_val_loss:.4f}")
        
        # Si la pérdida inicial es extremadamente alta, advertir
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
    logger.info("=================================")
    
    # Training loop mejorado
    logger.info(f"=== Iniciando entrenamiento ({epochs} épocas) ===")
    start_time_total = time.time()
    
    # Paso 1: Loggear el rango de salida del modelo ANTES de la loss
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
                # Si es diccionario, obtener todos los valores
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
    
    for epoch in range(epochs):
        epoch_start_time = time.time()
        
        # --- Entrenamiento ---
        model.train()
        train_loss = 0.0
        n_batches = 0
        
        for batch_idx, batch_data in enumerate(train_loader):
            batch_start_time = time.time()
            
            # Manejo de modelo híbrido
            if use_pixel_features:
                if len(batch_data) != 3:
                    logger.error(f"Error: Se esperaban 3 tensores, se obtuvieron {len(batch_data)}")
                    continue
                images, targets_batch, pixel_features = batch_data
                images = images.to(device, non_blocking=True)
                pixel_features = pixel_features.to(device, non_blocking=True)
                inputs = (images, pixel_features)
            else:
                if len(batch_data) != 2:
                    logger.error(f"Error: Se esperaban 2 tensores, se obtuvieron {len(batch_data)}")
                    continue
                images, targets_batch = batch_data
                images = images.to(device, non_blocking=True)
                inputs = (images,)
            
            optimizer.zero_grad()
            
            outputs = model(*inputs)
            
            # Logging temporal para depuración
            logger.debug(
                f"Train batch shapes -> outputs: {outputs.shape if isinstance(outputs, torch.Tensor) else 'dict'}, "
                f"targets: {targets_batch.shape if isinstance(targets_batch, torch.Tensor) else 'dict'}"
            )
            
            outputs_dict = _split_outputs(outputs)
            loss = 0.0
            targets_dict = _split_targets(targets_batch, device)
            
            # Use uncertainty-weighted loss if available
            if use_uncertainty_loss:
                # Convert outputs_dict and targets_dict to tensors
                outputs_tensor = torch.stack([
                    outputs_dict[target].squeeze() for target in TARGETS
                ], dim=1)  # [batch, 4]
                targets_tensor = torch.stack([
                    targets_dict[target].squeeze() for target in TARGETS
                ], dim=1)  # [batch, 4]
                
                loss = criterion(outputs_tensor, targets_tensor)
            else:
                for target in TARGETS:
                    target_values = targets_dict[target]
                    target_loss = criterion(
                        outputs_dict[target].squeeze(),
                        target_values.squeeze()
                    )
                    loss += target_loss
            
            # Validar pérdida del batch
            if not torch.isfinite(loss):
                logger.error(f"Batch {batch_idx}: Pérdida no finita: {loss.item()}")
                continue
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.get('max_grad_norm', 1.0))
            optimizer.step()
            
            batch_loss_value = loss.item()
            train_loss += batch_loss_value
            n_batches += 1
            
            # Log cada N batches (cada 10% de los batches o mínimo cada 10)
            log_every_n = max(10, len(train_loader) // 10)
            if (batch_idx + 1) % log_every_n == 0 or batch_idx == 0:
                batch_time = time.time() - batch_start_time
                logger.debug(
                    f"Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}/{len(train_loader)}: "
                    f"Loss={batch_loss_value:.4f}, Time={batch_time:.3f}s"
                )
        
        avg_train_loss = train_loss / (n_batches + 1e-6)
        
        # --- Validación ---
        model.eval()
        val_loss = 0.0
        val_metrics_epoch = {target: {'preds': [], 'targets': []} for target in TARGETS}
        n_val_batches = 0
        
        with torch.no_grad():
            for batch_data in val_loader:
                if use_pixel_features:
                    if len(batch_data) != 3:
                        continue
                    images, targets_batch, pixel_features = batch_data
                    images = images.to(device)
                    pixel_features = pixel_features.to(device)
                    inputs = (images, pixel_features)
                else:
                    if len(batch_data) != 2:
                        continue
                    images, targets_batch = batch_data
                    images = images.to(device)
                    inputs = (images,)
                
                outputs = model(*inputs)
                
                # Logging temporal para depuración
                logger.debug(
                    f"Val batch shapes -> outputs: {outputs.shape if isinstance(outputs, torch.Tensor) else 'dict'}, "
                    f"targets: {targets_batch.shape if isinstance(targets_batch, torch.Tensor) else 'dict'}"
                )
                
                outputs_dict = _split_outputs(outputs)
                batch_loss = 0.0
                targets_dict = _split_targets(targets_batch, device)
                
                # Use uncertainty-weighted loss if available
                if use_uncertainty_loss:
                    outputs_tensor = torch.stack([
                        outputs_dict[target].squeeze() for target in TARGETS
                    ], dim=1)  # [batch, 4]
                    targets_tensor = torch.stack([
                        targets_dict[target].squeeze() for target in TARGETS
                    ], dim=1)  # [batch, 4]
                    
                    batch_loss = criterion(outputs_tensor, targets_tensor)
                else:
                    for target in TARGETS:
                        target_values = targets_dict[target]
                        target_loss = criterion(
                            outputs_dict[target].squeeze(),
                            target_values.squeeze()
                        )
                        batch_loss = batch_loss + target_loss
                
                # Store predictions and targets for metrics (for both loss types)
                for target in TARGETS:
                    val_metrics_epoch[target]['preds'].extend(
                        outputs_dict[target].cpu().numpy().flatten()
                    )
                    val_metrics_epoch[target]['targets'].extend(
                        targets_dict[target].cpu().numpy().flatten()
                    )
                
                val_loss += batch_loss.item()
                n_val_batches += 1
        
        avg_val_loss = val_loss / (n_val_batches + 1e-6)
        
        # Actualizar scheduler
        if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(avg_val_loss)
            current_lr = optimizer.param_groups[0]['lr']
        else:
            scheduler.step()
            current_lr = scheduler.get_last_lr()[0] if hasattr(scheduler, 'get_last_lr') else optimizer.param_groups[0]['lr']
        
        # Calcular tiempo de epoch
        epoch_time = time.time() - epoch_start_time
        
        # Guardar en historial
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['learning_rate'].append(current_lr)
        history['epoch_time'].append(epoch_time)
        
        # Desnormalizar y calcular métricas R²
        pred_dict_norm = {t: np.array(val_metrics_epoch[t]['preds']) for t in TARGETS}
        targ_dict_norm = {t: np.array(val_metrics_epoch[t]['targets']) for t in TARGETS}
        
        # Validar alineación
        if not validate_predictions_targets_alignment(pred_dict_norm, targ_dict_norm):
            logger.error("Problema de alineación entre predicciones y targets")
        
        # Desnormalizar y calcular métricas
        metrics_per_target, avg_r2 = denormalize_and_calculate_metrics(
            predictions_norm=pred_dict_norm,
            targets_norm=targ_dict_norm,
            scalers=scalers,
            target_names=TARGETS,
            verbose=False
        )
        
        # Guardar métricas en history
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
        
        # Construir log string
        log_str = (
            f"Epoch {epoch+1}/{epochs} | "
            f"Train Loss: {avg_train_loss:.4f} | "
            f"Val Loss: {avg_val_loss:.4f} | "
            f"LR: {current_lr:.2e} | "
            f"Time: {epoch_time:.2f}s"
        )
        
        # Agregar R² por target
        for target in TARGETS:
            if target in metrics_per_target:
                r2 = metrics_per_target[target]['r2']
                log_str += f" | {target} R²: {r2:.4f}"
        
        log_str += f" | Avg R²: {avg_r2:.4f}"
        
        # Log sigmas if using uncertainty loss
        if use_uncertainty_loss:
            sigmas = criterion.get_sigmas()
            # Mostrar cambio en sigmas desde el inicio
            if initial_sigmas is not None:
                sigma_changes = {k: f"{sigmas[k]:.4f} (Δ{((sigmas[k] - initial_sigmas.get(k, 0.3)) / 0.3 * 100):+.1f}%)" 
                               for k in sigmas}
                log_str += f" | Sigmas: {sigma_changes}"
            else:
                log_str += f" | Sigmas: {sigmas}"
        
        logger.info(log_str)
        
        # Log detallado cada 5 épocas o si hay problemas
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
        
        # Early stopping inteligente o básico
        r2_scores = {target: metrics_per_target.get(target, {}).get('r2', 0.0) for target in TARGETS}
        
        if use_intelligent_early_stopping:
            should_stop, is_best_loss, should_reduce_lr, should_rollback = early_stopping(
                epoch + 1,
                avg_val_loss,
                r2_scores,
                optimizer
            )
            
            if is_best_loss:
                best_val_loss = avg_val_loss
                best_epoch = epoch + 1
                best_model_state = model.state_dict().copy()
                
                # Guardar checkpoint
                checkpoint_path = checkpoint_dir / "best_loss.pt"
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': best_model_state,
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'val_loss': best_val_loss,
                    'metrics': metrics_per_target,
                    'avg_r2': avg_r2,
                    'config': config
                }, checkpoint_path)
                logger.info(f"✓ Best loss checkpoint guardado: {checkpoint_path} (Val Loss: {best_val_loss:.4f})")
            
            # Guardar best_avg_r2 checkpoint
            best_avg_r2 = max(history.get('val_r2_avg', [0.0])) if history.get('val_r2_avg') else -float('inf')
            if avg_r2 > best_avg_r2:
                checkpoint_path = checkpoint_dir / "best_avg_r2.pt"
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'val_loss': avg_val_loss,
                    'metrics': metrics_per_target,
                    'avg_r2': avg_r2,
                    'config': config
                }, checkpoint_path)
                logger.info(f"✓ Best R² checkpoint guardado: {checkpoint_path} (Avg R²: {avg_r2:.4f})")
            
            # Rollback if needed
            if should_rollback and best_model_state is not None:
                logger.warning("Rolling back to best checkpoint")
                model.load_state_dict(best_model_state)
            
            if should_stop:
                logger.info(f"Early stopping en época {epoch+1} (mejor época: {best_epoch}, Val Loss: {best_val_loss:.4f})")
                break
        else:
            # Early stopping básico (fallback)
            if avg_val_loss < best_val_loss - improvement_threshold:
                best_val_loss = avg_val_loss
                best_epoch = epoch + 1
                patience_counter = 0
                best_model_state = model.state_dict().copy()
                
                # Guardar checkpoint
                checkpoint_path = checkpoint_dir / f"best_model_epoch_{epoch+1}.pt"
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': best_model_state,
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'val_loss': best_val_loss,
                    'metrics': metrics_per_target,
                    'avg_r2': avg_r2,
                    'config': config
                }, checkpoint_path)
                logger.info(f"✓ Checkpoint guardado: {checkpoint_path} (Val Loss: {best_val_loss:.4f})")
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping en época {epoch+1} (mejor época: {best_epoch}, Val Loss: {best_val_loss:.4f})")
                break
    
    # Cargar mejor modelo antes de guardar
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info(f"Mejor modelo cargado (Época {best_epoch}, Val Loss: {best_val_loss:.4f})")
    else:
        logger.warning("No se encontró best_model_state, guardando modelo actual")
        best_val_loss = avg_val_loss if 'avg_val_loss' in locals() else float('inf')
        best_epoch = epochs
    
    total_time = time.time() - start_time_total
    logger.info(f"=== Entrenamiento completado en {total_time:.2f}s ===")
    
    # === GUARDADO DE MODELO FINAL ===
    # El pipeline espera hybrid.pt o multihead.pt en /app/ml/artifacts/regressors/
    artifacts_dir = get_regressors_artifacts_dir()
    model_name = "hybrid.pt" if is_hybrid else "multihead.pt"
    final_path = artifacts_dir / model_name
    
    try:
        # Asegurar que el directorio existe
        ensure_dir_exists(artifacts_dir)
        
        # Usar model.module si está en DataParallel/DistributedDataParallel
        model_to_save = model.module if hasattr(model, "module") else model
        
        # Guardar en CPU para evitar problemas de memoria
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
        
        # Verificar que el archivo se guardó correctamente
        if not final_path.exists():
            raise IOError(f"El archivo {final_path} no se creó después de torch.save")
        if final_path.stat().st_size == 0:
            raise IOError(f"El archivo {final_path} está vacío")
        
        # Volver a mover el modelo al device original
        model_to_save.to(original_device)
        
        logger.info(f"[OK] Modelo final guardado en: {final_path}")
        logger.info(f"[OK] Tamaño del archivo: {final_path.stat().st_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        logger.error(f"[ERROR] No se pudo guardar {model_name}: {e}", exc_info=True)
        # Re-lanzar la excepción para que el pipeline lo detecte
        raise
    
    return history

