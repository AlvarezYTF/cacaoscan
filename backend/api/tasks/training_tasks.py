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


def _get_training_config(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Get training configuration with defaults."""
    if config is not None:
        return config
    return {
        'epochs': 150,
        'batch_size': 16,
        'learning_rate': 0.001,
        'multi_head': False,
        'model_type': 'resnet18',
        'img_size': 224,
        'early_stopping_patience': 25,
        'save_best_only': True
    }

def get_task_id(self) -> Optional[str]:
    """
    Safely get task_id from self.request.id with fallback.
    
    Returns:
        task_id if available, None otherwise (e.g., in test mode)
    """
    try:
        if hasattr(self, 'request') and hasattr(self.request, 'id'):
            task_id = getattr(self.request, 'id', None)
            if task_id is not None:
                return str(task_id)
    except (AttributeError, TypeError):
        pass
    return None


def _is_does_not_exist_exception(exception: Exception) -> bool:
    """Check if exception is a DoesNotExist exception."""
    if TrainingJob is None or not hasattr(TrainingJob, 'DoesNotExist'):
        return False
    try:
        does_not_exist_class = TrainingJob.DoesNotExist
        if isinstance(does_not_exist_class, type) and issubclass(does_not_exist_class, BaseException):
            return isinstance(exception, does_not_exist_class)
    except (TypeError, AttributeError):
        pass
    return False

def _handle_training_exception(self, exception: Exception, job_id: str, log_message, job=None) -> Dict[str, Any]:
    """Handle training exceptions."""
    if _is_does_not_exist_exception(exception):
        error_msg = f"TrainingJob {job_id} not found"
        logger.error(error_msg)
        log_message(error_msg)
        safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
        return {'status': 'failed', 'error': error_msg}
    
    error_msg = str(exception)
    logger.error(f"Error in training for job {job_id}: {error_msg}", exc_info=True)
    log_message(f"Error in training for job {job_id}: {error_msg}")
    if job is not None:
        try:
            job.mark_failed(error_msg)
        except Exception:
            pass
    safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
    return {'status': 'failed', 'error': error_msg}

def safe_update_state(self, state: str, meta: Dict[str, Any]) -> None:
    """
    Safely update task state without failing if update_state is not available.
    Only updates state if task_id exists (not in test mode).
    Handles exceptions gracefully to prevent task failures.
    """
    try:
        # Only update state if we have a valid task_id (not in test mode)
        task_id = get_task_id(self)
        if task_id is None:
            # We are in test mode or task_id is not available, skip update_state
            return
        
        if hasattr(self, 'update_state'):
            self.update_state(state=state, meta=meta)
    except Exception:
        # Silently ignore update_state errors to prevent task failures
        pass


@shared_task(bind=True, name='api.tasks.train_model')
def train_model_task(self, job_id: str, dataset_id: Optional[str] = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Asynchronous task to train an ML model.
    
    Args:
        job_id: ID of the TrainingJob
        dataset_id: Optional dataset ID (for future use)
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments, including:
            - config: Training configuration dictionary with:
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
    # Extract config from kwargs, dataset_id (if dict), or first positional arg (for backward compatibility)
    config: Dict[str, Any] = kwargs.get('config', {})
    if not config and isinstance(dataset_id, dict):
        config = dataset_id
        dataset_id = None
    elif not config and args and isinstance(args[0], dict):
        config = args[0]
    
    # Minimal support for self.log
    def log_message(message: str) -> None:
        """Log message using self.log if available, otherwise use logger."""
        if hasattr(self, 'log'):
            self.log(message)
        else:
            logger.info(message)
    
    try:
        if TrainingJob is None:
            error_msg = "TrainingJob model not available"
            logger.error(error_msg)
            log_message(error_msg)
            safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
            return {
                'status': 'failed',
                'error': error_msg
            }
        
        job = TrainingJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        log_message(f"Starting training for job {job_id}")
        safe_update_state(self, 'PROGRESS', {'status': 'Initializing pipeline...', 'progress': 5})
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
            safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
            return {
                'status': 'failed',
                'error': error_msg
            }
        
        log_message(f"Using dataset: {clean_csv_path}")
        safe_update_state(self, 'PROGRESS', {'status': f'Loading dataset: {clean_csv_path.name}', 'progress': 10})
        job.update_progress(10, f"Loading dataset: {clean_csv_path.name}")
        
        # Execute training with improved configuration for high confidence
        safe_update_state(self, 'PROGRESS', {'status': 'Running training pipeline...', 'progress': 20})
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
            
            log_message(f"Training completed for job {job_id}")
            safe_update_state(self, 'SUCCESS', {'status': 'Training completed successfully', 'progress': 100})
            return {
                'status': 'completed',
                'job_id': job_id
            }
        else:
            error_msg = "Training failed"
            job.mark_failed(error_msg)
            safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
            return {
                'status': 'failed',
                'error': error_msg
            }
            
    except Exception as e:
        return _handle_training_exception(self, e, job_id, log_message, locals().get('job'))


@shared_task(bind=True, name='api.tasks.auto_train_model')
def auto_train_model_task(self, save_results: bool = True, config: Optional[Dict[str, Any]] = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Asynchronous task to automatically train the model after git pull.
    Uses the existing train_cacao_models command with customizable parameters.
    
    Args:
        save_results: If True, saves training results (default: True)
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
        *args: Additional positional arguments (for backward compatibility)
        **kwargs: Additional keyword arguments
        
    Returns:
        dict: Training result with status and message/error
    """
    # Get task_id safely with fallback (always available, None in test mode)
    task_id: Optional[str] = get_task_id(self)
    
    # Handle backward compatibility: config can be passed as second positional arg after save_results
    # original_func(mock_task, False, config) -> save_results=False, config from args[0]
    if config is None and args and len(args) > 0 and isinstance(args[0], dict):
        config = args[0]
    elif config is None:
        config = kwargs.get('config', None)
    
    # Minimal support for self.log with task_id context
    def log_message(message: str) -> None:
        """Log message using self.log if available, otherwise use logger."""
        # Include task_id in log message if available (capture from outer scope)
        current_task_id = get_task_id(self)
        log_msg = message
        if current_task_id:
            log_msg = f"[task_id={current_task_id}] {message}"
        
        if hasattr(self, 'log'):
            self.log(log_msg)
        else:
            logger.info(log_msg)
    
    try:
        from ml.pipeline.train_all import run_training_pipeline
        from ml.utils.paths import get_datasets_dir
        
        log_message("Starting automatic model training")
        safe_update_state(self, 'PROGRESS', {'status': 'Starting automatic model training', 'progress': 0})
        
        # Verify dataset exists
        datasets_dir = get_datasets_dir()
        clean_csv_path = datasets_dir / "dataset_cacao.clean.csv"
        
        if not clean_csv_path.exists():
            error_msg = f"Dataset not found in {clean_csv_path}"
            logger.warning(error_msg)
            log_message(error_msg)
            safe_update_state(self, 'SKIPPED', {'status': error_msg, 'progress': 0})
            return {
                'status': 'skipped',
                'message': error_msg
            }
        
        # Verify there are .bmp images in raw
        from ml.utils.paths import get_raw_images_dir
        raw_images_dir = get_raw_images_dir()
        bmp_files = list(raw_images_dir.rglob('*.bmp')) + list(raw_images_dir.rglob('*.BMP'))
        
        if not raw_images_dir.exists() or not bmp_files:
            error_msg = f"No .bmp images found in {raw_images_dir}"
            logger.warning(error_msg)
            log_message(error_msg)
            safe_update_state(self, 'SKIPPED', {'status': error_msg, 'progress': 0})
            return {
                'status': 'skipped',
                'message': error_msg
            }
        
        log_message(f"Found {len(bmp_files)} .bmp images for training")
        safe_update_state(self, 'PROGRESS', {'status': f'Found {len(bmp_files)} images for training', 'progress': 10})
        
        training_config = _get_training_config(config)
        
        # Execute training using run_training_pipeline
        safe_update_state(self, 'PROGRESS', {'status': 'Running training pipeline...', 'progress': 20})
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
            log_message("Automatic training completed successfully")
            safe_update_state(self, 'SUCCESS', {'status': 'Automatic training completed successfully', 'progress': 100})
            result = {
                'status': 'completed'
            }
            if task_id:
                result['task_id'] = task_id
            return result
        else:
            error_msg = 'Training failed'
            safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
            return {
                'status': 'failed',
                'error': error_msg
            }
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in automatic training: {error_msg}", exc_info=True)
        log_message(f"Error in automatic training: {error_msg}")
        safe_update_state(self, 'FAILURE', {'status': error_msg, 'progress': 0})
        return {
            'status': 'failed',
            'error': error_msg
        }
