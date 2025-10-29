"""
Configuración del admin para la app personas.
"""
from django.contrib import admin
from .models import TipoDocumento, Genero, Ubicacion, Persona


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    """Admin para TipoDocumento."""
    list_display = ['codigo', 'nombre']
    search_fields = ['codigo', 'nombre']
    list_filter = ['codigo']


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    """Admin para Genero."""
    list_display = ['codigo', 'nombre']
    search_fields = ['codigo', 'nombre']
    list_filter = ['codigo']


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    """Admin para Ubicacion."""
    list_display = ['municipio', 'departamento']
    search_fields = ['municipio', 'departamento']
    list_filter = ['departamento']


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    """Admin para Persona."""
    list_display = [
        'numero_documento',
        'primer_nombre',
        'primer_apellido',
        'telefono',
        'email_usuario',
        'fecha_creacion'
    ]
    search_fields = [
        'primer_nombre',
        'primer_apellido',
        'numero_documento',
        'telefono',
        'user__email'
    ]
    list_filter = ['tipo_documento', 'genero', 'ubicacion', 'fecha_creacion']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Documento de Identidad', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
        ('Nombres', {
            'fields': ('primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido')
        }),
        ('Información Personal', {
            'fields': ('telefono', 'direccion', 'genero', 'fecha_nacimiento')
        }),
        ('Ubicación', {
            'fields': ('ubicacion',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',)
        }),
    )
    
    def email_usuario(self, obj):
        """Mostrar el email del usuario."""
        return obj.user.email if obj.user else '-'
    email_usuario.short_description = 'Email'
    
    def departamento_list(self, obj):
        """Mostrar el departamento."""
        return obj.ubicacion.departamento if obj.ubicacion else '-'
    departamento_list.short_description = 'Departamento'
