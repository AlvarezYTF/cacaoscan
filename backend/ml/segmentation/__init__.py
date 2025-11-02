"""
MÃ³dulo de segmentaciÃ³n para CacaoScan.

Incluye:
- Inferencia con YOLOv8-seg
- Procesamiento de recortes
- Entrenamiento de modelos personalizados
"""

from .infer_yolo_seg import YOLOSegmentationInference, create_yolo_inference
from .cropper import CacaoCropper, create_cacao_cropper
from .train_yolo import (
    YOLOTrainingManager, 
    create_yolo_trainer, 
    train_cacao_yolo_model
)

__all__ = [
    'YOLOSegmentationInference',
    'create_yolo_inference',
    'CacaoCropper',
    'create_cacao_cropper',
    'YOLOTrainingManager',
    'create_yolo_trainer',
    'train_cacao_yolo_model'
]


