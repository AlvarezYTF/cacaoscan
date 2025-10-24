"""
Modelos CNN para regresión de dimensiones y peso de granos de cacao.
"""
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, List, Optional, Tuple
import logging

try:
    import timm
    TIMM_AVAILABLE = True
except ImportError:
    TIMM_AVAILABLE = False
    logging.warning("timm no está disponible. ConvNeXt no estará disponible.")

from ..utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.regression")


class ResNet18Regression(nn.Module):
    """ResNet18 adaptado para regresión de dimensiones de cacao."""
    
    def __init__(
        self,
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.2
    ):
        """
        Inicializa el modelo ResNet18 para regresión.
        
        Args:
            num_outputs: Número de salidas de regresión
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
        """
        super(ResNet18Regression, self).__init__()
        
        # Cargar ResNet18 pre-entrenado
        self.backbone = models.resnet18(pretrained=pretrained)
        
        # Obtener número de características del último layer
        num_features = self.backbone.fc.in_features
        
        # Reemplazar la capa de clasificación con regresión
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_outputs)
        )
        
        self.num_outputs = num_outputs
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass del modelo."""
        return self.backbone(x)
    
    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extrae características antes de la capa final."""
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)
        
        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)
        
        x = self.backbone.avgpool(x)
        x = torch.flatten(x, 1)
        
        return x


class ConvNeXtTinyRegression(nn.Module):
    """ConvNeXt Tiny adaptado para regresión de dimensiones de cacao."""
    
    def __init__(
        self,
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.2
    ):
        """
        Inicializa el modelo ConvNeXt Tiny para regresión.
        
        Args:
            num_outputs: Número de salidas de regresión
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
        """
        super(ConvNeXtTinyRegression, self).__init__()
        
        if not TIMM_AVAILABLE:
            raise ImportError("timm es requerido para ConvNeXt. Instalar con: pip install timm")
        
        # Cargar ConvNeXt Tiny pre-entrenado
        self.backbone = timm.create_model(
            'convnext_tiny',
            pretrained=pretrained,
            num_classes=0  # Remover clasificador
        )
        
        # Obtener número de características
        num_features = self.backbone.num_features
        
        # Agregar cabeza de regresión
        self.regression_head = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_outputs)
        )
        
        self.num_outputs = num_outputs
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass del modelo."""
        features = self.backbone(x)
        return self.regression_head(features)
    
    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extrae características antes de la cabeza de regresión."""
        return self.backbone(x)


class MultiHeadRegression(nn.Module):
    """Modelo multi-head para predecir las 4 dimensiones simultáneamente."""
    
    def __init__(
        self,
        backbone_type: str = "resnet18",
        pretrained: bool = True,
        dropout_rate: float = 0.2,
        shared_features: bool = True
    ):
        """
        Inicializa el modelo multi-head.
        
        Args:
            backbone_type: Tipo de backbone ("resnet18" o "convnext_tiny")
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
            shared_features: Si compartir características entre heads
        """
        super(MultiHeadRegression, self).__init__()
        
        self.backbone_type = backbone_type
        self.shared_features = shared_features
        
        # Crear backbone
        if backbone_type == "resnet18":
            self.backbone = ResNet18Regression(
                num_outputs=1,  # Solo para obtener características
                pretrained=pretrained,
                dropout_rate=0.0  # No dropout en backbone
            )
            # Remover la cabeza de regresión del backbone
            self.backbone.backbone.fc = nn.Identity()
            num_features = 512  # Tamaño de características de ResNet18
            
        elif backbone_type == "convnext_tiny":
            if not TIMM_AVAILABLE:
                raise ImportError("timm es requerido para ConvNeXt")
            
            self.backbone = ConvNeXtTinyRegression(
                num_outputs=1,
                pretrained=pretrained,
                dropout_rate=0.0
            )
            # Remover la cabeza de regresión del backbone
            self.backbone.regression_head = nn.Identity()
            num_features = self.backbone.backbone.num_features
            
        else:
            raise ValueError(f"Backbone tipo '{backbone_type}' no soportado")
        
        # Crear heads individuales para cada target
        self.heads = nn.ModuleDict({
            'alto': self._create_head(num_features, dropout_rate),
            'ancho': self._create_head(num_features, dropout_rate),
            'grosor': self._create_head(num_features, dropout_rate),
            'peso': self._create_head(num_features, dropout_rate)
        })
        
        # Head compartido si se especifica
        if shared_features:
            self.shared_head = self._create_head(num_features, dropout_rate, shared=True)
        else:
            self.shared_head = None
    
    def _create_head(self, num_features: int, dropout_rate: float, shared: bool = False) -> nn.Module:
        """Crea una cabeza de regresión."""
        if shared:
            # Head compartido con más capacidad
            return nn.Sequential(
                nn.Dropout(dropout_rate),
                nn.Linear(num_features, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(512, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(256, 4)  # 4 salidas: alto, ancho, grosor, peso
            )
        else:
            # Head individual
            return nn.Sequential(
                nn.Dropout(dropout_rate),
                nn.Linear(num_features, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(256, 64),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(64, 1)
            )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass del modelo."""
        # Extraer características
        features = self.backbone.get_features(x) if hasattr(self.backbone, 'get_features') else self.backbone(x)
        
        if self.shared_features and self.shared_head is not None:
            # Usar head compartido
            shared_output = self.shared_head(features)
            return {
                'alto': shared_output[:, 0:1],
                'ancho': shared_output[:, 1:2],
                'grosor': shared_output[:, 2:3],
                'peso': shared_output[:, 3:4]
            }
        else:
            # Usar heads individuales
            outputs = {}
            for target, head in self.heads.items():
                outputs[target] = head(features)
            return outputs
    
    def forward_single(self, x: torch.Tensor, target: str) -> torch.Tensor:
        """Forward pass para un target específico."""
        features = self.backbone.get_features(x) if hasattr(self.backbone, 'get_features') else self.backbone(x)
        return self.heads[target](features)


def create_model(
    model_type: str = "resnet18",
    num_outputs: int = 1,
    pretrained: bool = True,
    dropout_rate: float = 0.2,
    multi_head: bool = False
) -> nn.Module:
    """
    Función de conveniencia para crear modelos.
    
    Args:
        model_type: Tipo de modelo ("resnet18" o "convnext_tiny")
        num_outputs: Número de salidas (ignorado si multi_head=True)
        pretrained: Si usar pesos pre-entrenados
        dropout_rate: Tasa de dropout
        multi_head: Si crear modelo multi-head
        
    Returns:
        Modelo creado
    """
    if multi_head:
        return MultiHeadRegression(
            backbone_type=model_type,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            shared_features=True
        )
    else:
        if model_type == "resnet18":
            return ResNet18Regression(
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
        elif model_type == "convnext_tiny":
            return ConvNeXtTinyRegression(
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
        else:
            raise ValueError(f"Tipo de modelo '{model_type}' no soportado")


def get_model_info(model: nn.Module) -> Dict[str, any]:
    """
    Obtiene información del modelo.
    
    Args:
        model: Modelo a analizar
        
    Returns:
        Diccionario con información del modelo
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'model_type': type(model).__name__,
        'device': next(model.parameters()).device
    }


def count_parameters(model: nn.Module) -> int:
    """Cuenta el número total de parámetros del modelo."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# Constantes para targets
TARGETS = ['alto', 'ancho', 'grosor', 'peso']
TARGET_NAMES = {
    'alto': 'Altura (mm)',
    'ancho': 'Ancho (mm)',
    'grosor': 'Grosor (mm)',
    'peso': 'Peso (g)'
}
