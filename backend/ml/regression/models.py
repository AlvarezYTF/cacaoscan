"""
Modelos CNN para regresiÃ³n de dimensiones y peso de granos de cacao.
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
    logging.warning("timm no estÃ¡ disponible. ConvNeXt no estarÃ¡ disponible.")

from ..utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.regression")


class ResNet18Regression(nn.Module):
    """ResNet18 adaptado para regresiÃ³n de dimensiones de cacao."""
    
    def __init__(
        self,
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.2
    ):
        """
        Inicializa el modelo ResNet18 para regresiÃ³n.
        
        Args:
            num_outputs: NÃºmero de salidas de regresiÃ³n
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
        """
        super(ResNet18Regression, self).__init__()
        
        # Cargar ResNet18 pre-entrenado
        self.backbone = models.resnet18(pretrained=pretrained)
        
        # Obtener nÃºmero de caracterÃ­sticas del Ãºltimo layer
        num_features = self.backbone.fc.in_features
        
        # Reemplazar la capa de clasificaciÃ³n con regresiÃ³n
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
        """Extrae caracterÃ­sticas antes de la capa final."""
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
    """ConvNeXt Tiny adaptado para regresiÃ³n de dimensiones de cacao."""
    
    def __init__(
        self,
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.2
    ):
        """
        Inicializa el modelo ConvNeXt Tiny para regresiÃ³n.
        
        Args:
            num_outputs: NÃºmero de salidas de regresiÃ³n
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
        
        # Obtener nÃºmero de caracterÃ­sticas
        num_features = self.backbone.num_features
        
        # Agregar cabeza de regresiÃ³n
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
        """Extrae caracterÃ­sticas antes de la cabeza de regresiÃ³n."""
        return self.backbone(x)


