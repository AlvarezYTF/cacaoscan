"""
Configuración de Celery para CacaoScan.
Solo se inicializa si USE_CELERY_REDIS está habilitado.
"""
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

# Verificar si Celery está habilitado antes de inicializar
USE_CELERY_REDIS = os.environ.get('USE_CELERY_REDIS', 'True').lower() == 'true'

if USE_CELERY_REDIS:
    app = Celery('cacaoscan')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
    
    @app.task(bind=True, ignore_result=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
else:
    # Crear un objeto dummy para evitar errores de importación
    app = None

