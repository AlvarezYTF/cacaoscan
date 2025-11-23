"""
Views module for CacaoScan API.
Organized by domain for better maintainability.
"""
from .auth import (
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
)

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

from .user_views import (
    UserListView,
    UserUpdateView,
    UserDeleteView,
    UserStatsView,
    AdminStatsView,
    UserDetailView
)

from .training_views import (
    TrainingJobListView,
    TrainingJobCreateView,
    TrainingJobStatusView
)

from .ml_views import (
    ModelsStatusView,
    DatasetValidationView,
    LoadModelsView,
    AutoInitializeView,
    LatestMetricsView,
    PromoteModelView,
    AutoTrainView
)

# Import views from new modular structure
from .finca import (
    FincaListCreateView, FincaDetailView, FincaUpdateView,
    FincaDeleteView, FincaActivateView, FincaStatsView,
    LoteListCreateView, LoteDetailView, LoteUpdateView,
    LoteDeleteView, LoteStatsView, LotesPorFincaView,
)
# OTP views already imported from .auth above
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
)
from .reports import (
    ReporteListCreateView, ReporteDetailView, ReporteDownloadView,
    ReporteDeleteView, ReporteStatsView, ReporteCleanupView,
    ReporteAgricultoresView, ReporteUsuariosView,
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
)
__all__ = [
    # Auth views
    'LoginView',
    'RegisterView',
    'LogoutView',
    'UserProfileView',
    'RefreshTokenView',
    'ChangePasswordView',
    'EmailVerificationView',
    'ResendVerificationView',
    'PreRegisterView',
    'VerifyEmailPreRegistrationView',
    'ForgotPasswordView',
    'ResetPasswordView',
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
    # User views
    'UserListView',
    'UserUpdateView',
    'UserDeleteView',
    'UserStatsView',
    'AdminStatsView',
    'UserDetailView',
    # Training views
    'TrainingJobListView',
    'TrainingJobCreateView',
    'TrainingJobStatusView',
    # ML views
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

