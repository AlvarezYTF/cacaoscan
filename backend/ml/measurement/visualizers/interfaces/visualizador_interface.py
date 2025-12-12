"""
Interfaz para visualización de resultados de calibración.

Define el contrato que deben cumplir todas las implementaciones
de visualización, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol
from pathlib import Path
import numpy as np


class IVisualizadorCalibracion(Protocol):
    """
    Interfaz para visualización de calibración.
    
    Define los métodos que debe implementar cualquier clase
    que visualice resultados de calibración.
    """
    
    def save_calibration_image(
        self,
        image: np.ndarray,
        calibration_dir: Path
    ) -> Path:
        """
        Guarda imagen de calibración.
        
        Args:
            image: Imagen a guardar
            calibration_dir: Directorio para guardar imagen
            
        Returns:
            Ruta a la imagen guardada
        """
        ...

