"""
Modelos para verificación de email y tokens con expiración en CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token
import uuid
import logging
from datetime import timedelta

logger = logging.getLogger("cacaoscan.api")


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
    finca = models.CharField(max_length=200, blank=True, null=True)  # Mantener para compatibilidad
    region = models.CharField(max_length=100, blank=True, null=True)
    lote = models.ForeignKey(
        'Lote', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cacao_images',
        help_text="Lote al que pertenece esta imagen"
    )
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


class Finca(models.Model):
    """
    Modelo para gestionar fincas de cacao.
    """
    nombre = models.CharField(max_length=200, help_text="Nombre de la finca")
    ubicacion = models.CharField(max_length=300, help_text="Dirección o ubicación de la finca")
    municipio = models.CharField(max_length=100, help_text="Municipio donde se encuentra la finca")
    departamento = models.CharField(max_length=100, help_text="Departamento donde se encuentra la finca")
    hectareas = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Área total de la finca en hectáreas"
    )
    agricultor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='fincas',
        help_text="Agricultor propietario de la finca"
    )
    
    # Información adicional
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional de la finca")
    coordenadas_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Latitud GPS de la finca"
    )
    coordenadas_lng = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Longitud GPS de la finca"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, help_text="Fecha de registro de la finca")
    activa = models.BooleanField(default=True, help_text="Indica si la finca está activa")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Finca'
        verbose_name_plural = 'Fincas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agricultor', '-created_at']),
            models.Index(fields=['agricultor_id']),  # Índice específico para búsquedas por agricultor
            models.Index(fields=['municipio', 'departamento']),
            models.Index(fields=['activa']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(hectareas__gt=0),
                name='finca_hectareas_positivas'
            ),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.municipio}, {self.departamento}"
    
    @property
    def total_lotes(self):
        """Obtener número total de lotes en la finca."""
        return self.lotes.count()
    
    @property
    def lotes_activos(self):
        """Obtener número de lotes activos en la finca."""
        return self.lotes.filter(activo=True).count()
    
    @property
    def total_analisis(self):
        """Obtener número total de análisis realizados en la finca."""
        from django.db.models import Count
        return self.lotes.aggregate(
            total=Count('cacao_images__prediction', distinct=True)
        )['total'] or 0
    
    @property
    def calidad_promedio(self):
        """Calcular calidad promedio de la finca basada en análisis."""
        from django.db.models import Avg
        try:
            avg_confidence = self.lotes.aggregate(
                avg_quality=Avg('cacao_images__prediction__average_confidence')
            )['avg_quality']
            return round(float(avg_confidence or 0) * 100, 2)
        except Exception:
            # Si hay error calculando el promedio (relación no existe, etc.)
            return 0.0
    
    @property
    def ubicacion_completa(self):
        """Obtener ubicación completa formateada."""
        return f"{self.ubicacion}, {self.municipio}, {self.departamento}"
    
    def get_estadisticas(self):
        """Obtener estadísticas completas de la finca."""
        return {
            'total_lotes': self.total_lotes,
            'lotes_activos': self.lotes_activos,
            'total_analisis': self.total_analisis,
            'calidad_promedio': self.calidad_promedio,
            'hectareas': float(self.hectareas),
            'fecha_registro': self.fecha_registro.strftime('%d/%m/%Y'),
            'activa': self.activa
        }


class Notification(models.Model):
    """
    Modelo para gestionar notificaciones del sistema.
    """
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito'),
        ('defect_alert', 'Alerta de Defecto'),
        ('report_ready', 'Reporte Listo'),
        ('training_complete', 'Entrenamiento Completo'),
        ('welcome', 'Bienvenida'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        help_text="Usuario destinatario de la notificación"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        help_text="Tipo de notificación"
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Título de la notificación"
    )
    mensaje = models.TextField(
        help_text="Mensaje detallado de la notificación"
    )
    leida = models.BooleanField(
        default=False,
        help_text="Indica si la notificación ha sido leída"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la notificación"
    )
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se marcó como leída"
    )
    datos_extra = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales en formato JSON"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['user', '-fecha_creacion']),
            models.Index(fields=['leida']),
            models.Index(fields=['tipo']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.user.username} ({'Leída' if self.leida else 'No leída'})"
    
    def mark_as_read(self):
        """Marcar notificación como leída."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Marcar todas las notificaciones de un usuario como leídas."""
        cls.objects.filter(user=user, leida=False).update(
            leida=True,
            fecha_lectura=timezone.now()
        )
    
    @classmethod
    def get_unread_count(cls, user):
        """Obtener número de notificaciones no leídas de un usuario."""
        return cls.objects.filter(user=user, leida=False).count()
    
    @classmethod
    def create_notification(cls, user, tipo, titulo, mensaje, datos_extra=None):
        """Crear una nueva notificación."""
        return cls.objects.create(
            user=user,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            datos_extra=datos_extra or {}
        )
    
    @property
    def tiempo_transcurrido(self):
        """Obtener tiempo transcurrido desde la creación."""
        delta = timezone.now() - self.fecha_creacion
        
        if delta.days > 0:
            return f"{delta.days} día{'s' if delta.days > 1 else ''}"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hora{'s' if hours > 1 else ''}"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "Hace un momento"


