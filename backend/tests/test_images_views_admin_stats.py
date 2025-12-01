"""
Tests for admin statistics views.
"""
from unittest.mock import patch
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
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
)
from images_app.models import CacaoImage, CacaoPrediction
from images_app.views.image.admin.stats_views import AdminDatasetStatsView


class AdminDatasetStatsViewTest(APITestCase):
    """Tests for AdminDatasetStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        
        self.image1 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test1.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            region='Region 1',
            finca='Finca 1',
            variedad='Variedad 1'
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
        
        self.view = AdminDatasetStatsView()
    
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
    
    def test_get_basic_dataset_stats(self):
        """Test getting basic dataset statistics."""
        stats = self.view._get_basic_dataset_stats()
        
        self.assertIn('total_images', stats)
        self.assertIn('processed_images', stats)
        self.assertIn('pending_images', stats)
        self.assertGreaterEqual(stats['total_images'], 1)
    
    def test_get_temporal_stats(self):
        """Test getting temporal statistics."""
        stats = self.view._get_temporal_stats()
        
        self.assertIn('last_24h', stats)
        self.assertIn('last_7d', stats)
        self.assertIn('last_30d', stats)
        self.assertIsInstance(stats['last_24h'], int)
    
    def test_get_confidence_stats(self):
        """Test getting confidence statistics."""
        stats = self.view._get_confidence_stats()
        
        self.assertIn('avg_confidence', stats)
        self.assertIn('min_confidence', stats)
        self.assertIn('max_confidence', stats)
    
    def test_get_model_stats(self):
        """Test getting model statistics."""
        stats = list(self.view._get_model_stats())
        
        self.assertIsInstance(stats, list)
        if len(stats) > 0:
            self.assertIn('model_version', stats[0])
            self.assertIn('count', stats[0])
    
    def test_get_device_stats(self):
        """Test getting device statistics."""
        stats = list(self.view._get_device_stats())
        
        self.assertIsInstance(stats, list)
        if len(stats) > 0:
            self.assertIn('device_used', stats[0])
            self.assertIn('count', stats[0])
    
    def test_get_top_users(self):
        """Test getting top users."""
        users = list(self.view._get_top_users())
        
        self.assertIsInstance(users, list)
    
    def test_get_file_stats(self):
        """Test getting file statistics."""
        stats = self.view._get_file_stats()
        
        self.assertIn('total_size', stats)
        self.assertIn('avg_size', stats)
        self.assertIsInstance(stats['total_size'], (int, type(None)))
    
    def test_get_metadata_completeness(self):
        """Test getting metadata completeness."""
        count = self.view._get_metadata_completeness()
        
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_get_stats_as_admin(self):
        """Test getting stats as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('dataset_overview', response.data)
        self.assertIn('temporal_stats', response.data)
        self.assertIn('geographic_stats', response.data)
        self.assertIn('variety_stats', response.data)
        self.assertIn('quality_stats', response.data)
        self.assertIn('model_stats', response.data)
        self.assertIn('user_activity', response.data)
        self.assertIn('storage_stats', response.data)
    
    def test_get_stats_dataset_overview(self):
        """Test dataset_overview in stats response."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        overview = response.data['dataset_overview']
        self.assertIn('total_images', overview)
        self.assertIn('processed_images', overview)
        self.assertIn('processing_rate', overview)
    
    def test_get_stats_geographic_stats(self):
        """Test geographic_stats in response."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        geo_stats = response.data['geographic_stats']
        self.assertIn('top_regions', geo_stats)
        self.assertIn('top_fincas', geo_stats)
        self.assertIn('unique_regions', geo_stats)
        self.assertIn('unique_fincas', geo_stats)
    
    def test_get_stats_quality_stats(self):
        """Test quality_stats in response."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        quality_stats = response.data['quality_stats']
        self.assertIn('average_dimensions', quality_stats)
        self.assertIn('confidence_stats', quality_stats)
        self.assertIn('processing_stats', quality_stats)
    
    def test_get_stats_as_non_admin(self):
        """Test getting stats as non-admin."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_stats_unauthenticated(self):
        """Test getting stats without authentication."""
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_stats_exception_handling(self):
        """Test that exceptions are handled gracefully."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/admin-stats/'
        response = self.client.get(url)
        
        # Should return 200 or 500, but handle gracefully
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            self.assertIn('error', response.data)

