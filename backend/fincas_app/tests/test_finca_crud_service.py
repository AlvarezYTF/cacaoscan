"""
Tests for FincaCRUDService.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from django.contrib.auth.models import User

from fincas_app.services.finca.finca_crud_service import FincaCRUDService
from api.services.base import ValidationServiceError


@pytest.fixture
def service():
    """Create FincaCRUDService instance."""
    return FincaCRUDService()


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
def finca_data():
    """Create test finca data."""
    return {
        'nombre': 'Test Finca',
        'ubicacion': 'Test Location',
        'municipio': 'Test Municipio',
        'departamento': 'Test Departamento',
        'hectareas': Decimal('10.5'),
        'activa': True,
        'descripcion': 'Test Description'
    }


@pytest.mark.django_db
class TestFincaCRUDService:
    """Tests for FincaCRUDService class."""
    
    def test_create_finca(self, service, user, finca_data):
        """Test create_finca method."""
        result = service.create_finca(finca_data, user)
        assert result.success is True
        assert 'data' in result.data
        assert result.data['data']['nombre'] == 'Test Finca'
    
    def test_create_finca_validation_error(self, service, user):
        """Test create_finca with validation error."""
        invalid_data = {'nombre': 'A'}  # Too short
        result = service.create_finca(invalid_data, user)
        assert result.success is False
    
    def test_create_finca_without_hectareas(self, service, user):
        """Test create_finca without hectareas."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento'
        }
        result = service.create_finca(data, user)
        assert result.success is False
    
    def test_create_finca_with_negative_hectareas(self, service, user):
        """Test create_finca with negative hectareas."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': -10
        }
        result = service.create_finca(data, user)
        assert result.success is False
    
    def test_create_finca_with_area_total(self, service, user):
        """Test create_finca with area_total alias."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'area_total': Decimal('10.5')
        }
        result = service.create_finca(data, user)
        assert result.success is True
    
    def test_create_finca_with_propietario(self, service, user, admin_user):
        """Test create_finca with propietario alias."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': Decimal('10.5'),
            'propietario': admin_user
        }
        result = service.create_finca(data, user)
        assert result.success is True
    
    def test_get_user_fincas(self, service, user, finca_data):
        """Test get_user_fincas method."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.get_user_fincas(user)
            assert result.success is True
            assert 'fincas' in result.data
            assert len(result.data['fincas']) > 0
    
    def test_get_user_fincas_admin(self, service, admin_user, user, finca_data):
        """Test get_user_fincas for admin user."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.get_user_fincas(admin_user)
            assert result.success is True
            assert 'fincas' in result.data
    
    def test_get_user_fincas_with_filters(self, service, user, finca_data):
        """Test get_user_fincas with filters."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        filters = {'activa': True, 'departamento': 'Test Departamento'}
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.get_user_fincas(user, filters=filters)
            assert result.success is True
    
    def test_get_user_fincas_with_search(self, service, user, finca_data):
        """Test get_user_fincas with search filter."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        filters = {'search': 'Test'}
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.get_user_fincas(user, filters=filters)
            assert result.success is True
    
    def test_get_user_fincas_pagination(self, service, user, finca_data):
        """Test get_user_fincas with pagination."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.get_user_fincas(user, page=1, page_size=10)
            assert result.success is True
            assert 'pagination' in result.data
    
    def test_get_finca_details(self, service, user, finca_data):
        """Test get_finca_details method."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        # Mock lote_service methods
        from api.services.base import ServiceResult
        with patch.object(service.lote_service, 'get_finca_lotes_stats') as mock_stats:
            mock_stats.return_value = ServiceResult.success(data={'lotes_stats': {}, 'lotes_recientes': []})
            with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
                result = service.get_finca_details(finca_id, user)
                assert result.success is True
                assert result.data['nombre'] == 'Test Finca'
    
    def test_get_finca_details_not_found(self, service, user):
        """Test get_finca_details with non-existent finca."""
        result = service.get_finca_details(99999, user)
        assert result.success is False
    
    def test_get_finca_details_admin(self, service, admin_user, user, finca_data):
        """Test get_finca_details for admin user."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        # Mock lote_service methods
        from api.services.base import ServiceResult
        with patch.object(service.lote_service, 'get_finca_lotes_stats') as mock_stats:
            mock_stats.return_value = ServiceResult.success(data={'lotes_stats': {}, 'lotes_recientes': []})
            with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
                result = service.get_finca_details(finca_id, admin_user)
                assert result.success is True
    
    def test_update_finca(self, service, user, finca_data):
        """Test update_finca method."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        
        update_data = {'nombre': 'Updated Finca'}
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.update_finca(finca_id, user, update_data)
            assert result.success is True
            assert result.data['data']['nombre'] == 'Updated Finca'
    
    def test_update_finca_not_found(self, service, user):
        """Test update_finca with non-existent finca."""
        result = service.update_finca(99999, user, {'nombre': 'Test'})
        assert result.success is False
    
    def test_update_finca_with_area_total(self, service, user, finca_data):
        """Test update_finca with area_total alias."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        
        update_data = {'area_total': Decimal('20.0')}
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.update_finca(finca_id, user, update_data)
            assert result.success is True
    
    def test_update_finca_with_propietario(self, service, user, admin_user, finca_data):
        """Test update_finca with propietario alias."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        
        update_data = {'propietario': admin_user}
        # Mock lote_service to avoid issues
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.update_finca(finca_id, user, update_data)
            assert result.success is True
    
    def test_delete_finca(self, service, user, finca_data):
        """Test delete_finca method."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        
        # Mock lote_service to return 0 lotes so deletion can proceed
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            result = service.delete_finca(finca_id, user)
            assert result.success is True
    
    def test_delete_finca_not_found(self, service, user):
        """Test delete_finca with non-existent finca."""
        result = service.delete_finca(99999, user)
        assert result.success is False
    
    def test_delete_finca_with_lotes(self, service, user, finca_data):
        """Test delete_finca with associated lotes."""
        create_result = service.create_finca(finca_data, user)
        finca_id = create_result.data['data']['id']
        
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=5):
            result = service.delete_finca(finca_id, user)
            assert result.success is False
    
    def test_serialize_finca(self, service, user, finca_data):
        """Test _serialize_finca method."""
        create_result = service.create_finca(finca_data, user)
        assert create_result.success is True
        finca_id = create_result.data['data']['id']
        
        from fincas_app.models import Finca
        # Get finca first, then mock lote_service to avoid transaction issues
        finca = Finca.objects.get(id=finca_id)
        # Mock lote_service to avoid transaction issues and ensure it works
        # Use patch before calling _serialize_finca to avoid transaction errors
        with patch.object(service.lote_service, 'count_finca_lotes', return_value=0):
            serialized = service._serialize_finca(finca)
        
        assert 'id' in serialized
        assert 'nombre' in serialized
        assert 'hectareas' in serialized
        assert 'area_total' in serialized
        assert 'propietario' in serialized


