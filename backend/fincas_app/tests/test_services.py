"""
Tests for Fincas App Services.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from decimal import Decimal

from fincas_app.services.finca.finca_crud_service import FincaCRUDService
from fincas_app.services.finca.finca_stats_service import FincaStatsService
from fincas_app.services.finca.finca_validation_service import FincaValidationService
from fincas_app.services.lote_service import LoteService


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='farmer',
        email='farmer@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def finca_data():
    """Valid finca data."""
    return {
        'nombre': 'Finca Test',
        'ubicacion': 'Vereda El Test',
        'municipio': 'Medellín',
        'departamento': 'Antioquia',
        'hectareas': 10.5,
        'activa': True,
        'descripcion': 'Finca de prueba'
    }


@pytest.fixture
def lote_data():
    """Valid lote data."""
    return {
        'nombre': 'Lote 1',
        'identificador': 'L1',
        'variedad': 'Criollo',
        'area_hectareas': 5.0,
        'estado': 'activo',
        'descripcion': 'Lote de prueba'
    }


@pytest.mark.django_db
class TestFincaCRUDService:
    """Tests for FincaCRUDService."""

    def test_create_finca_success(self, user, finca_data):
        """Test successful finca creation."""
        service = FincaCRUDService()
        
        result = service.create_finca(finca_data, user)
        
        assert result.success is True
        assert result.data['nombre'] == 'Finca Test'
        assert result.data['hectareas'] == Decimal('10.5')
        assert result.message == "Finca creada exitosamente"
        
        # Verify finca was created
        from fincas_app.models import Finca
        finca = Finca.objects.get(nombre='Finca Test')
        assert finca.agricultor == user

    def test_create_finca_missing_required_fields(self, user):
        """Test finca creation with missing required fields."""
        service = FincaCRUDService()
        
        incomplete_data = {'nombre': 'Test Finca'}
        result = service.create_finca(incomplete_data, user)
        
        assert result.success is False
        assert 'requerido' in str(result.error).lower() or 'required' in str(result.error).lower()

    def test_create_finca_invalid_hectareas(self, user, finca_data):
        """Test finca creation with invalid hectareas."""
        service = FincaCRUDService()
        
        finca_data['hectareas'] = -5  # Negative
        result = service.create_finca(finca_data, user)
        
        assert result.success is False
        assert 'hectáreas' in str(result.error).lower() or 'mayor' in str(result.error).lower()

    def test_create_finca_area_total_alias(self, user, finca_data):
        """Test finca creation using area_total alias."""
        service = FincaCRUDService()
        
        finca_data.pop('hectareas')
        finca_data['area_total'] = 10.5
        
        result = service.create_finca(finca_data, user)
        
        assert result.success is True
        assert result.data['hectareas'] == Decimal('10.5')

    def test_get_user_fincas_success(self, user, finca_data):
        """Test getting user fincas successfully."""
        service = FincaCRUDService()
        
        # Create a finca first
        service.create_finca(finca_data, user)
        
        result = service.get_user_fincas(user, page=1, page_size=20)
        
        assert result.success is True
        assert 'fincas' in result.data
        assert len(result.data['fincas']) >= 1
        assert 'pagination' in result.data

    def test_get_user_fincas_with_filters(self, user, finca_data):
        """Test getting fincas with filters."""
        service = FincaCRUDService()
        
        # Create fincas
        service.create_finca(finca_data, user)
        finca_data['nombre'] = 'Finca 2'
        finca_data['activa'] = False
        service.create_finca(finca_data, user)
        
        filters = {'activa': True}
        result = service.get_user_fincas(user, page=1, page_size=20, filters=filters)
        
        assert result.success is True
        assert all(f['activa'] for f in result.data['fincas'])

    def test_get_user_fincas_admin_sees_all(self, user, admin_user, finca_data):
        """Test that admin can see all fincas."""
        service = FincaCRUDService()
        
        # Create finca for regular user
        service.create_finca(finca_data, user)
        
        # Admin should see it
        result = service.get_user_fincas(admin_user, page=1, page_size=20)
        
        assert result.success is True
        assert len(result.data['fincas']) >= 1

    def test_get_finca_details_success(self, user, finca_data):
        """Test getting finca details successfully."""
        service = FincaCRUDService()
        
        # Create a finca first
        create_result = service.create_finca(finca_data, user)
        finca_id = create_result.data['id']
        
        result = service.get_finca_details(finca_id, user)
        
        assert result.success is True
        assert result.data['id'] == finca_id
        assert result.data['nombre'] == 'Finca Test'
        assert 'lotes_stats' in result.data

    def test_get_finca_details_not_found(self, user):
        """Test getting non-existent finca."""
        service = FincaCRUDService()
        
        result = service.get_finca_details(99999, user)
        
        assert result.success is False
        assert 'no encontrada' in str(result.error).lower()

    def test_update_finca_success(self, user, finca_data):
        """Test updating finca successfully."""
        service = FincaCRUDService()
        
        # Create a finca first
        create_result = service.create_finca(finca_data, user)
        finca_id = create_result.data['id']
        
        update_data = {
            'nombre': 'Finca Actualizada',
            'descripcion': 'Nueva descripción'
        }
        
        result = service.update_finca(finca_id, user, update_data)
        
        assert result.success is True
        assert result.data['nombre'] == 'Finca Actualizada'
        assert result.data['descripcion'] == 'Nueva descripción'

    def test_update_finca_not_found(self, user):
        """Test updating non-existent finca."""
        service = FincaCRUDService()
        
        update_data = {'nombre': 'Updated'}
        result = service.update_finca(99999, user, update_data)
        
        assert result.success is False
        assert 'no encontrada' in str(result.error).lower()

    def test_delete_finca_success(self, user, finca_data):
        """Test deleting finca successfully."""
        service = FincaCRUDService()
        
        # Create a finca first
        create_result = service.create_finca(finca_data, user)
        finca_id = create_result.data['id']
        
        result = service.delete_finca(finca_id, user)
        
        assert result.success is True
        assert result.message == "Finca eliminada exitosamente"
        
        # Verify finca was deleted
        from fincas_app.models import Finca
        assert not Finca.objects.filter(id=finca_id).exists()

    def test_delete_finca_with_lotes(self, user, finca_data, lote_data):
        """Test deleting finca with associated lotes fails."""
        service = FincaCRUDService()
        lote_service = LoteService()
        
        # Create finca and lote
        create_result = service.create_finca(finca_data, user)
        finca_id = create_result.data['id']
        
        lote_data['finca_id'] = finca_id
        lote_service.create_lote(lote_data, user)
        
        result = service.delete_finca(finca_id, user)
        
        assert result.success is False
        assert 'lotes' in str(result.error).lower()


@pytest.mark.django_db
class TestFincaStatsService:
    """Tests for FincaStatsService."""

    def test_get_finca_statistics_success(self, user, finca_data):
        """Test getting finca statistics successfully."""
        service = FincaStatsService()
        
        # Create fincas
        crud_service = FincaCRUDService()
        crud_service.create_finca(finca_data, user)
        
        finca_data['nombre'] = 'Finca 2'
        finca_data['hectareas'] = 15.0
        crud_service.create_finca(finca_data, user)
        
        result = service.get_finca_statistics(user)
        
        assert result.success is True
        assert result.data['total_fincas'] >= 2
        assert 'fincas_activas' in result.data
        assert 'total_hectareas' in result.data
        assert 'departamentos' in result.data

    def test_get_finca_statistics_with_filters(self, user, finca_data):
        """Test getting statistics with filters."""
        service = FincaStatsService()
        
        # Create fincas
        crud_service = FincaCRUDService()
        crud_service.create_finca(finca_data, user)
        
        finca_data['nombre'] = 'Finca 2'
        finca_data['activa'] = False
        crud_service.create_finca(finca_data, user)
        
        filters = {'activa': True}
        result = service.get_finca_statistics(user, filters=filters)
        
        assert result.success is True
        assert result.data['fincas_activas'] >= 1
        assert result.data['fincas_inactivas'] == 0  # Filtered out

    def test_get_finca_statistics_admin_sees_all(self, user, admin_user, finca_data):
        """Test that admin sees all fincas in statistics."""
        service = FincaStatsService()
        
        # Create finca for regular user
        crud_service = FincaCRUDService()
        crud_service.create_finca(finca_data, user)
        
        # Admin should see it
        result = service.get_finca_statistics(admin_user)
        
        assert result.success is True
        assert result.data['total_fincas'] >= 1


@pytest.mark.django_db
class TestFincaValidationService:
    """Tests for FincaValidationService."""

    def test_validate_finca_data_valid(self, finca_data):
        """Test validating valid finca data."""
        service = FincaValidationService()
        
        result = service.validate_finca_data(finca_data, is_create=True)
        
        assert result['valid'] is True

    def test_validate_finca_data_missing_fields(self):
        """Test validating finca data with missing required fields."""
        service = FincaValidationService()
        
        incomplete_data = {'nombre': 'Test'}
        result = service.validate_finca_data(incomplete_data, is_create=True)
        
        assert result['valid'] is False
        assert 'error' in result

    def test_validate_finca_data_invalid_nombre(self, finca_data):
        """Test validating finca data with invalid nombre."""
        service = FincaValidationService()
        
        finca_data['nombre'] = 'A'  # Too short
        result = service.validate_finca_data(finca_data, is_create=True)
        
        assert result['valid'] is False

    def test_validate_finca_data_update_partial(self, finca_data):
        """Test validating finca data for update (partial)."""
        service = FincaValidationService()
        
        # Update should allow partial data
        update_data = {'nombre': 'Updated Name'}
        result = service.validate_finca_data(update_data, is_create=False)
        
        # Should be valid for update
        assert result['valid'] is True


@pytest.mark.django_db
class TestLoteService:
    """Tests for LoteService."""

    def test_create_lote_success(self, user, finca_data, lote_data):
        """Test successful lote creation."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        # Create finca first
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        result = service.create_lote(lote_data, user)
        
        assert result.success is True
        assert result.data['identificador'] == 'L1'
        assert result.data['variedad'] == 'Criollo'
        assert result.message == "Lote created successfully"
        
        # Verify lote was created
        from fincas_app.models import Lote
        lote = Lote.objects.get(identificador='L1')
        assert lote.finca.id == finca_id

    def test_create_lote_missing_finca_id(self, user, lote_data):
        """Test lote creation without finca_id."""
        service = LoteService()
        
        result = service.create_lote(lote_data, user)
        
        assert result.success is False
        assert 'finca' in str(result.error).lower()

    def test_create_lote_missing_area(self, user, finca_data, lote_data):
        """Test lote creation without area."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        lote_data['finca_id'] = finca_result.data['id']
        lote_data.pop('area_hectareas')
        
        result = service.create_lote(lote_data, user)
        
        assert result.success is False
        assert 'área' in str(result.error).lower() or 'area' in str(result.error).lower()

    def test_create_lote_area_exceeds_finca(self, user, finca_data, lote_data):
        """Test lote creation with area exceeding finca area."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        lote_data['area_hectareas'] = 100.0  # Exceeds finca's 10.5 ha
        
        result = service.create_lote(lote_data, user)
        
        assert result.success is False
        assert 'exceder' in str(result.error).lower() or 'exceed' in str(result.error).lower()

    def test_create_lote_duplicate_identificador(self, user, finca_data, lote_data):
        """Test lote creation with duplicate identificador."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        service.create_lote(lote_data, user)
        
        # Try to create another with same identificador
        lote_data['nombre'] = 'Lote 2'
        result = service.create_lote(lote_data, user)
        
        assert result.success is False
        assert 'identificador' in str(result.error).lower()

    def test_get_finca_lotes_success(self, user, finca_data, lote_data):
        """Test getting finca lotes successfully."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        # Create finca and lotes
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        service.create_lote(lote_data, user)
        
        result = service.get_finca_lotes(finca_id, user, page=1, page_size=20)
        
        assert result.success is True
        assert 'lotes' in result.data
        assert len(result.data['lotes']) >= 1
        assert 'pagination' in result.data

    def test_get_finca_lotes_with_filters(self, user, finca_data, lote_data):
        """Test getting lotes with filters."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        service.create_lote(lote_data, user)
        
        lote_data['identificador'] = 'L2'
        lote_data['estado'] = 'inactivo'
        service.create_lote(lote_data, user)
        
        filters = {'estado': 'activo'}
        result = service.get_finca_lotes(finca_id, user, page=1, page_size=20, filters=filters)
        
        assert result.success is True
        assert all(l['estado'] == 'activo' for l in result.data['lotes'])

    def test_get_lote_details_success(self, user, finca_data, lote_data):
        """Test getting lote details successfully."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        create_result = service.create_lote(lote_data, user)
        lote_id = create_result.data['id']
        
        result = service.get_lote_details(lote_id, user)
        
        assert result.success is True
        assert result.data['id'] == lote_id
        assert result.data['identificador'] == 'L1'
        assert 'finca' in result.data

    def test_get_lote_details_not_found(self, user):
        """Test getting non-existent lote."""
        service = LoteService()
        
        result = service.get_lote_details(99999, user)
        
        assert result.success is False
        assert 'not found' in str(result.error).lower()

    def test_update_lote_success(self, user, finca_data, lote_data):
        """Test updating lote successfully."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        create_result = service.create_lote(lote_data, user)
        lote_id = create_result.data['id']
        
        update_data = {
            'variedad': 'Trinitario',
            'descripcion': 'Updated description'
        }
        
        result = service.update_lote(lote_id, user, update_data)
        
        assert result.success is True
        assert result.data['variedad'] == 'Trinitario'
        assert result.data['descripcion'] == 'Updated description'

    def test_update_lote_area_exceeds_finca(self, user, finca_data, lote_data):
        """Test updating lote with area exceeding finca."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        create_result = service.create_lote(lote_data, user)
        lote_id = create_result.data['id']
        
        update_data = {'area_hectareas': 100.0}  # Exceeds finca
        
        result = service.update_lote(lote_id, user, update_data)
        
        assert result.success is False
        assert 'exceder' in str(result.error).lower() or 'exceed' in str(result.error).lower()

    def test_delete_lote_success(self, user, finca_data, lote_data):
        """Test deleting lote successfully."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        create_result = service.create_lote(lote_data, user)
        lote_id = create_result.data['id']
        
        result = service.delete_lote(lote_id, user)
        
        assert result.success is True
        assert result.message == "Lote deleted successfully"
        
        # Verify lote was deleted
        from fincas_app.models import Lote
        assert not Lote.objects.filter(id=lote_id).exists()

    def test_get_lote_statistics(self, user, finca_data, lote_data):
        """Test getting lote statistics."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        service.create_lote(lote_data, user)
        
        result = service.get_lote_statistics(user)
        
        assert result.success is True
        assert result.data['total_lotes'] >= 1
        assert 'lotes_activos' in result.data
        assert 'total_hectareas' in result.data
        assert 'variedades' in result.data

    def test_get_finca_lotes_stats(self, user, finca_data, lote_data):
        """Test getting finca lotes statistics."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        service.create_lote(lote_data, user)
        
        result = service.get_finca_lotes_stats(finca_id, user)
        
        assert result.success is True
        assert 'lotes_stats' in result.data
        assert 'lotes_recientes' in result.data

    def test_count_finca_lotes(self, user, finca_data, lote_data):
        """Test counting finca lotes."""
        service = LoteService()
        crud_service = FincaCRUDService()
        
        finca_result = crud_service.create_finca(finca_data, user)
        finca_id = finca_result.data['id']
        
        lote_data['finca_id'] = finca_id
        service.create_lote(lote_data, user)
        
        count = service.count_finca_lotes(finca_id)
        
        assert count >= 1

