"""
Alias para backend.settings que importa desde cacaoscan.settings.
Esto permite usar 'backend.settings' como DJANGO_SETTINGS_MODULE.
"""
# Importar desde el módulo cacaoscan.settings relativo dentro de backend
from .cacaoscan.settings import *  # noqa: F401, F403
