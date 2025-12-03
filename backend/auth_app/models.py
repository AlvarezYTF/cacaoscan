"""
Modelos de autenticación para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import logging
import secrets

logger = logging.getLogger("cacaoscan.auth")


class EmailVerificationToken(models.Model):
    """
    Modelo para tokens de verificación de email.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_email_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Configuración de expiración (24 horas por defecto)
    EXPIRATION_HOURS = 24
    
    # Alias para compatibilidad con tests
    @property
    def created(self):
        """Alias para created_at (compatibilidad con tests)."""
        return self.created_at
    
    @created.setter
    def created(self, value):
        """Setter para created (compatibilidad con tests)."""
        self.created_at = value
    
    class Meta:
        verbose_name = 'Token de Verificación de Email'
        verbose_name_plural = 'Tokens de Verificación de Email'
        ordering = ['-created_at']
    
    def __str__(self):
        """Representación string del token."""
        return f"Token para {self.user.email}"
    
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
    
    @expires_at.setter
    def expires_at(self, value):
        """Setter para expires_at (compatibilidad con tests)."""
        # No hacemos nada, es una propiedad calculada
        pass
    
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_profile')
    
    # Información de contacto
    phone_number = models.CharField(max_length=20, blank=True, default="")
    
    # Información geográfica
    region = models.CharField(max_length=100, blank=True, default="")
    municipality = models.CharField(max_length=100, blank=True, default="")
    
    # Información de la finca
    farm_name = models.CharField(max_length=200, blank=True, default="")
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
            # Usar auth_email_token como relación estándar
            if hasattr(self.user, 'auth_email_token'):
                return self.user.auth_email_token.is_verified
            return False
        except (AttributeError, KeyError, ValueError):
            return False


class PendingEmailVerification(models.Model):
    """
    Modelo para verificación pendiente de email con código OTP.
    Guarda temporalmente los datos del usuario hasta que verifique el código OTP.
    """
    email = models.EmailField(unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(auto_now=True)
    temp_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Verificación Pendiente de Email'
        verbose_name_plural = 'Verificaciones Pendientes de Email'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'otp_code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"OTP para {self.email} - {self.otp_code}"

    def is_expired(self):
        """Verificar si el código OTP ha expirado (10 minutos)."""
        return (timezone.now() - self.created_at).total_seconds() > 600

    @staticmethod
    def generate_code():
        """Generar un código OTP aleatorio de 6 dígitos."""
        # Use the `secrets` module for cryptographically secure random numbers
        # to generate OTP codes. This avoids predictable or weak PRNGs.
        return str(secrets.randbelow(900000) + 100000)


