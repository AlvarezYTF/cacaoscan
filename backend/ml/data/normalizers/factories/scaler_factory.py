"""
Factory de scalers para crear scalers de normalización.

Este módulo maneja la creación de diferentes tipos de scalers,
siguiendo el patrón Factory y el principio de Responsabilidad Única.
"""
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Union

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.normalizers.factories")


class ScalerFactory:
    """
    Factory para crear scalers de normalización.
    
    Esta clase es responsable de:
    - Crear scalers según el tipo
    - Validar tipos de scalers
    - Proporcionar scalers por defecto
    
    Siguiendo el patrón Factory y el principio de Responsabilidad Única.
    """
    
    SUPPORTED_TYPES = ["standard", "minmax"]
    
    @staticmethod
    def create(scaler_type: str) -> Union[StandardScaler, MinMaxScaler]:
        """
        Crea un scaler del tipo especificado.
        
        Args:
            scaler_type: Tipo de scaler ("standard" o "minmax")
            
        Returns:
            Instancia del scaler
            
        Raises:
            ValueError: Si el tipo de scaler no es soportado
        """
        if scaler_type not in ScalerFactory.SUPPORTED_TYPES:
            raise ValueError(
                f"Tipo de scaler no soportado: {scaler_type}. "
                f"Tipos soportados: {ScalerFactory.SUPPORTED_TYPES}"
            )
        
        if scaler_type == "standard":
            scaler = StandardScaler()
            logger.debug("StandardScaler creado")
        else:  # minmax
            scaler = MinMaxScaler()
            logger.debug("MinMaxScaler creado")
        
        return scaler

