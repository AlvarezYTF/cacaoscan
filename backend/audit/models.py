"""
Modelos de auditoría para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """
    Modelo para registrar actividades del sistema.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text="Usuario que realizó la acción"
    )
    action = models.CharField(max_length=100, help_text="Acción realizada")
    resource_type = models.CharField(max_length=50, blank=True, default="", help_text="Tipo de recurso afectado")
    resource_id = models.IntegerField(null=True, blank=True, help_text="ID del recurso afectado")
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
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
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
        null=True,
        blank=True,
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
