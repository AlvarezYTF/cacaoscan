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
    },
    'vision_model': {
        'model_path': MODELS_DIR / 'vision_model.pth',
        'model_type': 'pytorch_vision',
        'input_shape': (3, 224, 224),
        'outputs': ['width', 'height', 'thickness', 'weight'],
        'output_units': ['mm', 'mm', 'mm', 'g'],
        'model_class': 'CacaoVisionModel'
    },
    'weight_regression': {
        'model_path': MODELS_DIR / 'weight_regression.pkl',
        'model_type': 'sklearn_regression',
        'inputs': ['width', 'height', 'thickness'],
        'input_units': ['mm', 'mm', 'mm'],
        'outputs': ['weight'],
        'output_units': ['g'],
        'model_class': 'WeightRegressionModel',
        'algorithms': ['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting', 'svr']
    },
    'yolo_weight_model': {
        'model_path': MODELS_DIR / 'weight_predictor_yolo' / 'weight_yolo.pt',
        'model_type': 'yolo_v8',
        'input_shape': (640, 640, 3),
        'classes': ['cacao_grain'],
        'confidence_threshold': 0.5,
        'iou_threshold': 0.45,
        'outputs': ['peso_estimado', 'altura_mm', 'ancho_mm', 'grosor_mm'],
        'output_units': ['g', 'mm', 'mm', 'mm'],
        'model_class': 'CacaoYOLOModel',
        'calibration_file': MODELS_DIR / 'weight_predictor_yolo' / 'calibration.json',
        'integrated_model_file': MODELS_DIR / 'weight_predictor_yolo' / 'integrated_weight_model.json',
        'training_config': {
            'epochs': 100,
            'batch_size': 16,
            'learning_rate': 0.01,
            'patience': 20,
            'device': 'auto'
        }
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

# Configuración específica para YOLOv8
YOLO_CONFIG = {
    'model_sizes': ['n', 's', 'm', 'l', 'x'],
    'default_model_size': 'n',
    'input_size': 640,
    'confidence_threshold': 0.5,
    'iou_threshold': 0.45,
    'max_detections': 100,
    'agnostic_nms': False,
    'augment': False,
    'visualize': False,
    'save_txt': False,
    'save_conf': False,
    'save_crop': False,
    'show_labels': True,
    'show_conf': True,
    'line_width': 3,
    'box': True,
    'labels': True,
    'conf': True,
    'device': 'auto',
    'half': False,
    'dnn': False,
    'data': None,
    'imgsz': 640,
    'rect': False,
    'resume': False,
    'nosave': False,
    'noval': False,
    'noaug': False,
    'noplots': False,
    'evolve': None,
    'bucket': '',
    'cache': None,
    'image_weights': False,
    'multi_scale': False,
    'single_cls': False,
    'optimizer': 'auto',
    'sync_bn': False,
    'workers': 8,
    'project': 'runs/detect',
    'name': 'exp',
    'exist_ok': False,
    'quad': False,
    'cos_lr': False,
    'label_smoothing': 0.0,
    'patience': 100,
    'freeze': None,
    'lr0': 0.01,
    'lrf': 0.01,
    'momentum': 0.937,
    'weight_decay': 0.0005,
    'warmup_epochs': 3.0,
    'warmup_momentum': 0.8,
    'warmup_bias_lr': 0.1,
    'box': 7.5,
    'cls': 0.5,
    'dfl': 1.5,
    'pose': 12.0,
    'kobj': 1.0,
    'label_smoothing': 0.0,
    'nbs': 64,
    'overlap_mask': True,
    'mask_ratio': 4,
    'dropout': 0.0,
    'val': True,
    'plots': True,
    'verbose': True,
    'seed': 42,
    'deterministic': True,
    'single_cls': False,
    'rect': False,
    'cos_lr': False,
    'close_mosaic': 10,
    'resume': False,
    'amp': True,
    'fraction': 1.0,
    'profile': False,
    'freeze': None,
    'multi_scale': False
}

# Configuración de calibración para YOLOv8
YOLO_CALIBRATION = {
    'default_pixels_per_mm': 10.0,
    'reference_object_size_mm': 20.0,
    'calibration_methods': ['manual', 'automatic', 'reference_object'],
    'min_calibration_points': 3,
    'max_calibration_error': 0.1,  # 10% error máximo
    'calibration_update_frequency': 'monthly'
}

# Configuración de predicción de peso para YOLOv8
YOLO_WEIGHT_PREDICTION = {
    'density_g_per_cm3': 1.0,  # Densidad promedio del cacao
    'shape_factor': 0.8,  # Factor de corrección por forma irregular
    'min_weight_g': 0.5,
    'max_weight_g': 3.0,
    'weight_formula': 'weight = density * volume * shape_factor',
    'volume_formula': 'volume = (4/3) * π * (width/2) * (height/2) * (thickness/2)',
    'confidence_weighting': True,
    'ensemble_with_other_models': True
}

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

# Configuración de entrenamiento
TRAINING_CONFIG = {
    'default_epochs': 100,
    'default_batch_size': 16,
    'default_learning_rate': 1e-3,
    'default_optimizer': 'adam',
    'default_scheduler': 'reduce_on_plateau',
    'early_stopping_patience': 15,
    'save_checkpoint_every': 10,
    'validation_split': 0.2,
    'augmentation_enabled': True,
    'gradient_clipping': 1.0,
    'weight_decay': 1e-4
}

# Configuración de hardware
HARDWARE_CONFIG = {
    'use_gpu': True,
    'gpu_memory_limit': 4096,  # MB
    'num_workers': 2,  # Para DataLoader
    'pin_memory': True,
    'mixed_precision': False,  # Para entrenamiento con AMP
    'cudnn_benchmark': True
}

# Configuración de validación de datos
DATA_VALIDATION_CONFIG = {
    'min_dataset_size': 50,
    'max_image_size_mb': 10,
    'required_image_formats': SUPPORTED_IMAGE_FORMATS,
    'check_image_corruption': True,
    'min_image_dimensions': (32, 32),
    'max_image_dimensions': (4096, 4096),
    'allow_grayscale_conversion': True
}

# Configuración de métricas de evaluación
EVALUATION_METRICS = {
    'regression_metrics': ['mae', 'mse', 'rmse', 'mape', 'r2'],
    'classification_metrics': ['accuracy', 'precision', 'recall', 'f1'],
    'custom_metrics': ['aspect_ratio_error', 'volume_estimation_error'],
    'tolerance_thresholds': {
        'width': 0.5,  # mm
        'height': 0.5,  # mm  
        'thickness': 0.3,  # mm
        'weight': 0.05  # g
    }
}

# Configuración de modelos por defecto
DEFAULT_MODEL_PARAMS = {
    'vision_model': {
        'input_channels': 3,
        'num_outputs': 4,
        'dropout_rate': 0.5,
        'activation': 'relu',
        'batch_norm': True,
        'weight_init': 'kaiming'
    },
    'classifier_model': {
        'num_classes': 4,
        'dropout_rate': 0.3,
        'use_pretrained': True,
        'fine_tune_layers': 2
    }
}

# Configuración de logging detallado
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_training_metrics': True,
    'log_prediction_times': True,
    'log_memory_usage': True,
    'tensorboard_enabled': True,
    'save_model_graphs': True
}

