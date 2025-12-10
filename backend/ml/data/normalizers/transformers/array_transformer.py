"""
Transformador de arrays para operaciones de normalización en lote.

Este módulo maneja la transformación de arrays,
siguiendo el principio de Responsabilidad Única.
"""
from typing import Dict
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.normalizers.transformers")


class ArrayTransformer:
    """
    Transformador para operaciones de normalización de arrays.
    
    Esta clase es responsable de:
    - Transformar arrays (normalizar/desnormalizar)
    - Redimensionar arrays para compatibilidad con scalers
    - Manejar operaciones en lote
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]
    
    @staticmethod
    def prepare_array(array: np.ndarray) -> np.ndarray:
        """
        Prepara array para el scaler (asegura forma 2D).
        
        Args:
            array: Array de entrada
            
        Returns:
            Array redimensionado (2D)
        """
        array = np.array(array)
        if array.ndim == 1:
            array = array.reshape(-1, 1)
        return array
    
    @staticmethod
    def transform_batch(
        targets: Dict[str, np.ndarray],
        scalers: Dict[str, StandardScaler | MinMaxScaler],
        operation: str = "transform"
    ) -> Dict[str, np.ndarray]:
        """
        Transforma un lote de targets.
        
        Args:
            targets: Diccionario con arrays de targets
            scalers: Diccionario con scalers ajustados
            operation: Operación a realizar ("transform" o "inverse_transform")
            
        Returns:
            Diccionario con targets transformados
            
        Raises:
            ValueError: Si faltan targets o la operación es inválida
        """
        if operation not in ["transform", "inverse_transform"]:
            raise ValueError(
                f"Operación inválida: {operation}. "
                f"Debe ser 'transform' o 'inverse_transform'"
            )
        
        transformed = {}
        for target in ArrayTransformer.TARGET_ORDER:
            if target not in targets:
                raise ValueError(f"Target '{target}' no encontrado")
            
            if target not in scalers:
                raise ValueError(f"Scaler para '{target}' no encontrado")
            
            target_array = ArrayTransformer.prepare_array(targets[target])
            
            if operation == "transform":
                transformed_array = scalers[target].transform(target_array)
            else:  # inverse_transform
                transformed_array = scalers[target].inverse_transform(target_array)
            
            transformed[target] = transformed_array.flatten()
        
        return transformed

