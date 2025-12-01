"""
Tests for ML calibration views.
Covers CalibrationStatusView, CalibrationView, and CalibratedScanMeasureView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
import io

from api.views.ml.calibration_views import (
    CalibrationStatusView,
    CalibrationView,
    CalibratedScanMeasureView
)


@pytest.fixture
def authenticated_user(db):
    """Create authenticated user for tests."""
    return User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123'
    )


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def sample_image():
    """Create a sample image file for testing."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return SimpleUploadedFile(
        "test_image.jpg",
        img_bytes.read(),
        content_type="image/jpeg"
    )


@pytest.mark.django_db
class TestCalibrationStatusView:
    """Tests for CalibrationStatusView."""
    
    def test_calibration_status_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/calibration/status/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_calibration_status_success(self, mock_get_predictor, api_client, authenticated_user):
        """Test getting calibration status successfully."""
        mock_predictor = MagicMock()
        mock_predictor.get_calibration_status.return_value = {
            'calibration_enabled': True,
            'calibration_loaded': True,
            'pixels_per_mm': 10.5,
            'method': 'coin_detection',
            'confidence': 0.95
        }
        mock_get_predictor.return_value = mock_predictor
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['calibration_enabled'] is True
        assert 'pixels_per_mm' in response.data
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_calibration_status_exception(self, mock_get_predictor, api_client, authenticated_user):
        """Test exception handling in calibration status."""
        mock_get_predictor.side_effect = Exception("ML service error")
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


@pytest.mark.django_db
class TestCalibrationView:
    """Tests for CalibrationView."""
    
    def test_calibration_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot calibrate."""
        response = api_client.post('/api/v1/ml/calibration/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_calibration_missing_image(self, api_client, authenticated_user):
        """Test calibration without image file."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {}
        request.data = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'No se proporcionó archivo' in response.data['error']
    
    def test_calibration_invalid_file_type(self, api_client, authenticated_user):
        """Test calibration with invalid file type."""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': invalid_file}
        request.data = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Tipo de archivo no válido' in response.data['error']
    
    def test_calibration_file_too_large(self, api_client, authenticated_user):
        """Test calibration with file too large."""
        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (21 * 1024 * 1024),  # 21MB
            content_type="image/jpeg"
        )
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': large_file}
        request.data = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'demasiado grande' in response.data['error']
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    @patch('api.views.ml.calibration_views.CalibrationMethod')
    def test_calibration_success(self, mock_calibration_method, mock_get_predictor, 
                                 api_client, authenticated_user, sample_image):
        """Test calibration successfully."""
        mock_predictor = MagicMock()
        mock_predictor.calibrate_image.return_value = {
            'success': True,
            'pixels_per_mm': 10.5,
            'confidence': 0.95,
            'method': 'coin_detection',
            'reference_object': 'COIN_1000_COP'
        }
        mock_get_predictor.return_value = mock_predictor
        
        mock_method = MagicMock()
        mock_calibration_method.return_value = mock_method
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        request.data = {
            'method': 'coin_detection',
            'reference_object': 'COIN_1000_COP'
        }
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'pixels_per_mm' in response.data
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_calibration_invalid_method(self, mock_get_predictor, api_client, authenticated_user, sample_image):
        """Test calibration with invalid method."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        request.data = {'method': 'invalid_method'}
        
        with patch('api.views.ml.calibration_views.CalibrationMethod') as mock_method:
            mock_method.side_effect = ValueError("Invalid method")
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Método de calibración no válido' in response.data['error']
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_calibration_failure(self, mock_get_predictor, api_client, authenticated_user, sample_image):
        """Test calibration failure."""
        mock_predictor = MagicMock()
        mock_predictor.calibrate_image.return_value = {
            'success': False,
            'error': 'Could not detect reference object'
        }
        mock_get_predictor.return_value = mock_predictor
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibrationView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        request.data = {'method': 'coin_detection'}
        
        with patch('api.views.ml.calibration_views.CalibrationMethod'):
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'error' in response.data


@pytest.mark.django_db
class TestCalibratedScanMeasureView:
    """Tests for CalibratedScanMeasureView."""
    
    def test_scan_measure_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot scan."""
        response = api_client.post('/api/v1/ml/calibration/scan/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_scan_measure_missing_image(self, api_client, authenticated_user):
        """Test scan measure without image file."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibratedScanMeasureView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_scan_measure_models_not_loaded(self, mock_get_predictor, api_client, authenticated_user, sample_image):
        """Test scan measure when models are not loaded."""
        mock_predictor = MagicMock()
        mock_predictor.models_loaded = False
        mock_predictor.load_artifacts.return_value = False
        mock_get_predictor.return_value = mock_predictor
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibratedScanMeasureView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert 'Error cargando modelos' in response.data['error']
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_scan_measure_success(self, mock_get_predictor, api_client, authenticated_user, sample_image):
        """Test scan measure successfully."""
        mock_predictor = MagicMock()
        mock_predictor.models_loaded = True
        mock_predictor.predict.return_value = {
            'success': True,
            'predictions': {
                'alto_mm': 22.5,
                'ancho_mm': 10.2,
                'grosor_mm': 16.3,
                'peso_g': 1.72
            },
            'confidences': {
                'confidence_alto': 0.92,
                'confidence_ancho': 0.88
            },
            'calibration_info': {
                'pixels_per_mm': 10.5
            },
            'processing_time_ms': 1250,
            'crop_url': '/media/crops/test.jpg',
            'model_version': 'v2.0'
        }
        mock_get_predictor.return_value = mock_predictor
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibratedScanMeasureView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'predictions' in response.data
        assert response.data['predictions']['alto_mm'] == 22.5
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_scan_measure_prediction_failure(self, mock_get_predictor, api_client, authenticated_user, sample_image):
        """Test scan measure when prediction fails."""
        mock_predictor = MagicMock()
        mock_predictor.models_loaded = True
        mock_predictor.predict.return_value = {
            'success': False,
            'error': 'Segmentation failed'
        }
        mock_get_predictor.return_value = mock_predictor
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibratedScanMeasureView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
    
    @patch('api.views.ml.calibration_views.get_calibrated_predictor')
    def test_scan_measure_exception(self, mock_get_predictor, api_client, authenticated_user, sample_image):
        """Test exception handling in scan measure."""
        mock_get_predictor.side_effect = Exception("ML service error")
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = CalibratedScanMeasureView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'image': sample_image}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