class ActivityLog(models.Model):
    """
    Modelo para registrar logs de actividad del sistema.
    """
    ACCION_CHOICES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('create', 'Creación'),
        ('update', 'Actualización'),
        ('delete', 'Eliminación'),
        ('view', 'Visualización'),
        ('download', 'Descarga'),
        ('upload', 'Subida'),
        ('analysis', 'Análisis'),
        ('training', 'Entrenamiento'),
        ('report', 'Reporte'),
        ('error', 'Error'),
    ]
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs',
        help_text="Usuario que realizó la acción"
    )
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        help_text="Tipo de acción realizada"
    )
    modelo = models.CharField(
        max_length=50,
        help_text="Modelo afectado (ej: CacaoImage, Finca)"
    )
    objeto_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID del objeto afectado"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada de la acción"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP del usuario"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User Agent del navegador"
    )
    datos_antes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Estado del objeto antes de la acción"
    )
    datos_despues = models.JSONField(
        default=dict,
        blank=True,
        help_text="Estado del objeto después de la acción"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la acción"
    )
    
    class Meta:
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['accion', '-timestamp']),
            models.Index(fields=['modelo', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        usuario_name = self.usuario.username if self.usuario else 'Usuario Anónimo'
        return f"{usuario_name} - {self.get_accion_display()} - {self.modelo} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
    
    @classmethod
    def log_activity(cls, usuario, accion, modelo, descripcion, objeto_id=None, 
                     ip_address=None, user_agent=None, datos_antes=None, datos_despues=None):
        """
        Crear un log de actividad.
        
        Args:
            usuario: Usuario que realizó la acción
            accion: Tipo de acción
            modelo: Modelo afectado
            descripcion: Descripción de la acción
            objeto_id: ID del objeto afectado
            ip_address: Dirección IP
            user_agent: User Agent del navegador
            datos_antes: Estado antes de la acción
            datos_despues: Estado después de la acción
        """
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=modelo,
            objeto_id=objeto_id,
            descripcion=descripcion,
            ip_address=ip_address,
            user_agent=user_agent,
            datos_antes=datos_antes or {},
            datos_despues=datos_despues or {}
        )


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
    
    def calculate_session_duration(self):
        """Calcular duración de la sesión."""
        if self.logout_time:
            self.session_duration = self.logout_time - self.login_time
            self.save(update_fields=['session_duration'])
    
    @classmethod
    def log_login(cls, usuario, ip_address, user_agent, success=True, failure_reason=None):
        """
        Registrar un inicio de sesión.
        
        Args:
            usuario: Usuario que inició sesión
            ip_address: Dirección IP
            user_agent: User Agent del navegador
            success: Si el login fue exitoso
            failure_reason: Razón del fallo si no fue exitoso
        """
        return cls.objects.create(
            usuario=usuario,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
    
    @classmethod
    def log_logout(cls, usuario, ip_address):
        """
        Registrar un cierre de sesión.
        
        Args:
            usuario: Usuario que cerró sesión
            ip_address: Dirección IP
        """
        try:
            # Buscar la sesión activa más reciente
            login_record = cls.objects.filter(
                usuario=usuario,
                ip_address=ip_address,
                logout_time__isnull=True,
                success=True
            ).order_by('-login_time').first()
            
            if login_record:
                login_record.logout_time = timezone.now()
                login_record.calculate_session_duration()
                
        except Exception as e:
            logger.error(f"Error registrando logout: {e}")


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
    tipo_reporte = models.CharField(
        max_length=20,
        choices=TIPO_REPORTE_CHOICES,
        help_text="Tipo de reporte generado"
    )
    formato = models.CharField(
        max_length=10,
        choices=FORMATO_CHOICES,
        help_text="Formato del reporte"
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Título del reporte"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción del reporte"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='generando',
        help_text="Estado actual del reporte"
    )
    
    # Archivo generado
    archivo = models.FileField(
        upload_to='reportes/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Archivo del reporte generado"
    )
    nombre_archivo = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Nombre del archivo generado"
    )
    tamaño_archivo = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Tamaño del archivo en bytes"
    )
    
    # Parámetros del reporte
    parametros = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parámetros utilizados para generar el reporte"
    )
    filtros_aplicados = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtros aplicados al generar el reporte"
    )
    
    # Metadatos
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de solicitud del reporte"
    )
    fecha_generacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de generación del reporte"
    )
    fecha_expiracion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de expiración del reporte"
    )
    tiempo_generacion = models.DurationField(
        null=True,
        blank=True,
        help_text="Tiempo que tardó en generarse"
    )
    
    # Información de error
    mensaje_error = models.TextField(
        null=True,
        blank=True,
        help_text="Mensaje de error si falló la generación"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['usuario', '-fecha_solicitud']),
            models.Index(fields=['tipo_reporte', '-fecha_solicitud']),
            models.Index(fields=['estado']),
            models.Index(fields=['formato']),
            models.Index(fields=['fecha_solicitud']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_reporte_display()} ({self.get_estado_display()})"
    
    @property
    def archivo_url(self):
        """Obtener URL del archivo."""
        if self.archivo:
            return self.archivo.url
        return None
    
    @property
    def tamaño_archivo_mb(self):
        """Obtener tamaño del archivo en MB."""
        if self.tamaño_archivo:
            return round(self.tamaño_archivo / (1024 * 1024), 2)
        return None
    
    @property
    def tiempo_generacion_segundos(self):
        """Obtener tiempo de generación en segundos."""
        if self.tiempo_generacion:
            return self.tiempo_generacion.total_seconds()
        return None
    
    @property
    def esta_expirado(self):
        """Verificar si el reporte ha expirado."""
        if self.fecha_expiracion:
            return timezone.now() > self.fecha_expiracion
        return False
    
    def marcar_completado(self, archivo, tiempo_generacion=None):
        """Marcar reporte como completado."""
        self.estado = 'completado'
        self.archivo = archivo
        self.fecha_generacion = timezone.now()
        self.tiempo_generacion = tiempo_generacion
        
        # Establecer fecha de expiración (7 días por defecto)
        if not self.fecha_expiracion:
            self.fecha_expiracion = timezone.now() + timedelta(days=7)
        
        # Guardar información del archivo
        if archivo:
            self.nombre_archivo = archivo.name
            self.tamaño_archivo = archivo.size
        
        self.save()
    
    def marcar_fallido(self, mensaje_error):
        """Marcar reporte como fallido."""
        self.estado = 'fallido'
        self.mensaje_error = mensaje_error
        self.fecha_generacion = timezone.now()
        self.save()
    
    def marcar_expirado(self):
        """Marcar reporte como expirado."""
        self.estado = 'expirado'
        self.save()
    
    @classmethod
    def limpiar_expirados(cls):
        """Limpiar reportes expirados."""
        expirados = cls.objects.filter(
            fecha_expiracion__lt=timezone.now(),
            estado='completado'
        )
        
        count = 0
        for reporte in expirados:
            try:
                # Eliminar archivo físico
                if reporte.archivo:
                    reporte.archivo.delete(save=False)
                
                # Marcar como expirado
                reporte.marcar_expirado()
                count += 1
                
            except Exception as e:
                logger.error(f"Error limpiando reporte expirado {reporte.id}: {e}")
        
        logger.info(f"Se limpiaron {count} reportes expirados")
        return count
    
    @classmethod
    def generar_reporte(cls, usuario, tipo_reporte, formato, titulo, 
                       descripcion=None, parametros=None, filtros=None):
        """
        Crear un nuevo reporte para generar.
        
        Args:
            usuario: Usuario que solicita el reporte
            tipo_reporte: Tipo de reporte
            formato: Formato del reporte
            titulo: Título del reporte
            descripcion: Descripción del reporte
            parametros: Parámetros del reporte
            filtros: Filtros a aplicar
        """
        return cls.objects.create(
            usuario=usuario,
            tipo_reporte=tipo_reporte,
            formato=formato,
            titulo=titulo,
            descripcion=descripcion,
            parametros=parametros or {},
            filtros_aplicados=filtros or {}
        )


