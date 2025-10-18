"""
Módulo de predicción para CacaoScan.

Este módulo contiene predictores especializados para diferentes tipos de análisis:
- YOLOv8 para detección y predicción de peso
- Recorte inteligente estilo iPhone
- Segmentación avanzada con máscaras transparentes
"""

from .predict_weight_yolo import (
    WeightPredictorYOLO,
    SmartCropProcessor,
    create_weight_predictor,
    load_weight_predictor
)

__all__ = [
    'WeightPredictorYOLO',
    'SmartCropProcessor', 
    'create_weight_predictor',
    'load_weight_predictor'
]

__version__ = '1.0.0'
__author__ = 'CacaoScan Team'
