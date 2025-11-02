"""
Modelo para gestionar trabajos de entrenamiento de modelos ML.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TrainingJob(models.Model):
    """
    Modelo para gestionar trabajos de entrenamiento de modelos ML.
    """
    JOB_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutándose'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('regression', 'Modelo de Regresión'),
        ('vision', 'Modelo de Visión (YOLOv8)'),
        ('incremental', 'Entrenamiento Incremental'),
    ]
    
    # Información básica
    job_id = models.CharField(max_length=100, unique=True, help_text="ID único del trabajo")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_jobs')
    
    # Configuración del entrenamiento
    model_name = models.CharField(max_length=100, help_text="Nombre del modelo a entrenar")
    dataset_size = models.PositiveIntegerField(help_text="Número de imágenes en el dataset")
    epochs = models.PositiveIntegerField(default=100)
    batch_size = models.PositiveIntegerField(default=16)
    learning_rate = models.FloatField(default=0.001)
    
    # Parámetros específicos
    config_params = models.JSONField(default=dict, help_text="Parámetros adicionales de configuración")
    
    # Resultados
    metrics = models.JSONField(default=dict, help_text="Métricas de entrenamiento")
    model_path = models.CharField(max_length=500, blank=True, null=True, help_text="Ruta del modelo entrenado")
    logs = models.TextField(blank=True, help_text="Logs del entrenamiento")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Información adicional
    error_message = models.TextField(blank=True, help_text="Mensaje de error si falló")
    progress_percentage = models.FloatField(default=0.0, help_text="Porcentaje de progreso")
    
    class Meta:
        verbose_name = 'Trabajo de Entrenamiento'
        verbose_name_plural = 'Trabajos de Entrenamiento'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['job_type']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"Training Job {self.job_id} - {self.get_job_type_display()} ({self.status})"
    
    @property
    def duration(self):
        """Duración del entrenamiento en segundos."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (timezone.now() - self.started_at).total_seconds()
        return None
    
    @property
    def duration_formatted(self):
        """Duración formateada."""
        duration = self.duration
        if duration is None:
            return "N/A"
        
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @property
    def is_active(self):
        """Verificar si el trabajo está activo."""
        return self.status in ['pending', 'running']
    
    def update_progress(self, percentage, logs=None):
        """Actualizar progreso del trabajo."""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        if logs:
            self.logs += f"\n[{timezone.now().isoformat()}] {logs}"
        self.save(update_fields=['progress_percentage', 'logs'])
    
    def mark_started(self):
        """Marcar trabajo como iniciado."""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_completed(self, metrics=None, model_path=None):
        """Marcar trabajo como completado."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100.0
        if metrics:
            self.metrics = metrics
        if model_path:
            self.model_path = model_path
        self.save(update_fields=['status', 'completed_at', 'progress_percentage', 'metrics', 'model_path'])
    
    def mark_failed(self, error_message):
        """Marcar trabajo como fallido."""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=['status', 'completed_at', 'error_message'])
    
    def mark_cancelled(self):
        """Marcar trabajo como cancelado."""
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
