"""
Script de entrenamiento para modelos de regresión de dimensiones de cacao.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging
import json
import time
from datetime import datetime

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from .models import create_model, TARGETS, TARGET_NAMES, get_model_info
from .scalers import CacaoScalers, save_scalers


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
        
        Args:
            model: Modelo a entrenar
            train_loader: DataLoader de entrenamiento
            val_loader: DataLoader de validación
            scalers: Escaladores para normalización
            target: Target a entrenar
            device: Dispositivo para entrenamiento
            config: Configuración de entrenamiento
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.scalers = scalers
        self.target = target
        self.device = device
        self.config = config
        
        # Configurar optimizador
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config.get('learning_rate', 1e-4),
            weight_decay=config.get('weight_decay', 1e-4)
        )
        
        # Configurar scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=config.get('epochs', 50),
            eta_min=config.get('min_lr', 1e-6)
        )
        
        # Criterio de pérdida
        self.criterion = nn.MSELoss()
        
        # Early stopping
        self.early_stopping_patience = config.get('early_stopping_patience', 10)
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.best_model_state = None
        
        # Historial de entrenamiento
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'val_mae': [],
            'val_rmse': [],
            'val_r2': [],
            'learning_rate': []
        }
        
        logger.info(f"Entrenador inicializado para target: {target}")
        logger.info(f"Modelo: {get_model_info(self.model)}")
    
    def train_epoch(self) -> float:
        """Entrena el modelo por una época."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, (images, targets) in enumerate(self.train_loader):
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            
            # Calcular pérdida
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # Log periódico
            if batch_idx % 10 == 0:
                logger.debug(f"Epoch batch {batch_idx}/{len(self.train_loader)}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate_epoch(self) -> Tuple[float, float, float, float]:
        """
        Valida el modelo por una época.
        
        Returns:
            Tuple con (loss, mae, rmse, r2)
        """
        self.model.eval()
        total_loss = 0.0
        total_mae = 0.0
        total_rmse = 0.0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for images, targets in self.val_loader:
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)
                
                total_loss += loss.item()
                
                # Convertir a numpy para métricas
                predictions = outputs.cpu().numpy().flatten()
                targets_np = targets.cpu().numpy().flatten()
                
                all_predictions.extend(predictions)
                all_targets.extend(targets_np)
        
        # Calcular métricas
        all_predictions = np.array(all_predictions)
        all_targets = np.array(all_targets)
        
        avg_loss = total_loss / len(self.val_loader)
        mae = np.mean(np.abs(all_predictions - all_targets))
        rmse = np.sqrt(np.mean((all_predictions - all_targets) ** 2))
        
        # R² score
        ss_res = np.sum((all_targets - all_predictions) ** 2)
        ss_tot = np.sum((all_targets - np.mean(all_targets)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return avg_loss, mae, rmse, r2
    
    def train(self) -> Dict[str, List[float]]:
        """
        Entrena el modelo completo.
        
        Returns:
            Historial de entrenamiento
        """
        logger.info(f"Iniciando entrenamiento para {self.target}")
        logger.info(f"Épocas: {self.config['epochs']}, Batch size: {self.config['batch_size']}")
        
        start_time = time.time()
        
        for epoch in range(self.config['epochs']):
            epoch_start = time.time()
            
            # Entrenar
            train_loss = self.train_epoch()
            
            # Validar
            val_loss, val_mae, val_rmse, val_r2 = self.validate_epoch()
            
            # Actualizar scheduler
            self.scheduler.step()
            current_lr = self.scheduler.get_last_lr()[0]
            
            # Guardar en historial
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['val_mae'].append(val_mae)
            self.history['val_rmse'].append(val_rmse)
            self.history['val_r2'].append(val_r2)
            self.history['learning_rate'].append(current_lr)
            
            # Early stopping check
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.best_model_state = self.model.state_dict().copy()
            else:
                self.patience_counter += 1
            
            # Log de época
            epoch_time = time.time() - epoch_start
            logger.info(
                f"Epoch {epoch+1}/{self.config['epochs']} - "
                f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                f"Val MAE: {val_mae:.4f}, Val RMSE: {val_rmse:.4f}, "
                f"Val R²: {val_r2:.4f}, LR: {current_lr:.2e}, "
                f"Time: {epoch_time:.2f}s"
            )
            
            # Early stopping
            if self.patience_counter >= self.early_stopping_patience:
                logger.info(f"Early stopping en época {epoch+1}")
                break
        
        # Cargar mejor modelo
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            logger.info("Mejor modelo cargado")
        
        total_time = time.time() - start_time
        logger.info(f"Entrenamiento completado en {total_time:.2f}s")
        
        return self.history
    
    def save_model(self, file_path: Path) -> None:
        """Guarda el modelo entrenado."""
        try:
            ensure_dir_exists(file_path.parent)
            
            # Información del modelo
            model_info = {
                'target': self.target,
                'model_type': type(self.model).__name__,
                'config': self.config,
                'best_val_loss': self.best_val_loss,
                'training_history': self.history,
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar modelo y metadatos
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_info': model_info,
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict()
            }, file_path)
            
            # Verificar que el archivo se guardó correctamente
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"✅ Modelo guardado exitosamente en {file_path} ({file_path.stat().st_size} bytes)")
            else:
                logger.error(f"❌ Error: El archivo no se guardó correctamente: {file_path}")
                raise IOError(f"No se pudo guardar el modelo en {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Error guardando modelo para {self.target}: {e}")
            raise


