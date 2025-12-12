"""
Modelo U-Net ligero para segmentación de fondo.

Este módulo contiene el modelo U-Net completo,
siguiendo el principio de Responsabilidad Única.
"""
import torch
import torch.nn as nn

from ....utils.logs import get_ml_logger
from .double_conv import DoubleConv

logger = get_ml_logger("cacaoscan.ml.data.transforms.models")


class UNet(nn.Module):
    """
    Modelo U-Net ligero para segmentación de fondo.
    
    Esta clase es responsable de:
    - Arquitectura encoder-decoder
    - Segmentación binaria de fondo
    - Conexiones skip entre encoder y decoder
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(self, n_channels: int = 3, n_classes: int = 1):
        """
        Inicializa modelo U-Net.
        
        Args:
            n_channels: Número de canales de entrada (por defecto: 3 para RGB)
            n_classes: Número de clases de salida (por defecto: 1 para segmentación binaria)
        """
        super().__init__()
        self.down1 = DoubleConv(n_channels, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.bottom = DoubleConv(128, 256)
        self.up1 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.conv1 = DoubleConv(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.conv2 = DoubleConv(128, 64)
        self.final = nn.Conv2d(64, n_classes, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Paso forward del modelo.
        
        Args:
            x: Tensor de entrada (imagen)
            
        Returns:
            Tensor de salida (máscara de segmentación)
        """
        x1 = self.down1(x)
        x2 = self.pool1(x1)
        x3 = self.down2(x2)
        x4 = self.pool2(x3)
        x5 = self.bottom(x4)
        x = self.up1(x5)
        x = torch.cat([x, x3], dim=1)
        x = self.conv1(x)
        x = self.up2(x)
        x = torch.cat([x, x1], dim=1)
        x = self.conv2(x)
        x = self.final(x)
        return self.sigmoid(x)

