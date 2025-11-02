from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
    verbose_name = 'AutenticaciÃ³n'
    
    def ready(self):
        """Ejecutado cuando la app estÃ¡ lista."""
        try:
            import auth_app.signals
        except ImportError:
            pass


