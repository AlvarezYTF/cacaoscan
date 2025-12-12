"""
Views module for CacaoScan API.
Organized by domain for better maintainability.
Re-exports views from modular apps for backward compatibility.
"""
# Import views from modular apps
from auth_app.views import (
    LoginView,
    RegisterView,
    LogoutView,
    UserProfileView,
    RefreshTokenView,
    ChangePasswordView,
    EmailVerificationView,
    ResendVerificationView,
    PreRegisterView,
    VerifyEmailPreRegistrationView,
    ForgotPasswordView,
    ResetPasswordView,
    SetPasswordView,
    SendOtpView,
    VerifyOtpView,
    UserListView,
    UserUpdateView,
    UserDeleteView,
    UserStatsView,
    AdminStatsView,
    UserDetailView,
    GoogleLoginView,
)

# Images app views imported lazily to avoid circular dependency
# They are available in __all__ but imported on demand via __getattr__
_images_views = None

# Fincas app views imported lazily to avoid circular dependency
# They are available in __all__ but imported on demand via __getattr__
_fincas_views = None

# Reports views imported lazily to avoid circular dependency
# They are available in __all__ but imported on demand via __getattr__
_reports_views = None

# Import views that remain in api/views
from .notifications import (
    NotificationListCreateView, NotificationDetailView,
    NotificationMarkReadView, NotificationMarkAllReadView,
    NotificationUnreadCountView, NotificationStatsView,
    NotificationCreateView,
)
from .admin import (
    ActivityLogListView, LoginHistoryListView, AuditStatsView,
    SystemSettingsView, SystemGeneralConfigView, SystemSecurityConfigView,
    SystemMLConfigView, SystemInfoView,
    TaskStatusView,
)
from .ml import (
    CalibrationStatusView, CalibrationView, CalibratedScanMeasureView,
    IncrementalTrainingStatusView, IncrementalTrainingView,
    IncrementalDataUploadView, IncrementalModelVersionsView,
    IncrementalDataVersionsView,
    ModelMetricsListView, ModelMetricsDetailView, ModelMetricsCreateView,
    ModelMetricsUpdateView, ModelMetricsDeleteView, ModelMetricsStatsView,
    ModelPerformanceTrendView, ModelComparisonView, BestModelsView,
    ProductionModelsView,
    # Model views
    ModelsStatusView,
    DatasetValidationView,
    LoadModelsView,
    AutoInitializeView,
    LatestMetricsView,
    PromoteModelView,
    AutoTrainView,
    # Training views
    TrainingJobListView,
    TrainingJobCreateView,
    TrainingJobStatusView,
)
__all__ = [
    # Auth views
    'LoginView',
    'RegisterView',
    'LogoutView',
    'UserProfileView',
    'RefreshTokenView',
    'GoogleLoginView',
    'ChangePasswordView',
    'EmailVerificationView',
    'ResendVerificationView',
    'PreRegisterView',
    'VerifyEmailPreRegistrationView',
    'ForgotPasswordView',
    'ResetPasswordView',
    'SetPasswordView',
    # Image views
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
    # User views (moved to auth module)
    'UserListView',
    'UserUpdateView',
    'UserDeleteView',
    'UserStatsView',
    'AdminStatsView',
    'UserDetailView',
    # Training views (moved to ml module)
    'TrainingJobListView',
    'TrainingJobCreateView',
    'TrainingJobStatusView',
    # ML views (moved to ml module)
    'ModelsStatusView',
    'DatasetValidationView',
    'LoadModelsView',
    'AutoInitializeView',
    'LatestMetricsView',
    'PromoteModelView',
    'AutoTrainView',
    # Finca views
    'FincaListCreateView',
    'FincaDetailView',
    'FincaUpdateView',
    'FincaDeleteView',
    'FincaActivateView',
    'FincaStatsView',
    'LoteListCreateView',
    'LoteDetailView',
    'LoteUpdateView',
    'LoteDeleteView',
    'LoteStatsView',
    'LotesPorFincaView',
    'LoteAnalisisView',
    # Auth OTP views
    'SendOtpView',
    'VerifyOtpView',
    # Notification views
    'NotificationListCreateView',
    'NotificationDetailView',
    'NotificationMarkReadView',
    'NotificationMarkAllReadView',
    'NotificationUnreadCountView',
    'NotificationStatsView',
    'NotificationCreateView',
    # Admin views
    'ActivityLogListView',
    'LoginHistoryListView',
    'AuditStatsView',
    'SystemSettingsView',
    'SystemGeneralConfigView',
    'SystemSecurityConfigView',
    'SystemMLConfigView',
    'SystemInfoView',
    'TaskStatusView',
    # Report views
    'ReporteListCreateView',
    'ReporteDetailView',
    'ReporteDownloadView',
    'ReporteDeleteView',
    'ReporteStatsView',
    'ReporteCleanupView',
    'ReporteAgricultoresView',
    'ReporteUsuariosView',
    # ML views (calibration, incremental, metrics)
    'CalibrationStatusView',
    'CalibrationView',
    'CalibratedScanMeasureView',
    'IncrementalTrainingStatusView',
    'IncrementalTrainingView',
    'IncrementalDataUploadView',
    'IncrementalModelVersionsView',
    'IncrementalDataVersionsView',
    'ModelMetricsListView',
    'ModelMetricsDetailView',
    'ModelMetricsCreateView',
    'ModelMetricsUpdateView',
    'ModelMetricsDeleteView',
    'ModelMetricsStatsView',
    'ModelPerformanceTrendView',
    'ModelComparisonView',
    'BestModelsView',
    'ProductionModelsView',
    # Image batch views
    'BatchAnalysisView',
]


