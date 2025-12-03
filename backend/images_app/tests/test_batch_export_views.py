"""
Tests for Images App batch and export views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from api.models import CacaoImage, CacaoPrediction, Finca, Lote
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
)


class BatchAnalysisViewTest(APITestCase):
    """Tests for BatchAnalysisView."""
    
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
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def _create_test_image_file(self, name='test_image.jpg'):
        """Create a test image file."""
        return SimpleUploadedFile(
            name,
            b'fake image content',
            content_type='image/jpeg'
        )
    
    @patch('images_app.views.image.batch.batch_upload_views.process_batch_analysis_task')
    def test_batch_analysis_success(self, mock_task):
        """Test batch analysis successfully."""
        mock_task.delay.return_value = Mock(id='test-task-id')
        
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        image1 = self._create_test_image_file('image1.jpg')
        image2 = self._create_test_image_file('image2.jpg')
        
        data = {
            'name': 'Test Lote',
            'farm': 'Test Finca',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15',
            'originPlace': 'Test Origin',
            'origin': 'Test Department',
            'notes': 'Test notes',
            'images': [image1, image2]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertIn('lote_id', response.data)
        self.assertIn('total_images', response.data)
        self.assertEqual(response.data['status'], 'processing')
        mock_task.delay.assert_called_once()
    
    def test_batch_analysis_missing_name(self):
        """Test batch analysis with missing name."""
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        data = {
            'farm': 'Test Finca',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15',
            'images': [self._create_test_image_file()]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_batch_analysis_missing_farm(self):
        """Test batch analysis with missing farm."""
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        data = {
            'name': 'Test Lote',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15',
            'images': [self._create_test_image_file()]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_batch_analysis_missing_genetics(self):
        """Test batch analysis with missing genetics."""
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        data = {
            'name': 'Test Lote',
            'farm': 'Test Finca',
            'collectionDate': '2024-01-15',
            'images': [self._create_test_image_file()]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_batch_analysis_missing_collection_date(self):
        """Test batch analysis with missing collection date."""
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        data = {
            'name': 'Test Lote',
            'farm': 'Test Finca',
            'genetics': 'Test Variety',
            'images': [self._create_test_image_file()]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_batch_analysis_no_images(self):
        """Test batch analysis with no images."""
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        data = {
            'name': 'Test Lote',
            'farm': 'Test Finca',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15'
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('images_app.views.image.batch.batch_upload_views.process_batch_analysis_task')
    def test_batch_analysis_creates_finca(self, mock_task):
        """Test batch analysis creates finca if it doesn't exist."""
        mock_task.delay.return_value = Mock(id='test-task-id')
        
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        image = self._create_test_image_file()
        
        data = {
            'name': 'Test Lote',
            'farm': 'New Finca',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15',
            'images': [image]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(Finca.objects.filter(nombre='New Finca', agricultor=self.user).exists())
    
    @patch('images_app.views.image.batch.batch_upload_views.process_batch_analysis_task')
    def test_batch_analysis_creates_lote(self, mock_task):
        """Test batch analysis creates lote if it doesn't exist."""
        mock_task.delay.return_value = Mock(id='test-task-id')
        
        headers = self._get_auth_headers(self.user)
        url = reverse('batch-analysis')
        
        image = self._create_test_image_file()
        
        data = {
            'name': 'New Lote',
            'farm': 'Test Finca',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15',
            'images': [image]
        }
        
        response = self.client.post(url, data, format='multipart', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(Lote.objects.filter(identificador='New Lote', finca=self.finca).exists())
    
    def test_batch_analysis_unauthenticated(self):
        """Test batch analysis without authentication."""
        url = reverse('batch-analysis')
        
        image = self._create_test_image_file()
        data = {
            'name': 'Test Lote',
            'farm': 'Test Finca',
            'genetics': 'Test Variety',
            'collectionDate': '2024-01-15',
            'images': [image]
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ImagesExportViewTest(APITestCase):
    """Tests for ImagesExportView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
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
            region='Region A',
            variedad='Variety A',
            fecha_cosecha=date(2024, 1, 15)
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
            model_version='v1.0',
            device_used='cpu',
            average_confidence=Decimal('0.825')
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
    
    def test_export_csv_success(self):
        """Test exporting CSV successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.csv', response['Content-Disposition'])
    
    def test_export_csv_with_images_only(self):
        """Test exporting CSV with images only."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': False
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_csv_with_predictions_only(self):
        """Test exporting CSV with predictions only."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': False,
            'include_predictions': True
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_csv_with_region_filter(self):
        """Test exporting CSV with region filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True,
            'region': 'Region A'
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_csv_with_finca_filter(self):
        """Test exporting CSV with finca filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True,
            'finca': 'Test Finca'
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_csv_with_date_filters(self):
        """Test exporting CSV with date filters."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        today = timezone.now().date()
        date_from = (today - timedelta(days=7)).isoformat()
        date_to = today.isoformat()
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True,
            'date_from': date_from,
            'date_to': date_to
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_csv_with_processed_only_filter(self):
        """Test exporting CSV with processed_only filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True,
            'processed_only': True
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_invalid_format(self):
        """Test exporting with invalid format."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'excel',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_export_csv_only_user_images(self):
        """Test export only includes user's images."""
        headers = self._get_auth_headers(self.user)
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, export_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode('utf-8')
        self.assertIn('test_image1', content)
        self.assertIn('test_image2', content)
        self.assertNotIn('other_image', content)
    
    def test_export_csv_unauthenticated(self):
        """Test exporting CSV without authentication."""
        url = reverse('images-export')
        
        export_data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, export_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

