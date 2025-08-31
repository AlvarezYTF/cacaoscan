"""
Gestor de modelos para CacaoScan con patrón singleton.

Este módulo gestiona la carga y administración de todos los modelos ML
usando lazy loading y singleton pattern para optimizar el rendimiento.
"""

import os
import logging
import threading
from typing import Optional, Dict, Any, Union
from pathlib import Path
import time

# Configurar Django si no está configurado
import django
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from .config import MODEL_CONFIGS, get_model_path, get_model_config
from .utils import performance_profiler

# Configurar logging
logger = logging.getLogger('ml')


class ModelManagerSingleton:
    """
    Gestor singleton para la carga y administración de modelos ML.
    
    Implementa lazy loading para cargar modelos solo cuando se necesiten
    y asegurar que cada modelo se cargue una sola vez en memoria.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementación del patrón singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelManagerSingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de modelos (solo una vez)."""
        if self._initialized:
            return
        
        # Almacén de modelos cargados
        self._models = {}
        self._model_metadata = {}
        self._loading_locks = {}
        
        # Configuración
        self.auto_reload = False
        self.max_models_in_memory = 5
        self.model_timeout = 3600  # 1 hora antes de descargar modelos no usados
        
        # Estadísticas
        self.load_times = {}
        self.access_counts = {}
        self.last_access_times = {}
        
        # Inicializar locks para cada modelo
        for model_name in MODEL_CONFIGS.keys():
            self._loading_locks[model_name] = threading.Lock()
        
        self._initialized = True
        logger.info("ModelManager inicializado como singleton")
    
    def get_vision_model(self, device: str = 'auto') -> Optional[Any]:
        """
        Obtiene el modelo de visión CNN.
        
        Args:
            device (str): Device donde cargar el modelo ('auto', 'cpu', 'cuda')
            
        Returns:
            CacaoVisionModel o None si hay error
        """
        return self._get_model('vision_model', device=device)
    
    def get_regression_model(self) -> Optional[Any]:
        """
        Obtiene el modelo de regresión de peso.
        
        Returns:
            WeightRegressionModel o None si hay error
        """
        return self._get_model('weight_regression')
    
    def get_classifier_model(self, model_type: str = 'cacao_pytorch', device: str = 'auto') -> Optional[Any]:
        """
        Obtiene el modelo de clasificación.
        
        Args:
            model_type (str): Tipo de modelo ('cacao_pytorch' o 'cacao_classifier')
            device (str): Device donde cargar el modelo
            
        Returns:
            Modelo de clasificación o None si hay error
        """
        return self._get_model(model_type, device=device)
    
    def _get_model(self, model_name: str, **kwargs) -> Optional[Any]:
        """
        Método interno para obtener un modelo con lazy loading.
        
        Args:
            model_name (str): Nombre del modelo en MODEL_CONFIGS
            **kwargs: Argumentos adicionales para la carga del modelo
            
        Returns:
            Modelo cargado o None si hay error
        """
        # Verificar si el modelo ya está cargado
        if model_name in self._models:
            self._update_access_stats(model_name)
            logger.debug(f"Modelo {model_name} obtenido desde cache")
            return self._models[model_name]
        
        # Cargar modelo con lock para evitar cargas múltiples
        with self._loading_locks[model_name]:
            # Double-check locking pattern
            if model_name in self._models:
                self._update_access_stats(model_name)
                return self._models[model_name]
            
            # Cargar modelo
            model = self._load_model(model_name, **kwargs)
            
            if model is not None:
                self._models[model_name] = model
                self._update_access_stats(model_name)
                self._cleanup_old_models()
                logger.info(f"Modelo {model_name} cargado exitosamente")
            
            return model
    
    @performance_profiler.profile_function("model_loading")
    def _load_model(self, model_name: str, **kwargs) -> Optional[Any]:
        """
        Carga un modelo desde archivo.
        
        Args:
            model_name (str): Nombre del modelo
            **kwargs: Argumentos adicionales
            
        Returns:
            Modelo cargado o None si hay error
        """
        start_time = time.time()
        
        try:
            # Obtener configuración del modelo
            if model_name not in MODEL_CONFIGS:
                logger.error(f"Modelo {model_name} no encontrado en configuración")
                return None
            
            config = get_model_config(model_name)
            model_path = config['model_path']
            model_type = config['model_type']
            
            # Verificar que el archivo existe
            if not model_path.exists():
                logger.error(f"Archivo de modelo no encontrado: {model_path}")
                return None
            
            # Cargar según el tipo de modelo
            model = self._load_model_by_type(model_type, model_path, config, **kwargs)
            
            if model is not None:
                # Guardar metadata
                load_time = time.time() - start_time
                self.load_times[model_name] = load_time
                self._model_metadata[model_name] = {
                    'config': config,
                    'load_time': load_time,
                    'file_size': model_path.stat().st_size,
                    'loaded_at': time.time()
                }
                
                logger.info(f"Modelo {model_name} cargado en {load_time:.2f}s")
            
            return model
            
        except Exception as e:
            logger.error(f"Error cargando modelo {model_name}: {e}")
            return None
    
    def _load_model_by_type(self, model_type: str, model_path: Path, 
                           config: Dict, **kwargs) -> Optional[Any]:
        """
        Carga un modelo basado en su tipo.
        
        Args:
            model_type (str): Tipo del modelo
            model_path (Path): Ruta al archivo del modelo
            config (Dict): Configuración del modelo
            **kwargs: Argumentos adicionales
            
        Returns:
            Modelo cargado o None si hay error
        """
        try:
            if model_type == 'pytorch_vision':
                # Cargar modelo de visión PyTorch
                from .vision_model import load_model
                device = kwargs.get('device', 'auto')
                return load_model(str(model_path), device=device)
            
            elif model_type == 'sklearn_regression':
                # Cargar modelo de regresión sklearn
                from .regression_model import WeightRegressionModel
                return WeightRegressionModel.load_model(model_path)
            
            elif model_type == 'pytorch':
                # Cargar modelo PyTorch general
                import torch
                device = kwargs.get('device', 'auto')
                if device == 'auto':
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                
                checkpoint = torch.load(model_path, map_location=device)
                
                # Esto requerirá implementación específica según el tipo de modelo
                logger.warning(f"Carga de modelo PyTorch general no implementada completamente")
                return checkpoint
            
            elif model_type == 'tensorflow':
                # Cargar modelo TensorFlow/Keras
                try:
                    import tensorflow as tf
                    return tf.keras.models.load_model(model_path)
                except ImportError:
                    logger.error("TensorFlow no está disponible")
                    return None
            
            else:
                logger.error(f"Tipo de modelo no soportado: {model_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error cargando modelo tipo {model_type}: {e}")
            return None
    
    def _update_access_stats(self, model_name: str):
        """
        Actualiza estadísticas de acceso a un modelo.
        
        Args:
            model_name (str): Nombre del modelo
        """
        current_time = time.time()
        
        if model_name not in self.access_counts:
            self.access_counts[model_name] = 0
        
        self.access_counts[model_name] += 1
        self.last_access_times[model_name] = current_time
    
    def _cleanup_old_models(self):
        """
        Limpia modelos antiguos de memoria si se excede el límite.
        """
        if len(self._models) <= self.max_models_in_memory:
            return
        
        current_time = time.time()
        
        # Encontrar modelos que no se han usado recientemente
        old_models = []
        for model_name, last_access in self.last_access_times.items():
            if current_time - last_access > self.model_timeout:
                old_models.append((model_name, last_access))
        
        # Ordenar por tiempo de último acceso (más antiguo primero)
        old_models.sort(key=lambda x: x[1])
        
        # Descargar modelos antiguos hasta estar bajo el límite
        models_to_remove = len(self._models) - self.max_models_in_memory + 1
        for model_name, _ in old_models[:models_to_remove]:
            self.unload_model(model_name)
    
    def unload_model(self, model_name: str) -> bool:
        """
        Descarga un modelo de memoria.
        
        Args:
            model_name (str): Nombre del modelo a descargar
            
        Returns:
            bool: True si se descargó exitosamente
        """
        if model_name in self._models:
            del self._models[model_name]
            logger.info(f"Modelo {model_name} descargado de memoria")
            return True
        return False
    
    def reload_model(self, model_name: str, **kwargs) -> Optional[Any]:
        """
        Recarga un modelo forzando su actualización.
        
        Args:
            model_name (str): Nombre del modelo
            **kwargs: Argumentos adicionales
            
        Returns:
            Modelo recargado o None si hay error
        """
        self.unload_model(model_name)
        return self._get_model(model_name, **kwargs)
    
    def get_loaded_models(self) -> Dict[str, Any]:
        """
        Obtiene una lista de modelos actualmente cargados.
        
        Returns:
            Dict: Modelos cargados con su metadata
        """
        return {
            name: {
                'model': model,
                'metadata': self._model_metadata.get(name, {}),
                'access_count': self.access_counts.get(name, 0),
                'last_access': self.last_access_times.get(name, 0)
            }
            for name, model in self._models.items()
        }
    
    def get_model_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de modelos.
        
        Returns:
            Dict: Estadísticas completas
        """
        current_time = time.time()
        
        stats = {
            'loaded_models': list(self._models.keys()),
            'total_loaded': len(self._models),
            'max_models': self.max_models_in_memory,
            'model_stats': {}
        }
        
        for model_name in MODEL_CONFIGS.keys():
            model_stats = {
                'is_loaded': model_name in self._models,
                'access_count': self.access_counts.get(model_name, 0),
                'load_time': self.load_times.get(model_name, 0),
                'last_access_ago': current_time - self.last_access_times.get(model_name, current_time)
            }
            
            if model_name in self._model_metadata:
                model_stats.update(self._model_metadata[model_name])
            
            stats['model_stats'][model_name] = model_stats
        
        return stats
    
    def clear_all_models(self):
        """Limpia todos los modelos de memoria."""
        self._models.clear()
        self._model_metadata.clear()
        self.access_counts.clear()
        self.last_access_times.clear()
        self.load_times.clear()
        logger.info("Todos los modelos limpiados de memoria")
    
    def warmup_models(self, model_names: Optional[list] = None):
        """
        Pre-carga modelos en memoria para mejor rendimiento.
        
        Args:
            model_names (list, optional): Lista de modelos a precargar.
                                        Si es None, precarga modelos críticos.
        """
        if model_names is None:
            # Modelos críticos por defecto
            model_names = ['vision_model', 'weight_regression']
        
        logger.info(f"Precargando modelos: {model_names}")
        
        for model_name in model_names:
            try:
                self._get_model(model_name)
                logger.info(f"Modelo {model_name} precargado")
            except Exception as e:
                logger.error(f"Error precargando modelo {model_name}: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del gestor de modelos.
        
        Returns:
            Dict: Estado de salud completo
        """
        health = {
            'status': 'healthy',
            'issues': [],
            'model_availability': {},
            'memory_usage': {
                'loaded_models': len(self._models),
                'max_models': self.max_models_in_memory
            }
        }
        
        # Verificar disponibilidad de archivos de modelo
        for model_name, config in MODEL_CONFIGS.items():
            model_path = config['model_path']
            available = model_path.exists()
            
            health['model_availability'][model_name] = {
                'file_exists': available,
                'is_loaded': model_name in self._models,
                'path': str(model_path)
            }
            
            if not available:
                health['issues'].append(f"Archivo de modelo no encontrado: {model_name}")
                health['status'] = 'warning'
        
        # Verificar memoria
        if len(self._models) >= self.max_models_in_memory:
            health['issues'].append("Límite de modelos en memoria alcanzado")
            health['status'] = 'warning'
        
        return health


