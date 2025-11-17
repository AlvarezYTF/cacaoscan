"""
Scalers utilities for target normalization with selective log-transform.
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from sklearn.preprocessing import StandardScaler
import logging

from .paths import get_regressors_artifacts_dir, ensure_dir_exists
from .logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.utils.scalers")


class CacaoRobustScaler:
    """
    StandardScaler wrapper for cacao targets with selective log-transform.
    
    Applies log(x + 1) transform ONLY to:
    - grosor_mm
    - peso_g
    
    Other targets (alto_mm, ancho_mm) do NOT get log transform.
    """
    
    TARGETS = ["alto", "ancho", "grosor", "peso"]
    
    # Targets that require log-transform
    LOG_TARGETS = {"grosor", "peso"}
    
    def __init__(self):
        """Initialize the scaler."""
        self.scalers: Dict[str, StandardScaler] = {}
        self.is_fitted = False
        
        ensure_dir_exists(get_regressors_artifacts_dir())
    
    def fit(self, targets: Dict[str, np.ndarray]) -> None:
        """
        Fit scalers to training data.
        
        Args:
            targets: Dictionary with target arrays {target: array}
        """
        logger.info("Fitting StandardScalers for targets with selective log-transform")
        logger.info(f"LOG_TARGETS (will apply log1p): {self.LOG_TARGETS}")
        
        for target in self.TARGETS:
            if target not in targets:
                raise ValueError(f"Target '{target}' not found in data")
            
            target_array = np.array(targets[target], dtype=np.float32)
            
            # Apply log(x + 1) transform ONLY to grosor and peso
            if target in self.LOG_TARGETS:
                target_array = np.log1p(target_array)
                logger.debug(f"Applied log1p transform to {target}")
            else:
                logger.debug(f"No log transform for {target}")
            
            # Reshape for scaler
            if target_array.ndim == 1:
                target_array = target_array.reshape(-1, 1)
            
            # Fit StandardScaler
            scaler = StandardScaler()
            scaler.fit(target_array)
            self.scalers[target] = scaler
            
            logger.debug(
                f"Scaler fitted for {target}: "
                f"mean={scaler.mean_[0]:.3f}, std={scaler.scale_[0]:.3f}"
            )
        
        self.is_fitted = True
        logger.info("All scalers fitted successfully")
    
    def transform(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Transform targets using fitted scalers.
        
        Args:
            targets: Dictionary with target arrays
            
        Returns:
            Transformed targets dictionary
        """
        if not self.is_fitted:
            raise ValueError("Scalers must be fitted before transform")
        
        transformed = {}
        
        for target in self.TARGETS:
            if target not in targets:
                raise ValueError(f"Target '{target}' not found in data")
            
            target_array = np.array(targets[target], dtype=np.float32)
            
            # Apply log1p transform ONLY to grosor and peso
            if target in self.LOG_TARGETS:
                target_array = np.log1p(target_array)
            
            # Reshape for scaler
            if target_array.ndim == 1:
                target_array = target_array.reshape(-1, 1)
            
            # Transform
            transformed_array = self.scalers[target].transform(target_array)
            
            # Flatten back
            transformed[target] = transformed_array.flatten()
        
        return transformed
    
    def inverse_transform(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Inverse transform targets (denormalize).
        
        Args:
            targets: Dictionary with normalized target arrays
            
        Returns:
            Denormalized targets dictionary
        """
        if not self.is_fitted:
            raise ValueError("Scalers must be fitted before inverse_transform")
        
        denormalized = {}
        
        for target in self.TARGETS:
            if target not in targets:
                raise ValueError(f"Target '{target}' not found in data")
            
            target_array = np.array(targets[target], dtype=np.float32)
            
            # Reshape for scaler
            if target_array.ndim == 1:
                target_array = target_array.reshape(-1, 1)
            
            # Inverse transform
            denormalized_array = self.scalers[target].inverse_transform(target_array)
            
            # Apply expm1 to grosor and peso after inverse transform
            if target in self.LOG_TARGETS:
                denormalized_array = np.expm1(denormalized_array)
                # Ensure non-negative
                denormalized_array = np.maximum(denormalized_array, 0.0)
            
            # Flatten back
            denormalized[target] = denormalized_array.flatten()
        
        return denormalized
    
    def fit_transform(self, targets: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Fit and transform in one step.
        
        Args:
            targets: Dictionary with target arrays
            
        Returns:
            Transformed targets dictionary
        """
        self.fit(targets)
        return self.transform(targets)
    
    def save(self, file_prefix: str = "") -> None:
        """
        Save scalers to pickle files.
        
        Args:
            file_prefix: Prefix for filenames
        """
        if not self.is_fitted:
            raise ValueError("Scalers must be fitted before saving")
        
        artifacts_dir = get_regressors_artifacts_dir()
        saved_scalers = []
        
        for target in self.TARGETS:
            scaler_path = artifacts_dir / f"{file_prefix}{target}_scaler.pkl"
            joblib.dump(self.scalers[target], scaler_path)
            
            if scaler_path.exists() and scaler_path.stat().st_size > 0:
                logger.debug(f"Scaler saved for {target}: {scaler_path}")
                saved_scalers.append(target)
            else:
                raise IOError(f"Failed to save scaler for {target}")
        
        # Save metadata
        metadata = {
            "log_targets": list(self.LOG_TARGETS),
            "targets": self.TARGETS
        }
        metadata_path = artifacts_dir / f"{file_prefix}scaler_metadata.pkl"
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"All scalers saved successfully: {saved_scalers}")
    
    def load(self, file_prefix: str = "") -> None:
        """
        Load scalers from pickle files.
        
        Args:
            file_prefix: Prefix for filenames
        """
        artifacts_dir = get_regressors_artifacts_dir()
        
        for target in self.TARGETS:
            scaler_path = artifacts_dir / f"{file_prefix}{target}_scaler.pkl"
            
            if not scaler_path.exists():
                raise FileNotFoundError(f"Scaler not found for {target}: {scaler_path}")
            
            self.scalers[target] = joblib.load(scaler_path)
            logger.debug(f"Scaler loaded for {target}: {scaler_path}")
        
        # Load metadata
        metadata_path = artifacts_dir / f"{file_prefix}scaler_metadata.pkl"
        if metadata_path.exists():
            metadata = joblib.load(metadata_path)
            log_targets = metadata.get("log_targets", ["grosor", "peso"])
            self.LOG_TARGETS = set(log_targets)
        
        self.is_fitted = True
        logger.info("All scalers loaded successfully")


def load_scalers(file_prefix: str = "") -> CacaoRobustScaler:
    """
    Load scalers from disk.
    
    Args:
        file_prefix: Prefix for filenames
        
    Returns:
        CacaoRobustScaler instance
    """
    scaler = CacaoRobustScaler()
    scaler.load(file_prefix)
    return scaler
