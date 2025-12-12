"""
Pytest configuration and fixtures for CacaoScan backend tests.
"""
import os
import django

# Configure Django settings before importing Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from unittest.mock import Mock, MagicMock
import tempfile
from pathlib import Path
import uuid

# Test passwords from environment variables with safe defaults for testing
# These are test-only credentials and not used in production
TEST_USER_PASSWORD: str = os.getenv('TEST_USER_PASSWORD', 'testpass123')
TEST_ADMIN_PASSWORD: str = os.getenv('TEST_ADMIN_PASSWORD', 'adminpass123')
TEST_STAFF_PASSWORD: str = os.getenv('TEST_STAFF_PASSWORD', 'staffpass123')


def _generate_unique_username(prefix: str = 'testuser') -> str:
    """Generate a unique username using UUID."""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}"


def _generate_unique_email(prefix: str = 'test') -> str:
    """Generate a unique email using UUID."""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}@example.com"


def create_test_user(username_prefix: str = 'testuser', **kwargs):
    """
    Helper function to create a test user with unique username and email.
    
    Args:
        username_prefix: Prefix for username (default: 'testuser')
        **kwargs: Additional arguments to pass to create_user
    
    Returns:
        User instance with unique username and email
    """
    unique_id = str(uuid.uuid4())[:8]
    username = kwargs.pop('username', f"{username_prefix}_{unique_id}")
    email = kwargs.pop('email', f"test_{unique_id}@example.com")
    password = kwargs.pop('password', TEST_USER_PASSWORD)
    
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        **kwargs
    )


def create_test_admin_user(username_prefix: str = 'admin', **kwargs):
    """
    Helper function to create a test admin user with unique username and email.
    
    Args:
        username_prefix: Prefix for username (default: 'admin')
        **kwargs: Additional arguments to pass to create_superuser
    
    Returns:
        User instance with unique username and email
    """
    unique_id = str(uuid.uuid4())[:8]
    username = kwargs.pop('username', f"{username_prefix}_{unique_id}")
    email = kwargs.pop('email', f"admin_{unique_id}@example.com")
    password = kwargs.pop('password', TEST_ADMIN_PASSWORD)
    
    return User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        **kwargs
    )


def create_test_staff_user(username_prefix: str = 'staff', **kwargs):
    """
    Helper function to create a test staff user with unique username and email.
    
    Args:
        username_prefix: Prefix for username (default: 'staff')
        **kwargs: Additional arguments to pass to create_user
    
    Returns:
        User instance with unique username and email
    """
    unique_id = str(uuid.uuid4())[:8]
    username = kwargs.pop('username', f"{username_prefix}_{unique_id}")
    email = kwargs.pop('email', f"staff_{unique_id}@example.com")
    password = kwargs.pop('password', TEST_STAFF_PASSWORD)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        **kwargs
    )
    user.is_staff = True
    user.save()
    return user


@pytest.fixture(scope='function')
def user(db):
    """Create a regular user for testing with unique username and email."""
    return User.objects.create_user(
        username=_generate_unique_username('testuser'),
        email=_generate_unique_email('test'),
        password=TEST_USER_PASSWORD,
        first_name='Test',
        last_name='User'
    )


@pytest.fixture(scope='function')
def login_user(db):
    """Create a user for login tests with unique username and email."""
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password=TEST_USER_PASSWORD,
        first_name='Test',
        last_name='User'
    )
    # Store original username pattern for backward compatibility in tests
    user._test_username = f'testuser_{unique_id}'
    return user


