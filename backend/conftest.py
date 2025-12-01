"""
Configuración de pytest para CacaoScan.

Este módulo centraliza fixtures y helpers comunes para tests del backend,
optimizando la creación de datos de prueba y reduciendo duplicación.
"""
import os
import sys
from pathlib import Path
from decimal import Decimal
from typing import Optional
import pytest

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


# ============================================================================
# FIXTURES CENTRALIZADOS - Fase 5: Optimización Final
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
