"""
Model import utilities for CacaoScan API.
Provides safe model imports to handle optional dependencies.
"""
from typing import Optional, Any, Dict
import importlib
import logging

logger = logging.getLogger("cacaoscan.api.utils.model_imports")


def get_model_safely(model_path: str) -> Optional[Any]:
    """
    Safely imports a model or class from a module path.
    
    Args:
        model_path: Full path to the model/class (e.g., 'images_app.models.CacaoImage')
        
    Returns:
        The imported model/class if successful, None otherwise
        
    Example:
        CacaoImage = get_model_safely('images_app.models.CacaoImage')
    """
    try:
        module_path, class_name = model_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError, ValueError) as e:
        logger.debug(f"Could not import {model_path}: {e}")
        return None


def get_models_safely(model_paths: Dict[str, str]) -> Dict[str, Optional[Any]]:
    """
    Safely imports multiple models/classes from module paths.
    
    Args:
        model_paths: Dictionary mapping variable names to model paths
                    (e.g., {'CacaoImage': 'images_app.models.CacaoImage',
                            'CacaoPrediction': 'images_app.models.CacaoPrediction'})
        
    Returns:
        Dictionary mapping variable names to imported models/classes (or None if import failed)
        
    Example:
        models = get_models_safely({
            'CacaoImage': 'images_app.models.CacaoImage',
            'CacaoPrediction': 'images_app.models.CacaoPrediction'
        })
        CacaoImage = models['CacaoImage']
        CacaoPrediction = models['CacaoPrediction']
    """
    result = {}
    for var_name, model_path in model_paths.items():
        result[var_name] = get_model_safely(model_path)
    return result
