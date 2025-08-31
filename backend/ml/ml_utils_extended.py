"""
Utilidades extendidas para Machine Learning en CacaoScan.

Este módulo contiene utilidades adicionales para gestión de modelos,
validación de datasets, profiling de rendimiento y otras tareas avanzadas de ML.
"""

import logging
import numpy as np
from typing import Union, Tuple, List, Optional, Any, Dict
from pathlib import Path
import time
import json
from datetime import datetime

# Configurar logging
logger = logging.getLogger('ml')


class ModelManager:
    """
    Gestor de modelos ML para CacaoScan.
    """
    
    def __init__(self):
        """Inicializa el gestor de modelos."""
        from .config import MODELS_DIR
        self.models_dir = MODELS_DIR
        self._loaded_models = {}
    
    def list_available_models(self) -> dict:
        """
        Lista todos los modelos disponibles.
        
        Returns:
            dict: Información de modelos disponibles
        """
        models = {}
        
        # Buscar modelos PyTorch
        for model_file in self.models_dir.glob('*.pth'):
            try:
                import torch
                # Cargar solo metadatos sin cargar el modelo completo
                checkpoint = torch.load(model_file, map_location='cpu')
                
                models[model_file.stem] = {
                    'path': str(model_file),
                    'framework': 'pytorch',
                    'size_mb': model_file.stat().st_size / (1024 * 1024),
                    'modified': model_file.stat().st_mtime,
                    'config': checkpoint.get('model_config', {}),
                    'epoch': checkpoint.get('epoch', 0),
                    'loss': checkpoint.get('loss', 0.0)
                }
            except Exception as e:
                logger.warning(f"Error al leer modelo {model_file}: {e}")
                
        # Buscar modelos TensorFlow
        for model_file in self.models_dir.glob('*.h5'):
            models[model_file.stem] = {
                'path': str(model_file),
                'framework': 'tensorflow',
                'size_mb': model_file.stat().st_size / (1024 * 1024),
                'modified': model_file.stat().st_mtime
            }
            
        return models
    
    def load_model(self, model_name: str, device: str = 'auto'):
        """
        Carga un modelo específico.
        
        Args:
            model_name (str): Nombre del modelo
            device (str): Device donde cargar ('auto', 'cpu', 'cuda')
            
        Returns:
            Model object o None si hay error
        """
        if model_name in self._loaded_models:
            return self._loaded_models[model_name]
        
        model_path = self.models_dir / f"{model_name}.pth"
        
        if not model_path.exists():
            logger.error(f"Modelo no encontrado: {model_path}")
            return None
        
        try:
            if device == 'auto':
                try:
                    import torch
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                except ImportError:
                    device = 'cpu'
            
            from .vision_model import load_model
            model = load_model(str(model_path), device=device)
            
            self._loaded_models[model_name] = model
            logger.info(f"Modelo {model_name} cargado en {device}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error al cargar modelo {model_name}: {e}")
            return None
    
    def unload_model(self, model_name: str):
        """Descarga un modelo de memoria."""
        if model_name in self._loaded_models:
            del self._loaded_models[model_name]
            logger.info(f"Modelo {model_name} descargado de memoria")
    
    def clear_cache(self):
        """Limpia todos los modelos cargados."""
        self._loaded_models.clear()
        logger.info("Cache de modelos limpiado")


