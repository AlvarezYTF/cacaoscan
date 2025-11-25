"""
Modelos de reportes para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    tipo_reporte = models.CharField(max_length=20, choices=TIPO_REPORTE_CHOICES)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='generando')
    
    archivo = models.FileField(upload_to='reportes/%Y/%m/%d/', null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255, null=True, blank=True)
    tamano_archivo = models.PositiveIntegerField(null=True, blank=True, db_column='tamaño_archivo')
    
    parametros = models.JSONField(default=dict, blank=True)
    filtros_aplicados = models.JSONField(default=dict, blank=True)
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    tiempo_generacion = models.DurationField(null=True, blank=True)
    
    mensaje_error = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_reportegenerado'  # Mantener nombre de tabla para compatibilidad
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_solicitud']
    
    @property
    def tamano_archivo_mb(self):
        """Obtener tamaño del archivo en MB."""
        if self.tamano_archivo:
            return round(self.tamano_archivo / (1024 * 1024), 2)
        return None
    
    @property
    def archivo_url(self):
        """Obtener URL del archivo."""
        if self.archivo:
            return self.archivo.url
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