# Configuración de seguridad y límites
SECURITY_CONFIG = {
    'max_file_uploads_per_hour': 100,
    'allowed_file_extensions': SUPPORTED_IMAGE_FORMATS,
    'scan_uploaded_files': True,
    'quarantine_suspicious_files': True,
    'max_prediction_requests_per_minute': 30
}

# Configuración de API endpoints
API_CONFIG = {
    'pagination_size': 20,
    'max_batch_prediction_size': 10,
    'request_timeout': 30,  # segundos
    'enable_model_info_endpoint': True,
    'enable_metrics_endpoint': True,
    'enable_training_endpoint': False  # Solo en desarrollo
}

# Configuración del servicio de predicción
PREDICTION_SERVICE_CONFIG = {
    'enable_caching': True,
    'cache_timeout': 1800,  # 30 minutos
    'default_device': 'auto',
    'confidence_threshold': 0.7,
    'max_cache_size': 1000,
    'enable_performance_profiling': True,
    'warmup_on_startup': True,
    'critical_models': ['vision_model', 'weight_regression']
}

# Configuración del gestor de modelos
MODEL_MANAGER_CONFIG = {
    'max_models_in_memory': 5,
    'model_timeout': 3600,  # 1 hora
    'auto_reload': False,
    'enable_health_checks': True,
    'warmup_critical_models': True,
    'performance_monitoring': True
}

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


