"""
Celery tasks for model training operations in CacaoScan.
Handles asynchronous model training tasks.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from celery import shared_task
from django.utils import timezone

from ..utils.model_imports import get_model_safely

logger = logging.getLogger("cacaoscan.api.tasks.training")

# Import TrainingJob safely
TrainingJob = get_model_safely('training.models.TrainingJob')


@shared_task(bind=True, name='api.tasks.train_model')
def train_model_task(self, job_id: str, config: dict) -> Dict[str, Any]:
    """
    Asynchronous task to train an ML model.
    
    Args:
        job_id: ID of the TrainingJob
        config: Training configuration dictionary with:
            - epochs: int
            - batch_size: int
            - learning_rate: float
            - multi_head: bool
            - model_type: str
            - img_size: int
            - early_stopping_patience: int
            - save_best_only: bool
        
    Returns:
        dict: Training result with status, job_id, and message/error
    """
    try:
        if TrainingJob is None:
            logger.error("TrainingJob model not available")
            return {
                'status': 'failed',
                'job_id': job_id,
                'error': 'TrainingJob model not available'
            }
        
        job = TrainingJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        logger.info(f"Starting training for job {job_id}")
        job.update_progress(5, "Initializing pipeline...")
        
        # Import training pipeline
        from ml.pipeline.train_all import run_training_pipeline
        from ml.utils.paths import get_datasets_dir
        
        # Ensure we use dataset_cacao.clean.csv
        datasets_dir = get_datasets_dir()
        clean_csv_path = datasets_dir / "dataset_cacao.clean.csv"
        
        if not clean_csv_path.exists():
            error_msg = f"Clean dataset not found: {clean_csv_path}"
            logger.error(error_msg)
            job.mark_failed(error_msg)
            return {
                'status': 'failed',
                'job_id': job_id,
                'error': error_msg
            }
        
        logger.info(f"Using dataset: {clean_csv_path}")
        job.update_progress(10, f"Loading dataset: {clean_csv_path.name}")
        
        # Execute training with improved configuration for high confidence
        success = run_training_pipeline(
            epochs=config.get('epochs', 150),
            batch_size=config.get('batch_size', 16),
            learning_rate=config.get('learning_rate', 0.001),
            multi_head=config.get('multi_head', False),
            model_type=config.get('model_type', 'resnet18'),
            img_size=config.get('img_size', 224),
            early_stopping_patience=config.get('early_stopping_patience', 25),
            save_best_only=config.get('save_best_only', True)
        )
        
        if success:
            job.mark_completed()
            job.logs += "\n[COMPLETED] Training completed successfully"
            job.save()
            
            logger.info(f"Training completed for job {job_id}")
            return {
                'status': 'completed',
                'job_id': job_id,
                'message': 'Training completed successfully'
            }
        else:
            error_msg = "Training failed"
            job.mark_failed(error_msg)
            return {
                'status': 'failed',
                'job_id': job_id,
                'error': error_msg
            }
            
    except TrainingJob.DoesNotExist:
        logger.error(f"TrainingJob {job_id} not found")
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': 'Job not found'
        }
    except Exception as e:
        logger.error(f"Error in training for job {job_id}: {e}", exc_info=True)
        if 'job' in locals():
            job.mark_failed(str(e))
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': str(e)
        }


@shared_task(bind=True, name='api.tasks.auto_train_model')
def auto_train_model_task(self, force: bool = False, config: Optional[dict] = None) -> Dict[str, Any]:
    """
    Asynchronous task to automatically train the model after git pull.
    Uses the existing train_cacao_models command with customizable parameters.
    
    Args:
        force: If True, forces training even if no changes detected
        config: Custom training configuration. If None, uses default values.
            Dictionary with:
            - epochs: int
            - batch_size: int
            - learning_rate: float
            - multi_head: bool
            - model_type: str
            - img_size: int
            - early_stopping_patience: int
            - save_best_only: bool
        
    Returns:
        dict: Training result with status and message/error
    """
    try:
        from ml.pipeline.train_all import run_training_pipeline
        from ml.utils.paths import get_datasets_dir
        
        logger.info("Starting automatic model training")
        
        # Verify dataset exists
        datasets_dir = get_datasets_dir()
        clean_csv_path = datasets_dir / "dataset_cacao.clean.csv"
        
        if not clean_csv_path.exists():
            logger.warning(f"Dataset not found in {clean_csv_path}")
            return {
                'status': 'skipped',
                'message': 'Dataset not found. Run: python manage.py prepare_dataset'
            }
        
        # Verify there are .bmp images in raw
        raw_images_dir = Path('media/cacao_images/raw')
        bmp_files = list(raw_images_dir.rglob('*.bmp')) + list(raw_images_dir.rglob('*.BMP'))
        
        if not raw_images_dir.exists() or not bmp_files:
            logger.warning(f"No .bmp images found in {raw_images_dir}")
            return {
                'status': 'skipped',
                'message': f'No .bmp images found for training'
            }
        
        logger.info(f"Found {len(bmp_files)} .bmp images for training")
        
        # Use custom configuration if provided, otherwise default values
        if config:
            training_config = config
        else:
            training_config = {
                'epochs': 150,
                'batch_size': 16,
                'learning_rate': 0.001,
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 25,
                'save_best_only': True
            }
        
        # Execute training using run_training_pipeline
        success = run_training_pipeline(
            epochs=training_config.get('epochs', 150),
            batch_size=training_config.get('batch_size', 16),
            learning_rate=training_config.get('learning_rate', 0.001),
            multi_head=training_config.get('multi_head', False),
            model_type=training_config.get('model_type', 'resnet18'),
            img_size=training_config.get('img_size', 224),
            early_stopping_patience=training_config.get('early_stopping_patience', 25),
            save_best_only=training_config.get('save_best_only', True)
        )
        
        if success:
            logger.info("Automatic training completed successfully")
            return {
                'status': 'completed',
                'message': 'Automatic training completed successfully'
            }
        else:
            return {
                'status': 'failed',
                'message': 'Training failed'
            }
            
    except Exception as e:
        logger.error(f"Error in automatic training: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }

