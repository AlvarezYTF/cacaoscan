from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
    verbose_name = 'Autenticación'
    
    def ready(self):
        """Ejecutado cuando la app está lista."""
        try:
            import auth_app.signals
        except ImportError:
            pass
