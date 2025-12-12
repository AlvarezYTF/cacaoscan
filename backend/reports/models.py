"""
Modelos de reportes para CacaoScan.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from catalogos.models import Parametro


class ReporteGenerado(models.Model):
    """
    Modelo para gestionar reportes generados del sistema.
    Normalización 3FN: Usa catálogos para tipo_reporte, formato y estado.
    """
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reportes_generados',
        help_text="Usuario que solicitó el reporte"
    )
    tipo_reporte = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        related_name='reportes_tipo',
        limit_choices_to={'tema__codigo': 'TEMA_TIPO_REPORTE'},
        help_text="Tipo de reporte"
    )
    formato = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        related_name='reportes_formato',
        limit_choices_to={'tema__codigo': 'TEMA_FORMATO_REPORTE'},
        help_text="Formato del reporte"
    )
    titulo = models.CharField(max_length=200, blank=True, default="")
    descripcion = models.TextField(blank=True, default="")
    estado = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        related_name='reportes_estado',
        limit_choices_to={'tema__codigo': 'TEMA_ESTADO_REPORTE'},
        help_text="Estado del reporte"
    )
    
    archivo = models.FileField(upload_to='reportes/%Y/%m/%d/', null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255, blank=True, default="")
    ruta_archivo = models.CharField(max_length=500, blank=True, default="", help_text="Ruta del archivo generado")
    tamano_archivo = models.PositiveIntegerField(blank=True, default=0, db_column='tamaño_archivo')
    
    parametros = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Parámetros adicionales del reporte (JSON). Evitar duplicar datos que deberían ser ForeignKeys (ej: IDs de fincas, municipios). Usar referencias por ID en lugar de objetos completos."
    )
    filtros_aplicados = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Filtros aplicados al generar el reporte (JSON). Evitar duplicar datos que deberían ser ForeignKeys. Usar referencias por ID en lugar de objetos completos."
    )
    
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
        tipo = self.tipo_reporte.nombre if hasattr(self.tipo_reporte, 'nombre') else str(self.tipo_reporte)
        return f"Reporte {tipo} - {self.nombre_archivo}"
    
    @staticmethod
    def generar_reporte(usuario, tipo_reporte, formato, titulo, descripcion='', parametros=None, filtros=None):
        """
        Crea un nuevo reporte.
        
        Args:
            usuario: Usuario que solicita el reporte
            tipo_reporte: TipoReporte (FK) o código de tipo de reporte
            formato: FormatoReporte (FK) o código de formato
            titulo: Título del reporte
            descripcion: Descripción del reporte
            parametros: Parámetros adicionales
            filtros: Filtros a aplicar
            
        Returns:
            ReporteGenerado: Instancia del reporte creado
        """
        # Convertir códigos a objetos FK si es necesario
        if isinstance(tipo_reporte, str):
            tipo_reporte = Parametro.objects.get(tema__codigo='TEMA_TIPO_REPORTE', codigo=tipo_reporte.upper())
        if isinstance(formato, str):
            formato = Parametro.objects.get(tema__codigo='TEMA_FORMATO_REPORTE', codigo=formato.upper())
        
        # Obtener estado por defecto
        estado = Parametro.objects.get(tema__codigo='TEMA_ESTADO_REPORTE', codigo='PENDIENTE')
        
        reporte = ReporteGenerado(
            usuario=usuario,
            tipo_reporte=tipo_reporte,
            formato=formato,
            titulo=titulo,
            descripcion=descripcion or '',
            parametros=parametros or {},
            filtros_aplicados=filtros or {},
            estado=estado
        )
        reporte.save()
        return reporte
    
    def marcar_completado(self, archivo, tiempo_generacion):
        """Marca el reporte como completado."""
        estado = Parametro.objects.get(tema__codigo='TEMA_ESTADO_REPORTE', codigo='COMPLETADO')
        self.estado = estado
        self.archivo = archivo
        self.tiempo_generacion = tiempo_generacion
        self.fecha_generacion = timezone.now()
        
        # Set nombre_archivo if not already set
        if not self.nombre_archivo and hasattr(archivo, 'name'):
            self.nombre_archivo = archivo.name
        
        # Set tamano_archivo if available
        if hasattr(archivo, 'size'):
            self.tamano_archivo = archivo.size
        elif hasattr(archivo, 'read'):
            # For ContentFile, read to get size
            try:
                current_pos = archivo.tell()
                archivo.seek(0, 2)  # Seek to end
                size = archivo.tell()
                archivo.seek(current_pos)  # Restore position
                self.tamano_archivo = size
            except Exception:
                pass
        
        self.save()
    
    def marcar_fallido(self, mensaje_error):
        """Marca el reporte como fallido."""
        estado = Parametro.objects.get(tema__codigo='TEMA_ESTADO_REPORTE', codigo='FALLIDO')
        self.estado = estado
        self.mensaje_error = mensaje_error
        self.save()
    
    def clean(self):
        """
        Validar que los campos JSONB no contengan datos que deberían ser ForeignKeys.
        """
        from django.core.exceptions import ValidationError
        
        # Validar parametros: no debe contener objetos completos de entidades normalizadas
        if self.parametros:
            forbidden_keys = ['finca', 'municipio', 'departamento', 'variedad', 'lote', 'usuario']
            for key in forbidden_keys:
                if key in self.parametros and isinstance(self.parametros[key], dict):
                    # Si contiene un objeto completo, debe ser solo un ID
                    if 'id' not in self.parametros[key] and len(self.parametros[key]) > 1:
                        raise ValidationError({
                            'parametros': f'parametros no debe contener objetos completos de {key}. Usar solo el ID (ej: {{"{key}_id": 123}})'
                        })
        
        # Validar filtros_aplicados: no debe contener objetos completos de entidades normalizadas
        if self.filtros_aplicados:
            forbidden_keys = ['finca', 'municipio', 'departamento', 'variedad', 'lote', 'usuario']
            for key in forbidden_keys:
                if key in self.filtros_aplicados and isinstance(self.filtros_aplicados[key], dict):
                    # Si contiene un objeto completo, debe ser solo un ID
                    if 'id' not in self.filtros_aplicados[key] and len(self.filtros_aplicados[key]) > 1:
                        raise ValidationError({
                            'filtros_aplicados': f'filtros_aplicados no debe contener objetos completos de {key}. Usar solo el ID (ej: {{"{key}_id": 123}})'
                        })
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.full_clean()
        super().save(*args, **kwargs)
