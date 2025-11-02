"""
Modelos para gestiÃ³n de fincas y lotes en CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel


class Finca(TimeStampedModel):
    """
    Modelo para gestionar fincas de cacao.
    """
    nombre = models.CharField(max_length=200, help_text="Nombre de la finca")
    ubicacion = models.CharField(max_length=300, help_text="DirecciÃ³n o ubicaciÃ³n de la finca")
    municipio = models.CharField(max_length=100, help_text="Municipio donde se encuentra la finca")
    departamento = models.CharField(max_length=100, help_text="Departamento donde se encuentra la finca")
    hectareas = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Ãrea total de la finca en hectÃ¡reas"
    )
    agricultor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='fincas_app_fincas',
        help_text="Agricultor propietario de la finca"
    )
    
    # InformaciÃ³n adicional
    descripcion = models.TextField(blank=True, null=True, help_text="DescripciÃ³n adicional de la finca")
    coordenadas_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Latitud GPS de la finca"
    )
    coordenadas_lng = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Longitud GPS de la finca"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, help_text="Fecha de registro de la finca")
    activa = models.BooleanField(default=True, help_text="Indica si la finca estÃ¡ activa")
    
    class Meta:
        db_table = 'api_finca'
        verbose_name = 'Finca'
        verbose_name_plural = 'Fincas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agricultor', '-created_at']),
            models.Index(fields=['agricultor_id']),
            models.Index(fields=['municipio', 'departamento']),
            models.Index(fields=['activa']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(hectareas__gt=0),
                name='fincas_app_finca_hectareas_positivas'
            ),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.municipio}, {self.departamento}"
    
    @property
    def total_lotes(self):
        """Obtener nÃºmero total de lotes en la finca."""
        return self.lotes.count()
    
    @property
    def lotes_activos(self):
        """Obtener nÃºmero de lotes activos en la finca."""
        return self.lotes.filter(activo=True).count()
    
    @property
    def total_analisis(self):
        """Obtener nÃºmero total de anÃ¡lisis realizados en la finca."""
        from django.db.models import Count
        try:
            return self.lotes.aggregate(
                total=Count('cacao_images__prediction', distinct=True)
            )['total'] or 0
        except:
            return 0
    
    @property
    def calidad_promedio(self):
        """Calcular calidad promedio de la finca basada en anÃ¡lisis."""
        from django.db.models import Avg
        try:
            avg_confidence = self.lotes.aggregate(
                avg_quality=Avg('cacao_images__prediction__average_confidence')
            )['avg_quality']
            return round(float(avg_confidence or 0) * 100, 2)
        except Exception:
            return 0.0
    
    @property
    def ubicacion_completa(self):
        """Obtener ubicaciÃ³n completa formateada."""
        return f"{self.ubicacion}, {self.municipio}, {self.departamento}"
    
    def get_estadisticas(self):
        """Obtener estadÃ­sticas completas de la finca."""
        return {
            'total_lotes': self.total_lotes,
            'lotes_activos': self.lotes_activos,
            'total_analisis': self.total_analisis,
            'calidad_promedio': self.calidad_promedio,
            'hectareas': float(self.hectareas),
            'fecha_registro': self.fecha_registro.strftime('%d/%m/%Y'),
            'activa': self.activa
        }


class Lote(TimeStampedModel):
    """
    Modelo para gestionar lotes de cacao dentro de fincas.
    """
    finca = models.ForeignKey(
        Finca, 
        on_delete=models.CASCADE, 
        related_name='fincas_app_lotes',
        help_text="Finca a la que pertenece el lote"
    )
    identificador = models.CharField(
        max_length=50, 
        help_text="Identificador Ãºnico del lote dentro de la finca"
    )
    variedad = models.CharField(
        max_length=100, 
        help_text="Variedad de cacao del lote"
    )
    fecha_plantacion = models.DateField(
        help_text="Fecha de plantaciÃ³n del lote"
    )
    fecha_cosecha = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de cosecha del lote"
    )
    area_hectareas = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Ãrea del lote en hectÃ¡reas"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('cosechado', 'Cosechado'),
            ('renovado', 'Renovado'),
        ],
        default='activo',
        help_text="Estado actual del lote"
    )
    
    # InformaciÃ³n adicional
    descripcion = models.TextField(blank=True, null=True, help_text="DescripciÃ³n adicional del lote")
    coordenadas_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Latitud GPS del lote"
    )
    coordenadas_lng = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        blank=True, 
        null=True,
        help_text="Longitud GPS del lote"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, help_text="Fecha de registro del lote")
    activo = models.BooleanField(default=True, help_text="Indica si el lote estÃ¡ activo")
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['finca', '-created_at']),
            models.Index(fields=['variedad']),
            models.Index(fields=['estado']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(area_hectareas__gt=0),
                name='fincas_app_lote_area_positiva'
            ),
            models.CheckConstraint(
                check=models.Q(fecha_cosecha__isnull=True) | models.Q(fecha_cosecha__gte=models.F('fecha_plantacion')),
                name='fincas_app_lote_fecha_cosecha_valida'
            ),
            models.UniqueConstraint(
                fields=['finca', 'identificador'],
                name='fincas_app_lote_identificador_unico_por_finca'
            ),
        ]
    
    def __str__(self):
        return f"{self.identificador} - {self.variedad} ({self.finca.nombre})"
    
    @property
    def total_analisis(self):
        """Obtener nÃºmero total de anÃ¡lisis realizados en el lote."""
        try:
            return self.cacao_images.count()
        except:
            return 0
    
    @property
    def analisis_procesados(self):
        """Obtener nÃºmero de anÃ¡lisis procesados en el lote."""
        try:
            return self.cacao_images.filter(processed=True).count()
        except:
            return 0
    
    @property
    def calidad_promedio(self):
        """Calcular calidad promedio del lote basada en anÃ¡lisis."""
        from django.db.models import Avg
        try:
            avg_confidence = self.cacao_images.aggregate(
                avg_quality=Avg('prediction__average_confidence')
            )['avg_quality']
            return round(float(avg_confidence or 0) * 100, 2)
        except:
            return 0.0
    
    @property
    def edad_meses(self):
        """Calcular edad del lote en meses."""
        from datetime import date
        today = date.today()
        delta = today - self.fecha_plantacion
        return delta.days // 30
    
    @property
    def ubicacion_completa(self):
        """Obtener ubicaciÃ³n completa formateada."""
        return f"{self.finca.ubicacion}, {self.finca.municipio}, {self.finca.departamento}"
    
    def get_estadisticas(self):
        """Obtener estadÃ­sticas completas del lote."""
        return {
            'total_analisis': self.total_analisis,
            'analisis_procesados': self.analisis_procesados,
            'calidad_promedio': self.calidad_promedio,
            'area_hectareas': float(self.area_hectareas),
            'edad_meses': self.edad_meses,
            'estado': self.estado,
            'activo': self.activo,
            'fecha_plantacion': self.fecha_plantacion.strftime('%d/%m/%Y'),
            'fecha_cosecha': self.fecha_cosecha.strftime('%d/%m/%Y') if self.fecha_cosecha else None,
        }


