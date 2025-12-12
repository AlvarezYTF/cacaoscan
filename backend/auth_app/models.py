"""
Modelos de autenticación para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from catalogos.models import Municipio
import uuid
import logging
import secrets

logger = logging.getLogger("cacaoscan.auth")


# Note: Compatibilidad con auth_email_token se manejará mediante actualización de código
# que usa este atributo, ya que agregar propiedades dinámicas al modelo User puede causar problemas


class EmailVerification(models.Model):
    """
    Modelo unificado para verificación de email.
    Soporta múltiples tipos de verificación: registro, reset de contraseña, cambio de email, OTP.
    """
    VERIFICATION_TYPE_REGISTRATION = 'registration'
    VERIFICATION_TYPE_PASSWORD_RESET = 'password_reset'
    VERIFICATION_TYPE_EMAIL_CHANGE = 'email_change'
    VERIFICATION_TYPE_OTP = 'otp'
    
    VERIFICATION_TYPE_CHOICES = [
        (VERIFICATION_TYPE_REGISTRATION, 'Registro'),
        (VERIFICATION_TYPE_PASSWORD_RESET, 'Recuperación de contraseña'),
        (VERIFICATION_TYPE_EMAIL_CHANGE, 'Cambio de email'),
        (VERIFICATION_TYPE_OTP, 'OTP'),
    ]
    
    email = models.EmailField(help_text="Email a verificar")
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPE_CHOICES,
        default=VERIFICATION_TYPE_REGISTRATION,
        help_text="Tipo de verificación"
    )
    
    # Token UUID para verificación por enlace (nullable para OTP)
    token = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True, help_text="Token UUID para verificación por enlace")
    
    # OTP code para verificación por código (nullable para tokens)
    otp_code = models.CharField(max_length=6, null=True, blank=True, help_text="Código OTP de 6 dígitos")
    
    # User solo para usuarios existentes (nullable para pre-registro)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verifications',
        null=True,
        blank=True,
        help_text="Usuario existente (solo para verificación de usuarios registrados)"
    )
    
    # Datos temporales para pre-registro o flujos que necesitan datos adicionales
    temp_data = models.JSONField(default=dict, blank=True, help_text="Datos temporales (ej: datos de pre-registro)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación")
    last_sent = models.DateTimeField(auto_now=True, help_text="Última vez que se envió el código/token")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="Fecha de verificación")
    is_verified = models.BooleanField(default=False, help_text="Indica si ya fue verificado")
    
    # Configuración de expiración
    EXPIRATION_HOURS_TOKEN = 24  # Para tokens UUID
    EXPIRATION_MINUTES_OTP = 10  # Para códigos OTP
    
    class Meta:
        verbose_name = 'Verificación de Email'
        verbose_name_plural = 'Verificaciones de Email'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'verification_type']),
            models.Index(fields=['token']),
            models.Index(fields=['email', 'otp_code']),
            models.Index(fields=['is_verified', 'created_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        """Representación string de la verificación."""
        if self.user:
            return f"Verificación {self.verification_type} para {self.user.email}"
        return f"Verificación {self.verification_type} para {self.email}"
    
    @property
    def is_expired(self):
        """Verificar si la verificación ha expirado."""
        if self.is_verified:
            return False
        
        if self.verification_type == self.VERIFICATION_TYPE_OTP:
            # OTP expira en 10 minutos
            expiration_time = self.created_at + timezone.timedelta(minutes=self.EXPIRATION_MINUTES_OTP)
        else:
            # Tokens expiran en 24 horas
            expiration_time = self.created_at + timezone.timedelta(hours=self.EXPIRATION_HOURS_TOKEN)
        
        return timezone.now() > expiration_time
    
    @property
    def expires_at(self):
        """Obtener fecha de expiración."""
        if self.verification_type == self.VERIFICATION_TYPE_OTP:
            return self.created_at + timezone.timedelta(minutes=self.EXPIRATION_MINUTES_OTP)
        return self.created_at + timezone.timedelta(hours=self.EXPIRATION_HOURS_TOKEN)
    
    def verify(self):
        """Marcar la verificación como completada."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
        
        # Marcar el usuario como activo si no lo estaba
        if self.user and not self.user.is_active:
            self.user.is_active = True
            self.user.save()
    
    @classmethod
    def create_for_user(cls, user, verification_type=VERIFICATION_TYPE_REGISTRATION):
        """
        Crear una nueva verificación para un usuario existente.
        
        Args:
            user: Usuario existente
            verification_type: Tipo de verificación
        
        Returns:
            EmailVerification instance
        """
        # Eliminar verificaciones existentes del mismo tipo para este usuario
        cls.objects.filter(user=user, verification_type=verification_type, is_verified=False).delete()
        
        # Crear nueva verificación
        return cls.objects.create(
            user=user,
            email=user.email,
            verification_type=verification_type,
            token=uuid.uuid4()
        )
    
    
    @classmethod
    def create_for_email(cls, email, verification_type=VERIFICATION_TYPE_REGISTRATION, temp_data=None):
        """
        Crear una nueva verificación para un email (pre-registro o OTP).
        
        Args:
            email: Email a verificar
            verification_type: Tipo de verificación
            temp_data: Datos temporales (opcional)
        
        Returns:
            EmailVerification instance
        """
        if temp_data is None:
            temp_data = {}
        
        if verification_type == cls.VERIFICATION_TYPE_OTP:
            # Para OTP, usar código en lugar de token
            otp_code = cls.generate_otp_code()
            return cls.objects.create(
                email=email,
                verification_type=verification_type,
                otp_code=otp_code,
                temp_data=temp_data
            )
        else:
            # Para otros tipos, usar token UUID
            return cls.objects.create(
                email=email,
                verification_type=verification_type,
                token=uuid.uuid4(),
                temp_data=temp_data
            )
    
    @classmethod
    def get_valid_token(cls, token_uuid):
        """
        Obtener una verificación válida por token UUID.
        
        Args:
            token_uuid: UUID del token
        
        Returns:
            EmailVerification instance o None
        """
        try:
            verification = cls.objects.get(token=token_uuid)
            if verification.is_expired or verification.is_verified:
                return None
            return verification
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_valid_otp(cls, email, otp_code):
        """
        Obtener una verificación válida por email y código OTP.
        
        Args:
            email: Email
            otp_code: Código OTP
        
        Returns:
            EmailVerification instance o None
        """
        try:
            verification = cls.objects.get(email=email, otp_code=otp_code, verification_type=cls.VERIFICATION_TYPE_OTP)
            if verification.is_expired or verification.is_verified:
                return None
            return verification
        except cls.DoesNotExist:
            return None
    
    @staticmethod
    def generate_otp_code():
        """Generar un código OTP aleatorio de 6 dígitos."""
        return str(secrets.randbelow(900000) + 100000)


