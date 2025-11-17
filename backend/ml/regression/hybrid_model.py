"""
Advanced hybrid regression model with feature gating fusion.
"""
import torch
import torch.nn as nn
from typing import Optional, Tuple
import logging

try:
    import timm
    TIMM_AVAILABLE = True
except ImportError:
    TIMM_AVAILABLE = False
    logging.warning("timm no está disponible. ConvNeXt no estará disponible.")

from ..utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.regression.hybrid")


class HybridRegressor(nn.Module):
    """
    Advanced hybrid regressor with feature gating fusion.
    
    Architecture:
    - ConvNeXt Tiny backbone (768 dims)
    - Pixel features MLP projection (P → 256)
    - Feature gating: sigmoid(Linear(img_feat + pix_feat))
    - Gated fusion: concat(img_feat * gating, pix_feat * (1 - gating))
    - MLP: 512 → 256 → 128 → 4 outputs
    
    Purpose:
    - Avoid pixel features contaminating altura/ancho prediction
    - Avoid image features contaminating grosor/peso prediction
    - Control feature-map dominance
    """
    
    def __init__(
        self,
        backbone_name: str = "convnext_tiny",
        pixel_dim: int = 10,
        pretrained: bool = True,
        dropout_rate: float = 0.1
    ):
        """
        Initialize the hybrid regressor.
        
        Args:
            backbone_name: Name of backbone model (from timm)
            pixel_dim: Dimension of pixel features (10 with compactness and roundness)
            pretrained: Use pretrained weights
            dropout_rate: Dropout rate
        """
        super(HybridRegressor, self).__init__()
        
        if not TIMM_AVAILABLE:
            raise ImportError("timm es requerido. Instalar con: pip install timm")
        
        # Backbone: ConvNeXt Tiny con pesos ImageNet-12k preentrenados
        if pretrained and backbone_name == "convnext_tiny":
            # Usar la variante con pesos ImageNet-12k para mejor rendimiento
            backbone_name = 'convnext_tiny.in12k_ft_in1k'
            logger.info("✔ Cargando ConvNeXt Tiny con pesos ImageNet-12k preentrenados")
        elif not pretrained:
            logger.warning("⚠ ConvNeXt Tiny se inicializará con pesos aleatorios (pretrained=False)")
        
        self.backbone = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0,  # Remove classifier
            global_pool='avg'  # Global average pooling
        )
        
        backbone_dim = self.backbone.num_features  # Can be 640 or 768 depending on timm version
        logger.info(f"✔ Backbone {backbone_name} cargado con {backbone_dim} features")
        
        # Image feature projection: backbone_dim → 512
        self.img_projection = nn.Sequential(
            nn.Linear(backbone_dim, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(dropout_rate)
        )
        
        # Pixel feature projection: P → 256
        self.pix_projection = nn.Sequential(
            nn.Linear(pixel_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout_rate)
        )
        
        # Feature gating: sigmoid(Linear(img_feat + pix_feat))
        # Input: 512 (img) + 256 (pix) = 768
        self.gating = nn.Sequential(
            nn.Linear(512 + 256, 256),
            nn.GELU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
        # Fusion: concat(img_feat * gating, pix_feat * (1 - gating))
        # Output: 512 + 256 = 768, but we'll use 512 for efficiency
        fusion_dim = 512 + 256  # 768
        
        # Final MLP: 768 → 256 → 128 → 4
        self.fusion_mlp = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, 4)  # 4 outputs: [alto, ancho, grosor, peso]
        )
        
        # Initialize weights
        self._initialize_weights()
        
        logger.info(
            f"HybridRegressor created with FEATURE GATING: "
            f"backbone={backbone_name} (dim={backbone_dim}), "
            f"pixel_dim={pixel_dim}, "
            f"img_proj=512, pix_proj=256, "
            f"fusion_dim={fusion_dim}, "
            f"gating_enabled=True"
        )
    
    def _initialize_weights(self) -> None:
        """Initialize weights using Xavier uniform for Linear layers."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0.0)
            elif isinstance(module, nn.LayerNorm):
                nn.init.constant_(module.weight, 1.0)
                nn.init.constant_(module.bias, 0.0)
    
    def forward(
        self,
        image: torch.Tensor,
        pixel_features: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass with feature gating.
        
        Args:
            image: Image tensor [batch, 3, H, W]
            pixel_features: Pixel features tensor [batch, pixel_dim]
            
        Returns:
            Tuple of (predictions [batch, 4], gating_values [batch, 1])
        """
        # Extract image features
        img_features = self.backbone(image)  # [batch, backbone_dim]
        
        # Project features
        img_proj = self.img_projection(img_features)  # [batch, 512]
        pix_proj = self.pix_projection(pixel_features)  # [batch, 256]
        
        # Concatenate for gating
        concat_for_gating = torch.cat([img_proj, pix_proj], dim=1)  # [batch, 768]
        
        # Compute gating values
        gating_values = self.gating(concat_for_gating)  # [batch, 1]
        
        # Apply gating
        img_gated = img_proj * gating_values  # [batch, 512]
        pix_gated = pix_proj * (1 - gating_values)  # [batch, 256]
        
        # Concatenate gated features
        fused = torch.cat([img_gated, pix_gated], dim=1)  # [batch, 768]
        
        # Final regression
        output = self.fusion_mlp(fused)  # [batch, 4]
        
        return output, gating_values


def create_hybrid_model(
    backbone_name: str = "convnext_tiny",
    pixel_dim: int = 10,
    pretrained: bool = True,
    dropout_rate: float = 0.1
) -> HybridRegressor:
    """
    Factory function to create a hybrid model.
    
    Args:
        backbone_name: Name of backbone model
        pixel_dim: Dimension of pixel features (10 with compactness and roundness)
        pretrained: Use pretrained weights
        dropout_rate: Dropout rate
        
    Returns:
        HybridRegressor instance
    """
    return HybridRegressor(
        backbone_name=backbone_name,
        pixel_dim=pixel_dim,
        pretrained=pretrained,
        dropout_rate=dropout_rate
    )
