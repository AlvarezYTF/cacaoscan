"""
URLs para la API de CacaoScan.
"""
from django.urls import path
from . import views
# Import views from modular structure
from .views import (
    # Auth views (from auth_app)
    LoginView, RegisterView, LogoutView, UserProfileView, RefreshTokenView,
    ChangePasswordView, EmailVerificationView, ResendVerificationView,
    PreRegisterView, VerifyEmailPreRegistrationView, ForgotPasswordView,
    ResetPasswordView, SendOtpView, VerifyOtpView,
    # User views (from auth_app)
    UserListView, UserUpdateView, UserDeleteView, UserStatsView,
    AdminStatsView, UserDetailView,
    # Image views (from images_app)
    ScanMeasureView, ImagesListView, ImageDetailView, ImagesStatsView,
    ImageUpdateView, ImageDeleteView, ImageDownloadView, ImagesExportView,
    AdminImagesListView, AdminImageDetailView, AdminImageUpdateView,
    AdminImageDeleteView, AdminBulkUpdateView, AdminDatasetStatsView,
    BatchAnalysisView,
    # Finca views (from fincas_app)
    FincaListCreateView, FincaDetailView, FincaUpdateView,
    FincaDeleteView, FincaActivateView, FincaStatsView,
    LoteListCreateView, LoteDetailView, LoteUpdateView,
    LoteDeleteView, LoteStatsView, LotesPorFincaView,
    # Report views (from reports)
    ReporteListCreateView, ReporteDetailView, ReporteDownloadView,
    ReporteDeleteView, ReporteStatsView, ReporteCleanupView,
    ReporteAgricultoresView, ReporteUsuariosView,
    # Training views (from ml module)
    TrainingJobListView, TrainingJobCreateView, TrainingJobStatusView,
    # ML views (from ml module)
    ModelsStatusView, DatasetValidationView, LoadModelsView, AutoInitializeView,
    LatestMetricsView, PromoteModelView
)
# Import remaining views from api/views (not moved to modular apps)
from .views.notifications import (
    NotificationListCreateView, NotificationDetailView,
    NotificationMarkReadView, NotificationMarkAllReadView,
    NotificationUnreadCountView, NotificationStatsView,
    NotificationCreateView,
)
from .views.admin import (
    ActivityLogListView, LoginHistoryListView, AuditStatsView,
    SystemSettingsView, SystemGeneralConfigView, SystemSecurityConfigView,
    SystemMLConfigView, SystemInfoView, TaskStatusView,
    EmailStatusView, SendTestEmailView, SendBulkNotificationView,
    EmailTemplatePreviewView, EmailLogsView,
)
from .views.ml import (
    CalibrationStatusView, CalibrationView, CalibratedScanMeasureView,
    IncrementalTrainingStatusView, IncrementalTrainingView,
    IncrementalDataUploadView, IncrementalModelVersionsView,
    IncrementalDataVersionsView,
    ModelMetricsListView, ModelMetricsDetailView, ModelMetricsCreateView,
    ModelMetricsUpdateView, ModelMetricsDeleteView, ModelMetricsStatsView,
    ModelPerformanceTrendView, ModelComparisonView, BestModelsView,
    ProductionModelsView,
    ModelsStatusView, LoadModelsView, UnloadModelsView, AutoTrainView,
)

