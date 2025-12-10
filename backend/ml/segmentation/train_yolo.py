"""
Entrenamiento de YOLOv8-seg personalizado para segmentación de granos de cacao.

REFACTORIZADO: Aplicando principios SOLID
- Funciones auxiliares extraídas para mejorar SRP
- Mejores docstrings y type hints
- Separación de responsabilidades mejorada
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
    logging.warning("Ultralytics no está instalado. La funcionalidad de entrenamiento no estará disponible.")

from ..utils.paths import (
    get_yolo_artifacts_dir, 
    get_raw_images_dir, 
    get_cacao_images_dir,
    ensure_dir_exists
)
from ..utils.logs import get_ml_logger
from ..data.dataset_loader import CacaoDatasetLoader


logger = get_ml_logger("cacaoscan.ml.segmentation")


def _normalizar_mascara_yolo(mask: np.ndarray, target_height: int, target_width: int) -> np.ndarray:
    """
    Normaliza y redimensiona máscara a dimensiones objetivo.
    
    Args:
        mask: Máscara original
        target_height: Altura objetivo
        target_width: Ancho objetivo
        
    Returns:
        Máscara normalizada y redimensionada
    """
    mask_height, mask_width = mask.shape[:2]
    
    if mask_height != target_height or mask_width != target_width:
        mask = cv2.resize(mask, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
    
    if mask.dtype != np.uint8:
        if mask.max() <= 1.0:
            mask = (mask * 255).astype(np.uint8)
        else:
            mask = mask.astype(np.uint8)
    
    return mask


def _calcular_bbox_yolo_desde_mascara(mask: np.ndarray, width: int, height: int) -> Optional[List[float]]:
    """
    Calcula bounding box en formato YOLO desde máscara.
    
    Args:
        mask: Máscara binaria
        width: Ancho de la imagen
        height: Altura de la imagen
        
    Returns:
        Bounding box en formato YOLO [x_center, y_center, width, height] normalizado o None
    """
    coords = np.nonzero(mask > 128)
    if len(coords[0]) == 0:
        return None
    
    y_min, y_max = int(coords[0].min()), int(coords[0].max())
    x_min, x_max = int(coords[1].min()), int(coords[1].max())
    
    x_center = ((x_min + x_max) / 2) / width
    y_center = ((y_min + y_max) / 2) / height
    bbox_w = (x_max - x_min) / width
    bbox_h = (y_max - y_min) / height
    
    return [x_center, y_center, bbox_w, bbox_h]


def _convertir_mascara_a_poligono_yolo(mask: np.ndarray, width: int, height: int) -> Optional[List[float]]:
    """
    Convierte máscara binaria a polígono en formato YOLO para segmentación.
    
    Args:
        mask: Máscara binaria (uint8, valores 0-255)
        width: Ancho de la imagen
        height: Altura de la imagen
        
    Returns:
        Lista de puntos normalizados [x1, y1, x2, y2, ...] o None si no hay contorno
    """
    # Asegurar que la máscara es binaria
    if mask.dtype != np.uint8:
        mask_binary = (mask > 128).astype(np.uint8) * 255
    else:
        mask_binary = (mask > 128).astype(np.uint8) * 255
    
    # Encontrar contornos
    contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return None
    
    # Usar el contorno más grande
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Simplificar el contorno si tiene muchos puntos (reducir complejidad)
    epsilon = 0.001 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    
    # Aplanar y normalizar puntos
    polygon_points: List[float] = []
    for point in approx:
        x = float(point[0][0]) / width
        y = float(point[0][1]) / height
        # Asegurar que los valores están en el rango [0, 1]
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        polygon_points.extend([x, y])
    
    return polygon_points if len(polygon_points) >= 6 else None


def _crear_diccionario_anotacion(bbox: List[float], mask: np.ndarray, confidence: float) -> Dict[str, Any]:
    """
    Crea diccionario de anotación en formato estándar.
    
    Args:
        bbox: Bounding box en formato YOLO
        mask: Máscara binaria
        confidence: Confianza de la detección
        
    Returns:
        Diccionario con anotación
    """
    return {
        'class_id': 0,  # cacao_grain
        'bbox': bbox,
        'mask': mask,
        'confidence': confidence
    }

# Dataset file constants
DATASET_YAML_FILENAME = "dataset.yaml"


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
            dataset_size: Número de imágenes para el dataset
            train_split: Proporción para entrenamiento
            val_split: Proporción para validación
            test_split: Proporción para testing
            image_size: Tamaño de imagen para entrenamiento
            epochs: Número de épocas
            batch_size: Tamaño del batch
            confidence_threshold: Umbral de confianza
            iou_threshold: Umbral de IoU
        """
        if YOLO is None:
            raise ImportError("Ultralytics no está instalado. Instalar con: pip install ultralytics")
        
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
        
        # Configuración de clases
        self.class_names = ["cacao_grain"]
        self.num_classes = len(self.class_names)
        
        logger.info(f"YOLO Training Manager inicializado para {self.dataset_size} imágenes")
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
        Genera anotaciones automáticas basadas en los crops existentes.
        
        Returns:
            Diccionario con anotaciones por imagen
        """
        logger.info("Generando anotaciones automáticas desde crops existentes...")
        
        # Cargar dataset
        loader = CacaoDatasetLoader()
        df = loader.load_dataset()
        valid_df, _ = loader.validate_images_exist(df)
        
        if len(valid_df) < self.dataset_size:
            logger.warning(f"Solo {len(valid_df)} imágenes disponibles, solicitadas {self.dataset_size}")
            self.dataset_size = len(valid_df)
        
        # Seleccionar muestras aleatorias
        sample_df = valid_df.sample(n=self.dataset_size, random_state=42)
        
        annotations = {}
        
        for _, row in sample_df.iterrows():
            image_id = int(row['id'])
            image_path = self.raw_images_dir / f"{image_id}.bmp"
            
            if not image_path.exists():
                continue
            
            # Generar anotación automática (centro de la imagen)
            annotation = self._generate_automatic_annotation(image_path)
            if annotation:
                annotations[str(image_id)] = annotation
        
        logger.info(f"Generadas {len(annotations)} anotaciones automáticas")
        return annotations
    
    def _normalize_mask(self, mask: np.ndarray, target_height: int, target_width: int) -> np.ndarray:
        """
        Normaliza y redimensiona máscara a dimensiones objetivo.
        
        Args:
            mask: Máscara original
            target_height: Altura objetivo
            target_width: Ancho objetivo
            
        Returns:
            Máscara normalizada y redimensionada
        """
        return _normalizar_mascara_yolo(mask, target_height, target_width)
    
    def _calculate_yolo_bbox_from_mask(self, mask: np.ndarray, width: int, height: int) -> Optional[List[float]]:
        """
        Calcula bounding box en formato YOLO desde máscara.
        
        Args:
            mask: Máscara binaria
            width: Ancho de la imagen
            height: Altura de la imagen
            
        Returns:
            Bounding box en formato YOLO normalizado o None
        """
        return _calcular_bbox_yolo_desde_mascara(mask, width, height)
    
    def _create_annotation_dict(self, bbox: List[float], mask: np.ndarray, confidence: float) -> Dict[str, Any]:
        """
        Crea diccionario de anotación en formato estándar.
        
        Args:
            bbox: Bounding box en formato YOLO
            mask: Máscara binaria
            confidence: Confianza de la detección
            
        Returns:
            Diccionario con anotación
        """
        return _crear_diccionario_anotacion(bbox, mask, confidence)
    
    def _generate_annotation_from_yolo(self, image_path: Path) -> Optional[List[Dict]]:
        """Generates annotation using YOLO base model."""
        try:
            from .infer_yolo_seg import YOLOSegmentationInference
            
            yolo_inference = YOLOSegmentationInference(confidence_threshold=0.2)
            prediction = yolo_inference.get_best_prediction(image_path)
            
            if not prediction or prediction.get('mask') is None:
                return None
            
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            height, width = image.shape[:2]
            mask = self._normalize_mask(prediction['mask'], height, width)
            bbox = self._calculate_yolo_bbox_from_mask(mask, width, height)
            
            if bbox is None:
                return None
            
            annotation = self._create_annotation_dict(
                bbox,
                mask,
                prediction.get('confidence', 0.5)
            )
            
            logger.debug(f"Anotación generada usando YOLO base para {image_path.name}")
            return [annotation]
        except Exception as e:
            logger.debug(f"No se pudo usar YOLO base para {image_path.name}: {e}")
            return None
    
    def _generate_annotation_from_crop(self, image_path: Path) -> Optional[List[Dict]]:
        """Generates annotation from existing crop."""
        try:
            from ..utils.paths import get_crops_dir
            from PIL import Image
            
            image_id = image_path.stem
            crop_path = get_crops_dir() / f"{image_id}.png"
            
            if not crop_path.exists():
                return None
            
            crop_image = Image.open(crop_path)
            if crop_image.mode != 'RGBA':
                return None
            
            crop_array = np.array(crop_image)
            alpha = crop_array[:, :, 3]
            
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            height, width = image.shape[:2]
            mask = cv2.resize(alpha, (width, height), interpolation=cv2.INTER_LINEAR)
            bbox = self._calculate_yolo_bbox_from_mask(mask, width, height)
            
            if bbox is None:
                return None
            
            annotation = self._create_annotation_dict(bbox, mask, 0.8)
            
            logger.debug(f"Anotación generada usando crop existente para {image_path.name}")
            return [annotation]
        except Exception as e:
            logger.debug(f"No se pudo usar crop existente para {image_path.name}: {e}")
            return None
    
    def _generate_annotation_fallback(self, image_path: Path) -> Optional[List[Dict]]:
        """Generates fallback centered annotation."""
        image = cv2.imread(str(image_path))
        if image is None:
            return None
        
        height, width = image.shape[:2]
        
        center_x = width // 2
        center_y = height // 2
        bbox_width = int(width * 0.2)
        bbox_height = int(height * 0.2)
        
        x1 = max(0, center_x - bbox_width // 2)
        y1 = max(0, center_y - bbox_height // 2)
        x2 = min(width, center_x + bbox_width // 2)
        y2 = min(height, center_y + bbox_height // 2)
        
        x_center = (x1 + x2) / 2 / width
        y_center = (y1 + y2) / 2 / height
        bbox_w = (x2 - x1) / width
        bbox_h = (y2 - y1) / height
        
        mask = np.zeros((height, width), dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255
        
        annotation = self._create_annotation_dict([x_center, y_center, bbox_w, bbox_h], mask, 0.5)
        
        logger.debug(f"Anotación generada usando método fallback (centrado) para {image_path.name}")
        return [annotation]
    
    def _generate_automatic_annotation(self, image_path: Path) -> Optional[List[Dict]]:
        """
        Genera una anotación automática para una imagen.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Lista de anotaciones o None si falla
        """
        try:
            # Método 1: Intentar usar YOLO base
            annotation = self._generate_annotation_from_yolo(image_path)
            if annotation:
                return annotation
            
            # Método 2: Intentar usar crop existente
            annotation = self._generate_annotation_from_crop(image_path)
            if annotation:
                return annotation
            
            # Método 3: Fallback - anotación centrada
            return self._generate_annotation_fallback(image_path)
            
        except Exception as e:
            logger.error(f"Error generando anotación para {image_path}: {e}")
            return None
    
    def create_yolo_dataset(
        self, 
        annotations: Dict[str, List[Dict]],
        manual_annotations: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """
        Crea el dataset YOLO con imágenes y etiquetas.
        
        Args:
            annotations: Anotaciones automáticas
            manual_annotations: Anotaciones manuales opcionales
            
        Returns:
            Diccionario con rutas de archivos por split
        """
        logger.info("Creando dataset YOLO...")
        
        # Combinar anotaciones automáticas y manuales
        all_annotations = annotations.copy()
        if manual_annotations:
            all_annotations.update(manual_annotations)
        
        # Crear estructura de directorios
        self.create_dataset_structure()
        
        # Dividir dataset
        image_ids = list(all_annotations.keys())
        rng = np.random.default_rng(42)
        rng.shuffle(image_ids)
        
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
            logger.info(f"Procesando split {split_name}: {len(ids)} imágenes")
            
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
                    
                    height, width = image.shape[:2]
                    
                    target_image_path = images_dir / f"{image_id}.jpg"
                    cv2.imwrite(str(target_image_path), image)
                    
                    # Crear archivo de etiquetas
                    label_path = labels_dir / f"{image_id}.txt"
                    self._create_yolo_label_file(label_path, all_annotations[image_id], width, height)
                    
                except Exception as e:
                    logger.error(f"Error procesando imagen {image_id}: {e}")
        
        # Crear archivo de configuración del dataset
        self._create_dataset_yaml()
        
        logger.info("Dataset YOLO creado exitosamente")
        return splits
    
    def _create_yolo_label_file(self, label_path: Path, annotations: List[Dict], width: int, height: int) -> None:
        """
        Crea archivo de etiquetas en formato YOLO para segmentación.
        
        Args:
            label_path: Ruta al archivo de etiquetas
            annotations: Lista de anotaciones (debe incluir 'mask')
            width: Ancho de la imagen
            height: Altura de la imagen
        """
        with open(label_path, 'w') as f:
            for annotation in annotations:
                class_id = annotation['class_id']
                mask = annotation.get('mask')
                
                if mask is None:
                    # Fallback a bbox si no hay máscara
                    bbox = annotation['bbox']
                    line = f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n"
                    f.write(line)
                    continue
                
                # Asegurar que la máscara tiene las dimensiones correctas
                mask_height, mask_width = mask.shape[:2]
                if mask_height != height or mask_width != width:
                    mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_LINEAR)
                
                # Convertir máscara a polígono
                polygon = _convertir_mascara_a_poligono_yolo(mask, width, height)
                
                if polygon is None or len(polygon) < 6:  # Mínimo 3 puntos (6 valores)
                    # Fallback a bbox si no se puede generar polígono
                    bbox = annotation['bbox']
                    line = f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n"
                    f.write(line)
                    logger.warning(f"No se pudo generar polígono para anotación, usando bbox como fallback")
                    continue
                
                # Formato YOLO segmentación: class_id x1 y1 x2 y2 ... xn yn
                polygon_str = ' '.join(f"{coord:.6f}" for coord in polygon)
                line = f"{class_id} {polygon_str}\n"
                f.write(line)
    
    def _create_dataset_yaml(self) -> None:
        """Crea archivo de configuración del dataset."""
        dataset_config = {
            'path': str(self.dataset_dir),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': self.num_classes,
            'names': self.class_names
        }
        
        yaml_path = self.dataset_dir / DATASET_YAML_FILENAME
        with open(yaml_path, 'w') as f:
            yaml.dump(dataset_config, f, default_flow_style=False)
        
        logger.info(f"Archivo de configuración creado: {yaml_path}")
    
    def train_model(
        self,
        model_name: str = "yolov8s-seg",
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
        
        # Configuración de entrenamiento
        train_config = {
                'data': str(self.dataset_dir / DATASET_YAML_FILENAME),
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
            
            # Guardar información del entrenamiento
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
            
            # Guardar información en JSON
            info_path = results.save_dir / "training_info.json"
            with open(info_path, 'w') as f:
                json.dump(training_info, f, indent=2, default=str)
            
            logger.info("Entrenamiento completado exitosamente")
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
            Diccionario con métricas de validación
        """
        logger.info(f"Validando modelo: {model_path}")
        
        try:
            # Cargar modelo
            model = YOLO(str(model_path))
            
            # Validar en dataset de test
            results = model.val(
                    data=str(self.dataset_dir / DATASET_YAML_FILENAME),
                split='test',
                imgsz=self.image_size,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                plots=True,
                save_json=True
            )
            
            # Extraer métricas principales
            metrics = {
                'mAP50': results.box.map50,
                'mAP50-95': results.box.map,
                'precision': results.box.mp,
                'recall': results.box.mr,
                'f1_score': 2 * (results.box.mp * results.box.mr) / (results.box.mp + results.box.mr) if (results.box.mp + results.box.mr) > 0 else 0,
                'mask_mAP50': results.seg.map50 if hasattr(results, 'seg') else 0,
                'mask_mAP50-95': results.seg.map if hasattr(results, 'seg') else 0
            }
            
            logger.info("Métricas de validación:")
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
                    'dataset_config': str(self.dataset_dir / DATASET_YAML_FILENAME)
                }
            }
            
            logger.info("=== PIPELINE COMPLETADO EXITOSAMENTE ===")
            logger.info(f"Duración total: {duration:.2f} segundos")
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
    Función de conveniencia para crear un entrenador YOLO.
    
    Args:
        dataset_size: Número de imágenes para el dataset
        epochs: Número de épocas
        batch_size: Tamaño del batch
        
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
    Función de conveniencia para entrenar modelo YOLO de cacao.
    
    Args:
        dataset_size: Número de imágenes para el dataset
        epochs: Número de épocas
        batch_size: Tamaño del batch
        model_name: Nombre del modelo base
        
    Returns:
        Resultados del entrenamiento
    """
    trainer = create_yolo_trainer(dataset_size, epochs, batch_size)
    return trainer.run_full_training_pipeline(model_name)


