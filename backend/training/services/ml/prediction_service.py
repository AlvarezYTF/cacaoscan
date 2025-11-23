"""
Prediction service for ML models in CacaoScan.
Handles all ML prediction-related operations.
"""
import logging
import time
from typing import Dict, Any
from PIL import Image

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from .ml_service import MLService

logger = logging.getLogger("cacaoscan.services.ml.prediction")


class PredictionService(BaseService):
    """
    Service for handling ML predictions.
    
    Responsibilities:
    - Performing predictions on images
    - Managing prediction workflow
    
    Note: Model loading is handled by MLService to ensure singleton pattern.
    """
    
    def __init__(self):
        super().__init__()
        self.ml_service = MLService()
    
    def get_predictor(self) -> ServiceResult:
        """
        Gets the ML predictor instance.
        
        Uses MLService to ensure models are loaded only once.
        
        Returns:
            ServiceResult with predictor instance
        """
        return self.ml_service.get_predictor()
    
    def predict(self, image: Image.Image) -> ServiceResult:
        """
        Performs prediction on an image.
        
        Args:
            image: PIL Image object to predict on
            
        Returns:
            ServiceResult with prediction results
        """
        try:
            # Get predictor
            predictor_result = self.get_predictor()
            if not predictor_result.success:
                return predictor_result
            
            predictor = predictor_result.data
            
            # Perform prediction
            prediction_start = time.time()
            result = predictor.predict(image)
            prediction_time_ms = int((time.time() - prediction_start) * 1000)
            
            # Add processing time to result
            result['processing_time_ms'] = prediction_time_ms
            
            self.log_info(f"Prediction completed in {prediction_time_ms}ms")
            
            return ServiceResult.success(
                data=result,
                message="Prediction completed successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error performing prediction: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error during prediction", details={"original_error": str(e)})
            )
    
    def check_models_status(self) -> ServiceResult:
        """
        Checks the status of ML models.
        
        Returns:
            ServiceResult with model status information
        """
        return self.ml_service.get_model_status()

