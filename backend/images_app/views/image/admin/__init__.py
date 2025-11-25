"""
Admin image views module.
"""
from .list_views import AdminImagesListView
from .crud_views import (
    AdminImageDetailView,
    AdminImageUpdateView,
    AdminImageDeleteView,
)
from .bulk_views import AdminBulkUpdateView
from .stats_views import AdminDatasetStatsView

__all__ = [
    'AdminImagesListView',
    'AdminImageDetailView',
    'AdminImageUpdateView',
    'AdminImageDeleteView',
    'AdminBulkUpdateView',
    'AdminDatasetStatsView',
]

