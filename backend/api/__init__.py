"""
API module for CacaoScan.
"""
# Re-export views from separate modules for backward compatibility
from .otp_views import SendOtpView, VerifyOtpView
from .fincas_views import (
    FincaListCreateView, FincaDetailView, FincaUpdateView,
    FincaDeleteView, FincaActivateView, FincaStatsView
)
from .lotes_views import (
    LoteListCreateView, LoteDetailView, LoteUpdateView,
    LoteDeleteView, LoteStatsView, LotesPorFincaView
)
from .notifications_views import (
    NotificationListCreateView, NotificationDetailView,
    NotificationMarkReadView, NotificationMarkAllReadView,
    NotificationUnreadCountView, NotificationStatsView,
    NotificationCreateView
)
from .audit_views import (
    ActivityLogListView, LoginHistoryListView, AuditStatsView
)
from .report_views import (
    ReporteListCreateView, ReporteDetailView, ReporteDownloadView,
    ReporteDeleteView, ReporteStatsView, ReporteCleanupView,
    ReporteAgricultoresView, ReporteUsuariosView
)
from .calibration_views import (
    CalibrationStatusView, CalibrationView, CalibratedScanMeasureView
)
from .incremental_views import (
    IncrementalTrainingStatusView, IncrementalTrainingView,
    IncrementalDataUploadView, IncrementalModelVersionsView,
    IncrementalDataVersionsView
)
from .model_metrics_views import (
    ModelMetricsListView, ModelMetricsDetailView, ModelMetricsCreateView,
    ModelMetricsUpdateView, ModelMetricsDeleteView, ModelMetricsStatsView,
    ModelPerformanceTrendView, ModelComparisonView, BestModelsView,
    ProductionModelsView
)
from .batch_analysis_views import BatchAnalysisView
from .config_views import (
    SystemSettingsView, SystemGeneralConfigView, SystemSecurityConfigView,
    SystemMLConfigView, SystemInfoView
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

