"""
Modelos de la API - Importar desde apps modulares.

Este archivo actúa como un punto de acceso para evitar conflictos de importación.
En lugar de definir modelos aquí, importamos desde las apps modulares correspondientes.
"""

# Importar modelos desde apps modulares para evitar duplicación
try:
    from auth_app.models import EmailVerificationToken, UserProfile
except ImportError:
    pass

try:
    from fincas_app.models import Finca, Lote
except ImportError:
    pass

try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    pass

try:
    from notifications.models import Notification
except ImportError:
    pass

try:
    from audit.models import ActivityLog
except ImportError:
    pass

try:
    from training.models import TrainingJob
except ImportError:
    pass

try:
    from core.models import SystemSettings
except ImportError:
    pass

# Mantener solo modelos únicos de API (si los hay)
from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


# Modelos únicos de la app 'api' que no están en otras apps
class LoginHistory(models.Model):
    """
    Modelo para registrar el historial de inicios de sesión.
    """
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_history',
        help_text="Usuario que inició sesión"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Dirección IP del usuario"
    )
    user_agent = models.TextField(
        help_text="User Agent del navegador"
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del inicio de sesión"
    )
    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora del cierre de sesión"
    )
    session_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Duración de la sesión"
    )
    success = models.BooleanField(
        default=True,
        help_text="Indica si el inicio de sesión fue exitoso"
    )
    failure_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Razón del fallo si no fue exitoso"
    )
    
    class Meta:
        verbose_name = 'Historial de Login'
        verbose_name_plural = 'Historial de Logins'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['usuario', '-login_time']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['login_time']),
            models.Index(fields=['success']),
        ]
    
    def __str__(self):
        status = "Exitoso" if self.success else "Fallido"
        return f"{self.usuario.username} - {status} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"


class ReporteGenerado(models.Model):
    """
    Modelo para gestionar reportes generados del sistema.
    """
    TIPO_REPORTE_CHOICES = [
        ('calidad', 'Reporte de Calidad'),
        ('defectos', 'Reporte de Defectos'),
        ('rendimiento', 'Reporte de Rendimiento'),
        ('finca', 'Reporte de Finca'),
        ('lote', 'Reporte de Lote'),
        ('usuario', 'Reporte de Usuario'),
        ('auditoria', 'Reporte de Auditoría'),
        ('personalizado', 'Reporte Personalizado'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    ESTADO_CHOICES = [
        ('generando', 'Generando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('expirado', 'Expirado'),
    ]
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reportes_generados',
        help_text="Usuario que solicitó el reporte"
    )
    tipo_reporte = models.CharField(max_length=20, choices=TIPO_REPORTE_CHOICES)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='generando')
    
    archivo = models.FileField(upload_to='reportes/%Y/%m/%d/', null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255, null=True, blank=True)
    tamaño_archivo = models.PositiveIntegerField(null=True, blank=True)
    
    parametros = models.JSONField(default=dict, blank=True)
    filtros_aplicados = models.JSONField(default=dict, blank=True)
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    tiempo_generacion = models.DurationField(null=True, blank=True)
    
    mensaje_error = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_solicitud']


class ModelMetrics(models.Model):
    """
    Modelo para almacenar métricas detalladas de modelos de machine learning.
    """
    MODEL_TYPE_CHOICES = [
        ('regression', 'Modelo de Regresión'),
        ('classification', 'Modelo de Clasificación'),
        ('segmentation', 'Modelo de Segmentación'),
        ('incremental', 'Modelo Incremental'),
    ]
    
    TARGET_CHOICES = [
        ('alto', 'Altura'),
        ('ancho', 'Ancho'),
        ('grosor', 'Grosor'),
        ('peso', 'Peso'),
        ('calidad', 'Calidad'),
        ('variedad', 'Variedad'),
    ]
    
    METRIC_TYPE_CHOICES = [
        ('training', 'Métricas de Entrenamiento'),
        ('validation', 'Métricas de Validación'),
        ('test', 'Métricas de Prueba'),
        ('incremental', 'Métricas Incrementales'),
    ]
    
    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPE_CHOICES)
    target = models.CharField(max_length=20, choices=TARGET_CHOICES)
    version = models.CharField(max_length=20)
    
    # training_job = models.ForeignKey('TrainingJob', ...) # Deshabilitado temporalmente
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='model_metrics')
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    
    mae = models.FloatField()
    mse = models.FloatField()
    rmse = models.FloatField()
    r2_score = models.FloatField()
    mape = models.FloatField(null=True, blank=True)
    
    additional_metrics = models.JSONField(default=dict)
    
    dataset_size = models.PositiveIntegerField()
    train_size = models.PositiveIntegerField()
    validation_size = models.PositiveIntegerField()
    test_size = models.PositiveIntegerField()
    
    epochs = models.PositiveIntegerField()
    batch_size = models.PositiveIntegerField()
    learning_rate = models.FloatField()
    
    model_params = models.JSONField(default=dict)
    
    training_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    inference_time_ms = models.FloatField(null=True, blank=True)
    
    stability_score = models.FloatField(null=True, blank=True)
    knowledge_retention = models.FloatField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    is_best_model = models.BooleanField(default=False)
    is_production_model = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Métricas de Modelo'
        verbose_name_plural = 'Métricas de Modelos'
        ordering = ['-created_at']
