"""
Compatibilidad hacia atrás para CropValidator.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en validador_recorte.py.
"""

from .validador_recorte import ValidadorRecorte

# Alias para compatibilidad hacia atrás
CropValidator = ValidadorRecorte

