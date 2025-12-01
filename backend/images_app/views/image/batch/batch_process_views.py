"""
Image processing logic for batch analysis in CacaoScan.
Handles ML prediction processing and statistics calculation.
"""
import logging
import time
from PIL import Image

from api.utils.model_imports import get_models_safely
from api.utils.ml_helpers import (
    get_predictor,
    load_image_for_prediction,
    create_prediction_from_result,
    calculate_prediction_statistics,
    process_image_prediction
)

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage'
})
CacaoImage = models['CacaoImage']

logger = logging.getLogger("cacaoscan.api")


class BatchImageProcessor:
    """
    Helper class for processing images in batch analysis.
    Handles ML predictions and statistics calculation.
    """
    
    
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
                pil_image = load_image_for_prediction(image_file, cacao_image)
                prediction_start = time.time()
                result_dict, error = process_image_prediction(
                    predictor,
                    pil_image,
                    cacao_image,
                    prediction_start_time=prediction_start
                )
                
                if error or not result_dict.get('success', False):
                    return {
                        'success': False,
                        'image_id': cacao_image.id,
                        'error': error or result_dict.get('error', 'Unknown error')
                    }
                
                return result_dict
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
        predictor, error = get_predictor()
        if error:
            logger.error(f"Error obteniendo predictor: {error.get('error', 'Unknown error')}")
            predictor = None
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
        return calculate_prediction_statistics(results)

