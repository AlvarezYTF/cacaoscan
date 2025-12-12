"""
Interfaz para detectores de granos de cacao.

Este módulo define el protocolo que deben seguir los detectores,
siguiendo el principio de Segregación de Interfaces.
"""
from typing import Protocol, Dict, Any
from PIL import Image


class IDetector(Protocol):
    """
    Protocolo para detectores de granos de cacao.
    
    Define la interfaz mínima que deben implementar todos los detectores,
    siguiendo el principio de Segregación de Interfaces.
    """
    
    def detect(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detecta granos de cacao en una imagen.
        
        Args:
            image: Imagen PIL del grano de cacao
            
        Returns:
            Diccionario con información de detección:
            - success: bool
            - confidence: float
            - bbox: Optional[Tuple[int, int, int, int]]
            - mask: Optional[np.ndarray]
            - error_message: Optional[str]
        """
        ...
    
    def validate_detection(self, detection_result: Dict[str, Any]) -> bool:
        """
        Valida que una detección sea válida.
        
        Args:
            detection_result: Resultado de detección
            
        Returns:
            True si la detección es válida
        """
        ...

