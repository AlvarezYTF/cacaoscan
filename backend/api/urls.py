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
    # path('auth/refresh/', views.RefreshTokenView.as_view(), name='auth-refresh'),  # No usado con Token Auth
    
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
]
