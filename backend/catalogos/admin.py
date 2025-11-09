from django.contrib import admin
from .models import Tema, Parametro, Departamento, Municipio


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo', 'parametros_count']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre', 'descripcion']
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
    
    def parametros_count(self, obj):
        """Muestra el número de parámetros del tema"""
        return obj.parametros.filter(activo=True).count()
    parametros_count.short_description = 'Parámetros Activos'


@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tema', 'activo']
    list_filter = ['tema', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion', 'tema__nombre']
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tema', 'codigo', 'nombre', 'descripcion')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'municipios_count']
    search_fields = ['codigo', 'nombre']
    list_filter = []
    
    fieldsets = (
        ('Información', {
            'fields': ('codigo', 'nombre')
        }),
    )
    
    def municipios_count(self, obj):
        """Muestra el número de municipios del departamento"""
        return obj.municipios.count()
    municipios_count.short_description = 'Municipios'


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'departamento']
    list_filter = ['departamento']
    search_fields = ['codigo', 'nombre', 'departamento__nombre']
    
    fieldsets = (
        ('Información', {
            'fields': ('departamento', 'codigo', 'nombre')
        }),
    )

