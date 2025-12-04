"""
Pytest configuration and fixtures for CacaoScan backend tests.
"""
import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from unittest.mock import Mock, MagicMock
import tempfile
import os
from pathlib import Path


@pytest.fixture
def user():
    """Create a regular user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def staff_user():
    """Create a staff user for testing."""
    user = User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='staffpass123',
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

