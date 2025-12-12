"""
Interface for predictors.

Defines the contract that all predictor implementations must follow,
following Dependency Inversion principle.
"""
from typing import Protocol, Dict, Any
from PIL import Image


class IPredictor(Protocol):
    """
    Interface for predictors.
    
    Defines the methods that any predictor implementation must provide.
    """
    
    def load_artifacts(self) -> bool:
        """
        Load all artifacts necessary for prediction.
        
        Returns:
            True if artifacts loaded successfully, False otherwise
        """
        ...
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predict dimensions and weight of a cacao bean.
        
        Args:
            image: PIL Image of the cacao bean
            
        Returns:
            Dictionary with predictions and metadata
        """
        ...

