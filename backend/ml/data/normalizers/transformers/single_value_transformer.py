"""
Transformador de valores individuales para operaciones de normalización.

Este módulo maneja la transformación de valores individuales,
siguiendo el principio de Responsabilidad Única.
"""
from typing import Union
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.normalizers.transformers")


class SingleValueTransformer:
    """
    Transformador para operaciones de normalización de valores individuales.
    
    Esta clase es responsable de:
    - Transformar valores individuales (normalizar/desnormalizar)
    - Preparar valores para operaciones de scaler
    - Manejar operaciones individuales
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    @staticmethod
    def transform_single(
        value: float,
        scaler: Union[StandardScaler, MinMaxScaler],
        operation: str = "transform"
    ) -> float:
        """
        Transforma un valor individual.
        
        Args:
            value: Valor a transformar
            scaler: Scaler ajustado
            operation: Operación a realizar ("transform" o "inverse_transform")
            
        Returns:
            Valor transformado
            
        Raises:
            ValueError: Si la operación es inválida
        """
        if operation not in ["transform", "inverse_transform"]:
            raise ValueError(
                f"Operación inválida: {operation}. "
                f"Debe ser 'transform' o 'inverse_transform'"
            )
        
        value_array = np.array([[value]])
        
        if operation == "transform":
            transformed = scaler.transform(value_array)
        else:  # inverse_transform
            transformed = scaler.inverse_transform(value_array)
        
        return float(transformed[0, 0])

