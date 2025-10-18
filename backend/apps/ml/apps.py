"""
Configuración de la aplicación ML para CacaoScan.
"""

from django.apps import AppConfig


class MLConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ml'
    verbose_name = 'Machine Learning'
    
    def ready(self):
        """Inicialización de la aplicación ML."""
        # Importar señales si es necesario
        pass
