"""
Image views module.
"""
from .user import (
    ScanMeasureView,
    ImagesListView,
    ImageDetailView,
    ImagesStatsView,
    ImageUpdateView,
    ImageDeleteView,
    ImageDownloadView,
)
from .admin import (
    AdminImagesListView,
    AdminImageDetailView,
    AdminImageUpdateView,
    AdminImageDeleteView,
    AdminBulkUpdateView,
    AdminDatasetStatsView,
)
from .export import ImagesExportView
from .batch import BatchAnalysisView
from .mixins import ImagePermissionMixin

__all__ = [
    # User views
    'ScanMeasureView',
    'ImagesListView',
    'ImageDetailView',
    'ImagesStatsView',
    'ImageUpdateView',
    'ImageDeleteView',
    'ImageDownloadView',
    # Admin views
    'AdminImagesListView',
    'AdminImageDetailView',
    'AdminImageUpdateView',
    'AdminImageDeleteView',
    'AdminBulkUpdateView',
    'AdminDatasetStatsView',
    # Export views
    'ImagesExportView',
    # Batch analysis
    'BatchAnalysisView',
    # Mixins
    'ImagePermissionMixin',
]
