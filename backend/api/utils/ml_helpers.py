"""
Shared ML utilities for image processing and prediction.
Contains common functions for ML predictor access and statistics calculation.
"""
import logging
import time
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import io

from training.services import MLService
from ..utils.model_imports import get_models_safely

logger = logging.getLogger("cacaoscan.api.utils.ml_helpers")

# Import models safely
models = get_models_safely({
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoPrediction = models['CacaoPrediction']


def get_predictor() -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Gets the ML predictor.
    
    Returns:
        Tuple of (predictor, error_dict). If successful, predictor is not None and error_dict is None.
        If failed, predictor is None and error_dict contains error information.
    """
    try:
        ml_service = MLService()
        predictor_result = ml_service.get_predictor()
        
        if not predictor_result.success:
            error_msg = f"ML models not available: {predictor_result.error.message}"
            logger.error(f"No se pudieron cargar los modelos ML: {predictor_result.error.message}")
            return None, {'status': 'error', 'error': error_msg}
        
        predictor = predictor_result.data
        if not predictor.models_loaded:
            error_msg = 'ML models not loaded'
            logger.error(error_msg)
            return None, {'status': 'error', 'error': error_msg}
        
        return predictor, None
    except Exception as e:
        logger.error(f"Error obteniendo predictor: {e}", exc_info=True)
        return None, {'status': 'error', 'error': str(e)}


def load_image_for_prediction(image_file, cacao_image) -> Image.Image:
    """
    Loads image for prediction from memory or disk.
    
    Args:
        image_file: File object or path
        cacao_image: CacaoImage instance
        
    Returns:
        PIL Image object
    """
    try:
        if hasattr(image_file, 'seek') and hasattr(image_file, 'read'):
            image_file.seek(0)
            image_bytes = image_file.read()
            if image_bytes:
                return Image.open(io.BytesIO(image_bytes))
    except (AttributeError, ValueError, IOError):
        pass
    
    return Image.open(cacao_image.image.path)


def get_tipo_dispositivo_from_code(codigo: str):
    """Get Parametro (TEMA_TIPO_DISPOSITIVO) from code string."""
    from api.utils.model_imports import get_model_safely
    Parametro = get_model_safely('catalogos.models.Parametro')
    Tema = get_model_safely('catalogos.models.Tema')
    
    if not Parametro or not Tema:
        return None
    
    # Get TEMA_TIPO_DISPOSITIVO theme
    try:
        tema_tipo_dispositivo = Tema.objects.get(codigo='TEMA_TIPO_DISPOSITIVO')
    except Tema.DoesNotExist:
        return None
    
    codigo_upper = codigo.strip().upper()
    device_map = {
        'CPU': 'CPU',
        'CUDA': 'CUDA',
        'MPS': 'MPS',
    }
    codigo_mapped = device_map.get(codigo_upper, codigo_upper)
    
    try:
        return Parametro.objects.get(tema=tema_tipo_dispositivo, codigo=codigo_mapped, activo=True)
    except Parametro.DoesNotExist:
        # Default to CPU
        try:
            return Parametro.objects.get(tema=tema_tipo_dispositivo, codigo='CPU', activo=True)
        except Parametro.DoesNotExist:
            return None


def get_version_modelo_from_code(codigo: str):
    """Get Parametro (TEMA_VERSION_MODELO) from code string."""
    from api.utils.model_imports import get_model_safely
    Parametro = get_model_safely('catalogos.models.Parametro')
    Tema = get_model_safely('catalogos.models.Tema')
    
    if not Parametro or not Tema:
        return None
    
    # Get TEMA_VERSION_MODELO theme
    try:
        tema_version_modelo = Tema.objects.get(codigo='TEMA_VERSION_MODELO')
    except Tema.DoesNotExist:
        return None
    
    codigo_clean = codigo.strip()
    
    try:
        return Parametro.objects.get(tema=tema_version_modelo, codigo=codigo_clean, activo=True)
    except Parametro.DoesNotExist:
        # Try to create if it doesn't exist (for dynamic versions)
        try:
            return Parametro.objects.create(
                tema=tema_version_modelo,
                codigo=codigo_clean,
                nombre=codigo_clean,
                descripcion=f'Versión {codigo_clean} del modelo',
                activo=True
            )
        except Exception:
            # Default to v1.0
            try:
                return Parametro.objects.get(tema=tema_version_modelo, codigo='v1.0', activo=True)
            except Parametro.DoesNotExist:
                return None


def create_prediction_from_result(
    cacao_image,
    result: Dict[str, Any],
    prediction_time_ms: int
) -> CacaoPrediction:
    """
    Creates and saves a CacaoPrediction from prediction result.
    
    Args:
        cacao_image: CacaoImage instance
        result: Prediction result dictionary
        prediction_time_ms: Prediction time in milliseconds
        
    Returns:
        Created CacaoPrediction instance
    """
    device = result.get('debug', {}).get('device', 'cpu')
    device_code = device.split(':')[0] if ':' in str(device) else 'cpu'
    device_used = get_tipo_dispositivo_from_code(device_code)
    
    model_version_code = result.get('debug', {}).get('models_version', 'v1.0')
    model_version = get_version_modelo_from_code(model_version_code)
    
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
        model_version=model_version,
        device_used=device_used
    )
    cacao_prediction.save()
    cacao_image.processed = True
    cacao_image.save()
    
    return cacao_prediction


def calculate_prediction_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates statistics from prediction results.
    
    Args:
        results: List of processing results with 'success' and 'prediction' keys
        
    Returns:
        Dictionary with statistics:
        - total_images: Total number of images
        - processed_images: Number of successful predictions
        - failed_images: Number of failed predictions
        - average_confidence: Average confidence across all predictions
        - average_dimensions: Dict with average alto, ancho, grosor
        - total_weight: Total weight sum
    """
    successful_results = [r for r in results if r.get('success', False)]
    
    if not successful_results:
        return {
            'total_images': len(results),
            'processed_images': 0,
            'failed_images': len(results),
            'average_confidence': 0,
            'average_dimensions': {'alto': 0, 'ancho': 0, 'grosor': 0},
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
    
    total_images = len(results)
    processed_images = len(successful_results)
    failed_images = total_images - processed_images
    
    return {
        'total_images': total_images,
        'processed_images': processed_images,
        'failed_images': failed_images,
        'average_confidence': round(sum(confidences) / len(confidences) if confidences else 0, 3),
        'average_dimensions': {
            'alto': round(sum(altos) / len(altos) if altos else 0, 2),
            'ancho': round(sum(anchos) / len(anchos) if anchos else 0, 2),
            'grosor': round(sum(grosor) / len(grosor) if grosor else 0, 2)
        },
        'total_weight': round(sum(pesos), 2)
    }


def process_image_prediction(
    predictor,
    image_source,
    cacao_image,
    prediction_start_time: Optional[float] = None
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Processes image with ML predictor and creates prediction.
    
    If prediction fails due to SegmentationError (no cacao bean detected),
    the image is deleted and no data is returned.
    
    Args:
        predictor: ML predictor instance
        image_source: PIL Image or path to image file
        cacao_image: CacaoImage instance
        prediction_start_time: Optional start time for prediction (defaults to current time)
        
    Returns:
        Tuple of (result_dict, error_string). If successful, result_dict has 'success': True.
        If SegmentationError occurs, image is deleted and error is returned.
    """
    try:
        if isinstance(image_source, str):
            pil_image = Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            pil_image = image_source
        else:
            pil_image = load_image_for_prediction(image_source, cacao_image)
        
        start_time = prediction_start_time if prediction_start_time is not None else time.time()
        result = predictor.predict(pil_image)
        prediction_time_ms = int((time.time() - start_time) * 1000)
        
        create_prediction_from_result(cacao_image, result, prediction_time_ms)
        
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
        # Check if it's a SegmentationError (no cacao bean detected)
        from ml.segmentation.processor import SegmentationError
        if isinstance(pred_error, SegmentationError):
            logger.error(f"No se detectó un grano de cacao en la imagen {cacao_image.id}: {pred_error}")
            # Delete the image since it's not a valid cacao bean
            try:
                if cacao_image.image:
                    cacao_image.image.delete(save=False)
                cacao_image.delete()
                logger.info(f"Imagen {cacao_image.id} eliminada porque no contiene un grano de cacao válido")
            except Exception as delete_error:
                logger.warning(f"Error eliminando imagen {cacao_image.id}: {delete_error}")
        
        logger.error(f"Error in prediction: {pred_error}", exc_info=True)
        return {
            'success': False,
            'image_id': cacao_image.id if cacao_image and hasattr(cacao_image, 'id') else None,
            'error': str(pred_error)
        }, str(pred_error)

