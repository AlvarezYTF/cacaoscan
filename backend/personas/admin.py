"""
Configuración del admin para la app personas.

INTEGRACI"N:
- Persona ahora usa Parametro (catálogos) para tipo_documento y genero
- Persona ahora usa Departamento y Municipio (ubicaciones) para ubicación
"""
from django.contrib import admin
from .models import Persona, PendingRegistration


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    """
    Admin para Persona.
    
    Campos relacionados integrados:
    - tipo_documento: Parametro del tema TIPO_DOC
    - genero: Parametro del tema SEXO
    - departamento: Departamento (normalizado)
    - municipio: Municipio (normalizado)
    """
    list_display = [
        'numero_documento',
        'nombre_completo',
        'email_usuario',
        'get_departamento',
        'get_municipio',
        'fecha_creacion'
    ]
    search_fields = [
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'numero_documento',
        'telefono',
        'user__email'
    ]
    list_filter = [
        'tipo_documento__tema',
        'genero__tema',
        'departamento',
        'fecha_creacion'
    ]
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Documento de Identidad', {
            'fields': ('tipo_documento', 'numero_documento'),
            'description': 'Tipo de documento es un Parametro del catálogo TIPO_DOC'
        }),
        ('Nombres', {
            'fields': ('primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido')
        }),
        ('Información Personal', {
            'fields': ('telefono', 'direccion', 'genero', 'fecha_nacimiento'),
            'description': 'Género es un Parametro del catálogo SEXO'
        }),
        ('Ubicación (Normalizada)', {
            'fields': ('departamento', 'municipio'),
            'description': 'Ubicación usa las tablas normalizadas de ubicaciones'
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',)
        }),
    )
    
    def nombre_completo(self, obj):
        """Mostrar el nombre completo de la persona."""
        nombres = f"{obj.primer_nombre}"
        if obj.segundo_nombre:
            nombres += f" {obj.segundo_nombre}"
        apellidos = f"{obj.primer_apellido}"
        if obj.segundo_apellido:
            apellidos += f" {obj.segundo_apellido}"
        return f"{nombres} {apellidos}"
    nombre_completo.short_description = 'Nombre Completo'
    
    def email_usuario(self, obj):
        """Mostrar el email del usuario."""
        return obj.user.email if obj.user else '-'
    email_usuario.short_description = 'Email'
    
    def get_departamento(self, obj):
        """Mostrar el departamento."""
        return obj.departamento.nombre if obj.departamento else '-'
    get_departamento.short_description = 'Departamento'
    
    def get_municipio(self, obj):
        """Mostrar el municipio."""
        return obj.municipio.nombre if obj.municipio else '-'
    get_municipio.short_description = 'Municipio'


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    """Admin para registros pendientes de verificación."""
    list_display = [
        'email',
        'is_verified',
        'created_at',
        'verified_at',
        'is_expired_display'
    ]
    search_fields = ['email', 'verification_token']
    list_filter = ['is_verified', 'created_at']
    readonly_fields = ['verification_token', 'created_at', 'verified_at']
    
    def is_expired_display(self, obj):
        """Indica si el registro ha expirado."""
        return "Sí" if obj.is_expired() else "No"
    is_expired_display.short_description = 'Expirado'
    is_expired_display.boolean = True

