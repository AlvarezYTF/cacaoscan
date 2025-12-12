"""
Calculador de métricas para validación de calibración.

Responsabilidad única: calcular métricas de precisión,
siguiendo el principio de Single Responsibility (SOLID).
"""
from typing import Dict, Any

from ...models import CalibrationParams
from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.validators.calculadores")


class CalculadorMetricas:
    """
    Calculador de métricas para validación de calibración.
    
    Calcula métricas de precisión comparando calibración actual
    con valores esperados o usando solo la confianza.
    """
    
    # Umbrales de validación
    UMBRAL_PRECISION: float = 0.8
    UMBRAL_CONFIANZA: float = 0.7
    
    @staticmethod
    def calcular_accuracy_score(
        pixels_per_mm_actual: float,
        pixels_per_mm_esperado: float
    ) -> float:
        """
        Calcula el score de precisión comparando valores actuales y esperados.
        
        Args:
            pixels_per_mm_actual: Valor actual de píxeles por mm
            pixels_per_mm_esperado: Valor esperado de píxeles por mm
            
        Returns:
            Score de precisión entre 0.0 y 1.0
        """
        diferencia = abs(pixels_per_mm_actual - pixels_per_mm_esperado)
        accuracy_score = max(
            0.0,
            1.0 - (diferencia / pixels_per_mm_esperado)
        )
        return accuracy_score
    
    @staticmethod
    def calcular_metricas_con_esperado(
        calibration_params: CalibrationParams,
        expected_pixels_per_mm: float
    ) -> Dict[str, Any]:
        """
        Calcula métricas comparando con un valor esperado.
        
        Args:
            calibration_params: Parámetros de calibración actuales
            expected_pixels_per_mm: Valor esperado de píxeles por mm
            
        Returns:
            Diccionario con métricas calculadas
        """
        pixels_per_mm_actual = calibration_params.pixels_per_mm
        diferencia = abs(pixels_per_mm_actual - expected_pixels_per_mm)
        accuracy_score = CalculadorMetricas.calcular_accuracy_score(
            pixels_per_mm_actual,
            expected_pixels_per_mm
        )
        
        return {
            'accuracy_score': accuracy_score,
            'pixels_per_mm_current': pixels_per_mm_actual,
            'pixels_per_mm_expected': expected_pixels_per_mm,
            'difference': diferencia,
            'confidence': calibration_params.confidence
        }
    
    @staticmethod
    def calcular_metricas_sin_esperado(
        calibration_params: CalibrationParams
    ) -> Dict[str, Any]:
        """
        Calcula métricas usando solo la confianza de la calibración.
        
        Args:
            calibration_params: Parámetros de calibración actuales
            
        Returns:
            Diccionario con métricas calculadas
        """
        return {
            'accuracy_score': calibration_params.confidence,
            'pixels_per_mm': calibration_params.pixels_per_mm,
            'confidence': calibration_params.confidence
        }