class Lote(models.Model):
    """
    Modelo para gestionar lotes de cacao dentro de fincas.
    """
    finca = models.ForeignKey(
        Finca, 
        on_delete=models.CASCADE, 
        related_name='lotes',
        help_text="Finca a la que pertenece el lote"
    )
    identificador = models.CharField(
        max_length=50, 
        help_text="Identificador único del lote dentro de la finca"
    )
    variedad = models.CharField(
        max_length=100, 
        help_text="Variedad de cacao del lote"
    )
    fecha_plantacion = models.DateField(
        help_text="Fecha de plantación del lote"
    )
    fecha_cosecha = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de cosecha del lote"
    )
    area_hectareas = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Área del lote en hectáreas"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('cosechado', 'Cosechado'),
            ('renovado', 'Renovado'),
        ],
        default='activo',
        help_text="Estado actual del lote"
    )
    
    # Información adicional
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional del lote")
    coordenadas_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Latitud GPS del lote"
    )
    coordenadas_lng = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Longitud GPS del lote"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, help_text="Fecha de registro del lote")
    activo = models.BooleanField(default=True, help_text="Indica si el lote está activo")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['finca', '-created_at']),
            models.Index(fields=['variedad']),
            models.Index(fields=['estado']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(area_hectareas__gt=0),
                name='lote_area_positiva'
            ),
            models.CheckConstraint(
                check=models.Q(fecha_cosecha__isnull=True) | models.Q(fecha_cosecha__gte=models.F('fecha_plantacion')),
                name='lote_fecha_cosecha_valida'
            ),
            models.UniqueConstraint(
                fields=['finca', 'identificador'],
                name='lote_identificador_unico_por_finca'
            ),
        ]
    
    def __str__(self):
        return f"{self.identificador} - {self.variedad} ({self.finca.nombre})"
    
    @property
    def total_analisis(self):
        """Obtener número total de análisis realizados en el lote."""
        return self.cacao_images.count()
    
    @property
    def analisis_procesados(self):
        """Obtener número de análisis procesados en el lote."""
        return self.cacao_images.filter(processed=True).count()
    
    @property
    def calidad_promedio(self):
        """Calcular calidad promedio del lote basada en análisis."""
        from django.db.models import Avg
        avg_confidence = self.cacao_images.aggregate(
            avg_quality=Avg('prediction__average_confidence')
        )['avg_quality']
        return round(float(avg_confidence or 0) * 100, 2)
    
    @property
    def edad_meses(self):
        """Calcular edad del lote en meses."""
        from datetime import date
        today = date.today()
        delta = today - self.fecha_plantacion
        return delta.days // 30
    
    @property
    def ubicacion_completa(self):
        """Obtener ubicación completa formateada."""
        return f"{self.finca.ubicacion}, {self.finca.municipio}, {self.finca.departamento}"
    
    def get_estadisticas(self):
        """Obtener estadísticas completas del lote."""
        return {
            'total_analisis': self.total_analisis,
            'analisis_procesados': self.analisis_procesados,
            'calidad_promedio': self.calidad_promedio,
            'area_hectareas': float(self.area_hectareas),
            'edad_meses': self.edad_meses,
            'estado': self.estado,
            'activo': self.activo,
            'fecha_plantacion': self.fecha_plantacion.strftime('%d/%m/%Y'),
            'fecha_cosecha': self.fecha_cosecha.strftime('%d/%m/%Y') if self.fecha_cosecha else None,
        }


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
    
    # Información básica del modelo
    model_name = models.CharField(max_length=100, help_text="Nombre del modelo")
    model_type = models.CharField(max_length=20, choices=MODEL_TYPE_CHOICES)
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, help_text="Variable objetivo")
    version = models.CharField(max_length=20, help_text="Versión del modelo")
    
    # Información del entrenamiento
    training_job = models.ForeignKey(
        TrainingJob, 
        on_delete=models.CASCADE, 
        related_name='model_metrics',
        null=True, 
        blank=True,
        help_text="Trabajo de entrenamiento asociado"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='model_metrics')
    
    # Tipo de métricas
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    
    # Métricas principales
    mae = models.FloatField(help_text="Mean Absolute Error")
    mse = models.FloatField(help_text="Mean Squared Error")
    rmse = models.FloatField(help_text="Root Mean Squared Error")
    r2_score = models.FloatField(help_text="R² Score")
    mape = models.FloatField(help_text="Mean Absolute Percentage Error", null=True, blank=True)
    
    # Métricas adicionales (almacenadas como JSON)
    additional_metrics = models.JSONField(
        default=dict, 
        help_text="Métricas adicionales específicas del modelo"
    )
    
    # Información del dataset
    dataset_size = models.PositiveIntegerField(help_text="Tamaño del dataset usado")
    train_size = models.PositiveIntegerField(help_text="Tamaño del conjunto de entrenamiento")
    validation_size = models.PositiveIntegerField(help_text="Tamaño del conjunto de validación")
    test_size = models.PositiveIntegerField(help_text="Tamaño del conjunto de prueba")
    
    # Configuración del modelo
    epochs = models.PositiveIntegerField(help_text="Número de épocas de entrenamiento")
    batch_size = models.PositiveIntegerField(help_text="Tamaño del batch")
    learning_rate = models.FloatField(help_text="Tasa de aprendizaje")
    
    # Parámetros específicos del modelo
    model_params = models.JSONField(
        default=dict, 
        help_text="Parámetros específicos del modelo"
    )
    
    # Información de rendimiento
    training_time_seconds = models.PositiveIntegerField(
        help_text="Tiempo de entrenamiento en segundos",
        null=True, 
        blank=True
    )
    inference_time_ms = models.FloatField(
        help_text="Tiempo de inferencia promedio en milisegundos",
        null=True, 
        blank=True
    )
    
    # Información de estabilidad (para modelos incrementales)
    stability_score = models.FloatField(
        help_text="Puntuación de estabilidad del modelo",
        null=True, 
        blank=True
    )
    knowledge_retention = models.FloatField(
        help_text="Porcentaje de retención de conocimiento",
        null=True, 
        blank=True
    )
    
    # Metadatos adicionales
    notes = models.TextField(blank=True, help_text="Notas adicionales sobre el modelo")
    is_best_model = models.BooleanField(default=False, help_text="Indica si es el mejor modelo")
    is_production_model = models.BooleanField(default=False, help_text="Indica si está en producción")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Métricas de Modelo'
        verbose_name_plural = 'Métricas de Modelos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'version']),
            models.Index(fields=['model_type', 'target']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['is_best_model']),
            models.Index(fields=['is_production_model']),
        ]
        unique_together = ['model_name', 'version', 'metric_type', 'target']
    
    def __str__(self):
        return f"{self.model_name} v{self.version} - {self.get_target_display()} ({self.get_metric_type_display()})"
    
    @property
    def accuracy_percentage(self):
        """Obtener precisión como porcentaje."""
        if self.r2_score is not None:
            return round(self.r2_score * 100, 2)
        return None
    
    @property
    def training_time_formatted(self):
        """Obtener tiempo de entrenamiento formateado."""
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
        """Obtener resumen de rendimiento."""
        return {
            'mae': round(self.mae, 4),
            'rmse': round(self.rmse, 4),
            'r2_score': round(self.r2_score, 4),
            'accuracy_percentage': self.accuracy_percentage,
            'training_time': self.training_time_formatted,
            'inference_time_ms': round(self.inference_time_ms, 2) if self.inference_time_ms else None,
        }
    
    @property
    def dataset_summary(self):
        """Obtener resumen del dataset."""
        return {
            'total_size': self.dataset_size,
            'train_size': self.train_size,
            'validation_size': self.validation_size,
            'test_size': self.test_size,
            'train_ratio': round(self.train_size / self.dataset_size, 3) if self.dataset_size > 0 else 0,
            'validation_ratio': round(self.validation_size / self.dataset_size, 3) if self.dataset_size > 0 else 0,
            'test_ratio': round(self.test_size / self.dataset_size, 3) if self.dataset_size > 0 else 0,
        }
    
    @property
    def model_summary(self):
        """Obtener resumen del modelo."""
        return {
            'name': self.model_name,
            'type': self.get_model_type_display(),
            'target': self.get_target_display(),
            'version': self.version,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'is_best': self.is_best_model,
            'is_production': self.is_production_model,
        }
    
    def get_comparison_with_previous(self):
        """Comparar con la versión anterior del mismo modelo."""
        previous = ModelMetrics.objects.filter(
            model_name=self.model_name,
            target=self.target,
            metric_type=self.metric_type,
            created_at__lt=self.created_at
        ).order_by('-created_at').first()
        
        if not previous:
            return None
        
        return {
            'previous_version': previous.version,
            'mae_change': round(self.mae - previous.mae, 4),
            'rmse_change': round(self.rmse - previous.rmse, 4),
            'r2_change': round(self.r2_score - previous.r2_score, 4),
            'improvement': self.r2_score > previous.r2_score,
        }
    
    def mark_as_best(self):
        """Marcar como el mejor modelo de su tipo."""
        # Desmarcar otros modelos del mismo tipo como mejores
        ModelMetrics.objects.filter(
            model_name=self.model_name,
            target=self.target,
            is_best_model=True
        ).exclude(id=self.id).update(is_best_model=False)
        
        # Marcar este modelo como el mejor
        self.is_best_model = True
        self.save(update_fields=['is_best_model'])
    
    def mark_as_production(self):
        """Marcar como modelo en producción."""
        # Desmarcar otros modelos del mismo tipo en producción
        ModelMetrics.objects.filter(
            model_name=self.model_name,
            target=self.target,
            is_production_model=True
        ).exclude(id=self.id).update(is_production_model=False)
        
        # Marcar este modelo como en producción
        self.is_production_model = True
        self.save(update_fields=['is_production_model'])
    
    @classmethod
    def get_best_models(cls):
        """Obtener todos los mejores modelos."""
        return cls.objects.filter(is_best_model=True).order_by('model_name', 'target')
    
    @classmethod
    def get_production_models(cls):
        """Obtener todos los modelos en producción."""
        return cls.objects.filter(is_production_model=True).order_by('model_name', 'target')
    
    @classmethod
    def get_model_history(cls, model_name, target=None):
        """Obtener historial de un modelo específico."""
        queryset = cls.objects.filter(model_name=model_name)
        if target:
            queryset = queryset.filter(target=target)
        return queryset.order_by('-created_at')
    
    @classmethod
    def get_performance_trend(cls, model_name, target, metric_type='validation'):
        """Obtener tendencia de rendimiento de un modelo."""
        metrics = cls.objects.filter(
            model_name=model_name,
            target=target,
            metric_type=metric_type
        ).order_by('created_at')
        
        return [
            {
                'version': m.version,
                'date': m.created_at.strftime('%Y-%m-%d'),
                'r2_score': m.r2_score,
                'mae': m.mae,
                'rmse': m.rmse,
            }
            for m in metrics
        ]


