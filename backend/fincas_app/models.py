"""
Modelos para gestión de fincas y lotes en CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from catalogos.models import Municipio, Parametro

# Date format constants
DATE_FORMAT_DMY = '%d/%m/%Y'


class Finca(TimeStampedModel):
    """
    Modelo para gestionar fincas de cacao.
    """
    nombre = models.CharField(max_length=200, help_text="Nombre de la finca")
    ubicacion = models.CharField(max_length=300, help_text="Dirección o ubicación de la finca")
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        related_name='fincas',
        help_text="Municipio donde se encuentra la finca"
    )
    hectareas = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Área total de la finca en hectáreas"
    )
    agricultor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='fincas_app_fincas',
        help_text="Agricultor propietario de la finca"
    )
    
    # Alias para compatibilidad con tests
    @property
    def propietario(self):
        """Alias para agricultor (compatibilidad con tests)."""
        return self.agricultor
    
    @propietario.setter
    def propietario(self, value):
        """Setter para propietario (compatibilidad con tests)."""
        self.agricultor = value
    
    @property
    def area_total(self):
        """Alias para hectareas (compatibilidad con tests)."""
        return self.hectareas
    
    @area_total.setter
    def area_total(self, value):
        """Setter para area_total (compatibilidad con tests)."""
        self.hectareas = value
    
    # Información adicional
    descripcion = models.TextField(blank=True, default="", help_text="Descripción adicional de la finca")
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
    activa = models.BooleanField(default=True, help_text="Indica si la finca está activa")
    
    # Campos adicionales requeridos por tests
    altitud = models.IntegerField(default=100, help_text="Altitud en metros sobre el nivel del mar")
    tipo_suelo = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='fincas_tipo_suelo',
        limit_choices_to={'tema__codigo': 'TEMA_TIPO_SUELO'},
        help_text="Tipo de suelo de la finca"
    )
    clima = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='fincas_clima',
        limit_choices_to={'tema__codigo': 'TEMA_CLIMA'},
        help_text="Tipo de clima de la finca"
    )
    estado = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='fincas_estado',
        limit_choices_to={'tema__codigo': 'TEMA_ESTADO_FINCA'},
        help_text="Estado de la finca"
    )
    precipitacion_anual = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Precipitación anual en mm"
    )
    temperatura_promedio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Temperatura promedio en grados Celsius"
    )
    
    class Meta:
        db_table = 'api_finca'
        verbose_name = 'Finca'
        verbose_name_plural = 'Fincas'
        ordering = ['-created_at']
        indexes = [
            # Composite index for agricultor + created_at (useful for queries filtering by agricultor and date)
            models.Index(fields=['agricultor', '-created_at']),
            # Index for activa (not a FK, needs explicit index)
            models.Index(fields=['activa']),
            # Note: Django automatically creates indexes for ForeignKeys (estado, tipo_suelo, clima, municipio, agricultor)
            # So we don't need explicit indexes for those fields
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hectareas__gt=0),
                name='fincas_app_finca_hectareas_positivas'
            ),
        ]
    
    def __str__(self):
        if self.municipio:
            return f"{self.nombre} - {self.municipio.nombre}, {self.municipio.departamento.nombre}"
        return f"{self.nombre}"
    
    @property
    def total_lotes(self):
        """Obtener número total de lotes en la finca."""
        return self.lotes.count()
    
    @property
    def lotes_activos(self):
        """Obtener número de lotes activos en la finca."""
        return self.lotes.filter(activo=True).count()
    
    @property
    def total_analisis(self):
        """Obtener número total de análisis realizados en la finca."""
        from django.db.models import Count
        try:
            return self.lotes.aggregate(
                total=Count('cacao_images__prediction', distinct=True)
            )['total'] or 0
        except (ValueError, TypeError, AttributeError):
            return 0
    
    @property
    def calidad_promedio(self):
        """Calcular calidad promedio de la finca basada en análisis."""
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
        """Obtener ubicación completa formateada."""
        if self.municipio:
            return f"{self.ubicacion}, {self.municipio.nombre}, {self.municipio.departamento.nombre}"
        return self.ubicacion
    
    def get_estadisticas(self):
        """Obtener estadísticas completas de la finca."""
        return {
            'total_lotes': self.total_lotes,
            'lotes_activos': self.lotes_activos,
            'total_analisis': self.total_analisis,
            'calidad_promedio': self.calidad_promedio,
            'hectareas': float(self.hectareas),
            'fecha_registro': self.fecha_registro.strftime(DATE_FORMAT_DMY),
            'activa': self.activa
        }


class Lote(TimeStampedModel):
    """
    Modelo para gestionar lotes de cacao como bultos de granos.
    Un lote representa un bulto de granos de cacao que será escaneado por IA
    para determinar sus características de calidad.
    """
    finca = models.ForeignKey(
        Finca, 
        on_delete=models.CASCADE, 
        related_name='lotes',
        help_text="Finca de origen del bulto de granos"
    )
    identificador = models.CharField(
        max_length=50, 
        blank=True,
        default="",
        help_text="Identificador único del lote dentro de la finca"
    )
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre o descripción del bulto"
    )
    variedad = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        related_name='lotes_variedad',
        limit_choices_to={'tema__codigo': 'TEMA_VARIEDAD_CACAO'},
        help_text="Variedad de cacao del bulto"
    )
    peso_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Peso del bulto en kilogramos"
    )
    fecha_recepcion = models.DateField(
        help_text="Fecha en que se recibió el bulto"
    )
    fecha_plantacion = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de plantación del cacao (opcional)"
    )
    fecha_cosecha = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de cosecha del cacao (opcional)"
    )
    fecha_procesamiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de procesamiento/fermentación del bulto (opcional)"
    )
    estado = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='lotes_estado',
        limit_choices_to={'tema__codigo': 'TEMA_ESTADO_LOTE'},
        help_text="Estado del procesamiento del bulto (Recibido, En fermentación, Fermentado, Secado, Listo para análisis, Analizado)"
    )
    
    # Información adicional
    descripcion = models.TextField(blank=True, default="", help_text="Descripción adicional o notas sobre el bulto")
    fecha_registro = models.DateTimeField(auto_now_add=True, help_text="Fecha de registro del lote")
    activo = models.BooleanField(default=True, help_text="Indica si el lote está activo")
    
    # Campos adicionales requeridos por tests (mantener para compatibilidad temporal)
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del lote")
    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización")
    
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
                condition=models.Q(peso_kg__gt=0),
                name='fincas_app_lote_peso_positivo'
            ),
            models.CheckConstraint(
                condition=models.Q(fecha_procesamiento__isnull=True) | models.Q(fecha_procesamiento__gte=models.F('fecha_recepcion')),
                name='fincas_app_lote_fecha_procesamiento_valida'
            ),
            models.CheckConstraint(
                condition=models.Q(fecha_cosecha__isnull=True) | models.Q(fecha_plantacion__isnull=True) | models.Q(fecha_cosecha__gte=models.F('fecha_plantacion')),
                name='fincas_app_lote_fecha_cosecha_valida'
            ),
            models.UniqueConstraint(
                fields=['finca', 'identificador'],
                name='fincas_app_lote_identificador_unico_por_finca',
                condition=models.Q(identificador__gt='')
            ),
        ]
    
    def __str__(self):
        """Representación string del lote."""
        if self.nombre:
            return f"{self.nombre} - {self.finca.nombre}"
        variedad_nombre = self.variedad.nombre if self.variedad else "N/A"
        return f"{self.identificador} - {variedad_nombre} ({self.finca.nombre})"
    
    @property
    def total_analisis(self):
        """Obtener número total de análisis realizados en el lote."""
        try:
            return self.cacao_images.count()
        except (ValueError, TypeError, AttributeError):
            return 0
    
    @property
    def analisis_procesados(self):
        """Obtener número de análisis procesados en el lote."""
        try:
            return self.cacao_images.filter(processed=True).count()
        except (ValueError, TypeError, AttributeError):
            return 0
    
    @property
    def calidad_promedio(self):
        """Calcular calidad promedio del lote basada en análisis."""
        from django.db.models import Avg
        try:
            if not hasattr(self, 'cacao_images') or not self.cacao_images.exists():
                return 0.0
            avg_confidence = self.cacao_images.aggregate(
                avg_quality=Avg('prediction__average_confidence')
            )['avg_quality']
            return round(float(avg_confidence or 0) * 100, 2)
        except (ValueError, TypeError, AttributeError):
            return 0.0
    
    @property
    def edad_meses(self):
        """Calcular edad del lote en meses."""
        try:
            if not self.fecha_plantacion:
                return 0
            from datetime import date
            today = date.today()
            delta = today - self.fecha_plantacion
            return max(0, delta.days // 30)
        except (ValueError, TypeError, AttributeError):
            return 0
    
    @property
    def ubicacion_completa(self):
        """Obtener ubicación completa formateada."""
        if self.finca and self.finca.municipio:
            return f"{self.finca.ubicacion}, {self.finca.municipio.nombre}, {self.finca.municipio.departamento.nombre}"
        elif self.finca:
            return self.finca.ubicacion
        return ""
    
    def get_estadisticas(self):
        """Obtener estadísticas completas del lote."""
        try:
            return {
                'total_analisis': self.total_analisis,
                'analisis_procesados': self.analisis_procesados,
                'calidad_promedio': self.calidad_promedio,
                'peso_kg': float(self.peso_kg) if self.peso_kg else 0.0,
                'edad_meses': self.edad_meses,
                'estado': self.estado.nombre if self.estado else None,
                'activo': self.activo,
                'fecha_plantacion': self.fecha_plantacion.strftime(DATE_FORMAT_DMY) if self.fecha_plantacion else None,
                'fecha_cosecha': self.fecha_cosecha.strftime(DATE_FORMAT_DMY) if self.fecha_cosecha else None,
                'fecha_recepcion': self.fecha_recepcion.strftime(DATE_FORMAT_DMY) if self.fecha_recepcion else None,
                'fecha_procesamiento': self.fecha_procesamiento.strftime(DATE_FORMAT_DMY) if self.fecha_procesamiento else None,
            }
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger("cacaoscan.models")
            logger.error(f"Error obteniendo estadísticas de lote {self.id}: {e}", exc_info=True)
            # Return safe default statistics
            return {
                'total_analisis': 0,
                'analisis_procesados': 0,
                'calidad_promedio': 0.0,
                'peso_kg': float(self.peso_kg) if self.peso_kg else 0.0,
                'edad_meses': 0,
                'estado': None,
                'activo': getattr(self, 'activo', True),
                'fecha_plantacion': None,
                'fecha_cosecha': None,
                'fecha_recepcion': None,
                'fecha_procesamiento': None,
            }


