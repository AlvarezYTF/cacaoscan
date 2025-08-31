"""
Configuraciones para el módulo de Machine Learning.

Este archivo contiene todas las constantes y configuraciones
necesarias para el procesamiento de imágenes y modelos ML.
"""

import os
from pathlib import Path
from django.conf import settings

# Rutas base
BASE_DIR = Path(__file__).resolve().parent
ML_BASE_DIR = BASE_DIR
MODELS_DIR = ML_BASE_DIR / 'models'
DATA_DIR = ML_BASE_DIR / 'data'
IMAGES_DIR = DATA_DIR / 'images'

# Configuración de modelos
MODEL_CONFIGS = {
    'cacao_classifier': {
        'model_path': MODELS_DIR / 'modelo_cacao.h5',
        'model_type': 'tensorflow',  # 'tensorflow' o 'pytorch'
        'input_shape': (224, 224, 3),
        'classes': [
            'grano_sano',
            'grano_defectuoso',
            'grano_fermentado',
            'grano_mohoso'
        ],
        'confidence_threshold': 0.7
    },
    'cacao_pytorch': {
        'model_path': MODELS_DIR / 'modelo_cacao.pth',
        'model_type': 'pytorch',
        'input_shape': (3, 224, 224),
        'classes': [
            'grano_sano',
            'grano_defectuoso',
            'grano_fermentado',
            'grano_mohoso'
        ],
        'confidence_threshold': 0.7
    }
}

# Configuración de preprocesamiento de imágenes
IMAGE_PREPROCESSING = {
    'target_size': (224, 224),
    'color_mode': 'rgb',
    'normalize': True,
    'mean': [0.485, 0.456, 0.406],  # ImageNet means
    'std': [0.229, 0.224, 0.225],   # ImageNet stds
    'data_format': 'channels_last'  # 'channels_last' o 'channels_first'
}

# Configuración de augmentación de datos
DATA_AUGMENTATION = {
    'rotation_range': 20,
    'width_shift_range': 0.2,
    'height_shift_range': 0.2,
    'horizontal_flip': True,
    'vertical_flip': False,
    'zoom_range': 0.2,
    'brightness_range': [0.8, 1.2],
    'fill_mode': 'nearest'
}

# Formatos de imagen soportados
SUPPORTED_IMAGE_FORMATS = [
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
]

# Tamaño máximo de archivo (en bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

# Configuración de logging para ML
ML_LOG_LEVEL = 'INFO'
ML_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configuración de GPU/CPU
USE_GPU = True
GPU_MEMORY_LIMIT = 4096  # MB

# Configuración de batch processing
BATCH_SIZE = 32
MAX_CONCURRENT_PREDICTIONS = 5

# Métricas y umbrales
QUALITY_THRESHOLDS = {
    'excellent': 0.9,
    'good': 0.75,
    'fair': 0.6,
    'poor': 0.4
}

# Configuración de cache
CACHE_PREDICTIONS = True
CACHE_TIMEOUT = 3600  # 1 hora en segundos

# Rutas de modelos pre-entrenados
PRETRAINED_MODELS = {
    'resnet50': 'resnet50_imagenet',
    'efficientnet': 'efficientnet_b0',
    'mobilenet': 'mobilenet_v2'
}

def get_model_path(model_name: str) -> Path:
    """
    Obtiene la ruta completa del modelo especificado.
    
    Args:
        model_name (str): Nombre del modelo en MODEL_CONFIGS
        
    Returns:
        Path: Ruta completa al archivo del modelo
    """
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Modelo '{model_name}' no encontrado en configuración")
    
    return MODEL_CONFIGS[model_name]['model_path']

def get_model_config(model_name: str) -> dict:
    """
    Obtiene la configuración completa del modelo especificado.
    
    Args:
        model_name (str): Nombre del modelo en MODEL_CONFIGS
        
    Returns:
        dict: Configuración del modelo
    """
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Modelo '{model_name}' no encontrado en configuración")
    
    return MODEL_CONFIGS[model_name].copy()

def ensure_directories():
    """
    Crea los directorios necesarios si no existen.
    """
    directories = [MODELS_DIR, DATA_DIR, IMAGES_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Inicializar directorios al importar el módulo
ensure_directories()