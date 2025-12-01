"""
Tests for export views.
"""
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
from images_app.models import CacaoImage, CacaoPrediction
from images_app.views.image.export.export_views import ImagesExportView


class ImagesExportViewTest(APITestCase):
    """Tests for ImagesExportView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        
        self.image1 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test1.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca='Test Finca 1',
            region='Region 1',
            variedad='Variedad 1',
            fecha_cosecha='2024-01-15'
        )
        
        self.prediction1 = CacaoPrediction.objects.create(
            image=self.image1,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            average_confidence=0.91,
            processing_time_ms=1500,
            model_version='v1.0',
            device_used='cpu'
        )
        
        self.view = ImagesExportView()
    
    def _create_test_image(self):
        """Create test image file."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            'test_image.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_validate_export_format_csv(self):
        """Test validating CSV format."""
        result = self.view._validate_export_format('csv')
        
        self.assertIsNone(result)
    
    def test_validate_export_format_invalid(self):
        """Test validating invalid format."""
        result = self.view._validate_export_format('json')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_apply_export_filters_date_from(self):
        """Test applying date_from filter."""
        from datetime import date
        queryset = CacaoImage.objects.all()
        
        result = self.view._apply_export_filters(
            queryset, date.today().isoformat(), None, None, None, False
        )
        
        self.assertIsNotNone(result)
    
    def test_apply_export_filters_date_to(self):
        """Test applying date_to filter."""
        from datetime import date
        queryset = CacaoImage.objects.all()
        
        result = self.view._apply_export_filters(
            queryset, None, date.today().isoformat(), None, None, False
        )
        
        self.assertIsNotNone(result)
    
    def test_apply_export_filters_region(self):
        """Test applying region filter."""
        queryset = CacaoImage.objects.all()
        
        result = self.view._apply_export_filters(
            queryset, None, None, 'Region 1', None, False
        )
        
        self.assertEqual(result.count(), 1)
    
    def test_apply_export_filters_finca(self):
        """Test applying finca filter."""
        queryset = CacaoImage.objects.all()
        
        result = self.view._apply_export_filters(
            queryset, None, None, None, 'Test Finca 1', False
        )
        
        self.assertEqual(result.count(), 1)
    
    def test_apply_export_filters_processed_only(self):
        """Test applying processed_only filter."""
        queryset = CacaoImage.objects.all()
        
        result = self.view._apply_export_filters(
            queryset, None, None, None, None, True
        )
        
        self.assertEqual(result.count(), 1)
    
    def test_build_csv_headers_images_only(self):
        """Test building CSV headers with images only."""
        headers = self.view._build_csv_headers(include_images=True, include_predictions=False)
        
        self.assertIn('image_id', headers)
        self.assertIn('file_name', headers)
        self.assertNotIn('prediction_id', headers)
    
    def test_build_csv_headers_predictions_only(self):
        """Test building CSV headers with predictions only."""
        headers = self.view._build_csv_headers(include_images=False, include_predictions=True)
        
        self.assertIn('prediction_id', headers)
        self.assertIn('alto_mm', headers)
        self.assertNotIn('image_id', headers)
    
    def test_build_csv_headers_both(self):
        """Test building CSV headers with both."""
        headers = self.view._build_csv_headers(include_images=True, include_predictions=True)
        
        self.assertIn('image_id', headers)
        self.assertIn('prediction_id', headers)
    
    def test_build_image_row(self):
        """Test building image row data."""
        row = self.view._build_image_row(self.image1)
        
        self.assertEqual(row[0], self.image1.id)
        self.assertEqual(row[1], 'test1.jpg')
        self.assertEqual(row[3], 'Test Finca 1')
    
    def test_build_prediction_row(self):
        """Test building prediction row data."""
        row = self.view._build_prediction_row(self.prediction1)
        
        self.assertEqual(row[0], self.prediction1.id)
        self.assertEqual(float(row[1]), 15.5)
        self.assertEqual(float(row[2]), 12.3)
    
    def test_post_export_csv_success(self):
        """Test successful CSV export."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/export/'
        data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_post_export_csv_images_only(self):
        """Test CSV export with images only."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/export/'
        data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_post_export_csv_predictions_only(self):
        """Test CSV export with predictions only."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/export/'
        data = {
            'format': 'csv',
            'include_images': False,
            'include_predictions': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_post_export_invalid_format(self):
        """Test export with invalid format."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/export/'
        data = {
            'format': 'json',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_export_with_filters(self):
        """Test export with filters."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/export/'
        data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True,
            'region': 'Region 1',
            'processed_only': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_post_export_unauthenticated(self):
        """Test export without authentication."""
        url = '/api/v1/images/export/'
        data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_write_csv_data_with_prediction(self):
        """Test writing CSV data with prediction."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        queryset = CacaoImage.objects.filter(id=self.image1.id)
        self.view._write_csv_data(writer, queryset, True, True)
        
        output.seek(0)
        lines = output.readlines()
        
        self.assertGreater(len(lines), 0)

