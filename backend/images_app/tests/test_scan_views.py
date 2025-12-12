"""
Tests for scan views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from images_app.views.image.user.scan_views import ScanMeasureView


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


@pytest.fixture
def user(db):
    """Create test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.fixture
def image_file():
    """Create test image file."""
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'fake image content',
        content_type='image/jpeg'
    )


@pytest.fixture
def view():
    """Create view instance."""
    return ScanMeasureView()


def test_validate_image_file_success(view, request_factory, image_file):
    """Test _validate_image_file with valid file."""
    from rest_framework.test import APIRequestFactory
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    api_factory = APIRequestFactory()
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    request = api_factory.post('/api/scan/', {'image': image_file}, format='multipart')
    force_authenticate(request, user=user)
    
    file, error = view._validate_image_file(request)
    
    # Compare file attributes instead of object identity
    assert file is not None
    assert file.name == image_file.name
    assert error is None


def test_validate_image_file_missing(view, request_factory):
    """Test _validate_image_file without file."""
    from rest_framework.test import APIRequestFactory
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    api_factory = APIRequestFactory()
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    request = api_factory.post('/api/scan/', {}, format='multipart')
    force_authenticate(request, user=user)
    
    file, error = view._validate_image_file(request)
    
    assert file is None
    assert error is not None
    assert error.status_code == status.HTTP_400_BAD_REQUEST


def test_calculate_confidence_level_high(view):
    """Test _calculate_confidence_level with high confidence."""
    assert view._calculate_confidence_level(0.9) == 'high'
    assert view._calculate_confidence_level(0.8) == 'high'


def test_calculate_confidence_level_medium(view):
    """Test _calculate_confidence_level with medium confidence."""
    assert view._calculate_confidence_level(0.7) == 'medium'
    assert view._calculate_confidence_level(0.6) == 'medium'


def test_calculate_confidence_level_low(view):
    """Test _calculate_confidence_level with low confidence."""
    assert view._calculate_confidence_level(0.5) == 'low'
    assert view._calculate_confidence_level(0.3) == 'low'


def test_build_email_context(view, user):
    """Test _build_email_context."""
    response_data = {
        'prediction_id': 123,
        'confidences': {
            'alto': 0.9,
            'ancho': 0.8,
            'grosor': 0.7,
            'peso': 0.85
        },
        'alto_mm': 25.5,
        'ancho_mm': 20.3,
        'grosor_mm': 15.2,
        'peso_g': 8.5,
        'debug': {'model_version': 'v1.0'},
        'crop_url': 'http://example.com/crop.jpg'
    }
    
    context = view._build_email_context(response_data, user)
    
    assert context['user_name'] == user.username
    assert context['user_email'] == user.email
    assert context['analysis_id'] == 123
    assert context['alto_mm'] == 25.5
    assert 'confidence' in context


@patch('api.services.email.email_service.send_email_notification')
def test_send_analysis_email_success(mock_send_email, view, user):
    """Test _send_analysis_email with success."""
    mock_send_email.return_value = {'success': True}
    
    response_data = {
        'confidences': {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.85},
        'alto_mm': 25.5,
        'ancho_mm': 20.3,
        'grosor_mm': 15.2,
        'peso_g': 8.5
    }
    
    view._send_analysis_email(user, response_data)
    
    mock_send_email.assert_called_once()


@patch('api.services.email.email_service.send_email_notification')
def test_send_analysis_email_failure(mock_send_email, view, user):
    """Test _send_analysis_email with failure."""
    mock_send_email.return_value = {'success': False, 'error': 'Email error'}
    
    response_data = {
        'confidences': {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.85},
        'alto_mm': 25.5,
        'ancho_mm': 20.3,
        'grosor_mm': 15.2,
        'peso_g': 8.5
    }
    
    # Should not raise
    view._send_analysis_email(user, response_data)


def test_map_error_to_status_code_validation(view):
    """Test _map_error_to_status_code for validation error."""
    result = Mock()
    result.error = Mock()
    result.error.error_code = 'validation_error'
    result.error.details = {'field': 'file_size'}
    
    status_code = view._map_error_to_status_code(result)
    
    assert status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


def test_map_error_to_status_code_not_available(view):
    """Test _map_error_to_status_code for service unavailable."""
    result = Mock()
    result.error = Mock()
    result.error.error_code = 'other'
    result.error.message = 'Service not available'
    
    status_code = view._map_error_to_status_code(result)
    
    assert status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_map_error_to_status_code_default(view):
    """Test _map_error_to_status_code default."""
    result = Mock()
    result.error = Mock()
    result.error.error_code = 'other'
    result.error.message = 'Some error'
    
    status_code = view._map_error_to_status_code(result)
    
    assert status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@patch('images_app.views.image.user.scan_views.AnalysisService')
def test_post_success(mock_service_class, view, user, image_file):
    """Test POST with successful analysis."""
    from rest_framework.test import APIRequestFactory
    from rest_framework.test import force_authenticate
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_service.process_image_with_segmentation.return_value = Mock(
        success=True,
        data={
            'alto_mm': 25.5,
            'ancho_mm': 20.3,
            'grosor_mm': 15.2,
            'peso_g': 8.5,
            'confidences': {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.85},
            'crop_url': 'http://example.com/crop.jpg',
            'debug': {
                'segmented': True,
                'yolo_conf': 0.95,
                'latency_ms': 150,
                'models_version': 'v1.0',
                'device': 'cpu',
                'total_time_s': 0.3
            },
            'saved_to_database': True
        }
    )
    
    api_factory = APIRequestFactory()
    request = api_factory.post('/api/scan/', {'image': image_file}, format='multipart')
    force_authenticate(request, user=user)
    # Ensure request.user is set (force_authenticate should do this, but set it explicitly)
    request.user = user
    
    with patch.object(view, '_send_analysis_email'):
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK


@patch('images_app.views.image.user.scan_views.AnalysisService')
def test_post_no_image(mock_service_class, view, user):
    """Test POST without image file."""
    from rest_framework.test import APIRequestFactory
    from rest_framework.test import force_authenticate
    
    api_factory = APIRequestFactory()
    request = api_factory.post('/api/scan/', {}, format='multipart')
    force_authenticate(request, user=user)
    
    response = view.post(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch('images_app.views.image.user.scan_views.AnalysisService')
def test_post_service_error(mock_service_class, view, user, image_file):
    """Test POST with service error."""
    from rest_framework.test import APIRequestFactory
    from rest_framework.test import force_authenticate
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_service.process_image_with_segmentation.return_value = Mock(
        success=False,
        error=Mock(
            message='Service error',
            error_code='service_error',
            details={}
        )
    )
    
    api_factory = APIRequestFactory()
    request = api_factory.post('/api/scan/', {'image': image_file}, format='multipart')
    force_authenticate(request, user=user)
    # Ensure request.user is set
    request.user = user
    
    response = view.post(request)
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


