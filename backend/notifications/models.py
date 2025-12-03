"""
Modelos para el sistema de notificaciones.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """Modelo para notificaciones del sistema."""
    
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
        help_text='Usuario destinatario de la notificación'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='info',
        help_text='Tipo de notificación'
    )
    titulo = models.CharField(
        max_length=200,
        help_text='Título de la notificación'
    )
    mensaje = models.TextField(
        help_text='Mensaje detallado de la notificación'
    )
    leida = models.BooleanField(
        default=False,
        help_text='Indica si la notificación ha sido leída'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación de la notificación'
    )
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha en que se marcó como leída'
    )
    datos_extra = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales en formato JSON'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['user', '-fecha_creacion']),
            models.Index(fields=['leida', '-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"Notificación para {self.user.username}: {self.titulo}"
    
    def mark_as_read(self):
        """Marca la notificación como leída."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])
    
    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la creación."""
        if not self.fecha_creacion:
            return ''
        
        delta = timezone.now() - self.fecha_creacion
        
        if delta.days > 0:
            return f"hace {delta.days} día{'s' if delta.days > 1 else ''}"
        elif delta.seconds >= 3600:
            horas = delta.seconds // 3600
            return f"hace {horas} hora{'s' if horas > 1 else ''}"
        elif delta.seconds >= 60:
            minutos = delta.seconds // 60
            return f"hace {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            return "hace unos momentos"
