"""
Finca views module.
"""
from .finca_views import (
    FincaListCreateView,
    FincaDetailView,
    FincaUpdateView,
    FincaDeleteView,
    FincaActivateView,
    FincaStatsView,
    FincaPermissionMixin
)
from .lote_views import (
    LoteListCreateView,
    LoteDetailView,
    LoteUpdateView,
    LoteDeleteView,
    LoteStatsView,
    LotesPorFincaView,
    LoteAnalisisView,
    LotePermissionMixin
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
