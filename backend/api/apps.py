from django.apps import AppConfig
from django.conf import settings


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """Importar signals cuando la app esté lista."""
        # No ejecutar signals en modo test
        if getattr(settings, "TESTING", False):
            return
        
        # Importar signals solo si no estamos en modo test
        import api.signals


