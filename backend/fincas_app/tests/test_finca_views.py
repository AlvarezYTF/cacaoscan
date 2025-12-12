"""
Tests for finca views.
"""
import pytest
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.contrib.auth.models import User
from decimal import Decimal

from fincas_app.views.finca.finca_views import (
    FincaListCreateView,
    FincaDetailView,
    FincaUpdateView,
    FincaDeleteView,
    FincaActivateView,
    FincaStatsView
)


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def user(db):
    """Create test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """Create admin user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_superuser(
        username=f'admin_{unique_id}',
        email=f'admin_{unique_id}@example.com',
        password='adminpass123'
    )


@pytest.fixture
def finca(user, municipio):
    """Create test finca."""
    from fincas_app.models import Finca
    return Finca.objects.create(
        nombre='Test Finca',
        ubicacion='Test Location',
        municipio=municipio,
        hectareas=Decimal('10.5'),
        agricultor=user,
        activa=True
    )


class TestFincaListCreateView:
    """Tests for FincaListCreateView class."""
    
    def test_get_list_fincas(self, request_factory, user, finca):
        """Test GET list fincas."""
        view = FincaListCreateView.as_view()
        request = request_factory.get('/api/fincas/')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_list_fincas_with_search(self, request_factory, user, finca):
        """Test GET list fincas with search filter."""
        view = FincaListCreateView.as_view()
        request = request_factory.get('/api/fincas/?search=Test')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_list_fincas_with_municipio(self, request_factory, user, finca):
        """Test GET list fincas with municipio filter."""
        view = FincaListCreateView.as_view()
        request = request_factory.get('/api/fincas/?municipio=Test')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_list_fincas_with_departamento(self, request_factory, user, finca):
        """Test GET list fincas with departamento filter."""
        view = FincaListCreateView.as_view()
        request = request_factory.get('/api/fincas/?departamento=Test')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_list_fincas_with_agricultor(self, request_factory, user, finca):
        """Test GET list fincas with agricultor filter."""
        view = FincaListCreateView.as_view()
        request = request_factory.get(f'/api/fincas/?agricultor={user.id}')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_list_fincas_admin(self, request_factory, admin_user, finca):
        """Test GET list fincas for admin."""
        view = FincaListCreateView.as_view()
        request = request_factory.get('/api/fincas/')
        force_authenticate(request, user=admin_user)
        
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
    
    def test_post_create_finca(self, request_factory, user):
        """Test POST create finca."""
        view = FincaListCreateView.as_view()
        data = {
            'nombre': 'New Finca',
            'ubicacion': 'New Location',
            'municipio': 'New Municipio',
            'departamento': 'New Departamento',
            'hectareas': Decimal('15.0')
        }
        request = request_factory.post('/api/fincas/', data, format='json')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_post_create_finca_invalid_data(self, request_factory, user):
        """Test POST create finca with invalid data."""
        view = FincaListCreateView.as_view()
        data = {'nombre': 'A'}  # Too short
        request = request_factory.post('/api/fincas/', data, format='json')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestFincaDetailView:
    """Tests for FincaDetailView class."""
    
    def test_get_finca_detail(self, request_factory, user, finca):
        """Test GET finca detail."""
        view = FincaDetailView.as_view()
        request = request_factory.get(f'/api/fincas/{finca.id}/')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_finca_detail_not_found(self, request_factory, user):
        """Test GET finca detail not found."""
        view = FincaDetailView.as_view()
        request = request_factory.get('/api/fincas/99999/')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=99999)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFincaUpdateView:
    """Tests for FincaUpdateView class."""
    
    def test_put_update_finca(self, request_factory, user, finca):
        """Test PUT update finca."""
        view = FincaUpdateView.as_view()
        # PUT requires all fields, so include all required fields
        data = {
            'nombre': 'Updated Finca',
            'ubicacion': finca.ubicacion,
            'municipio': finca.municipio,
            'departamento': finca.departamento,
            'hectareas': float(finca.hectareas)
        }
        request = request_factory.put(f'/api/fincas/{finca.id}/', data, format='json')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_200_OK
    
    def test_patch_update_finca(self, request_factory, user, finca):
        """Test PATCH update finca."""
        view = FincaUpdateView.as_view()
        data = {'nombre': 'Patched Finca'}
        request = request_factory.patch(f'/api/fincas/{finca.id}/', data, format='json')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_finca_not_found(self, request_factory, user):
        """Test update finca not found."""
        view = FincaUpdateView.as_view()
        data = {'nombre': 'Updated Finca'}
        request = request_factory.put('/api/fincas/99999/', data, format='json')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=99999)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFincaDeleteView:
    """Tests for FincaDeleteView class."""
    
    def test_delete_finca(self, request_factory, user, finca):
        """Test DELETE finca."""
        view = FincaDeleteView.as_view()
        request = request_factory.delete(f'/api/fincas/{finca.id}/')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_finca_not_found(self, request_factory, user):
        """Test DELETE finca not found."""
        view = FincaDeleteView.as_view()
        request = request_factory.delete('/api/fincas/99999/')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=99999)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFincaActivateView:
    """Tests for FincaActivateView class."""
    
    def test_post_activate_finca(self, request_factory, admin_user, finca):
        """Test POST activate finca (admin only)."""
        finca.activa = False
        finca.save()
        
        view = FincaActivateView.as_view()
        request = request_factory.post(f'/api/fincas/{finca.id}/activate/')
        force_authenticate(request, user=admin_user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_200_OK
    
    def test_activate_finca_not_found(self, request_factory, admin_user):
        """Test activate finca not found."""
        view = FincaActivateView.as_view()
        request = request_factory.post('/api/fincas/99999/activate/')
        force_authenticate(request, user=admin_user)
        
        response = view(request, finca_id=99999)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFincaStatsView:
    """Tests for FincaStatsView class."""
    
    def test_get_finca_stats(self, request_factory, user, finca):
        """Test GET finca stats."""
        view = FincaStatsView.as_view()
        request = request_factory.get(f'/api/fincas/{finca.id}/stats/')
        force_authenticate(request, user=user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_finca_stats_admin(self, request_factory, admin_user, finca):
        """Test GET finca stats for admin."""
        view = FincaStatsView.as_view()
        request = request_factory.get(f'/api/fincas/{finca.id}/stats/')
        force_authenticate(request, user=admin_user)
        
        response = view(request, finca_id=finca.id)
        assert response.status_code == status.HTTP_200_OK

