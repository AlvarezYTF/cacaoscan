"""
Script de entrenamiento para modelos de regresión de dimensiones de cacao.
ACTUALIZADO: Modificado para soportar el 'Flujo Mejorado'.
- 'train_multi_head_model' ahora detecta si se están pasando 'pixel_features'.
- Si es así, pasa (imagen, pixel_features) al 'model.forward()' para
  entrenar el 'HybridCacaoRegression'.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
import json
import time
from datetime import datetime

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from .models import create_model, TARGETS, TARGET_NAMES, get_model_info
from .scalers import CacaoScalers, save_scalers

# Importar Django para usar ModelMetrics
import os
import sys
from pathlib import Path

# Configurar Django
project_root = Path(__file__).resolve().parents[2] # Sube 2 niveles (regression/ml/backend)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
try:
    django.setup()
    from api.models import ModelMetrics, TrainingJob
    from django.contrib.auth.models import User
    DJANGO_LOADED = True
except Exception as e:
    # Fallback si Django no está cargado (ej. script se usa fuera de Django)
    DJANGO_LOADED = False
    print(f"Advertencia: No se pudo cargar Django. ModelMetrics no se guardará. Error: {e}")
    # Definir clases dummy para que el script no falle
    class ModelMetrics:
        objects = type('objects', (object,), {'create': lambda **kwargs: None})
    class TrainingJob:
        pass
    class User:
        objects = type('objects', (object,), {'filter': lambda **kwargs: type('filter', (object,), {'first': lambda: None})()})


logger = get_ml_logger("cacaoscan.ml.regression")


class RegressionTrainer:
    """Entrenador para modelos de regresión de cacao."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        scalers: CacaoScalers,
        target: str,
        device: torch.device,
        config: Dict
    ):
        """
        Inicializa el entrenador.
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.scalers = scalers
        self.target = target
        self.device = device
        self.config = config
        
        # Configurar optimizador mejorado
        learning_rate = config.get('learning_rate', 1e-4)
        # Validar learning rate
        if learning_rate > 5e-4:
            logger.warning(f"Learning rate {learning_rate} puede ser muy alto. Reduciendo a 5e-4")
            learning_rate = 5e-4
        
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=config.get('weight_decay', 1e-4),
            betas=(0.9, 0.999),
            eps=1e-8
        )
        
        # Configurar scheduler mejorado
        scheduler_type = config.get('scheduler_type', 'reduce_on_plateau')
        epochs = config.get('epochs', 50)
        
        if scheduler_type == 'reduce_on_plateau':
            # ReduceLROnPlateau es más robusto para regresión
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                factor=0.5,
                patience=5,
                verbose=True,
                min_lr=config.get('min_lr', 1e-7)
            )
        elif scheduler_type == 'onecycle':
            self.scheduler = optim.lr_scheduler.OneCycleLR(
                self.optimizer,
                max_lr=learning_rate * 10,
                epochs=epochs,
                steps_per_epoch=len(train_loader),
                pct_start=0.3
            )
        elif scheduler_type == 'cosine_warmup':
            self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
                self.optimizer,
                T_0=max(1, epochs // 4),
                T_mult=2,
                eta_min=config.get('min_lr', 1e-7)
            )
        else: # 'cosine'
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=epochs,
                eta_min=config.get('min_lr', 1e-6)
            )
        
        # Criterio de pérdida mejorado: SmoothL1Loss por defecto (más robusta)
        loss_type = config.get('loss_type', 'smooth_l1')
        if loss_type == 'huber':
            self.criterion = nn.HuberLoss(delta=1.0)
        elif loss_type == 'mse':
            self.criterion = nn.MSELoss()
        else: # 'smooth_l1' (default)
            self.criterion = nn.SmoothL1Loss()
        
        logger.info(f"Optimizador: AdamW (lr={learning_rate:.2e}), Loss: {loss_type}, Scheduler: {scheduler_type}")
        
        # Gradient clipping
        self.max_grad_norm = config.get('max_grad_norm', 1.0)
        
        # Early stopping
        self.early_stopping_patience = config.get('early_stopping_patience', 10)
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.best_model_state = None
        
        # Historial
        self.history = {
            'train_loss': [], 'val_loss': [], 'val_mae': [],
            'val_rmse': [], 'val_r2': [], 'learning_rate': []
        }
        
        logger.info(f"Entrenador (individual) inicializado para target: {target}")
        logger.info(f"Modelo: {get_model_info(self.model)}")
    
    def train_epoch(self) -> float:
        """Entrena el modelo por una época."""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, batch_data in enumerate(self.train_loader):
            
            # --- MANEJO DE MODELO HÍBRIDO (Aunque este trainer es para individual) ---
            # El dataloader para individual (creado en train_all) solo debe pasar 2 items
            if len(batch_data) == 3:
                # Caso Híbrido (no debería ocurrir aquí, pero por si acaso)
                images, targets_dict, pixel_features = batch_data
                targets = targets_dict[self.target] # Extraer el target específico
                images = images.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                pixel_features = pixel_features.to(self.device, non_blocking=True)
                inputs = (images, pixel_features)
            else:
                # Caso Individual
                images, targets = batch_data
                images = images.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                inputs = (images,)

            self.optimizer.zero_grad()
            
            outputs = self.model(*inputs)
            loss = self.criterion(outputs.squeeze(), targets.squeeze())
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
            self.optimizer.step()
            
            if isinstance(self.scheduler, optim.lr_scheduler.OneCycleLR):
                self.scheduler.step()
            
            total_loss += loss.item()
        
        return total_loss / (len(self.train_loader) + 1e-6)
    
    def validate_epoch(self) -> Tuple[float, float, float, float]:
        """
        Valida el modelo por una época.
        
        IMPORTANTE: Desnormaliza predicciones y targets antes de calcular R².
        """
        self.model.eval()
        total_loss = 0.0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for batch_data in self.val_loader:
                
                if len(batch_data) == 3:
                    images, targets_dict, pixel_features = batch_data
                    targets = targets_dict[self.target] # Extraer el target específico
                    images = images.to(self.device)
                    targets = targets.to(self.device)
                    pixel_features = pixel_features.to(self.device)
                    inputs = (images, pixel_features)
                else:
                    images, targets = batch_data
                    images = images.to(self.device)
                    targets = targets.to(self.device)
                    inputs = (images,)

                outputs = self.model(*inputs)
                loss = self.criterion(outputs.squeeze(), targets.squeeze())
                
                total_loss += loss.item()
                
                predictions = outputs.cpu().numpy().flatten()
                targets_np = targets.cpu().numpy().flatten()
                
                all_predictions.extend(predictions)
                all_targets.extend(targets_np)
        
        all_predictions = np.array(all_predictions)
        all_targets = np.array(all_targets)
        
        avg_loss = total_loss / (len(self.val_loader) + 1e-6)
        
        # Manejar caso de targets vacíos (raro, pero defensivo)
        if len(all_targets) == 0:
            logger.warning("Val Loader vacío, no se pueden calcular métricas.")
            return avg_loss, 0.0, 0.0, 0.0

        # CRÍTICO: Desnormalizar antes de calcular métricas
        if self.scalers is not None and self.scalers.is_fitted:
            try:
                # Crear diccionarios para desnormalización
                pred_dict_norm = {self.target: all_predictions}
                targ_dict_norm = {self.target: all_targets}
                
                # Desnormalizar
                pred_dict_denorm = self.scalers.inverse_transform(pred_dict_norm)
                targ_dict_denorm = self.scalers.inverse_transform(targ_dict_norm)
                
                all_predictions = pred_dict_denorm[self.target]
                all_targets = targ_dict_denorm[self.target]
                
                logger.debug(f"{self.target}: Predicciones y targets desnormalizados para métricas")
            except Exception as e:
                logger.warning(
                    f"{self.target}: Error desnormalizando para métricas: {e}. "
                    f"Usando valores normalizados (R² puede ser incorrecto)"
                )
        else:
            logger.warning(
                f"{self.target}: Scalers no disponibles, usando valores normalizados "
                f"(R² puede ser incorrecto)"
            )

        # Usar función robusta de R²
        from .metrics import robust_r2_score
        
        mae = np.mean(np.abs(all_predictions - all_targets))
        rmse = np.sqrt(np.mean((all_predictions - all_targets) ** 2))
        r2 = robust_r2_score(
            all_targets,
            all_predictions,
            target_name=self.target,
            verbose=False
        )
        
        return avg_loss, mae, rmse, r2
    
    def train(self) -> Dict[str, List[float]]:
        """Entrena el modelo completo."""
        logger.info(f"Iniciando entrenamiento para {self.target}")
        start_time = time.time()
        
        for epoch in range(self.config['epochs']):
            epoch_start = time.time()
            
            train_loss = self.train_epoch()
            val_loss, val_mae, val_rmse, val_r2 = self.validate_epoch()
            
            # Actualizar scheduler (diferente para ReduceLROnPlateau y OneCycleLR)
            if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                self.scheduler.step(val_loss)
                current_lr = self.optimizer.param_groups[0]['lr']
            elif isinstance(self.scheduler, optim.lr_scheduler.OneCycleLR):
                # OneCycleLR se actualiza en cada step del optimizador
                current_lr = self.optimizer.param_groups[0]['lr']
            else:
                self.scheduler.step()
                current_lr = self.scheduler.get_last_lr()[0] if hasattr(self.scheduler, 'get_last_lr') else self.optimizer.param_groups[0]['lr']
            
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['val_mae'].append(val_mae)
            self.history['val_rmse'].append(val_rmse)
            self.history['val_r2'].append(val_r2)
            self.history['learning_rate'].append(current_lr)
            
            epoch_time = time.time() - epoch_start
            logger.info(
                f"Epoch {epoch+1}/{self.config['epochs']} - "
                f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                f"Val MAE: {val_mae:.4f}, Val RMSE: {val_rmse:.4f}, "
                f"Val R²: {val_r2:.4f}, LR: {current_lr:.2e}, "
                f"Time: {epoch_time:.2f}s"
            )
            
            # Early stopping
            improvement_threshold = self.config.get('improvement_threshold', 1e-4)
            if val_loss < self.best_val_loss - improvement_threshold:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.best_model_state = self.model.state_dict().copy()
            else:
                self.patience_counter += 1
            
            if self.patience_counter >= self.early_stopping_patience:
                logger.info(f"Early stopping en época {epoch+1}")
                break
        
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            logger.info(f"Mejor modelo cargado (Val Loss: {self.best_val_loss:.4f})")
        
        total_time = time.time() - start_time
        logger.info(f"Entrenamiento completado en {total_time:.2f}s")
        
        return self.history
    
    def _convert_to_native_types(self, obj: Any) -> Any:
        """Convierte valores de NumPy/PyTorch a tipos nativos de Python."""
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, torch.Tensor):
            return float(obj.item())
        elif isinstance(obj, dict):
            return {key: self._convert_to_native_types(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_native_types(item) for item in obj]
        return obj
    
    def save_metrics_to_db(self, training_job: Optional[TrainingJob] = None, dataset_info: Optional[Dict] = None) -> None:
        """Guarda las métricas del entrenamiento en la base de datos (si Django está cargado)."""
        if not DJANGO_LOADED:
            logger.warning("Django no está cargado, omitiendo guardado de métricas en DB.")
            return

        try:
            final_metrics = {
                'mae': self.history['val_mae'][-1] if self.history['val_mae'] else 0.0,
                'mse': self.history['val_loss'][-1] if self.history['val_loss'] else 0.0, # Asumimos que la loss es MSE o similar
                'rmse': self.history['val_rmse'][-1] if self.history['val_rmse'] else 0.0,
                'r2_score': self.history['val_r2'][-1] if self.history['val_r2'] else 0.0,
            }

            train_size = dataset_info.get('train_size', 0) if dataset_info else 0
            val_size = dataset_info.get('val_size', 0) if dataset_info else 0
            test_size = dataset_info.get('test_size', 0) if dataset_info else 0
            
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()

            ModelMetrics.objects.create(
                model_name=f"regression_{self.target}",
                model_type='regression',
                target=self.target,
                version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                training_job=training_job,
                created_by=user,
                metric_type='validation',
                
                **final_metrics,
                
                additional_metrics=self._convert_to_native_types({
                    'best_val_loss': self.best_val_loss,
                    'epochs_completed': len(self.history['train_loss']),
                }),
                
                dataset_size=int(train_size + val_size + test_size),
                train_size=int(train_size),
                validation_size=int(val_size),
                test_size=int(test_size),
                
                epochs=int(self.config.get('epochs', 50)),
                batch_size=int(self.config.get('batch_size', 32)),
                learning_rate=float(self.config.get('learning_rate', 1e-4)),
                
                model_params=self._convert_to_native_types({
                    'model_type': self.config.get('model_type', 'resnet18'),
                    'pretrained': self.config.get('pretrained', True),
                    'dropout_rate': self.config.get('dropout_rate', 0.2),
                }),
                
                notes=f"Modelo entrenado para {self.target}."
            )
            
            logger.info(f"[OK] Métricas guardadas en DB para {self.target}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando métricas en DB para {self.target}: {e}")

    def save_model(self, file_path: Path) -> None:
        """Guarda el modelo entrenado."""
        try:
            ensure_dir_exists(file_path.parent)
            
            model_info = {
                'target': self.target,
                'model_type': self.config.get('model_type', type(self.model).__name__),
                'config': self.config,
                'best_val_loss': self.best_val_loss,
                'training_history': self.history,
                'timestamp': datetime.now().isoformat()
            }
            
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_info': model_info,
            }, file_path)
            
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[OK] Modelo guardado exitosamente en {file_path}")
            else:
                raise IOError(f"No se pudo guardar el modelo en {file_path}")
                
        except Exception as e:
            logger.error(f"[ERROR] Error guardando modelo para {self.target}: {e}")
            raise


def train_single_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    target: str,
    config: Dict,
    device: torch.device,
    training_job: Optional[TrainingJob] = None,
    dataset_info: Optional[Dict] = None,
    save_metrics: bool = True
) -> Dict[str, List[float]]:
    """
    Entrena un modelo individual.
    """
    trainer = RegressionTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        scalers=scalers,
        target=target,
        device=device,
        config=config
    )
    
    history = trainer.train()
    
    # Guardar modelo
    artifacts_dir = get_regressors_artifacts_dir()
    model_path = artifacts_dir / f"{target}.pt"
    trainer.save_model(model_path)
    
    # Guardar métricas en la base de datos
    if save_metrics:
        trainer.save_metrics_to_db(training_job, dataset_info)
    
    return history


def train_multi_head_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    config: Dict,
    device: torch.device,
    training_job: Optional[TrainingJob] = None,
    dataset_info: Optional[Dict] = None,
    save_metrics: bool = True,
    use_improved: bool = True,  # Usar training loop mejorado por defecto
    use_uncertainty_loss: Optional[bool] = None  # Si None, se detecta automáticamente
) -> Dict[str, List[float]]:
    """
    Entrena un modelo multi-head o híbrido.
    ACTUALIZADO: Maneja la entrada de features de píxeles para el modelo híbrido.
    
    Si use_improved=True, usa el training loop mejorado con:
    - Validación de normalización
    - Logging detallado
    - Checkpoints automáticos
    - Validación de pérdidas
    
    Args:
        use_uncertainty_loss: Si usar UncertaintyWeightedLoss. Si None, se detecta automáticamente.
    """
    # Intentar usar training loop mejorado si está disponible
    if use_improved:
        try:
            from .train_improved import train_multi_head_model_improved
            logger.info("Usando training loop mejorado")
            return train_multi_head_model_improved(
                model=model,
                train_loader=train_loader,
                val_loader=val_loader,
                scalers=scalers,
                config=config,
                device=device,
                training_job=training_job,
                dataset_info=dataset_info,
                save_metrics=save_metrics,
                use_uncertainty_loss=use_uncertainty_loss
            )
        except ImportError:
            logger.warning("Training loop mejorado no disponible, usando versión estándar")
    
    # Versión estándar (código original)
    is_hybrid = config.get('hybrid', False) or config.get('model_type') == 'hybrid'
    use_pixel_features = config.get('use_pixel_features', False) and is_hybrid
    
    if is_hybrid:
        logger.info(f"Entrenando modelo HÍBRIDO (use_pixel_features={use_pixel_features})")
    else:
        logger.info("Entrenando modelo MULTI-HEAD")

    model = model.to(device)
    
    # Optimizador mejorado con learning rate más conservador
    learning_rate = config.get('learning_rate', 1e-4)
    # Si el learning rate es muy alto, reducirlo
    if learning_rate > 5e-4:
        logger.warning(f"Learning rate {learning_rate} puede ser muy alto. Reduciendo a 5e-4")
        learning_rate = 5e-4
    
    # CRÍTICO: Verificar si la loss tiene parámetros aprendibles (ej. UncertaintyWeightedLoss)
    # Si los tiene, incluirlos en el optimizador
    criterion = None
    use_uncertainty_loss = False
    try:
        from ..utils.losses import UncertaintyWeightedLoss
        # Intentar detectar si se está usando UncertaintyWeightedLoss
        # Nota: En esta versión estándar, no se crea la loss aquí, pero verificamos si está en config
        if config.get('use_uncertainty_loss', False):
            use_uncertainty_loss = True
            logger.info("UncertaintyWeightedLoss detectado en config, pero no se crea aquí (usar train_improved)")
    except ImportError:
        pass
    
    # Crear loss function (estándar, sin parámetros aprendibles)
    loss_type = config.get('loss_type', 'smooth_l1')
    if loss_type == 'mse':
        criterion = nn.MSELoss()
    elif loss_type == 'huber':
        criterion = nn.HuberLoss(delta=1.0)
    else:  # 'smooth_l1' (default)
        criterion = nn.SmoothL1Loss()
    
    # CRÍTICO: Incluir parámetros del modelo Y de la loss (si tiene parámetros aprendibles)
    # Si la loss tiene parámetros (ej. log_sigmas en UncertaintyWeightedLoss), incluirlos
    # IMPORTANTE: Los sigmas necesitan un LR más alto (100x) para actualizarse correctamente
    if criterion is not None and hasattr(criterion, 'parameters'):
        # Verificar si realmente tiene parámetros aprendibles
        loss_params = list(criterion.parameters())
        if len(loss_params) > 0:
            # Definir Learning Rates separados para modelo y sigmas
            # El modelo usa el LR bajo y estable
            model_lr = learning_rate
            
            # Los sigmas necesitan un LR 100 veces más alto para moverse y balancear las tareas
            # Esto es crítico: con LR bajo, los sigmas no se actualizan (Δ+0.0%)
            sigma_lr = learning_rate * 100.0  # 100x más alto (ej. 1e-5 * 100 = 1e-3)
            
            # Usar grupos de parámetros con LR separados
            optimizer = optim.AdamW(
                [
                    {'params': model.parameters(), 'lr': model_lr},
                    {'params': criterion.parameters(), 'lr': sigma_lr}
                ],
                weight_decay=config.get('weight_decay', 1e-4),
                betas=(0.9, 0.999),
                eps=1e-8
            )
            logger.info("✔ Optimizador incluye parámetros del modelo Y de la loss")
            logger.info(f"  Learning Rate del modelo: {model_lr:.2e}")
            logger.info(f"  Learning Rate de los sigmas: {sigma_lr:.2e} (100x más alto)")
            logger.info(f"  Parámetros del modelo: {sum(p.numel() for p in model.parameters())}")
            logger.info(f"  Parámetros de la loss: {sum(p.numel() for p in loss_params)}")
        else:
            # Solo parámetros del modelo (loss estándar sin parámetros aprendibles)
            optimizer = optim.AdamW(
                model.parameters(),
                lr=learning_rate,
                weight_decay=config.get('weight_decay', 1e-4),
                betas=(0.9, 0.999),
                eps=1e-8
            )
    else:
        # Solo parámetros del modelo (loss estándar sin parámetros aprendibles)
        optimizer = optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=config.get('weight_decay', 1e-4),
            betas=(0.9, 0.999),
            eps=1e-8
        )
    
    # Scheduler mejorado: ReduceLROnPlateau es más robusto para regresión
    scheduler_type = config.get('scheduler_type', 'reduce_on_plateau')
    
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
            T_max=config.get('epochs', 50),
            eta_min=config.get('min_lr', 1e-6)
        )
    else:
        # Default: CosineAnnealingWarmRestarts
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=max(1, config.get('epochs', 50) // 4),
            T_mult=2,
            eta_min=config.get('min_lr', 1e-7)
        )
    
    # Loss function mejorada: SmoothL1Loss es más robusta que MSE
    # NOTA: Si se usa UncertaintyWeightedLoss, debe crearse ANTES del optimizador
    # En esta versión estándar, usamos loss estándar (sin parámetros aprendibles)
    loss_type = config.get('loss_type', 'smooth_l1')
    if loss_type == 'mse':
        criterion = nn.MSELoss()
    elif loss_type == 'huber':
        criterion = nn.HuberLoss(delta=1.0)
    else:  # 'smooth_l1' (default)
        criterion = nn.SmoothL1Loss()
    
    logger.info(f"Optimizador: AdamW (lr={learning_rate:.2e}), Loss: {loss_type}, Scheduler: {scheduler_type}")
    logger.info("NOTA: Para usar UncertaintyWeightedLoss, usar train_improved.py en lugar de esta versión estándar")
    
    history = {
        'train_loss': [], 'val_loss': [], 'learning_rate': [],
        **{f'val_mae_{t}': [] for t in TARGETS},
        **{f'val_rmse_{t}': [] for t in TARGETS},
        **{f'val_r2_{t}': [] for t in TARGETS},
        'val_r2_avg': [],  # R² promedio sobre todos los targets
    }
    
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None

    def _split_targets(batch_targets: Any, device: torch.device) -> Dict[str, torch.Tensor]:
        """
        Normaliza el formato de targets por batch a un dict por clave en TARGETS.
        Soporta:
        - Dict[str, Tensor]
        - Tensor 1D o 2D donde el último dim tiene al menos 4 valores en el orden:
          [alto, ancho, grosor, peso, ...]
        """
        if isinstance(batch_targets, dict):
            return {k: v.to(device) for k, v in batch_targets.items()}

        if isinstance(batch_targets, torch.Tensor):
            # Asegurar dimensión de batch
            if batch_targets.ndim == 1:
                batch_targets = batch_targets.unsqueeze(0)

            # Aplanar todo menos la última dimensión
            if batch_targets.ndim > 2:
                batch_targets = batch_targets.view(-1, batch_targets.shape[-1])

            if batch_targets.shape[-1] < len(TARGETS):
                raise ValueError(
                    f"Se esperaban al menos {len(TARGETS)} columnas para targets tensor, "
                    f"se obtuvo shape={batch_targets.shape}"
                )

            batch_targets = batch_targets.to(device)
            return {
                "alto": batch_targets[:, 0],
                "ancho": batch_targets[:, 1],
                "grosor": batch_targets[:, 2],
                "peso": batch_targets[:, 3],
            }

        raise TypeError(f"Formato de targets no soportado: {type(batch_targets)}")

    def _split_outputs(batch_outputs: Any) -> Dict[str, torch.Tensor]:
        """
        Normaliza la salida del modelo a un dict por TARGET.
        Soporta:
        - Dict[str, Tensor] (ya en formato esperado)
        - Tensor [B, C, ...] con C>=4; se usan las 4 primeras columnas como
          [alto, ancho, grosor, peso].
        """
        if isinstance(batch_outputs, dict):
            return batch_outputs

        if isinstance(batch_outputs, torch.Tensor):
            out = batch_outputs
            # Aplanar todas las dimensiones excepto batch
            if out.ndim > 2:
                out = out.view(out.shape[0], -1)
            if out.shape[1] < len(TARGETS):
                raise ValueError(
                    f"Se esperaban al menos {len(TARGETS)} columnas en outputs tensor, "
                    f"se obtuvo shape={out.shape}"
                )
            return {
                "alto": out[:, 0],
                "ancho": out[:, 1],
                "grosor": out[:, 2],
                "peso": out[:, 3],
            }

        raise TypeError(f"Formato de outputs no soportado: {type(batch_outputs)}")
    
    for epoch in range(config['epochs']):
        # --- Entrenamiento ---
        model.train()
        train_loss = 0.0
        
        for batch_data in train_loader:
            
            # --- MANEJO DE MODELO HÍBRIDO ---
            if use_pixel_features:
                if len(batch_data) != 3:
                    logger.error(f"Error: Se esperaban 3 tensores (img, targets, pixels), se obtuvieron {len(batch_data)}")
                    continue
                images, targets_batch, pixel_features = batch_data
                images = images.to(device, non_blocking=True)
                pixel_features = pixel_features.to(device, non_blocking=True)
                inputs = (images, pixel_features)
            else:
                if len(batch_data) != 2:
                    logger.error(f"Error: Se esperaban 2 tensores (img, targets), se obtuvieron {len(batch_data)}")
                    continue
                images, targets_batch = batch_data
                images = images.to(device, non_blocking=True)
                inputs = (images,)
            
            optimizer.zero_grad()
            
            outputs = model(*inputs)
            outputs_dict = _split_outputs(outputs)
            loss = 0.0
            targets_dict = _split_targets(targets_batch, device)

            for target in TARGETS:
                target_values = targets_dict[target]
                # Asegurar que ambos tengan la misma forma (ej. [B] o [B, 1])
                target_loss = criterion(outputs_dict[target].squeeze(), target_values.squeeze())
                loss += target_loss
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.get('max_grad_norm', 1.0))
            optimizer.step()
            train_loss += loss.item()
        
        avg_train_loss = train_loss / (len(train_loader) + 1e-6)
        
        # --- Validación ---
        model.eval()
        val_loss = 0.0
        val_metrics_epoch = {target: {'preds': [], 'targets': []} for target in TARGETS}
        
        with torch.no_grad():
            for batch_data in val_loader:
                
                # --- MANEJO DE MODELO HÍBRIDO ---
                if use_pixel_features:
                    if len(batch_data) != 3: continue # Ignorar batch corrupto
                    images, targets_batch, pixel_features = batch_data
                    images = images.to(device)
                    pixel_features = pixel_features.to(device)
                    inputs = (images, pixel_features)
                else:
                    if len(batch_data) != 2: continue # Ignorar batch corrupto
                    images, targets_batch = batch_data
                    images = images.to(device)
                    inputs = (images,)
                
                outputs = model(*inputs)
                outputs_dict = _split_outputs(outputs)
                batch_loss = 0.0
                targets_dict = _split_targets(targets_batch, device)

                for target in TARGETS:
                    target_values = targets_dict[target]
                    target_loss = criterion(outputs_dict[target].squeeze(), target_values.squeeze())
                    batch_loss += target_loss
                    
                    val_metrics_epoch[target]['preds'].extend(
                        outputs_dict[target].cpu().numpy().flatten()
                    )
                    val_metrics_epoch[target]['targets'].extend(
                        target_values.cpu().numpy().flatten()
                    )
                
                val_loss += batch_loss.item()
        
        avg_val_loss = val_loss / (len(val_loader) + 1e-6)
        
        # Actualizar scheduler (diferente para ReduceLROnPlateau)
        if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(avg_val_loss)
            current_lr = optimizer.param_groups[0]['lr']
        else:
            scheduler.step()
            current_lr = scheduler.get_last_lr()[0] if hasattr(scheduler, 'get_last_lr') else optimizer.param_groups[0]['lr']
        
        # Calcular métricas de validación
        log_str = (
            f"Epoch {epoch+1}/{config['epochs']} - "
            f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
        )
        
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['learning_rate'].append(current_lr)

        # CRÍTICO: Desnormalizar predicciones y targets antes de calcular métricas
        # Usar función robusta de métricas
        from .metrics import (
            denormalize_and_calculate_metrics,
            validate_predictions_targets_alignment
        )
        
        # Preparar diccionarios de predicciones y targets normalizados
        pred_dict_norm = {t: np.array(val_metrics_epoch[t]['preds']) for t in TARGETS}
        targ_dict_norm = {t: np.array(val_metrics_epoch[t]['targets']) for t in TARGETS}
        
        # Validar alineación
        if not validate_predictions_targets_alignment(pred_dict_norm, targ_dict_norm):
            logger.error("Problema de alineación entre predicciones y targets")
        
        # Desnormalizar y calcular métricas usando función robusta
        metrics_per_target, avg_r2 = denormalize_and_calculate_metrics(
            predictions_norm=pred_dict_norm,
            targets_norm=targ_dict_norm,
            scalers=scalers,
            target_names=TARGETS,
            verbose=False  # No verbose aquí, lo haremos después
        )
        
        # Guardar métricas en history y construir log string
        for target in TARGETS:
            if target in metrics_per_target:
                mae = metrics_per_target[target]['mae']
                rmse = metrics_per_target[target]['rmse']
                r2 = metrics_per_target[target]['r2']
                
                history[f'val_mae_{target}'].append(mae)
                history[f'val_rmse_{target}'].append(rmse)
                history[f'val_r2_{target}'].append(r2)
                log_str += f", {target} R²: {r2:.4f}"
            else:
                logger.warning(f"No se calcularon métricas para {target}")
                history[f'val_mae_{target}'].append(0.0)
                history[f'val_rmse_{target}'].append(0.0)
                history[f'val_r2_{target}'].append(0.0)
                log_str += f", {target} R²: 0.0000"
        
        # Agregar R² promedio al log y al historial
        log_str += f" | Avg R²: {avg_r2:.4f}"
        history['val_r2_avg'].append(avg_r2)

        logger.info(log_str)
        
        # Log detallado por componente (cada 5 épocas o si R² es muy negativo)
        if (epoch + 1) % 5 == 0 or any(
            metrics_per_target.get(t, {}).get('r2', 0) < -100
            for t in TARGETS
        ):
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
            logger.info("==========================================")
        
        # Early stopping
        improvement_threshold = config.get('improvement_threshold', 1e-4)
        if avg_val_loss < best_val_loss - (improvement_threshold):
            best_val_loss = avg_val_loss
            patience_counter = 0
            best_model_state = model.state_dict().copy()
        else:
            patience_counter += 1
        
        # Nota: scheduler.step() ya se llamó arriba (antes de early stopping)
        
        if patience_counter >= config.get('early_stopping_patience', 10):
            logger.info(f"Early stopping en época {epoch+1}")
            break
    
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info(f"Mejor modelo cargado (Val Loss: {best_val_loss:.4f})")
    
    # --- Guardar modelo (Híbrido o Multi-head) ---
    artifacts_dir = get_regressors_artifacts_dir()
    model_name = "hybrid.pt" if is_hybrid else "multihead.pt"
    model_path = artifacts_dir / model_name
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_info': {
            'model_type': 'HybridCacaoRegression' if is_hybrid else 'MultiHeadRegression',
            'config': config,
            'best_val_loss': best_val_loss,
            'training_history': history,
            'timestamp': datetime.now().isoformat()
        }
    }, model_path)
    
    logger.info(f"Modelo {model_name} guardado en {model_path}")
    
    # --- Guardar métricas en DB (si está cargado) ---
    if save_metrics and DJANGO_LOADED:
        try:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            train_size = dataset_info.get('train_size', 0) if dataset_info else 0
            val_size = dataset_info.get('val_size', 0) if dataset_info else 0
            test_size = dataset_info.get('test_size', 0) if dataset_info else 0

            for target in TARGETS:
                ModelMetrics.objects.create(
                    model_name=f"hybrid_regression" if is_hybrid else "multihead_regression",
                    model_type='regression',
                    target=target,
                    version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    training_job=training_job,
                    created_by=user,
                    metric_type='validation',
                    
                    mae=history[f'val_mae_{target}'][-1],
                    mse=history['val_loss'][-1], # Pérdida general
                    rmse=history[f'val_rmse_{target}'][-1],
                    r2_score=history[f'val_r2_{target}'][-1],
                    
                    dataset_size=int(train_size + val_size + test_size),
                    train_size=int(train_size),
                    validation_size=int(val_size),
                    
                    epochs=int(len(history['train_loss'])),
                    batch_size=int(config.get('batch_size', 32)),
                    learning_rate=float(config.get('learning_rate', 1e-4)),
                    
                    model_params={
                        'model_type': config.get('model_type', 'hybrid'),
                        'hybrid': is_hybrid,
                        'use_pixel_features': use_pixel_features,
                        'dropout_rate': config.get('dropout_rate', 0.2),
                    },
                    notes=f"Modelo {'Híbrido' if is_hybrid else 'Multi-head'} para {target}."
                )
            logger.info(f"[OK] Métricas del modelo {model_name} guardadas en DB")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando métricas del modelo {model_name}: {e}")
    
    return history


def get_device() -> torch.device:
    """Obtiene el dispositivo disponible para entrenamiento."""
    if torch.cuda.is_available():
        device = torch.device('cuda')
        logger.info(f"Usando GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        logger.info("Usando CPU")
    
    return device


def create_training_job(
    job_type: str = 'regression',
    model_name: str = 'regression_model',
    dataset_size: int = 0,
    config: Dict = None,
    user: Optional[User] = None
) -> Optional[TrainingJob]:
    """Crea un TrainingJob (si Django está cargado)."""
    if not DJANGO_LOADED:
        logger.warning("Django no está cargado, no se puede crear TrainingJob.")
        return None
        
    try:
        if not user:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        
        job_id = f"{job_type}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        training_job = TrainingJob.objects.create(
            job_id=job_id,
            job_type=job_type,
            model_name=model_name,
            dataset_size=dataset_size,
            epochs=config.get('epochs', 50) if config else 50,
            batch_size=config.get('batch_size', 32) if config else 32,
            learning_rate=config.get('learning_rate', 1e-4) if config else 1e-4,
            config_params=config or {},
            created_by=user,
            status='running'
        )
        
        logger.info(f"[OK] TrainingJob creado con ID: {job_id}")
        return training_job
        
    except Exception as e:
        logger.error(f"[ERROR] Error creando TrainingJob: {e}")
        return None


def update_training_job_metrics(
    training_job: Optional[TrainingJob],
    metrics: Dict,
    model_path: str = None
) -> None:
    """Actualiza un TrainingJob (si Django está cargado)."""
    if not DJANGO_LOADED or not training_job:
        return
        
    try:
        training_job.mark_completed(
            metrics=metrics,
            model_path=model_path
        )
        logger.info(f"[OK] TrainingJob {training_job.job_id} actualizado con métricas")
    except Exception as e:
        logger.error(f"[ERROR] Error actualizando TrainingJob: {e}")