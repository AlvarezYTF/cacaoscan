"""
Módulo de Machine Learning para CacaoScan.

Este módulo contiene todas las funcionalidades relacionadas con
el procesamiento de imágenes y análisis de granos de cacao usando
técnicas de machine learning.

Componentes principales:
- vision_model: Modelo CNN para predicción de características físicas
- data_preprocessing: Utilidades de preprocesamiento de datos e imágenes
- train_vision: Scripts de entrenamiento de modelos
- utils: Utilidades comunes para tareas de ML
- config: Configuraciones centralizadas del módulo ML
- predict: Funciones de inferencia y predicción
- evaluate: Herramientas de evaluación de modelos
"""

import logging
import os
from pathlib import Path

# Información del módulo
__version__ = "1.0.0"
__author__ = "CacaoScan Team"
__license__ = "MIT"

# Configurar logging para el módulo ML
logger = logging.getLogger('ml')

# Directorios del módulo ML
ML_ROOT = Path(__file__).parent
MODELS_DIR = ML_ROOT / 'models'
DATA_DIR = ML_ROOT / 'data'
LOGS_DIR = ML_ROOT / 'logs'

# Asegurar que los directorios existen
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / 'images').mkdir(exist_ok=True)
(DATA_DIR / 'processed').mkdir(exist_ok=True)
(DATA_DIR / 'temp').mkdir(exist_ok=True)

# Configuración por defecto
DEFAULT_CONFIG = {
    'image_size': (224, 224),
    'batch_size': 32,
    'device': 'auto',  # 'auto', 'cpu', 'cuda'
    'precision': 'float32',
}

def get_available_models():
    """
    Obtiene una lista de modelos disponibles en el directorio de modelos.
    
    Returns:
        dict: Diccionario con información de modelos disponibles
    """
    models = {}
    
    if MODELS_DIR.exists():
        for model_file in MODELS_DIR.glob('*.pth'):
            model_name = model_file.stem
            models[model_name] = {
                'path': str(model_file),
                'size': model_file.stat().st_size,
                'modified': model_file.stat().st_mtime
            }
        
        for model_file in MODELS_DIR.glob('*.h5'):
            model_name = model_file.stem
            models[model_name] = {
                'path': str(model_file),
                'size': model_file.stat().st_size,
                'modified': model_file.stat().st_mtime,
                'framework': 'tensorflow'
            }
    
    return models

def check_dependencies():
    """
    Verifica que las dependencias requeridas estén instaladas.
    
    Returns:
        dict: Estado de las dependencias
    """
    dependencies = {
        'torch': False,
        'torchvision': False,
        'tensorflow': False,
        'opencv': False,
        'PIL': False,
        'numpy': False,
        'sklearn': False,
        'pandas': False
    }
    
    # Verificar PyTorch
    try:
        import torch
        dependencies['torch'] = True
        logger.info(f"PyTorch {torch.__version__} disponible")
    except ImportError:
        logger.warning("PyTorch no está disponible")
    
    # Verificar TorchVision
    try:
        import torchvision
        dependencies['torchvision'] = True
        logger.info(f"TorchVision {torchvision.__version__} disponible")
    except ImportError:
        logger.warning("TorchVision no está disponible")
    
    # Verificar TensorFlow
    try:
        import tensorflow as tf
        dependencies['tensorflow'] = True
        logger.info(f"TensorFlow {tf.__version__} disponible")
    except ImportError:
        logger.warning("TensorFlow no está disponible")
    
    # Verificar OpenCV
    try:
        import cv2
        dependencies['opencv'] = True
        logger.info(f"OpenCV {cv2.__version__} disponible")
    except ImportError:
        logger.warning("OpenCV no está disponible")
    
    # Verificar PIL
    try:
        from PIL import Image
        dependencies['PIL'] = True
        logger.info("PIL/Pillow disponible")
    except ImportError:
        logger.warning("PIL/Pillow no está disponible")
    
    # Verificar NumPy
    try:
        import numpy as np
        dependencies['numpy'] = True
        logger.info(f"NumPy {np.__version__} disponible")
    except ImportError:
        logger.warning("NumPy no está disponible")
    
    # Verificar Scikit-learn
    try:
        import sklearn
        dependencies['sklearn'] = True
        logger.info(f"Scikit-learn {sklearn.__version__} disponible")
    except ImportError:
        logger.warning("Scikit-learn no está disponible")
    
    # Verificar Pandas
    try:
        import pandas as pd
        dependencies['pandas'] = True
        logger.info(f"Pandas {pd.__version__} disponible")
    except ImportError:
        logger.warning("Pandas no está disponible")
    
    return dependencies

def get_system_info():
    """
    Obtiene información del sistema para ML.
    
    Returns:
        dict: Información del sistema
    """
    info = {
        'ml_module_version': __version__,
        'ml_root': str(ML_ROOT),
        'models_dir': str(MODELS_DIR),
        'data_dir': str(DATA_DIR),
        'available_models': list(get_available_models().keys()),
        'dependencies': check_dependencies()
    }
    
    # Información de GPU si PyTorch está disponible
    try:
        import torch
        info['cuda_available'] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info['cuda_device_count'] = torch.cuda.device_count()
            info['cuda_device_name'] = torch.cuda.get_device_name(0)
            info['cuda_memory'] = torch.cuda.get_device_properties(0).total_memory
    except ImportError:
        info['cuda_available'] = False
    
    return info

# Importaciones opcionales de submódulos
try:
    from .config import *
    logger.info("Configuración del módulo ML cargada")
except ImportError as e:
    logger.warning(f"No se pudo cargar la configuración ML: {e}")

try:
    from .utils import image_processor
    logger.info("Utilidades ML cargadas")
except ImportError as e:
    logger.warning(f"No se pudieron cargar las utilidades ML: {e}")

# Funciones de conveniencia exportadas
__all__ = [
    '__version__',
    '__author__',
    '__license__',
    'get_available_models',
    'check_dependencies', 
    'get_system_info',
    'DEFAULT_CONFIG',
    'ML_ROOT',
    'MODELS_DIR',
    'DATA_DIR',
    'LOGS_DIR'
]

# Inicialización del módulo
logger.info(f"Módulo ML CacaoScan v{__version__} inicializado")
logger.info(f"Directorio raíz: {ML_ROOT}")

# Verificar dependencias críticas al importar
deps = check_dependencies()
critical_deps = ['numpy', 'PIL']
missing_critical = [dep for dep in critical_deps if not deps[dep]]

if missing_critical:
    logger.error(f"Dependencias críticas faltantes: {missing_critical}")
    raise ImportError(f"Dependencias críticas no encontradas: {missing_critical}")

logger.info("Módulo ML inicializado correctamente")
