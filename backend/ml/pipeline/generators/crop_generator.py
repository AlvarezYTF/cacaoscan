"""
Compatibilidad hacia atrás para CropGenerator.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en generador_recorte.py.
"""

from .generador_recorte import GeneradorRecorte

# Alias para compatibilidad hacia atrás
CropGenerator = GeneradorRecorte
