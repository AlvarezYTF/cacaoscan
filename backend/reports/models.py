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
        ('analisis_periodo', 'Análisis por Período'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
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
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='pdf')
    titulo = models.CharField(max_length=200, blank=True, default="")
    descripcion = models.TextField(blank=True, default="")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    archivo = models.FileField(upload_to='reportes/%Y/%m/%d/', null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255, blank=True, default="")
    ruta_archivo = models.CharField(max_length=500, blank=True, default="", help_text="Ruta del archivo generado")
    tamano_archivo = models.PositiveIntegerField(blank=True, default=0, db_column='tamaño_archivo')
    
    parametros = models.JSONField(default=dict, blank=True)
    filtros_aplicados = models.JSONField(default=dict, blank=True)
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de generación del reporte")
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    tiempo_generacion = models.DurationField(null=True, blank=True)
    
    mensaje_error = models.TextField(blank=True, default="")
    
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
    
    def __str__(self):
        """Representación string del reporte."""
        return f"Reporte {self.tipo_reporte} - {self.nombre_archivo}"
    
    @staticmethod
    def generar_reporte(usuario, tipo_reporte, formato, titulo, descripcion='', parametros=None, filtros=None):
        """
        Crea un nuevo reporte.
        
        Args:
            usuario: Usuario que solicita el reporte
            tipo_reporte: Tipo de reporte
            formato: Formato del reporte
            titulo: Título del reporte
            descripcion: Descripción del reporte
            parametros: Parámetros adicionales
            filtros: Filtros a aplicar
            
        Returns:
            ReporteGenerado: Instancia del reporte creado
        """
        reporte = ReporteGenerado(
            usuario=usuario,
            tipo_reporte=tipo_reporte,
            formato=formato,
            titulo=titulo,
            descripcion=descripcion or '',
            parametros=parametros or {},
            filtros_aplicados=filtros or {},
            estado='pendiente'
        )
        reporte.save()
        return reporte
    
    def marcar_completado(self, archivo, tiempo_generacion):
        """Marca el reporte como completado."""
        self.estado = 'completado'
        self.archivo = archivo
        self.tiempo_generacion = tiempo_generacion
        self.fecha_generacion = timezone.now()
        self.save()
    
    def marcar_fallido(self, mensaje_error):
        """Marca el reporte como fallido."""
        self.estado = 'fallido'
        self.mensaje_error = mensaje_error
        self.save()
