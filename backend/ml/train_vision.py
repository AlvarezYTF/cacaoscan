"""
Script de entrenamiento para el modelo de visión artificial de cacao.

Este script entrena el CacaoVisionModel utilizando imágenes y medidas físicas
de la base de datos Django, con soporte para validación, checkpoints y logging.
"""

import os
import sys
import logging
import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.images.models import CacaoImage
from .vision_model import CacaoVisionModel, save_model, load_model
from .data_preprocessing import CacaoDataset, CacaoImageTransforms, create_data_loaders, split_dataset
from .config import get_model_path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CacaoTrainer:
    """
    Clase principal para entrenar el modelo de visión de cacao.
    
    Maneja el proceso completo de entrenamiento incluyendo:
    - Carga de datos
    - Entrenamiento y validación
    - Guardado de checkpoints
    - Logging y métricas
    """
    
    def __init__(self, 
                 model: CacaoVisionModel,
                 train_loader: DataLoader,
                 val_loader: Optional[DataLoader] = None,
                 device: str = 'auto',
                 save_dir: str = 'checkpoints'):
        """
        Inicializa el trainer.
        
        Args:
            model (CacaoVisionModel): Modelo a entrenar
            train_loader (DataLoader): DataLoader de entrenamiento
            val_loader (DataLoader, optional): DataLoader de validación
            device (str): Device a usar ('auto', 'cpu', 'cuda')
            save_dir (str): Directorio para guardar checkpoints
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar device
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        self.model.to(self.device)
        logger.info(f"Usando device: {self.device}")
        
        # Métricas de entrenamiento
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        self.epochs_without_improvement = 0
        
        # Configurar TensorBoard
        self.writer = SummaryWriter(log_dir=self.save_dir / 'tensorboard')
        
    def setup_optimizer_and_scheduler(self, 
                                    learning_rate: float = 1e-3,
                                    weight_decay: float = 1e-4,
                                    optimizer_type: str = 'adam',
                                    scheduler_type: str = 'reduce_on_plateau'):
        """
        Configura el optimizador y scheduler.
        
        Args:
            learning_rate (float): Tasa de aprendizaje inicial
            weight_decay (float): Regularización L2
            optimizer_type (str): Tipo de optimizador ('adam', 'sgd', 'adamw')
            scheduler_type (str): Tipo de scheduler ('reduce_on_plateau', 'cosine', 'step')
        """
        # Configurar optimizador
        if optimizer_type.lower() == 'adam':
            self.optimizer = optim.Adam(
                self.model.parameters(),
                lr=learning_rate,
                weight_decay=weight_decay
            )
        elif optimizer_type.lower() == 'adamw':
            self.optimizer = optim.AdamW(
                self.model.parameters(),
                lr=learning_rate,
                weight_decay=weight_decay
            )
        elif optimizer_type.lower() == 'sgd':
            self.optimizer = optim.SGD(
                self.model.parameters(),
                lr=learning_rate,
                momentum=0.9,
                weight_decay=weight_decay
            )
        else:
            raise ValueError(f"Optimizador no soportado: {optimizer_type}")
        
        # Configurar scheduler
        if scheduler_type.lower() == 'reduce_on_plateau':
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                factor=0.5,
                patience=5,
                verbose=True
            )
        elif scheduler_type.lower() == 'cosine':
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=50
            )
        elif scheduler_type.lower() == 'step':
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=20,
                gamma=0.1
            )
        else:
            self.scheduler = None
            
        logger.info(f"Configurado optimizador: {optimizer_type}, scheduler: {scheduler_type}")
    
    def setup_loss_function(self, loss_type: str = 'mse', weights: Optional[List[float]] = None):
        """
        Configura la función de pérdida.
        
        Args:
            loss_type (str): Tipo de pérdida ('mse', 'mae', 'huber', 'weighted_mse')
            weights (List[float], optional): Pesos para cada salida
        """
        if loss_type.lower() == 'mse':
            self.criterion = nn.MSELoss()
        elif loss_type.lower() == 'mae':
            self.criterion = nn.L1Loss()
        elif loss_type.lower() == 'huber':
            self.criterion = nn.SmoothL1Loss()
        elif loss_type.lower() == 'weighted_mse':
            self.criterion = self._weighted_mse_loss
            self.loss_weights = torch.tensor(weights or [1.0, 1.0, 1.0, 1.0]).to(self.device)
        else:
            raise ValueError(f"Función de pérdida no soportada: {loss_type}")
            
        self.loss_type = loss_type
        logger.info(f"Configurada función de pérdida: {loss_type}")
    
    def _weighted_mse_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Función de pérdida MSE ponderada.
        
        Args:
            predictions (torch.Tensor): Predicciones del modelo
            targets (torch.Tensor): Valores objetivo
            
        Returns:
            torch.Tensor: Pérdida calculada
        """
        squared_errors = (predictions - targets) ** 2
        weighted_errors = squared_errors * self.loss_weights
        return weighted_errors.mean()
    
    def train_epoch(self) -> float:
        """
        Entrena una época.
        
        Returns:
            float: Pérdida promedio de la época
        """
        self.model.train()
        total_loss = 0.0
        num_batches = len(self.train_loader)
        
        for batch_idx, (images, targets, metadata) in enumerate(self.train_loader):
            # Mover datos al device
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            predictions = self.model(images)
            loss = self.criterion(predictions, targets)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping para estabilidad
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            
            # Log progreso cada 20 batches
            if batch_idx % 20 == 0:
                logger.info(f"Batch {batch_idx}/{num_batches}, Loss: {loss.item():.6f}")
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate_epoch(self) -> Tuple[float, Dict[str, float]]:
        """
        Valida una época.
        
        Returns:
            Tuple[float, Dict]: Pérdida promedio y métricas detalladas
        """
        if self.val_loader is None:
            return 0.0, {}
        
        self.model.eval()
        total_loss = 0.0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for images, targets, metadata in self.val_loader:
                # Mover datos al device
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                predictions = self.model(images)
                loss = self.criterion(predictions, targets)
                
                total_loss += loss.item()
                
                # Recopilar predicciones para métricas
                all_predictions.append(predictions.cpu().numpy())
                all_targets.append(targets.cpu().numpy())
        
        avg_loss = total_loss / len(self.val_loader)
        
        # Calcular métricas detalladas
        all_predictions = np.concatenate(all_predictions, axis=0)
        all_targets = np.concatenate(all_targets, axis=0)
        
        metrics = self._calculate_metrics(all_predictions, all_targets)
        
        return avg_loss, metrics
    
    def _calculate_metrics(self, predictions: np.ndarray, targets: np.ndarray) -> Dict[str, float]:
        """
        Calcula métricas detalladas.
        
        Args:
            predictions (np.ndarray): Predicciones del modelo
            targets (np.ndarray): Valores objetivo
            
        Returns:
            Dict[str, float]: Métricas calculadas
        """
        metrics = {}
        feature_names = ['width', 'height', 'thickness', 'weight']
        
        # Métricas globales
        metrics['mae_global'] = mean_absolute_error(targets, predictions)
        metrics['mse_global'] = mean_squared_error(targets, predictions)
        metrics['rmse_global'] = np.sqrt(metrics['mse_global'])
        
        # Métricas por característica
        for i, feature in enumerate(feature_names):
            pred_feature = predictions[:, i]
            target_feature = targets[:, i]
            
            metrics[f'mae_{feature}'] = mean_absolute_error(target_feature, pred_feature)
            metrics[f'mse_{feature}'] = mean_squared_error(target_feature, pred_feature)
            metrics[f'rmse_{feature}'] = np.sqrt(metrics[f'mse_{feature}'])
            
            # Error porcentual medio absoluto (MAPE)
            mask = target_feature != 0
            if mask.sum() > 0:
                mape = np.mean(np.abs((target_feature[mask] - pred_feature[mask]) / target_feature[mask])) * 100
                metrics[f'mape_{feature}'] = mape
        
        return metrics
    
    def train(self, 
              num_epochs: int = 100,
              early_stopping_patience: int = 15,
              save_every: int = 10,
              validate_every: int = 1) -> Dict:
        """
        Ejecuta el entrenamiento completo.
        
        Args:
            num_epochs (int): Número de épocas
            early_stopping_patience (int): Paciencia para early stopping
            save_every (int): Guardar checkpoint cada N épocas
            validate_every (int): Validar cada N épocas
            
        Returns:
            Dict: Historial de entrenamiento
        """
        logger.info(f"Iniciando entrenamiento por {num_epochs} épocas")
        logger.info(f"Tamaño dataset entrenamiento: {len(self.train_loader.dataset)}")
        if self.val_loader:
            logger.info(f"Tamaño dataset validación: {len(self.val_loader.dataset)}")
        
        training_history = {
            'train_losses': [],
            'val_losses': [],
            'metrics': [],
            'epochs': [],
            'best_epoch': 0,
            'best_val_loss': float('inf')
        }
        
        start_time = time.time()
        
        for epoch in range(num_epochs):
            epoch_start_time = time.time()
            
            # Entrenamiento
            train_loss = self.train_epoch()
            self.train_losses.append(train_loss)
            training_history['train_losses'].append(train_loss)
            
            # Validación
            val_loss = 0.0
            metrics = {}
            if epoch % validate_every == 0 and self.val_loader:
                val_loss, metrics = self.validate_epoch()
                self.val_losses.append(val_loss)
                training_history['val_losses'].append(val_loss)
                training_history['metrics'].append(metrics)
                
                # Early stopping y mejor modelo
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.epochs_without_improvement = 0
                    training_history['best_epoch'] = epoch
                    training_history['best_val_loss'] = val_loss
                    
                    # Guardar mejor modelo
                    best_model_path = self.save_dir / 'best_model.pth'
                    save_model(
                        self.model,
                        str(best_model_path),
                        epoch=epoch,
                        optimizer_state=self.optimizer.state_dict(),
                        loss=val_loss,
                        additional_info={'metrics': metrics}
                    )
                    logger.info(f"Nuevo mejor modelo guardado con val_loss: {val_loss:.6f}")
                else:
                    self.epochs_without_improvement += 1
            
            # Logging
            epoch_time = time.time() - epoch_start_time
            lr = self.optimizer.param_groups[0]['lr']
            
            log_msg = f"Época {epoch+1}/{num_epochs} "
            log_msg += f"- Train Loss: {train_loss:.6f} "
            if val_loss > 0:
                log_msg += f"- Val Loss: {val_loss:.6f} "
            log_msg += f"- LR: {lr:.2e} "
            log_msg += f"- Tiempo: {epoch_time:.2f}s"
            
            logger.info(log_msg)
            
            # TensorBoard logging
            self.writer.add_scalar('Loss/Train', train_loss, epoch)
            if val_loss > 0:
                self.writer.add_scalar('Loss/Validation', val_loss, epoch)
            self.writer.add_scalar('Learning_Rate', lr, epoch)
            
            # Log métricas a TensorBoard
            for metric_name, metric_value in metrics.items():
                self.writer.add_scalar(f'Metrics/{metric_name}', metric_value, epoch)
            
            # Actualizar scheduler
            if self.scheduler:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss if val_loss > 0 else train_loss)
                else:
                    self.scheduler.step()
            
            # Guardar checkpoint periódico
            if (epoch + 1) % save_every == 0:
                checkpoint_path = self.save_dir / f'checkpoint_epoch_{epoch+1}.pth'
                save_model(
                    self.model,
                    str(checkpoint_path),
                    epoch=epoch,
                    optimizer_state=self.optimizer.state_dict(),
                    loss=val_loss if val_loss > 0 else train_loss,
                    additional_info={'train_loss': train_loss, 'val_loss': val_loss}
                )
                logger.info(f"Checkpoint guardado: {checkpoint_path}")
            
            # Early stopping
            if self.epochs_without_improvement >= early_stopping_patience and val_loss > 0:
                logger.info(f"Early stopping en época {epoch+1} "
                          f"(sin mejora por {early_stopping_patience} épocas)")
                break
            
            training_history['epochs'].append(epoch)
        
        total_time = time.time() - start_time
        logger.info(f"Entrenamiento completado en {total_time:.2f} segundos")
        
        # Guardar modelo final
        final_model_path = self.save_dir / 'final_model.pth'
        save_model(
            self.model,
            str(final_model_path),
            epoch=epoch,
            optimizer_state=self.optimizer.state_dict(),
            loss=val_loss if val_loss > 0 else train_loss,
            additional_info={'training_history': training_history}
        )
        
        # Guardar historial de entrenamiento
        history_path = self.save_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(training_history, f, indent=2)
        
        self.writer.close()
        return training_history


