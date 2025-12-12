"""
Fincas app views module.
"""
from .finca import (
    FincaListCreateView,
    FincaDetailView,
    FincaUpdateView,
    FincaDeleteView,
    FincaActivateView,
    FincaStatsView,
    FincaPermissionMixin,
    LoteListCreateView,
    LoteDetailView,
    LoteUpdateView,
    LoteDeleteView,
    LoteStatsView,
    LotesPorFincaView,
    LoteAnalisisView,
    LotePermissionMixin,
)

__all__ = [
    'FincaListCreateView',
    'FincaDetailView',
    'FincaUpdateView',
    'FincaDeleteView',
    'FincaActivateView',
    'FincaStatsView',
    'FincaPermissionMixin',
    'LoteListCreateView',
    'LoteDetailView',
    'LoteUpdateView',
    'LoteDeleteView',
    'LoteStatsView',
    'LotesPorFincaView',
    'LoteAnalisisView',
    'LotePermissionMixin',
]
