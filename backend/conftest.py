"""
Configuración de pytest para CacaoScan.
"""
import os
import sys
import django
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()


def pytest_configure():
    """Configuración de pytest."""
    import django
    from django.conf import settings
    
    if not settings.configured:
        django.setup()
