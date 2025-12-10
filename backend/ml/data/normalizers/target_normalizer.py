"""
Normalizador de targets para regresión.

Este módulo orquesta la normalización y desnormalización de valores de targets,
siguiendo los principios de Responsabilidad Única e Inversión de Dependencias.
"""
from typing import Dict
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from ...utils.logs import get_ml_logger
from .factories import ScalerFactory
from .transformers import ArrayTransformer, SingleValueTransformer

logger = get_ml_logger("cacaoscan.ml.data.normalizers")


class TargetNormalizer:
    """
    Normalizador de targets para regresión con funciones de normalizar/desnormalizar.
    
    Esta clase orquesta la normalización delegando a clases especializadas,
    siguiendo los principios de Responsabilidad Única e Inversión de Dependencias.
    """
    
    TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(self, scaler_type: str = "standard"):
        """
        Inicializa el normalizador de targets.
        
        Args:
            scaler_type: Tipo de scaler ("standard" o "minmax")
        """
        self.scaler_type = scaler_type
        self.scalers: Dict[str, StandardScaler | MinMaxScaler] = {}
        self.is_fitted = False
        self.scaler_factory = ScalerFactory()
        self.array_transformer = ArrayTransformer()
        self.single_transformer = SingleValueTransformer()
        
        logger.info(f"TargetNormalizer initialized (scaler_type={scaler_type})")
    
    def fit(self, targets: Dict[str, np.ndarray]) -> None:
        """
        Ajusta los scalers a los datos de entrenamiento.
        
        Args:
            targets: Diccionario con arrays de targets {target: array}
            
        Raises:
            ValueError: Si faltan targets
        """
        logger.info(f"Fitting {self.scaler_type} normalizers for targets")
        
        for target in self.TARGET_ORDER:
            if target not in targets:
                raise ValueError(f"Target '{target}' not found in data")
            
            target_array = self.array_transformer.prepare_array(targets[target])
            
            scaler = self.scaler_factory.create(self.scaler_type)
            scaler.fit(target_array)
            self.scalers[target] = scaler
            
            if hasattr(scaler, 'mean_'):
                logger.debug(
                    f"Scaler fitted for {target}: "
                    f"mean={scaler.mean_[0]:.3f}, std={scaler.scale_[0]:.3f}"
                )
            else:
                logger.debug(
                    f"Scaler fitted for {target}: "
                    f"min={scaler.data_min_[0]:.3f}, max={scaler.data_max_[0]:.3f}"
                )
        
        self.is_fitted = True
        logger.info("Normalizers fitted successfully")
    
    def normalize(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Normaliza valores de targets.
        
        Args:
            targets: Diccionario con arrays de targets
            
        Returns:
            Diccionario con targets normalizados
            
        Raises:
            ValueError: Si no está ajustado o faltan targets
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben estar ajustados antes de normalizar")
        
        return self.array_transformer.transform_batch(
            targets,
            self.scalers,
            operation="transform"
        )
    
    def denormalize(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Desnormaliza valores de targets.
        
        Args:
            targets: Diccionario con arrays de targets normalizados
            
        Returns:
            Diccionario con targets desnormalizados
            
        Raises:
            ValueError: Si no está ajustado o faltan targets
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben estar ajustados antes de desnormalizar")
        
        return self.array_transformer.transform_batch(
            targets,
            self.scalers,
            operation="inverse_transform"
        )
    
    def normalize_single(self, target_name: str, value: float) -> float:
        """
        Normaliza un valor individual de target.
        
        Args:
            target_name: Nombre del target
            value: Valor a normalizar
            
        Returns:
            Valor normalizado
            
        Raises:
            ValueError: Si no está ajustado o el target no se encuentra
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben estar ajustados antes de normalizar")
        
        if target_name not in self.scalers:
            raise ValueError(
                f"Target '{target_name}' no encontrado en los normalizadores"
            )
        
        return self.single_transformer.transform_single(
            value,
            self.scalers[target_name],
            operation="transform"
        )
    
    def denormalize_single(self, target_name: str, value: float) -> float:
        """
        Desnormaliza un valor individual de target.
        
        Args:
            target_name: Nombre del target
            value: Valor normalizado a desnormalizar
            
        Returns:
            Valor desnormalizado
            
        Raises:
            ValueError: Si no está ajustado o el target no se encuentra
        """
        if not self.is_fitted:
            raise ValueError("Los normalizadores deben estar ajustados antes de desnormalizar")
        
        if target_name not in self.scalers:
            raise ValueError(
                f"Target '{target_name}' no encontrado en los normalizadores"
            )
        
        return self.single_transformer.transform_single(
            value,
            self.scalers[target_name],
            operation="inverse_transform"
        )

