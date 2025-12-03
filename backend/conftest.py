"""
Configuración de pytest para CacaoScan.

Este módulo centraliza fixtures y helpers comunes para tests del backend,
optimizando la creación de datos de prueba y reduciendo duplicación.
"""
import os
import sys
import warnings
import django
from pathlib import Path
from decimal import Decimal
from typing import Optional
import pytest

# Force UTF-8 encoding for all operations before Django setup
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "UTF-8"
os.environ["PGCLIENTENCODING"] = "UTF8"

def clean_env_value(value):
    """Clean environment variable value to ensure UTF-8 encoding."""
    if not value:
        return value
    if isinstance(value, bytes):
        try:
            value = value.decode('utf-8', errors='replace')
        except Exception:
            value = value.decode('latin-1', errors='replace')
    if not isinstance(value, str):
        value = str(value)
    # Remove problematic bytes
    value_bytes = value.encode('utf-8', errors='replace')
    value_bytes = value_bytes.replace(b'\xf3', b'')
    value = value_bytes.decode('utf-8', errors='replace')
    return value

# Clean critical database environment variables before Django setup
_db_env_vars = [
    'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT',
    'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT',
    'POSTGRES_DB_TEST'
]
for var in _db_env_vars:
    if var in os.environ:
        os.environ[var] = clean_env_value(os.environ[var])

# Añadir el directorio raíz del proyecto al PYTHONPATH
# Esto permite importar 'cacaoscan.settings' cuando pytest se ejecuta desde la raíz
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configurar Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cacaoscan.settings")
django.setup()


def pytest_configure(config):
    """Configuración de pytest."""
    # Registrar marcadores personalizados
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    
    # Suprimir advertencias conocidas de librerías externas y Django
    # Estas advertencias no afectan la funcionalidad y son de librerías de terceros
    warnings.filterwarnings(
        "ignore",
        message=".*pkg_resources.declare_namespace.*",
        category=DeprecationWarning
    )
    warnings.filterwarnings(
        "ignore",
        message=".*load_module.*",
        category=DeprecationWarning
    )
    warnings.filterwarnings(
        "ignore",
        message=".*ast.NameConstant.*",
        category=DeprecationWarning
    )
    # Advertencias de Django 6.0 sobre CheckConstraint.check (migraciones antiguas)
    # RemovedInDjango60Warning es una categoría específica de Django
    # Intentar importar la categoría específica de Django
    try:
        from django.utils.deprecation import RemovedInDjango60Warning
        warnings.filterwarnings("ignore", category=RemovedInDjango60Warning)
    except (ImportError, AttributeError):
        # Si la versión de Django no tiene esta categoría, usar filtro por mensaje
        # Esto funciona para versiones anteriores de Django
        pass
    
    # Filtro adicional por mensaje para asegurar que se capturen todas las variantes
    # Este filtro funciona independientemente de la versión de Django
    warnings.filterwarnings(
        "ignore",
        message=".*CheckConstraint.check is deprecated.*",
    )
    warnings.filterwarnings(
        "ignore",
        message=".*RemovedInDjango60Warning.*",
    )
    # Filtro general para todas las advertencias de deprecación de Django relacionadas con constraints
    warnings.filterwarnings(
        "ignore",
        message=".*CheckConstraint.*",
        module=".*migrations.*",
    )
    # Advertencia sobre directorio staticfiles (se crea automáticamente si es necesario)
    warnings.filterwarnings(
        "ignore",
        message=".*No directory at.*staticfiles.*",
        category=UserWarning
    )
    
    # Crear directorio staticfiles si no existe (para evitar UserWarning)
    # Esto debe hacerse después de que Django esté configurado
    try:
        from django.conf import settings
        static_root = Path(settings.STATIC_ROOT)
        if not static_root.exists():
            static_root.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Si Django aún no está completamente configurado, ignorar
        pass


# ============================================================================
# FIXTURES CENTRALIZADOS
# ============================================================================

@pytest.fixture
def test_user(db):
    """
    Fixture para crear un usuario de prueba estándar.
    
    Returns:
        User: Usuario de prueba con credenciales estándar
    """
    from django.contrib.auth.models import User
    from api.tests.test_constants import (
        TEST_USER_USERNAME,
        TEST_USER_EMAIL,
        TEST_USER_PASSWORD,
        TEST_USER_FIRST_NAME,
        TEST_USER_LAST_NAME
    )
    
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD,
        first_name=TEST_USER_FIRST_NAME,
        last_name=TEST_USER_LAST_NAME,
        is_active=True
    )


@pytest.fixture
def test_admin_user(db):
    """
    Fixture para crear un usuario administrador de prueba.
    
    Returns:
        User: Usuario administrador de prueba
    """
    from django.contrib.auth.models import User
    from api.tests.test_constants import (
        TEST_ADMIN_USERNAME,
        TEST_ADMIN_EMAIL,
        TEST_ADMIN_PASSWORD,
        TEST_ADMIN_FIRST_NAME,
        TEST_ADMIN_LAST_NAME
    )
    
    return User.objects.create_superuser(
        username=TEST_ADMIN_USERNAME,
        email=TEST_ADMIN_EMAIL,
        password=TEST_ADMIN_PASSWORD,
        first_name=TEST_ADMIN_FIRST_NAME,
        last_name=TEST_ADMIN_LAST_NAME
    )


@pytest.fixture
def test_other_user(db):
    """
    Fixture para crear un usuario adicional de prueba.
    
    Returns:
        User: Usuario adicional de prueba
    """
    from django.contrib.auth.models import User
    from api.tests.test_constants import (
        TEST_OTHER_USER_USERNAME,
        TEST_OTHER_USER_EMAIL,
        TEST_OTHER_USER_PASSWORD
    )
    
    return User.objects.create_user(
        username=TEST_OTHER_USER_USERNAME,
        email=TEST_OTHER_USER_EMAIL,
        password=TEST_OTHER_USER_PASSWORD,
        is_active=True
    )