def main():
    """Función principal de entrenamiento."""
    parser = argparse.ArgumentParser(description='Entrenar modelo de visión de cacao')
    parser.add_argument('--epochs', type=int, default=100, help='Número de épocas')
    parser.add_argument('--batch-size', type=int, default=16, help='Tamaño del batch')
    parser.add_argument('--learning-rate', type=float, default=1e-3, help='Tasa de aprendizaje')
    parser.add_argument('--weight-decay', type=float, default=1e-4, help='Regularización L2')
    parser.add_argument('--device', type=str, default='auto', help='Device (auto/cpu/cuda)')
    parser.add_argument('--save-dir', type=str, default='checkpoints', help='Directorio de guardado')
    parser.add_argument('--train-ratio', type=float, default=0.8, help='Proporción de entrenamiento')
    parser.add_argument('--image-size', type=int, default=224, help='Tamaño de imagen')
    parser.add_argument('--augment', action='store_true', help='Usar augmentación de datos')
    parser.add_argument('--optimizer', type=str, default='adam', help='Optimizador (adam/adamw/sgd)')
    parser.add_argument('--scheduler', type=str, default='reduce_on_plateau', help='Scheduler')
    parser.add_argument('--loss', type=str, default='mse', help='Función de pérdida')
    
    args = parser.parse_args()
    
    # Verificar datos disponibles
    total_images = CacaoImage.objects.filter(
        width__isnull=False,
        height__isnull=False,
        thickness__isnull=False,
        weight__isnull=False,
        image__isnull=False
    ).count()
    
    if total_images == 0:
        logger.error("No hay imágenes con medidas completas disponibles para entrenamiento")
        return
    
    logger.info(f"Encontradas {total_images} imágenes con medidas completas")
    
    # Crear dataset
    transforms = CacaoImageTransforms(
        image_size=(args.image_size, args.image_size),
        augment=args.augment
    )
    
    full_dataset = CacaoDataset(
        transforms=transforms.get_transforms(training=False),
        filter_complete=True
    )
    
    # Dividir dataset
    train_dataset, val_dataset = split_dataset(
        full_dataset,
        train_ratio=args.train_ratio,
        val_ratio=1.0 - args.train_ratio
    )
    
    # Actualizar transformaciones
    train_dataset.transforms = transforms.get_transforms(training=True)
    val_dataset.transforms = transforms.get_transforms(training=False)
    
    # Crear data loaders
    train_loader, val_loader = create_data_loaders(
        train_dataset,
        val_dataset,
        batch_size=args.batch_size,
        num_workers=2  # Reducido para compatibilidad
    )
    
    # Crear modelo
    model = CacaoVisionModel()
    logger.info("Modelo creado:")
    info = model.get_model_info()
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    # Crear trainer
    trainer = CacaoTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=args.device,
        save_dir=args.save_dir
    )
    
    # Configurar optimización
    trainer.setup_optimizer_and_scheduler(
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        optimizer_type=args.optimizer,
        scheduler_type=args.scheduler
    )
    
    trainer.setup_loss_function(loss_type=args.loss)
    
    # Entrenar
    history = trainer.train(num_epochs=args.epochs)
    
    # Guardar modelo final en la ubicación esperada
    model_path = get_model_path('vision_model')
    if hasattr(model_path, 'parent'):
        model_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_model(
        trainer.model,
        str(model_path),
        epoch=history.get('best_epoch', 0),
        loss=history.get('best_val_loss', 0.0),
        additional_info={'training_complete': True, 'history': history}
    )
    
    logger.info(f"Modelo final guardado en: {model_path}")
    logger.info("Entrenamiento completado exitosamente!")


if __name__ == "__main__":
    main()
