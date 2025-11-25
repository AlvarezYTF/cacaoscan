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


@shared_task(bind=True, name='api.tasks.image.process_batch_analysis')
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
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': len(images_data),
                'status': 'Loading models...'
            }
        )
        
        # Get user and lote
        from django.contrib.auth import get_user_model
        from django.conf import settings
        from pathlib import Path
        import os
        
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return {
                'status': 'error',
                'error': f'User {user_id} not found'
            }
        
        try:
            lote = Lote.objects.select_related('finca').get(id=lote_id)
        except Lote.DoesNotExist:
            return {
                'status': 'error',
                'error': f'Lote {lote_id} not found'
            }
        
        # Get ML predictor
        ml_service = MLService()
        predictor_result = ml_service.get_predictor()
        
        if not predictor_result.success:
            return {
                'status': 'error',
                'error': f'ML models not available: {predictor_result.error.message}'
            }
        
        predictor = predictor_result.data
        
        if not predictor.models_loaded:
            return {
                'status': 'error',
                'error': 'ML models not loaded'
            }
        
        # Process images
        results = []
        total_images = len(images_data)
        media_root = Path(settings.MEDIA_ROOT)
        
        for idx, image_data in enumerate(images_data):
            try:
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': idx + 1,
                        'total': total_images,
                        'status': f'Processing image {idx + 1}/{total_images}...'
                    }
                )
                
                # Load image from temporary path
                temp_path = image_data.get('temp_path')
                if not temp_path or not os.path.exists(temp_path):
                    results.append({
                        'success': False,
                        'error': 'Image file not found'
                    })
                    continue
                
                # Create CacaoImage instance
                with transaction.atomic():
                    # Read image file
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
                    
                    # Process with ML
                    try:
                        pil_image = Image.open(temp_path)
                        
                        prediction_start = time.time()
                        result = predictor.predict(pil_image)
                        prediction_time_ms = int((time.time() - prediction_start) * 1000)
                        
                        # Save prediction
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
                            device_used=result.get('debug', {}).get('device', 'cpu').split(':')[0] if ':' in str(result.get('debug', {}).get('device', 'cpu')) else 'cpu'
                        )
                        cacao_prediction.save()
                        
                        cacao_image.processed = True
                        cacao_image.save()
                        
                        results.append({
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
                        })
                        
                    except Exception as pred_error:
                        logger.error(f"Error in prediction for image {idx + 1}: {pred_error}", exc_info=True)
                        results.append({
                            'success': False,
                            'image_id': cacao_image.id,
                            'error': str(pred_error)
                        })
                    
                    # Clean up temporary file
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Error cleaning up temp file {temp_path}: {cleanup_error}")
                
            except Exception as e:
                logger.error(f"Error processing image {idx + 1}: {e}", exc_info=True)
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate statistics
        processed_images = sum(1 for r in results if r.get('success', False))
        failed_images = total_images - processed_images
        
        successful_results = [r for r in results if r.get('success', False)]
        
        avg_confidence = 0
        avg_dimensions = {
            'alto': 0,
            'ancho': 0,
            'grosor': 0
        }
        total_weight = 0
        
        if successful_results:
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
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            avg_dimensions = {
                'alto': sum(altos) / len(altos) if altos else 0,
                'ancho': sum(anchos) / len(anchos) if anchos else 0,
                'grosor': sum(grosor) / len(grosor) if grosor else 0
            }
            total_weight = sum(pesos)
        
        total_time = time.time() - start_time
        
        return {
            'status': 'completed',
            'lote_id': lote_id,
            'lote_name': lote.identificador if lote else None,
            'total_images': total_images,
            'processed_images': processed_images,
            'failed_images': failed_images,
            'average_confidence': round(avg_confidence, 3),
            'average_dimensions': avg_dimensions,
            'total_weight': round(total_weight, 2),
            'predictions': results,
            'processing_time_seconds': round(total_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis task: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }

