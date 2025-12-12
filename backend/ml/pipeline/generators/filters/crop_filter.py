"""
Compatibilidad hacia atrás para CropFilter.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en filtro_recorte.py.
"""

from .filtro_recorte import FiltroRecorte

# Alias para compatibilidad hacia atrás
CropFilter = FiltroRecorte

