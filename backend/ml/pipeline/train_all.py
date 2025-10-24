"""
Pipeline completo de entrenamiento para modelos de regresión de cacao.
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import time
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import QuantileTransformer

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
django.setup()

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.regression.models import create_model, TARGETS, TARGET_NAMES
from ml.regression.scalers import create_scalers_from_data, save_scalers
from ml.regression.train import train_single_model, train_multi_head_model, get_device
from ml.regression.evaluate import RegressionEvaluator
from ml.utils.paths import get_regressors_artifacts_dir, get_artifacts_dir
from ml.utils.io import save_json
from ml.utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.pipeline")


class CacaoDataset:
    """Dataset personalizado para entrenamiento de modelos de cacao."""
    
    def __init__(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        transform=None
    ):
        """
        Inicializa el dataset.
        
        Args:
            image_paths: Lista de rutas a imágenes
            targets: Diccionario con targets normalizados
            transform: Transformaciones a aplicar
        """
        self.image_paths = image_paths
        self.targets = targets
        self.transform = transform
        
        # Verificar que todas las listas tienen la misma longitud
        lengths = [len(image_paths)] + [len(targets[target]) for target in targets.keys()]
        if len(set(lengths)) > 1:
            raise ValueError(f"Longitudes inconsistentes: {lengths}")
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Cargar imagen
        from PIL import Image
        import torchvision.transforms as transforms
        
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        
        # Aplicar transformaciones por defecto si no se especifican
        if self.transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        image = self.transform(image)
        
        # Obtener targets
        available_targets = list(self.targets.keys())
        if len(available_targets) == 1:
            # Modelo individual
            target_name = available_targets[0]
            target = self.targets[target_name][idx]
            return image, torch.tensor(target, dtype=torch.float32)
        else:
            # Modelo multi-head
            targets_dict = {}
            for target_name in available_targets:
                targets_dict[target_name] = torch.tensor(
                    self.targets[target_name][idx], dtype=torch.float32
                )
            return image, targets_dict


class CacaoTrainingPipeline:
    """Pipeline completo de entrenamiento."""
    
    def __init__(self, config: Dict):
        """
        Inicializa el pipeline.
        
        Args:
            config: Configuración del entrenamiento
        """
        self.config = config
        self.device = get_device()
        self.scalers = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        logger.info(f"Pipeline inicializado con configuración: {config}")
    
    def load_data(self) -> Tuple[List[Path], Dict[str, np.ndarray]]:
        """
        Carga y prepara los datos.
        
        Returns:
            Tuple con (rutas de imágenes, targets)
        """
        logger.info("Cargando datos...")
        
        # Cargar registros válidos
        loader = CacaoDatasetLoader()
        valid_records = loader.get_valid_records()
        
        if not valid_records:
            raise ValueError("No se encontraron registros válidos")
        
        logger.info(f"Encontrados {len(valid_records)} registros válidos")
        
        # Filtrar registros que tienen crops
        crop_records = []
        missing_crop_records = []
        
        for record in valid_records:
            crop_path = record['crop_image_path']
            if crop_path and crop_path.exists():
                crop_records.append(record)
            else:
                missing_crop_records.append(record)
        
        logger.info(f"Registros con crops disponibles: {len(crop_records)}")
        logger.info(f"Registros sin crops: {len(missing_crop_records)}")
        
        # Solo generar crops para los que faltan si hay algunos faltantes
        if missing_crop_records:
            logger.info(f"Generando crops para {len(missing_crop_records)} imágenes faltantes...")
            new_crop_records = self._generate_crops_for_missing(missing_crop_records)
            crop_records.extend(new_crop_records)
            
            logger.info(f"Total de registros con crops después de generación: {len(crop_records)}")
            
            if len(crop_records) < 10:
                raise ValueError(f"Muy pocos registros con crops después de generación: {len(crop_records)}")
        else:
            logger.info("✅ Todos los crops ya existen. No se necesita generación.")
        
        # Extraer rutas de imágenes y targets
        image_paths = [record['crop_image_path'] for record in crop_records]
        targets = {target: np.array([record[target] for record in crop_records]) for target in TARGETS}
        
        return image_paths, targets
    
    def create_stratified_split(
        self,
        image_paths: List[Path],
        targets: Dict[str, np.ndarray],
        test_size: float = 0.2,
        val_size: float = 0.1
    ) -> Tuple[List[Path], List[Path], List[Path], Dict, Dict, Dict]:
        """
        Crea split estratificado basado en cuantiles de peso y dimensiones.
        
        Args:
            image_paths: Rutas de imágenes
            targets: Targets
            test_size: Proporción para test
            val_size: Proporción para validación
            
        Returns:
            Tuples con splits de imágenes y targets
        """
        logger.info("Creando split estratificado...")
        
        n_samples = len(image_paths)
        
        # Crear estratos basados en cuantiles de peso
        peso_values = targets['peso']
        n_quantiles = min(5, n_samples // 10)  # Ajustar número de cuantiles
        
        if n_quantiles < 2:
            logger.warning("Muy pocos muestras para estratificación, usando split aleatorio")
            # Split aleatorio simple
            train_idx, test_idx = train_test_split(
                range(n_samples), test_size=test_size, random_state=42
            )
            train_idx, val_idx = train_test_split(
                train_idx, test_size=val_size/(1-test_size), random_state=42
            )
        else:
            try:
                # Estratificación por cuantiles de peso
                quantile_transformer = QuantileTransformer(n_quantiles=n_quantiles, random_state=42)
                peso_quantiles = quantile_transformer.fit_transform(peso_values.reshape(-1, 1)).flatten()
                
                # Convertir a bins para estratificación
                strata = pd.cut(peso_quantiles, bins=n_quantiles, labels=False)
                
                # Verificar que todos los estratos tengan al menos 2 muestras
                strata_counts = pd.Series(strata).value_counts()
                min_strata_count = strata_counts.min()
                
                if min_strata_count < 2:
                    logger.warning(f"Algunos estratos tienen menos de 2 muestras (mínimo: {min_strata_count}). Usando split aleatorio.")
                    raise ValueError("Estratificación no viable")
                
                # Split estratificado
                train_idx, test_idx = train_test_split(
                    range(n_samples), test_size=test_size, random_state=42, stratify=strata
                )
                
                # Crear estratos para el conjunto de entrenamiento
                train_strata = strata[train_idx]
                train_strata_counts = pd.Series(train_strata).value_counts()
                
                # Verificar que los estratos del train también tengan al menos 2 muestras
                if train_strata_counts.min() < 2:
                    logger.warning("Estratificación no viable para validación. Usando split aleatorio para validación.")
                    train_idx, val_idx = train_test_split(
                        train_idx, test_size=val_size/(1-test_size), random_state=42
                    )
                else:
                    train_idx, val_idx = train_test_split(
                        train_idx, test_size=val_size/(1-test_size), random_state=42, stratify=train_strata
                    )
                    
            except (ValueError, Exception) as e:
                logger.warning(f"Error en estratificación: {e}. Usando split aleatorio.")
                # Fallback a split aleatorio
                train_idx, test_idx = train_test_split(
                    range(n_samples), test_size=test_size, random_state=42
                )
                train_idx, val_idx = train_test_split(
                    train_idx, test_size=val_size/(1-test_size), random_state=42
                )
        
        # Crear splits de imágenes
        train_images = [image_paths[i] for i in train_idx]
        val_images = [image_paths[i] for i in val_idx]
        test_images = [image_paths[i] for i in test_idx]
        
        # Crear splits de targets
        train_targets = {target: targets[target][train_idx] for target in TARGETS}
        val_targets = {target: targets[target][val_idx] for target in TARGETS}
        test_targets = {target: targets[target][test_idx] for target in TARGETS}
        
        logger.info(f"Split creado: Train={len(train_images)}, Val={len(val_images)}, Test={len(test_images)}")
        
        return train_images, val_images, test_images, train_targets, val_targets, test_targets
    
    def create_data_loaders(
        self,
        train_images: List[Path],
        val_images: List[Path],
        test_images: List[Path],
        train_targets: Dict[str, np.ndarray],
        val_targets: Dict[str, np.ndarray],
        test_targets: Dict[str, np.ndarray]
    ) -> None:
        """
        Crea los data loaders.
        """
        logger.info("Creando data loaders...")
        
        import torchvision.transforms as transforms
        
        # Transformaciones de entrenamiento con augmentaciones moderadas
        train_transform = transforms.Compose([
            transforms.Resize((self.config['img_size'], self.config['img_size'])),
            transforms.RandomRotation(degrees=5),  # Rotación leve ±5°
            transforms.ColorJitter(brightness=0.1, contrast=0.1),  # Ligero jitter
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Transformaciones de validación/test (sin augmentaciones)
        val_transform = transforms.Compose([
            transforms.Resize((self.config['img_size'], self.config['img_size'])),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Crear datasets
        train_dataset = CacaoDataset(train_images, train_targets, train_transform)
        val_dataset = CacaoDataset(val_images, val_targets, val_transform)
        test_dataset = CacaoDataset(test_images, test_targets, val_transform)
        
        # Crear data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config['batch_size'],
            shuffle=True,
            num_workers=self.config.get('num_workers', 2),
            pin_memory=True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config['batch_size'],
            shuffle=False,
            num_workers=self.config.get('num_workers', 2),
            pin_memory=True
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config['batch_size'],
            shuffle=False,
            num_workers=self.config.get('num_workers', 2),
            pin_memory=True
        )
        
        logger.info("Data loaders creados exitosamente")
    
    def prepare_scalers(self, train_targets: Dict[str, np.ndarray]) -> None:
        """
        Prepara y ajusta los escaladores.
        """
        logger.info("Preparando escaladores...")
        
        # Crear DataFrame para escaladores
        train_df = pd.DataFrame(train_targets)
        self.scalers = create_scalers_from_data(train_df, scaler_type="standard")
        
        logger.info("Escaladores preparados")
    
    def train_models(self, multi_head: bool = False) -> Dict[str, Union[Dict, List]]:
        """
        Entrena los modelos.
        
        Args:
            multi_head: Si entrenar modelo multi-head o individuales
            
        Returns:
            Historiales de entrenamiento
        """
        logger.info(f"Iniciando entrenamiento (multi_head={multi_head})...")
        
        if multi_head:
            return self._train_multi_head_model()
        else:
            return self._train_individual_models()
    
    def _train_individual_models(self) -> Dict[str, Dict]:
        """Entrena modelos individuales para cada target."""
        histories = {}
        
        for target in TARGETS:
            logger.info(f"Entrenando modelo para {target}...")
            
            # Crear modelo individual
            model = create_model(
                model_type=self.config['model_type'],
                num_outputs=1,
                pretrained=self.config.get('pretrained', True),
                dropout_rate=self.config.get('dropout_rate', 0.2),
                multi_head=False
            )
            
            # Crear targets individuales para este modelo
            train_targets_single = {target: self.train_loader.dataset.targets[target]}
            val_targets_single = {target: self.val_loader.dataset.targets[target]}
            
            # Crear data loaders individuales
            train_dataset_single = CacaoDataset(
                [self.train_loader.dataset.image_paths[i] for i in range(len(self.train_loader.dataset))],
                train_targets_single,
                self.train_loader.dataset.transform
            )
            val_dataset_single = CacaoDataset(
                [self.val_loader.dataset.image_paths[i] for i in range(len(self.val_loader.dataset))],
                val_targets_single,
                self.val_loader.dataset.transform
            )
            
            train_loader_single = DataLoader(
                train_dataset_single,
                batch_size=self.config['batch_size'],
                shuffle=True,
                num_workers=self.config.get('num_workers', 2),
                pin_memory=True
            )
            val_loader_single = DataLoader(
                val_dataset_single,
                batch_size=self.config['batch_size'],
                shuffle=False,
                num_workers=self.config.get('num_workers', 2),
                pin_memory=True
            )
            
            # Entrenar modelo
            history = train_single_model(
                model=model,
                train_loader=train_loader_single,
                val_loader=val_loader_single,
                scalers=self.scalers,
                target=target,
                config=self.config,
                device=self.device
            )
            
            histories[target] = history
        
        return histories
    
    def _train_multi_head_model(self) -> Dict[str, Union[Dict, List]]:
        """Entrena modelo multi-head."""
        logger.info("Entrenando modelo multi-head...")
        
        # Crear modelo multi-head
        model = create_model(
            model_type=self.config['model_type'],
            num_outputs=4,
            pretrained=self.config.get('pretrained', True),
            dropout_rate=self.config.get('dropout_rate', 0.2),
            multi_head=True
        )
        
        # Entrenar modelo
        history = train_multi_head_model(
            model=model,
            train_loader=self.train_loader,
            val_loader=self.val_loader,
            scalers=self.scalers,
            config=self.config,
            device=self.device
        )
        
        return {'multihead': history}
    
    def evaluate_models(self, multi_head: bool = False) -> Dict[str, Union[Dict, List]]:
        """
        Evalúa los modelos entrenados.
        
        Args:
            multi_head: Si evaluar modelo multi-head o individuales
            
        Returns:
            Resultados de evaluación
        """
        logger.info(f"Evaluando modelos (multi_head={multi_head})...")
        
        if multi_head:
            return self._evaluate_multi_head_model()
        else:
            return self._evaluate_individual_models()
    
    def _evaluate_individual_models(self) -> Dict[str, Dict]:
        """Evalúa modelos individuales."""
        results = {}
        
        for target in TARGETS:
            logger.info(f"Evaluando modelo para {target}...")
            
            # Cargar modelo
            model_path = get_regressors_artifacts_dir() / f"{target}.pt"
            if not model_path.exists():
                logger.warning(f"Modelo no encontrado para {target}: {model_path}")
                continue
            
            # Crear modelo y cargar pesos
            model = create_model(
                model_type=self.config['model_type'],
                num_outputs=1,
                pretrained=False,
                dropout_rate=self.config.get('dropout_rate', 0.2),
                multi_head=False
            )
            
            checkpoint = torch.load(model_path, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # Crear evaluador
            evaluator = RegressionEvaluator(
                model=model,
                test_loader=self.test_loader,
                scalers=self.scalers,
                device=self.device
            )
            
            # Evaluar
            target_results = evaluator.evaluate_single_model(target)
            results[target] = target_results
        
        return results
    
    def _evaluate_multi_head_model(self) -> Dict[str, Dict]:
        """Evalúa modelo multi-head."""
        logger.info("Evaluando modelo multi-head...")
        
        # Cargar modelo
        model_path = get_regressors_artifacts_dir() / "multihead.pt"
        if not model_path.exists():
            logger.warning(f"Modelo multi-head no encontrado: {model_path}")
            return {}
        
        # Crear modelo y cargar pesos
        model = create_model(
            model_type=self.config['model_type'],
            num_outputs=4,
            pretrained=False,
            dropout_rate=self.config.get('dropout_rate', 0.2),
            multi_head=True
        )
        
        checkpoint = torch.load(model_path, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        
        # Crear evaluador
        evaluator = RegressionEvaluator(
            model=model,
            test_loader=self.test_loader,
            scalers=self.scalers,
            device=self.device
        )
        
        # Evaluar
        results = evaluator.evaluate_multi_head_model()
        
        return {'multihead': results}
    
    def save_scalers(self) -> None:
        """Guarda los escaladores."""
        if self.scalers is None:
            logger.warning("No hay escaladores para guardar")
            return
        
        save_scalers(self.scalers)
        logger.info("Escaladores guardados")
    
    def _verify_artifacts_saved(self) -> None:
        """Verifica que todos los artefactos se guardaron correctamente."""
        logger.info("Verificando que todos los artefactos se guardaron correctamente...")
        
        artifacts_dir = get_regressors_artifacts_dir()
        missing_files = []
        
        # Verificar modelos
        for target in TARGETS:
            model_path = artifacts_dir / f"{target}.pt"
            if not model_path.exists():
                missing_files.append(f"Modelo {target}: {model_path}")
            elif model_path.stat().st_size == 0:
                missing_files.append(f"Modelo {target} está vacío: {model_path}")
        
        # Verificar escaladores
        for target in TARGETS:
            scaler_path = artifacts_dir / f"{target}_scaler.pkl"
            if not scaler_path.exists():
                missing_files.append(f"Escalador {target}: {scaler_path}")
            elif scaler_path.stat().st_size == 0:
                missing_files.append(f"Escalador {target} está vacío: {scaler_path}")
        
        if missing_files:
            error_msg = f"❌ Archivos faltantes o vacíos: {missing_files}"
            logger.error(error_msg)
            raise IOError(error_msg)
        else:
            logger.info("✅ Todos los artefactos se guardaron correctamente")
            
            # Mostrar resumen de archivos guardados
            total_size = sum(
                (artifacts_dir / f"{target}.pt").stat().st_size + 
                (artifacts_dir / f"{target}_scaler.pkl").stat().st_size
                for target in TARGETS
            )
            logger.info(f"📊 Total de artefactos guardados: {len(TARGETS) * 2} archivos, {total_size / 1024 / 1024:.2f} MB")
    
    def generate_reports(self, evaluation_results: Dict, save_dir: Optional[Path] = None) -> None:
        """
        Genera reportes y gráficos.
        
        Args:
            evaluation_results: Resultados de evaluación
            save_dir: Directorio para guardar reportes
        """
        if save_dir is None:
            save_dir = get_artifacts_dir() / "reports"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar reporte JSON
        report_path = save_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_json(evaluation_results, report_path)
        
        logger.info(f"Reporte guardado en {report_path}")
    
    def run_pipeline(self, multi_head: bool = False) -> Dict[str, Union[Dict, List]]:
        """
        Ejecuta el pipeline completo.
        
        Args:
            multi_head: Si usar modelo multi-head o individuales
            
        Returns:
            Resultados completos del pipeline
        """
        logger.info("=== INICIANDO PIPELINE DE ENTRENAMIENTO ===")
        start_time = time.time()
        
        try:
            # 1. Cargar datos
            logger.info("Paso 1: Cargando datos...")
            image_paths, targets = self.load_data()
            
            if not image_paths or len(image_paths) < 10:
                raise ValueError(f"Dataset insuficiente: solo {len(image_paths)} muestras. Se necesitan al menos 10.")
            
            # 2. Crear splits
            logger.info("Paso 2: Creando splits de datos...")
            train_images, val_images, test_images, train_targets, val_targets, test_targets = self.create_stratified_split(
                image_paths, targets
            )
            
            logger.info(f"Splits creados - Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")
            
            # 3. Crear data loaders
            self.create_data_loaders(
                train_images, val_images, test_images,
                train_targets, val_targets, test_targets
            )
            
            # 4. Preparar escaladores
            self.prepare_scalers(train_targets)
            
            # 5. Entrenar modelos
            training_histories = self.train_models(multi_head)
            
            # 6. Guardar escaladores
            self.save_scalers()
            
            # 7. Verificar que todos los artefactos se guardaron correctamente
            self._verify_artifacts_saved()
            
            # 8. Evaluar modelos
            evaluation_results = self.evaluate_models(multi_head)
            
            # 9. Generar reportes
            self.generate_reports(evaluation_results)
            
            total_time = time.time() - start_time
            logger.info(f"=== PIPELINE COMPLETADO EN {total_time:.2f}s ===")
            
            return {
                'training_histories': training_histories,
                'evaluation_results': evaluation_results,
                'total_time': total_time,
                'config': self.config
            }
            
        except ValueError as e:
            logger.error(f"Error de validación en pipeline: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en pipeline: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _generate_crops_for_missing(self, missing_records: List[Dict]) -> List[Dict]:
        """
        Genera crops solo para los registros que no tienen crops.
        
        Args:
            missing_records: Lista de registros que no tienen crops
            
        Returns:
            Lista de registros con crops generados exitosamente
        """
        logger.info(f"🚀 Generando crops para {len(missing_records)} imágenes faltantes...")
        
        from pathlib import Path
        from PIL import Image
        import os
        
        # Crear directorio de crops si no existe
        crops_dir = Path("media/cacao_images/crops")
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        crop_records = []
        successful = 0
        failed = 0
        
        for i, record in enumerate(missing_records):
            try:
                image_id = record['id']
                image_path = Path(record['image_path'])
                crop_path = Path(record['crop_image_path'])
                
                # Verificar si la imagen original existe
                if not image_path.exists():
                    logger.warning(f"Imagen original no existe: {image_path}")
                    failed += 1
                    continue
                
                # Verificar si el crop ya existe (doble verificación)
                if crop_path.exists():
                    logger.debug(f"Crop ya existe (saltando): {crop_path}")
                    crop_records.append(record)
                    successful += 1
                    continue
                
                # Generar crop simple (redimensionar imagen original)
                img = Image.open(image_path)
                img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
                img_resized.save(crop_path, "PNG")
                
                logger.debug(f"Crop generado: {crop_path}")
                crop_records.append(record)
                successful += 1
                
                # Log de progreso cada 10 imágenes
                if (i + 1) % 10 == 0:
                    logger.info(f"Generados {i + 1}/{len(missing_records)} crops faltantes...")
                    
            except Exception as e:
                logger.error(f"Error generando crop para ID {record['id']}: {e}")
                failed += 1
        
        logger.info(f"✅ Generación de crops faltantes completada: {successful} exitosos, {failed} fallidos")
        return crop_records
    
    def _generate_crops_automatically(self, valid_records: List[Dict]) -> List[Dict]:
        """
        Genera crops automáticamente para los registros válidos (método legacy).
        
        Args:
            valid_records: Lista de registros válidos
            
        Returns:
            Lista de registros con crops generados
        """
        logger.info("🚀 Generando crops automáticamente (método legacy)...")
        
        from pathlib import Path
        from PIL import Image
        import os
        
        # Crear directorio de crops si no existe
        crops_dir = Path("media/cacao_images/crops")
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        crop_records = []
        successful = 0
        failed = 0
        
        for i, record in enumerate(valid_records):
            try:
                image_id = record['id']
                image_path = Path(record['image_path'])
                crop_path = Path(record['crop_image_path'])
                
                # Verificar si la imagen original existe
                if not image_path.exists():
                    logger.warning(f"Imagen original no existe: {image_path}")
                    failed += 1
                    continue
                
                # Verificar si el crop ya existe
                if crop_path.exists() and not self.config.get('overwrite', False):
                    logger.debug(f"Crop ya existe: {crop_path}")
                    crop_records.append(record)
                    successful += 1
                    continue
                
                # Generar crop simple (redimensionar imagen original)
                img = Image.open(image_path)
                img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
                img_resized.save(crop_path, "PNG")
                
                logger.debug(f"Crop generado: {crop_path}")
                crop_records.append(record)
                successful += 1
                
                # Log de progreso cada 50 imágenes
                if (i + 1) % 50 == 0:
                    logger.info(f"Generados {i + 1}/{len(valid_records)} crops...")
                    
            except Exception as e:
                logger.error(f"Error generando crop para ID {record['id']}: {e}")
                failed += 1
        
        logger.info(f"✅ Generación de crops completada: {successful} exitosos, {failed} fallidos")
        return crop_records


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Pipeline de entrenamiento para modelos de cacao')
    
    # Argumentos del modelo
    parser.add_argument('--multihead', type=str, default='false', choices=['true', 'false'],
                       help='Usar modelo multi-head (default: false)')
    parser.add_argument('--model-type', type=str, default='resnet18', choices=['resnet18', 'convnext_tiny'],
                       help='Tipo de modelo (default: resnet18)')
    
    # Argumentos de entrenamiento
    parser.add_argument('--epochs', type=int, default=50,
                       help='Número de épocas (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Tamaño de batch (default: 32)')
    parser.add_argument('--img-size', type=int, default=224,
                       help='Tamaño de imagen (default: 224)')
    parser.add_argument('--learning-rate', type=float, default=1e-4,
                       help='Learning rate (default: 1e-4)')
    
    # Argumentos adicionales
    parser.add_argument('--num-workers', type=int, default=2,
                       help='Número de workers para data loading (default: 2)')
    parser.add_argument('--early-stopping-patience', type=int, default=10,
                       help='Paciencia para early stopping (default: 10)')
    
    args = parser.parse_args()
    
    # Crear configuración
    config = {
        'multi_head': args.multihead.lower() == 'true',
        'model_type': args.model_type,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'img_size': args.img_size,
        'learning_rate': args.learning_rate,
        'num_workers': args.num_workers,
        'early_stopping_patience': args.early_stopping_patience,
        'pretrained': True,
        'dropout_rate': 0.2,
        'weight_decay': 1e-4,
        'min_lr': 1e-6
    }
    
    # Crear y ejecutar pipeline
    pipeline = CacaoTrainingPipeline(config)
    results = pipeline.run_pipeline(config['multi_head'])
    
    print("Pipeline completado exitosamente!")
    print(f"Tiempo total: {results['total_time']:.2f}s")
    
    # Mostrar resultados de evaluación
    if 'evaluation_results' in results:
        eval_results = results['evaluation_results']
        print("\n=== RESULTADOS DE EVALUACIÓN ===")
        
        if config['multi_head'] and 'multihead' in eval_results:
            multihead_results = eval_results['multihead']
            for target in TARGETS:
                if target in multihead_results:
                    metrics = multihead_results[target]
                    print(f"{target.upper()}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
        else:
            for target in TARGETS:
                if target in eval_results:
                    metrics = eval_results[target]
                    print(f"{target.upper()}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")


def run_training_pipeline(
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 1e-4,
    multi_head: bool = False,
    model_type: str = 'resnet18',
    img_size: int = 224,
    early_stopping_patience: int = 10,
    save_best_only: bool = True
) -> bool:
    """
    Función para ejecutar el pipeline de entrenamiento desde otros módulos.
    
    Args:
        epochs: Número de épocas
        batch_size: Tamaño de batch
        learning_rate: Learning rate
        multi_head: Si usar modelo multi-head
        model_type: Tipo de modelo
        img_size: Tamaño de imagen
        early_stopping_patience: Paciencia para early stopping
        save_best_only: Solo guardar el mejor modelo
        
    Returns:
        bool: True si el entrenamiento fue exitoso, False en caso contrario
    """
    try:
        logger.info("🚀 Iniciando pipeline de entrenamiento...")
        
        # Crear configuración
        config = {
            'multi_head': multi_head,
            'model_type': model_type,
            'epochs': epochs,
            'batch_size': batch_size,
            'img_size': img_size,
            'learning_rate': learning_rate,
            'num_workers': 2,
            'early_stopping_patience': early_stopping_patience,
            'pretrained': True,
            'dropout_rate': 0.2,
            'weight_decay': 1e-4,
            'min_lr': 1e-6,
            'save_best_only': save_best_only
        }
        
        # Crear y ejecutar pipeline
        pipeline = CacaoTrainingPipeline(config)
        results = pipeline.run_pipeline(multi_head)
        
        logger.info("✅ Pipeline de entrenamiento completado exitosamente!")
        logger.info(f"Tiempo total: {results['total_time']:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en pipeline de entrenamiento: {e}")
        return False


if __name__ == "__main__":
    main()
