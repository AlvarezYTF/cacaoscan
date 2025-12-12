"""
Interfaz para validación de parámetros de calibración.

Define el contrato que deben cumplir todas las implementaciones
de validación, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, Any, Optional

from ...models import CalibrationParams


class IValidadorCalibracion(Protocol):
    """
    Interfaz para validación de calibración.
    
    Define los métodos que debe implementar cualquier clase
    que valide parámetros de calibración.
    """
    
    def validate(
        self,
        current_calibration: CalibrationParams,
        expected_pixels_per_mm: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Valida la precisión de la calibración.
        
        Args:
            current_calibration: Parámetros de calibración actuales
            expected_pixels_per_mm: Valor esperado de píxeles por mm (opcional)
            
        Returns:
            Diccionario con métricas de validación
        """
        ...