urlpatterns = [
    # Endpoints principales
    path('scan/measure/', ScanMeasureView.as_view(), name='scan-measure'),
    path('models/status/', ModelsStatusView.as_view(), name='models-status'),
    path('models/load/', LoadModelsView.as_view(), name='load-models'),
    path('dataset/validation/', DatasetValidationView.as_view(), name='dataset-validation'),
    
    # Endpoints ML (alias para compatibilidad con tests)
    path('ml/models/status/', ModelsStatusView.as_view(), name='ml-models-status'),
    path('ml/models/load/', LoadModelsView.as_view(), name='ml-models-load'),
    path('ml/models/unload/', UnloadModelsView.as_view(), name='ml-models-unload'),
    path('ml/auto-train/', AutoTrainView.as_view(), name='ml-auto-train'),
    
    # Endpoints de estado de tareas Celery
    path('tasks/<str:task_id>/status/', TaskStatusView.as_view(), name='task-status'),
    path('admin/tasks/<str:task_id>/status/', TaskStatusView.as_view(), name='admin-task-status'),
    
    # Inicialización automática
    path('auto-initialize/', AutoInitializeView.as_view(), name='auto-initialize'),
    
    # Endpoints de autenticación
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/profile/', UserProfileView.as_view(), name='auth-profile'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    
    # Endpoints de verificación de email
    path('auth/verify-email/', EmailVerificationView.as_view(), name='auth-verify-email'),
    path('auth/verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='auth-verify-email-token'),
    path('auth/resend-verification/', ResendVerificationView.as_view(), name='auth-resend-verification'),
    
    # Endpoints OTP de verificación
    path('auth/send-otp/', SendOtpView.as_view(), name='auth-send-otp'),
    path('auth/verify-otp/', VerifyOtpView.as_view(), name='auth-verify-otp'),
    
    # Endpoints de pre-registro (verificación previa)
    path('auth/preregistro/', PreRegisterView.as_view(), name='auth-preregister'),
    path('auth/verificar/<uuid:token>/', VerifyEmailPreRegistrationView.as_view(), name='auth-verify-email-pre-registration'),
    
    # Endpoints de recuperación de contraseña
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='auth-reset-password'),
    
    # Endpoints de imágenes
    path('images/', ImagesListView.as_view(), name='images-list'),
    path('images/<int:image_id>/', ImageDetailView.as_view(), name='image-detail'),
    path('images/<int:image_id>/update/', ImageUpdateView.as_view(), name='image-update'),
    path('images/<int:image_id>/delete/', ImageDeleteView.as_view(), name='image-delete'),
    path('images/<int:image_id>/download/', ImageDownloadView.as_view(), name='image-download'),
    path('images/stats/', ImagesStatsView.as_view(), name='images-stats'),
    path('images/export/', ImagesExportView.as_view(), name='images-export'),
    
    # Endpoints de gestión de usuarios (Admin)
    path('auth/users/', UserListView.as_view(), name='user-list'),
    path('auth/users/stats/', UserStatsView.as_view(), name='users-stats'),
    path('auth/users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('auth/users/<int:user_id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('auth/users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('auth/admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    
    # Endpoints de panel admin de dataset global
    path('images/admin/images/', AdminImagesListView.as_view(), name='admin-images-list'),
    path('images/admin/images/<int:image_id>/', AdminImageDetailView.as_view(), name='admin-image-detail'),
    path('images/admin/images/<int:image_id>/update/', AdminImageUpdateView.as_view(), name='admin-image-update'),
    path('images/admin/images/<int:image_id>/delete/', AdminImageDeleteView.as_view(), name='admin-image-delete'),
    path('images/admin/images/bulk-update/', AdminBulkUpdateView.as_view(), name='admin-bulk-update'),
    path('images/admin/images/admin-stats/', AdminDatasetStatsView.as_view(), name='admin-dataset-stats'),
    
    # Endpoints de sistema de entrenamiento
    path('train/jobs/', TrainingJobListView.as_view(), name='training-jobs-list'),
    path('train/jobs/create/', TrainingJobCreateView.as_view(), name='training-job-create'),
    path('train/jobs/<str:job_id>/status/', TrainingJobStatusView.as_view(), name='training-job-status'),
    
    # Endpoints ML (alias más simples)
    path('ml/train/', TrainingJobCreateView.as_view(), name='ml-train'),
    path('ml/metrics/latest/', LatestMetricsView.as_view(), name='ml-metrics-latest'),
    path('ml/promote/<str:version>/', PromoteModelView.as_view(), name='ml-promote'),
    
    # Endpoints de gestin de fincas
    path('fincas/', FincaListCreateView.as_view(), name='fincas-list-create'),
    path('fincas/<int:finca_id>/', FincaDetailView.as_view(), name='finca-detail'),
    path('fincas/<int:finca_id>/update/', FincaUpdateView.as_view(), name='finca-update'),
    path('fincas/<int:finca_id>/delete/', FincaDeleteView.as_view(), name='finca-delete'),
    path('fincas/<int:finca_id>/activate/', FincaActivateView.as_view(), name='finca-activate'),
    path('fincas/<int:finca_id>/stats/', FincaStatsView.as_view(), name='finca-stats'),
    path('fincas/stats/', FincaStatsView.as_view(), name='fincas-stats'),
    
    # Endpoints de gestión de lotes
    path('lotes/', LoteListCreateView.as_view(), name='lotes-list'),
    path('lotes/', LoteListCreateView.as_view(), name='lotes-list-create'),
    path('lotes/<int:pk>/', LoteDetailView.as_view(), name='lotes-detail'),
    path('lotes/<int:lote_id>/', LoteDetailView.as_view(), name='lote-detail'),
    path('lotes/<int:lote_id>/update/', LoteUpdateView.as_view(), name='lote-update'),
    path('lotes/<int:lote_id>/delete/', LoteDeleteView.as_view(), name='lote-delete'),
    path('lotes/<int:lote_id>/stats/', LoteStatsView.as_view(), name='lote-stats'),
    path('fincas/<int:finca_id>/lotes/', LotesPorFincaView.as_view(), name='lotes-por-finca'),
    
    # Endpoints de gestión de notificaciones
    path('notifications/', NotificationListCreateView.as_view(), name='notifications-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/<int:notification_id>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notifications-mark-all-read'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notifications-unread-count'),
    path('notifications/stats/', NotificationStatsView.as_view(), name='notification-stats'),
    path('notifications/stats/', NotificationStatsView.as_view(), name='notifications-stats'),
    path('notifications/create/', NotificationCreateView.as_view(), name='notification-create'),
    path('admin/notifications/create/', NotificationCreateView.as_view(), name='admin-notification-create'),
    
    # Endpoints de auditoría (solo administradores)
    path('audit/activity-logs/', ActivityLogListView.as_view(), name='activity-logs-list'),
    path('audit/login-history/', LoginHistoryListView.as_view(), name='login-history-list'),
    path('audit/stats/', AuditStatsView.as_view(), name='audit-stats'),
    
    # Endpoints de gestión de reportes
    path('reportes/', ReporteListCreateView.as_view(), name='reportes-list-create'),
    path('reportes/<int:pk>/', ReporteDetailView.as_view(), name='reportes-detail'),
    path('reportes/<int:reporte_id>/', ReporteDetailView.as_view(), name='reporte-detail'),
    path('reportes/<int:pk>/download/', ReporteDownloadView.as_view(), name='reportes-download'),
    path('reportes/<int:reporte_id>/download/', ReporteDownloadView.as_view(), name='reporte-download'),
    path('reportes/<int:reporte_id>/delete/', ReporteDeleteView.as_view(), name='reporte-delete'),
    path('reportes/stats/', ReporteStatsView.as_view(), name='reportes-stats'),
    path('reportes/cleanup/', ReporteCleanupView.as_view(), name='reportes-cleanup'),
    
    # Endpoints de reportes especiales (solo admin)
    path('reports/agricultores/', ReporteAgricultoresView.as_view(), name='reporte-agricultores'),
    path('reports/usuarios/', ReporteUsuariosView.as_view(), name='reporte-usuarios'),
    
    # Endpoints de calibración
    path('calibration/status/', CalibrationStatusView.as_view(), name='calibration-status'),
    path('calibration/', CalibrationView.as_view(), name='calibration'),
    path('scan/measure/calibrated/', CalibratedScanMeasureView.as_view(), name='scan-measure-calibrated'),
    path('ml/calibration/upload/', CalibrationView.as_view(), name='ml-calibration-upload'),
    path('ml/calibration/status/', CalibrationStatusView.as_view(), name='ml-calibration-status'),
    
    
    # Endpoints de entrenamiento incremental
    path('incremental/status/', IncrementalTrainingStatusView.as_view(), name='incremental-status'),
    path('incremental/train/', IncrementalTrainingView.as_view(), name='incremental-train'),
    path('incremental/upload/', IncrementalDataUploadView.as_view(), name='incremental-upload'),
    path('incremental/models/', IncrementalModelVersionsView.as_view(), name='incremental-models'),
    path('incremental/data/', IncrementalDataVersionsView.as_view(), name='incremental-data'),
    path('ml/incremental/status/', IncrementalTrainingStatusView.as_view(), name='ml-incremental-status'),
    path('ml/incremental/start/', IncrementalTrainingView.as_view(), name='ml-incremental-start'),
    path('ml/incremental/stop/', IncrementalTrainingView.as_view(), name='ml-incremental-stop'),
    
    # Endpoints de métricas de modelos
    path('model-metrics/', ModelMetricsListView.as_view(), name='model-metrics-list'),
    path('model-metrics/create/', ModelMetricsCreateView.as_view(), name='model-metrics-create'),
    path('model-metrics/<int:metrics_id>/', ModelMetricsDetailView.as_view(), name='model-metrics-detail'),
    path('model-metrics/<int:metrics_id>/update/', ModelMetricsUpdateView.as_view(), name='model-metrics-update'),
    path('model-metrics/<int:metrics_id>/delete/', ModelMetricsDeleteView.as_view(), name='model-metrics-delete'),
    path('model-metrics/stats/', ModelMetricsStatsView.as_view(), name='model-metrics-stats'),
    path('model-metrics/trend/', ModelPerformanceTrendView.as_view(), name='model-metrics-trend'),
    path('model-metrics/compare/', ModelComparisonView.as_view(), name='model-metrics-compare'),
    path('model-metrics/best/', BestModelsView.as_view(), name='model-metrics-best'),
    path('model-metrics/production/', ProductionModelsView.as_view(), name='model-metrics-production'),
    
    # Endpoints ML metrics (alias para compatibilidad con tests)
    path('ml/metrics/', ModelMetricsListView.as_view(), name='ml-metrics-list'),
    path('ml/metrics/<int:pk>/', ModelMetricsDetailView.as_view(), name='ml-metrics-detail'),
    path('ml/metrics/create/', ModelMetricsCreateView.as_view(), name='ml-metrics-create'),
    path('ml/metrics/<int:pk>/update/', ModelMetricsUpdateView.as_view(), name='ml-metrics-update'),
    path('ml/metrics/<int:pk>/delete/', ModelMetricsDeleteView.as_view(), name='ml-metrics-delete'),
    path('ml/metrics/stats/', ModelMetricsStatsView.as_view(), name='ml-metrics-stats'),
    path('ml/performance-trend/', ModelPerformanceTrendView.as_view(), name='ml-performance-trend'),
    path('ml/best-models/', BestModelsView.as_view(), name='ml-best-models'),
    path('ml/production-models/', ProductionModelsView.as_view(), name='ml-production-models'),
    path('ml/model-comparison/', ModelComparisonView.as_view(), name='ml-model-comparison'),
    path('ml/model-comparison/batch/', ModelComparisonView.as_view(), name='ml-model-comparison-batch'),
    
    # Endpoints de análisis batch
    path('analysis/batch/', BatchAnalysisView.as_view(), name='batch-analysis'),
    
    # Endpoints de configuración del sistema
    path('config/', SystemSettingsView.as_view(), name='system-settings'),
    path('config/general/', SystemGeneralConfigView.as_view(), name='system-general-config'),
    path('config/security/', SystemSecurityConfigView.as_view(), name='system-security-config'),
    path('config/ml/', SystemMLConfigView.as_view(), name='system-ml-config'),
    path('config/system/', SystemInfoView.as_view(), name='system-info'),
    
    # Endpoints de administración de emails
    path('admin/email/status/', EmailStatusView.as_view(), name='admin-email-status'),
    path('admin/email/send-test/', SendTestEmailView.as_view(), name='admin-send-test-email'),
    path('admin/email/bulk-notification/', SendBulkNotificationView.as_view(), name='admin-send-bulk-notification'),
    path('admin/email/template-preview/', EmailTemplatePreviewView.as_view(), name='admin-email-template-preview'),
    path('admin/email/logs/', EmailLogsView.as_view(), name='admin-email-logs'),
]


