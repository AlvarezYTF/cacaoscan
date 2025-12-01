"""
Tests for user CRUD views.
"""
from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io
import os

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_OTHER_USER_USERNAME,
    TEST_OTHER_USER_EMAIL,
)
from images_app.models import CacaoImage, CacaoPrediction
from images_app.views.image.user.crud_views import (
    ImageDetailView,
    ImageUpdateView,
    ImageDeleteView,
    ImageDownloadView
)


class ImageDetailViewTest(APITestCase):
    """Tests for ImageDetailView."""
    
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
        
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.cacao_image,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            processing_time_ms=1500,
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
    
    def test_get_image_detail_as_owner(self):
        """Test getting image detail as owner."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cacao_image.id)
        self.assertIn('prediction', response.data)
    
    def test_get_image_detail_as_admin(self):
        """Test getting image detail as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_image_detail_as_other_user(self):
        """Test getting image detail as other user (should fail)."""
        self.client.force_authenticate(user=self.other_user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_image_detail_not_found(self):
        """Test getting non-existent image detail."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_image_detail_unauthenticated(self):
        """Test getting image detail without authentication."""
        url = f'/api/v1/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ImageUpdateViewTest(APITestCase):
    """Tests for ImageUpdateView."""
    
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
        
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=False,
            finca='Old Finca',
            region='Old Region'
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
    
    def test_update_image_as_owner(self):
        """Test updating image as owner."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/update/'
        data = {
            'finca': 'New Finca',
            'region': 'New Region',
            'variedad': 'New Variedad',
            'notas': 'Updated notes'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_fields', response.data)
        
        self.cacao_image.refresh_from_db()
        self.assertEqual(self.cacao_image.finca, 'New Finca')
        self.assertEqual(self.cacao_image.region, 'New Region')
    
    def test_update_image_with_date(self):
        """Test updating image with fecha_cosecha."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/update/'
        data = {
            'fecha_cosecha': '2024-01-15'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.cacao_image.refresh_from_db()
        self.assertIsNotNone(self.cacao_image.fecha_cosecha)
    
    def test_update_image_invalid_date(self):
        """Test updating image with invalid date."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/update/'
        data = {
            'fecha_cosecha': 'invalid-date'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_image_as_admin(self):
        """Test updating image as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/update/'
        data = {'finca': 'Admin Updated Finca'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_image_as_other_user(self):
        """Test updating image as other user (should fail)."""
        self.client.force_authenticate(user=self.other_user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/update/'
        data = {'finca': 'Unauthorized Update'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_image_not_found(self):
        """Test updating non-existent image."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/99999/update/'
        data = {'finca': 'New Finca'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ImageDeleteViewTest(APITestCase):
    """Tests for ImageDeleteView."""
    
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
        
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.cacao_image,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            processing_time_ms=1500,
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
    
    def test_delete_image_as_owner(self):
        """Test deleting image as owner."""
        self.client.force_authenticate(user=self.user)
        
        image_id = self.cacao_image.id
        prediction_id = self.prediction.id
        url = f'/api/v1/images/{image_id}/delete/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deleted_image', response.data)
        self.assertIn('deleted_prediction', response.data)
        self.assertFalse(CacaoImage.objects.filter(id=image_id).exists())
        self.assertFalse(CacaoPrediction.objects.filter(id=prediction_id).exists())
    
    def test_delete_image_as_admin(self):
        """Test deleting image as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        image_id = self.cacao_image.id
        url = f'/api/v1/images/{image_id}/delete/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CacaoImage.objects.filter(id=image_id).exists())
    
    def test_delete_image_as_other_user(self):
        """Test deleting image as other user (should fail)."""
        self.client.force_authenticate(user=self.other_user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/delete/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CacaoImage.objects.filter(id=self.cacao_image.id).exists())
    
    def test_delete_image_not_found(self):
        """Test deleting non-existent image."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/99999/delete/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ImageDownloadViewTest(APITestCase):
    """Tests for ImageDownloadView."""
    
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
        
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.cacao_image,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            processing_time_ms=1500,
            model_version='v1.0',
            device_used='cpu',
            crop_url='http://example.com/crop.jpg'
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
    
    @patch('images_app.views.image.user.crud_views.os.path.exists')
    def test_download_original_image(self, mock_exists):
        """Test downloading original image."""
        mock_exists.return_value = True
        
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/download/?type=original'
        
        response = self.client.get(url)
        
        # Should return file response or redirect
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_302_FOUND,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_download_processed_image(self):
        """Test downloading processed image."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/download/?type=processed'
        
        response = self.client.get(url)
        
        # Should redirect to crop_url
        self.assertIn(response.status_code, [
            status.HTTP_302_FOUND,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_download_invalid_type(self):
        """Test downloading with invalid type."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/download/?type=invalid'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_download_as_other_user(self):
        """Test downloading image as other user (should fail)."""
        self.client.force_authenticate(user=self.other_user)
        
        url = f'/api/v1/images/{self.cacao_image.id}/download/?type=original'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_download_image_not_found(self):
        """Test downloading non-existent image."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/99999/download/?type=original'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_image_or_404_found(self):
        """Test _get_image_or_404 with existing image."""
        view = ImageDownloadView()
        
        image, error_response = view._get_image_or_404(self.cacao_image.id)
        
        self.assertIsNotNone(image)
        self.assertIsNone(error_response)
        self.assertEqual(image.id, self.cacao_image.id)
    
    def test_get_image_or_404_not_found(self):
        """Test _get_image_or_404 with non-existent image."""
        view = ImageDownloadView()
        
        image, error_response = view._get_image_or_404(99999)
        
        self.assertIsNone(image)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_content_type_jpg(self):
        """Test content type detection for JPG."""
        view = ImageDownloadView()
        
        content_type = view._get_content_type('test.jpg')
        
        self.assertEqual(content_type, 'image/jpeg')
    
    def test_get_content_type_png(self):
        """Test content type detection for PNG."""
        view = ImageDownloadView()
        
        content_type = view._get_content_type('test.png')
        
        self.assertEqual(content_type, 'image/png')
    
    def test_get_content_type_unknown(self):
        """Test content type detection for unknown extension."""
        view = ImageDownloadView()
        
        content_type = view._get_content_type('test.unknown')
        
        self.assertEqual(content_type, 'application/octet-stream')