# Alias para compatibilidad hacia atrás
EmailVerificationToken = EmailVerification


class UserProfile(models.Model):
    """
    Perfil extendido del usuario con información específica de agricultores.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_profile')
    
    # Información geográfica (normalizada)
    # Note: phone_number removed - use Persona.telefono instead
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        help_text="Municipio de residencia del usuario"
    )
    
    # Información profesional
    years_experience = models.PositiveIntegerField(blank=True, null=True)
    farm_size_hectares = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Preferencias del usuario
    preferred_language = models.CharField(max_length=10, default='es', choices=[
        ('es', 'Español'),
        ('en', 'English'),
    ])
    email_notifications = models.BooleanField(default=True)
    
    # Método de autenticación
    login_provider = models.CharField(
        max_length=20,
        default='local',
        choices=[
            ('local', 'Local'),
            ('google', 'Google'),
        ],
        help_text="Método de autenticación utilizado por el usuario"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-created_at']
        # Note: No explicit index on municipio - Django automatically creates one for ForeignKey
    
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
            # Buscar verificación de registro verificada para este usuario
            verification = EmailVerification.objects.filter(
                user=self.user,
                verification_type=EmailVerification.VERIFICATION_TYPE_REGISTRATION,
                is_verified=True
            ).first()
            return verification is not None
        except (AttributeError, KeyError, ValueError):
            return False


# PendingEmailVerification eliminado - usar EmailVerification con verification_type='otp' en su lugar
# Se mantiene como alias para compatibilidad temporal durante la migración
PendingEmailVerification = EmailVerification