@pytest.fixture
def test_finca(db, test_user):
    """
    Fixture para crear una finca de prueba.
    
    Args:
        test_user: Usuario propietario de la finca
        
    Returns:
        Finca: Finca de prueba
    """
    from api.models import Finca
    
    return Finca.objects.create(
        nombre='Finca Test',
        propietario=test_user,
        area_total=Decimal('20.0'),
        ubicacion='Test Location',
        descripcion='Test farm description',
        coordenadas_lat=Decimal('0.0'),
        coordenadas_lng=Decimal('0.0')
    )


@pytest.fixture
def test_lote(db, test_finca):
    """
    Fixture para crear un lote de prueba.
    
    Args:
        test_finca: Finca a la que pertenece el lote
        
    Returns:
        Lote: Lote de prueba
    """
    from api.models import Lote
    
    return Lote.objects.create(
        finca=test_finca,
        nombre='Lote Test',
        area=Decimal('5.0'),
        variedad='CCN-51',
        edad_plantas=5,
        descripcion='Test lot description'
    )


@pytest.fixture
def test_cacao_image(db, test_user):
    """
    Fixture para crear una imagen de cacao de prueba.
    
    Args:
        test_user: Usuario propietario de la imagen
        
    Returns:
        CacaoImage: Imagen de cacao de prueba
    """
    from api.models import CacaoImage
    
    return CacaoImage.objects.create(
        user=test_user,
        filename='test_image.jpg',
        upload_status='completed',
        image_width=800,
        image_height=600,
        file_size=1024
    )


@pytest.fixture
def test_user_profile(db, test_user):
    """
    Fixture para crear un perfil de usuario de prueba.
    
    Args:
        test_user: Usuario asociado al perfil
        
    Returns:
        UserProfile: Perfil de usuario de prueba
    """
    from auth_app.models import UserProfile
    
    return UserProfile.objects.create(
        user=test_user,
        phone_number='1234567890',
        region='Test Region',
        municipality='Test Municipality'
    )


@pytest.fixture
def test_email_verification_token(db, test_user):
    """
    Fixture para crear un token de verificación de email de prueba.
    
    Args:
        test_user: Usuario asociado al token
        
    Returns:
        EmailVerificationToken: Token de verificación de prueba
    """
    from api.models import EmailVerificationToken
    
    return EmailVerificationToken.create_for_user(test_user)


# ============================================================================
# HELPERS PARA CREACIÓN DE DATOS DE PRUEBA
# ============================================================================

def create_test_user(
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: bool = True,
    is_superuser: bool = False
):
    """
    Helper para crear un usuario de prueba con parámetros personalizados.
    
    Args:
        username: Nombre de usuario (opcional)
        email: Email del usuario (opcional)
        password: Contraseña del usuario (opcional)
        is_active: Si el usuario está activo
        is_superuser: Si el usuario es superusuario
        
    Returns:
        User: Usuario creado
    """
    from django.contrib.auth.models import User
    from api.tests.test_constants import (
        TEST_USER_USERNAME,
        TEST_USER_EMAIL,
        TEST_USER_PASSWORD
    )
    
    if username is None:
        username = TEST_USER_USERNAME
    if email is None:
        email = TEST_USER_EMAIL
    if password is None:
        password = TEST_USER_PASSWORD
    
    if is_superuser:
        return User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
    
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_active=is_active
    )


def create_test_finca(
    user,
    nombre: str = 'Finca Test',
    area_total: Decimal = Decimal('20.0'),
    ubicacion: str = 'Test Location'
):
    """
    Helper para crear una finca de prueba con parámetros personalizados.
    
    Args:
        user: Usuario propietario de la finca
        nombre: Nombre de la finca
        area_total: Área total de la finca
        ubicacion: Ubicación de la finca
        
    Returns:
        Finca: Finca creada
    """
    from api.models import Finca
    
    return Finca.objects.create(
        nombre=nombre,
        propietario=user,
        area_total=area_total,
        ubicacion=ubicacion,
        descripcion='Test farm description',
        coordenadas_lat=Decimal('0.0'),
        coordenadas_lng=Decimal('0.0')
    )


def create_test_lote(
    finca,
    nombre: str = 'Lote Test',
    area: Decimal = Decimal('5.0'),
    variedad: str = 'CCN-51'
):
    """
    Helper para crear un lote de prueba con parámetros personalizados.
    
    Args:
        finca: Finca a la que pertenece el lote
        nombre: Nombre del lote
        area: Área del lote
        variedad: Variedad del lote
        
    Returns:
        Lote: Lote creado
    """
    from api.models import Lote
    
    return Lote.objects.create(
        finca=finca,
        nombre=nombre,
        area=area,
        variedad=variedad,
        edad_plantas=5,
        descripcion='Test lot description'
    )


def create_test_cacao_image(
    user,
    filename: str = 'test_image.jpg',
    upload_status: str = 'completed',
    image_width: int = 800,
    image_height: int = 600
):
    """
    Helper para crear una imagen de cacao de prueba con parámetros personalizados.
    
    Args:
        user: Usuario propietario de la imagen
        filename: Nombre del archivo
        upload_status: Estado de carga
        image_width: Ancho de la imagen
        image_height: Alto de la imagen
        
    Returns:
        CacaoImage: Imagen creada
    """
    from api.models import CacaoImage
    
    return CacaoImage.objects.create(
        user=user,
        filename=filename,
        upload_status=upload_status,
        image_width=image_width,
        image_height=image_height,
        file_size=1024
    )