@pytest.fixture(scope='function')
def admin_user(db):
    """Create an admin user for testing with unique username and email."""
    return User.objects.create_superuser(
        username=_generate_unique_username('admin'),
        email=_generate_unique_email('admin'),
        password=TEST_ADMIN_PASSWORD,
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture(scope='function')
def staff_user(db):
    """Create a staff user for testing with unique username and email."""
    user = User.objects.create_user(
        username=_generate_unique_username('staff'),
        email=_generate_unique_email('staff'),
        password=TEST_STAFF_PASSWORD,
        first_name='Staff',
        last_name='User'
    )
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def request_factory():
    """Django request factory."""
    return RequestFactory()


@pytest.fixture
def authenticated_request(request_factory, user):
    """Create an authenticated request."""
    request = request_factory.get('/')
    request.user = user
    return request


@pytest.fixture
def admin_request(request_factory, admin_user):
    """Create an admin authenticated request."""
    request = request_factory.get('/')
    request.user = admin_user
    return request


@pytest.fixture
def mock_image_file():
    """Create a mock image file for testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_io.read(),
        content_type='image/jpeg'
    )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    import shutil
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_predictor():
    """Create a mock ML predictor."""
    predictor = Mock()
    predictor.models_loaded = True
    predictor.predict.return_value = {
        'alto_mm': 25.5,
        'ancho_mm': 20.3,
        'grosor_mm': 15.2,
        'peso_g': 8.5,
        'confidences': {'alto': 0.95, 'ancho': 0.92, 'grosor': 0.88, 'peso': 0.90},
        'processing_time_ms': 150
    }
    return predictor


@pytest.fixture
def mock_service_result():
    """Create a mock service result."""
    from api.services.base import ServiceResult
    return ServiceResult.success(data={'test': 'data'}, message='Success')


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


@pytest.fixture(autouse=True)
def clean_db(db):
    """
    Ensure database is clean between tests.
    This fixture runs automatically for all tests.
    """
    # The db fixture already handles transaction rollback
    # This is just for explicit documentation
    yield
    # Cleanup happens automatically via transaction rollback


@pytest.fixture(scope='function')
def departamento(db):
    """Create a test Departamento."""
    from catalogos.models import Departamento
    return Departamento.objects.create(
        codigo='TEST',
        nombre='Test Departamento'
    )


@pytest.fixture(scope='function')
def municipio(db, departamento):
    """Create a test Municipio."""
    from catalogos.models import Municipio
    return Municipio.objects.create(
        departamento=departamento,
        codigo='TEST',
        nombre='Test Municipio'
    )


@pytest.fixture(scope='function')
def tema_tipo_notificacion(db):
    """Create TEMA_TIPO_NOTIFICACION theme."""
    from catalogos.models import Tema
    tema, _ = Tema.objects.get_or_create(
        codigo='TEMA_TIPO_NOTIFICACION',
        defaults={
            'nombre': 'Tipo de Notificación',
            'descripcion': 'Tipos de notificaciones del sistema'
        }
    )
    return tema


@pytest.fixture(scope='function')
def parametro_tipo_notificacion_info(db, tema_tipo_notificacion):
    """Create INFO notification type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_notificacion,
        codigo='INFO',
        defaults={
            'nombre': 'Información',
            'descripcion': 'Notificación informativa'
        }
    )
    return parametro


@pytest.fixture(scope='function')
def parametro_tipo_notificacion_success(db, tema_tipo_notificacion):
    """Create SUCCESS notification type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_notificacion,
        codigo='SUCCESS',
        defaults={
            'nombre': 'Éxito',
            'descripcion': 'Notificación de éxito'
        }
    )
    return parametro


@pytest.fixture(scope='function')
def parametro_tipo_notificacion_warning(db, tema_tipo_notificacion):
    """Create WARNING notification type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_notificacion,
        codigo='WARNING',
        defaults={
            'nombre': 'Advertencia',
            'descripcion': 'Notificación de advertencia'
        }
    )
    return parametro


@pytest.fixture(scope='function')
def parametro_tipo_notificacion_error(db, tema_tipo_notificacion):
    """Create ERROR notification type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_notificacion,
        codigo='ERROR',
        defaults={
            'nombre': 'Error',
            'descripcion': 'Notificación de error'
        }
    )
    return parametro


@pytest.fixture(scope='function')
def parametro_tipo_notificacion_welcome(db, tema_tipo_notificacion):
    """Create WELCOME notification type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_notificacion,
        codigo='WELCOME',
        defaults={
            'nombre': 'Bienvenida',
            'descripcion': 'Notificación de bienvenida'
        }
    )
    return parametro


@pytest.fixture(scope='function')
def tema_tipo_archivo(db):
    """Create TEMA_TIPO_ARCHIVO theme."""
    from catalogos.models import Tema
    tema, _ = Tema.objects.get_or_create(
        codigo='TEMA_TIPO_ARCHIVO',
        defaults={
            'nombre': 'Tipo de Archivo',
            'descripcion': 'Tipos de archivos del sistema'
        }
    )
    return tema


@pytest.fixture(scope='function')
def parametro_tipo_archivo_jpeg(db, tema_tipo_archivo):
    """Create image/jpeg file type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_archivo,
        codigo='IMAGE_JPEG',
        defaults={
            'nombre': 'JPEG',
            'descripcion': 'Imagen JPEG',
            'metadata': {'mime_type': 'image/jpeg'}
        }
    )
    return parametro


@pytest.fixture(scope='function')
def tema_tipo_reporte(db):
    """Create TEMA_TIPO_REPORTE theme."""
    from catalogos.models import Tema
    tema, _ = Tema.objects.get_or_create(
        codigo='TEMA_TIPO_REPORTE',
        defaults={
            'nombre': 'Tipo de Reporte',
            'descripcion': 'Tipos de reportes del sistema'
        }
    )
    return tema


@pytest.fixture(scope='function')
def parametro_tipo_reporte_analisis(db, tema_tipo_reporte):
    """Create analisis report type parameter."""
    from catalogos.models import Parametro
    parametro, _ = Parametro.objects.get_or_create(
        tema=tema_tipo_reporte,
        codigo='ANALISIS',
        defaults={
            'nombre': 'Análisis',
            'descripcion': 'Reporte de análisis'
        }
    )
    return parametro