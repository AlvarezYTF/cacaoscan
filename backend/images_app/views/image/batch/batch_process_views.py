"""
Image processing logic for batch analysis in CacaoScan.
Handles ML prediction processing and statistics calculation.
"""
import logging
import time
import io
from PIL import Image

from api.utils.model_imports import get_models_safely
from training.services import MLService

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

logger = logging.getLogger("cacaoscan.api")


class BatchImageProcessor:
    """
    Helper class for processing images in batch analysis.
    Handles ML predictions and statistics calculation.
    """
    
    @staticmethod
    def _get_predictor():
        """Obtiene el predictor ML."""
        try:
            ml_service = MLService()
            predictor_result = ml_service.get_predictor()
            
            if not predictor_result.success:
                logger.error(f"No se pudieron cargar los modelos ML: {predictor_result.error.message}")
                return None
            
            return predictor_result.data
        except Exception as e:
            logger.error(f"Error obteniendo predictor: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _load_image_for_prediction(image_file, cacao_image):
        """Carga la imagen para predicción desde memoria o disco."""
        try:
            image_file.seek(0)
            image_bytes = image_file.read()
            if image_bytes:
                return Image.open(io.BytesIO(image_bytes))
        except (AttributeError, ValueError, IOError):
            pass
        
        return Image.open(cacao_image.image.path)
    
    @staticmethod
    def _create_prediction(cacao_image, result: dict, prediction_time_ms: int):
        """Crea y guarda la predicción."""
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
    
    @staticmethod
    def _process_single_image(request, image_file, lote, idx: int, predictor) -> dict:
        """Procesa una sola imagen."""
        try:
            cacao_image = CacaoImage(
                user=request.user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False,
                lote=lote,
                variedad=lote.variedad,
                fecha_cosecha=lote.fecha_cosecha
            )
            cacao_image.save()
            
            if not predictor or not predictor.models_loaded:
                return {
                    'success': False,
                    'image_id': cacao_image.id,
                    'error': 'Modelos ML no disponibles'
                }
            
            try:
                pil_image = BatchImageProcessor._load_image_for_prediction(image_file, cacao_image)
                prediction_start = time.time()
                result = predictor.predict(pil_image)
                prediction_time_ms = int((time.time() - prediction_start) * 1000)
                
                BatchImageProcessor._create_prediction(cacao_image, result, prediction_time_ms)
                
                return {
                    'success': True,
                    'image_id': cacao_image.id,
                    'prediction': result
                }
            except Exception as pred_error:
                logger.error(f"Error en predicción de imagen {idx + 1}: {pred_error}", exc_info=True)
                return {
                    'success': False,
                    'image_id': cacao_image.id,
                    'error': str(pred_error)
                }
        except Exception as e:
            logger.error(f"Error procesando imagen {idx + 1}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def process_images_batch(request, images, lote):
        """
        Process multiple images with ML.
        
        Args:
            request: HTTP request object
            images: List of image files
            lote: Lote instance
            
        Returns:
            List of processing results
        """
        predictor = BatchImageProcessor._get_predictor()
        results = []
        
        for idx, image_file in enumerate(images):
            result = BatchImageProcessor._process_single_image(request, image_file, lote, idx, predictor)
            results.append(result)
        
        return results
    
    @staticmethod
    def calculate_stats(results):
        """
        Calculate batch statistics.
        
        Args:
            results: List of processing results
            
        Returns:
            Dictionary with statistics
        """
        total_images = len(results)
        processed_images = sum(1 for r in results if r.get('success', False))
        failed_images = total_images - processed_images
        
        successful_results = [r for r in results if r.get('success', False)]
        
        # Calculate averages
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
                
                # Average confidence
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
        
        return {
            'total_images': total_images,
            'processed_images': processed_images,
            'failed_images': failed_images,
            'average_confidence': round(avg_confidence, 3),
            'average_dimensions': avg_dimensions,
            'total_weight': round(total_weight, 2)
        }

