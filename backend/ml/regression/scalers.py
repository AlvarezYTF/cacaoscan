"""
Manejo de escaladores para normalización de targets de regresión.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from sklearn.preprocessing import StandardScaler
import logging

from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from ..utils.logs import get_ml_logger
from .models import TARGETS


logger = get_ml_logger("cacaoscan.ml.regression")


class CacaoScalers:
    """
    Manejador de escaladores para targets de regresión con log-transform selectivo.
    
    Aplica log1p SOLO a grosor y peso.
    """
    
    # Targets que requieren log-transform
    LOG_TARGETS = {"grosor", "peso"}
    
    def __init__(self, scaler_type: str = "standard"):
        """
        Inicializa el manejador de escaladores.
        
        Args:
            scaler_type: Tipo de escalador ("standard", "minmax", "robust")
        """
        self.scaler_type = scaler_type
        self.scalers: Dict[str, StandardScaler] = {}
        self.is_fitted = False
        
        # Asegurar que el directorio de artefactos existe
        ensure_dir_exists(get_regressors_artifacts_dir())
        
        logger.info(f"CacaoScalers initialized with LOG_TARGETS: {self.LOG_TARGETS}")
    
    def _create_scaler(self) -> StandardScaler:
        """Crea un escalador según el tipo especificado."""
        if self.scaler_type == "standard":
            return StandardScaler()
        elif self.scaler_type == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            return MinMaxScaler()
        elif self.scaler_type == "robust":
            from sklearn.preprocessing import RobustScaler
            return RobustScaler()
        else:
            raise ValueError(f"Tipo de escalador '{self.scaler_type}' no soportado")
    
    def fit(self, data: Union[pd.DataFrame, Dict[str, np.ndarray]]) -> None:
        """
        Ajusta los escaladores a los datos de entrenamiento.
        
        Args:
            data: DataFrame con columnas de targets o diccionario con arrays
        """
        logger.info(f"Ajustando escaladores {self.scaler_type} para {len(TARGETS)} targets")
        
        # Convertir a diccionario si es DataFrame
        if isinstance(data, pd.DataFrame):
            target_data = {}
            for target in TARGETS:
                if target in data.columns:
                    target_data[target] = data[target].values.reshape(-1, 1)
                else:
                    raise ValueError(f"Columna '{target}' no encontrada en DataFrame")
        else:
            # Si es diccionario, asegurar que los arrays sean 2D para los scalers
            target_data = {}
            for target in TARGETS:
                if target not in data:
                    raise ValueError(f"Target '{target}' no encontrado en datos")
                
                target_array = data[target]
                # Asegurar que sea array numpy
                if not isinstance(target_array, np.ndarray):
                    target_array = np.array(target_array)
                
                # Reshape a 2D si es 1D
                if target_array.ndim == 1:
                    target_data[target] = target_array.reshape(-1, 1)
                elif target_array.ndim == 2:
                    target_data[target] = target_array
                else:
                    raise ValueError(f"Array de target '{target}' tiene dimensión inválida: {target_array.ndim}")
        
        # Crear y ajustar escalador para cada target
        for target in TARGETS:
            if target not in target_data:
                raise ValueError(f"Target '{target}' no encontrado en datos")
            
            # Aplicar log1p SOLO a grosor y peso ANTES de normalizar
            target_array = target_data[target].copy()
            if target in self.LOG_TARGETS:
                target_array = np.log1p(target_array)
                logger.info(f"Applied log1p transform to {target} before scaling")
            else:
                logger.debug(f"No log transform for {target}")
            
            scaler = self._create_scaler()
            scaler.fit(target_array)
            self.scalers[target] = scaler
            
            logger.debug(f"Escalador ajustado para {target}: mean={scaler.mean_[0]:.3f}, std={scaler.scale_[0]:.3f}")
        
        self.is_fitted = True
        logger.info("Escaladores ajustados exitosamente")
    
    def transform(self, data: Union[pd.DataFrame, Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """
        Transforma los datos usando los escaladores ajustados.
        
        Args:
            data: Datos a transformar
            
        Returns:
            Diccionario con datos transformados
        """
        if not self.is_fitted:
            raise ValueError("Los escaladores deben ser ajustados antes de transformar")
        
        # Convertir a diccionario si es DataFrame
        if isinstance(data, pd.DataFrame):
            target_data = {}
            for target in TARGETS:
                if target in data.columns:
                    target_data[target] = data[target].values.reshape(-1, 1)
                else:
                    raise ValueError(f"Columna '{target}' no encontrada en DataFrame")
        else:
            # Si es diccionario, asegurar que los arrays sean 2D para los scalers
            target_data = {}
            for target in TARGETS:
                if target not in data:
                    raise ValueError(f"Target '{target}' no encontrado en datos")
                
                target_array = data[target]
                # Asegurar que sea array numpy
                if not isinstance(target_array, np.ndarray):
                    target_array = np.array(target_array)
                
                # Reshape a 2D si es 1D
                if target_array.ndim == 1:
                    target_data[target] = target_array.reshape(-1, 1)
                elif target_array.ndim == 2:
                    target_data[target] = target_array
                else:
                    raise ValueError(f"Array de target '{target}' tiene dimensión inválida: {target_array.ndim}")
        
        transformed_data = {}
        for target in TARGETS:
            if target not in target_data:
                raise ValueError(f"Target '{target}' no encontrado en datos")
            
            # Aplicar log1p SOLO a grosor y peso ANTES de transformar
            target_array = target_data[target].copy()
            if target in self.LOG_TARGETS:
                target_array = np.log1p(target_array)
            
            transformed = self.scalers[target].transform(target_array)
            transformed_data[target] = transformed.flatten()
            
        return transformed_data
    
    def inverse_transform(self, data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Transforma los datos de vuelta al espacio original.
        
        Args:
            data: Datos normalizados a transformar de vuelta
            
        Returns:
            Diccionario con datos en espacio original
        """
        if not self.is_fitted:
            raise ValueError("Los escaladores deben ser ajustados antes de transformar")
        
        original_data = {}
        for target in TARGETS:
            if target not in data:
                raise ValueError(f"Target '{target}' no encontrado en datos")
            
            # Reshape para el escalador
            target_values = data[target].reshape(-1, 1)
            original = self.scalers[target].inverse_transform(target_values)
            
            # Aplicar expm1 SOLO a grosor y peso DESPUÉS de inverse_transform
            if target in self.LOG_TARGETS:
                original = np.expm1(original)
                original = np.maximum(original, 0.0)  # Ensure non-negative
            
            original_data[target] = original.flatten()
            
        return original_data
    
    def fit_transform(self, data: Union[pd.DataFrame, Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """
        Ajusta y transforma los datos en una sola operación.
        
        Args:
            data: Datos a ajustar y transformar
            
        Returns:
            Datos transformados
        """
        self.fit(data)
        return self.transform(data)
    
    def save(self, file_prefix: str = "") -> None:
        """
        Guarda los escaladores en archivos pickle.
        
        Args:
            file_prefix: Prefijo para los nombres de archivo
        """
        if not self.is_fitted:
            raise ValueError("Los escaladores deben ser ajustados antes de guardar")
        
        try:
            artifacts_dir = get_regressors_artifacts_dir()
            saved_scalers = []
            
            for target in TARGETS:
                scaler_path = artifacts_dir / f"{file_prefix}{target}_scaler.pkl"
                joblib.dump(self.scalers[target], scaler_path)
                
                # Verificar que el archivo se guardó correctamente
                if scaler_path.exists() and scaler_path.stat().st_size > 0:
                    logger.debug(f"[OK] Escalador guardado para {target} en {scaler_path} ({scaler_path.stat().st_size} bytes)")
                    saved_scalers.append(target)
                else:
                    logger.error(f"[ERROR] Error: Escalador no se guardó para {target}: {scaler_path}")
                    raise IOError(f"No se pudo guardar el escalador para {target}")
            
            logger.info(f"[OK] Todos los escaladores guardados exitosamente en {artifacts_dir}: {saved_scalers}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando escaladores: {e}")
            raise
    
    def load(self, file_prefix: str = "") -> None:
        """
        Carga los escaladores desde archivos pickle.
        
        Args:
            file_prefix: Prefijo para los nombres de archivo
        """
        artifacts_dir = get_regressors_artifacts_dir()
        
        for target in TARGETS:
            scaler_path = artifacts_dir / f"{file_prefix}{target}_scaler.pkl"
            
            if not scaler_path.exists():
                raise FileNotFoundError(f"Escalador no encontrado para {target} en {scaler_path}")
            
            self.scalers[target] = joblib.load(scaler_path)
            logger.debug(f"Escalador cargado para {target} desde {scaler_path}")
        
        self.is_fitted = True
        logger.info("Escaladores cargados exitosamente")
    
    def get_scaler_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Obtiene estadísticas de los escaladores ajustados.
        
        Returns:
            Diccionario con estadísticas por target
        """
        if not self.is_fitted:
            raise ValueError("Los escaladores deben ser ajustados antes de obtener estadísticas")
        
        stats = {}
        for target in TARGETS:
            scaler = self.scalers[target]
            stats[target] = {
                'mean': scaler.mean_[0] if hasattr(scaler, 'mean_') else None,
                'std': scaler.scale_[0] if hasattr(scaler, 'scale_') else None,
                'min': scaler.data_min_[0] if hasattr(scaler, 'data_min_') else None,
                'max': scaler.data_max_[0] if hasattr(scaler, 'data_max_') else None
            }
        
        return stats


def load_scalers(file_prefix: str = "") -> CacaoScalers:
    """
    Función de conveniencia para cargar escaladores.
    
    Args:
        file_prefix: Prefijo para los nombres de archivo
        
    Returns:
        Instancia de CacaoScalers con escaladores cargados
    """
    scalers = CacaoScalers()
    scalers.load(file_prefix)
    return scalers


def save_scalers(
    scalers: CacaoScalers,
    file_prefix: str = ""
) -> None:
    """
    Función de conveniencia para guardar escaladores.
    
    Args:
        scalers: Instancia de CacaoScalers
        file_prefix: Prefijo para los nombres de archivo
    """
    scalers.save(file_prefix)


def create_scalers_from_data(
    data: Union[pd.DataFrame, Dict[str, np.ndarray]],
    scaler_type: str = "standard"
) -> CacaoScalers:
    """
    Función de conveniencia para crear y ajustar escaladores desde datos.
    
    Args:
        data: Datos de entrenamiento
        scaler_type: Tipo de escalador
        
    Returns:
        Instancia de CacaoScalers ajustada
    """
    scalers = CacaoScalers(scaler_type=scaler_type)
    scalers.fit(data)
    return scalers


def validate_scalers(scalers: CacaoScalers) -> bool:
    """
    Valida que todos los escaladores estén correctamente ajustados.
    
    Args:
        scalers: Instancia de CacaoScalers a validar
        
    Returns:
        True si todos los escaladores son válidos
    """
    if not scalers.is_fitted:
        return False
    
    for target in TARGETS:
        if target not in scalers.scalers:
            logger.error(f"Escalador faltante para target: {target}")
            return False
        
        scaler = scalers.scalers[target]
        if not hasattr(scaler, 'mean_') or scaler.mean_ is None:
            logger.error(f"Escalador no ajustado para target: {target}")
            return False
    
    logger.info("Todos los escaladores son válidos")
    return True
