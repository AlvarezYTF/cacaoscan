"""
Reports app views module.
"""
import sys
import importlib.util
from pathlib import Path

from images_app.models import CacaoImage

from .reports import (
    ReporteListCreateView,
    ReporteDetailView,
    ReporteDownloadView,
    ReporteDeleteView,
    ReporteStatsView,
    ReporteCleanupView,
    ReporteAgricultoresView,
    ReporteUsuariosView,
)

# Import views from the parent module (reports/views.py)
# Import directly from the file to avoid package/module name conflict
_parent_dir = Path(__file__).parent.parent
_views_module_path = _parent_dir / 'views.py'
if _views_module_path.exists():
    spec = importlib.util.spec_from_file_location('reports.views_module', _views_module_path)
    if spec and spec.loader:
        views_module = importlib.util.module_from_spec(spec)
        sys.modules['reports.views_module'] = views_module
        spec.loader.exec_module(views_module)
        
        # Ensure CacaoImage is available in views_module
        if not hasattr(views_module, 'CacaoImage'):
            views_module.CacaoImage = CacaoImage
        
        GenerateQualityReportView = views_module.GenerateQualityReportView
        GenerateDefectsReportView = views_module.GenerateDefectsReportView
        GeneratePerformanceReportView = views_module.GeneratePerformanceReportView
        ReportStatsView = views_module.ReportStatsView
        apply_image_filters = views_module.apply_image_filters
        apply_query_filters = views_module.apply_query_filters
        generate_pdf_response = views_module.generate_pdf_response
        handle_report_error = views_module.handle_report_error
        FILTER_DATE_FROM = views_module.FILTER_DATE_FROM
        FILTER_DATE_TO = views_module.FILTER_DATE_TO
        FILTER_REGION = views_module.FILTER_REGION
        CONTENT_TYPE_PDF = views_module.CONTENT_TYPE_PDF
        ERROR_REPORT_GENERATION = views_module.ERROR_REPORT_GENERATION
        logger = views_module.logger
    else:
        raise ImportError("Could not load reports/views.py module")
else:
    raise ImportError(f"Module file not found: {_views_module_path}")

__all__ = [
    'CacaoImage',
    'ReporteListCreateView',
    'ReporteDetailView',
    'ReporteDownloadView',
    'ReporteDeleteView',
    'ReporteStatsView',
    'ReporteCleanupView',
    'ReporteAgricultoresView',
    'ReporteUsuariosView',
    'GenerateQualityReportView',
    'GenerateDefectsReportView',
    'GeneratePerformanceReportView',
    'ReportStatsView',
    'apply_image_filters',
    'apply_query_filters',
    'generate_pdf_response',
    'handle_report_error',
    'FILTER_DATE_FROM',
    'FILTER_DATE_TO',
    'FILTER_REGION',
    'CONTENT_TYPE_PDF',
    'ERROR_REPORT_GENERATION',
    'logger',
]