def train_single_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    target: str,
    config: Dict,
    device: torch.device
) -> Dict[str, List[float]]:
    """
    Entrena un modelo individual.
    
    Args:
        model: Modelo a entrenar
        train_loader: DataLoader de entrenamiento
        val_loader: DataLoader de validación
        scalers: Escaladores para normalización
        target: Target a entrenar
        config: Configuración de entrenamiento
        device: Dispositivo para entrenamiento
        
    Returns:
        Historial de entrenamiento
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
    
    return history


def train_multi_head_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    config: Dict,
    device: torch.device
) -> Dict[str, List[float]]:
    """
    Entrena un modelo multi-head.
    
    Args:
        model: Modelo multi-head a entrenar
        train_loader: DataLoader de entrenamiento
        val_loader: DataLoader de validación
        scalers: Escaladores para normalización
        config: Configuración de entrenamiento
        device: Dispositivo para entrenamiento
        
    Returns:
        Historial de entrenamiento
    """
    logger.info("Entrenando modelo multi-head")
    
    # Configurar optimizador
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.get('learning_rate', 1e-4),
        weight_decay=config.get('weight_decay', 1e-4)
    )
    
    # Configurar scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config.get('epochs', 50),
        eta_min=config.get('min_lr', 1e-6)
    )
    
    criterion = nn.MSELoss()
    
    # Historial
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_mae': {target: [] for target in TARGETS},
        'val_rmse': {target: [] for target in TARGETS},
        'val_r2': {target: [] for target in TARGETS},
        'learning_rate': []
    }
    
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None
    
    model = model.to(device)
    
    for epoch in range(config['epochs']):
        # Entrenamiento
        model.train()
        train_loss = 0.0
        
        for batch_idx, (images, targets_dict) in enumerate(train_loader):
            images = images.to(device)
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = 0.0
            
            # Calcular pérdida para cada target
            for target in TARGETS:
                target_values = targets_dict[target].to(device)
                target_loss = criterion(outputs[target], target_values)
                loss += target_loss
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validación
        model.eval()
        val_loss = 0.0
        val_metrics = {target: {'mae': [], 'rmse': [], 'r2': []} for target in TARGETS}
        
        with torch.no_grad():
            for images, targets_dict in val_loader:
                images = images.to(device)
                outputs = model(images)
                
                batch_loss = 0.0
                
                for target in TARGETS:
                    target_values = targets_dict[target].to(device)
                    target_loss = criterion(outputs[target], target_values)
                    batch_loss += target_loss
                    
                    # Calcular métricas
                    pred = outputs[target].cpu().numpy().flatten()
                    true = target_values.cpu().numpy().flatten()
                    
                    mae = np.mean(np.abs(pred - true))
                    rmse = np.sqrt(np.mean((pred - true) ** 2))
                    
                    ss_res = np.sum((true - pred) ** 2)
                    ss_tot = np.sum((true - np.mean(true)) ** 2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                    
                    val_metrics[target]['mae'].append(mae)
                    val_metrics[target]['rmse'].append(rmse)
                    val_metrics[target]['r2'].append(r2)
                
                val_loss += batch_loss
        
        # Promediar métricas
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        
        # Guardar en historial
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['learning_rate'].append(scheduler.get_last_lr()[0])
        
        for target in TARGETS:
            history['val_mae'][target].append(np.mean(val_metrics[target]['mae']))
            history['val_rmse'][target].append(np.mean(val_metrics[target]['rmse']))
            history['val_r2'][target].append(np.mean(val_metrics[target]['r2']))
        
        # Early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            best_model_state = model.state_dict().copy()
        else:
            patience_counter += 1
        
        scheduler.step()
        
        # Log
        logger.info(
            f"Epoch {epoch+1}/{config['epochs']} - "
            f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
        )
        
        for target in TARGETS:
            logger.info(
                f"  {target}: MAE={history['val_mae'][target][-1]:.4f}, "
                f"RMSE={history['val_rmse'][target][-1]:.4f}, "
                f"R²={history['val_r2'][target][-1]:.4f}"
            )
        
        if patience_counter >= config.get('early_stopping_patience', 10):
            logger.info(f"Early stopping en época {epoch+1}")
            break
    
    # Guardar mejor modelo
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    # Guardar modelo multi-head
    artifacts_dir = get_regressors_artifacts_dir()
    model_path = artifacts_dir / "multihead.pt"
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_info': {
            'model_type': 'MultiHeadRegression',
            'config': config,
            'best_val_loss': best_val_loss,
            'training_history': history,
            'timestamp': datetime.now().isoformat()
        }
    }, model_path)
    
    logger.info(f"Modelo multi-head guardado en {model_path}")
    
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
