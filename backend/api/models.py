"""
Modelos para verificación de email y tokens con expiración en CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token
import uuid


class EmailVerificationToken(models.Model):
    """
    Modelo para tokens de verificación de email.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Configuración de expiración (24 horas por defecto)
    EXPIRATION_HOURS = 24
    
    class Meta:
        verbose_name = 'Token de Verificación de Email'
        verbose_name_plural = 'Tokens de Verificación de Email'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Token para {self.user.email} - {'Verificado' if self.is_verified else 'Pendiente'}"
    
    @property
    def is_expired(self):
        """Verificar si el token ha expirado."""
        if self.is_verified:
            return False
        
        expiration_time = self.created_at + timezone.timedelta(hours=self.EXPIRATION_HOURS)
        return timezone.now() > expiration_time
    
    @property
    def expires_at(self):
        """Obtener fecha de expiración del token."""
        return self.created_at + timezone.timedelta(hours=self.EXPIRATION_HOURS)
    
    def verify(self):
        """Marcar el token como verificado."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
        
        # Marcar el usuario como activo si no lo estaba
        if not self.user.is_active:
            self.user.is_active = True
            self.user.save()
    
    @classmethod
    def create_for_user(cls, user):
        """Crear un nuevo token de verificación para un usuario."""
        # Eliminar token existente si existe
        cls.objects.filter(user=user).delete()
        
        # Crear nuevo token
        return cls.objects.create(user=user)
    
    @classmethod
    def get_valid_token(cls, token_uuid):
        """Obtener un token válido por UUID."""
        try:
            token_obj = cls.objects.get(token=token_uuid)
            if token_obj.is_expired:
                return None
            return token_obj
        except cls.DoesNotExist:
            return None


class ExpiringToken(Token):
    """
    Token con expiración personalizado para CacaoScan.
    Extiende el Token de DRF para agregar funcionalidad de expiración.
    """
    # Duración del token en horas (24 horas por defecto)
    EXPIRATION_HOURS = 24
    
    class Meta:
        proxy = True
        verbose_name = 'Token con Expiración'
        verbose_name_plural = 'Tokens con Expiración'
    
    @property
    def is_expired(self):
        """Verificar si el token ha expirado."""
        expiration_time = self.created + timezone.timedelta(hours=self.EXPIRATION_HOURS)
        return timezone.now() > expiration_time
    
    @property
    def expires_at(self):
        """Obtener fecha de expiración del token."""
        return self.created + timezone.timedelta(hours=self.EXPIRATION_HOURS)
    
    @classmethod
    def get_valid_token(cls, key):
        """Obtener un token válido por clave."""
        try:
            token = cls.objects.get(key=key)
            if token.is_expired:
                token.delete()  # Eliminar token expirado
                return None
            return token
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def create_for_user(cls, user):
        """Crear un nuevo token para un usuario."""
        # Eliminar tokens existentes del usuario
        cls.objects.filter(user=user).delete()
        
        # Crear nuevo token
        return cls.objects.create(user=user)
    
    def save(self, *args, **kwargs):
        """Guardar token con timestamp de creación."""
        if not self.pk:
            self.created = timezone.now()
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Perfil extendido del usuario con información específica de agricultores.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Información de contacto
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Información geográfica
    region = models.CharField(max_length=100, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)
    
    # Información de la finca
    farm_name = models.CharField(max_length=200, blank=True, null=True)
    years_experience = models.PositiveIntegerField(blank=True, null=True)
    farm_size_hectares = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Preferencias del usuario
    preferred_language = models.CharField(max_length=10, default='es', choices=[
        ('es', 'Español'),
        ('en', 'English'),
    ])
    email_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name(self):
        """Obtener nombre completo del usuario."""
        return self.user.get_full_name() or self.user.username
    
    @property
    def role(self):
        """Obtener rol del usuario desde el username o grupos."""
        # Por ahora, determinar rol basado en grupos o username
        if self.user.is_superuser:
            return 'admin'
        elif self.user.groups.filter(name='analyst').exists():
            return 'analyst'
        else:
            return 'farmer'
    
    @property
    def is_verified(self):
        """Verificar si el usuario está verificado."""
        try:
            return self.user.email_verification_token.is_verified
        except:
            return False


class CacaoImage(models.Model):
    """
    Modelo para almacenar imágenes de granos de cacao procesadas.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cacao_images')
    
    # Archivo de imagen
    image = models.ImageField(upload_to='cacao_images/processed/%Y/%m/%d/')
    
    # Metadatos de procesamiento
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    # Metadatos del grano/finca
    finca = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    lote_id = models.CharField(max_length=50, blank=True, null=True)
    variedad = models.CharField(max_length=100, blank=True, null=True)
    fecha_cosecha = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    # Información técnica del archivo
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Imagen de Cacao'
        verbose_name_plural = 'Imágenes de Cacao'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['processed']),
            models.Index(fields=['region', 'finca']),
        ]
    
    def __str__(self):
        return f"Imagen {self.id} - {self.user.username} ({self.uploaded_at.strftime('%Y-%m-%d')})"
    
    @property
    def file_size_mb(self):
        """Obtener tamaño del archivo en MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    @property
    def has_prediction(self):
        """Verificar si tiene predicción asociada."""
        return hasattr(self, 'prediction') and self.prediction is not None


class CacaoPrediction(models.Model):
    """
    Modelo para almacenar resultados de predicciones ML de granos de cacao.
    """
    image = models.OneToOneField(CacaoImage, on_delete=models.CASCADE, related_name='prediction')
    
    # Predicciones de dimensiones (en mm)
    alto_mm = models.DecimalField(max_digits=8, decimal_places=2)
    ancho_mm = models.DecimalField(max_digits=8, decimal_places=2)
    grosor_mm = models.DecimalField(max_digits=8, decimal_places=2)
    peso_g = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Scores de confianza (0.0 a 1.0)
    confidence_alto = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_ancho = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_grosor = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    confidence_peso = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    
    # Metadatos de procesamiento
    processing_time_ms = models.PositiveIntegerField(help_text="Tiempo de procesamiento en milisegundos")
    crop_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL del crop procesado")
    
    # Información técnica del modelo
    model_version = models.CharField(max_length=50, default='v1.0')
    device_used = models.CharField(max_length=20, default='cpu', choices=[
        ('cpu', 'CPU'),
        ('cuda', 'GPU CUDA'),
        ('mps', 'Apple Silicon'),
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Predicción de Cacao'
        verbose_name_plural = 'Predicciones de Cacao'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['image']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['model_version']),
        ]
    
    def __str__(self):
        return f"Predicción {self.id} - {self.image.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def average_confidence(self):
        """Calcular confianza promedio."""
        confidences = [
            float(self.confidence_alto),
            float(self.confidence_ancho),
            float(self.confidence_grosor),
            float(self.confidence_peso)
        ]
        return round(sum(confidences) / len(confidences), 3)
    
    @property
    def volume_cm3(self):
        """Calcular volumen aproximado en cm³."""
        # Volumen aproximado como elipsoide: (4/3) * π * a * b * c
        import math
        a = float(self.alto_mm) / 10  # convertir a cm
        b = float(self.ancho_mm) / 10
        c = float(self.grosor_mm) / 10
        volume = (4/3) * math.pi * a * b * c
        return round(volume, 3)
    
    @property
    def density_g_cm3(self):
        """Calcular densidad aproximada en g/cm³."""
        if self.volume_cm3 > 0:
            density = float(self.peso_g) / self.volume_cm3
            return round(density, 3)
        return None


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