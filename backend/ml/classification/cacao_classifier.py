"""
Binary classifier for cacao bean detection using example images.

This module provides a CNN-based binary classifier that uses example images
to determine if an uploaded image contains a cacao bean or not.
"""
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import numpy as np

from ..utils.paths import get_artifacts_dir, ensure_dir_exists
from ..utils.logs import get_ml_logger
from ..segmentation.processor import SegmentationError

logger = get_ml_logger("cacaoscan.ml.classification")


class CacaoBinaryClassifier(nn.Module):
    """
    Binary CNN classifier for cacao bean detection.
    
    Uses a pre-trained ResNet18 as backbone and fine-tunes it
    for binary classification (cacao / not cacao).
    """
    
    def __init__(self, num_classes: int = 2):
        """
        Initialize the binary classifier.
        
        Args:
            num_classes: Number of classes (2 for binary: cacao/not_cacao)
        """
        super(CacaoBinaryClassifier, self).__init__()
        
        # Use ResNet18 as backbone
        from torchvision.models import resnet18, ResNet18_Weights
        
        self.backbone = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        
        # Replace the final fully connected layer for binary classification
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.backbone(x)


class CacaoImageClassifier:
    """
    Service class for binary classification of cacao images.
    
    Uses example images to determine if an image contains a cacao bean.
    """
    
    # Default paths
    DEFAULT_MODEL_PATH = "cacao_classifier.pt"
    MIN_CONFIDENCE = 0.90  # Very high threshold to avoid false positives (90%)
    MIN_CACAO_PROBABILITY = 0.85  # Minimum probability of being cacao (85%)
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize the classifier.
        
        Args:
            model_path: Path to the trained model. If None, uses default path.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.model_loaded = False
        
        # Image preprocessing (same as ImageNet)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Determine model path
        if model_path is None:
            artifacts_dir = get_artifacts_dir()
            ensure_dir_exists(artifacts_dir)
            model_path = artifacts_dir / self.DEFAULT_MODEL_PATH
        
        self.model_path = Path(model_path)
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the trained model."""
        try:
            if not self.model_path.exists():
                logger.warning(
                    f"[Clasificador] ⚠️ Modelo no encontrado en {self.model_path}. "
                    "El clasificador no estará disponible. "
                    "Entrena el modelo primero usando: python manage.py train_cacao_classifier"
                )
                self.model_loaded = False
                return
            
            logger.info(f"[Clasificador] Cargando modelo desde {self.model_path}...")
            self.model = CacaoBinaryClassifier(num_classes=2)
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            self.model_loaded = True
            
            logger.info(
                f"[Clasificador] ✅ Modelo cargado exitosamente. "
                f"Umbral de confianza: {self.MIN_CONFIDENCE*100:.0f}%, "
                f"Umbral de probabilidad cacao: {self.MIN_CACAO_PROBABILITY*100:.0f}%"
            )
            
        except Exception as e:
            logger.error(f"[Clasificador] ❌ Error cargando modelo: {e}", exc_info=True)
            self.model_loaded = False
    
    def is_available(self) -> bool:
        """Check if the classifier is available."""
        return self.model_loaded and self.model is not None
    
    def classify(self, image_path: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Classify an image as containing a cacao bean or not.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of:
            - is_cacao: True if image contains a cacao bean
            - confidence: Confidence score (0.0 to 1.0)
            - details: Dictionary with classification details
            
        Raises:
            SegmentationError: If image cannot be processed or is not a cacao bean
        """
        if not self.is_available():
            # If classifier is not available, skip validation (don't block)
            logger.warning("Clasificador no disponible, saltando validación de clasificación")
            return True, 1.0, {"classifier_available": False}
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted_class = torch.max(probabilities, 1)
            
            confidence_score = float(confidence[0])
            is_cacao = predicted_class[0].item() == 1  # Class 1 = cacao, Class 0 = not_cacao
            
            # Get probabilities for both classes
            probs = probabilities[0].cpu().numpy()
            cacao_prob = float(probs[1])
            not_cacao_prob = float(probs[0])
            
            details = {
                "is_cacao": is_cacao,
                "confidence": confidence_score,
                "cacao_probability": cacao_prob,
                "not_cacao_probability": not_cacao_prob,
                "predicted_class": "cacao" if is_cacao else "not_cacao",
                "classifier_available": True
            }
            
            logger.info(
                f"Clasificación: {'CACAO' if is_cacao else 'NO CACAO'}, "
                f"confianza={confidence_score:.3f}, "
                f"prob_cacao={cacao_prob:.3f}, prob_no_cacao={not_cacao_prob:.3f}"
            )
            
            # STRICT VALIDATION: Multiple checks to avoid false positives
            # Check 1: Must be predicted as cacao
            if not is_cacao:
                logger.error(
                    f"[Clasificador] ❌ Rechazado: Predicción='no cacao', "
                    f"confianza={confidence_score:.3f}, prob_cacao={cacao_prob:.3f}"
                )
                raise SegmentationError(
                    f"La imagen no contiene un grano de cacao. "
                    f"El clasificador detectó: 'no cacao' con confianza {confidence_score*100:.1f}%. "
                    f"Probabilidad de cacao: {cacao_prob*100:.1f}%."
                )
            
            # Check 2: Confidence must be high enough
            if confidence_score < self.MIN_CONFIDENCE:
                logger.error(
                    f"[Clasificador] ❌ Rechazado: Confianza insuficiente, "
                    f"confianza={confidence_score:.3f} < {self.MIN_CONFIDENCE:.3f}, "
                    f"prob_cacao={cacao_prob:.3f}"
                )
                raise SegmentationError(
                    f"No se puede confirmar que la imagen contenga un grano de cacao. "
                    f"Confianza de detección: {confidence_score*100:.1f}% "
                    f"(mínimo requerido: {self.MIN_CONFIDENCE*100:.0f}%). "
                    f"Probabilidad de cacao: {cacao_prob*100:.1f}%."
                )
            
            # Check 3: Probability of being cacao must be high enough
            if cacao_prob < self.MIN_CACAO_PROBABILITY:
                logger.error(
                    f"[Clasificador] ❌ Rechazado: Probabilidad de cacao insuficiente, "
                    f"prob_cacao={cacao_prob:.3f} < {self.MIN_CACAO_PROBABILITY:.3f}, "
                    f"confianza={confidence_score:.3f}"
                )
                raise SegmentationError(
                    f"No se puede confirmar que la imagen contenga un grano de cacao. "
                    f"Probabilidad de ser cacao: {cacao_prob*100:.1f}% "
                    f"(mínimo requerido: {self.MIN_CACAO_PROBABILITY*100:.0f}%). "
                    f"Confianza: {confidence_score*100:.1f}%."
                )
            
            # All checks passed
            logger.info(
                f"[Clasificador] ✅ Aceptado: prob_cacao={cacao_prob:.3f}, "
                f"confianza={confidence_score:.3f}, prob_no_cacao={not_cacao_prob:.3f}"
            )
            return True, confidence_score, details
                
        except SegmentationError:
            raise
        except Exception as e:
            logger.error(f"Error en clasificación: {e}", exc_info=True)
            # If classification fails, don't block (fallback to YOLO only)
            logger.warning("Error en clasificación, usando solo validación YOLO")
            return True, 0.5, {"classifier_error": str(e), "classifier_available": False}


# Global instance
_classifier_instance: Optional[CacaoImageClassifier] = None


def get_cacao_classifier() -> Optional[CacaoImageClassifier]:
    """
    Get the global classifier instance (lazy initialization).
    
    Returns:
        CacaoImageClassifier instance or None if not available
    """
    global _classifier_instance
    
    if _classifier_instance is None:
        logger.info("[Clasificador] Inicializando clasificador binario...")
        _classifier_instance = CacaoImageClassifier()
    
    if _classifier_instance.is_available():
        logger.debug("[Clasificador] Clasificador disponible y listo para usar")
        return _classifier_instance
    else:
        logger.warning(
            "[Clasificador] ⚠️ Clasificador no disponible. "
            "Verifica que el modelo esté entrenado y en la ruta correcta."
        )
        return None

