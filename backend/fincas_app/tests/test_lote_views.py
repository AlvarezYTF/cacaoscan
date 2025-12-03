"""
Tests for Fincas App lote views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

from fincas_app.models import Finca, Lote
from api.models import CacaoImage
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
    TEST_OTHER_USER_USERNAME,
)


class LoteListCreateViewTest(APITestCase):
    """Tests for LoteListCreateView."""
    
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
            agricultor=self.user,
            activa=True
        )
        
        self.other_finca = Finca.objects.create(
            nombre='Other Finca',
            ubicacion='Other Location',
            municipio='Other Municipio',
            departamento='Other Departamento',
            hectareas=3.0,
            agricultor=self.other_user,
            activa=True
        )
        
        self.lote1 = Lote.objects.create(
            finca=self.finca,
            identificador='Lote 1',
            variedad='Variety A',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
        
        self.lote2 = Lote.objects.create(
            finca=self.finca,
            identificador='Lote 2',
            variedad='Variety B',
            fecha_plantacion=date(2021, 1, 1),
            fecha_cosecha=date(2024, 2, 1),
            area_hectareas=2.0,
            estado='activo',
            activo=True
        )
        
        self.other_lote = Lote.objects.create(
            finca=self.other_finca,
            identificador='Other Lote',
            variedad='Variety C',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_lotes_success(self):
        """Test listing lotes successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_lotes_admin_sees_all(self):
        """Test admin can see all lotes."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('lote-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 3)
    
    def test_list_lotes_with_finca_filter(self):
        """Test listing lotes with finca filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        response = self.client.get(url, {'finca': self.finca.id}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_lotes_with_variedad_filter(self):
        """Test listing lotes with variedad filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        response = self.client.get(url, {'variedad': 'Variety A'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_lotes_with_estado_filter(self):
        """Test listing lotes with estado filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        response = self.client.get(url, {'estado': 'activo'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_lotes_with_search(self):
        """Test listing lotes with search."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        response = self.client.get(url, {'search': 'Lote 1'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_lotes_with_pagination(self):
        """Test listing lotes with pagination."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        response = self.client.get(url, {'page': 1, 'page_size': 1}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
    
    def test_create_lote_success(self):
        """Test creating lote successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        lote_data = {
            'finca': self.finca.id,
            'identificador': 'New Lote',
            'variedad': 'New Variety',
            'fecha_plantacion': '2020-01-01',
            'area_hectareas': 1.5
        }
        
        response = self.client.post(url, lote_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lote.objects.filter(identificador='New Lote', finca=self.finca).exists())
    
    def test_create_lote_missing_required_fields(self):
        """Test creating lote with missing required fields."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        lote_data = {
            'identificador': 'New Lote'
        }
        
        response = self.client.post(url, lote_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_lote_without_finca(self):
        """Test creating lote without finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        lote_data = {
            'identificador': 'New Lote',
            'variedad': 'New Variety',
            'fecha_plantacion': '2020-01-01',
            'area_hectareas': 1.5
        }
        
        response = self.client.post(url, lote_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_lote_permission_denied(self):
        """Test creating lote in other user's finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        lote_data = {
            'finca': self.other_finca.id,
            'identificador': 'Unauthorized Lote',
            'variedad': 'New Variety',
            'fecha_plantacion': '2020-01-01',
            'area_hectareas': 1.5
        }
        
        response = self.client.post(url, lote_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_create_lote_finca_not_found(self):
        """Test creating lote with non-existent finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-list')
        
        lote_data = {
            'finca': 99999,
            'identificador': 'New Lote',
            'variedad': 'New Variety',
            'fecha_plantacion': '2020-01-01',
            'area_hectareas': 1.5
        }
        
        response = self.client.post(url, lote_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_create_lote_unauthenticated(self):
        """Test creating lote without authentication."""
        url = reverse('lote-list')
        
        lote_data = {
            'finca': self.finca.id,
            'identificador': 'New Lote',
            'variedad': 'New Variety',
            'fecha_plantacion': '2020-01-01',
            'area_hectareas': 1.5
        }
        
        response = self.client.post(url, lote_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_lotes_unauthenticated(self):
        """Test listing lotes without authentication."""
        url = reverse('lote-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LoteDetailViewTest(APITestCase):
    """Tests for LoteDetailView."""
    
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
            agricultor=self.user,
            activa=True
        )
        
        self.lote = Lote.objects.create(
            finca=self.finca,
            identificador='Test Lote',
            variedad='Test Variety',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_lote_detail_success(self):
        """Test getting lote detail successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-detail', kwargs={'lote_id': self.lote.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lote.id)
        self.assertEqual(response.data['identificador'], 'Test Lote')
    
    def test_get_lote_detail_not_found(self):
        """Test getting non-existent lote."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-detail', kwargs={'lote_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_lote_detail_permission_denied(self):
        """Test getting lote detail without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('lote-detail', kwargs={'lote_id': self.lote.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_lote_detail_admin_access(self):
        """Test admin can access any lote."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('lote-detail', kwargs={'lote_id': self.lote.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lote.id)


class LoteUpdateViewTest(APITestCase):
    """Tests for LoteUpdateView."""
    
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
            agricultor=self.user,
            activa=True
        )
        
        self.lote = Lote.objects.create(
            finca=self.finca,
            identificador='Test Lote',
            variedad='Test Variety',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_update_lote_success(self):
        """Test updating lote successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-update', kwargs={'lote_id': self.lote.id})
        
        update_data = {
            'identificador': 'Updated Lote',
            'variedad': 'Updated Variety',
            'area_hectareas': 2.0
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lote.refresh_from_db()
        self.assertEqual(self.lote.identificador, 'Updated Lote')
        self.assertEqual(self.lote.variedad, 'Updated Variety')
        self.assertEqual(self.lote.area_hectareas, 2.0)
    
    def test_update_lote_partial(self):
        """Test partial update of lote."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-update', kwargs={'lote_id': self.lote.id})
        
        update_data = {
            'identificador': 'Partially Updated Lote'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lote.refresh_from_db()
        self.assertEqual(self.lote.identificador, 'Partially Updated Lote')
    
    def test_update_lote_permission_denied(self):
        """Test updating lote without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('lote-update', kwargs={'lote_id': self.lote.id})
        
        update_data = {'identificador': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_lote_not_found(self):
        """Test updating non-existent lote."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-update', kwargs={'lote_id': 99999})
        
        update_data = {'identificador': 'Updated Lote'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LoteDeleteViewTest(APITestCase):
    """Tests for LoteDeleteView."""
    
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
            agricultor=self.user,
            activa=True
        )
        
        self.lote = Lote.objects.create(
            finca=self.finca,
            identificador='Test Lote',
            variedad='Test Variety',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_delete_lote_success(self):
        """Test deleting lote successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-delete', kwargs={'lote_id': self.lote.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lote.objects.filter(id=self.lote.id).exists())
    
    def test_delete_lote_with_images(self):
        """Test deleting lote with associated images."""
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        CacaoImage.objects.create(
            user=self.user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            lote=self.lote,
            finca=self.finca
        )
        
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-delete', kwargs={'lote_id': self.lote.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertTrue(Lote.objects.filter(id=self.lote.id).exists())
    
    def test_delete_lote_permission_denied(self):
        """Test deleting lote without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('lote-delete', kwargs={'lote_id': self.lote.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Lote.objects.filter(id=self.lote.id).exists())
    
    def test_delete_lote_not_found(self):
        """Test deleting non-existent lote."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-delete', kwargs={'lote_id': 99999})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LoteStatsViewTest(APITestCase):
    """Tests for LoteStatsView."""
    
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
            agricultor=self.user,
            activa=True
        )
        
        self.lote = Lote.objects.create(
            finca=self.finca,
            identificador='Test Lote',
            variedad='Test Variety',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_lote_stats_success(self):
        """Test getting lote stats successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-stats', kwargs={'lote_id': self.lote.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lote_identificador', response.data)
        self.assertIn('finca_nombre', response.data)
        self.assertIn('agricultor_nombre', response.data)
        self.assertIn('ubicacion_completa', response.data)
    
    def test_get_lote_stats_not_found(self):
        """Test getting stats for non-existent lote."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lote-stats', kwargs={'lote_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_lote_stats_permission_denied(self):
        """Test getting lote stats without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('lote-stats', kwargs={'lote_id': self.lote.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LotesPorFincaViewTest(APITestCase):
    """Tests for LotesPorFincaView."""
    
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
            agricultor=self.user,
            activa=True
        )
        
        self.lote1 = Lote.objects.create(
            finca=self.finca,
            identificador='Lote 1',
            variedad='Variety A',
            fecha_plantacion=date(2020, 1, 1),
            fecha_cosecha=date(2024, 1, 1),
            area_hectareas=1.0,
            estado='activo',
            activo=True
        )
        
        self.lote2 = Lote.objects.create(
            finca=self.finca,
            identificador='Lote 2',
            variedad='Variety B',
            fecha_plantacion=date(2021, 1, 1),
            fecha_cosecha=date(2024, 2, 1),
            area_hectareas=2.0,
            estado='activo',
            activo=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_lotes_por_finca_success(self):
        """Test getting lotes por finca successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lotes-por-finca', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('finca', response.data)
        self.assertIn('lotes', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(len(response.data['lotes']), 2)
        self.assertEqual(response.data['total'], 2)
    
    def test_get_lotes_por_finca_admin_access(self):
        """Test admin can access lotes from any finca."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('lotes-por-finca', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['lotes']), 2)
    
    def test_get_lotes_por_finca_permission_denied(self):
        """Test getting lotes por finca without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('lotes-por-finca', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_lotes_por_finca_not_found(self):
        """Test getting lotes for non-existent finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('lotes-por-finca', kwargs={'finca_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

