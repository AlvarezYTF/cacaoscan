"""
Filtros para registros de recortes.

Este módulo proporciona filtros para registros de recortes,
siguiendo principios SOLID con separación de responsabilidades.
"""

from .filtro_recorte import FiltroRecorte
from .crop_filter import CropFilter  # Compatibilidad hacia atrás
from .interfaces import IFiltro
from .normalizadores import NormalizadorPath
from .verificadores import VerificadorExistencia

# Compatibilidad hacia atrás
CropFilter = FiltroRecorte

__all__ = [
    # Nombres en español
    'FiltroRecorte',
    'IFiltro',
    'NormalizadorPath',
    'VerificadorExistencia',
    # Compatibilidad hacia atrás
    'CropFilter'
]

