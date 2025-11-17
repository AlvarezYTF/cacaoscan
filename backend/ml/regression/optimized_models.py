"""
Modelos de regresión optimizados para CacaoScan.

Mejoras implementadas:
- Batch Normalization en capas fully connected
- Inicialización de pesos adecuada
- Arquitectura más simple y robusta
- Head de regresión optimizada para 4 salidas
- Mejor manejo de gradientes
"""
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Optional, Tuple
import logging

try:
    import timm
    TIMM_AVAILABLE = True
except ImportError:
    TIMM_AVAILABLE = False
    logging.warning("timm no está disponible. ConvNeXt no estará disponible.")

from ..utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.regression.optimized")


def init_weights(m: nn.Module) -> None:
    """
    Inicializa los pesos de las capas fully connected.
    
    Args:
        m: Módulo a inicializar
    """
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.constant_(m.bias, 0.0)
    elif isinstance(m, nn.BatchNorm1d):
        nn.init.constant_(m.weight, 1.0)
        nn.init.constant_(m.bias, 0.0)


class OptimizedResNet18Regression(nn.Module):
    """
    ResNet18 optimizado para regresión de dimensiones de cacao.
    
    Mejoras:
    - Batch Normalization en capas fully connected
    - Inicialización de pesos adecuada
    - Arquitectura más simple y robusta
    - Head de regresión optimizada
    """
    
    def __init__(
        self,
        num_outputs: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        freeze_backbone: bool = False
    ):
        """
        Inicializa el modelo ResNet18 optimizado.
        
        Args:
            num_outputs: Número de salidas (4: alto, ancho, grosor, peso)
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
            freeze_backbone: Si congelar el backbone (solo entrenar head)
        """
        super(OptimizedResNet18Regression, self).__init__()
        
        # Cargar ResNet18 pre-entrenado
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        
        # Obtener número de características
        num_features = self.backbone.fc.in_features
        
        # Congelar backbone si se especifica (útil para fine-tuning)
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            logger.info("Backbone congelado, solo se entrenará la cabeza de regresión")
        
        # Reemplazar la capa de clasificación con regresión optimizada
        # Arquitectura: FC -> BN -> ReLU -> Dropout -> FC -> BN -> ReLU -> Dropout -> Output
        self.regression_head = nn.Sequential(
            # Primera capa: 512 -> 256
            nn.Linear(num_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            
            # Segunda capa: 256 -> 128
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            
            # Tercera capa: 128 -> 64
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5),  # Menos dropout en la última capa
            
            # Capa de salida: 64 -> num_outputs (sin activación para regresión)
            nn.Linear(64, num_outputs)
        )
        
        # Remover la capa fc original
        self.backbone.fc = nn.Identity()
        
        # Inicializar pesos de la cabeza de regresión
        self.regression_head.apply(init_weights)
        
        self.num_outputs = num_outputs
        
        logger.info(
            f"OptimizedResNet18Regression creado: "
            f"outputs={num_outputs}, dropout={dropout_rate}, "
            f"pretrained={pretrained}, frozen={freeze_backbone}"
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass del modelo.
        
        Args:
            x: Tensor de imagen [batch, 3, H, W]
            
        Returns:
            Tensor de predicciones [batch, num_outputs]
            Orden: [alto, ancho, grosor, peso]
        """
        # Extraer features del backbone
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
        
        # Aplicar cabeza de regresión
        output = self.regression_head(x)
        
        return output
    
    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extrae características antes de la cabeza de regresión."""
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


class OptimizedHybridRegression(nn.Module):
    """
    Modelo híbrido optimizado que fusiona ResNet18 y features de píxeles.
    
    Mejoras:
    - Arquitectura más simple (solo ResNet18 + pixel features)
    - Batch Normalization en todas las capas
    - Inicialización de pesos adecuada
    - Mejor manejo de features de píxeles
    """
    
    def __init__(
        self,
        num_outputs: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        num_pixel_features: int = 12,
        use_pixel_features: bool = True,
        freeze_backbone: bool = False
    ):
        """
        Inicializa el modelo híbrido optimizado.
        
        Args:
            num_outputs: Número de salidas (4: alto, ancho, grosor, peso)
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
            num_pixel_features: Número de features de píxeles (12 extendidos o 5 básicos)
            use_pixel_features: Si usar features de píxeles
            freeze_backbone: Si congelar el backbone
        """
        super(OptimizedHybridRegression, self).__init__()
        
        self.use_pixel_features = use_pixel_features
        
        # Backbone: ResNet18
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        resnet_features = self.backbone.fc.in_features  # 512
        self.backbone.fc = nn.Identity()
        
        # Congelar backbone si se especifica
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            logger.info("Backbone congelado")
        
        # Branch para features de píxeles
        pixel_features_dim = 0
        if use_pixel_features:
            self.pixel_branch = nn.Sequential(
                nn.Linear(num_pixel_features, 64),
                nn.BatchNorm1d(64),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate * 0.5),
                nn.Linear(64, 128),
                nn.BatchNorm1d(128),
                nn.ReLU(inplace=True)
            )
            pixel_features_dim = 128
        
        # Proyección de features de ResNet
        self.resnet_projection = nn.Sequential(
            nn.Linear(resnet_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        # Tamaño total después de concatenar
        fused_features_dim = 256 + pixel_features_dim
        
        # Capa de fusión
        self.fusion = nn.Sequential(
            nn.Linear(fused_features_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        # Cabeza de regresión
        self.regression_head = nn.Sequential(
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(64, num_outputs)  # 4 salidas: alto, ancho, grosor, peso
        )
        
        # Inicializar pesos
        self.pixel_branch.apply(init_weights) if use_pixel_features else None
        self.resnet_projection.apply(init_weights)
        self.fusion.apply(init_weights)
        self.regression_head.apply(init_weights)
        
        self.num_outputs = num_outputs
        
        logger.info(
            f"OptimizedHybridRegression creado: "
            f"outputs={num_outputs}, pixel_features={num_pixel_features}, "
            f"use_pixel={use_pixel_features}, dropout={dropout_rate}"
        )
    
    def forward(
        self,
        image: torch.Tensor,
        pixel_features: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass del modelo híbrido.
        
        Args:
            image: Tensor de imagen [batch, 3, H, W]
            pixel_features: Tensor de features de píxeles [batch, num_pixel_features]
            
        Returns:
            Diccionario con predicciones en orden: [alto, ancho, grosor, peso]
        """
        # Extraer features de ResNet18
        x = self.backbone.conv1(image)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)
        
        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)
        
        x = self.backbone.avgpool(x)
        resnet_feat = torch.flatten(x, 1)  # [batch, 512]
        
        # Proyectar features de ResNet
        resnet_proj = self.resnet_projection(resnet_feat)  # [batch, 256]
        
        # Procesar features de píxeles si están disponibles
        if self.use_pixel_features and pixel_features is not None:
            pixel_feat = self.pixel_branch(pixel_features)  # [batch, 128]
            # Concatenar
            fused = torch.cat([resnet_proj, pixel_feat], dim=1)  # [batch, 384]
        else:
            fused = resnet_proj  # [batch, 256]
        
        # Fusionar
        fused = self.fusion(fused)  # [batch, 128]
        
        # Regresión
        output = self.regression_head(fused)  # [batch, 4]
        
        # Convertir a diccionario para compatibilidad
        return {
            'alto': output[:, 0:1],
            'ancho': output[:, 1:2],
            'grosor': output[:, 2:3],
            'peso': output[:, 3:4]
        }


class SimpleCacaoRegression(nn.Module):
    """
    Modelo CNN simple y eficiente para regresión de cacao.
    
    Arquitectura minimalista pero efectiva:
    - ResNet18 como backbone
    - Head de regresión simple con BatchNorm
    - Optimizado para aprendizaje rápido
    """
    
    def __init__(
        self,
        num_outputs: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.25
    ):
        """
        Inicializa el modelo simple.
        
        Args:
            num_outputs: Número de salidas (4: alto, ancho, grosor, peso)
            pretrained: Si usar pesos pre-entrenados
            dropout_rate: Tasa de dropout
        """
        super(SimpleCacaoRegression, self).__init__()
        
        # Backbone ResNet18
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        # Head de regresión simple pero efectiva
        self.regression_head = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5),
            
            nn.Linear(128, num_outputs)
        )
        
        # Inicializar pesos
        self.regression_head.apply(init_weights)
        
        self.num_outputs = num_outputs
        
        logger.info(
            f"SimpleCacaoRegression creado: outputs={num_outputs}, "
            f"dropout={dropout_rate}, pretrained={pretrained}"
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Tensor de imagen [batch, 3, H, W]
            
        Returns:
            Tensor de predicciones [batch, 4]
            Orden: [alto, ancho, grosor, peso]
        """
        # Extraer features
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
        
        # Regresión
        return self.regression_head(x)


def create_optimized_model(
    model_type: str = "simple",
    num_outputs: int = 4,
    pretrained: bool = True,
    dropout_rate: float = 0.3,
    use_pixel_features: bool = False,
    num_pixel_features: int = 12,
    freeze_backbone: bool = False
) -> nn.Module:
    """
    Crea un modelo optimizado para regresión de cacao.
    
    Args:
        model_type: Tipo de modelo ("simple", "resnet18", "hybrid")
        num_outputs: Número de salidas (4: alto, ancho, grosor, peso)
        pretrained: Si usar pesos pre-entrenados
        dropout_rate: Tasa de dropout
        use_pixel_features: Si usar features de píxeles (solo para hybrid)
        num_pixel_features: Número de features de píxeles
        freeze_backbone: Si congelar el backbone
        
    Returns:
        Modelo optimizado
    """
    if model_type == "simple":
        logger.info("Creando SimpleCacaoRegression (recomendado para empezar)")
        return SimpleCacaoRegression(
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate
        )
    elif model_type == "resnet18":
        logger.info("Creando OptimizedResNet18Regression")
        return OptimizedResNet18Regression(
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            freeze_backbone=freeze_backbone
        )
    elif model_type == "hybrid":
        logger.info("Creando OptimizedHybridRegression")
        return OptimizedHybridRegression(
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            num_pixel_features=num_pixel_features,
            use_pixel_features=use_pixel_features,
            freeze_backbone=freeze_backbone
        )
    else:
        raise ValueError(f"Tipo de modelo '{model_type}' no soportado. Usar: 'simple', 'resnet18', 'hybrid'")


def get_model_summary(model: nn.Module) -> Dict[str, any]:
    """
    Obtiene un resumen del modelo.
    
    Args:
        model: Modelo a analizar
        
    Returns:
        Diccionario con información del modelo
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Contar capas
    num_layers = sum(1 for _ in model.modules() if isinstance(_, (nn.Linear, nn.Conv2d)))
    
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'num_layers': num_layers,
        'model_type': type(model).__name__,
        'device': next(model.parameters()).device if next(model.parameters(), None) is not None else 'cpu'
    }

