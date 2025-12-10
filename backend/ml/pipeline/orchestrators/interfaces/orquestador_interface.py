"""
Interfaz para orquestadores de entrenamiento.

Define el contrato que deben cumplir todas las implementaciones
de orquestadores, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, Optional, Any, Union
import torch
from torch.utils.data import DataLoader


class IOrquestadorEntrenamiento(Protocol):
    """
    Interfaz para orquestadores de entrenamiento.
    
    Define los métodos que debe implementar cualquier clase
    que gestione la orquestación del entrenamiento.
    """
    
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
        ...
    
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
        ...
    
    def evaluar_modelos_individuales(
        self,
        models: Dict[str, torch.nn.Module],
        test_loader: Optional[DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Evalúa modelos individuales.
        
        Args:
            models: Diccionario de modelos por target
            test_loader: Loader de test (opcional)
            
        Returns:
            Diccionario de métricas por target
        """
        ...
    
    def evaluar_modelo_multi_head(
        self,
        model: torch.nn.Module,
        test_loader: Optional[DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Evalúa modelo multi-head o híbrido.
        
        Args:
            model: Modelo multi-head o híbrido
            test_loader: Loader de test (opcional)
            
        Returns:
            Diccionario de métricas por target
        """
        ...

