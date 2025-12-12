"""
Compatibilidad hacia atrás para SegmentedCropGenerator.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en generador_recorte_segmentado.py.
"""

from .generador_recorte_segmentado import GeneradorRecorteSegmentado

# Alias para compatibilidad hacia atrás
SegmentedCropGenerator = GeneradorRecorteSegmentado
