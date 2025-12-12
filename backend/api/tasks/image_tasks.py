"""
Celery tasks for image processing operations in CacaoScan.
Handles heavy image processing operations asynchronously.
Can also be executed synchronously when Celery is not available.
"""
import logging
import time
from typing import Dict, Any, List
try:
    from celery import shared_task
except ImportError:
    # Si Celery no está disponible, crear un decorador dummy
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.db import transaction

from ..utils.model_imports import get_models_safely
from ..utils.ml_helpers import (
    get_predictor,
    calculate_prediction_statistics,
    process_image_prediction
)

logger = logging.getLogger("cacaoscan.api.tasks.image")

# Import models safely
models = get_models_safely({
    'Lote': 'fincas_app.models.Lote',
    'Finca': 'fincas_app.models.Finca',
    'CacaoImage': 'images_app.models.CacaoImage'
})
Lote = models['Lote']
Finca = models['Finca']
CacaoImage = models['CacaoImage']


def _get_user_and_lote(user_id: int, lote_id: int) -> tuple:
    """Obtiene el usuario y el lote."""
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    
    try:
        user = user_model.objects.get(id=user_id)
    except user_model.DoesNotExist:
        return None, None, {'status': 'error', 'error': f'User {user_id} not found'}
    
    try:
        lote = Lote.objects.select_related('finca').get(id=lote_id)
    except Lote.DoesNotExist:
        return None, None, {'status': 'error', 'error': f'Lote {lote_id} not found'}
    
    return user, lote, None


def _create_cacao_image(user, lote, image_data: Dict[str, Any], temp_path: str) -> tuple:
    """Crea la instancia de CacaoImage."""
    with open(temp_path, 'rb') as f:
        file_content = ContentFile(f.read())
        file_content.name = image_data.get('file_name', 'image.jpg')
        
        from images_app.utils import get_tipo_archivo_from_mime_type
        mime_type = image_data.get('file_type', 'image/jpeg')
        tipo_archivo = get_tipo_archivo_from_mime_type(mime_type)
        
        cacao_image = CacaoImage(
            user=user,
            image=file_content,
            file_name=image_data.get('file_name', 'unknown'),
            file_size=image_data.get('file_size', 0),
            file_type=tipo_archivo,
            processed=False,
            lote=lote
        )
        cacao_image.save()
        return cacao_image, None
    
    return None, {'success': False, 'error': 'Error creating image'}

def _process_image_with_ml(predictor, temp_path: str, cacao_image) -> tuple:
    """Procesa la imagen con ML y guarda la predicción."""
    return process_image_prediction(predictor, temp_path, cacao_image)

def _cleanup_temp_file(temp_path: str):
    """Limpia el archivo temporal."""
    import os
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as cleanup_error:
        logger.warning(f"Error cleaning up temp file {temp_path}: {cleanup_error}")

def _calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula las estadísticas de los resultados."""
    stats = calculate_prediction_statistics(results)
    return {
        'avg_confidence': stats['average_confidence'],
        'avg_dimensions': stats['average_dimensions'],
        'total_weight': stats['total_weight']
    }

def _process_single_image(task_instance, image_data, idx, total_images, user, lote, predictor):
    """Process a single image and return result."""
    def safe_update_state(state: str, meta: Dict[str, Any]) -> None:
        """Safely update task state, only if task_id exists (not in test mode)."""
        if task_instance is None:
            return
        if not hasattr(task_instance, 'request') or not getattr(task_instance.request, 'id', None):
            return
        if hasattr(task_instance, 'update_state'):
            task_instance.update_state(state=state, meta=meta)
    
    import os
    try:
        safe_update_state(
            'PROGRESS',
            {
                'current': idx + 1,
                'total': total_images,
                'status': f'Processing image {idx + 1}/{total_images}...'
            }
        )
        
        temp_path = image_data.get('temp_path')
        if not temp_path or not os.path.exists(temp_path):
            return {'success': False, 'error': 'Image file not found'}
        
        with transaction.atomic():
            cacao_image, error = _create_cacao_image(user, lote, image_data, temp_path)
            if error:
                return error
            
            result, _ = _process_image_with_ml(predictor, temp_path, cacao_image)
            _cleanup_temp_file(temp_path)
            return result
            
    except Exception as e:
        logger.error(f"Error processing image {idx + 1}: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

def _process_batch_analysis_impl(
    user_id: int,
    lote_id: int,
    images_data: List[Dict[str, Any]],
    task_instance=None
) -> Dict[str, Any]:
    """
    Internal implementation for processing a batch of images.
    Can be called directly or via Celery task.
    
    Args:
        user_id: ID of the user performing the analysis
        lote_id: ID of the lote to associate images with
        images_data: List of image data dictionaries with:
            - file_name: str
            - file_size: int
            - file_type: str
            - temp_path: str (temporary path to saved image file)
        task_instance: Optional Celery task instance for state updates
    
    Returns:
        Dictionary with processing results
    """
    def safe_update_state(state: str, meta: Dict[str, Any]) -> None:
        """Safely update task state, only if task_id exists (not in test mode)."""
        if task_instance is None:
            return
        if not hasattr(task_instance, 'request') or not getattr(task_instance.request, 'id', None):
            return
        if hasattr(task_instance, 'update_state'):
            task_instance.update_state(state=state, meta=meta)
    
    try:
        start_time = time.time()
        
        safe_update_state(
            'PROGRESS',
            {
                'current': 0,
                'total': len(images_data),
                'status': 'Loading models...'
            }
        )
        
        user, lote, error = _get_user_and_lote(user_id, lote_id)
        if error:
            return error
        
        predictor, error = get_predictor()
        if error:
            return error
        
        results = []
        total_images = len(images_data)
        
        for idx, image_data in enumerate(images_data):
            result = _process_single_image(task_instance, image_data, idx, total_images, user, lote, predictor)
            results.append(result)
        
        processed_images = sum(1 for r in results if r.get('success', False))
        failed_images = total_images - processed_images
        stats = _calculate_statistics(results)
        total_time = time.time() - start_time
        
        return {
            'status': 'completed',
            'lote_id': lote_id,
            'lote_name': lote.identificador if lote else None,
            'total_images': total_images,
            'processed_images': processed_images,
            'failed_images': failed_images,
            'average_confidence': round(stats['avg_confidence'], 3),
            'average_dimensions': stats['avg_dimensions'],
            'total_weight': round(stats['total_weight'], 2),
            'predictions': results,
            'processing_time_seconds': round(total_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis task: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='api.tasks.image.process_batch_analysis')
def process_batch_analysis_task(
    self,
    user_id: int,
    lote_id: int,
    images_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Celery task wrapper for processing a batch of images.
    Calls the internal implementation with the task instance.
    
    Args:
        self: Celery task instance
        user_id: ID of the user performing the analysis
        lote_id: ID of the lote to associate images with
        images_data: List of image data dictionaries
    
    Returns:
        Dictionary with processing results
    """
    return _process_batch_analysis_impl(user_id, lote_id, images_data, task_instance=self)

