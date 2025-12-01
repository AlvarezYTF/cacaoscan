"""
Tests for user list views.
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
from images_app.models import CacaoImage
from images_app.views.image.user.list_views import ImagesListView


class ImagesListViewTest(APITestCase):
    """Tests for ImagesListView."""
    
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
            notas='Test notes 1'
        )
        
        self.image2 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=False,
            finca='Test Finca 2',
            region='Region 2',
            variedad='Variedad 2',
            notas='Test notes 2'
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
    
    def test_get_list_authenticated(self):
        """Test getting image list as authenticated user."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)
    
    def test_get_list_unauthenticated(self):
        """Test getting image list without authentication."""
        url = '/api/v1/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_list_with_pagination(self):
        """Test getting list with pagination."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'page': 1, 'page_size': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    
    def test_get_list_filter_by_region(self):
        """Test filtering list by region."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'region': 'Region 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['region'], 'Region 1')
    
    def test_get_list_filter_by_finca(self):
        """Test filtering list by finca."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'finca': 'Test Finca 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_get_list_filter_by_processed_true(self):
        """Test filtering list by processed (true)."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'processed': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(response.data['results'][0]['processed'])
    
    def test_get_list_filter_by_processed_false(self):
        """Test filtering list by processed (false)."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'processed': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertFalse(response.data['results'][0]['processed'])
    
    def test_get_list_search(self):
        """Test searching in list."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'search': 'Variedad 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_get_list_search_in_notes(self):
        """Test searching in notes."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'search': 'notes 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_get_list_filter_by_date_from(self):
        """Test filtering by date_from."""
        from datetime import date
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'date_from': date.today().isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_list_filter_by_date_to(self):
        """Test filtering by date_to."""
        from datetime import date
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url, {'date_to': date.today().isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_list_ordered_by_created_at(self):
        """Test that list is ordered by created_at descending."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data['results']) > 1:
            # Most recent first
            self.assertGreaterEqual(
                response.data['results'][0]['created_at'],
                response.data['results'][1]['created_at']
            )
    
    def test_get_list_only_user_images(self):
        """Test that user only sees their own images."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        CacaoImage.objects.create(
            user=other_user,
            image=self.test_image,
            file_name='other_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True
        )
        
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Only user's images

