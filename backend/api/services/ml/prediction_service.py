"""
Prediction service for ML models in CacaoScan.
Handles all ML prediction-related operations.
"""
import logging
import time
from typing import Dict, Any
from PIL import Image

from ..base import BaseService, ServiceResult, ValidationServiceError
from ml.prediction.predict import get_predictor, load_artifacts

logger = logging.getLogger("cacaoscan.services.ml.prediction")


class PredictionService(BaseService):
    """
    Service for handling ML predictions.
    
    Responsibilities:
    - Loading and managing ML models
    - Performing predictions on images
    - Managing model state and availability
    """
    
    def __init__(self):
        super().__init__()
    
    def get_predictor(self) -> ServiceResult:
        """
        Gets the ML predictor instance.
        
        Returns:
            ServiceResult with predictor instance
        """
        try:
            predictor = get_predictor()
            
            if not predictor.models_loaded:
                # Try to load models automatically
                self.log_info("Models not loaded. Attempting automatic load...")
                success = load_artifacts()
                
                if not success:
                    return ServiceResult.error(
                        ValidationServiceError(
                            "Models not available. Run automatic initialization first.",
                            details={"suggestion": "POST /api/v1/auto-initialize/ to initialize the system"}
                        )
                    )
                
                # Retry getting predictor
                predictor = get_predictor()
                
                if not predictor.models_loaded:
                    return ServiceResult.error(
                        ValidationServiceError("Error loading models after automatic attempt.")
                    )
            
            return ServiceResult.success(
                data=predictor,
                message="Predictor obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting predictor: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting predictor", details={"original_error": str(e)})
            )
    
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
        try:
            predictor = get_predictor()
            
            status_data = {
                'models_loaded': predictor.models_loaded,
                'model_versions': getattr(predictor, 'model_versions', {}),
                'available_targets': getattr(predictor, 'available_targets', []),
                'device': getattr(predictor, 'device', 'unknown')
            }
            
            return ServiceResult.success(
                data=status_data,
                message="Model status obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error checking model status: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error checking model status", details={"original_error": str(e)})
            )

