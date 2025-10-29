"""
URLs para la API de CacaoScan.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Endpoints principales
    path('scan/measure/', views.ScanMeasureView.as_view(), name='scan-measure'),
    path('models/status/', views.ModelsStatusView.as_view(), name='models-status'),
    path('models/load/', views.LoadModelsView.as_view(), name='load-models'),
    path('dataset/validation/', views.DatasetValidationView.as_view(), name='dataset-validation'),
    
    # Inicialización automática
    path('auto-initialize/', views.AutoInitializeView.as_view(), name='auto-initialize'),
    
    # Endpoints de autenticación
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('auth/profile/', views.UserProfileView.as_view(), name='auth-profile'),
    path('auth/refresh/', views.RefreshTokenView.as_view(), name='auth-refresh'),
    
    # Endpoints de verificación de email
    path('auth/verify-email/', views.EmailVerificationView.as_view(), name='auth-verify-email'),
    path('auth/resend-verification/', views.ResendVerificationView.as_view(), name='auth-resend-verification'),
    
    # Endpoints de recuperación de contraseña
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('auth/reset-password/', views.ResetPasswordView.as_view(), name='auth-reset-password'),
    
    # Endpoints de imágenes
    path('images/', views.ImagesListView.as_view(), name='images-list'),
    path('images/<int:image_id>/', views.ImageDetailView.as_view(), name='image-detail'),
    path('images/<int:image_id>/update/', views.ImageUpdateView.as_view(), name='image-update'),
    path('images/<int:image_id>/delete/', views.ImageDeleteView.as_view(), name='image-delete'),
    path('images/<int:image_id>/download/', views.ImageDownloadView.as_view(), name='image-download'),
    path('images/stats/', views.ImagesStatsView.as_view(), name='images-stats'),
    path('images/export/', views.ImagesExportView.as_view(), name='images-export'),
    
    # Endpoints de gestión de usuarios (Admin)
    path('auth/users/', views.UserListView.as_view(), name='user-list'),
    path('auth/users/stats/', views.UserStatsView.as_view(), name='users-stats'),
    path('auth/users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('auth/users/<int:user_id>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('auth/users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    path('auth/admin/stats/', views.AdminStatsView.as_view(), name='admin-stats'),
    
    # Endpoints de panel admin de dataset global
    path('images/admin/images/', views.AdminImagesListView.as_view(), name='admin-images-list'),
    path('images/admin/images/<int:image_id>/', views.AdminImageDetailView.as_view(), name='admin-image-detail'),
    path('images/admin/images/<int:image_id>/update/', views.AdminImageUpdateView.as_view(), name='admin-image-update'),
    path('images/admin/images/<int:image_id>/delete/', views.AdminImageDeleteView.as_view(), name='admin-image-delete'),
    path('images/admin/images/bulk-update/', views.AdminBulkUpdateView.as_view(), name='admin-bulk-update'),
    path('images/admin/images/admin-stats/', views.AdminDatasetStatsView.as_view(), name='admin-dataset-stats'),
    
    # Endpoints de sistema de entrenamiento
    path('train/jobs/', views.TrainingJobListView.as_view(), name='training-jobs-list'),
    path('train/jobs/create/', views.TrainingJobCreateView.as_view(), name='training-job-create'),
    path('train/jobs/<str:job_id>/status/', views.TrainingJobStatusView.as_view(), name='training-job-status'),
    
    # Endpoints de gestión de fincas
    path('fincas/', views.FincaListCreateView.as_view(), name='fincas-list-create'),
    path('fincas/<int:finca_id>/', views.FincaDetailView.as_view(), name='finca-detail'),
    path('fincas/<int:finca_id>/update/', views.FincaUpdateView.as_view(), name='finca-update'),
    path('fincas/<int:finca_id>/delete/', views.FincaDeleteView.as_view(), name='finca-delete'),
    path('fincas/<int:finca_id>/activate/', views.FincaActivateView.as_view(), name='finca-activate'),
    path('fincas/<int:finca_id>/stats/', views.FincaStatsView.as_view(), name='finca-stats'),
    
    # Endpoints de gestión de lotes
    path('lotes/', views.LoteListCreateView.as_view(), name='lotes-list-create'),
    path('lotes/<int:lote_id>/', views.LoteDetailView.as_view(), name='lote-detail'),
    path('lotes/<int:lote_id>/update/', views.LoteUpdateView.as_view(), name='lote-update'),
    path('lotes/<int:lote_id>/delete/', views.LoteDeleteView.as_view(), name='lote-delete'),
    path('lotes/<int:lote_id>/stats/', views.LoteStatsView.as_view(), name='lote-stats'),
    path('fincas/<int:finca_id>/lotes/', views.LotesPorFincaView.as_view(), name='lotes-por-finca'),
    
    # Endpoints de gestión de notificaciones
    path('notifications/', views.NotificationListCreateView.as_view(), name='notifications-list'),
    path('notifications/<int:notification_id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:notification_id>/read/', views.NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/mark-all-read/', views.NotificationMarkAllReadView.as_view(), name='notifications-mark-all-read'),
    path('notifications/unread-count/', views.NotificationUnreadCountView.as_view(), name='notifications-unread-count'),
    path('notifications/stats/', views.NotificationStatsView.as_view(), name='notifications-stats'),
    path('notifications/create/', views.NotificationCreateView.as_view(), name='notification-create'),
    
    # Endpoints de auditoría (solo administradores)
    path('audit/activity-logs/', views.ActivityLogListView.as_view(), name='activity-logs-list'),
    path('audit/login-history/', views.LoginHistoryListView.as_view(), name='login-history-list'),
    path('audit/stats/', views.AuditStatsView.as_view(), name='audit-stats'),
    
    # Endpoints de gestión de reportes
    path('reportes/', views.ReporteListCreateView.as_view(), name='reportes-list-create'),
    path('reportes/<int:reporte_id>/', views.ReporteDetailView.as_view(), name='reporte-detail'),
    path('reportes/<int:reporte_id>/download/', views.ReporteDownloadView.as_view(), name='reporte-download'),
    path('reportes/<int:reporte_id>/delete/', views.ReporteDeleteView.as_view(), name='reporte-delete'),
    path('reportes/stats/', views.ReporteStatsView.as_view(), name='reportes-stats'),
    path('reportes/cleanup/', views.ReporteCleanupView.as_view(), name='reportes-cleanup'),
    
    # Endpoints de calibración
    path('calibration/status/', views.CalibrationStatusView.as_view(), name='calibration-status'),
    path('calibration/', views.CalibrationView.as_view(), name='calibration'),
    path('scan/measure/calibrated/', views.CalibratedScanMeasureView.as_view(), name='scan-measure-calibrated'),
    
    # Endpoints de gestión de emails
    # path('emails/status/', views.EmailStatusView.as_view(), name='email-status'),
    # path('emails/test/', views.SendTestEmailView.as_view(), name='email-test'),
    # path('emails/bulk/', views.SendBulkNotificationView.as_view(), name='email-bulk'),
    # path('emails/template-preview/', views.EmailTemplatePreviewView.as_view(), name='email-template-preview'),
    # path('emails/logs/', views.EmailLogsView.as_view(), name='email-logs'),
    
    # Endpoints de entrenamiento incremental
    path('incremental/status/', views.IncrementalTrainingStatusView.as_view(), name='incremental-status'),
    path('incremental/train/', views.IncrementalTrainingView.as_view(), name='incremental-train'),
    path('incremental/upload/', views.IncrementalDataUploadView.as_view(), name='incremental-upload'),
    path('incremental/models/', views.IncrementalModelVersionsView.as_view(), name='incremental-models'),
    path('incremental/data/', views.IncrementalDataVersionsView.as_view(), name='incremental-data'),
    
    # Endpoints de métricas de modelos
    path('model-metrics/', views.ModelMetricsListView.as_view(), name='model-metrics-list'),
    path('model-metrics/create/', views.ModelMetricsCreateView.as_view(), name='model-metrics-create'),
    path('model-metrics/<int:metrics_id>/', views.ModelMetricsDetailView.as_view(), name='model-metrics-detail'),
    path('model-metrics/<int:metrics_id>/update/', views.ModelMetricsUpdateView.as_view(), name='model-metrics-update'),
    path('model-metrics/<int:metrics_id>/delete/', views.ModelMetricsDeleteView.as_view(), name='model-metrics-delete'),
    path('model-metrics/stats/', views.ModelMetricsStatsView.as_view(), name='model-metrics-stats'),
    path('model-metrics/trend/', views.ModelPerformanceTrendView.as_view(), name='model-metrics-trend'),
    path('model-metrics/compare/', views.ModelComparisonView.as_view(), name='model-metrics-compare'),
    path('model-metrics/best/', views.BestModelsView.as_view(), name='model-metrics-best'),
    path('model-metrics/production/', views.ProductionModelsView.as_view(), name='model-metrics-production'),
    
    # Endpoints de análisis batch
    path('analysis/batch/', views.BatchAnalysisView.as_view(), name='batch-analysis'),
    
    # Endpoints de configuración del sistema
    path('config/', views.SystemSettingsView.as_view(), name='system-settings'),
    path('config/general/', views.SystemGeneralConfigView.as_view(), name='system-general-config'),
    path('config/security/', views.SystemSecurityConfigView.as_view(), name='system-security-config'),
    path('config/ml/', views.SystemMLConfigView.as_view(), name='system-ml-config'),
    path('config/system/', views.SystemInfoView.as_view(), name='system-info'),
]
