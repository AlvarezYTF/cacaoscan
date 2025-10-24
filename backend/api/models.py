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