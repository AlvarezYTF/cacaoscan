from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """Importar signals cuando la app esté lista."""
        # Temporarily disabled to avoid import errors
        # import api.signals
        pass


