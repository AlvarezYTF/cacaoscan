"""
Base abstract predictor class for cacao regression models.

This module provides a base class that extracts common functionality
from different predictor implementations, following SOLID principles:
- Single Responsibility: Each predictor handles one prediction strategy
- Open/Closed: Base class is open for extension, closed for modification
- Liskov Substitution: All predictors can be used interchangeably
- Interface Segregation: Abstract methods define minimal required interface
- Dependency Inversion: Depends on abstractions (nn.Module, Image)
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
import torchvision.transforms as transforms

from ..utils.logs import get_ml_logger
from ..regression.scalers import CacaoScalers
from .interfaces import IPredictor

logger = get_ml_logger("cacaoscan.ml.prediction.base_predictor")


class PredictorBase(ABC, IPredictor):
    """
    Abstract base class for cacao regression predictors.
    
    This class provides common functionality for:
    - Device management (GPU/CPU)
    - Model and scaler loading
    - Image preprocessing
    - Basic prediction structure
    
    Subclasses must implement:
    - load_artifacts() - Load models and scalers
    - predict() - Main prediction method
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        image_size: Tuple[int, int] = (224, 224),
        imagenet_mean: Optional[list] = None,
        imagenet_std: Optional[list] = None
    ):
        """
        Initialize base predictor.
        
        Args:
            confidence_threshold: Confidence threshold for predictions
            image_size: Target image size for preprocessing
            imagenet_mean: ImageNet mean values for normalization
            imagenet_std: ImageNet std values for normalization
        """
        self.confidence_threshold = confidence_threshold
        self.device = self._get_device()
        self.models_loaded = False
        
        # Image preprocessing configuration
        self.image_size = image_size
        self.imagenet_mean = imagenet_mean or [0.485, 0.456, 0.406]
        self.imagenet_std = imagenet_std or [0.229, 0.224, 0.225]
        
        # Setup image transform
        self._image_transform = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.imagenet_mean, std=self.imagenet_std)
        ])
        
        # Model and scaler storage (to be set by subclasses)
        self.regression_model: Optional[nn.Module] = None
        self.scalers: Optional[CacaoScalers] = None
        
        logger.info(f"PredictorBase initialized (device={self.device})")
    
    def _get_device(self) -> torch.device:
        """
        Get available device (GPU/CPU).
        
        Returns:
            torch.device instance
        """
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
            logger.info("Using CPU")
        return device
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess image for regression models.
        
        Args:
            image: PIL Image to preprocess
            
        Returns:
            Preprocessed tensor ready for model input
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        tensor = self._image_transform(image)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        tensor = tensor.to(self.device)
        return tensor
    
    def _denormalize_predictions(
        self,
        normalized_values: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Denormalize a dictionary of predicted values using scalers.
        
        Args:
            normalized_values: Dictionary of normalized predictions
            
        Returns:
            Dictionary of denormalized predictions
            
        Raises:
            ValueError: If scalers are not available
        """
        if not self.scalers:
            raise ValueError("No scalers available for denormalization")
        
        from ..regression.models import TARGETS
        
        # Convert to numpy arrays (required by inverse_transform)
        temp_data = {
            target: np.array([normalized_values[target]], dtype=np.float32)
            for target in TARGETS
            if target in normalized_values
        }
        
        denorm_data = self.scalers.inverse_transform(temp_data)
        denormalized_predictions = {
            target: float(denorm_data[target][0])
            for target in TARGETS
            if target in denorm_data
        }
        
        return denormalized_predictions
    
    def _validate_models_loaded(self) -> None:
        """
        Validate that models are loaded before prediction.
        
        Raises:
            ValueError: If models are not loaded
        """
        if not self.models_loaded:
            raise ValueError(
                "Models not loaded. Call load_artifacts() first."
            )
    
    def get_device(self) -> torch.device:
        """
        Get the current device.
        
        Returns:
            torch.device instance
        """
        return self.device
    
    def is_models_loaded(self) -> bool:
        """
        Check if models are loaded.
        
        Returns:
            True if models are loaded, False otherwise
        """
        return self.models_loaded
    
    @abstractmethod
    def load_artifacts(self) -> bool:
        """
        Load all artifacts necessary for prediction.
        
        Returns:
            True if artifacts loaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predict dimensions and weight of a cacao bean.
        
        Args:
            image: PIL Image of the cacao bean
            
        Returns:
            Dictionary with predictions and metadata
        """
        pass
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predict from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary with predictions and metadata
            
        Raises:
            InvalidImageError: If image cannot be processed
        """
        import io
        from .predict import InvalidImageError  # type: ignore
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return self.predict(image)
        except Exception as e:
            logger.error(f"Error processing image from bytes: {e}", exc_info=True)
            raise InvalidImageError(f"Error processing image: {e}") from e

