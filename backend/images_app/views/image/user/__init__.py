"""
User image views module.
"""
from .scan_views import ScanMeasureView
from .list_views import ImagesListView
from .crud_views import (
    ImageDetailView,
    ImageUpdateView,
    ImageDeleteView,
    ImageDownloadView,
)
from .stats_views import ImagesStatsView

__all__ = [
    'ScanMeasureView',
    'ImagesListView',
    'ImageDetailView',
    'ImagesStatsView',
    'ImageUpdateView',
    'ImageDeleteView',
    'ImageDownloadView',
]

