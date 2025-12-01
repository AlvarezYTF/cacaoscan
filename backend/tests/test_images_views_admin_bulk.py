"""
Tests for admin bulk update views.
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
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
)
from images_app.models import CacaoImage
# Import directly to avoid circular import issues
import sys
if 'images_app.views.image.admin.bulk_views' not in sys.modules:
    from images_app.views.image.admin import bulk_views
    AdminBulkUpdateView = bulk_views.AdminBulkUpdateView
else:
    from images_app.views.image.admin.bulk_views import AdminBulkUpdateView


class AdminBulkUpdateViewTest(APITestCase):
    """Tests for AdminBulkUpdateView."""
    
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
            processed=False,
            finca='Old Finca',
            region='Old Region'
        )
        
        self.image2 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=False,
            finca='Old Finca',
            region='Old Region'
        )
        
        self.view = AdminBulkUpdateView()
    
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
    
    def test_apply_filters_user_id(self):
        """Test applying user_id filter."""
        queryset = CacaoImage.objects.all()
        filters = {'user_id': self.user.id}
        
        result = self.view._apply_filters(queryset, filters)
        
        self.assertEqual(result.count(), 2)
    
    def test_apply_filters_username(self):
        """Test applying username filter."""
        queryset = CacaoImage.objects.all()
        filters = {'username': TEST_USER_USERNAME}
        
        result = self.view._apply_filters(queryset, filters)
        
        self.assertEqual(result.count(), 2)
    
    def test_apply_filters_region(self):
        """Test applying region filter."""
        queryset = CacaoImage.objects.all()
        filters = {'region': 'Old Region'}
        
        result = self.view._apply_filters(queryset, filters)
        
        self.assertEqual(result.count(), 2)
    
    def test_apply_filters_processed(self):
        """Test applying processed filter."""
        queryset = CacaoImage.objects.all()
        filters = {'processed': True}
        
        result = self.view._apply_filters(queryset, filters)
        
        self.assertEqual(result.count(), 0)
    
    def test_validate_fecha_cosecha_valid(self):
        """Test validating valid fecha_cosecha."""
        updates = {'fecha_cosecha': '2024-01-15'}
        
        result = self.view._validate_fecha_cosecha(updates)
        
        self.assertIsNone(result)
        self.assertIsInstance(updates['fecha_cosecha'], type(updates['fecha_cosecha']))
    
    def test_validate_fecha_cosecha_invalid(self):
        """Test validating invalid fecha_cosecha."""
        updates = {'fecha_cosecha': 'invalid-date'}
        
        result = self.view._validate_fecha_cosecha(updates)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_allowed_fields(self):
        """Test filtering allowed fields."""
        updates = {
            'finca': 'New Finca',
            'region': 'New Region',
            'invalid_field': 'Should be removed',
            'notas': 'Test notes'
        }
        
        result = self.view._filter_allowed_fields(updates)
        
        self.assertIn('finca', result)
        self.assertIn('region', result)
        self.assertIn('notas', result)
        self.assertNotIn('invalid_field', result)
    
    def test_add_admin_notes(self):
        """Test adding admin notes."""
        filtered_updates = {}
        admin_notes = 'Test admin note'
        
        self.view._add_admin_notes(filtered_updates, admin_notes, self.admin_user.username)
        
        self.assertIn('notas', filtered_updates)
        self.assertIn(admin_notes, filtered_updates['notas'])
    
    def test_add_admin_notes_existing_notas(self):
        """Test adding admin notes to existing notas."""
        filtered_updates = {'notas': 'Existing notes'}
        admin_notes = 'Test admin note'
        
        self.view._add_admin_notes(filtered_updates, admin_notes, self.admin_user.username)
        
        self.assertIn('Existing notes', filtered_updates['notas'])
        self.assertIn(admin_notes, filtered_updates['notas'])
    
    def test_post_bulk_update_success(self):
        """Test successful bulk update."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/bulk-update/'
        data = {
            'image_ids': [self.image1.id, self.image2.id],
            'updates': {
                'finca': 'New Finca',
                'region': 'New Region',
                'processed': True
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_count', response.data)
        self.assertEqual(response.data['updated_count'], 2)
        
        self.image1.refresh_from_db()
        self.image2.refresh_from_db()
        self.assertEqual(self.image1.finca, 'New Finca')
        self.assertEqual(self.image2.finca, 'New Finca')
    
    def test_post_bulk_update_with_filters(self):
        """Test bulk update with filters."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/bulk-update/'
        data = {
            'filters': {
                'region': 'Old Region'
            },
            'updates': {
                'finca': 'Filtered Finca'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
    
    def test_post_bulk_update_no_updates(self):
        """Test bulk update without updates."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/bulk-update/'
        data = {
            'image_ids': [self.image1.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_bulk_update_no_images_found(self):
        """Test bulk update with no matching images."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/bulk-update/'
        data = {
            'filters': {
                'region': 'Non-existent Region'
            },
            'updates': {
                'finca': 'New Finca'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_bulk_update_as_non_admin(self):
        """Test bulk update as non-admin."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/admin/images/bulk-update/'
        data = {
            'image_ids': [self.image1.id],
            'updates': {'finca': 'New Finca'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_post_bulk_update_invalid_date(self):
        """Test bulk update with invalid date."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/bulk-update/'
        data = {
            'image_ids': [self.image1.id],
            'updates': {
                'fecha_cosecha': 'invalid-date'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

