"""
Configuración del admin de Django para la app de auditoría.
"""
from django.contrib import admin
from .models import LoginHistory


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin para historial de logins."""
    list_display = ('usuario', 'ip_address', 'login_time', 'logout_time', 'success', 'session_duration')
    list_filter = ('success', 'login_time', 'ip_address')
    search_fields = ('usuario__username', 'usuario__email', 'ip_address')
    readonly_fields = ('login_time', 'logout_time', 'session_duration')
    date_hierarchy = 'login_time'
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Información de Sesión', {
            'fields': ('ip_address', 'user_agent', 'login_time', 'logout_time', 'session_duration')
        }),
        ('Estado', {
            'fields': ('success', 'failure_reason')
        }),
    )
