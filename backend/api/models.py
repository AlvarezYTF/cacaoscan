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