def get_config_value(config_dict: dict, key: str, default=None):
    """
    Obtiene un valor de configuración de forma segura.
    
    Args:
        config_dict (dict): Diccionario de configuración
        key (str): Clave a buscar
        default: Valor por defecto si no se encuentra
        
    Returns:
        Valor de configuración o default
    """
    return config_dict.get(key, default)


def validate_config():
    """
    Valida la configuración del módulo ML.
    
    Returns:
        dict: Resultado de la validación
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validar directorios
    required_dirs = [MODELS_DIR, DATA_DIR, IMAGES_DIR]
    for directory in required_dirs:
        if not directory.exists():
            validation_result['errors'].append(f"Directorio no encontrado: {directory}")
            validation_result['valid'] = False
    
    # Validar configuración de modelos
    for model_name, config in MODEL_CONFIGS.items():
        model_path = config.get('model_path')
        if model_path and not model_path.exists():
            validation_result['warnings'].append(f"Modelo no encontrado: {model_path}")
    
    # Validar configuración de imagen
    image_size = IMAGE_PREPROCESSING.get('target_size')
    if not isinstance(image_size, tuple) or len(image_size) != 2:
        validation_result['errors'].append("target_size debe ser una tupla de 2 elementos")
        validation_result['valid'] = False
    
    # Validar configuración de entrenamiento
    batch_size = TRAINING_CONFIG.get('default_batch_size', 0)
    if batch_size <= 0:
        validation_result['errors'].append("batch_size debe ser mayor que 0")
        validation_result['valid'] = False
    
    return validation_result


def get_device_config():
    """
    Obtiene la configuración óptima del device basada en hardware disponible.
    
    Returns:
        dict: Configuración del device
    """
    device_config = {
        'device': 'cpu',
        'cuda_available': False,
        'num_gpus': 0,
        'gpu_memory': 0,
        'recommended_batch_size': TRAINING_CONFIG['default_batch_size']
    }
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_config['device'] = 'cuda'
            device_config['cuda_available'] = True
            device_config['num_gpus'] = torch.cuda.device_count()
            
            if device_config['num_gpus'] > 0:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                device_config['gpu_memory'] = gpu_memory
                
                # Ajustar batch size basado en memoria GPU
                if gpu_memory >= 8:
                    device_config['recommended_batch_size'] = 32
                elif gpu_memory >= 4:
                    device_config['recommended_batch_size'] = 16
                else:
                    device_config['recommended_batch_size'] = 8
        
    except ImportError:
        pass
    
    return device_config


def get_training_config_for_dataset_size(dataset_size: int) -> dict:
    """
    Ajusta la configuración de entrenamiento basada en el tamaño del dataset.
    
    Args:
        dataset_size (int): Tamaño del dataset
        
    Returns:
        dict: Configuración ajustada
    """
    config = TRAINING_CONFIG.copy()
    
    # Ajustar épocas basado en tamaño del dataset
    if dataset_size < 100:
        config['default_epochs'] = 200
        config['early_stopping_patience'] = 30
    elif dataset_size < 500:
        config['default_epochs'] = 150
        config['early_stopping_patience'] = 20
    elif dataset_size < 1000:
        config['default_epochs'] = 100
        config['early_stopping_patience'] = 15
    else:
        config['default_epochs'] = 80
        config['early_stopping_patience'] = 10
    
    # Ajustar batch size
    if dataset_size < 50:
        config['default_batch_size'] = 8
    elif dataset_size < 200:
        config['default_batch_size'] = 16
    else:
        config['default_batch_size'] = 32
    
    return config


def export_config_to_json(output_path: Path = None) -> dict:
    """
    Exporta toda la configuración a un archivo JSON.
    
    Args:
        output_path (Path, optional): Ruta del archivo de salida
        
    Returns:
        dict: Configuración exportada
    """
    import json
    from datetime import datetime
    
    # Preparar configuración para exportación
    config_export = {
        'exported_at': datetime.now().isoformat(),
        'version': '1.0.0',
        'model_configs': {},
        'image_preprocessing': IMAGE_PREPROCESSING.copy(),
        'data_augmentation': DATA_AUGMENTATION.copy(),
        'training_config': TRAINING_CONFIG.copy(),
        'hardware_config': HARDWARE_CONFIG.copy(),
        'data_validation_config': DATA_VALIDATION_CONFIG.copy(),
        'evaluation_metrics': EVALUATION_METRICS.copy(),
        'logging_config': LOGGING_CONFIG.copy(),
        'security_config': SECURITY_CONFIG.copy(),
        'api_config': API_CONFIG.copy()
    }
    
    # Convertir paths a strings para JSON
    for model_name, config in MODEL_CONFIGS.items():
        config_export['model_configs'][model_name] = {
            k: str(v) if isinstance(v, Path) else v 
            for k, v in config.items()
        }
    
    if output_path:
        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_export, f, indent=2, ensure_ascii=False)
    
    return config_export


def load_config_from_json(config_path: Path):
    """
    Carga configuración desde un archivo JSON.
    
    Args:
        config_path (Path): Ruta al archivo de configuración
    """
    import json
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Actualizar configuraciones globales
        if 'training_config' in config_data:
            TRAINING_CONFIG.update(config_data['training_config'])
        
        if 'hardware_config' in config_data:
            HARDWARE_CONFIG.update(config_data['hardware_config'])
        
        # Más actualizaciones según sea necesario
        
    except Exception as e:
        print(f"Error cargando configuración desde {config_path}: {e}")


def get_environment_config():
    """
    Obtiene configuración basada en variables de entorno.
    
    Returns:
        dict: Configuración de entorno
    """
    import os
    
    env_config = {
        'debug_mode': os.getenv('ML_DEBUG', 'False').lower() == 'true',
        'gpu_enabled': os.getenv('ML_USE_GPU', 'True').lower() == 'true',
        'log_level': os.getenv('ML_LOG_LEVEL', 'INFO'),
        'batch_size': int(os.getenv('ML_BATCH_SIZE', TRAINING_CONFIG['default_batch_size'])),
        'num_workers': int(os.getenv('ML_NUM_WORKERS', HARDWARE_CONFIG['num_workers'])),
        'cache_enabled': os.getenv('ML_CACHE_ENABLED', 'True').lower() == 'true'
    }
    
    return env_config


# Validar configuración al importar
validation_result = validate_config()
if not validation_result['valid']:
    print(f"ADVERTENCIA: Errores en configuración ML: {validation_result['errors']}")
if validation_result['warnings']:
    print(f"ADVERTENCIA: {validation_result['warnings']}")

# Obtener información del device
DEVICE_CONFIG = get_device_config()

# Aplicar configuración de entorno
ENV_CONFIG = get_environment_config()