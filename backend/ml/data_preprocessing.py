"""
Módulo de preprocesamiento de datos para el modelo de visión de cacao.

Este módulo contiene funciones para cargar, procesar y transformar imágenes
de granos de cacao desde la base de datos Django y prepararlas para el entrenamiento
y la inferencia del modelo de visión artificial.
"""

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import logging
from typing import List, Tuple, Optional, Dict, Union
from pathlib import Path
import django
from django.conf import settings

# Configurar Django si no está configurado
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from apps.images.models import CacaoImage
from .config import IMAGE_PREPROCESSING, SUPPORTED_IMAGE_FORMATS

# Configurar logging
logger = logging.getLogger(__name__)


class CacaoImageTransforms:
    """
    Clase para manejar las transformaciones de imágenes de cacao.
    
    Proporciona transformaciones tanto para entrenamiento (con augmentación)
    como para inferencia (solo normalización).
    """
    
    def __init__(self, image_size: Tuple[int, int] = (224, 224), 
                 normalize: bool = True, augment: bool = False):
        """
        Inicializa las transformaciones.
        
        Args:
            image_size (Tuple[int, int]): Tamaño objetivo de las imágenes
            normalize (bool): Si aplicar normalización
            augment (bool): Si aplicar augmentación de datos
        """
        self.image_size = image_size
        self.normalize = normalize
        self.augment = augment
        
        # Estadísticas de normalización (ImageNet por defecto)
        self.mean = IMAGE_PREPROCESSING.get('mean', [0.485, 0.456, 0.406])
        self.std = IMAGE_PREPROCESSING.get('std', [0.229, 0.224, 0.225])
        
        self.train_transforms = self._build_train_transforms()
        self.val_transforms = self._build_val_transforms()
    
    def _build_train_transforms(self) -> transforms.Compose:
        """
        Construye las transformaciones para entrenamiento.
        
        Returns:
            transforms.Compose: Transformaciones de entrenamiento
        """
        transform_list = [
            transforms.Resize(self.image_size),
            transforms.ToTensor()
        ]
        
        if self.augment:
            # Insertar augmentaciones antes de ToTensor
            augment_transforms = [
                transforms.Resize((int(self.image_size[0] * 1.1), int(self.image_size[1] * 1.1))),
                transforms.RandomCrop(self.image_size),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                transforms.ToTensor()
            ]
            transform_list = augment_transforms
        
        if self.normalize:
            transform_list.append(
                transforms.Normalize(mean=self.mean, std=self.std)
            )
        
        return transforms.Compose(transform_list)
    
    def _build_val_transforms(self) -> transforms.Compose:
        """
        Construye las transformaciones para validación/inferencia.
        
        Returns:
            transforms.Compose: Transformaciones de validación
        """
        transform_list = [
            transforms.Resize(self.image_size),
            transforms.ToTensor()
        ]
        
        if self.normalize:
            transform_list.append(
                transforms.Normalize(mean=self.mean, std=self.std)
            )
        
        return transforms.Compose(transform_list)
    
    def get_transforms(self, training: bool = True) -> transforms.Compose:
        """
        Obtiene las transformaciones apropiadas.
        
        Args:
            training (bool): Si es para entrenamiento o no
            
        Returns:
            transforms.Compose: Transformaciones apropiadas
        """
        return self.train_transforms if training else self.val_transforms


