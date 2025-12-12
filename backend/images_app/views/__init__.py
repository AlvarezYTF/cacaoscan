"""
Images app views module.
"""
# Import views from views.py file (avoiding conflict with views directory)
import sys
import importlib.util
from pathlib import Path

# Import from the views.py file in parent directory
_parent_dir = Path(__file__).parent.parent
_views_module_path = _parent_dir / 'views.py'
if _views_module_path.exists():
    spec = importlib.util.spec_from_file_location('images_app.views_module', _views_module_path)
    if spec and spec.loader:
        views_module = importlib.util.module_from_spec(spec)
        sys.modules['images_app.views_module'] = views_module
        spec.loader.exec_module(views_module)
        
        CacaoImageUploadView = views_module.CacaoImageUploadView
        CacaoImageListView = views_module.CacaoImageListView
    else:
        raise ImportError("Could not load images_app/views.py module")
else:
    raise ImportError(f"Module file not found: {_views_module_path}")

from .image import (
    ScanMeasureView,
    ImagesListView,
    ImageDetailView,
    ImagesStatsView,
    ImageUpdateView,
    ImageDeleteView,
    ImageDownloadView,
    ImagesExportView,
    AdminImagesListView,
    AdminImageDetailView,
    AdminImageUpdateView,
    AdminImageDeleteView,
    AdminBulkUpdateView,
    AdminDatasetStatsView,
    ImagePermissionMixin,
    BatchAnalysisView,
)

__all__ = [
    'ScanMeasureView',
    'ImagesListView',
    'ImageDetailView',
    'ImagesStatsView',
    'ImageUpdateView',
    'ImageDeleteView',
    'ImageDownloadView',
    'ImagesExportView',
    'AdminImagesListView',
    'AdminImageDetailView',
    'AdminImageUpdateView',
    'AdminImageDeleteView',
    'AdminBulkUpdateView',
    'AdminDatasetStatsView',
    'ImagePermissionMixin',
    'BatchAnalysisView',
]

# Add CacaoImageUploadView and CacaoImageListView if they exist
if CacaoImageUploadView:
    __all__.append('CacaoImageUploadView')
if CacaoImageListView:
    __all__.append('CacaoImageListView')
