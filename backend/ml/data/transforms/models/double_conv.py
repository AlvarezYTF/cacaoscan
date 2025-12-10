"""
Bloque de doble convolución para U-Net.

Este módulo contiene el bloque básico de convolución,
siguiendo el principio de Responsabilidad Única.
"""
import torch
import torch.nn as nn

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.models")


class DoubleConv(nn.Module):
    """
    Bloque de doble convolución para U-Net.
    
    Esta clase es responsable de:
    - Aplicar dos convoluciones secuenciales
    - Normalización por lotes
    - Activación ReLU
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(self, in_channels: int, out_channels: int):
        """
        Inicializa bloque de doble convolución.
        
        Args:
            in_channels: Canales de entrada
            out_channels: Canales de salida
        """
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Paso forward del bloque.
        
        Args:
            x: Tensor de entrada
            
        Returns:
            Tensor procesado
        """
        return self.conv(x)

