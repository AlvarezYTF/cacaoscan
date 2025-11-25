"""
Modelos de auditoría para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """
    Modelo para registrar actividades del sistema.
    """
    # Este modelo puede estar en otra parte, pero lo dejamos aquí por ahora
    pass


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
        db_table = 'api_loginhistory'  # Mantener nombre de tabla para compatibilidad
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
