"""
Validador de precisión de calibración para granos de cacao.

Este módulo valida la precisión de calibración usando métricas,
siguiendo principios SOLID:
- Single Responsibility: solo validación, no cálculo de métricas
- Dependency Inversion: implementa IValidadorCalibracion
"""
from typing import Dict, Any, Optional

from ...utils.logs import get_ml_logger
from ..models import CalibrationParams
from .calculadores import CalculadorMetricas

logger = get_ml_logger("cacaoscan.ml.measurement.validators")


class ValidadorCalibracion:
    """
    Validador de precisión de calibración para granos de cacao.
    
    Responsabilidad única: validar calibración usando métricas.
    El cálculo de métricas está delegado a CalculadorMetricas (SRP).
    """
    
    def __init__(self):
        """Inicializa el validador de calibración."""
        self.calculador = CalculadorMetricas()
    
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
        if not current_calibration:
            return {
                'valid': False,
                'error': 'No hay calibración para validar',
                'accuracy_score': 0.0
            }
        
        # Si se proporciona un valor esperado, comparar
        if expected_pixels_per_mm is not None:
            metricas = self.calculador.calcular_metricas_con_esperado(
                current_calibration,
                expected_pixels_per_mm
            )
            
            return {
                'valid': metricas['accuracy_score'] > CalculadorMetricas.UMBRAL_PRECISION,
                **metricas
            }
        
        # Si no hay valor esperado, validar solo la confianza
        metricas = self.calculador.calcular_metricas_sin_esperado(current_calibration)
        
        return {
            'valid': metricas['confidence'] > CalculadorMetricas.UMBRAL_CONFIANZA,
            **metricas
        }

