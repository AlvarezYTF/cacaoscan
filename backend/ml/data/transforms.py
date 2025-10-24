"""
Transformaciones de imágenes para el procesamiento de cacao.
"""
import numpy as np
from PIL import Image, ImageOps
from typing import Tuple, Optional
import cv2


def resize_with_padding(
    image: np.ndarray,
    target_size: Tuple[int, int] = (640, 640),
    fill_color: Tuple[int, int, int] = (0, 0, 0)
) -> np.ndarray:
    """
    Redimensiona una imagen manteniendo la proporción y añadiendo padding.
    
    Args:
        image: Imagen como array numpy
        target_size: Tamaño objetivo (width, height)
        target_size: Tamaño objetivo (width, height)
        fill_color: Color de relleno para el padding
        
    Returns:
        Imagen redimensionada con padding
    """
    h, w = image.shape[:2]
    target_w, target_h = target_size
    
    # Calcular la escala para mantener la proporción
    scale = min(target_w / w, target_h / h)
    
    # Calcular el nuevo tamaño
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Redimensionar
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    # Crear imagen con padding
    padded = np.full((target_h, target_w, 3), fill_color, dtype=np.uint8)
    
    # Calcular posición para centrar
    y_offset = (target_h - new_h) // 2
    x_offset = (target_w - new_w) // 2
    
    # Colocar imagen redimensionada en el centro
    padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return padded


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normaliza una imagen al rango [0, 1].
    
    Args:
        image: Imagen como array numpy
        
    Returns:
        Imagen normalizada
    """
    return image.astype(np.float32) / 255.0


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """
    Desnormaliza una imagen del rango [0, 1] a [0, 255].
    
    Args:
        image: Imagen normalizada
        
    Returns:
        Imagen desnormalizada
    """
    return (image * 255).astype(np.uint8)


def apply_mask_to_image(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Aplica una máscara a una imagen.
    
    Args:
        image: Imagen original
        mask: Máscara binaria
        
    Returns:
        Imagen con máscara aplicada
    """
    if len(image.shape) == 3:
        # Imagen a color
        masked = image.copy()
        masked[mask == 0] = 0
        return masked
    else:
        # Imagen en escala de grises
        return image * mask


def crop_with_mask(
    image: np.ndarray,
    mask: np.ndarray,
    padding: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Recorta una imagen usando una máscara con padding adicional.
    
    Args:
        image: Imagen original
        mask: Máscara binaria
        padding: Padding adicional en píxeles
        
    Returns:
        Tuple con (imagen recortada, máscara recortada)
    """
    # Encontrar bounding box de la máscara
    coords = np.where(mask > 0)
    if len(coords[0]) == 0:
        # No hay píxeles activos en la máscara
        return image, mask
    
    y_min, y_max = coords[0].min(), coords[0].max()
    x_min, x_max = coords[1].min(), coords[1].max()
    
    # Añadir padding
    h, w = image.shape[:2]
    y_min = max(0, y_min - padding)
    y_max = min(h, y_max + padding)
    x_min = max(0, x_min - padding)
    x_max = min(w, x_max + padding)
    
    # Recortar imagen y máscara
    cropped_image = image[y_min:y_max, x_min:x_max]
    cropped_mask = mask[y_min:y_max, x_min:x_max]
    
    return cropped_image, cropped_mask


def create_transparent_crop(
    image: np.ndarray,
    mask: np.ndarray,
    padding: int = 10
) -> np.ndarray:
    """
    Crea un recorte con transparencia estilo iPhone.
    
    Args:
        image: Imagen original
        mask: Máscara binaria
        padding: Padding adicional
        
    Returns:
        Imagen recortada con canal alpha
    """
    # Recortar imagen y máscara
    cropped_image, cropped_mask = crop_with_mask(image, mask, padding)
    
    # Crear imagen RGBA
    if len(cropped_image.shape) == 3:
        # Imagen a color
        rgba_image = np.zeros((cropped_image.shape[0], cropped_image.shape[1], 4), dtype=np.uint8)
        rgba_image[:, :, :3] = cropped_image
        rgba_image[:, :, 3] = cropped_mask * 255
    else:
        # Imagen en escala de grises
        rgba_image = np.zeros((cropped_image.shape[0], cropped_image.shape[1], 4), dtype=np.uint8)
        rgba_image[:, :, 0] = cropped_image  # R
        rgba_image[:, :, 1] = cropped_image  # G
        rgba_image[:, :, 2] = cropped_image  # B
        rgba_image[:, :, 3] = cropped_mask * 255  # Alpha
    
    return rgba_image


def resize_crop_to_square(
    image: np.ndarray,
    target_size: int = 512,
    fill_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
) -> np.ndarray:
    """
    Redimensiona un recorte a un cuadrado manteniendo la proporción.
    
    Args:
        image: Imagen RGBA
        target_size: Tamaño del cuadrado objetivo
        fill_color: Color de relleno (RGBA)
        
    Returns:
        Imagen cuadrada con transparencia
    """
    h, w = image.shape[:2]
    
    # Calcular la escala para mantener la proporción
    scale = min(target_size / w, target_size / h)
    
    # Calcular el nuevo tamaño
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Redimensionar
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    # Crear imagen cuadrada
    square = np.full((target_size, target_size, 4), fill_color, dtype=np.uint8)
    
    # Calcular posición para centrar
    y_offset = (target_size - new_h) // 2
    x_offset = (target_size - new_w) // 2
    
    # Colocar imagen redimensionada en el centro
    square[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return square


def validate_crop_quality(
    image: np.ndarray,
    mask: np.ndarray,
    min_area_ratio: float = 0.01,
    max_aspect_ratio: float = 5.0
) -> bool:
    """
    Valida la calidad de un recorte.
    
    Args:
        image: Imagen original
        mask: Máscara binaria
        min_area_ratio: Proporción mínima de área de la máscara respecto a la imagen
        max_aspect_ratio: Proporción máxima de aspecto del bounding box
        
    Returns:
        True si el recorte es válido, False en caso contrario
    """
    # Calcular área de la máscara
    mask_area = np.sum(mask > 0)
    total_area = mask.size
    
    # Verificar área mínima
    if mask_area / total_area < min_area_ratio:
        return False
    
    # Calcular bounding box
    coords = np.where(mask > 0)
    if len(coords[0]) == 0:
        return False
    
    y_min, y_max = coords[0].min(), coords[0].max()
    x_min, x_max = coords[1].min(), coords[1].max()
    
    # Calcular proporción de aspecto
    bbox_width = x_max - x_min
    bbox_height = y_max - y_min
    
    if bbox_height == 0:
        return False
    
    aspect_ratio = max(bbox_width / bbox_height, bbox_height / bbox_width)
    
    # Verificar proporción de aspecto
    if aspect_ratio > max_aspect_ratio:
        return False
    
    return True
