"""
Utilidades para el módulo de Machine Learning.

Este módulo contiene funciones auxiliares para el procesamiento
de imágenes, carga de modelos y manipulación de datos para ML.
"""

import os
import logging
import numpy as np
from typing import Union, Tuple, List, Optional, Any
from pathlib import Path
from PIL import Image, ImageOps
import cv2

# Configuración de logging
logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Clase para el procesamiento de imágenes para modelos de ML.
    """
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        """
        Inicializa el procesador de imágenes.
        
        Args:
            target_size (Tuple[int, int]): Tamaño objetivo (ancho, alto)
        """
        self.target_size = target_size
        
    def load_image(self, image_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        Carga una imagen desde archivo.
        
        Args:
            image_path (Union[str, Path]): Ruta al archivo de imagen
            
        Returns:
            Optional[np.ndarray]: Array de la imagen o None si hay error
        """
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                logger.error(f"Archivo de imagen no encontrado: {image_path}")
                return None
                
            # Cargar con PIL para mayor compatibilidad
            with Image.open(image_path) as img:
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convertir a numpy array
                image_array = np.array(img)
                
            logger.info(f"Imagen cargada exitosamente: {image_path}")
            return image_array
            
        except Exception as e:
            logger.error(f"Error al cargar imagen {image_path}: {str(e)}")
            return None
    
    def load_image_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Carga una imagen desde bytes.
        
        Args:
            image_bytes (bytes): Datos de la imagen en bytes
            
        Returns:
            Optional[np.ndarray]: Array de la imagen o None si hay error
        """
        try:
            # Convertir bytes a array numpy
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # Decodificar imagen
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("No se pudo decodificar la imagen desde bytes")
                return None
            
            # Convertir de BGR a RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            logger.info("Imagen cargada exitosamente desde bytes")
            return image
            
        except Exception as e:
            logger.error(f"Error al cargar imagen desde bytes: {str(e)}")
            return None
    
    def resize_image(self, image: np.ndarray, 
                    target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Redimensiona una imagen al tamaño objetivo.
        
        Args:
            image (np.ndarray): Imagen a redimensionar
            target_size (Optional[Tuple[int, int]]): Tamaño objetivo
            
        Returns:
            np.ndarray: Imagen redimensionada
        """
        if target_size is None:
            target_size = self.target_size
            
        try:
            # Usar PIL para mejor calidad de redimensionado
            pil_image = Image.fromarray(image)
            resized_image = pil_image.resize(target_size, Image.Resampling.LANCZOS)
            
            return np.array(resized_image)
            
        except Exception as e:
            logger.error(f"Error al redimensionar imagen: {str(e)}")
            # Fallback con OpenCV
            return cv2.resize(image, target_size)
    
    def normalize_image(self, image: np.ndarray,
                       mean: Optional[List[float]] = None,
                       std: Optional[List[float]] = None) -> np.ndarray:
        """
        Normaliza una imagen.
        
        Args:
            image (np.ndarray): Imagen a normalizar
            mean (Optional[List[float]]): Medias para normalización
            std (Optional[List[float]]): Desviaciones estándar
            
        Returns:
            np.ndarray: Imagen normalizada
        """
        # Convertir a float32 y normalizar a [0, 1]
        normalized = image.astype(np.float32) / 255.0
        
        # Aplicar normalización con media y std si se proporcionan
        if mean is not None and std is not None:
            mean = np.array(mean, dtype=np.float32)
            std = np.array(std, dtype=np.float32)
            
            normalized = (normalized - mean) / std
            
        return normalized
    
    def preprocess_image(self, image: Union[str, Path, np.ndarray, bytes],
                        target_size: Optional[Tuple[int, int]] = None,
                        normalize: bool = True,
                        mean: Optional[List[float]] = None,
                        std: Optional[List[float]] = None) -> Optional[np.ndarray]:
        """
        Preprocesa una imagen para el modelo ML.
        
        Args:
            image: Imagen (ruta, array numpy o bytes)
            target_size: Tamaño objetivo
            normalize: Si normalizar la imagen
            mean: Medias para normalización
            std: Desviaciones estándar para normalización
            
        Returns:
            Optional[np.ndarray]: Imagen preprocesada
        """
        try:
            # Cargar imagen según el tipo
            if isinstance(image, (str, Path)):
                img_array = self.load_image(image)
            elif isinstance(image, bytes):
                img_array = self.load_image_from_bytes(image)
            elif isinstance(image, np.ndarray):
                img_array = image.copy()
            else:
                logger.error(f"Tipo de imagen no soportado: {type(image)}")
                return None
            
            if img_array is None:
                return None
            
            # Redimensionar
            if target_size is None:
                target_size = self.target_size
            img_array = self.resize_image(img_array, target_size)
            
            # Normalizar si se solicita
            if normalize:
                img_array = self.normalize_image(img_array, mean, std)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento de imagen: {str(e)}")
            return None
    
    def preprocess_batch(self, images: List[Any],
                        target_size: Optional[Tuple[int, int]] = None,
                        normalize: bool = True,
                        mean: Optional[List[float]] = None,
                        std: Optional[List[float]] = None) -> np.ndarray:
        """
        Preprocesa un lote de imágenes.
        
        Args:
            images: Lista de imágenes (rutas, arrays o bytes)
            target_size: Tamaño objetivo
            normalize: Si normalizar las imágenes
            mean: Medias para normalización
            std: Desviaciones estándar para normalización
            
        Returns:
            np.ndarray: Lote de imágenes preprocesadas
        """
        processed_images = []
        
        for image in images:
            processed_img = self.preprocess_image(
                image, target_size, normalize, mean, std
            )
            
            if processed_img is not None:
                processed_images.append(processed_img)
            else:
                logger.warning("Imagen omitida debido a error en procesamiento")
        
        if not processed_images:
            logger.error("No se procesaron imágenes exitosamente")
            return np.array([])
        
        return np.array(processed_images)

