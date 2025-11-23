"""
Image views module.
"""
from .user_image_views import (
    ScanMeasureView,
    ImagesListView,
    ImageDetailView,
    ImagesStatsView,
    ImageUpdateView,
    ImageDeleteView,
    ImageDownloadView,
)
from .admin_image_views import (
    AdminImagesListView,
    AdminImageDetailView,
    AdminImageUpdateView,
    AdminImageDeleteView,
    AdminBulkUpdateView,
    AdminDatasetStatsView,
)
from .image_export_views import ImagesExportView
from .batch_analysis_views import BatchAnalysisView
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
