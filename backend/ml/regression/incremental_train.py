"""
Sistema de entrenamiento incremental real para modelos de regresión de cacao.

Este módulo implementa estrategias avanzadas de aprendizaje incremental que permiten:
- Entrenar modelos con nuevos datos sin perder conocimiento previo
- Gestión de versiones de modelos
- Estrategias anti-catastrophic forgetting
- Evaluación continua del rendimiento
- Integración con el sistema existente
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, ConcatDataset, Subset
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
import json
import time
from datetime import datetime
import copy
from collections import defaultdict
import pickle
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from ..utils.io import save_json, load_json
from .models import create_model, TARGETS, TARGET_NAMES, get_model_info
from .scalers import CacaoScalers, save_scalers, load_scalers
from .train import RegressionTrainer, get_device
from ..data.dataset_loader import CacaoDatasetLoader
from ..data.transforms import resize_with_padding, normalize_image

logger = get_ml_logger("cacaoscan.ml.incremental")


class IncrementalDataManager:
    """
    Gestor de datos para entrenamiento incremental.
    
    Maneja la adición de nuevos datos, versionado de datasets,
    y estrategias de muestreo para evitar catastrophic forgetting.
    """
    
    def __init__(self, base_data_dir: Optional[Path] = None):
        """
        Inicializa el gestor de datos incrementales.
        
        Args:
            base_data_dir: Directorio base para datos incrementales
        """
        self.base_data_dir = base_data_dir or Path("backend/ml/data/incremental")
        ensure_dir_exists(self.base_data_dir)
        
        self.datasets_dir = self.base_data_dir / "datasets"
        self.metadata_dir = self.base_data_dir / "metadata"
        ensure_dir_exists(self.datasets_dir)
        ensure_dir_exists(self.metadata_dir)
        
        self.current_version = self._get_latest_version()
        self.dataset_metadata = self._load_dataset_metadata()
        
        logger.info(f"Gestor de datos incrementales inicializado. Versión actual: {self.current_version}")
    
    def _get_latest_version(self) -> int:
        """Obtiene la última versión de dataset."""
        if not self.datasets_dir.exists():
            return 0
        
        versions = []
        for item in self.datasets_dir.iterdir():
            if item.is_dir() and item.name.startswith("v"):
                try:
                    version = int(item.name[1:])
                    versions.append(version)
                except ValueError:
                    continue
        
        return max(versions) if versions else 0
    
    def _load_dataset_metadata(self) -> Dict:
        """Carga metadatos de datasets."""
        metadata_file = self.metadata_dir / "dataset_metadata.json"
        if metadata_file.exists():
            return load_json(metadata_file)
        return {
            "versions": {},
            "current_version": self.current_version,
            "total_samples": 0,
            "last_updated": None
        }
    
    def _save_dataset_metadata(self):
        """Guarda metadatos de datasets."""
        metadata_file = self.metadata_dir / "dataset_metadata.json"
        self.dataset_metadata["last_updated"] = datetime.now().isoformat()
        save_json(self.dataset_metadata, metadata_file)
    
    def add_new_data(self, new_records: List[Dict], version_name: Optional[str] = None) -> int:
        """
        Añade nuevos datos al sistema incremental.
        
        Args:
            new_records: Lista de nuevos registros con formato estándar
            version_name: Nombre opcional para la versión
            
        Returns:
            Número de versión creada
        """
        if not new_records:
            raise ValueError("No se proporcionaron nuevos registros")
        
        # Crear nueva versión
        self.current_version += 1
        version_dir = self.datasets_dir / f"v{self.current_version}"
        ensure_dir_exists(version_dir)
        
        # Guardar nuevos datos
        new_data_file = version_dir / "new_data.json"
        save_json(new_records, new_data_file)
        
        # Crear metadatos de la versión
        version_metadata = {
            "version": self.current_version,
            "name": version_name or f"incremental_v{self.current_version}",
            "samples_count": len(new_records),
            "created_at": datetime.now().isoformat(),
            "data_file": str(new_data_file),
            "targets_distribution": self._analyze_targets_distribution(new_records)
        }
        
        # Actualizar metadatos globales
        self.dataset_metadata["versions"][str(self.current_version)] = version_metadata
        self.dataset_metadata["current_version"] = self.current_version
        self.dataset_metadata["total_samples"] += len(new_records)
        
        # Guardar metadatos
        self._save_dataset_metadata()
        
        logger.info(f"Nueva versión {self.current_version} creada con {len(new_records)} muestras")
        return self.current_version
    
    def _analyze_targets_distribution(self, records: List[Dict]) -> Dict[str, Dict]:
        """Analiza la distribución de targets en los nuevos datos."""
        distribution = {}
        
        for target in TARGETS:
            values = [record.get(target) for record in records if record.get(target) is not None]
            if values:
                distribution[target] = {
                    "count": len(values),
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
        
        return distribution
    
    def get_combined_dataset(self, 
                           include_versions: Optional[List[int]] = None,
                           max_samples_per_version: Optional[int] = None) -> Tuple[List[Dict], Dict]:
        """
        Obtiene un dataset combinado de múltiples versiones.
        
        Args:
            include_versions: Versiones a incluir (None = todas)
            max_samples_per_version: Máximo de muestras por versión
            
        Returns:
            Tuple con (registros combinados, metadatos)
        """
        if include_versions is None:
            include_versions = list(self.dataset_metadata["versions"].keys())
        
        combined_records = []
        version_info = {}
        
        for version_str in include_versions:
            version_num = int(version_str)
            version_dir = self.datasets_dir / f"v{version_num}"
            
            if not version_dir.exists():
                logger.warning(f"Directorio de versión {version_num} no encontrado")
                continue
            
            # Cargar datos de la versión
            new_data_file = version_dir / "new_data.json"
            if new_data_file.exists():
                version_records = load_json(new_data_file)
                
                # Limitar muestras si se especifica
                if max_samples_per_version and len(version_records) > max_samples_per_version:
                    # Muestreo estratificado por target
                    version_records = self._stratified_sampling(version_records, max_samples_per_version)
                
                combined_records.extend(version_records)
                version_info[version_str] = {
                    "samples": len(version_records),
                    "metadata": self.dataset_metadata["versions"][version_str]
                }
        
        logger.info(f"Dataset combinado creado con {len(combined_records)} muestras de {len(include_versions)} versiones")
        
        return combined_records, version_info
    
    def _stratified_sampling(self, records: List[Dict], max_samples: int) -> List[Dict]:
        """Muestreo estratificado para mantener distribución de targets."""
        if len(records) <= max_samples:
            return records
        
        # Agrupar por rangos de valores para cada target
        sampled_records = []
        samples_per_group = max_samples // len(TARGETS)
        
        for target in TARGETS:
            target_values = [(i, record[target]) for i, record in enumerate(records) 
                           if record.get(target) is not None]
            
            if not target_values:
                continue
            
            # Ordenar por valor del target
            target_values.sort(key=lambda x: x[1])
            
            # Muestreo sistemático
            step = len(target_values) // samples_per_group
            selected_indices = [target_values[i * step][0] for i in range(samples_per_group)]
            
            sampled_records.extend([records[i] for i in selected_indices])
        
        # Si no tenemos suficientes muestras, añadir aleatoriamente
        if len(sampled_records) < max_samples:
            sampled_indices = set()
            for i, record in enumerate(records):
                if record in sampled_records:
                    sampled_indices.add(i)
            remaining_indices = set(range(len(records))) - sampled_indices
            additional_needed = max_samples - len(sampled_records)
            # Use fixed seed for reproducibility in stratified sampling
            rng = np.random.default_rng(seed=42)
            additional_indices = rng.choice(list(remaining_indices), 
                                          min(additional_needed, len(remaining_indices)), 
                                          replace=False)
            sampled_records.extend([records[i] for i in additional_indices])
        
        return sampled_records[:max_samples]
    
    def get_version_info(self, version: int) -> Optional[Dict]:
        """Obtiene información de una versión específica."""
        return self.dataset_metadata["versions"].get(str(version))
    
    def list_versions(self) -> List[Dict]:
        """Lista todas las versiones disponibles."""
        versions = []
        for version_str, metadata in self.dataset_metadata["versions"].items():
            versions.append({
                "version": int(version_str),
                "name": metadata["name"],
                "samples": metadata["samples_count"],
                "created_at": metadata["created_at"]
            })
        return sorted(versions, key=lambda x: x["version"])


class IncrementalLearningStrategy:
    """
    Estrategias de aprendizaje incremental para evitar catastrophic forgetting.
    """
    
    def __init__(self, strategy_type: str = "elastic_weight_consolidation"):
        """
        Inicializa la estrategia de aprendizaje incremental.
        
        Args:
            strategy_type: Tipo de estrategia ('ewc', 'l2', 'replay', 'mixed')
        """
        self.strategy_type = strategy_type
        self.fisher_information = {}
        self.importance_weights = {}
        self.replay_buffer = []
        
        logger.info(f"Estrategia de aprendizaje incremental: {strategy_type}")
    
    def compute_fisher_information(self, model: nn.Module, dataloader: DataLoader, device: torch.device):
        """
        Computa la información de Fisher para Elastic Weight Consolidation (EWC).
        
        Args:
            model: Modelo a analizar
            dataloader: DataLoader con datos de la tarea anterior
            device: Dispositivo para computación
        """
        model.eval()
        fisher_info = {}
        
        # Inicializar gradientes de Fisher
        for name, param in model.named_parameters():
            fisher_info[name] = torch.zeros_like(param)
        
        criterion = nn.MSELoss()
        
        for batch_idx, (images, targets) in enumerate(dataloader):
            images = images.to(device)
            targets = targets.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, targets)
            
            # Computar gradientes
            model.zero_grad()
            loss.backward()
            
            # Acumular información de Fisher
            for name, param in model.named_parameters():
                if param.grad is not None:
                    fisher_info[name] += param.grad.data ** 2
        
        # Normalizar por número de muestras
        num_samples = len(dataloader.dataset)
        for name in fisher_info:
            fisher_info[name] /= num_samples
        
        self.fisher_information = fisher_info
        logger.info("Información de Fisher computada")
    
    def elastic_weight_consolidation_loss(self, model: nn.Module, current_loss: torch.Tensor, 
                                        lambda_ewc: float = 1000.0) -> torch.Tensor:
        """
        Computa la pérdida EWC para evitar catastrophic forgetting.
        
        Args:
            model: Modelo actual
            current_loss: Pérdida de la tarea actual
            lambda_ewc: Peso del término EWC
            
        Returns:
            Pérdida total con término EWC
        """
        if not self.fisher_information:
            return current_loss
        
        ewc_loss = current_loss
        
        for name, param in model.named_parameters():
            if name in self.fisher_information:
                fisher_info = self.fisher_information[name]
                # Asumir que los parámetros anteriores están en self.importance_weights
                if name in self.importance_weights:
                    prev_params = self.importance_weights[name]
                    ewc_loss += lambda_ewc * torch.sum(fisher_info * (param - prev_params) ** 2)
        
        return ewc_loss
    
    def l2_regularization_loss(self, model: nn.Module, current_loss: torch.Tensor,
                              lambda_l2: float = 0.01) -> torch.Tensor:
        """
        Pérdida de regularización L2 para mantener parámetros cerca de los anteriores.
        
        Args:
            model: Modelo actual
            current_loss: Pérdida de la tarea actual
            lambda_l2: Peso de la regularización L2
            
        Returns:
            Pérdida total con regularización L2
        """
        l2_loss = current_loss
        
        for name, param in model.named_parameters():
            if name in self.importance_weights:
                prev_params = self.importance_weights[name]
                l2_loss += lambda_l2 * torch.sum((param - prev_params) ** 2)
        
        return l2_loss
    
    def update_importance_weights(self, model: nn.Module):
        """Actualiza los pesos importantes con los parámetros actuales del modelo."""
        self.importance_weights = {}
        for name, param in model.named_parameters():
            self.importance_weights[name] = param.data.clone()
    
    def add_to_replay_buffer(self, samples: List[Dict], max_buffer_size: int = 1000):
        """
        Añade muestras al buffer de replay.
        
        Args:
            samples: Muestras a añadir
            max_buffer_size: Tamaño máximo del buffer
        """
        self.replay_buffer.extend(samples)
        
        # Mantener tamaño del buffer
        if len(self.replay_buffer) > max_buffer_size:
            # Eliminar muestras más antiguas
            self.replay_buffer = self.replay_buffer[-max_buffer_size:]
        
        logger.info(f"Buffer de replay actualizado: {len(self.replay_buffer)} muestras")
    
    def get_replay_samples(self, num_samples: int) -> List[Dict]:
        """Obtiene muestras aleatorias del buffer de replay."""
        if not self.replay_buffer:
            return []
        
        num_samples = min(num_samples, len(self.replay_buffer))
        # Use fixed seed for reproducibility in replay buffer sampling
        rng = np.random.default_rng(seed=42)
        return rng.choice(self.replay_buffer, num_samples, replace=False).tolist()


class IncrementalModelManager:
    """
    Gestor de versiones de modelos para entrenamiento incremental.
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Inicializa el gestor de modelos incrementales.
        
        Args:
            models_dir: Directorio para modelos incrementales
        """
        self.models_dir = models_dir or Path("backend/ml/models/incremental")
        ensure_dir_exists(self.models_dir)
        
        self.versions_dir = self.models_dir / "versions"
        self.checkpoints_dir = self.models_dir / "checkpoints"
        ensure_dir_exists(self.versions_dir)
        ensure_dir_exists(self.checkpoints_dir)
        
        self.model_metadata = self._load_model_metadata()
        self.current_version = self._get_latest_model_version()
        
        logger.info(f"Gestor de modelos incrementales inicializado. Versión actual: {self.current_version}")
    
    def _load_model_metadata(self) -> Dict:
        """Carga metadatos de modelos."""
        metadata_file = self.models_dir / "model_metadata.json"
        if metadata_file.exists():
            return load_json(metadata_file)
        return {
            "versions": {},
            "current_version": 0,
            "best_performance": {},
            "last_updated": None
        }
    
    def _save_model_metadata(self):
        """Guarda metadatos de modelos."""
        metadata_file = self.models_dir / "model_metadata.json"
        self.model_metadata["last_updated"] = datetime.now().isoformat()
        save_json(self.model_metadata, metadata_file)
    
    def _get_latest_model_version(self) -> int:
        """Obtiene la última versión de modelo."""
        if not self.versions_dir.exists():
            return 0
        
        versions = []
        for item in self.versions_dir.iterdir():
            if item.is_dir() and item.name.startswith("v"):
                try:
                    version = int(item.name[1:])
                    versions.append(version)
                except ValueError:
                    continue
        
        return max(versions) if versions else 0
    
    def save_model_version(self, model: nn.Module, version_info: Dict, 
                          performance_metrics: Dict) -> int:
        """
        Guarda una nueva versión del modelo.
        
        Args:
            model: Modelo a guardar
            version_info: Información de la versión
            performance_metrics: Métricas de rendimiento
            
        Returns:
            Número de versión guardada
        """
        self.current_version += 1
        version_dir = self.versions_dir / f"v{self.current_version}"
        ensure_dir_exists(version_dir)
        
        # Guardar modelo
        model_path = version_dir / "model.pt"
        torch.save({
            'model_state_dict': model.state_dict(),
            'model_info': version_info,
            'performance_metrics': performance_metrics,
            'timestamp': datetime.now().isoformat()
        }, model_path)
        
        # Guardar metadatos de la versión
        version_metadata = {
            "version": self.current_version,
            "model_path": str(model_path),
            "version_info": version_info,
            "performance_metrics": performance_metrics,
            "created_at": datetime.now().isoformat()
        }
        
        # Actualizar metadatos globales
        self.model_metadata["versions"][str(self.current_version)] = version_metadata
        self.model_metadata["current_version"] = self.current_version
        
        # Actualizar mejor rendimiento
        for target, metrics in performance_metrics.items():
            if target not in self.model_metadata["best_performance"]:
                self.model_metadata["best_performance"][target] = metrics
            else:
                # Comparar por R² score
                if metrics.get("r2", 0) > self.model_metadata["best_performance"][target].get("r2", 0):
                    self.model_metadata["best_performance"][target] = metrics
        
        self._save_model_metadata()
        
        logger.info(f"Modelo versión {self.current_version} guardado exitosamente")
        return self.current_version
    
    def load_model_version(self, version: int, model_class: nn.Module, 
                          device: torch.device) -> Tuple[nn.Module, Dict]:
        """
        Carga una versión específica del modelo.
        
        Security note: This function loads checkpoints created by this manager.
        Checkpoints should only be loaded from trusted sources (same training system).
        The checkpoint structure is validated after loading to detect tampering.
        
        SECURITY: Uses weights_only=True to prevent arbitrary code execution (S6985).
        This ensures only model weights and state_dicts are loaded, not arbitrary Python objects.
        
        Args:
            version: Número de versión
            model_class: Clase del modelo
            device: Dispositivo para cargar
            
        Returns:
            Tuple con (modelo cargado, metadatos)
        """
        version_dir = self.versions_dir / f"v{version}"
        if not version_dir.exists():
            raise FileNotFoundError(f"Versión {version} no encontrada")
        
        model_path = version_dir / "model.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {model_path}")
        
        # Security: Load checkpoint and validate structure
        # Checkpoints are created by this same manager, so they come from a trusted source
        # We validate the structure to ensure it matches our expected format
        try:
            # SECURITY: Use weights_only=True to prevent arbitrary code execution (S6985)
            # This is the safest way to load PyTorch checkpoints (available in PyTorch 2.1+)
            # Checkpoints are created by our own save_model_version method which only saves
            # state_dicts (dictionaries of tensors) and metadata, not arbitrary Python objects
            try:
                # Try to load with weights_only=True (safest method, PyTorch 2.1+)
                # SECURITY: weights_only=True prevents arbitrary code execution (S6985)
                checkpoint = torch.load(model_path, map_location=device, weights_only=True)
            except TypeError as exc:
                raise RuntimeError(
                    "La versión instalada de PyTorch no soporta weights_only=True. "
                    "Actualiza al menos a PyTorch 2.1 para cargar checkpoints de forma segura "
                    f"(archivo: {model_path})."
                ) from exc
            
            # Validate checkpoint structure to ensure it's a valid checkpoint from our manager
            # This helps detect if a checkpoint was tampered with
            required_keys = ['model_state_dict', 'model_info', 'performance_metrics', 'timestamp']
            if not all(key in checkpoint for key in required_keys):
                raise ValueError(f"Invalid checkpoint structure. Missing required keys: {required_keys}")
            
            # Validate that model_state_dict is a dictionary with string keys
            if not isinstance(checkpoint['model_state_dict'], dict):
                raise ValueError("Invalid checkpoint: model_state_dict is not a dictionary")
            
            # State dicts should have string keys (layer names)
            if checkpoint['model_state_dict'] and not all(isinstance(k, str) for k in checkpoint['model_state_dict'].keys()):
                raise ValueError("Invalid checkpoint: model_state_dict has non-string keys")
            
            # Validate that values in state_dict are tensors (not arbitrary objects)
            for key, value in checkpoint['model_state_dict'].items():
                if not isinstance(value, torch.Tensor):
                    raise ValueError(f"Invalid checkpoint: model_state_dict[{key}] is not a tensor")
            
            # Validate that model_info and performance_metrics are dictionaries
            if not isinstance(checkpoint['model_info'], dict):
                raise ValueError("Invalid checkpoint: model_info is not a dictionary")
            
            if not isinstance(checkpoint['performance_metrics'], dict):
                raise ValueError("Invalid checkpoint: performance_metrics is not a dictionary")
            
            # Validate timestamp is a string
            if not isinstance(checkpoint['timestamp'], str):
                raise ValueError("Invalid checkpoint: timestamp is not a string")
            
            # Crear modelo y cargar pesos
            model = model_class
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(device)
            
            metadata = checkpoint['model_info']
            performance_metrics = checkpoint['performance_metrics']
            
            logger.info(f"Modelo versión {version} cargado exitosamente")
            return model, {
                "metadata": metadata,
                "performance_metrics": performance_metrics,
                "timestamp": checkpoint['timestamp']
            }
        except Exception as e:
            logger.error(f"Error loading checkpoint from {model_path}: {e}")
            raise
    
    def get_best_model(self, target: str, model_class: nn.Module, 
                      device: torch.device) -> Tuple[nn.Module, Dict]:
        """
        Obtiene el mejor modelo para un target específico.
        
        Args:
            target: Target específico
            model_class: Clase del modelo
            device: Dispositivo para cargar
            
        Returns:
            Tuple con (mejor modelo, metadatos)
        """
        best_version = None
        best_r2 = -float('inf')
        
        for version_str, metadata in self.model_metadata["versions"].items():
            performance = metadata["performance_metrics"].get(target, {})
            r2 = performance.get("r2", -float('inf'))
            
            if r2 > best_r2:
                best_r2 = r2
                best_version = int(version_str)
        
        if best_version is None:
            raise ValueError(f"No se encontró modelo para target {target}")
        
        return self.load_model_version(best_version, model_class, device)
    
    def list_model_versions(self) -> List[Dict]:
        """Lista todas las versiones de modelos disponibles."""
        versions = []
        for version_str, metadata in self.model_metadata["versions"].items():
            versions.append({
                "version": int(version_str),
                "created_at": metadata["created_at"],
                "performance_metrics": metadata["performance_metrics"]
            })
        return sorted(versions, key=lambda x: x["version"])


class IncrementalTrainer:
    """
    Entrenador principal para aprendizaje incremental.
    
    Combina todas las estrategias y componentes para realizar
    entrenamiento incremental efectivo.
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa el entrenador incremental.
        
        Args:
            config: Configuración del entrenamiento incremental
        """
        self.config = config
        self.device = get_device()
        
        # Inicializar componentes
        self.data_manager = IncrementalDataManager()
        self.model_manager = IncrementalModelManager()
        self.learning_strategy = IncrementalLearningStrategy(
            strategy_type=config.get('strategy_type', 'elastic_weight_consolidation')
        )
        
        # Configuración de entrenamiento
        self.learning_rate = config.get('learning_rate', 1e-4)
        self.epochs = config.get('epochs', 20)
        self.batch_size = config.get('batch_size', 16)
        self.ewc_lambda = config.get('ewc_lambda', 1000.0)
        self.replay_ratio = config.get('replay_ratio', 0.3)
        
        logger.info("Entrenador incremental inicializado")
    
    def train_incremental(self, new_data: List[Dict], 
                         base_model_version: Optional[int] = None,
                         target: str = "alto") -> Dict:
        """
        Realiza entrenamiento incremental con nuevos datos.
        
        Args:
            new_data: Nuevos datos para entrenamiento
            base_model_version: Versión del modelo base (None = última versión)
            target: Target específico a entrenar
            
        Returns:
            Diccionario con resultados del entrenamiento
        """
        logger.info(f"Iniciando entrenamiento incremental para {target}")
        
        # 1. Añadir nuevos datos al sistema
        new_version = self.data_manager.add_new_data(new_data, f"incremental_{target}")
        logger.info(f"Nuevos datos añadidos como versión {new_version}")
        
        # 2. Cargar modelo base
        if base_model_version is None:
            base_model_version = self.model_manager.current_version
        
        if base_model_version > 0:
            try:
                base_model, base_metadata = self.model_manager.load_model_version(
                    base_model_version, 
                    create_model(num_outputs=1),
                    self.device
                )
                logger.info(f"Modelo base versión {base_model_version} cargado")
            except FileNotFoundError:
                logger.warning("Modelo base no encontrado, entrenando desde cero")
                base_model = create_model(num_outputs=1).to(self.device)
                base_metadata = None
        else:
            base_model = create_model(num_outputs=1).to(self.device)
            base_metadata = None
        
        # 3. Preparar datos de entrenamiento
        train_data, val_data = self._prepare_incremental_data(new_data, target)
        
        # 4. Configurar estrategia de aprendizaje
        if base_metadata and self.learning_strategy.strategy_type == "elastic_weight_consolidation":
            # Computar información de Fisher si tenemos datos anteriores
            self._compute_fisher_information(base_model, target)
        
        # 5. Entrenar modelo incremental
        trained_model, training_history = self._train_incremental_model(
            base_model, train_data, val_data
        )
        
        # 6. Evaluar rendimiento
        performance_metrics = self._evaluate_incremental_model(trained_model, val_data, target)
        
        # 7. Guardar nueva versión
        version_info = {
            "target": target,
            "base_version": base_model_version,
            "data_version": new_version,
            "strategy": self.learning_strategy.strategy_type,
            "config": self.config
        }
        
        model_version = self.model_manager.save_model_version(
            trained_model, version_info, performance_metrics
        )
        
        # 8. Actualizar estrategia de aprendizaje
        self.learning_strategy.update_importance_weights(trained_model)
        
        # Añadir muestras al buffer de replay
        if self.learning_strategy.strategy_type in ["replay", "mixed"]:
            self.learning_strategy.add_to_replay_buffer(new_data)
        
        logger.info(f"Entrenamiento incremental completado. Nueva versión: {model_version}")
        
        return {
            "model_version": model_version,
            "performance_metrics": performance_metrics,
            "training_history": training_history,
            "data_version": new_version,
            "strategy_used": self.learning_strategy.strategy_type
        }
    
    def _prepare_incremental_data(self, new_data: List[Dict], target: str) -> Tuple[DataLoader, DataLoader]:
        """Prepara datos para entrenamiento incremental."""
        # Combinar nuevos datos con datos de replay si es necesario
        if self.learning_strategy.strategy_type in ["replay", "mixed"]:
            replay_samples = self.learning_strategy.get_replay_samples(
                int(len(new_data) * self.replay_ratio)
            )
            combined_data = new_data + replay_samples
        else:
            combined_data = new_data
        
        # Crear dataset y data loaders
        from ..pipeline.train_all import CacaoDataset
        
        # Preparar datos para el dataset
        image_paths = []
        targets_dict = {target: []}
        
        for record in combined_data:
            image_path = Path(record['image_path'])
            if image_path.exists():
                image_paths.append(image_path)
                targets_dict[target].append(record[target])
        
        # Crear dataset
        dataset = CacaoDataset(image_paths, targets_dict, self.config.get('img_size', 224))
        
        # Split train/validation
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        # Crear data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.config.get('num_workers', 2)
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.config.get('num_workers', 2)
        )
        
        return train_loader, val_loader
    
    def _compute_fisher_information(self, model: nn.Module, target: str):
        """Computa información de Fisher para EWC."""
        # Obtener datos de versiones anteriores para computar Fisher
        try:
            previous_data, _ = self.data_manager.get_combined_dataset(
                include_versions=[str(self.data_manager.current_version - 1)],
                max_samples_per_version=100  # Limitar para eficiencia
            )
            
            if previous_data:
                train_loader, _ = self._prepare_incremental_data(previous_data, target)
                self.learning_strategy.compute_fisher_information(model, train_loader, self.device)
        except Exception as e:
            logger.warning(f"No se pudo computar información de Fisher: {e}")
    
    def _train_incremental_model(self, model: nn.Module, train_loader: DataLoader, 
                                val_loader: DataLoader) -> Tuple[nn.Module, Dict]:
        """Entrena el modelo con estrategias incrementales."""
        model.train()
        
        # Configurar optimizador
        optimizer = optim.AdamW(
            model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.config.get('weight_decay', 1e-4)
        )
        
        # Configurar scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=self.epochs,
            eta_min=self.config.get('min_lr', 1e-6)
        )
        
        criterion = nn.MSELoss()
        
        # Historial de entrenamiento
        history = {
            'train_loss': [],
            'val_loss': [],
            'val_mae': [],
            'val_rmse': [],
            'val_r2': [],
            'learning_rate': []
        }
        
        best_val_loss = float('inf')
        best_model_state = None
        
        for epoch in range(self.epochs):
            # Entrenamiento
            model.train()
            train_loss = 0.0
            
            for batch_idx, (images, targets) in enumerate(train_loader):
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                optimizer.zero_grad()
                
                # Forward pass
                outputs = model(images)
                loss = criterion(outputs, targets)
                
                # Aplicar estrategia incremental
                if self.learning_strategy.strategy_type == "elastic_weight_consolidation":
                    loss = self.learning_strategy.elastic_weight_consolidation_loss(
                        model, loss, self.ewc_lambda
                    )
                elif self.learning_strategy.strategy_type == "l2":
                    loss = self.learning_strategy.l2_regularization_loss(
                        model, loss, self.config.get('l2_lambda', 0.01)
                    )
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validación
            val_loss, val_mae, val_rmse, val_r2 = self._validate_epoch(model, val_loader, criterion)
            
            # Actualizar scheduler
            scheduler.step()
            current_lr = scheduler.get_last_lr()[0]
            
            # Guardar mejor modelo
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = model.state_dict().copy()
            
            # Guardar historial
            history['train_loss'].append(train_loss / len(train_loader))
            history['val_loss'].append(val_loss)
            history['val_mae'].append(val_mae)
            history['val_rmse'].append(val_rmse)
            history['val_r2'].append(val_r2)
            history['learning_rate'].append(current_lr)
            
            logger.info(
                f"Epoch {epoch+1}/{self.epochs} - "
                f"Train Loss: {train_loss/len(train_loader):.4f}, "
                f"Val Loss: {val_loss:.4f}, "
                f"Val MAE: {val_mae:.4f}, "
                f"Val R²: {val_r2:.4f}"
            )
        
        # Cargar mejor modelo
        if best_model_state is not None:
            model.load_state_dict(best_model_state)
        
        return model, history
    
    def _validate_epoch(self, model: nn.Module, val_loader: DataLoader, 
                       criterion: nn.Module) -> Tuple[float, float, float, float]:
        """Valida el modelo en una época."""
        model.eval()
        val_loss = 0.0
        predictions = []
        targets = []
        
        with torch.no_grad():
            for images, target_values in val_loader:
                images = images.to(self.device)
                target_values = target_values.to(self.device)
                
                outputs = model(images)
                loss = criterion(outputs, target_values)
                
                val_loss += loss.item()
                predictions.extend(outputs.cpu().numpy())
                targets.extend(target_values.cpu().numpy())
        
        # Calcular métricas
        predictions = np.array(predictions).flatten()
        targets = np.array(targets).flatten()
        
        mae = mean_absolute_error(targets, predictions)
        rmse = np.sqrt(mean_squared_error(targets, predictions))
        r2 = r2_score(targets, predictions)
        
        return val_loss / len(val_loader), mae, rmse, r2
    
    def _evaluate_incremental_model(self, model: nn.Module, val_loader: DataLoader, 
                                   target: str) -> Dict:
        """Evalúa el modelo incremental."""
        model.eval()
        predictions = []
        targets = []
        
        with torch.no_grad():
            for images, target_values in val_loader:
                images = images.to(self.device)
                target_values = target_values.to(self.device)
                
                outputs = model(images)
                predictions.extend(outputs.cpu().numpy())
                targets.extend(target_values.cpu().numpy())
        
        predictions = np.array(predictions).flatten()
        targets = np.array(targets).flatten()
        
        metrics = {
            "mae": float(mean_absolute_error(targets, predictions)),
            "rmse": float(np.sqrt(mean_squared_error(targets, predictions))),
            "r2": float(r2_score(targets, predictions)),
            "samples_evaluated": len(targets)
        }
        
        return {target: metrics}


def run_incremental_training(new_data: List[Dict], 
                           config: Optional[Dict] = None,
                           target: str = "alto") -> Dict:
    """
    Función principal para ejecutar entrenamiento incremental.
    
    Args:
        new_data: Nuevos datos para entrenamiento
        config: Configuración del entrenamiento
        target: Target específico a entrenar
        
    Returns:
        Resultados del entrenamiento incremental
    """
    if config is None:
        config = {
            'strategy_type': 'elastic_weight_consolidation',
            'learning_rate': 1e-4,
            'epochs': 20,
            'batch_size': 16,
            'ewc_lambda': 1000.0,
            'replay_ratio': 0.3,
            'img_size': 224,
            'num_workers': 2,
            'weight_decay': 1e-4,
            'min_lr': 1e-6
        }
    
    trainer = IncrementalTrainer(config)
    return trainer.train_incremental(new_data, target=target)


