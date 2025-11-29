"""
Celery tasks for image processing operations in CacaoScan.
Handles heavy image processing operations asynchronously.
"""
import logging
import time
import io
from typing import Dict, Any, List
from PIL import Image
from celery import shared_task
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.db import transaction

from training.services import MLService
from ..utils.model_imports import get_models_safely

logger = logging.getLogger("cacaoscan.api.tasks.image")

# Import models safely
models = get_models_safely({
    'Lote': 'fincas_app.models.Lote',
    'Finca': 'fincas_app.models.Finca',
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
Lote = models['Lote']
Finca = models['Finca']
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']


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

def _get_predictor():
    """Obtiene el predictor ML."""
    ml_service = MLService()
    predictor_result = ml_service.get_predictor()
    
    if not predictor_result.success:
        return None, {'status': 'error', 'error': f'ML models not available: {predictor_result.error.message}'}
    
    predictor = predictor_result.data
    if not predictor.models_loaded:
        return None, {'status': 'error', 'error': 'ML models not loaded'}
    
    return predictor, None

def _create_cacao_image(user, lote, image_data: Dict[str, Any], temp_path: str) -> tuple:
    """Crea la instancia de CacaoImage."""
    with open(temp_path, 'rb') as f:
        file_content = ContentFile(f.read())
        file_content.name = image_data.get('file_name', 'image.jpg')
        
        cacao_image = CacaoImage(
            user=user,
            image=file_content,
            file_name=image_data.get('file_name', 'unknown'),
            file_size=image_data.get('file_size', 0),
            file_type=image_data.get('file_type', 'image/jpeg'),
            processed=False,
            lote=lote,
            variedad=lote.variedad if lote else None,
            fecha_cosecha=lote.fecha_cosecha if lote else None
        )
        cacao_image.save()
        return cacao_image, None
    
    return None, {'success': False, 'error': 'Error creating image'}

def _process_image_with_ml(predictor, temp_path: str, cacao_image) -> tuple:
    """Procesa la imagen con ML y guarda la predicción."""
    try:
        pil_image = Image.open(temp_path)
        prediction_start = time.time()
        result = predictor.predict(pil_image)
        prediction_time_ms = int((time.time() - prediction_start) * 1000)
        
        device = result.get('debug', {}).get('device', 'cpu')
        device_used = device.split(':')[0] if ':' in str(device) else 'cpu'
        
        cacao_prediction = CacaoPrediction(
            image=cacao_image,
            alto_mm=result['alto_mm'],
            ancho_mm=result['ancho_mm'],
            grosor_mm=result['grosor_mm'],
            peso_g=result['peso_g'],
            confidence_alto=result['confidences']['alto'],
            confidence_ancho=result['confidences']['ancho'],
            confidence_grosor=result['confidences']['grosor'],
            confidence_peso=result['confidences']['peso'],
            processing_time_ms=prediction_time_ms,
            crop_url=result.get('crop_url', ''),
            model_version=result.get('debug', {}).get('models_version', 'v1.0'),
            device_used=device_used
        )
        cacao_prediction.save()
        
        cacao_image.processed = True
        cacao_image.save()
        
        return {
            'success': True,
            'image_id': cacao_image.id,
            'prediction': {
                'alto_mm': result['alto_mm'],
                'ancho_mm': result['ancho_mm'],
                'grosor_mm': result['grosor_mm'],
                'peso_g': result['peso_g'],
                'confidences': result['confidences'],
                'crop_url': result.get('crop_url', ''),
                'model_version': result.get('debug', {}).get('models_version', 'v1.0'),
                'processing_time_ms': prediction_time_ms
            }
        }, None
    except Exception as pred_error:
        logger.error(f"Error in prediction: {pred_error}", exc_info=True)
        return {
            'success': False,
            'image_id': cacao_image.id,
            'error': str(pred_error)
        }, None

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
    successful_results = [r for r in results if r.get('success', False)]
    
    if not successful_results:
        return {
            'avg_confidence': 0,
            'avg_dimensions': {'alto': 0, 'ancho': 0, 'grosor': 0},
            'total_weight': 0
        }
    
    confidences = []
    altos = []
    anchos = []
    grosor = []
    pesos = []
    
    for r in successful_results:
        pred = r.get('prediction', {})
        conf = pred.get('confidences', {})
        
        avg_conf = sum([
            conf.get('alto', 0),
            conf.get('ancho', 0),
            conf.get('grosor', 0),
            conf.get('peso', 0)
        ]) / 4
        confidences.append(avg_conf)
        
        altos.append(pred.get('alto_mm', 0))
        anchos.append(pred.get('ancho_mm', 0))
        grosor.append(pred.get('grosor_mm', 0))
        pesos.append(pred.get('peso_g', 0))
    
    return {
        'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
        'avg_dimensions': {
            'alto': sum(altos) / len(altos) if altos else 0,
            'ancho': sum(anchos) / len(anchos) if anchos else 0,
            'grosor': sum(grosor) / len(grosor) if grosor else 0
        },
        'total_weight': sum(pesos)
    }

def process_batch_analysis_task(
    self,
    user_id: int,
    lote_id: int,
    images_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process a batch of images with ML predictions asynchronously.
    
    Args:
        user_id: ID of the user performing the analysis
        lote_id: ID of the lote to associate images with
        images_data: List of image data dictionaries with:
            - file_name: str
            - file_size: int
            - file_type: str
            - temp_path: str (temporary path to saved image file)
    
    Returns:
        Dictionary with processing results
    """
    try:
        start_time = time.time()
        import os
        
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': len(images_data),
                'status': 'Loading models...'
            }
        )
        
        user, lote, error = _get_user_and_lote(user_id, lote_id)
        if error:
            return error
        
        predictor, error = _get_predictor()
        if error:
            return error
        
        results = []
        total_images = len(images_data)
        
        for idx, image_data in enumerate(images_data):
            try:
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': idx + 1,
                        'total': total_images,
                        'status': f'Processing image {idx + 1}/{total_images}...'
                    }
                )
                
                temp_path = image_data.get('temp_path')
                if not temp_path or not os.path.exists(temp_path):
                    results.append({
                        'success': False,
                        'error': 'Image file not found'
                    })
                    continue
                
                with transaction.atomic():
                    cacao_image, error = _create_cacao_image(user, lote, image_data, temp_path)
                    if error:
                        results.append(error)
                        continue
                    
                    result, _ = _process_image_with_ml(predictor, temp_path, cacao_image)
                    results.append(result)
                
                _cleanup_temp_file(temp_path)
                
            except Exception as e:
                logger.error(f"Error processing image {idx + 1}: {e}", exc_info=True)
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
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

