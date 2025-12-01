"""
Tests for scan views.
"""
from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)
from images_app.views.image.user.scan_views import ScanMeasureView
from api.services.analysis_service import AnalysisService
from api.services.base import ServiceResult, ValidationServiceError


class ScanMeasureViewTest(APITestCase):
    """Tests for ScanMeasureView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.view = ScanMeasureView()
    
    def _create_test_image(self, name='test_image.jpg'):
        """Create test image file."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            name,
            img_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_validate_image_file_present(self):
        """Test validation when image file is present."""
        request = Mock()
        request.FILES = {'image': self._create_test_image()}
        
        image_file, error_response = self.view._validate_image_file(request)
        
        self.assertIsNotNone(image_file)
        self.assertIsNone(error_response)
    
    def test_validate_image_file_missing(self):
        """Test validation when image file is missing."""
        request = Mock()
        request.FILES = {}
        
        image_file, error_response = self.view._validate_image_file(request)
        
        self.assertIsNone(image_file)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_calculate_confidence_level_high(self):
        """Test confidence level calculation (high)."""
        result = self.view._calculate_confidence_level(0.85)
        
        self.assertEqual(result, 'high')
    
    def test_calculate_confidence_level_medium(self):
        """Test confidence level calculation (medium)."""
        result = self.view._calculate_confidence_level(0.65)
        
        self.assertEqual(result, 'medium')
    
    def test_calculate_confidence_level_low(self):
        """Test confidence level calculation (low)."""
        result = self.view._calculate_confidence_level(0.5)
        
        self.assertEqual(result, 'low')
    
    def test_build_email_context(self):
        """Test building email context."""
        response_data = {
            'prediction_id': 123,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'alto_mm': 15.5,
            'ancho_mm': 12.3,
            'grosor_mm': 8.7,
            'peso_g': 1.2,
            'crop_url': 'http://example.com/crop.jpg',
            'debug': {'model_version': 'v1.0'}
        }
        
        context = self.view._build_email_context(response_data, self.user)
        
        self.assertIn('user_name', context)
        self.assertIn('confidence', context)
        self.assertIn('confidence_level', context)
        self.assertEqual(context['confidence_level'], 'high')
        self.assertEqual(context['alto_mm'], 15.5)
    
    @patch('images_app.views.image.user.scan_views.send_email_notification')
    def test_send_analysis_email_success(self, mock_send_email):
        """Test sending analysis email successfully."""
        mock_send_email.return_value = {'success': True}
        
        response_data = {
            'prediction_id': 123,
            'confidences': {'alto': 0.95, 'ancho': 0.92, 'grosor': 0.88, 'peso': 0.90},
            'alto_mm': 15.5,
            'ancho_mm': 12.3,
            'grosor_mm': 8.7,
            'peso_g': 1.2
        }
        
        self.view._send_analysis_email(self.user, response_data)
        
        mock_send_email.assert_called_once()
    
    @patch('images_app.views.image.user.scan_views.send_email_notification')
    def test_send_analysis_email_failure(self, mock_send_email):
        """Test sending analysis email with failure."""
        mock_send_email.return_value = {'success': False, 'error': 'Email error'}
        
        response_data = {
            'prediction_id': 123,
            'confidences': {'alto': 0.95, 'ancho': 0.92, 'grosor': 0.88, 'peso': 0.90},
            'alto_mm': 15.5
        }
        
        # Should not raise exception
        self.view._send_analysis_email(self.user, response_data)
    
    def test_map_error_to_status_code_validation(self):
        """Test error mapping for validation error."""
        error = ValidationServiceError('validation_error', 'File size too large', {'field': 'file_size'})
        result = Mock()
        result.error = error
        
        status_code = self.view._map_error_to_status_code(result)
        
        self.assertEqual(status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    
    def test_map_error_to_status_code_not_available(self):
        """Test error mapping for service unavailable."""
        error = Mock()
        error.error_code = 'service_error'
        error.message = 'Model not disponible'
        error.details = {}
        result = Mock()
        result.error = error
        
        status_code = self.view._map_error_to_status_code(result)
        
        self.assertEqual(status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
    
    def test_map_error_to_status_code_generic(self):
        """Test error mapping for generic error."""
        error = Mock()
        error.error_code = 'unknown_error'
        error.message = 'Some error'
        error.details = {}
        result = Mock()
        result.error = error
        
        status_code = self.view._map_error_to_status_code(result)
        
        self.assertEqual(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @patch('images_app.views.image.user.scan_views.AnalysisService')
    def test_post_success(self, mock_service_class):
        """Test successful POST request."""
        self.client.force_authenticate(user=self.user)
        
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_result = ServiceResult(
            success=True,
            data={
                'prediction_id': 123,
                'alto_mm': 15.5,
                'ancho_mm': 12.3,
                'grosor_mm': 8.7,
                'peso_g': 1.2,
                'confidences': {
                    'alto': 0.95,
                    'ancho': 0.92,
                    'grosor': 0.88,
                    'peso': 0.90
                }
            }
        )
        mock_service.process_image_with_segmentation.return_value = mock_result
        
        image = self._create_test_image()
        url = '/api/v1/scan/measure/'
        
        response = self.client.post(url, {'image': image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('alto_mm', response.data)
    
    def test_post_missing_image(self):
        """Test POST request without image."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/scan/measure/'
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_unauthenticated(self):
        """Test POST request without authentication."""
        image = self._create_test_image()
        url = '/api/v1/scan/measure/'
        
        response = self.client.post(url, {'image': image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('images_app.views.image.user.scan_views.AnalysisService')
    def test_post_service_error(self, mock_service_class):
        """Test POST request with service error."""
        self.client.force_authenticate(user=self.user)
        
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        error = ValidationServiceError('validation_error', 'Invalid image format', {})
        mock_result = ServiceResult(success=False, error=error)
        mock_service.process_image_with_segmentation.return_value = mock_result
        
        image = self._create_test_image()
        url = '/api/v1/scan/measure/'
        
        response = self.client.post(url, {'image': image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

