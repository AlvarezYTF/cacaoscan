"""
Orquestador de entrenamiento para modelos de regresión de granos de cacao.

Este módulo proporciona lógica de orquestación para el pipeline de entrenamiento,
coordinando carga de datos, entrenamiento de modelos y evaluación.
Siguiendo principios SOLID:
- Single Responsibility: orquestación del entrenamiento
- Dependency Inversion: implementa IOrquestadorEntrenamiento
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import torch
from torch.utils.data import DataLoader

from ...utils.logs import get_ml_logger
from ...regression.scalers import CacaoScalers
from ...regression.models import TARGETS
from .interfaces import IOrquestadorEntrenamiento

logger = get_ml_logger("cacaoscan.ml.pipeline.orchestrators")


class OrquestadorEntrenamiento(IOrquestadorEntrenamiento):
    """
    Orquestador para pipeline de entrenamiento.
    
    Esta clase coordina el proceso de entrenamiento:
    - Carga y división de datos
    - Entrenamiento de modelos (individual, multi-head, híbrido)
    - Evaluación de modelos
    - Agregación de resultados
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        device: torch.device,
        train_loader: Optional[DataLoader] = None,
        val_loader: Optional[DataLoader] = None,
        test_loader: Optional[DataLoader] = None,
        scalers: Optional[CacaoScalers] = None
    ):
        """
        Inicializa el orquestador de entrenamiento.
        
        Args:
            config: Configuración de entrenamiento
            device: Dispositivo para entrenamiento (cuda/cpu)
            train_loader: Loader de datos de entrenamiento
            val_loader: Loader de datos de validación
            test_loader: Loader de datos de test
            scalers: Scalers para normalización
        """
        self.config = config
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.scalers = scalers
        
        # Flags de tipo de modelo
        self.is_multi_head = bool(config.get("multi_head", False))
        self.is_hybrid = bool(config.get("hybrid", False))
        self.use_pixel_features = bool(config.get("use_pixel_features", False))
        
        logger.info(
            f"OrquestadorEntrenamiento inicializado "
            f"(multi_head={self.is_multi_head}, hybrid={self.is_hybrid})"
        )
    
    def entrenar_modelos_individuales(
        self,
        models: Dict[str, torch.nn.Module],
        train_loaders: Dict[str, DataLoader],
        val_loaders: Dict[str, DataLoader]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Entrena modelos individuales para cada target.
        
        Args:
            models: Diccionario de modelos por target
            train_loaders: Diccionario de loaders de entrenamiento por target
            val_loaders: Diccionario de loaders de validación por target
            
        Returns:
            Diccionario de historiales de entrenamiento por target
        """
        from ...regression.train import train_single_model
        
        logger.info("Entrenando modelos individuales...")
        historiales: Dict[str, Dict[str, Any]] = {}
        
        for target in TARGETS:
            if target not in models:
                logger.warning(f"Modelo para {target} no encontrado, omitiendo")
                continue
            
            logger.info(f"Entrenando modelo para {target}...")
            
            history = train_single_model(
                model=models[target],
                train_loader=train_loaders[target],
                val_loader=val_loaders[target],
                scalers=self.scalers,
                target=target,
                config=self.config,
                device=self.device
            )
            
            historiales[target] = history
        
        return historiales
    
    def entrenar_modelo_multi_head(
        self,
        model: torch.nn.Module
    ) -> Dict[str, Union[Dict, list]]:
        """
        Entrena modelo multi-head o híbrido.
        
        Args:
            model: Modelo multi-head o híbrido
            
        Returns:
            Diccionario con resultados de entrenamiento
        """
        from ...regression.train import train_multi_head_model
        
        if not self.train_loader or not self.val_loader:
            raise ValueError("Los loaders de entrenamiento y validación deben estar configurados")
        
        logger.info(
            f"Entrenando modelo {'híbrido' if self.is_hybrid else 'multi-head'}..."
        )
        
        history = train_multi_head_model(
            model=model,
            train_loader=self.train_loader,
            val_loader=self.val_loader,
            scalers=self.scalers,
            config=self.config,
            device=self.device,
            use_uncertainty_loss=self.config.get('use_uncertainty_loss', None)
        )
        
        return {
            'hybrid' if self.is_hybrid else 'multihead': history,
            'history': history
        }
    
    def evaluar_modelos_individuales(
        self,
        models: Dict[str, torch.nn.Module],
        test_loader: Optional[DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Evalúa modelos individuales.
        
        Args:
            models: Diccionario de modelos por target
            test_loader: Loader de test (usa self.test_loader si es None)
            
        Returns:
            Diccionario de métricas por target
        """
        from ...regression.evaluate import RegressionEvaluator
        
        if test_loader is None:
            test_loader = self.test_loader
        
        if test_loader is None:
            logger.warning("No hay loader de test disponible para evaluación")
            return {}
        
        logger.info("Evaluando modelos individuales...")
        evaluator = RegressionEvaluator(
            models=models,
            test_loader=test_loader,
            scalers=self.scalers,
            device=self.device
        )
        
        results = evaluator.evaluate_all()
        return results
    
    def evaluar_modelo_multi_head(
        self,
        model: torch.nn.Module,
        test_loader: Optional[DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Evalúa modelo multi-head o híbrido.
        
        Args:
            model: Modelo multi-head o híbrido
            test_loader: Loader de test (usa self.test_loader si es None)
            
        Returns:
            Diccionario de métricas por target
        """
        from ...regression.evaluate import RegressionEvaluator
        
        if test_loader is None:
            test_loader = self.test_loader
        
        if test_loader is None:
            logger.warning("No hay loader de test disponible para evaluación")
            return {}
        
        logger.info(
            f"Evaluando modelo {'híbrido' if self.is_hybrid else 'multi-head'}..."
        )
        
        # Convertir modelo único a formato dict para evaluator
        models_dict = {target: model for target in TARGETS}
        
        evaluator = RegressionEvaluator(
            models=models_dict,
            test_loader=test_loader,
            scalers=self.scalers,
            device=self.device,
            is_multi_head=True,
            is_hybrid=self.is_hybrid
        )
        
        results = evaluator.evaluate_all()
        return results
    
    def intentar_entrenamiento_hibrido_v2(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Union[Dict, list]]]:
        """
        Intenta usar el sistema de entrenamiento híbrido v2.
        
        Args:
            config: Configuración de entrenamiento opcional
            
        Returns:
            Resultados de entrenamiento si es exitoso, None en caso contrario
        """
        try:
            from ..hybrid_v2_training import entrenar_modelo_hibrido_v2
            
            logger.info("Usando sistema de entrenamiento híbrido v2 optimizado")
            training_config = config or self.config
            results = entrenar_modelo_hibrido_v2(training_config)
            
            return {
                'hybrid': results,
                'history': results.get('history', {}),
                'test_metrics': results.get('test_metrics', {})
            }
        except ImportError as e:
            logger.warning(f"Entrenamiento híbrido v2 no disponible: {e}")
            return None
        except Exception as e:
            logger.error(f"Error en entrenamiento híbrido v2: {e}")
            return None
    
    def intentar_entrenamiento_hibrido_v1(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Union[Dict, list]]]:
        """
        Intenta usar el sistema de entrenamiento híbrido v1.
        
        Args:
            config: Configuración de entrenamiento opcional
            
        Returns:
            Resultados de entrenamiento si es exitoso, None en caso contrario
        """
        try:
            from ..hybrid_training import entrenar_modelo_hibrido
            
            logger.info("Usando sistema de entrenamiento híbrido v1 con características de píxeles normalizadas")
            training_config = config or self.config
            results = entrenar_modelo_hibrido(training_config)
            
            return {
                'hybrid': results,
                'history': results.get('history', {}),
                'test_metrics': results.get('test_metrics', {})
            }
        except ImportError as e:
            logger.warning(f"Entrenamiento híbrido v1 no disponible: {e}")
            return None
        except Exception as e:
            logger.error(f"Error en entrenamiento híbrido v1: {e}")
            return None
    
    def determinar_dimension_caracteristicas_pixel(
        self,
        pixel_features: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Determina la dimensión de características de píxeles desde configuración o datos.
        
        Args:
            pixel_features: Diccionario opcional de características de píxeles
            
        Returns:
            Dimensión de características de píxeles
        """
        from ..train_all import CALIB_PIXEL_FEATURE_KEYS, PIXEL_FEATURE_KEYS
        
        # Intentar obtener de configuración primero
        config_dim = self.config.get('pixel_feature_dim')
        if config_dim and config_dim > 0:
            return int(config_dim)
        
        # Intentar inferir desde características de píxeles
        if pixel_features:
            if isinstance(pixel_features, dict):
                # Verificar características extendidas
                if all(k in pixel_features for k in CALIB_PIXEL_FEATURE_KEYS):
                    return len(CALIB_PIXEL_FEATURE_KEYS)
                elif all(k in pixel_features for k in PIXEL_FEATURE_KEYS):
                    return len(PIXEL_FEATURE_KEYS)
        
        # Por defecto usar características básicas
        return len(PIXEL_FEATURE_KEYS)
    
    # Métodos de compatibilidad hacia atrás
    def train_individual_models(
        self,
        models: Dict[str, torch.nn.Module],
        train_loaders: Dict[str, DataLoader],
        val_loaders: Dict[str, DataLoader]
    ) -> Dict[str, Dict[str, Any]]:
        """Alias de compatibilidad hacia atrás para entrenar_modelos_individuales."""
        return self.entrenar_modelos_individuales(models, train_loaders, val_loaders)
    
    def train_multi_head_model(
        self,
        model: torch.nn.Module
    ) -> Dict[str, Union[Dict, list]]:
        """Alias de compatibilidad hacia atrás para entrenar_modelo_multi_head."""
        return self.entrenar_modelo_multi_head(model)
    
    def evaluate_individual_models(
        self,
        models: Dict[str, torch.nn.Module],
        test_loader: Optional[DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """Alias de compatibilidad hacia atrás para evaluar_modelos_individuales."""
        return self.evaluar_modelos_individuales(models, test_loader)
    
    def evaluate_multi_head_model(
        self,
        model: torch.nn.Module,
        test_loader: Optional[DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """Alias de compatibilidad hacia atrás para evaluar_modelo_multi_head."""
        return self.evaluar_modelo_multi_head(model, test_loader)
    
    def try_hybrid_v2_training(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Union[Dict, list]]]:
        """Alias de compatibilidad hacia atrás para intentar_entrenamiento_hibrido_v2."""
        return self.intentar_entrenamiento_hibrido_v2(config)
    
    def try_hybrid_v1_training(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Union[Dict, list]]]:
        """Alias de compatibilidad hacia atrás para intentar_entrenamiento_hibrido_v1."""
        return self.intentar_entrenamiento_hibrido_v1(config)
    
    def determine_pixel_feature_dim(
        self,
        pixel_features: Optional[Dict[str, Any]] = None
    ) -> int:
        """Alias de compatibilidad hacia atrás para determinar_dimension_caracteristicas_pixel."""
        return self.determinar_dimension_caracteristicas_pixel(pixel_features)

