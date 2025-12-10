"""
Utilidades de modelos de segmentación.

Este módulo proporciona funciones de conveniencia para compatibilidad hacia atrás,
siguiendo principios SOLID para separación de responsabilidades.
"""

from .models import DoubleConv, UNet

__all__ = ['DoubleConv', 'UNet']

