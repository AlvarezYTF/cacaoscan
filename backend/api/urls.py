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
    path('images/stats/', views.ImagesStatsView.as_view(), name='images-stats'),
]
