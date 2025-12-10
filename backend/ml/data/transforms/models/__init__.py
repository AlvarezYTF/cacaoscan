"""
Modelos de segmentación para remoción de fondo.

Este módulo proporciona modelos de redes neuronales,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .double_conv import DoubleConv
from .unet import UNet

__all__ = ['DoubleConv', 'UNet']

