"""
Tests for Images App user views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date

from api.models import CacaoImage, CacaoPrediction, Finca, Lote
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
    TEST_OTHER_USER_USERNAME,
)


class ScanMeasureViewTest(APITestCase):
    """Tests for ScanMeasureView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('scan-measure')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def _create_test_image_file(self):
        """Create a test image file."""
        return SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
    
    @patch('images_app.views.image.user.scan_views.AnalysisService')
    def test_scan_measure_success(self, mock_analysis_service):
        """Test successful image scan."""
        mock_service_instance = Mock()
        mock_service_instance.process_image_with_segmentation.return_value = Mock(
            success=True,
            data={
                'prediction_id': 1,
                'alto_mm': 25.5,
                'ancho_mm': 15.3,
                'grosor_mm': 8.2,
                'peso_g': 1.5,
                'confidences': {
                    'alto': 0.9,
                    'ancho': 0.85,
                    'grosor': 0.8,
                    'peso': 0.75
                },
                'debug': {'model_version': 'v1.0'},
                'crop_url': 'http://example.com/crop.jpg'
            }
        )
        mock_analysis_service.return_value = mock_service_instance
        
        image_file = self._create_test_image_file()
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(
            self.url,
            {'image': image_file},
            format='multipart',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('alto_mm', response.data)
        self.assertIn('ancho_mm', response.data)
        self.assertIn('peso_g', response.data)
    
    def test_scan_measure_missing_image(self):
        """Test scan measure without image file."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(
            self.url,
            {},
            format='multipart',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_scan_measure_unauthenticated(self):
        """Test scan measure without authentication."""
        image_file = self._create_test_image_file()
        
        response = self.client.post(
            self.url,
            {'image': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('images_app.views.image.user.scan_views.AnalysisService')
    def test_scan_measure_validation_error(self, mock_analysis_service):
        """Test scan measure with validation error."""
        mock_service_instance = Mock()
        mock_service_instance.process_image_with_segmentation.return_value = Mock(
            success=False,
            error=Mock(
                error_code='validation_error',
                message='File size too large',
                details={'field': 'file_size'}
            )
        )
        mock_analysis_service.return_value = mock_service_instance
        
        image_file = self._create_test_image_file()
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(
            self.url,
            {'image': image_file},
            format='multipart',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertIn('error', response.data)
    
    @patch('images_app.views.image.user.scan_views.AnalysisService')
    def test_scan_measure_service_unavailable(self, mock_analysis_service):
        """Test scan measure when service is unavailable."""
        mock_service_instance = Mock()
        mock_service_instance.process_image_with_segmentation.return_value = Mock(
            success=False,
            error=Mock(
                error_code='service_error',
                message='ML models not available',
                details={}
            )
        )
        mock_analysis_service.return_value = mock_service_instance
        
        image_file = self._create_test_image_file()
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(
            self.url,
            {'image': image_file},
            format='multipart',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)
    
    @patch('images_app.views.image.user.scan_views.send_email_notification')
    @patch('images_app.views.image.user.scan_views.AnalysisService')
    def test_scan_measure_sends_email(self, mock_analysis_service, mock_send_email):
        """Test that email is sent after successful scan."""
        mock_service_instance = Mock()
        mock_service_instance.process_image_with_segmentation.return_value = Mock(
            success=True,
            data={
                'prediction_id': 1,
                'alto_mm': 25.5,
                'ancho_mm': 15.3,
                'grosor_mm': 8.2,
                'peso_g': 1.5,
                'confidences': {
                    'alto': 0.9,
                    'ancho': 0.85,
                    'grosor': 0.8,
                    'peso': 0.75
                },
                'debug': {'model_version': 'v1.0'},
                'crop_url': 'http://example.com/crop.jpg'
            }
        )
        mock_analysis_service.return_value = mock_service_instance
        mock_send_email.return_value = {'success': True}
        
        image_file = self._create_test_image_file()
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(
            self.url,
            {'image': image_file},
            format='multipart',
            **headers
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once()


class ImageDetailViewTest(APITestCase):
    """Tests for ImageDetailView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
        
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        self.image = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca=self.finca,
            region='Test Region'
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            alto_mm=Decimal('25.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('8.2'),
            peso_g=Decimal('1.5'),
            confidence_alto=Decimal('0.9'),
            confidence_ancho=Decimal('0.85'),
            confidence_grosor=Decimal('0.8'),
            confidence_peso=Decimal('0.75'),
            processing_time_ms=1500,
            model_version='v1.0'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_image_detail_success(self):
        """Test getting image details successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.image.id)
        self.assertIn('prediction', response.data)
    
    def test_get_image_detail_not_found(self):
        """Test getting non-existent image."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-detail', kwargs={'image_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_image_detail_permission_denied(self):
        """Test getting image detail without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_get_image_detail_admin_access(self):
        """Test admin can access any image."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.image.id)
    
    def test_get_image_detail_unauthenticated(self):
        """Test getting image detail without authentication."""
        url = reverse('image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ImageUpdateViewTest(APITestCase):
    """Tests for ImageUpdateView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
        
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        self.image = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca=self.finca,
            region='Test Region'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_update_image_success(self):
        """Test updating image successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-update', kwargs={'image_id': self.image.id})
        
        update_data = {
            'region': 'Updated Region',
            'variedad': 'Updated Variety',
            'notas': 'Updated notes'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_fields', response.data)
        self.image.refresh_from_db()
        self.assertEqual(self.image.region, 'Updated Region')
        self.assertEqual(self.image.variedad, 'Updated Variety')
    
    def test_update_image_with_date(self):
        """Test updating image with fecha_cosecha."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-update', kwargs={'image_id': self.image.id})
        
        update_data = {
            'fecha_cosecha': '2024-01-15'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image.refresh_from_db()
        self.assertEqual(self.image.fecha_cosecha, date(2024, 1, 15))
    
    def test_update_image_invalid_date_format(self):
        """Test updating image with invalid date format."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-update', kwargs={'image_id': self.image.id})
        
        update_data = {
            'fecha_cosecha': 'invalid-date'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_image_permission_denied(self):
        """Test updating image without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('image-update', kwargs={'image_id': self.image.id})
        
        update_data = {'region': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_update_image_not_found(self):
        """Test updating non-existent image."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-update', kwargs={'image_id': 99999})
        
        update_data = {'region': 'Updated Region'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class ImageDeleteViewTest(APITestCase):
    """Tests for ImageDeleteView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
        
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        self.image = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca=self.finca,
            region='Test Region'
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            alto_mm=Decimal('25.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('8.2'),
            peso_g=Decimal('1.5'),
            confidence_alto=Decimal('0.9'),
            confidence_ancho=Decimal('0.85'),
            confidence_grosor=Decimal('0.8'),
            confidence_peso=Decimal('0.75'),
            processing_time_ms=1500,
            model_version='v1.0'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_delete_image_success(self):
        """Test deleting image successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-delete', kwargs={'image_id': self.image.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CacaoImage.objects.filter(id=self.image.id).exists())
        self.assertFalse(CacaoPrediction.objects.filter(id=self.prediction.id).exists())
    
    def test_delete_image_permission_denied(self):
        """Test deleting image without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('image-delete', kwargs={'image_id': self.image.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CacaoImage.objects.filter(id=self.image.id).exists())
    
    def test_delete_image_not_found(self):
        """Test deleting non-existent image."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-delete', kwargs={'image_id': 99999})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class ImageDownloadViewTest(APITestCase):
    """Tests for ImageDownloadView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
        
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        self.image = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca=self.finca,
            region='Test Region'
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            alto_mm=Decimal('25.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('8.2'),
            peso_g=Decimal('1.5'),
            confidence_alto=Decimal('0.9'),
            confidence_ancho=Decimal('0.85'),
            confidence_grosor=Decimal('0.8'),
            confidence_peso=Decimal('0.75'),
            processing_time_ms=1500,
            model_version='v1.0',
            crop_url='http://example.com/crop.jpg'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_download_original_image_success(self, mock_open, mock_exists):
        """Test downloading original image successfully."""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.read.return_value = b'fake image content'
        mock_open.return_value.__enter__.return_value = mock_file
        
        headers = self._get_auth_headers(self.user)
        url = reverse('image-download', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, {'type': 'original'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
    
    def test_download_processed_image_success(self):
        """Test downloading processed image successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-download', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, {'type': 'processed'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.prediction.crop_url)
    
    def test_download_image_invalid_type(self):
        """Test downloading image with invalid type."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-download', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, {'type': 'invalid'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_download_image_permission_denied(self):
        """Test downloading image without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('image-download', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, {'type': 'original'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_download_image_not_found(self):
        """Test downloading non-existent image."""
        headers = self._get_auth_headers(self.user)
        url = reverse('image-download', kwargs={'image_id': 99999})
        
        response = self.client.get(url, {'type': 'original'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class ImagesListViewTest(APITestCase):
    """Tests for ImagesListView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
        
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        self.image1 = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image1.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca=self.finca,
            region='Region A'
        )
        
        self.image2 = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=False,
            finca=self.finca,
            region='Region B'
        )
        
        self.other_image = CacaoImage.objects.create(
            user=self.other_user,
            image=image_file,
            file_name='other_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            region='Region C'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_images_success(self):
        """Test listing images successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_images_with_region_filter(self):
        """Test listing images with region filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-list')
        
        response = self.client.get(url, {'region': 'Region A'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['region'], 'Region A')
    
    def test_list_images_with_processed_filter(self):
        """Test listing images with processed filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-list')
        
        response = self.client.get(url, {'processed': 'true'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['processed'])
    
    def test_list_images_with_search(self):
        """Test listing images with search."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-list')
        
        response = self.client.get(url, {'search': 'test_image1'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_images_with_pagination(self):
        """Test listing images with pagination."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-list')
        
        response = self.client.get(url, {'page': 1, 'page_size': 1}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
    
    def test_list_images_unauthenticated(self):
        """Test listing images without authentication."""
        url = reverse('images-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ImagesStatsViewTest(APITestCase):
    """Tests for ImagesStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
        
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        self.image1 = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image1.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca=self.finca,
            region='Region A'
        )
        
        self.prediction1 = CacaoPrediction.objects.create(
            image=self.image1,
            user=self.user,
            alto_mm=Decimal('25.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('8.2'),
            peso_g=Decimal('1.5'),
            confidence_alto=Decimal('0.9'),
            confidence_ancho=Decimal('0.85'),
            confidence_grosor=Decimal('0.8'),
            confidence_peso=Decimal('0.75'),
            processing_time_ms=1500,
            model_version='v1.0'
        )
        
        self.image2 = CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=False,
            finca=self.finca,
            region='Region B'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_stats_success(self):
        """Test getting image statistics successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-stats')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_images', response.data)
        self.assertIn('processed_images', response.data)
        self.assertIn('unprocessed_images', response.data)
        self.assertIn('average_confidence', response.data)
        self.assertIn('region_stats', response.data)
        self.assertIn('average_dimensions', response.data)
    
    def test_get_stats_values(self):
        """Test that stats values are correct."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-stats')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_images'], 2)
        self.assertEqual(response.data['processed_images'], 1)
        self.assertEqual(response.data['unprocessed_images'], 1)
    
    def test_get_stats_unauthenticated(self):
        """Test getting stats without authentication."""
        url = reverse('images-stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

