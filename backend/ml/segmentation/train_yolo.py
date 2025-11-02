"""
Entrenamiento de YOLOv8-seg personalizado para segmentaciÃ³n de granos de cacao.
"""
import os
import yaml
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import numpy as np
import cv2
from datetime import datetime

try:
    from ultralytics import YOLO
    from ultralytics.utils import LOGGER
except ImportError:
    YOLO = None
    LOGGER = None
    logging.warning("Ultralytics no estÃ¡ instalado. La funcionalidad de entrenamiento no estarÃ¡ disponible.")

from ..utils.paths import (
    get_yolo_artifacts_dir, 
    get_raw_images_dir, 
    get_cacao_images_dir,
    ensure_dir_exists
)
from ..utils.logs import get_ml_logger
from ..data.dataset_loader import CacaoDatasetLoader


logger = get_ml_logger("cacaoscan.ml.segmentation")


class YOLOTrainingManager:
    """Gestor de entrenamiento de YOLOv8-seg personalizado."""
    
    def __init__(
        self,
        dataset_size: int = 150,
        train_split: float = 0.7,
        val_split: float = 0.2,
        test_split: float = 0.1,
        image_size: int = 640,
        epochs: int = 100,
        batch_size: int = 16,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.7
    ):
        """
        Inicializa el gestor de entrenamiento.
        
        Args:
            dataset_size: NÃºmero de imÃ¡genes para el dataset
            train_split: ProporciÃ³n para entrenamiento
            val_split: ProporciÃ³n para validaciÃ³n
            test_split: ProporciÃ³n para testing
            image_size: TamaÃ±o de imagen para entrenamiento
            epochs: NÃºmero de Ã©pocas
            batch_size: TamaÃ±o del batch
            confidence_threshold: Umbral de confianza
            iou_threshold: Umbral de IoU
        """
        if YOLO is None:
            raise ImportError("Ultralytics no estÃ¡ instalado. Instalar con: pip install ultralytics")
        
        self.dataset_size = dataset_size
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = test_split
        self.image_size = image_size
        self.epochs = epochs
        self.batch_size = batch_size
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        
        # Directorios
        self.artifacts_dir = get_yolo_artifacts_dir()
        self.raw_images_dir = get_raw_images_dir()
        self.dataset_dir = self.artifacts_dir / "dataset"
        self.models_dir = self.artifacts_dir / "models"
        
        # Asegurar que los directorios existen
        ensure_dir_exists(self.dataset_dir)
        ensure_dir_exists(self.models_dir)
        
        # ConfiguraciÃ³n de clases
        self.class_names = ["cacao_grain"]
        self.num_classes = len(self.class_names)
        
        logger.info(f"YOLO Training Manager inicializado para {self.dataset_size} imÃ¡genes")
        logger.info(f"Split: Train={train_split:.1%}, Val={val_split:.1%}, Test={test_split:.1%}")
    
    def create_dataset_structure(self) -> Path:
        """
        Crea la estructura de directorios para el dataset YOLO.
        
        Returns:
            Ruta al directorio del dataset
        """
        # Crear estructura de directorios
        train_images_dir = self.dataset_dir / "train" / "images"
        train_labels_dir = self.dataset_dir / "train" / "labels"
        val_images_dir = self.dataset_dir / "val" / "images"
        val_labels_dir = self.dataset_dir / "val" / "labels"
        test_images_dir = self.dataset_dir / "test" / "images"
        test_labels_dir = self.dataset_dir / "test" / "labels"
        
        for dir_path in [train_images_dir, train_labels_dir, val_images_dir, 
                        val_labels_dir, test_images_dir, test_labels_dir]:
            ensure_dir_exists(dir_path)
        
        logger.info(f"Estructura de dataset creada en: {self.dataset_dir}")
        return self.dataset_dir
    
    def generate_annotations_from_crops(self) -> Dict[str, List[Dict]]:
        """
        Genera anotaciones automÃ¡ticas basadas en los crops existentes.
        
        Returns:
            Diccionario con anotaciones por imagen
        """
        logger.info("Generando anotaciones automÃ¡ticas desde crops existentes...")
        
        # Cargar dataset
        loader = CacaoDatasetLoader()
        df = loader.load_dataset()
        valid_df, missing_ids = loader.validate_images_exist(df)
        
        if len(valid_df) < self.dataset_size:
            logger.warning(f"Solo {len(valid_df)} imÃ¡genes disponibles, solicitadas {self.dataset_size}")
            self.dataset_size = len(valid_df)
        
        # Seleccionar muestras aleatorias
        sample_df = valid_df.sample(n=self.dataset_size, random_state=42)
        
        annotations = {}
        
        for _, row in sample_df.iterrows():
            image_id = int(row['id'])
            image_path = self.raw_images_dir / f"{image_id}.bmp"
            
            if not image_path.exists():
                continue
            
            # Generar anotaciÃ³n automÃ¡tica (centro de la imagen)
            annotation = self._generate_automatic_annotation(image_path)
            if annotation:
                annotations[str(image_id)] = annotation
        
        logger.info(f"Generadas {len(annotations)} anotaciones automÃ¡ticas")
        return annotations
    
    def _generate_automatic_annotation(self, image_path: Path) -> Optional[List[Dict]]:
        """
        Genera una anotaciÃ³n automÃ¡tica para una imagen.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Lista de anotaciones o None si falla
        """
        try:
            # Cargar imagen
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            height, width = image.shape[:2]
            
            # Crear anotaciÃ³n centrada (asumiendo que el grano estÃ¡ en el centro)
            center_x = width // 2
            center_y = height // 2
            
            # Calcular bounding box (20% del tamaÃ±o de la imagen)
            bbox_width = int(width * 0.2)
            bbox_height = int(height * 0.2)
            
            x1 = max(0, center_x - bbox_width // 2)
            y1 = max(0, center_y - bbox_height // 2)
            x2 = min(width, center_x + bbox_width // 2)
            y2 = min(height, center_y + bbox_height // 2)
            
            # Convertir a formato YOLO (normalizado)
            x_center = (x1 + x2) / 2 / width
            y_center = (y1 + y2) / 2 / height
            bbox_w = (x2 - x1) / width
            bbox_h = (y2 - y1) / height
            
            # Crear mÃ¡scara simple (rectÃ¡ngulo)
            mask = np.zeros((height, width), dtype=np.uint8)
            mask[y1:y2, x1:x2] = 255
            
            annotation = {
                'class_id': 0,  # cacao_grain
                'bbox': [x_center, y_center, bbox_w, bbox_h],
                'mask': mask,
                'confidence': 1.0
            }
            
            return [annotation]
            
        except Exception as e:
            logger.error(f"Error generando anotaciÃ³n para {image_path}: {e}")
            return None
    
    def create_yolo_dataset(
        self, 
        annotations: Dict[str, List[Dict]],
        manual_annotations: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """
        Crea el dataset YOLO con imÃ¡genes y etiquetas.
        
        Args:
            annotations: Anotaciones automÃ¡ticas
            manual_annotations: Anotaciones manuales opcionales
            
        Returns:
            Diccionario con rutas de archivos por split
        """
        logger.info("Creando dataset YOLO...")
        
        # Combinar anotaciones automÃ¡ticas y manuales
        all_annotations = annotations.copy()
        if manual_annotations:
            all_annotations.update(manual_annotations)
        
        # Crear estructura de directorios
        self.create_dataset_structure()
        
        # Dividir dataset
        image_ids = list(all_annotations.keys())
        np.random.seed(42)
        np.random.shuffle(image_ids)
        
        n_train = int(len(image_ids) * self.train_split)
        n_val = int(len(image_ids) * self.val_split)
        
        train_ids = image_ids[:n_train]
        val_ids = image_ids[n_train:n_train + n_val]
        test_ids = image_ids[n_train + n_val:]
        
        splits = {
            'train': train_ids,
            'val': val_ids,
            'test': test_ids
        }
        
        # Procesar cada split
        for split_name, ids in splits.items():
            logger.info(f"Procesando split {split_name}: {len(ids)} imÃ¡genes")
            
            images_dir = self.dataset_dir / split_name / "images"
            labels_dir = self.dataset_dir / split_name / "labels"
            
            for image_id in ids:
                try:
                    # Copiar imagen
                    source_path = self.raw_images_dir / f"{image_id}.bmp"
                    if not source_path.exists():
                        continue
                    
                    # Convertir a JPG para YOLO
                    image = cv2.imread(str(source_path))
                    if image is None:
                        continue
                    
                    target_image_path = images_dir / f"{image_id}.jpg"
                    cv2.imwrite(str(target_image_path), image)
                    
                    # Crear archivo de etiquetas
                    label_path = labels_dir / f"{image_id}.txt"
                    self._create_yolo_label_file(label_path, all_annotations[image_id])
                    
                except Exception as e:
                    logger.error(f"Error procesando imagen {image_id}: {e}")
        
        # Crear archivo de configuraciÃ³n del dataset
        self._create_dataset_yaml()
        
        logger.info("Dataset YOLO creado exitosamente")
        return splits
    
    def _create_yolo_label_file(self, label_path: Path, annotations: List[Dict]) -> None:
        """
        Crea archivo de etiquetas en formato YOLO.
        
        Args:
            label_path: Ruta al archivo de etiquetas
            annotations: Lista de anotaciones
        """
        with open(label_path, 'w') as f:
            for annotation in annotations:
                class_id = annotation['class_id']
                bbox = annotation['bbox']
                
                # Formato YOLO: class_id x_center y_center width height
                line = f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n"
                f.write(line)
    
    def _create_dataset_yaml(self) -> None:
        """Crea archivo de configuraciÃ³n del dataset."""
        dataset_config = {
            'path': str(self.dataset_dir),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': self.num_classes,
            'names': self.class_names
        }
        
        yaml_path = self.dataset_dir / "dataset.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(dataset_config, f, default_flow_style=False)
        
        logger.info(f"Archivo de configuraciÃ³n creado: {yaml_path}")
    
    def train_model(
        self,
        model_name: str = "yolov8s-seg",
        resume: bool = False,
        pretrained: bool = True
    ) -> Dict[str, Any]:
        """
        Entrena el modelo YOLOv8-seg.
        
        Args:
            model_name: Nombre del modelo base
            resume: Si continuar entrenamiento previo
            pretrained: Si usar pesos pre-entrenados
            
        Returns:
            Diccionario con resultados del entrenamiento
        """
        logger.info(f"Iniciando entrenamiento de {model_name}...")
        
        # Configurar logging de Ultralytics
        if LOGGER:
            LOGGER.setLevel(logging.INFO)
        
        # Cargar modelo
        model = YOLO(f"{model_name}.pt" if pretrained else model_name)
        
        # ConfiguraciÃ³n de entrenamiento
        train_config = {
            'data': str(self.dataset_dir / "dataset.yaml"),
            'epochs': self.epochs,
            'batch': self.batch_size,
            'imgsz': self.image_size,
            'conf': self.confidence_threshold,
            'iou': self.iou_threshold,
            'project': str(self.models_dir),
            'name': f"cacao_seg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'save': True,
            'save_period': 10,
            'cache': True,
            'device': 'cpu',  # Cambiar a 'cuda' si hay GPU disponible
            'workers': 4,
            'patience': 20,
            'lr0': 0.01,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'pose': 12.0,
            'kobj': 2.0,
            'label_smoothing': 0.0,
            'nbs': 64,
            'overlap_mask': True,
            'mask_ratio': 4,
            'dropout': 0.0,
            'val': True,
            'plots': True,
            'verbose': True
        }
        
        try:
            # Iniciar entrenamiento
            results = model.train(**train_config)
            
            # Guardar informaciÃ³n del entrenamiento
            training_info = {
                'model_name': model_name,
                'dataset_size': self.dataset_size,
                'epochs': self.epochs,
                'batch_size': self.batch_size,
                'image_size': self.image_size,
                'training_time': datetime.now().isoformat(),
                'results': results,
                'best_model_path': str(results.save_dir / "weights" / "best.pt"),
                'last_model_path': str(results.save_dir / "weights" / "last.pt")
            }
            
            # Guardar informaciÃ³n en JSON
            info_path = results.save_dir / "training_info.json"
            with open(info_path, 'w') as f:
                json.dump(training_info, f, indent=2, default=str)
            
            logger.info(f"Entrenamiento completado exitosamente")
            logger.info(f"Mejor modelo guardado en: {training_info['best_model_path']}")
            
            return training_info
            
        except Exception as e:
            logger.error(f"Error durante el entrenamiento: {e}")
            raise
    
    def validate_model(self, model_path: Path) -> Dict[str, Any]:
        """
        Valida el modelo entrenado.
        
        Args:
            model_path: Ruta al modelo entrenado
            
        Returns:
            Diccionario con mÃ©tricas de validaciÃ³n
        """
        logger.info(f"Validando modelo: {model_path}")
        
        try:
            # Cargar modelo
            model = YOLO(str(model_path))
            
            # Validar en dataset de test
            results = model.val(
                data=str(self.dataset_dir / "dataset.yaml"),
                split='test',
                imgsz=self.image_size,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                plots=True,
                save_json=True
            )
            
            # Extraer mÃ©tricas principales
            metrics = {
                'mAP50': results.box.map50,
                'mAP50-95': results.box.map,
                'precision': results.box.mp,
                'recall': results.box.mr,
                'f1_score': 2 * (results.box.mp * results.box.mr) / (results.box.mp + results.box.mr) if (results.box.mp + results.box.mr) > 0 else 0,
                'mask_mAP50': results.seg.map50 if hasattr(results, 'seg') else 0,
                'mask_mAP50-95': results.seg.map if hasattr(results, 'seg') else 0
            }
            
            logger.info(f"MÃ©tricas de validaciÃ³n:")
            logger.info(f"  mAP50: {metrics['mAP50']:.3f}")
            logger.info(f"  mAP50-95: {metrics['mAP50-95']:.3f}")
            logger.info(f"  Precision: {metrics['precision']:.3f}")
            logger.info(f"  Recall: {metrics['recall']:.3f}")
            logger.info(f"  F1-Score: {metrics['f1_score']:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error validando modelo: {e}")
            raise
    
    def run_full_training_pipeline(
        self,
        model_name: str = "yolov8s-seg",
        manual_annotations: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de entrenamiento.
        
        Args:
            model_name: Nombre del modelo base
            manual_annotations: Anotaciones manuales opcionales
            
        Returns:
            Diccionario con resultados completos
        """
        logger.info("=== INICIANDO PIPELINE DE ENTRENAMIENTO YOLO ===")
        start_time = datetime.now()
        
        try:
            # 1. Generar anotaciones
            logger.info("Paso 1: Generando anotaciones...")
            annotations = self.generate_annotations_from_crops()
            
            if not annotations:
                raise ValueError("No se pudieron generar anotaciones")
            
            # 2. Crear dataset YOLO
            logger.info("Paso 2: Creando dataset YOLO...")
            splits = self.create_yolo_dataset(annotations, manual_annotations)
            
            # 3. Entrenar modelo
            logger.info("Paso 3: Entrenando modelo...")
            training_results = self.train_model(model_name)
            
            # 4. Validar modelo
            logger.info("Paso 4: Validando modelo...")
            validation_metrics = self.validate_model(Path(training_results['best_model_path']))
            
            # 5. Compilar resultados finales
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            final_results = {
                'success': True,
                'training_duration': duration,
                'dataset_info': {
                    'total_images': len(annotations),
                    'train_images': len(splits['train']),
                    'val_images': len(splits['val']),
                    'test_images': len(splits['test'])
                },
                'training_results': training_results,
                'validation_metrics': validation_metrics,
                'model_paths': {
                    'best_model': training_results['best_model_path'],
                    'last_model': training_results['last_model_path'],
                    'dataset_config': str(self.dataset_dir / "dataset.yaml")
                }
            }
            
            logger.info("=== PIPELINE COMPLETADO EXITOSAMENTE ===")
            logger.info(f"DuraciÃ³n total: {duration:.2f} segundos")
            logger.info(f"Mejor modelo: {training_results['best_model_path']}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error en pipeline de entrenamiento: {e}")
            return {
                'success': False,
                'error': str(e),
                'training_duration': (datetime.now() - start_time).total_seconds()
            }


def create_yolo_trainer(
    dataset_size: int = 150,
    epochs: int = 100,
    batch_size: int = 16
) -> YOLOTrainingManager:
    """
    FunciÃ³n de conveniencia para crear un entrenador YOLO.
    
    Args:
        dataset_size: NÃºmero de imÃ¡genes para el dataset
        epochs: NÃºmero de Ã©pocas
        batch_size: TamaÃ±o del batch
        
    Returns:
        Instancia de YOLOTrainingManager
    """
    return YOLOTrainingManager(
        dataset_size=dataset_size,
        epochs=epochs,
        batch_size=batch_size
    )


def train_cacao_yolo_model(
    dataset_size: int = 150,
    epochs: int = 100,
    batch_size: int = 16,
    model_name: str = "yolov8s-seg"
) -> Dict[str, Any]:
    """
    FunciÃ³n de conveniencia para entrenar modelo YOLO de cacao.
    
    Args:
        dataset_size: NÃºmero de imÃ¡genes para el dataset
        epochs: NÃºmero de Ã©pocas
        batch_size: TamaÃ±o del batch
        model_name: Nombre del modelo base
        
    Returns:
        Resultados del entrenamiento
    """
    trainer = create_yolo_trainer(dataset_size, epochs, batch_size)
    return trainer.run_full_training_pipeline(model_name)


