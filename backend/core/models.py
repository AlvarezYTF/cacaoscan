"""
Modelos compartidos del core del sistema.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que provee campos created_at y updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SystemSettings(models.Model):
    """
    Modelo para almacenar la configuraciÃ³n del sistema.
    Solo debe haber un registro en esta tabla (singleton).
    """
    # ConfiguraciÃ³n General
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
        help_text='Lema o descripciÃ³n del sistema'
    )
    logo = models.ImageField(
        upload_to='system_settings/',
        null=True,
        blank=True,
        help_text='Logo del sistema'
    )
    
    # ConfiguraciÃ³n de Seguridad
    recaptcha_enabled = models.BooleanField(
        default=True,
        help_text='Activar reCAPTCHA'
    )
    session_timeout = models.IntegerField(
        default=60,
        help_text='Tiempo de sesiÃ³n en minutos'
    )
    login_attempts = models.IntegerField(
        default=5,
        help_text='NÃºmero mÃ¡ximo de intentos de login'
    )
    two_factor_auth = models.BooleanField(
        default=False,
        help_text='Activar autenticaciÃ³n de dos factores'
    )
    
    # ConfiguraciÃ³n de Modelos ML
    active_model = models.CharField(
        max_length=50,
        default='yolov8',
        help_text='Modelo activo para predicciones'
    )
    last_training = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de Ãºltimo entrenamiento'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ConfiguraciÃ³n del Sistema'
        verbose_name_plural = 'ConfiguraciÃ³n del Sistema'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'ConfiguraciÃ³n de {self.nombre_sistema}'
    
    @classmethod
    def get_singleton(cls):
        """
        Obtener o crear la Ãºnica instancia de configuraciÃ³n.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def save(self, *args, **kwargs):
        """Forzar que solo exista un registro."""
        self.pk = 1
        super().save(*args, **kwargs)