class SystemSettings(models.Model):
    """
    Modelo para almacenar la configuración del sistema.
    Solo debe haber un registro en esta tabla (singleton).
    """
    # Configuración General
    nombre_sistema = models.CharField(
        max_length=100,
        default='CacaoScan',
        help_text='Nombre del sistema'
    )
    email_contacto = models.EmailField(
        default='contacto@cacaoscan.com',
        help_text='Correo de contacto principal'
    )
    lema = models.CharField(
        max_length=200,
        default='La mejor plataforma para el control de calidad del cacao',
        help_text='Lema o descripción del sistema'
    )
    logo = models.ImageField(
        upload_to='system_settings/',
        null=True,
        blank=True,
        help_text='Logo del sistema'
    )
    
    # Configuración de Seguridad
    recaptcha_enabled = models.BooleanField(
        default=True,
        help_text='Activar reCAPTCHA'
    )
    session_timeout = models.IntegerField(
        default=60,
        help_text='Tiempo de sesión en minutos'
    )
    login_attempts = models.IntegerField(
        default=5,
        help_text='Número máximo de intentos de login'
    )
    two_factor_auth = models.BooleanField(
        default=False,
        help_text='Activar autenticación de dos factores'
    )
    
    # Configuración de Modelos ML
    active_model = models.CharField(
        max_length=50,
        default='yolov8',
        help_text='Modelo activo para predicciones'
    )
    last_training = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de último entrenamiento'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'Configuración de {self.nombre_sistema}'
    
    @classmethod
    def get_singleton(cls):
        """
        Obtener o crear la única instancia de configuración.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def save(self, *args, **kwargs):
        """Forzar que solo exista un registro."""
        self.pk = 1
        super().save(*args, **kwargs)