class MultiHeadRegression(nn.Module):
    """Modelo multi-head para predecir las 4 dimensiones simultÃ¡neamente."""
    
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
            shared_features: Si compartir caracterÃ­sticas entre heads
        """
        super(MultiHeadRegression, self).__init__()
        
        self.backbone_type = backbone_type
        self.shared_features = shared_features
        
        # Crear backbone
        if backbone_type == "resnet18":
            self.backbone = ResNet18Regression(
                num_outputs=1,  # Solo para obtener caracterÃ­sticas
                pretrained=pretrained,
                dropout_rate=0.0  # No dropout en backbone
            )
            # Remover la cabeza de regresiÃ³n del backbone
            self.backbone.backbone.fc = nn.Identity()
            num_features = 512  # TamaÃ±o de caracterÃ­sticas de ResNet18
            
        elif backbone_type == "convnext_tiny":
            if not TIMM_AVAILABLE:
                raise ImportError("timm es requerido para ConvNeXt")
            
            self.backbone = ConvNeXtTinyRegression(
                num_outputs=1,
                pretrained=pretrained,
                dropout_rate=0.0
            )
            # Remover la cabeza de regresiÃ³n del backbone
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
        """Crea una cabeza de regresiÃ³n."""
        if shared:
            # Head compartido con mÃ¡s capacidad
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
        # Extraer caracterÃ­sticas
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
        """Forward pass para un target especÃ­fico."""
        features = self.backbone.get_features(x) if hasattr(self.backbone, 'get_features') else self.backbone(x)
        return self.heads[target](features)


class HybridCacaoRegression(nn.Module):
    """
    Modelo híbrido que fusiona ResNet18 y ConvNeXt con features de píxeles.
    
    Arquitectura:
    - ResNet18: Extrae features visuales (512)
    - ConvNeXt: Extrae features visuales (768)
    - Pixel Features: Features de píxeles (5)
    - Fusion: Concatena todas las features → Regression Head
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
        Inicializa el modelo híbrido.
        
        Args:
            num_outputs: Número de salidas (4: alto, ancho, grosor, peso)
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
            num_pixel_features: Número de features de píxeles (5 por defecto)
            use_pixel_features: Si usar features de píxeles
        """
        super(HybridCacaoRegression, self).__init__()
        
        self.use_pixel_features = use_pixel_features
        
        # Backbone 1: ResNet18
        self.resnet18 = models.resnet18(pretrained=pretrained)
        # Remover capa final y obtener features
        self.resnet18.fc = nn.Identity()
        resnet_features = 512
        
        # Backbone 2: ConvNeXt Tiny
        if not TIMM_AVAILABLE:
            raise ImportError("timm es requerido para ConvNeXt. Instalar con: pip install timm")
        
        self.convnext = timm.create_model(
            'convnext_tiny',
            pretrained=pretrained,
            num_classes=0  # Remover clasificador
        )
        convnext_features = self.convnext.num_features  # 768
        
        # Branch para features de píxeles (si está habilitado)
        if use_pixel_features:
            self.pixel_branch = nn.Sequential(
                nn.Linear(num_pixel_features, 64),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(64, 128),
                nn.ReLU(inplace=True)
            )
            pixel_features = 128
        else:
            pixel_features = 0
        
        # Calcular tamaño total de features fusionadas
        total_features = resnet_features + convnext_features + pixel_features
        
        # Proyección de features para normalizar dimensiones
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
        fused_features = 256 + 256 + pixel_features  # 512 + 128 si usa píxeles, 512 si no
        
        # Capa de fusión
        self.fusion = nn.Sequential(
            nn.Linear(fused_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate)
        )
        
        # Cabeza de regresión
        self.regression_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_outputs)
        )
        
        self.num_outputs = num_outputs
    
    def forward(self, image: torch.Tensor, pixel_features: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass del modelo híbrido.
        
        Args:
            image: Tensor de imagen [batch, 3, 224, 224]
            pixel_features: Tensor de features de píxeles [batch, num_pixel_features] (opcional)
            
        Returns:
            Predicciones [batch, num_outputs]
        """
        # Extraer features de ResNet18
        resnet_feat = self.resnet18(image)  # [batch, 512]
        resnet_feat = self.resnet_projection(resnet_feat)  # [batch, 256]
        
        # Extraer features de ConvNeXt
        convnext_feat = self.convnext(image)  # [batch, 768]
        convnext_feat = self.convnext_projection(convnext_feat)  # [batch, 256]
        
        # Procesar features de píxeles si están disponibles
        if self.use_pixel_features and pixel_features is not None:
            pixel_feat = self.pixel_branch(pixel_features)  # [batch, 128]
            # Concatenar todas las features
            fused = torch.cat([resnet_feat, convnext_feat, pixel_feat], dim=1)  # [batch, 640]
        else:
            # Sin features de píxeles
            fused = torch.cat([resnet_feat, convnext_feat], dim=1)  # [batch, 512]
        
        # Fusionar
        fused = self.fusion(fused)  # [batch, 256]
        
        # Regresión
        output = self.regression_head(fused)  # [batch, num_outputs]
        
        return output
    
    def get_features(self, image: torch.Tensor, pixel_features: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Extrae features antes de la regresión (útil para análisis).
        
        Returns:
            Features fusionadas [batch, 256]
        """
        # Extraer features de ambos backbones
        resnet_feat = self.resnet18(image)
        resnet_feat = self.resnet_projection(resnet_feat)
        
        convnext_feat = self.convnext(image)
        convnext_feat = self.convnext_projection(convnext_feat)
        
        # Procesar features de píxeles si están disponibles
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
    FunciÃ³n de conveniencia para crear modelos.
    
    Args:
        model_type: Tipo de modelo ("resnet18", "convnext_tiny", o "hybrid")
        num_outputs: NÃºmero de salidas (ignorado si multi_head=True o hybrid=True)
        pretrained: Si usar pesos pre-entrenados
        dropout_rate: Tasa de dropout
        multi_head: Si crear modelo multi-head
        hybrid: Si crear modelo híbrido (fusiona ResNet18 + ConvNeXt + Píxeles)
        use_pixel_features: Si usar features de píxeles (solo si hybrid=True)
        
    Returns:
        Modelo creado
    """
    if hybrid:
        # Modelo híbrido que fusiona ResNet18 + ConvNeXt + Píxeles
        return HybridCacaoRegression(
            num_outputs=4 if num_outputs == 1 else num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            use_pixel_features=use_pixel_features
        )
    elif multi_head:
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
        elif model_type == "hybrid":
            # Si se especifica "hybrid" sin flag, crear modelo híbrido
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
    Obtiene informaciÃ³n del modelo.
    
    Args:
        model: Modelo a analizar
        
    Returns:
        Diccionario con informaciÃ³n del modelo
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
    """Cuenta el nÃºmero total de parÃ¡metros del modelo."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# Constantes para targets
TARGETS = ['alto', 'ancho', 'grosor', 'peso']
TARGET_NAMES = {
    'alto': 'Altura (mm)',
    'ancho': 'Ancho (mm)',
    'grosor': 'Grosor (mm)',
    'peso': 'Peso (g)'
}


