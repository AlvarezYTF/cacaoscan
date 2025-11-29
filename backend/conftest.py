"""
Configuración de pytest para CacaoScan.
"""
import os
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

try:
    import django
    django.setup()
except SyntaxError as e:
    # Error de sintaxis - mostrar información detallada
    import warnings
    warnings.warn(
        f"Error de sintaxis en settings.py: {e}\n"
        f"Archivo: {e.filename}, Línea: {e.lineno}\n"
        f"Texto: {e.text}",
        category=UserWarning
    )
    raise  # Re-raise para que pytest muestre el error completo
except Exception as e:
    # Otros errores - solo advertir, pytest intentará configurar Django de nuevo
    import warnings
    warnings.warn(f"Error configurando Django en conftest: {e}", category=UserWarning)


def pytest_configure(config):
    """Configuración de pytest."""
    import django
    from django.conf import settings
    
    # Registrar marcadores personalizados explícitamente
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    
    if not settings.configured:
        try:
            django.setup()
        except Exception as e:
            import warnings
            warnings.warn(f"Error en pytest_configure al configurar Django: {e}")
