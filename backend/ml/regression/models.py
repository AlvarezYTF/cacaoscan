"""
Modelos CNN para regresión de dimensiones y peso de granos de cacao.
"""
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, List, Optional, Tuple, Any
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
        
        # Cargar ResNet18 pre-entrenado (con la nueva API 'weights')
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        
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
        
        # --- CORRECCIÓN: Crear el backbone directamente ---
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
            
            self.backbone = timm.create_model(
                'convnext_tiny',
                pretrained=pretrained,
                num_classes=0  # Remover clasificador
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


class HybridCacaoRegression(nn.Module):
    """
    Modelo hbrido que fusiona ResNet18 y ConvNeXt con features de pxeles.
    
    Arquitectura:
    - ResNet18: Extrae features visuales (512)
    - ConvNeXt: Extrae features visuales (768)
    - Pixel Features: Features de pxeles (5)
    - Fusion: Concatena todas las features  Regression Head
    """
    
    def __init__(
        self,
        num_outputs: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.2,
        num_pixel_features: int = 5,
        use_pixel_features: bool = True
    ):
        """
        Inicializa el modelo hbrido.
        
        Args:
            num_outputs: Nmero de salidas (4: alto, ancho, grosor, peso)
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
            num_pixel_features: Nmero de features de pxeles (5 por defecto)
            use_pixel_features: Si usar features de pxeles
        """
        super(HybridCacaoRegression, self).__init__()
        
        if not TIMM_AVAILABLE:
            raise ImportError("timm es requerido para ConvNeXt. Instalar con: pip install timm")
            
        self.use_pixel_features = use_pixel_features
        
        # Backbone 1: ResNet18
        weights_resnet = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        self.resnet18 = models.resnet18(weights=weights_resnet)
        resnet_features = self.resnet18.fc.in_features # 512
        self.resnet18.fc = nn.Identity()
        
        # Extractor de features para ResNet
        def resnet_extractor(x):
            x = self.resnet18.conv1(x)
            x = self.resnet18.bn1(x)
            x = self.resnet18.relu(x)
            x = self.resnet18.maxpool(x)
            x = self.resnet18.layer1(x)
            x = self.resnet18.layer2(x)
            x = self.resnet18.layer3(x)
            x = self.resnet18.layer4(x)
            x = self.resnet18.avgpool(x)
            return torch.flatten(x, 1)
        self.resnet_feature_extractor = resnet_extractor
        
        # Backbone 2: ConvNeXt Tiny
        self.convnext = timm.create_model(
            'convnext_tiny',
            pretrained=pretrained,
            num_classes=0  # Remover clasificador
        )
        convnext_features = self.convnext.num_features  # 768
        
        # Branch para features de píxeles (si está habilitado)
        pixel_features_dim = 0
        if use_pixel_features:
            self.pixel_branch = nn.Sequential(
                nn.Linear(num_pixel_features, 64),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(64, 128),
                nn.ReLU(inplace=True)
            )
            pixel_features_dim = 128
        
        # Calcular tamaño total de features fusionadas
        total_features = resnet_features + convnext_features + pixel_features_dim
        
        # Proyeccin de features para normalizar dimensiones
        self.resnet_projection = nn.Sequential(
            nn.Linear(resnet_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate)
        )
        
        self.convnext_projection = nn.Sequential(
            nn.Linear(convnext_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate)
        )
        
        # Tamaño después de proyección
        fused_features_dim = 256 + 256 + pixel_features_dim  # 512 + 128 si usa píxeles, 512 si no
        
        # Capa de fusión
        self.fusion = nn.Sequential(
            nn.Linear(fused_features_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate)
        )
        
        # Cabeza de regresin
        self.regression_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_outputs)
        )
        
        self.num_outputs = num_outputs
        logger.info(f"Modelo Híbrido Creado: Fused features dim = {fused_features_dim} (use_pixel_features={use_pixel_features})")
    
    def forward(self, image: torch.Tensor, pixel_features: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Forward pass del modelo hbrido.
        
        Args:
            image: Tensor de imagen [batch, 3, 224, 224]
            pixel_features: Tensor de features de pxeles [batch, num_pixel_features] (opcional)
            
        Returns:
            Diccionario de predicciones (para compatibilidad con el loop de entrenamiento)
        """
        # Extraer features de ResNet18
        resnet_feat = self.resnet_feature_extractor(image)  # [batch, 512]
        resnet_feat = self.resnet_projection(resnet_feat)  # [batch, 256]
        
        # Extraer features de ConvNeXt
        convnext_feat = self.convnext(image)  # [batch, 768]
        convnext_feat = self.convnext_projection(convnext_feat)  # [batch, 256]
        
        # Procesar features de pxeles si estn disponibles
        if self.use_pixel_features and pixel_features is not None:
            pixel_feat = self.pixel_branch(pixel_features)  # [batch, 128]
            # Concatenar todas las features
            fused = torch.cat([resnet_feat, convnext_feat, pixel_feat], dim=1)
        else:
            # Sin features de pxeles
            fused = torch.cat([resnet_feat, convnext_feat], dim=1)  # [batch, 512]
        
        # Fusionar
        fused = self.fusion(fused)  # [batch, 256]
        
        # Regresin
        output = self.regression_head(fused)  # [batch, num_outputs]
        
        return output
    
    def get_features(self, image: torch.Tensor, pixel_features: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Extrae features antes de la regresin (til para anlisis).
        
        Returns:
            Features fusionadas [batch, 256]
        """
        # Extraer features de ambos backbones
        resnet_feat = self.resnet18(image)
        resnet_feat = self.resnet_projection(resnet_feat)
        
        convnext_feat = self.convnext(image)
        convnext_feat = self.convnext_projection(convnext_feat)
        
        # Procesar features de pxeles si estn disponibles
        if self.use_pixel_features and pixel_features is not None:
            pixel_feat = self.pixel_branch(pixel_features)
            fused = torch.cat([resnet_feat, convnext_feat, pixel_feat], dim=1)
        else:
            fused = torch.cat([resnet_feat, convnext_feat], dim=1)
        
        return self.fusion(fused)


def create_model(
    model_type: str = "resnet18",
    num_outputs: int = 1,
    pretrained: bool = True,
    dropout_rate: float = 0.2,
    multi_head: bool = False,
    hybrid: bool = False,
    use_pixel_features: bool = True
) -> nn.Module:
    """
    Función de conveniencia para crear modelos.
    
    Args:
        model_type: Tipo de modelo ("resnet18", "convnext_tiny", o "hybrid")
        num_outputs: Número de salidas (ignorado si multi_head=True o hybrid=True)
        pretrained: Si usar pesos pre-entrenados
        dropout_rate: Tasa de dropout
        multi_head: Si crear modelo multi-head
        hybrid: Si crear modelo hbrido (fusiona ResNet18 + ConvNeXt + Pxeles)
        use_pixel_features: Si usar features de pxeles (solo si hybrid=True)
        
    Returns:
        Modelo creado
    """
    if hybrid:
        # Modelo hbrido que fusiona ResNet18 + ConvNeXt + Pxeles
        return HybridCacaoRegression(
            num_outputs=4, # El modelo híbrido siempre tiene 4 salidas
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            use_pixel_features=use_pixel_features
        )
    elif multi_head:
        logger.info(f"Creando modelo Multi-Head (Backbone: {model_type})")
        return MultiHeadRegression(
            backbone_type=model_type,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            shared_features=True
        )
    else:
        logger.info(f"Creando modelo Individual (Backbone: {model_type}, Outputs: {num_outputs})")
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
        elif model_type == "hybrid":
            # Si se especifica "hybrid" sin flag, crear modelo hbrido
            return HybridCacaoRegression(
                num_outputs=4 if num_outputs == 1 else num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate,
                use_pixel_features=use_pixel_features
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
        'device': next(model.parameters()).device if next(model.parameters(), None) is not None else 'cpu'
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