# Instancia singleton global
model_manager = ModelManagerSingleton()


def get_vision_model(device: str = 'auto'):
    """
    Función de conveniencia para obtener el modelo de visión.
    
    Args:
        device (str): Device donde cargar el modelo
        
    Returns:
        Modelo de visión o None
    """
    return model_manager.get_vision_model(device=device)


def get_regression_model():
    """
    Función de conveniencia para obtener el modelo de regresión.
    
    Returns:
        Modelo de regresión o None
    """
    return model_manager.get_regression_model()


def get_classifier_model(model_type: str = 'cacao_pytorch', device: str = 'auto'):
    """
    Función de conveniencia para obtener el modelo de clasificación.
    
    Args:
        model_type (str): Tipo de modelo
        device (str): Device donde cargar el modelo
        
    Returns:
        Modelo de clasificación o None
    """
    return model_manager.get_classifier_model(model_type=model_type, device=device)


def warmup_critical_models():
    """Precarga los modelos críticos para mejor rendimiento."""
    model_manager.warmup_models(['vision_model', 'weight_regression'])


def get_model_manager_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del gestor de modelos.
    
    Returns:
        Dict: Estadísticas completas
    """
    return model_manager.get_model_stats()


def health_check() -> Dict[str, Any]:
    """
    Verifica el estado de salud del sistema de modelos.
    
    Returns:
        Dict: Estado de salud
    """
    return model_manager.health_check()


if __name__ == "__main__":
    # Ejemplo de uso
    print("Inicializando ModelManager...")
    
    # Verificar estado de salud
    health = health_check()
    print(f"Estado de salud: {health['status']}")
    
    if health['issues']:
        print("Problemas encontrados:")
        for issue in health['issues']:
            print(f"  - {issue}")
    
    # Obtener estadísticas
    stats = get_model_manager_stats()
    print(f"\nModelos disponibles: {len(stats['model_stats'])}")
    print(f"Modelos cargados: {stats['total_loaded']}")
    
    # Ejemplo de carga de modelo
    try:
        print("\nProbando carga de modelo de regresión...")
        regression_model = get_regression_model()
        if regression_model:
            print("✓ Modelo de regresión cargado exitosamente")
        else:
            print("✗ Error cargando modelo de regresión")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Mostrar estadísticas finales
    final_stats = get_model_manager_stats()
    print(f"\nModelos cargados finalmente: {final_stats['total_loaded']}")
    for model_name, loaded in final_stats['model_stats'].items():
        status = "✓" if loaded['is_loaded'] else "✗"
        print(f"  {status} {model_name}")
