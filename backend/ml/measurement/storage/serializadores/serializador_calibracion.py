"""
Serializador para parámetros de calibración.

Responsabilidad única: convertir CalibrationParams a/desde dict,
siguiendo el principio de Single Responsibility (SOLID).
"""
from typing import Dict, Any, Optional
from pathlib import Path

from ...models import CalibrationParams, CalibrationMethod
from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.storage.serializadores")


class SerializadorCalibracion:
    """
    Serializador para parámetros de calibración.
    
    Convierte entre objetos CalibrationParams y representaciones
    serializables (dict) para persistencia.
    """
    
    @staticmethod
    def serializar(calibration_params: CalibrationParams) -> Dict[str, Any]:
        """
        Serializa parámetros de calibración a diccionario.
        
        Args:
            calibration_params: Parámetros de calibración
            
        Returns:
            Diccionario serializable
        """
        return {
            'pixels_per_mm': calibration_params.pixels_per_mm,
            'method': calibration_params.method.value,
            'confidence': calibration_params.confidence,
            'timestamp': calibration_params.timestamp,
            'image_dimensions': calibration_params.image_dimensions,
            'validation_score': calibration_params.validation_score
        }
    
    @staticmethod
    def deserializar(calibration_data: Dict[str, Any]) -> Optional[CalibrationParams]:
        """
        Deserializa diccionario a parámetros de calibración.
        
        Args:
            calibration_data: Diccionario con datos de calibración
            
        Returns:
            Parámetros de calibración o None si hay error
        """
        try:
            return CalibrationParams(
                pixels_per_mm=calibration_data['pixels_per_mm'],
                method=CalibrationMethod(calibration_data['method']),
                confidence=calibration_data['confidence'],
                timestamp=calibration_data['timestamp'],
                image_dimensions=tuple(calibration_data['image_dimensions']),
                validation_score=calibration_data.get('validation_score')
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error deserializando calibración: {e}")
            return None

