"""
Modelos de auditoría para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ActivityLog(models.Model):
    """
    Modelo para registrar actividades del sistema.
    Auditoría flexible usando ContentType de Django para integridad referencial avanzada.
    NO viola normalización: es un patrón de diseño estándar de Django para relaciones polimórficas.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text="Usuario que realizó la acción"
    )
    action = models.CharField(max_length=100, help_text="Acción realizada")
    
    # Flexible audit fields using ContentType (Django's standard pattern for polymorphic relations)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Tipo de recurso afectado (usando ContentType para auditoría flexible)"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID del recurso afectado"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Legacy fields for backward compatibility (deprecated, use content_type/object_id)
    resource_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="[DEPRECATED] Tipo de recurso afectado - usar content_type. Debe ser un nombre de modelo válido (ej: 'CacaoImage', 'images_app.cacaoimage')"
    )
    resource_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="[DEPRECATED] ID del recurso afectado - usar object_id. Requiere resource_type si se proporciona."
    )
    
    details = models.JSONField(default=dict, blank=True, help_text="Detalles adicionales de la acción")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Dirección IP del usuario")
    user_agent = models.TextField(blank=True, default="", help_text="User Agent del navegador")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de la acción")
    
    class Meta:
        db_table = 'api_activitylog'
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['content_type', 'object_id']),
            # Legacy index for backward compatibility
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def clean(self):
        """
        Validar que los campos legacy y ContentType se usen correctamente.
        """
        from django.core.exceptions import ValidationError
        
        # Validar que si resource_id está presente, resource_type también lo esté
        if self.resource_id is not None and (not self.resource_type or self.resource_type == ''):
            raise ValidationError({
                'resource_id': 'resource_id requiere que resource_type también esté presente (campos legacy)'
            })
        
        # Validar que si object_id está presente, content_type también lo esté
        if self.object_id is not None and self.content_type is None:
            raise ValidationError({
                'object_id': 'object_id requiere que content_type también esté presente (campos ContentType)'
            })
        
        # Validar formato de resource_type si está presente
        if self.resource_type and self.resource_type != '':
            import re
            if not re.match(r'^[a-zA-Z0-9_.]+$', self.resource_type):
                raise ValidationError({
                    'resource_type': 'resource_type debe ser un nombre de modelo válido (solo letras, números, puntos y guiones bajos)'
                })
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        """Representación string del log."""
        return f"{self.user.username} - {self.action}"


class LoginHistory(models.Model):
    """
    Modelo para registrar el historial de inicios de sesión.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_history',
        help_text="Usuario que inició sesión"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP del usuario"
    )
    user_agent = models.TextField(
        blank=True,
        default="",
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
    login_successful = models.BooleanField(
        default=True,
        help_text="Indica si el inicio de sesión fue exitoso"
    )
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Razón del fallo si no fue exitoso"
    )
    
    # Alias para compatibilidad
    @property
    def success(self):
        """Alias para login_successful (compatibilidad)."""
        return self.login_successful
    
    @success.setter
    def success(self, value):
        """Setter para success (compatibilidad)."""
        self.login_successful = value
    
    @property
    def usuario(self):
        """Alias para user (compatibilidad)."""
        return self.user
    
    @usuario.setter
    def usuario(self, value):
        """Setter para usuario (compatibilidad)."""
        self.user = value
    
    class Meta:
        db_table = 'api_loginhistory'  # Mantener nombre de tabla para compatibilidad
        verbose_name = 'Historial de Login'
        verbose_name_plural = 'Historial de Logins'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['login_time']),
            models.Index(fields=['login_successful']),
        ]
    
    def __str__(self):
        """Representación string del historial."""
        status = "Exitoso" if self.login_successful else "Fallido"
        return f"Login de {self.user.username} - {status}"
