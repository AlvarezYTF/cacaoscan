"""
Interfaz para almacenamiento de parámetros de calibración.

Define el contrato que deben cumplir todas las implementaciones
de almacenamiento, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Optional
from pathlib import Path

from ...models import CalibrationParams


class IAlmacenamientoCalibracion(Protocol):
    """
    Interfaz para almacenamiento de calibración.
    
    Define los métodos que debe implementar cualquier clase
    que gestione la persistencia de parámetros de calibración.
    """
    
    def save(self, calibration_params: CalibrationParams) -> None:
        """
        Guarda parámetros de calibración.
        
        Args:
            calibration_params: Parámetros de calibración a guardar
        """
        ...
    
    def load(self) -> Optional[CalibrationParams]:
        """
        Carga parámetros de calibración guardados.
        
        Returns:
            Parámetros de calibración o None si no existen
        """
        ...

