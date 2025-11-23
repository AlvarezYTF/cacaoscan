"""
Celery tasks module for CacaoScan API.
"""
from .image_tasks import process_batch_analysis_task
from .ml_tasks import validate_dataset_task
from .stats_tasks import calculate_admin_stats_task
from .training_tasks import (
    train_model_task,
    auto_train_model_task,
)

__all__ = [
    # Image tasks
    'process_batch_analysis_task',
    # ML tasks
    'validate_dataset_task',
    # Stats tasks
    'calculate_admin_stats_task',
    # Training tasks
    'train_model_task',
    'auto_train_model_task',
]

