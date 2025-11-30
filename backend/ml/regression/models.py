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

# Model name constants
CONVNEXT_TINY_MODEL_NAME = 'convnext_tiny.in12k_ft_in1k'
CONVNEXT_LOADING_MSG = "✔ Cargando ConvNeXt Tiny con pesos ImageNet-12k preentrenados"
CONVNEXT_WARNING_MSG = "⚠ ConvNeXt Tiny se inicializará con pesos aleatorios (pretrained=False)"


class ResNet18Regression(nn.Module):
    """
    ResNet18 adaptado para regresión de dimensiones de cacao.
    
    OPTIMIZADO:
    - Batch Normalization en capas fully connected
    - Inicialización de pesos adecuada
    - Arquitectura más robusta
    """
    
    def __init__(
        self,
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.3
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
        
        # Reemplazar la capa de clasificación con regresión optimizada
        # Agregar BatchNorm para mejor entrenamiento
        self.backbone.fc = nn.Sequential(
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
        
        # Inicializar pesos de la cabeza de regresión
        def init_weights(m):
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)
        
        self.backbone.fc.apply(init_weights)
        
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
        
        # Cargar ConvNeXt Tiny pre-entrenado con pesos ImageNet-12k
        # FORZAR uso de pesos ImageNet-12k para mejor rendimiento
        if pretrained:
            backbone_name = CONVNEXT_TINY_MODEL_NAME  # Usar pesos ImageNet-12k
            logger.info("=" * 60)
            logger.info(CONVNEXT_LOADING_MSG)
            logger.info(f"  Modelo: {backbone_name}")
            logger.info("=" * 60)
        else:
            backbone_name = 'convnext_tiny'
            logger.warning("=" * 60)
            logger.warning(CONVNEXT_WARNING_MSG)
            logger.warning("=" * 60)
        
        logger.info(f"Creando backbone timm: {backbone_name}, pretrained={pretrained}")
        self.backbone = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0  # Remover clasificador
        )
        
        # Verificar que los pesos se cargaron
        if pretrained:
            try:
                first_conv_weight = list(self.backbone.stem.parameters())[0]
                weight_mean = first_conv_weight.data.mean().item()
                weight_std = first_conv_weight.data.std().item()
                logger.info(f"  Verificación pesos: mean={weight_mean:.6f}, std={weight_std:.6f}")
                if abs(weight_mean) < 0.001 and weight_std < 0.01:
                    logger.warning("⚠ Los pesos parecen estar cerca de cero - posible inicialización aleatoria")
                else:
                    logger.info("✔ Los pesos parecen estar cargados correctamente")
            except Exception as e:
                logger.warning(f"No se pudo verificar pesos: {e}")
        
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
    
    def _create_resnet18_backbone(self, pretrained: bool) -> Tuple[nn.Module, int]:
        """Crea backbone ResNet18 y retorna (backbone, num_features)."""
        backbone = ResNet18Regression(
            num_outputs=1,  # Solo para obtener características
            pretrained=pretrained,
            dropout_rate=0.0  # No dropout en backbone
        )
        backbone.backbone.fc = nn.Identity()
        return backbone, 512

    def _create_convnext_backbone(self, pretrained: bool) -> Tuple[nn.Module, int]:
        """Crea backbone ConvNeXt y retorna (backbone, num_features)."""
        if not TIMM_AVAILABLE:
            raise ImportError("timm es requerido para ConvNeXt")
        
        if pretrained:
            backbone_name = CONVNEXT_TINY_MODEL_NAME
            logger.info("=" * 60)
            logger.info(CONVNEXT_LOADING_MSG)
            logger.info(f"  Modelo: {backbone_name}")
            logger.info("=" * 60)
        else:
            backbone_name = 'convnext_tiny'
            logger.warning("=" * 60)
            logger.warning(CONVNEXT_WARNING_MSG)
            logger.warning("=" * 60)
        
        logger.info(f"Creando backbone timm: {backbone_name}, pretrained={pretrained}")
        backbone = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0
        )
        
        if pretrained:
            self._verify_convnext_weights(backbone)
        
        backbone.regression_head = nn.Identity()
        num_features = backbone.backbone.num_features
        return backbone, num_features

    def _verify_convnext_weights(self, backbone: nn.Module) -> None:
        """Verifica que los pesos del backbone ConvNeXt se cargaron correctamente."""
        try:
            first_conv_weight = list(backbone.stem.parameters())[0]
            weight_mean = first_conv_weight.data.mean().item()
            weight_std = first_conv_weight.data.std().item()
            logger.info(f"  Verificación pesos: mean={weight_mean:.6f}, std={weight_std:.6f}")
            if abs(weight_mean) < 0.001 and weight_std < 0.01:
                logger.warning("⚠ Los pesos parecen estar cerca de cero")
            else:
                logger.info("✔ Los pesos parecen estar cargados correctamente")
        except Exception as e:
            logger.warning(f"No se pudo verificar pesos: {e}")

    def _create_backbone(self, backbone_type: str, pretrained: bool) -> Tuple[nn.Module, int]:
        """Crea el backbone según el tipo especificado."""
        if backbone_type == "resnet18":
            return self._create_resnet18_backbone(pretrained)
        elif backbone_type == "convnext_tiny":
            return self._create_convnext_backbone(pretrained)
        else:
            raise ValueError(f"Backbone tipo '{backbone_type}' no soportado")

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
        
        self.backbone, num_features = self._create_backbone(backbone_type, pretrained)
        
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
    
    OPTIMIZADO:
    - Batch Normalization en todas las capas fully connected
    - Inicialización de pesos adecuada
    - Mejor manejo de features de píxeles
    
    Arquitectura:
    - ResNet18: Extrae features visuales (512)
    - ConvNeXt: Extrae features visuales (768)
    - Pixel Features: Features de pxeles (5 o 12)
    - Fusion: Concatena todas las features  Regression Head
    """
    
    def _create_resnet18_backbone(self, pretrained: bool) -> Tuple[nn.Module, int, Any]:
        """Crea y configura el backbone ResNet18."""
        weights_resnet = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        resnet18 = models.resnet18(weights=weights_resnet)
        resnet_features = resnet18.fc.in_features
        resnet18.fc = nn.Identity()
        
        def resnet_extractor(x):
            x = resnet18.conv1(x)
            x = resnet18.bn1(x)
            x = resnet18.relu(x)
            x = resnet18.maxpool(x)
            x = resnet18.layer1(x)
            x = resnet18.layer2(x)
            x = resnet18.layer3(x)
            x = resnet18.layer4(x)
            x = resnet18.avgpool(x)
            return torch.flatten(x, 1)
        
        return resnet18, resnet_features, resnet_extractor

    def _create_convnext_backbone(self, pretrained: bool) -> Tuple[nn.Module, int]:
        """Crea y configura el backbone ConvNeXt."""
        if pretrained:
            backbone_name = CONVNEXT_TINY_MODEL_NAME
            logger.info("=" * 60)
            logger.info(CONVNEXT_LOADING_MSG)
            logger.info(f"  Modelo: {backbone_name}")
            logger.info("=" * 60)
        else:
            backbone_name = 'convnext_tiny'
            logger.warning("=" * 60)
            logger.warning(CONVNEXT_WARNING_MSG)
            logger.warning("  Esto resultará en R² muy negativos en epoch 1")
            logger.warning("=" * 60)
        
        logger.info(f"Creando backbone timm: {backbone_name}, pretrained={pretrained}")
        convnext = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0,
            global_pool='avg'
        )
        convnext_features = convnext.num_features
        
        if pretrained:
            self._verify_convnext_weights_hybrid(convnext, backbone_name, convnext_features)
        else:
            logger.info(f"Backbone ConvNeXt creado (sin pretrained): {backbone_name} con {convnext_features} features")
        
        return convnext, convnext_features

    def _verify_convnext_weights_hybrid(self, convnext: nn.Module, backbone_name: str, convnext_features: int) -> None:
        """Verifica que los pesos del ConvNeXt se cargaron correctamente."""
        first_conv_weight = list(convnext.stem.parameters())[0]
        weight_mean = first_conv_weight.data.mean().item()
        weight_std = first_conv_weight.data.std().item()
        logger.info(f"✔ Backbone ConvNeXt cargado: {backbone_name} con {convnext_features} features")
        logger.info(f"  Verificación pesos: mean={weight_mean:.6f}, std={weight_std:.6f}")
        if abs(weight_mean) < 0.001 and weight_std < 0.01:
            logger.warning("⚠ Los pesos parecen estar cerca de cero - posible inicialización aleatoria")
        else:
            logger.info("✔ Los pesos parecen estar cargados correctamente (no son cercanos a cero)")

    def _create_pixel_branch(self, num_pixel_features: int, dropout_rate: float, use_pixel_features: bool) -> Tuple[Optional[nn.Module], int]:
        """Crea el branch de features de píxeles si está habilitado."""
        if not use_pixel_features:
            return None, 0
        
        pixel_branch = nn.Sequential(
            nn.Linear(num_pixel_features, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout_rate * 0.5)
        )
        return pixel_branch, 256

    def _create_projections(self, resnet_features: int, convnext_features: int, dropout_rate: float) -> Tuple[nn.Module, nn.Module, nn.Module]:
        """Crea las proyecciones de features."""
        resnet_projection = nn.Sequential(
            nn.Linear(resnet_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        convnext_projection = nn.Sequential(
            nn.Linear(convnext_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        img_projection = nn.Sequential(
            nn.Linear(resnet_features + convnext_features, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        return resnet_projection, convnext_projection, img_projection

    def _create_fusion_layers(self, pixel_features_dim: int, dropout_rate: float) -> Tuple[nn.Module, nn.Module]:
        """Crea las capas de fusión y gating."""
        gating = nn.Sequential(
            nn.Linear(512 + pixel_features_dim, 256),
            nn.GELU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
        fusion = nn.Sequential(
            nn.Linear(512 + pixel_features_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        return gating, fusion

    def _create_regression_head(self, num_outputs: int, dropout_rate: float) -> nn.Module:
        """Crea la cabeza de regresión."""
        final_outputs = 4
        if num_outputs != 4:
            logger.warning(f"num_outputs={num_outputs} != 4, forzando a 4 para compatibilidad")
        
        return nn.Sequential(
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(64, final_outputs)
        )

    def _init_module_weights(self, module: nn.Module) -> None:
        """Inicializa los pesos de un módulo individual."""
        def init_weights(m):
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)
        
        if module is not None:
            module.apply(init_weights)
    
    def _init_final_layer_weights(self, final_outputs: int) -> None:
        """Inicializa los pesos de la última capa del regression_head."""
        for module in reversed(list(self.regression_head.modules())):
            if isinstance(module, nn.Linear) and module.out_features == final_outputs:
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    module.bias.data.zero_()
                break
    
    def _init_weights(self, modules: List[nn.Module], final_outputs: int) -> None:
        """Inicializa los pesos de los módulos."""
        for module in modules:
            self._init_module_weights(module)
        
        self._init_final_layer_weights(final_outputs)

    def __init__(
        self,
        num_outputs: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        num_pixel_features: int = 10,  # Updated: 10 features with compactness and roundness
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
        
        # Crear backbones
        self.resnet18, resnet_features, self.resnet_feature_extractor = self._create_resnet18_backbone(pretrained)
        self.convnext, convnext_features = self._create_convnext_backbone(pretrained)
        
        # Crear pixel branch
        self.pixel_branch, pixel_features_dim = self._create_pixel_branch(num_pixel_features, dropout_rate, use_pixel_features)
        
        # Crear proyecciones
        self.resnet_projection, self.convnext_projection, self.img_projection = self._create_projections(
            resnet_features, convnext_features, dropout_rate
        )
        
        # Crear fusion layers
        self.gating, self.fusion = self._create_fusion_layers(pixel_features_dim, dropout_rate)
        
        # Crear regression head
        self.regression_head = self._create_regression_head(num_outputs, dropout_rate)
        final_outputs = 4
        
        # Inicializar pesos
        modules_to_init = [self.pixel_branch, self.resnet_projection, self.convnext_projection, self.fusion, self.regression_head]
        self._init_weights(modules_to_init, final_outputs)
        
        self.num_outputs = final_outputs  # Siempre 4
        fused_features_dim = 512 + pixel_features_dim if use_pixel_features else 512
        logger.info(
            f"Modelo Híbrido Creado con FEATURE GATING: "
            f"Fused features dim = {fused_features_dim} "
            f"(use_pixel_features={use_pixel_features}, "
            f"num_pixel_features={num_pixel_features}, "
            f"gating_enabled=True)"
        )
    
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
        
        # Extraer features de ConvNeXt
        convnext_feat = self.convnext(image)  # [batch, 768]
        
        # Concatenar imagen features
        img_feat_concat = torch.cat([resnet_feat, convnext_feat], dim=1)  # [batch, 1280]
        
        # Project image features: 1280 → 512
        img_proj = self.img_projection(img_feat_concat)  # [batch, 512]
        
        # Procesar features de píxeles si están disponibles
        if self.use_pixel_features and pixel_features is not None:
            pix_proj = self.pixel_branch(pixel_features)  # [batch, 256]
            
            # Feature gating: sigmoid(Linear(img_feat + pix_feat))
            concat_for_gating = torch.cat([img_proj, pix_proj], dim=1)  # [batch, 768]
            gating_values = self.gating(concat_for_gating)  # [batch, 1]
            
            # Apply gating
            img_gated = img_proj * gating_values  # [batch, 512]
            pix_gated = pix_proj * (1 - gating_values)  # [batch, 256]
            
            # Concatenate gated features
            fused = torch.cat([img_gated, pix_gated], dim=1)  # [batch, 768]
        else:
            # Sin features de píxeles
            fused = img_proj  # [batch, 512]
        
        # Fusionar
        fused = self.fusion(fused)  # [batch, 128]
        
        # Regresin
        output = self.regression_head(fused)  # [batch, num_outputs]
        
        # Convertir a diccionario para compatibilidad con el loop de entrenamiento
        # El orden es: alto, ancho, grosor, peso
        return {
            'alto': output[:, 0:1],
            'ancho': output[:, 1:2],
            'grosor': output[:, 2:3],
            'peso': output[:, 3:4]
        }
    
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


def _create_hybrid_model(
    pretrained: bool,
    dropout_rate: float,
    pixel_feature_dim: Optional[int],
    use_pixel_features: bool
) -> nn.Module:
    """Crea un modelo híbrido."""
    num_pixel_feat = pixel_feature_dim if pixel_feature_dim is not None else 10
    
    if not pretrained:
        logger.warning("=" * 60)
        logger.warning("⚠ pretrained=False detectado para modelo híbrido")
        logger.warning("  Esto resultará en R² muy negativos en epoch 1 (grosor R² ~-1.0)")
        logger.warning("  Forzando pretrained=True para mejor rendimiento")
        logger.warning("=" * 60)
        pretrained = True
    else:
        logger.info("=" * 60)
        logger.info("✔ Creando modelo híbrido con pretrained=True")
        logger.info(f"  ConvNeXt usará pesos ImageNet-12k ({CONVNEXT_TINY_MODEL_NAME})")
        logger.info("=" * 60)
    
    logger.info(f"Creando HybridCacaoRegression con pretrained={pretrained}, num_pixel_features={num_pixel_feat}")
    return HybridCacaoRegression(
        num_outputs=4,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
        num_pixel_features=num_pixel_feat,
        use_pixel_features=use_pixel_features
    )


def _create_multi_head_model(
    model_type: str,
    pretrained: bool,
    dropout_rate: float
) -> nn.Module:
    """Crea un modelo multi-head."""
    logger.info(f"Creando modelo Multi-Head (Backbone: {model_type})")
    return MultiHeadRegression(
        backbone_type=model_type,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
        shared_features=True
    )


def _create_optimized_model(
    model_type: str,
    num_outputs: int,
    pretrained: bool,
    dropout_rate: float
) -> Optional[nn.Module]:
    """Intenta crear un modelo optimizado."""
    try:
        from .optimized_models import create_optimized_model
        
        if model_type == "resnet18":
            logger.info("Usando modelo optimizado ResNet18")
            return create_optimized_model(
                model_type="resnet18",
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
        elif model_type == "simple":
            logger.info("Usando modelo Simple optimizado (recomendado)")
            return create_optimized_model(
                model_type="simple",
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
    except ImportError:
        logger.warning("Modelos optimizados no disponibles, usando modelos estándar")
    
    return None


def _create_standard_model(
    model_type: str,
    num_outputs: int,
    pretrained: bool,
    dropout_rate: float,
    pixel_feature_dim: Optional[int],
    use_pixel_features: bool
) -> nn.Module:
    """Crea un modelo estándar."""
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
        num_pixel_feat = pixel_feature_dim if pixel_feature_dim is not None else 5
        return HybridCacaoRegression(
            num_outputs=4 if num_outputs == 1 else num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            num_pixel_features=num_pixel_feat,
            use_pixel_features=use_pixel_features
        )
    else:
        raise ValueError(f"Tipo de modelo '{model_type}' no soportado")


def create_model(
    model_type: str = "resnet18",
    num_outputs: int = 1,
    pretrained: bool = True,
    dropout_rate: float = 0.3,
    multi_head: bool = False,
    hybrid: bool = False,
    use_pixel_features: bool = True,
    pixel_feature_dim: Optional[int] = None,
    use_optimized: bool = True
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
        return _create_hybrid_model(pretrained, dropout_rate, pixel_feature_dim, use_pixel_features)
    
    if multi_head:
        return _create_multi_head_model(model_type, pretrained, dropout_rate)
    
    logger.info(f"Creando modelo Individual (Backbone: {model_type}, Outputs: {num_outputs})")
    
    if use_optimized:
        optimized_model = _create_optimized_model(model_type, num_outputs, pretrained, dropout_rate)
        if optimized_model is not None:
            return optimized_model
    
    return _create_standard_model(
        model_type, num_outputs, pretrained, dropout_rate, pixel_feature_dim, use_pixel_features
    )


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