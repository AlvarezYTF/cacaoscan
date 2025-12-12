"""
Prediction module for cacao regression models.

This module provides predictors for cacao bean dimension and weight prediction,
following SOLID principles with separation of concerns.
"""

from .base_predictor import PredictorBase
from .predict import (
    PredictorCacao, 
    obtener_predictor, 
    predict_image, 
    predict_image_bytes,
    load_artifacts
)
from .calibrated_predict import PredictorCacaoCalibrado, obtener_predictor_calibrado
from .interfaces import IPredictor

# Compatibilidad hacia atrás (aliases)
BasePredictor = PredictorBase
CacaoPredictor = PredictorCacao
CalibratedCacaoPredictor = PredictorCacaoCalibrado
get_predictor = obtener_predictor
get_calibrated_predictor = obtener_predictor_calibrado

__all__ = [
    # Nombres en español
    'PredictorBase',
    'PredictorCacao',
    'PredictorCacaoCalibrado',
    'IPredictor',
    'obtener_predictor',
    'obtener_predictor_calibrado',
    'predict_image',
    'predict_image_bytes',
    'load_artifacts',
    # Compatibilidad hacia atrás
    'BasePredictor',
    'CacaoPredictor',
    'CalibratedCacaoPredictor',
    'get_predictor',
    'get_calibrated_predictor'
]

