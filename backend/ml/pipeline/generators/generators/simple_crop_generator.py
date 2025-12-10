"""
Compatibilidad hacia atrás para SimpleCropGenerator.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en generador_recorte_simple.py.
"""

from .generador_recorte_simple import GeneradorRecorteSimple

# Alias para compatibilidad hacia atrás
SimpleCropGenerator = GeneradorRecorteSimple