class CacaoDataset(Dataset):
    """
    Dataset personalizado para imágenes de cacao con medidas físicas.
    
    Carga imágenes desde el modelo Django CacaoImage y sus medidas correspondientes
    (width, height, thickness, weight).
    """
    
    def __init__(self, 
                 queryset: Optional[any] = None,
                 transforms: Optional[transforms.Compose] = None,
                 filter_complete: bool = True,
                 media_root: Optional[str] = None):
        """
        Inicializa el dataset.
        
        Args:
            queryset: QuerySet de Django con objetos CacaoImage
            transforms: Transformaciones a aplicar a las imágenes
            filter_complete: Si filtrar solo imágenes con todas las medidas
            media_root: Ruta raíz donde están las imágenes
        """
        self.media_root = media_root or settings.MEDIA_ROOT
        self.transforms = transforms or CacaoImageTransforms().get_transforms(training=False)
        
        # Obtener queryset
        if queryset is None:
            queryset = CacaoImage.objects.all()
        
        # Filtrar imágenes con datos completos si se requiere
        if filter_complete:
            queryset = queryset.filter(
                width__isnull=False,
                height__isnull=False,
                thickness__isnull=False,
                weight__isnull=False,
                image__isnull=False
            )
        
        self.data = list(queryset)
        
        if len(self.data) == 0:
            logger.warning("El dataset está vacío. Verificar que existan imágenes con medidas completas.")
    
    def __len__(self) -> int:
        """Retorna el tamaño del dataset."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        """
        Obtiene un elemento del dataset.
        
        Args:
            idx (int): Índice del elemento
            
        Returns:
            Tuple: (imagen_tensor, medidas_tensor, metadata)
        """
        cacao_image = self.data[idx]
        
        # Cargar imagen
        image_path = os.path.join(self.media_root, str(cacao_image.image))
        
        try:
            image = self._load_image(image_path)
            
            # Aplicar transformaciones
            if self.transforms:
                image = self.transforms(image)
            
            # Preparar targets (medidas físicas)
            targets = torch.tensor([
                float(cacao_image.width),
                float(cacao_image.height), 
                float(cacao_image.thickness),
                float(cacao_image.weight)
            ], dtype=torch.float32)
            
            # Metadata adicional
            metadata = {
                'id': cacao_image.id,
                'batch_number': cacao_image.batch_number,
                'quality': cacao_image.predicted_quality,
                'image_path': image_path,
                'created_at': cacao_image.created_at
            }
            
            return image, targets, metadata
            
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            # Retornar tensor vacío en caso de error
            empty_image = torch.zeros(3, 224, 224)
            empty_targets = torch.zeros(4)
            empty_metadata = {'id': cacao_image.id, 'error': str(e)}
            return empty_image, empty_targets, empty_metadata
    
    def _load_image(self, image_path: str) -> Image.Image:
        """
        Carga una imagen desde archivo.
        
        Args:
            image_path (str): Ruta a la imagen
            
        Returns:
            Image.Image: Imagen PIL cargada
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        # Verificar formato soportado
        ext = Path(image_path).suffix.lower()
        if ext not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"Formato de imagen no soportado: {ext}")
        
        # Cargar con PIL
        image = Image.open(image_path)
        
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def get_statistics(self) -> Dict:
        """
        Calcula estadísticas del dataset.
        
        Returns:
            Dict: Estadísticas del dataset
        """
        if len(self.data) == 0:
            return {}
        
        widths = []
        heights = []
        thicknesses = []
        weights = []
        
        for item in self.data:
            if all([item.width, item.height, item.thickness, item.weight]):
                widths.append(float(item.width))
                heights.append(float(item.height))
                thicknesses.append(float(item.thickness))
                weights.append(float(item.weight))
        
        stats = {
            'num_samples': len(self.data),
            'num_complete': len(widths),
            'width': {
                'mean': np.mean(widths) if widths else 0,
                'std': np.std(widths) if widths else 0,
                'min': np.min(widths) if widths else 0,
                'max': np.max(widths) if widths else 0
            },
            'height': {
                'mean': np.mean(heights) if heights else 0,
                'std': np.std(heights) if heights else 0,
                'min': np.min(heights) if heights else 0,
                'max': np.max(heights) if heights else 0
            },
            'thickness': {
                'mean': np.mean(thicknesses) if thicknesses else 0,
                'std': np.std(thicknesses) if thicknesses else 0,
                'min': np.min(thicknesses) if thicknesses else 0,
                'max': np.max(thicknesses) if thicknesses else 0
            },
            'weight': {
                'mean': np.mean(weights) if weights else 0,
                'std': np.std(weights) if weights else 0,
                'min': np.min(weights) if weights else 0,
                'max': np.max(weights) if weights else 0
            }
        }
        
        return stats


def load_cacao_images_from_media(media_path: str, 
                                image_extensions: List[str] = None) -> List[str]:
    """
    Carga rutas de imágenes desde la carpeta media.
    
    Args:
        media_path (str): Ruta a la carpeta media
        image_extensions (List[str]): Extensiones de imagen permitidas
        
    Returns:
        List[str]: Lista de rutas de imágenes encontradas
    """
    if image_extensions is None:
        image_extensions = SUPPORTED_IMAGE_FORMATS
    
    image_paths = []
    media_path = Path(media_path)
    
    if not media_path.exists():
        logger.warning(f"Carpeta media no encontrada: {media_path}")
        return image_paths
    
    # Buscar recursivamente imágenes
    for ext in image_extensions:
        pattern = f"**/*{ext}"
        found_images = list(media_path.glob(pattern))
        image_paths.extend([str(img) for img in found_images])
    
    logger.info(f"Encontradas {len(image_paths)} imágenes en {media_path}")
    return sorted(image_paths)


