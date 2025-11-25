"""
API module for CacaoScan.

This module re-exports views from api.views for backward compatibility.
All new code should import directly from api.views instead.
"""
# Re-export views from api.views module for backward compatibility
# NOTE: These re-exports are maintained for compatibility with urls.py
# New code should import from api.views or specific view modules directly
from .views import (
    # Auth views (from auth_app)
    SendOtpView, VerifyOtpView,
    # Finca views (from fincas_app)
    FincaListCreateView, FincaDetailView, FincaUpdateView,
    FincaDeleteView, FincaActivateView, FincaStatsView,
    LoteListCreateView, LoteDetailView, LoteUpdateView,
    LoteDeleteView, LoteStatsView, LotesPorFincaView,
    # Report views (from reports)
    ReporteListCreateView, ReporteDetailView, ReporteDownloadView,
    ReporteDeleteView, ReporteStatsView, ReporteCleanupView,
    ReporteAgricultoresView, ReporteUsuariosView,
    # Image views (from images_app)
    BatchAnalysisView,
    # Notification views (from api.views.notifications)
    NotificationListCreateView, NotificationDetailView,
    NotificationMarkReadView, NotificationMarkAllReadView,
    NotificationUnreadCountView, NotificationStatsView,
    NotificationCreateView,
    # Admin views (from api.views.admin)
    ActivityLogListView, LoginHistoryListView, AuditStatsView,
    SystemSettingsView, SystemGeneralConfigView, SystemSecurityConfigView,
    SystemMLConfigView, SystemInfoView,
    # ML views (from api.views.ml)
    CalibrationStatusView, CalibrationView, CalibratedScanMeasureView,
    IncrementalTrainingStatusView, IncrementalTrainingView,
    IncrementalDataUploadView, IncrementalModelVersionsView,
    IncrementalDataVersionsView,
    ModelMetricsListView, ModelMetricsDetailView, ModelMetricsCreateView,
    ModelMetricsUpdateView, ModelMetricsDeleteView, ModelMetricsStatsView,
    ModelPerformanceTrendView, ModelComparisonView, BestModelsView,
    ProductionModelsView,
)

__all__ = [
    # OTP views
    'SendOtpView', 'VerifyOtpView',
    # Finca views
    'FincaListCreateView', 'FincaDetailView', 'FincaUpdateView',
    'FincaDeleteView', 'FincaActivateView', 'FincaStatsView',
    # Lote views
    'LoteListCreateView', 'LoteDetailView', 'LoteUpdateView',
    'LoteDeleteView', 'LoteStatsView', 'LotesPorFincaView',
    # Notification views
    'NotificationListCreateView', 'NotificationDetailView',
    'NotificationMarkReadView', 'NotificationMarkAllReadView',
    'NotificationUnreadCountView', 'NotificationStatsView',
    'NotificationCreateView',
    # Audit views
    'ActivityLogListView', 'LoginHistoryListView', 'AuditStatsView',
    # Report views
    'ReporteListCreateView', 'ReporteDetailView', 'ReporteDownloadView',
    'ReporteDeleteView', 'ReporteStatsView', 'ReporteCleanupView',
    'ReporteAgricultoresView', 'ReporteUsuariosView',
    # Calibration views
    'CalibrationStatusView', 'CalibrationView', 'CalibratedScanMeasureView',
    # Incremental views
    'IncrementalTrainingStatusView', 'IncrementalTrainingView',
    'IncrementalDataUploadView', 'IncrementalModelVersionsView',
    'IncrementalDataVersionsView',
    # Model metrics views
    'ModelMetricsListView', 'ModelMetricsDetailView', 'ModelMetricsCreateView',
    'ModelMetricsUpdateView', 'ModelMetricsDeleteView', 'ModelMetricsStatsView',
    'ModelPerformanceTrendView', 'ModelComparisonView', 'BestModelsView',
    'ProductionModelsView',
    # Batch analysis views
    'BatchAnalysisView',
    # Config views
    'SystemSettingsView', 'SystemGeneralConfigView', 'SystemSecurityConfigView',
    'SystemMLConfigView', 'SystemInfoView',
]

