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
            backbone_name = 'convnext_tiny.in12k_ft_in1k'  # Usar pesos ImageNet-12k
            logger.info("=" * 60)
            logger.info("✔ Cargando ConvNeXt Tiny con pesos ImageNet-12k preentrenados")
            logger.info(f"  Modelo: {backbone_name}")
            logger.info("=" * 60)
        else:
            backbone_name = 'convnext_tiny'
            logger.warning("=" * 60)
            logger.warning("⚠ ConvNeXt Tiny se inicializará con pesos aleatorios (pretrained=False)")
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
            
            # FORZAR uso de pesos ImageNet-12k para mejor rendimiento
            if pretrained:
                backbone_name = 'convnext_tiny.in12k_ft_in1k'  # Usar pesos ImageNet-12k
                logger.info("=" * 60)
                logger.info("✔ Cargando ConvNeXt Tiny con pesos ImageNet-12k preentrenados")
                logger.info(f"  Modelo: {backbone_name}")
                logger.info("=" * 60)
            else:
                backbone_name = 'convnext_tiny'
                logger.warning("=" * 60)
                logger.warning("⚠ ConvNeXt Tiny se inicializará con pesos aleatorios (pretrained=False)")
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
                        logger.warning("⚠ Los pesos parecen estar cerca de cero")
                    else:
                        logger.info("✔ Los pesos parecen estar cargados correctamente")
                except Exception as e:
                    logger.warning(f"No se pudo verificar pesos: {e}")
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
        
        # Backbone 2: ConvNeXt Tiny con pesos ImageNet-12k preentrenados
        # FORZAR uso de pesos ImageNet-12k para mejor rendimiento
        if pretrained:
            backbone_name = 'convnext_tiny.in12k_ft_in1k'  # Usar pesos ImageNet-12k
            logger.info("=" * 60)
            logger.info("✔ Cargando ConvNeXt Tiny con pesos ImageNet-12k preentrenados")
            logger.info(f"  Modelo: {backbone_name}")
            logger.info("=" * 60)
        else:
            backbone_name = 'convnext_tiny'
            logger.warning("=" * 60)
            logger.warning("⚠ ConvNeXt Tiny se inicializará con pesos aleatorios (pretrained=False)")
            logger.warning("  Esto resultará en R² muy negativos en epoch 1")
            logger.warning("=" * 60)
        
        # Crear backbone con logging explícito
        logger.info(f"Creando backbone timm: {backbone_name}, pretrained={pretrained}")
        self.convnext = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0,  # Remover clasificador
            global_pool='avg'  # Global average pooling
        )
        convnext_features = self.convnext.num_features  # 768
        
        # Verificar que los pesos se cargaron (checking first layer weights)
        if pretrained:
            first_conv_weight = list(self.convnext.stem.parameters())[0]
            weight_mean = first_conv_weight.data.mean().item()
            weight_std = first_conv_weight.data.std().item()
            logger.info(f"✔ Backbone ConvNeXt cargado: {backbone_name} con {convnext_features} features")
            logger.info(f"  Verificación pesos: mean={weight_mean:.6f}, std={weight_std:.6f}")
            if abs(weight_mean) < 0.001 and weight_std < 0.01:
                logger.warning("⚠ Los pesos parecen estar cerca de cero - posible inicialización aleatoria")
            else:
                logger.info("✔ Los pesos parecen estar cargados correctamente (no son cercanos a cero)")
        else:
            logger.info(f"Backbone ConvNeXt creado (sin pretrained): {backbone_name} con {convnext_features} features")
        
        # Branch para features de píxeles (si está habilitado)
        # Updated for 10 pixel features with feature gating
        pixel_features_dim = 0
        if use_pixel_features:
            # Pixel projection: 10 → 256 (updated for new features)
            self.pixel_branch = nn.Sequential(
                nn.Linear(num_pixel_features, 256),
                nn.LayerNorm(256),
                nn.GELU(),
                nn.Dropout(dropout_rate * 0.5)
            )
            pixel_features_dim = 256
        
        # Calcular tamaño total de features fusionadas
        total_features = resnet_features + convnext_features + pixel_features_dim
        
        # Proyeccin de features para normalizar dimensiones (con BatchNorm)
        self.resnet_projection = nn.Sequential(
            nn.Linear(resnet_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        self.convnext_projection = nn.Sequential(
            nn.Linear(convnext_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        # Image projections: ResNet → 512, ConvNeXt → 512 (for feature gating)
        self.img_projection = nn.Sequential(
            nn.Linear(resnet_features + convnext_features, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        # Feature gating: sigmoid(Linear(img_feat + pix_feat))
        # Input: 512 (img) + 256 (pix) = 768
        self.gating = nn.Sequential(
            nn.Linear(512 + pixel_features_dim, 256),
            nn.GELU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
        # Tamaño después de proyección y gating
        fused_features_dim = 512 + pixel_features_dim  # 768 si usa píxeles, 512 si no
        
        # Capa de fusión con feature gating
        self.fusion = nn.Sequential(
            nn.Linear(fused_features_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(dropout_rate * 0.5)
        )
        
        # Cabeza de regresin (con BatchNorm)
        # Asegurar que siempre sea 4 outputs (alto, ancho, grosor, peso)
        final_outputs = 4 if num_outputs != 4 else num_outputs
        if num_outputs != 4:
            logger.warning(f"num_outputs={num_outputs} != 4, forzando a 4 para compatibilidad")
        
        self.regression_head = nn.Sequential(
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(64, final_outputs)  # Siempre 4 outputs
        )
        
        # Inicializar pesos
        def init_weights(m):
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)
        
        if use_pixel_features:
            self.pixel_branch.apply(init_weights)
        self.resnet_projection.apply(init_weights)
        self.convnext_projection.apply(init_weights)
        self.fusion.apply(init_weights)
        self.regression_head.apply(init_weights)
        
        # Paso 4: Inicializar correctamente la última capa (regressor final)
        # Obtener la última capa Linear del regression_head
        for module in reversed(list(self.regression_head.modules())):
            if isinstance(module, nn.Linear) and module.out_features == final_outputs:
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    module.bias.data.zero_()
                logger.debug(f"Última capa inicializada: {module.out_features} outputs (esperado: 4)")
                break
        
        self.num_outputs = final_outputs  # Siempre 4
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


def create_model(
    model_type: str = "resnet18",
    num_outputs: int = 1,
    pretrained: bool = True,
    dropout_rate: float = 0.3,  # Aumentado a 0.3 por defecto (mejor para regresión)
    multi_head: bool = False,
    hybrid: bool = False,
    use_pixel_features: bool = True,
    pixel_feature_dim: Optional[int] = None,
    use_optimized: bool = True  # Usar modelos optimizados por defecto
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
        # Determinar número de features de píxeles (10 por defecto con compactness y roundness)
        num_pixel_feat = pixel_feature_dim if pixel_feature_dim is not None else 10
        
        # FORZAR pretrained=True para cargar pesos ImageNet-12k (CRÍTICO para buen rendimiento)
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
            logger.info("  ConvNeXt usará pesos ImageNet-12k (convnext_tiny.in12k_ft_in1k)")
            logger.info("=" * 60)
        
        logger.info(f"Creando HybridCacaoRegression con pretrained={pretrained}, num_pixel_features={num_pixel_feat}")
        return HybridCacaoRegression(
            num_outputs=4, # El modelo híbrido siempre tiene 4 salidas
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            num_pixel_features=num_pixel_feat,
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
        
        # Intentar usar modelos optimizados si están disponibles
        if use_optimized:
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
        
        # Fallback a modelos estándar
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