def validate_image_format(file_path: Union[str, Path]) -> bool:
    """
    Valida si el archivo tiene un formato de imagen soportado.
    
    Args:
        file_path (Union[str, Path]): Ruta al archivo
        
    Returns:
        bool: True si el formato es soportado
    """
    from .config import SUPPORTED_IMAGE_FORMATS
    
    file_path = Path(file_path)
    file_extension = file_path.suffix.lower()
    
    return file_extension in SUPPORTED_IMAGE_FORMATS

def validate_image_size(file_path: Union[str, Path]) -> bool:
    """
    Valida si el tamaño del archivo está dentro del límite permitido.
    
    Args:
        file_path (Union[str, Path]): Ruta al archivo
        
    Returns:
        bool: True si el tamaño es válido
    """
    from .config import MAX_IMAGE_SIZE
    
    try:
        file_size = Path(file_path).stat().st_size
        return file_size <= MAX_IMAGE_SIZE
    except OSError:
        return False

def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    Obtiene información básica de una imagen.
    
    Args:
        image_path (Union[str, Path]): Ruta a la imagen
        
    Returns:
        dict: Información de la imagen
    """
    try:
        with Image.open(image_path) as img:
            info = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size': Path(image_path).stat().st_size
            }
            
        return info
        
    except Exception as e:
        logger.error(f"Error al obtener información de imagen: {str(e)}")
        return {}

def create_image_thumbnail(image_path: Union[str, Path],
                          thumbnail_size: Tuple[int, int] = (150, 150),
                          output_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """
    Crea una miniatura de una imagen.
    
    Args:
        image_path (Union[str, Path]): Ruta a la imagen original
        thumbnail_size (Tuple[int, int]): Tamaño de la miniatura
        output_path (Optional[Union[str, Path]]): Ruta de salida
        
    Returns:
        Optional[Path]: Ruta de la miniatura creada
    """
    try:
        image_path = Path(image_path)
        
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_thumb{image_path.suffix}"
        else:
            output_path = Path(output_path)
        
        with Image.open(image_path) as img:
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            img.save(output_path, optimize=True, quality=85)
        
        logger.info(f"Miniatura creada: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error al crear miniatura: {str(e)}")
        return None

def convert_to_tensor(image: np.ndarray, framework: str = 'tensorflow') -> Any:
    """
    Convierte una imagen numpy a tensor del framework especificado.
    
    Args:
        image (np.ndarray): Imagen como array numpy
        framework (str): Framework ('tensorflow' o 'pytorch')
        
    Returns:
        Any: Tensor del framework correspondiente
    """
    try:
        if framework.lower() == 'tensorflow':
            import tensorflow as tf
            # Agregar dimensión de batch si es necesario
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            return tf.constant(image, dtype=tf.float32)
            
        elif framework.lower() == 'pytorch':
            import torch
            # Cambiar orden de dimensiones para PyTorch (NCHW)
            if len(image.shape) == 3:
                image = np.transpose(image, (2, 0, 1))
                image = np.expand_dims(image, axis=0)
            elif len(image.shape) == 4:
                image = np.transpose(image, (0, 3, 1, 2))
            
            return torch.from_numpy(image).float()
            
        else:
            raise ValueError(f"Framework no soportado: {framework}")
            
    except ImportError as e:
        logger.error(f"Framework {framework} no está instalado: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error al convertir a tensor: {str(e)}")
        return None

# Instancia global del procesador de imágenes
image_processor = ImageProcessor()
