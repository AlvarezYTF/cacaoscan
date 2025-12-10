"""
Módulo de segmentación para CacaoScan.

REFACTORIZADO: Aplicando principios SOLID
- Funciones auxiliares extraídas para mejorar SRP
- Mejores docstrings y type hints
- Separación de responsabilidades mejorada

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
from .processor import segment_and_crop_cacao_bean, convert_bmp_to_jpg

__all__ = [
    'YOLOSegmentationInference',
    'create_yolo_inference',
    'CacaoCropper',
    'create_cacao_cropper',
    'YOLOTrainingManager',
    'create_yolo_trainer',
    'train_cacao_yolo_model',
    'segment_and_crop_cacao_bean',
    'convert_bmp_to_jpg'
]


