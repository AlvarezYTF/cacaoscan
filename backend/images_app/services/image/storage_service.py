"""
Image storage service for CacaoScan.
Handles image and prediction persistence operations.
"""
import logging
from typing import Dict, Any
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

logger = logging.getLogger("cacaoscan.services.image.storage")


class ImageStorageService(BaseService):
    """
    Service for handling image and prediction storage operations.
    
    Responsibilities:
    - Saving uploaded images to database
    - Saving predictions to database
    - Managing image-prediction relationships
    """
    
    def __init__(self):
        super().__init__()
    
    def save_uploaded_image(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Saves an uploaded image to the database.
        
        Args:
            image_file: Uploaded image file
            user: User who uploaded the image
            
        Returns:
            ServiceResult with saved CacaoImage instance
        """
        try:
            cacao_image = CacaoImage(
                user=user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False
            )
            
            cacao_image.save()
            
            # Invalidar cache de validación de dataset cuando se crean nuevas imágenes
            try:
                from core.utils import invalidate_dataset_validation_cache, invalidate_system_stats_cache
                invalidate_dataset_validation_cache()
                invalidate_system_stats_cache()
            except Exception as e:
                self.log_warning(f"Error invalidating cache after image save: {e}")
            
            self.log_info(f"Image saved with ID {cacao_image.id} for user {user.username}")
            
            return ServiceResult.success(
                data=cacao_image,
                message="Image saved successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error saving image: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error saving image", details={"original_error": str(e)})
            )
    
    def save_uploaded_image_with_segmentation(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Saves an uploaded image and performs segmentation.
        
        Args:
            image_file: Uploaded image file
            user: User who uploaded the image
            
        Returns:
            ServiceResult with saved CacaoImage instance and processed PNG path
        """
        try:
            from pathlib import Path
            from ml.segmentation.processor import segment_and_crop_cacao_bean
            
            # Create image
            cacao_image = CacaoImage(
                user=user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False
            )
            
            cacao_image.save()
            
            # Invalidar cache de validación de dataset cuando se crean nuevas imágenes
            try:
                from core.utils import invalidate_dataset_validation_cache, invalidate_system_stats_cache
                invalidate_dataset_validation_cache()
                invalidate_system_stats_cache()
            except Exception as e:
                self.log_warning(f"Error invalidating cache after image save: {e}")
            
            self.log_info(f"Image saved with ID {cacao_image.id} for user {user.username}")
            
            # Segment and save transparent PNG of the bean
            processed_png_path = None
            try:
                generated_path = segment_and_crop_cacao_bean(str(cacao_image.image.path), method="opencv")
                if generated_path:
                    processed_png_path = Path(generated_path)
                    self.log_info(f"Segmented PNG saved at: {processed_png_path.absolute()}")
                else:
                    self.log_warning(f"Could not segment image {cacao_image.id}: empty return")
            except Exception as seg_error:
                self.log_error(f"Error segmenting image {cacao_image.id}: {seg_error}")
            
            return ServiceResult.success(
                data={
                    'cacao_image': cacao_image,
                    'processed_png_path': processed_png_path
                },
                message="Image saved and segmented successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error saving image: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error saving image", details={"original_error": str(e)})
            )
    
    def save_prediction(self, cacao_image: CacaoImage, prediction_result: Dict[str, Any], processing_time_ms: int) -> ServiceResult:
        """
        Saves a prediction to the database.
        
        Args:
            cacao_image: CacaoImage instance
            prediction_result: Prediction result dictionary
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            ServiceResult with saved CacaoPrediction instance
        """
        try:
            # Calculate average confidence
            confidences = prediction_result['confidences']
            avg_confidence = sum(confidences.values()) / len(confidences)
            
            prediction = CacaoPrediction(
                image=cacao_image,
                alto_mm=prediction_result['alto_mm'],
                ancho_mm=prediction_result['ancho_mm'],
                grosor_mm=prediction_result['grosor_mm'],
                peso_g=prediction_result['peso_g'],
                average_confidence=avg_confidence,
                processing_time_ms=processing_time_ms,
                crop_url=prediction_result.get('crop_url', ''),
                debug_info=prediction_result.get('debug', {})
            )
            
            prediction.save()
            
            # Mark image as processed
            cacao_image.processed = True
            cacao_image.save()
            
            # Invalidar cache de estadísticas cuando se crean nuevas predicciones
            try:
                from core.utils import invalidate_system_stats_cache
                invalidate_system_stats_cache()
            except Exception as e:
                self.log_warning(f"Error invalidating cache after prediction save: {e}")
            
            self.log_info(f"Prediction saved with ID {prediction.id}")
            
            return ServiceResult.success(
                data=prediction,
                message="Prediction saved successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error saving prediction: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error saving prediction", details={"original_error": str(e)})
            )

