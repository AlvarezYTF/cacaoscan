"""
Batch analysis views module.
"""
from .batch_upload_views import BatchAnalysisView
from .batch_process_views import BatchImageProcessor

__all__ = [
    'BatchAnalysisView',
    'BatchImageProcessor',
]
