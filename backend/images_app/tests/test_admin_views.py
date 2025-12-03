"""
Tests for Images App admin views.
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
from datetime import date, timedelta
from django.utils import timezone

from api.models import CacaoImage, CacaoPrediction, Finca, Lote
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
    TEST_OTHER_USER_USERNAME,
)


class AdminImagesListViewTest(APITestCase):
    """Tests for AdminImagesListView."""
    
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
            user=self.other_user,
            image=image_file,
            file_name='test_image2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=False,
            region='Region B'
        )
        
        self.prediction = CacaoPrediction.objects.create(
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
            average_confidence=Decimal('0.825')
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_all_images_as_admin(self):
        """Test admin can list all images."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_images_with_user_id_filter(self):
        """Test listing images with user_id filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'user_id': self.user.id}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.image1.id)
    
    def test_list_images_with_username_filter(self):
        """Test listing images with username filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'username': TEST_USER_USERNAME}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_images_with_region_filter(self):
        """Test listing images with region filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'region': 'Region A'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_images_with_processed_filter(self):
        """Test listing images with processed filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'processed': 'true'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['processed'])
    
    def test_list_images_with_has_prediction_filter(self):
        """Test listing images with has_prediction filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'has_prediction': 'true'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_images_with_model_version_filter(self):
        """Test listing images with model_version filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'model_version': 'v1.0'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_images_with_confidence_filters(self):
        """Test listing images with confidence filters."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'min_confidence': '0.8', 'max_confidence': '0.9'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_images_with_search(self):
        """Test listing images with search."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, {'search': 'test_image1'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_images_with_date_filters(self):
        """Test listing images with date filters."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-images-list')
        
        today = timezone.now().date()
        date_from = (today - timedelta(days=7)).isoformat()
        date_to = today.isoformat()
        
        response = self.client.get(url, {'date_from': date_from, 'date_to': date_to}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_images_permission_denied(self):
        """Test non-admin cannot list all images."""
        headers = self._get_auth_headers(self.user)
        url = reverse('admin-images-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_list_images_unauthenticated(self):
        """Test listing images without authentication."""
        url = reverse('admin-images-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminImageDetailViewTest(APITestCase):
    """Tests for AdminImageDetailView."""
    
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
            device_used='cpu',
            crop_url='http://example.com/crop.jpg'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_admin_image_detail_success(self):
        """Test admin getting image details successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.image.id)
        self.assertIn('admin_info', response.data)
        self.assertIn('owner_info', response.data['admin_info'])
        self.assertIn('file_info', response.data['admin_info'])
        self.assertIn('processing_info', response.data['admin_info'])
        self.assertIn('access_info', response.data['admin_info'])
    
    def test_get_admin_image_detail_not_found(self):
        """Test getting non-existent image."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-detail', kwargs={'image_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_admin_image_detail_permission_denied(self):
        """Test non-admin cannot access admin detail view."""
        headers = self._get_auth_headers(self.user)
        url = reverse('admin-image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_get_admin_image_detail_unauthenticated(self):
        """Test getting admin image detail without authentication."""
        url = reverse('admin-image-detail', kwargs={'image_id': self.image.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminImageUpdateViewTest(APITestCase):
    """Tests for AdminImageUpdateView."""
    
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
    
    def test_update_image_as_admin_success(self):
        """Test admin updating image successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-update', kwargs={'image_id': self.image.id})
        
        update_data = {
            'region': 'Updated Region',
            'variedad': 'Updated Variety',
            'notas': 'Updated notes',
            'admin_notes': 'Admin update note'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_fields', response.data)
        self.assertIn('updated_by', response.data)
        self.image.refresh_from_db()
        self.assertEqual(self.image.region, 'Updated Region')
        self.assertEqual(self.image.variedad, 'Updated Variety')
        self.assertIn('Admin update note', self.image.notas)
    
    def test_update_image_with_date(self):
        """Test updating image with fecha_cosecha."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-update', kwargs={'image_id': self.image.id})
        
        update_data = {
            'fecha_cosecha': '2024-01-15'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image.refresh_from_db()
        self.assertEqual(self.image.fecha_cosecha, date(2024, 1, 15))
    
    def test_update_image_invalid_date_format(self):
        """Test updating image with invalid date format."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-update', kwargs={'image_id': self.image.id})
        
        update_data = {
            'fecha_cosecha': 'invalid-date'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_image_permission_denied(self):
        """Test non-admin cannot update image."""
        headers = self._get_auth_headers(self.user)
        url = reverse('admin-image-update', kwargs={'image_id': self.image.id})
        
        update_data = {'region': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_update_image_not_found(self):
        """Test updating non-existent image."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-update', kwargs={'image_id': 99999})
        
        update_data = {'region': 'Updated Region'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class AdminImageDeleteViewTest(APITestCase):
    """Tests for AdminImageDeleteView."""
    
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
    
    def test_delete_image_as_admin_success(self):
        """Test admin deleting image successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-delete', kwargs={'image_id': self.image.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('deleted_image', response.data)
        self.assertIn('deleted_by', response.data)
        self.assertFalse(CacaoImage.objects.filter(id=self.image.id).exists())
        self.assertFalse(CacaoPrediction.objects.filter(id=self.prediction.id).exists())
    
    def test_delete_image_permission_denied(self):
        """Test non-admin cannot delete image."""
        headers = self._get_auth_headers(self.user)
        url = reverse('admin-image-delete', kwargs={'image_id': self.image.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CacaoImage.objects.filter(id=self.image.id).exists())
    
    def test_delete_image_not_found(self):
        """Test deleting non-existent image."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-image-delete', kwargs={'image_id': 99999})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class AdminBulkUpdateViewTest(APITestCase):
    """Tests for AdminBulkUpdateView."""
    
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
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_bulk_update_by_ids_success(self):
        """Test bulk update by image IDs successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'image_ids': [self.image1.id, self.image2.id],
            'updates': {
                'region': 'Updated Region',
                'variedad': 'Updated Variety'
            },
            'admin_notes': 'Bulk update test'
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_count', response.data)
        self.assertEqual(response.data['updated_count'], 2)
        self.assertIn('updated_fields', response.data)
        self.image1.refresh_from_db()
        self.image2.refresh_from_db()
        self.assertEqual(self.image1.region, 'Updated Region')
        self.assertEqual(self.image2.region, 'Updated Region')
    
    def test_bulk_update_by_filters_success(self):
        """Test bulk update by filters successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'filters': {
                'region': 'Region A'
            },
            'updates': {
                'variedad': 'Filtered Variety'
            }
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_count', response.data)
        self.image1.refresh_from_db()
        self.assertEqual(self.image1.variedad, 'Filtered Variety')
    
    def test_bulk_update_with_date(self):
        """Test bulk update with fecha_cosecha."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'image_ids': [self.image1.id],
            'updates': {
                'fecha_cosecha': '2024-01-15'
            }
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image1.refresh_from_db()
        self.assertEqual(self.image1.fecha_cosecha, date(2024, 1, 15))
    
    def test_bulk_update_invalid_date_format(self):
        """Test bulk update with invalid date format."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'image_ids': [self.image1.id],
            'updates': {
                'fecha_cosecha': 'invalid-date'
            }
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_bulk_update_no_updates(self):
        """Test bulk update without updates."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'image_ids': [self.image1.id]
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_bulk_update_no_matching_images(self):
        """Test bulk update with no matching images."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'filters': {
                'region': 'Non-existent Region'
            },
            'updates': {
                'region': 'Updated Region'
            }
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_bulk_update_permission_denied(self):
        """Test non-admin cannot perform bulk update."""
        headers = self._get_auth_headers(self.user)
        url = reverse('admin-bulk-update')
        
        update_data = {
            'image_ids': [self.image1.id],
            'updates': {'region': 'Updated Region'}
        }
        
        response = self.client.post(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)


class AdminDatasetStatsViewTest(APITestCase):
    """Tests for AdminDatasetStatsView."""
    
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
            variedad='Variety A'
        )
        
        self.prediction = CacaoPrediction.objects.create(
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
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_dataset_stats_success(self):
        """Test getting dataset statistics successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-dataset-stats')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('dataset_overview', response.data)
        self.assertIn('temporal_stats', response.data)
        self.assertIn('geographic_stats', response.data)
        self.assertIn('variety_stats', response.data)
        self.assertIn('quality_stats', response.data)
        self.assertIn('model_stats', response.data)
        self.assertIn('user_activity', response.data)
        self.assertIn('storage_stats', response.data)
    
    def test_get_dataset_stats_values(self):
        """Test that dataset stats values are correct."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('admin-dataset-stats')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['dataset_overview']['total_images'], 2)
        self.assertEqual(response.data['dataset_overview']['processed_images'], 1)
        self.assertEqual(response.data['dataset_overview']['pending_images'], 1)
    
    def test_get_dataset_stats_permission_denied(self):
        """Test non-admin cannot get dataset stats."""
        headers = self._get_auth_headers(self.user)
        url = reverse('admin-dataset-stats')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_get_dataset_stats_unauthenticated(self):
        """Test getting dataset stats without authentication."""
        url = reverse('admin-dataset-stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

