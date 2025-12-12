"""
Inicialización de Celery para CacaoScan.
Solo se inicializa si USE_CELERY_REDIS está habilitado.
"""
import os

# Solo inicializar Celery si está habilitado
USE_CELERY_REDIS = os.environ.get('USE_CELERY_REDIS', 'True').lower() == 'true'

if USE_CELERY_REDIS:
    try:
        from .celery import app as celery_app
        __all__ = ('celery_app',)
    except Exception as e:
        # Si hay error al inicializar Celery, continuar sin él
        import warnings
        warnings.warn(f"Error inicializando Celery: {e}. Continuando sin Celery.")
        celery_app = None
        __all__ = ()
else:
    celery_app = None
    __all__ = ()