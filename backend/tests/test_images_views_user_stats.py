"""
Tests for user statistics views.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io
from datetime import timedelta
from django.utils import timezone

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)
from images_app.models import CacaoImage, CacaoPrediction
from images_app.views.image.user.stats_views import ImagesStatsView


class ImagesStatsViewTest(APITestCase):
    """Tests for ImagesStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        
        # Create images with different dates and states
        self.image1 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test1.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            region='Region 1',
            finca='Finca 1'
        )
        
        self.image2 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=True,
            region='Region 2',
            finca='Finca 2'
        )
        
        self.image3 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test3.jpg',
            file_size=3072,
            file_type='image/jpeg',
            processed=False,
            region='Region 1',
            finca='Finca 1'
        )
        
        # Create predictions
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
        
        self.prediction2 = CacaoPrediction.objects.create(
            image=self.image2,
            alto_mm=16.0,
            ancho_mm=13.0,
            grosor_mm=9.0,
            peso_g=1.3,
            confidence_alto=0.94,
            confidence_ancho=0.91,
            confidence_grosor=0.87,
            confidence_peso=0.89,
            average_confidence=0.90,
            processing_time_ms=1600,
            model_version='v1.0',
            device_used='cpu'
        )
    
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
    
    def test_get_stats_authenticated(self):
        """Test getting stats as authenticated user."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_images', response.data)
        self.assertIn('processed_images', response.data)
        self.assertIn('unprocessed_images', response.data)
        self.assertEqual(response.data['total_images'], 3)
        self.assertEqual(response.data['processed_images'], 2)
        self.assertEqual(response.data['unprocessed_images'], 1)
    
    def test_get_stats_unauthenticated(self):
        """Test getting stats without authentication."""
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_stats_processed_today(self):
        """Test processed_today statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('processed_today', response.data)
        self.assertIsInstance(response.data['processed_today'], int)
    
    def test_get_stats_processed_this_week(self):
        """Test processed_this_week statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('processed_this_week', response.data)
        self.assertIsInstance(response.data['processed_this_week'], int)
    
    def test_get_stats_processed_this_month(self):
        """Test processed_this_month statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('processed_this_month', response.data)
        self.assertIsInstance(response.data['processed_this_month'], int)
    
    def test_get_stats_average_confidence(self):
        """Test average_confidence statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_confidence', response.data)
        self.assertIsInstance(response.data['average_confidence'], (int, float))
    
    def test_get_stats_average_processing_time(self):
        """Test average_processing_time_ms statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_processing_time_ms', response.data)
        self.assertIsInstance(response.data['average_processing_time_ms'], (int, float))
    
    def test_get_stats_region_stats(self):
        """Test region_stats statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('region_stats', response.data)
        self.assertIsInstance(response.data['region_stats'], list)
        self.assertGreater(len(response.data['region_stats']), 0)
    
    def test_get_stats_top_fincas(self):
        """Test top_fincas statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('top_fincas', response.data)
        self.assertIsInstance(response.data['top_fincas'], list)
    
    def test_get_stats_average_dimensions(self):
        """Test average_dimensions statistic."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_dimensions', response.data)
        self.assertIn('alto_mm', response.data['average_dimensions'])
        self.assertIn('ancho_mm', response.data['average_dimensions'])
        self.assertIn('grosor_mm', response.data['average_dimensions'])
        self.assertIn('peso_g', response.data['average_dimensions'])
    
    def test_get_stats_no_images(self):
        """Test stats with no images."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.client.force_authenticate(user=other_user)
        
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_images'], 0)
        self.assertEqual(response.data['processed_images'], 0)
    
    def test_get_stats_exception_handling(self):
        """Test that exceptions are handled gracefully."""
        self.client.force_authenticate(user=self.user)
        
        # This should not raise an exception even if there's an error
        url = '/api/v1/images/stats/'
        response = self.client.get(url)
        
        # Should return 200 with empty/default stats
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_images', response.data)