def create_data_loaders(train_dataset: Dataset, 
                       val_dataset: Optional[Dataset] = None,
                       batch_size: int = 32,
                       num_workers: int = 4,
                       shuffle_train: bool = True) -> Tuple[DataLoader, Optional[DataLoader]]:
    """
    Crea DataLoaders para entrenamiento y validación.
    
    Args:
        train_dataset (Dataset): Dataset de entrenamiento
        val_dataset (Dataset, optional): Dataset de validación
        batch_size (int): Tamaño del batch
        num_workers (int): Número de workers para carga de datos
        shuffle_train (bool): Si mezclar datos de entrenamiento
        
    Returns:
        Tuple[DataLoader, Optional[DataLoader]]: DataLoaders de train y validación
    """
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=True
    )
    
    val_loader = None
    if val_dataset is not None:
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
            drop_last=False
        )
    
    return train_loader, val_loader


def split_dataset(dataset: CacaoDataset, 
                 train_ratio: float = 0.8,
                 val_ratio: float = 0.2,
                 random_seed: int = 42) -> Tuple[CacaoDataset, CacaoDataset]:
    """
    Divide el dataset en entrenamiento y validación.
    
    Args:
        dataset (CacaoDataset): Dataset original
        train_ratio (float): Proporción para entrenamiento
        val_ratio (float): Proporción para validación
        random_seed (int): Semilla para reproducibilidad
        
    Returns:
        Tuple[CacaoDataset, CacaoDataset]: Datasets de train y validación
    """
    if abs(train_ratio + val_ratio - 1.0) > 1e-6:
        raise ValueError("train_ratio + val_ratio debe ser igual a 1.0")
    
    # Configurar semilla
    np.random.seed(random_seed)
    
    # Obtener índices y mezclar
    total_size = len(dataset)
    indices = np.arange(total_size)
    np.random.shuffle(indices)
    
    # Calcular puntos de división
    train_size = int(total_size * train_ratio)
    
    train_indices = indices[:train_size]
    val_indices = indices[train_size:]
    
    # Crear subdatasets
    train_data = [dataset.data[i] for i in train_indices]
    val_data = [dataset.data[i] for i in val_indices]
    
    # Crear nuevos datasets
    train_transforms = CacaoImageTransforms(augment=True).get_transforms(training=True)
    val_transforms = CacaoImageTransforms(augment=False).get_transforms(training=False)
    
    train_dataset = CacaoDataset(transforms=train_transforms)
    train_dataset.data = train_data
    
    val_dataset = CacaoDataset(transforms=val_transforms)
    val_dataset.data = val_data
    
    logger.info(f"Dataset dividido: {len(train_data)} entrenamiento, {len(val_data)} validación")
    
    return train_dataset, val_dataset


def preprocess_single_image(image_path: str, 
                          target_size: Tuple[int, int] = (224, 224),
                          normalize: bool = True) -> torch.Tensor:
    """
    Preprocesa una sola imagen para inferencia.
    
    Args:
        image_path (str): Ruta a la imagen
        target_size (Tuple[int, int]): Tamaño objetivo
        normalize (bool): Si aplicar normalización
        
    Returns:
        torch.Tensor: Imagen preprocesada como tensor
    """
    transform = CacaoImageTransforms(
        image_size=target_size,
        normalize=normalize,
        augment=False
    ).get_transforms(training=False)
    
    # Cargar imagen
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Aplicar transformaciones
    tensor = transform(image)
    
    # Añadir dimensión de batch
    return tensor.unsqueeze(0)


def calculate_dataset_statistics(dataset: CacaoDataset) -> Dict:
    """
    Calcula estadísticas completas del dataset incluyendo estadísticas de imágenes.
    
    Args:
        dataset (CacaoDataset): Dataset a analizar
        
    Returns:
        Dict: Estadísticas completas
    """
    stats = dataset.get_statistics()
    
    # Añadir estadísticas de calidad
    quality_counts = {}
    defect_counts = {}
    
    for item in dataset.data:
        quality = item.predicted_quality
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        defect = item.defect_type
        defect_counts[defect] = defect_counts.get(defect, 0) + 1
    
    stats['quality_distribution'] = quality_counts
    stats['defect_distribution'] = defect_counts
    
    return stats


if __name__ == "__main__":
    # Ejemplo de uso
    print("Creando dataset de cacao...")
    
    # Crear transformaciones
    transforms_obj = CacaoImageTransforms(image_size=(224, 224), augment=True)
    
    # Crear dataset
    dataset = CacaoDataset(
        transforms=transforms_obj.get_transforms(training=True),
        filter_complete=True
    )
    
    print(f"Dataset creado con {len(dataset)} imágenes")
    
    if len(dataset) > 0:
        # Mostrar estadísticas
        stats = dataset.get_statistics()
        print("\nEstadísticas del dataset:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Ejemplo de carga de datos
        sample_image, sample_targets, sample_metadata = dataset[0]
        print(f"\nEjemplo de muestra:")
        print(f"  Forma de imagen: {sample_image.shape}")
        print(f"  Targets: {sample_targets}")
        print(f"  Metadata: {sample_metadata}")
    else:
        print("No hay imágenes disponibles para procesar.")
