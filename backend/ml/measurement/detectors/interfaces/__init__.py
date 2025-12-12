"""
Interfaces para detectores de granos de cacao.

Este módulo define los protocolos que deben seguir los detectores,
siguiendo el principio de Segregación de Interfaces.
"""

from .detector_interface import IDetector

__all__ = ['IDetector']

