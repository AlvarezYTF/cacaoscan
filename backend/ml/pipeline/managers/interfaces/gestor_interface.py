"""
Interfaz para gestores de artefactos.

Define el contrato que deben cumplir todas las implementaciones
de gestores, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, Optional
from pathlib import Path
import torch


class IGestorArtefactos(Protocol):
    """
    Interfaz para gestores de artefactos.
    
    Define los métodos que debe implementar cualquier clase
    que gestione artefactos de entrenamiento.
    """
    
    def guardar_scalers(self, scalers) -> bool:
        """
        Guarda scalers en disco.
        
        Args:
            scalers: Instancia de CacaoScalers a guardar
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        ...
    
    def guardar_checkpoint_modelo(
        self,
        model: torch.nn.Module,
        model_name: str,
        model_info: Optional[Dict] = None
    ) -> bool:
        """
        Guarda checkpoint de modelo en disco.
        
        Args:
            model: Modelo PyTorch a guardar
            model_name: Nombre del archivo del modelo
            model_info: Información adicional del modelo (opcional)
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        ...
    
    def verificar_artefactos_guardados(
        self,
        is_hybrid: bool = False,
        is_multi_head: bool = False
    ) -> bool:
        """
        Verifica que todos los artefactos requeridos estén guardados.
        
        Args:
            is_hybrid: Si se entrenó modelo híbrido
            is_multi_head: Si se entrenó modelo multi-head
            
        Returns:
            True si todos los artefactos están presentes, False en caso contrario
        """
        ...
    
    def obtener_directorio_artefactos(self) -> Path:
        """
        Obtiene el directorio de artefactos.
        
        Returns:
            Ruta al directorio de artefactos
        """
        ...