def _lazy_import_images_views():
    """Lazy import of images app views to avoid circular dependency."""
    global _images_views
    if _images_views is None:
        from images_app.views import (
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
        _images_views = {
            'ScanMeasureView': ScanMeasureView,
            'ImagesListView': ImagesListView,
            'ImageDetailView': ImageDetailView,
            'ImagesStatsView': ImagesStatsView,
            'ImageUpdateView': ImageUpdateView,
            'ImageDeleteView': ImageDeleteView,
            'ImageDownloadView': ImageDownloadView,
            'ImagesExportView': ImagesExportView,
            'AdminImagesListView': AdminImagesListView,
            'AdminImageDetailView': AdminImageDetailView,
            'AdminImageUpdateView': AdminImageUpdateView,
            'AdminImageDeleteView': AdminImageDeleteView,
            'AdminBulkUpdateView': AdminBulkUpdateView,
            'AdminDatasetStatsView': AdminDatasetStatsView,
            'ImagePermissionMixin': ImagePermissionMixin,
            'BatchAnalysisView': BatchAnalysisView,
        }
    return _images_views


def _lazy_import_fincas_views():
    """Lazy import of fincas app views to avoid circular dependency."""
    global _fincas_views
    if _fincas_views is None:
        from fincas_app.views import (
            FincaListCreateView,
            FincaDetailView,
            FincaUpdateView,
            FincaDeleteView,
            FincaActivateView,
            FincaStatsView,
            LoteListCreateView,
            LoteDetailView,
            LoteUpdateView,
            LoteDeleteView,
            LoteStatsView,
            LotesPorFincaView,
            LoteAnalisisView,
        )
        _fincas_views = {
            'FincaListCreateView': FincaListCreateView,
            'FincaDetailView': FincaDetailView,
            'FincaUpdateView': FincaUpdateView,
            'FincaDeleteView': FincaDeleteView,
            'FincaActivateView': FincaActivateView,
            'FincaStatsView': FincaStatsView,
            'LoteListCreateView': LoteListCreateView,
            'LoteDetailView': LoteDetailView,
            'LoteUpdateView': LoteUpdateView,
            'LoteDeleteView': LoteDeleteView,
            'LoteStatsView': LoteStatsView,
            'LotesPorFincaView': LotesPorFincaView,
            'LoteAnalisisView': LoteAnalisisView,
        }
    return _fincas_views

def _lazy_import_reports_views():
    """Lazy import of reports app views to avoid circular dependency."""
    global _reports_views
    if _reports_views is None:
        from reports.views import (
            ReporteListCreateView,
            ReporteDetailView,
            ReporteDownloadView,
            ReporteDeleteView,
            ReporteStatsView,
            ReporteCleanupView,
            ReporteAgricultoresView,
            ReporteUsuariosView,
        )
        _reports_views = {
            'ReporteListCreateView': ReporteListCreateView,
            'ReporteDetailView': ReporteDetailView,
            'ReporteDownloadView': ReporteDownloadView,
            'ReporteDeleteView': ReporteDeleteView,
            'ReporteStatsView': ReporteStatsView,
            'ReporteCleanupView': ReporteCleanupView,
            'ReporteAgricultoresView': ReporteAgricultoresView,
            'ReporteUsuariosView': ReporteUsuariosView,
        }
    return _reports_views


def __getattr__(name: str):
    """Lazy import for images, fincas and reports app views to avoid circular dependency."""
    images_views = _lazy_import_images_views()
    if name in images_views:
        return images_views[name]
    
    fincas_views = _lazy_import_fincas_views()
    if name in fincas_views:
        return fincas_views[name]
    
    reports_views = _lazy_import_reports_views()
    if name in reports_views:
        return reports_views[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