class DatasetValidator:
    """
    Validador de datasets para entrenamiento ML.
    """
    
    @staticmethod
    def validate_image_dataset(image_paths: List[Union[str, Path]], 
                             min_images: int = 10,
                             check_corrupted: bool = True) -> dict:
        """
        Valida un dataset de imágenes.
        
        Args:
            image_paths: Lista de rutas de imágenes
            min_images: Número mínimo de imágenes requeridas
            check_corrupted: Si verificar imágenes corruptas
            
        Returns:
            dict: Resultado de la validación
        """
        from .config import SUPPORTED_IMAGE_FORMATS, MAX_IMAGE_SIZE
        from PIL import Image
        
        results = {
            'valid': True,
            'total_images': len(image_paths),
            'valid_images': 0,
            'invalid_images': 0,
            'corrupted_images': [],
            'oversized_images': [],
            'unsupported_formats': [],
            'missing_files': [],
            'errors': []
        }
        
        if len(image_paths) < min_images:
            results['valid'] = False
            results['errors'].append(f"Insuficientes imágenes: {len(image_paths)} < {min_images}")
        
        for image_path in image_paths:
            path = Path(image_path)
            
            # Verificar que el archivo existe
            if not path.exists():
                results['missing_files'].append(str(path))
                results['invalid_images'] += 1
                continue
            
            # Verificar formato
            if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
                results['unsupported_formats'].append(str(path))
                results['invalid_images'] += 1
                continue
            
            # Verificar tamaño
            if path.stat().st_size > MAX_IMAGE_SIZE:
                results['oversized_images'].append(str(path))
                results['invalid_images'] += 1
                continue
            
            # Verificar si está corrupta
            if check_corrupted:
                try:
                    with Image.open(path) as img:
                        img.verify()
                    results['valid_images'] += 1
                except Exception:
                    results['corrupted_images'].append(str(path))
                    results['invalid_images'] += 1
            else:
                results['valid_images'] += 1
        
        if results['invalid_images'] > 0:
            results['valid'] = False
            
        return results
    
    @staticmethod
    def validate_training_data(images_data: List[dict]) -> dict:
        """
        Valida datos de entrenamiento con targets.
        
        Args:
            images_data: Lista de diccionarios con 'image_path' y 'targets'
            
        Returns:
            dict: Resultado de la validación
        """
        results = {
            'valid': True,
            'total_samples': len(images_data),
            'valid_samples': 0,
            'missing_targets': [],
            'invalid_targets': [],
            'target_statistics': {
                'width': {'min': float('inf'), 'max': float('-inf'), 'mean': 0},
                'height': {'min': float('inf'), 'max': float('-inf'), 'mean': 0},
                'thickness': {'min': float('inf'), 'max': float('-inf'), 'mean': 0},
                'weight': {'min': float('inf'), 'max': float('-inf'), 'mean': 0}
            },
            'errors': []
        }
        
        valid_targets = []
        
        for i, data in enumerate(images_data):
            # Verificar que tenga targets
            if 'targets' not in data or data['targets'] is None:
                results['missing_targets'].append(i)
                continue
            
            targets = data['targets']
            
            # Verificar que tenga 4 valores (width, height, thickness, weight)
            if len(targets) != 4:
                results['invalid_targets'].append(i)
                continue
            
            # Verificar que todos sean números positivos
            try:
                targets = [float(t) for t in targets]
                if any(t <= 0 for t in targets):
                    results['invalid_targets'].append(i)
                    continue
                
                valid_targets.append(targets)
                results['valid_samples'] += 1
                
            except (ValueError, TypeError):
                results['invalid_targets'].append(i)
                continue
        
        # Calcular estadísticas
        if valid_targets:
            valid_targets = np.array(valid_targets)
            target_names = ['width', 'height', 'thickness', 'weight']
            
            for i, name in enumerate(target_names):
                values = valid_targets[:, i]
                results['target_statistics'][name] = {
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values))
                }
        
        if results['valid_samples'] < len(images_data) * 0.8:  # Al menos 80% válido
            results['valid'] = False
            results['errors'].append(f"Muy pocos samples válidos: {results['valid_samples']}/{len(images_data)}")
        
        return results


class PerformanceProfiler:
    """
    Profiler de rendimiento para operaciones ML.
    """
    
    def __init__(self):
        """Inicializa el profiler."""
        self.timings = {}
        self.memory_usage = {}
    
    def profile_function(self, func_name: str):
        """
        Decorador para perfilar funciones.
        
        Args:
            func_name: Nombre de la función para el profiling
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    import psutil
                    
                    # Memoria antes
                    process = psutil.Process()
                    memory_before = process.memory_info().rss / 1024 / 1024  # MB
                    
                    # Tiempo de ejecución
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    # Memoria después
                    memory_after = process.memory_info().rss / 1024 / 1024  # MB
                    
                    # Guardar métricas
                    execution_time = end_time - start_time
                    memory_delta = memory_after - memory_before
                    
                    if func_name not in self.timings:
                        self.timings[func_name] = []
                        self.memory_usage[func_name] = []
                    
                    self.timings[func_name].append(execution_time)
                    self.memory_usage[func_name].append(memory_delta)
                    
                    logger.info(f"{func_name}: {execution_time:.3f}s, {memory_delta:+.1f}MB")
                    
                    return result
                except ImportError:
                    logger.warning("psutil no disponible para profiling")
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de rendimiento.
        
        Returns:
            dict: Estadísticas de rendimiento
        """
        stats = {}
        
        for func_name in self.timings:
            times = np.array(self.timings[func_name])
            memory = np.array(self.memory_usage[func_name])
            
            stats[func_name] = {
                'executions': len(times),
                'time': {
                    'mean': float(np.mean(times)),
                    'std': float(np.std(times)),
                    'min': float(np.min(times)),
                    'max': float(np.max(times)),
                    'total': float(np.sum(times))
                },
                'memory': {
                    'mean': float(np.mean(memory)),
                    'std': float(np.std(memory)),
                    'min': float(np.min(memory)),
                    'max': float(np.max(memory)),
                    'total': float(np.sum(memory))
                }
            }
        
        return stats
    
    def reset(self):
        """Resetea las estadísticas."""
        self.timings.clear()
        self.memory_usage.clear()


def setup_gpu_memory_limit(limit_mb: Optional[int] = None):
    """
    Configura límite de memoria GPU para PyTorch.
    
    Args:
        limit_mb: Límite en MB (None para usar toda la memoria disponible)
    """
    try:
        import torch
        
        if not torch.cuda.is_available():
            logger.info("CUDA no disponible, omitiendo configuración GPU")
            return
        
        if limit_mb is not None:
            # Configurar límite de memoria
            total_memory = torch.cuda.get_device_properties(0).total_memory
            fraction = (limit_mb * 1024 * 1024) / total_memory
            torch.cuda.set_per_process_memory_fraction(min(fraction, 1.0))
            logger.info(f"Límite de memoria GPU configurado: {limit_mb}MB")
        
        # Limpiar cache
        torch.cuda.empty_cache()
        
        # Información de GPU
        device_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
        
        logger.info(f"GPU: {device_name}, Memoria total: {total_memory:.0f}MB")
        
    except ImportError:
        logger.warning("PyTorch no está disponible para configuración GPU")
    except Exception as e:
        logger.error(f"Error configurando GPU: {e}")


