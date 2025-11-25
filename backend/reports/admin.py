"""
Configuración del admin de Django para la app de reportes.
"""
from django.contrib import admin
from .models import ReporteGenerado


@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    """Admin para reportes generados."""
    list_display = ('titulo', 'usuario', 'tipo_reporte', 'formato', 'estado', 'fecha_solicitud', 'tamano_archivo_mb')
    list_filter = ('tipo_reporte', 'formato', 'estado', 'fecha_solicitud')
    search_fields = ('titulo', 'usuario__username', 'usuario__email', 'descripcion')
    readonly_fields = ('fecha_solicitud', 'fecha_generacion', 'tiempo_generacion', 'tamano_archivo_mb', 'archivo_url', 'esta_expirado', 'created_at', 'updated_at')
    date_hierarchy = 'fecha_solicitud'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'titulo', 'descripcion', 'tipo_reporte', 'formato', 'estado')
        }),
        ('Archivo', {
            'fields': ('archivo', 'nombre_archivo', 'tamano_archivo', 'tamano_archivo_mb', 'archivo_url')
        }),
        ('Parámetros y Filtros', {
            'fields': ('parametros', 'filtros_aplicados'),
            'classes': ('collapse',)
        }),
        ('Fechas y Tiempos', {
            'fields': ('fecha_solicitud', 'fecha_generacion', 'fecha_expiracion', 'tiempo_generacion', 'tiempo_generacion_segundos', 'esta_expirado')
        }),
        ('Errores', {
            'fields': ('mensaje_error',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related."""
        return super().get_queryset(request).select_related('usuario')
