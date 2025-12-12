"""
Clase base abstracta para detectores de granos de cacao.

Este módulo define la interfaz común para detectores,
siguiendo el principio de Abierto/Cerrado y Inversión de Dependencias.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from PIL import Image

from ...utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.detectors")


class BaseDetector(ABC):
    """
    Clase base abstracta para detectores de granos de cacao.
    
    Proporciona la estructura común para todos los detectores,
    siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(self):
        """Inicializa el detector base."""
        self._is_initialized = False
    
    @abstractmethod
    def detect(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detecta granos de cacao en una imagen.
        
        Args:
            image: Imagen PIL del grano de cacao
            
        Returns:
            Diccionario con información de detección:
            - success: bool
            - confidence: float
            - bbox: Optional[Tuple[int, int, int, int]] (x, y, width, height)
            - mask: Optional[np.ndarray]
            - error_message: Optional[str]
        """
        pass
    
    @abstractmethod
    def validate_detection(self, detection_result: Dict[str, Any]) -> bool:
        """
        Valida que una detección sea válida.
        
        Args:
            detection_result: Resultado de detección
            
        Returns:
            True si la detección es válida
        """
        pass
    
    def is_initialized(self) -> bool:
        """
        Verifica si el detector está inicializado.
        
        Returns:
            True si está inicializado
        """
        return self._is_initialized
    
    def _set_initialized(self, value: bool = True) -> None:
        """
        Establece el estado de inicialización.
        
        Args:
            value: Estado de inicialización
        """
        self._is_initialized = value