def cleanup_temp_files(max_age_hours: int = 24):
    """
    Limpia archivos temporales antiguos.
    
    Args:
        max_age_hours: Edad máxima en horas para conservar archivos
    """
    from .config import DATA_DIR
    
    temp_dir = DATA_DIR / 'temp'
    if not temp_dir.exists():
        return
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned_files = 0
    
    for temp_file in temp_dir.rglob('*'):
        if temp_file.is_file() and temp_file.stat().st_mtime < cutoff_time:
            try:
                temp_file.unlink()
                cleaned_files += 1
            except OSError as e:
                logger.warning(f"No se pudo eliminar {temp_file}: {e}")
    
    logger.info(f"Archivos temporales limpiados: {cleaned_files}")


def export_model_info(model_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> dict:
    """
    Exporta información detallada de un modelo.
    
    Args:
        model_path: Ruta al modelo
        output_path: Ruta del archivo de salida (opcional)
        
    Returns:
        dict: Información del modelo
    """
    model_path = Path(model_path)
    
    try:
        if model_path.suffix == '.pth':
            try:
                import torch
                checkpoint = torch.load(model_path, map_location='cpu')
                
                info = {
                    'file_name': model_path.name,
                    'file_size_mb': model_path.stat().st_size / (1024 * 1024),
                    'framework': 'pytorch',
                    'model_config': checkpoint.get('model_config', {}),
                    'training_info': {
                        'epoch': checkpoint.get('epoch', 0),
                        'loss': checkpoint.get('loss', 0.0),
                        'additional_info': checkpoint.get('additional_info', {})
                    },
                    'exported_at': datetime.now().isoformat()
                }
            except ImportError:
                info = {
                    'file_name': model_path.name,
                    'file_size_mb': model_path.stat().st_size / (1024 * 1024),
                    'framework': 'pytorch',
                    'note': 'PyTorch no disponible para inspección detallada',
                    'exported_at': datetime.now().isoformat()
                }
            
        else:
            info = {
                'file_name': model_path.name,
                'file_size_mb': model_path.stat().st_size / (1024 * 1024),
                'framework': 'unknown',
                'exported_at': datetime.now().isoformat()
            }
        
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
            logger.info(f"Información del modelo exportada a {output_path}")
        
        return info
        
    except Exception as e:
        logger.error(f"Error exportando información del modelo: {e}")
        return {}


def validate_model_compatibility(model_path: Union[str, Path]) -> dict:
    """
    Valida la compatibilidad de un modelo con el sistema actual.
    
    Args:
        model_path: Ruta al modelo
        
    Returns:
        dict: Resultado de la validación
    """
    model_path = Path(model_path)
    result = {
        'compatible': True,
        'issues': [],
        'warnings': [],
        'model_info': {}
    }
    
    if not model_path.exists():
        result['compatible'] = False
        result['issues'].append(f"Archivo no encontrado: {model_path}")
        return result
    
    try:
        if model_path.suffix == '.pth':
            try:
                import torch
                checkpoint = torch.load(model_path, map_location='cpu')
                
                # Verificar estructura del checkpoint
                required_keys = ['model_state_dict', 'model_config']
                missing_keys = [key for key in required_keys if key not in checkpoint]
                
                if missing_keys:
                    result['warnings'].append(f"Claves faltantes en checkpoint: {missing_keys}")
                
                # Verificar configuración del modelo
                model_config = checkpoint.get('model_config', {})
                if not model_config:
                    result['warnings'].append("Configuración del modelo no encontrada")
                
                result['model_info'] = {
                    'framework': 'pytorch',
                    'config': model_config,
                    'epoch': checkpoint.get('epoch', 0),
                    'has_optimizer': 'optimizer_state_dict' in checkpoint
                }
                
            except ImportError:
                result['issues'].append("PyTorch no está instalado")
                result['compatible'] = False
            except Exception as e:
                result['issues'].append(f"Error cargando modelo PyTorch: {e}")
                result['compatible'] = False
        
        elif model_path.suffix == '.h5':
            try:
                import tensorflow as tf
                # Verificación básica para TensorFlow
                result['model_info'] = {
                    'framework': 'tensorflow',
                    'file_size': model_path.stat().st_size
                }
            except ImportError:
                result['issues'].append("TensorFlow no está instalado")
                result['compatible'] = False
        
        else:
            result['warnings'].append(f"Formato de modelo no reconocido: {model_path.suffix}")
    
    except Exception as e:
        result['issues'].append(f"Error validando modelo: {e}")
        result['compatible'] = False
    
    return result


# Instancias globales de utilidades extendidas
model_manager = ModelManager()
dataset_validator = DatasetValidator()
performance_profiler = PerformanceProfiler()
