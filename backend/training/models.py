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
    model_path = models.CharField(max_length=500, blank=True, default='', help_text="Ruta del modelo entrenado")
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
        db_table = 'api_modelmetrics'  # Mantener nombre de tabla para compatibilidad
        verbose_name = 'Métricas de Modelo'
        verbose_name_plural = 'Métricas de Modelos'
        ordering = ['-created_at']
    
    @classmethod
    def get_performance_trend(cls, model_name: str, target: str, metric_type: str = 'validation'):
        """
        Get performance trend data for a specific model.
        
        Args:
            model_name: Name of the model
            target: Target variable
            metric_type: Type of metrics (training, validation, test, incremental)
            
        Returns:
            List of dictionaries with trend data, each containing:
            - created_at: datetime
            - r2_score: float
            - mae: float
            - rmse: float
            - mse: float
        """
        queryset = cls.objects.filter(
            model_name=model_name,
            target=target,
            metric_type=metric_type
        ).order_by('created_at')
        
        trend_data = []
        for metric in queryset:
            trend_data.append({
                'created_at': metric.created_at.isoformat() if metric.created_at else None,
                'r2_score': float(metric.r2_score),
                'mae': float(metric.mae),
                'rmse': float(metric.rmse),
                'mse': float(metric.mse),
            })
        
        return trend_data
    
    @property
    def accuracy_percentage(self):
        """Calculate accuracy percentage from r2_score."""
        return round(float(self.r2_score) * 100, 2) if self.r2_score else 0.0
    
    @property
    def training_time_formatted(self):
        """Format training time in human-readable format."""
        if not self.training_time_seconds:
            return "N/A"
        
        hours = self.training_time_seconds // 3600
        minutes = (self.training_time_seconds % 3600) // 60
        seconds = self.training_time_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @property
    def performance_summary(self):
        """Get performance summary."""
        return {
            'r2_score': round(float(self.r2_score), 4),
            'mae': round(float(self.mae), 4),
            'rmse': round(float(self.rmse), 4),
            'accuracy_percentage': self.accuracy_percentage
        }
    
    @property
    def dataset_summary(self):
        """Get dataset summary."""
        return {
            'total_size': self.dataset_size,
            'train_size': self.train_size,
            'validation_size': self.validation_size,
            'test_size': self.test_size,
            'train_percentage': round((self.train_size / self.dataset_size * 100), 2) if self.dataset_size > 0 else 0,
            'validation_percentage': round((self.validation_size / self.dataset_size * 100), 2) if self.dataset_size > 0 else 0,
            'test_percentage': round((self.test_size / self.dataset_size * 100), 2) if self.dataset_size > 0 else 0
        }
    
    @property
    def model_summary(self):
        """Get model summary."""
        return {
            'model_name': self.model_name,
            'model_type': self.get_model_type_display(),
            'target': self.get_target_display(),
            'version': self.version,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate
        }
    
    def get_comparison_with_previous(self):
        """
        Get comparison with previous version of the same model.
        
        Returns:
            Dictionary with comparison metrics or None if no previous version exists
        """
        try:
            # Find previous version of the same model
            previous = ModelMetrics.objects.filter(
                model_name=self.model_name,
                target=self.target,
                metric_type=self.metric_type,
                created_at__lt=self.created_at
            ).order_by('-created_at').first()
            
            if not previous:
                return None
            
            # Calculate improvements
            mae_improvement = ((previous.mae - self.mae) / previous.mae * 100) if previous.mae > 0 else 0
            rmse_improvement = ((previous.rmse - self.rmse) / previous.rmse * 100) if previous.rmse > 0 else 0
            r2_improvement = ((self.r2_score - previous.r2_score) / abs(previous.r2_score) * 100) if previous.r2_score != 0 else 0
            
            return {
                'previous_version': previous.version,
                'previous_r2_score': float(previous.r2_score),
                'current_r2_score': float(self.r2_score),
                'r2_improvement': round(r2_improvement, 2),
                'mae_improvement': round(mae_improvement, 2),
                'rmse_improvement': round(rmse_improvement, 2),
                'improvement': round(r2_improvement, 2),
                'is_better': self.r2_score > previous.r2_score
            }
        except Exception:
            return None
    
    def get_comparison_with_previous(self):
        """
        Get comparison with previous version of the same model.
        
        Returns:
            Dictionary with comparison data or empty dict if no previous version exists.
        """
        try:
            previous = ModelMetrics.objects.filter(
                model_name=self.model_name,
                target=self.target,
                metric_type=self.metric_type,
                created_at__lt=self.created_at
            ).order_by('-created_at').first()
            
            if not previous:
                return {
                    'has_previous': False,
                    'message': 'No previous version found'
                }
            
            return {
                'has_previous': True,
                'previous_version': previous.version,
                'previous_r2_score': float(previous.r2_score),
                'current_r2_score': float(self.r2_score),
                'r2_improvement': float(self.r2_score - previous.r2_score),
                'previous_mae': float(previous.mae),
                'current_mae': float(self.mae),
                'mae_improvement': float(previous.mae - self.mae),
                'previous_rmse': float(previous.rmse),
                'current_rmse': float(self.rmse),
                'rmse_improvement': float(previous.rmse - self.rmse),
                'is_better': self.r2_score > previous.r2_score
            }
        except Exception:
            return {
                'has_previous': False,
                'message': 'Error comparing with previous version'
            }