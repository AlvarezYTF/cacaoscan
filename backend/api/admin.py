"""
Configuración del admin de Django para la API de CacaoScan.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import EmailVerificationToken, UserProfile, CacaoImage, CacaoPrediction, SystemSettings


# Configuración personalizada para User
class UserProfileInline(admin.StackedInline):
    """Inline para mostrar perfil extendido en el admin de User."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil Extendido'
    fields = (
        'phone_number', 'region', 'municipality', 'farm_name',
        'years_experience', 'farm_size_hectares', 'preferred_language',
        'email_notifications'
    )


class CustomUserAdmin(UserAdmin):
    """Admin personalizado para User con perfil extendido."""
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        """Mostrar inline solo si el objeto existe."""
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-registrar User con admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin para tokens de verificación de email."""
    list_display = ('user', 'email', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at', 'verified_at', 'expires_at')
    
    def email(self, obj):
        """Mostrar email del usuario."""
        return obj.user.email
    email.short_description = 'Email'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para perfiles de usuario."""
    list_display = ('user', 'full_name', 'role', 'region', 'farm_name', 'is_verified', 'created_at')
    list_filter = ('region', 'preferred_language', 'email_notifications', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'farm_name', 'region')
    readonly_fields = ('created_at', 'updated_at', 'full_name', 'role', 'is_verified')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'full_name', 'role', 'is_verified')
        }),
        ('Información de Contacto', {
            'fields': ('phone_number',)
        }),
        ('Información Geográfica', {
            'fields': ('region', 'municipality')
        }),
        ('Información de la Finca', {
            'fields': ('farm_name', 'years_experience', 'farm_size_hectares')
        }),
        ('Preferencias', {
            'fields': ('preferred_language', 'email_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CacaoImage)
class CacaoImageAdmin(admin.ModelAdmin):
    """Admin para imágenes de cacao."""
    list_display = ('id', 'user', 'file_name', 'region', 'finca', 'processed', 'has_prediction', 'uploaded_at')
    list_filter = ('processed', 'region', 'finca', 'uploaded_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'file_name', 'finca', 'region', 'lote_id', 'variedad')
    readonly_fields = ('id', 'uploaded_at', 'file_name', 'file_size', 'file_type', 'created_at', 'updated_at', 'file_size_mb', 'has_prediction')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'user', 'image', 'uploaded_at', 'processed')
        }),
        ('Metadatos del Grano/Finca', {
            'fields': ('finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas')
        }),
        ('Información Técnica', {
            'fields': ('file_name', 'file_size', 'file_size_mb', 'file_type', 'has_prediction')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related."""
        return super().get_queryset(request).select_related('user')


@admin.register(CacaoPrediction)
class CacaoPredictionAdmin(admin.ModelAdmin):
    """Admin para predicciones de cacao."""
    list_display = ('id', 'image_user', 'alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g', 'average_confidence', 'model_version', 'created_at')
    list_filter = ('model_version', 'device_used', 'created_at')
    search_fields = ('image__user__username', 'image__user__email', 'image__finca', 'image__region')
    readonly_fields = ('id', 'image', 'processing_time_ms', 'model_version', 'device_used', 'average_confidence', 'volume_cm3', 'density_g_cm3', 'created_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'image', 'created_at')
        }),
        ('Predicciones de Dimensiones', {
            'fields': ('alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g')
        }),
        ('Scores de Confianza', {
            'fields': ('confidence_alto', 'confidence_ancho', 'confidence_grosor', 'confidence_peso', 'average_confidence')
        }),
        ('Metadatos de Procesamiento', {
            'fields': ('processing_time_ms', 'crop_url', 'model_version', 'device_used')
        }),
        ('Cálculos Derivados', {
            'fields': ('volume_cm3', 'density_g_cm3'),
            'classes': ('collapse',)
        }),
    )
    
    def image_user(self, obj):
        """Mostrar usuario de la imagen."""
        return obj.image.user.username
    image_user.short_description = 'Usuario'
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related."""
        return super().get_queryset(request).select_related('image__user')


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin para configuración del sistema."""
    list_display = ('nombre_sistema', 'email_contacto', 'updated_at')
    
    def has_add_permission(self, request):
        """No permitir agregar más de una instancia."""
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar la configuración."""
        return False


# Configuración del sitio admin
admin.site.site_header = "CacaoScan - Administración"
admin.site.site_title = "CacaoScan Admin"
admin.site.index_title = "Panel de Administración"
