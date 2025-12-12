"""
Calibración manual usando puntos proporcionados por el usuario.

Este módulo maneja la calibración manual mediante puntos marcados
por el usuario para establecer la escala píxeles/mm,
siguiendo el principio de Responsabilidad Única.
"""
import math
from typing import List, Tuple, Optional

from ...utils.logs import get_ml_logger
from ..models import CalibrationResult, CalibrationMethod

logger = get_ml_logger("cacaoscan.ml.measurement.calibrators")


class CalibradorManual:
    """
    Calibrador usando puntos manuales proporcionados por el usuario.
    
    Esta clase es responsable de:
    - Calcular píxeles por milímetro desde puntos manuales marcados por el usuario
    - Validar que haya suficientes puntos
    - Retornar resultado de calibración con alta confianza
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def calibrate(
        self,
        manual_points: Optional[List[Tuple[int, int]]] = None,
        distance_mm: float = 10.0
    ) -> CalibrationResult:
        """
        Calibra usando puntos manuales proporcionados por el usuario.
        
        Args:
            manual_points: Lista de puntos de calibración manual (mínimo 2 puntos)
            distance_mm: Distancia real en milímetros entre los puntos
            
        Returns:
            Resultado de calibración con escala píxeles/mm
        """
        if not manual_points or len(manual_points) < 2:
            return CalibrationResult(
                success=False,
                pixels_per_mm=0.0,
                confidence=0.0,
                method=CalibrationMethod.MANUAL_POINTS,
                detected_points=[],
                error_message="Se requieren al menos 2 puntos para calibración manual"
            )
        
        # Calcular distancia en píxeles entre los dos puntos
        point1, point2 = manual_points[0], manual_points[1]
        distance_pixels = math.sqrt(
            (point2[0] - point1[0])**2 + (point2[1] - point1[1])**2
        )
        
        pixels_per_mm = distance_pixels / distance_mm
        
        return CalibrationResult(
            success=True,
            pixels_per_mm=pixels_per_mm,
            confidence=0.9,  # Alta confianza para calibración manual
            method=CalibrationMethod.MANUAL_POINTS,
            detected_points=manual_points
        )
