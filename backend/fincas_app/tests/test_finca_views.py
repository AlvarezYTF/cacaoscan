"""
Tests for Fincas App finca views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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


class FincaListCreateViewTest(APITestCase):
    """Tests for FincaListCreateView."""
    
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
        
        self.finca1 = Finca.objects.create(
            nombre='Finca Test 1',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user,
            activa=True
        )
        
        self.finca2 = Finca.objects.create(
            nombre='Finca Test 2',
            ubicacion='Vereda Test 2',
            municipio='Test Municipio 2',
            departamento='Test Departamento 2',
            hectareas=3.0,
            agricultor=self.user,
            activa=True
        )
        
        self.other_finca = Finca.objects.create(
            nombre='Other Finca',
            ubicacion='Other Location',
            municipio='Other Municipio',
            departamento='Other Departamento',
            hectareas=2.0,
            agricultor=self.other_user,
            activa=True
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_fincas_success(self):
        """Test listing fincas successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_fincas_admin_sees_all(self):
        """Test admin can see all fincas."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('finca-list')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 3)
    
    def test_list_fincas_with_search(self):
        """Test listing fincas with search filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        response = self.client.get(url, {'search': 'Test 1'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Finca Test 1')
    
    def test_list_fincas_with_municipio_filter(self):
        """Test listing fincas with municipio filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        response = self.client.get(url, {'municipio': 'Test Municipio'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_fincas_with_departamento_filter(self):
        """Test listing fincas with departamento filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        response = self.client.get(url, {'departamento': 'Test Departamento'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_fincas_with_agricultor_filter(self):
        """Test listing fincas with agricultor filter."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('finca-list')
        
        response = self.client.get(url, {'agricultor': self.user.id}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_fincas_with_pagination(self):
        """Test listing fincas with pagination."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        response = self.client.get(url, {'page': 1, 'page_size': 1}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
    
    def test_create_finca_success(self):
        """Test creating finca successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        finca_data = {
            'nombre': 'New Finca',
            'ubicacion': 'New Location',
            'municipio': 'New Municipio',
            'departamento': 'New Departamento',
            'hectareas': 10.0
        }
        
        response = self.client.post(url, finca_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Finca.objects.filter(nombre='New Finca', agricultor=self.user).exists())
    
    def test_create_finca_missing_required_fields(self):
        """Test creating finca with missing required fields."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-list')
        
        finca_data = {
            'nombre': 'New Finca'
        }
        
        response = self.client.post(url, finca_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_finca_unauthenticated(self):
        """Test creating finca without authentication."""
        url = reverse('finca-list')
        
        finca_data = {
            'nombre': 'New Finca',
            'ubicacion': 'New Location',
            'municipio': 'New Municipio',
            'departamento': 'New Departamento',
            'hectareas': 10.0
        }
        
        response = self.client.post(url, finca_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_fincas_unauthenticated(self):
        """Test listing fincas without authentication."""
        url = reverse('finca-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FincaDetailViewTest(APITestCase):
    """Tests for FincaDetailView."""
    
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
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_finca_detail_success(self):
        """Test getting finca detail successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-detail', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.finca.id)
        self.assertEqual(response.data['nombre'], 'Test Finca')
    
    def test_get_finca_detail_not_found(self):
        """Test getting non-existent finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-detail', kwargs={'finca_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_finca_detail_permission_denied(self):
        """Test getting finca detail without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('finca-detail', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_finca_detail_admin_access(self):
        """Test admin can access any finca."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('finca-detail', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.finca.id)


class FincaUpdateViewTest(APITestCase):
    """Tests for FincaUpdateView."""
    
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
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_update_finca_success(self):
        """Test updating finca successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-update', kwargs={'finca_id': self.finca.id})
        
        update_data = {
            'nombre': 'Updated Finca',
            'ubicacion': 'Updated Location',
            'municipio': 'Updated Municipio',
            'departamento': 'Updated Departamento',
            'hectareas': 7.0
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.finca.refresh_from_db()
        self.assertEqual(self.finca.nombre, 'Updated Finca')
        self.assertEqual(self.finca.hectareas, 7.0)
    
    def test_update_finca_partial(self):
        """Test partial update of finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-update', kwargs={'finca_id': self.finca.id})
        
        update_data = {
            'nombre': 'Partially Updated Finca'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.finca.refresh_from_db()
        self.assertEqual(self.finca.nombre, 'Partially Updated Finca')
    
    def test_update_finca_permission_denied(self):
        """Test updating finca without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('finca-update', kwargs={'finca_id': self.finca.id})
        
        update_data = {'nombre': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_finca_not_found(self):
        """Test updating non-existent finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-update', kwargs={'finca_id': 99999})
        
        update_data = {'nombre': 'Updated Finca'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FincaDeleteViewTest(APITestCase):
    """Tests for FincaDeleteView."""
    
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
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_delete_finca_success(self):
        """Test deleting finca successfully (soft delete)."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-delete', kwargs={'finca_id': self.finca.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.finca.refresh_from_db()
        self.assertFalse(self.finca.activa)
    
    def test_delete_finca_already_inactive(self):
        """Test deleting already inactive finca."""
        self.finca.activa = False
        self.finca.save()
        
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-delete', kwargs={'finca_id': self.finca.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_delete_finca_permission_denied(self):
        """Test deleting finca without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('finca-delete', kwargs={'finca_id': self.finca.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_finca_not_found(self):
        """Test deleting non-existent finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-delete', kwargs={'finca_id': 99999})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FincaActivateViewTest(APITestCase):
    """Tests for FincaActivateView."""
    
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
            agricultor=self.user,
            activa=False
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_activate_finca_success(self):
        """Test activating finca successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('finca-activate', kwargs={'finca_id': self.finca.id})
        
        response = self.client.post(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.finca.refresh_from_db()
        self.assertTrue(self.finca.activa)
    
    def test_activate_finca_already_active(self):
        """Test activating already active finca."""
        self.finca.activa = True
        self.finca.save()
        
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('finca-activate', kwargs={'finca_id': self.finca.id})
        
        response = self.client.post(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_activate_finca_permission_denied(self):
        """Test non-admin cannot activate finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-activate', kwargs={'finca_id': self.finca.id})
        
        response = self.client.post(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_activate_finca_not_found(self):
        """Test activating non-existent finca."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('finca-activate', kwargs={'finca_id': 99999})
        
        response = self.client.post(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FincaStatsViewTest(APITestCase):
    """Tests for FincaStatsView."""
    
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
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_finca_stats_success(self):
        """Test getting finca stats successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-stats', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('finca_nombre', response.data)
        self.assertIn('agricultor_nombre', response.data)
        self.assertIn('ubicacion_completa', response.data)
    
    def test_get_finca_stats_not_found(self):
        """Test getting stats for non-existent finca."""
        headers = self._get_auth_headers(self.user)
        url = reverse('finca-stats', kwargs={'finca_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_finca_stats_permission_denied(self):
        """Test getting finca stats without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('finca-stats', kwargs={'finca_id': self.finca.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

