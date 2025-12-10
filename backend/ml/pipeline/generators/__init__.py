"""
Utilidades de generación y validación de recortes.

Este módulo proporciona clases para generar y validar imágenes recortadas,
siguiendo principios SOLID con separación de responsabilidades.
"""

from .generador_recorte import GeneradorRecorte
from .interfaces import IGeneradorRecorte

# Compatibilidad hacia atrás
CropGenerator = GeneradorRecorte

__all__ = [
    # Nombres en español
    'GeneradorRecorte',
    'IGeneradorRecorte',
    # Compatibilidad hacia atrás
    'CropGenerator'
]

