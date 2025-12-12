"""
Tests for lote service.
"""
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from django.contrib.auth.models import User
from fincas_app.services.lote_service import LoteService
from api.services.base import ServiceResult


@pytest.mark.django_db
class TestLoteService:
    """Tests for LoteService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return LoteService()
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def finca(self, user, municipio):
        """Create test finca."""
        from fincas_app.models import Finca
        return Finca.objects.create(
            agricultor=user,
            nombre='Test Finca',
            hectareas=Decimal('10.0'),
            municipio=municipio,
            ubicacion='Test Location'
        )
    
    def test_extract_lote_data(self, service):
        """Test extracting lote data."""
        lote_data = {
            'finca_id': 1,
            'area': 5.0,
            'nombre': 'Test Lote',
            'identificador': 'LOTE-001',
            'variedad': 'Criollo'
        }
        
        result = service._extract_lote_data(lote_data)
        
        assert result['finca_id'] == 1
        assert result['area_hectareas'] == 5.0
        assert result['nombre'] == 'Test Lote'
    
    def test_extract_lote_data_aliases(self, service):
        """Test extracting lote data with different field names."""
        lote_data = {
            'finca': 1,
            'hectareas': 5.0,
            'identificador': 'LOTE-001'
        }
        
        result = service._extract_lote_data(lote_data)
        
        assert result['finca_id'] == 1
        assert result['area_hectareas'] == 5.0
    
    def test_validate_lote_required_fields_missing_finca(self, service):
        """Test validating lote with missing finca."""
        result = service._validate_lote_required_fields(None, 5.0, 'Test', 'LOTE-001')
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_required_fields_missing_area(self, service):
        """Test validating lote with missing area."""
        result = service._validate_lote_required_fields(1, None, 'Test', 'LOTE-001')
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_required_fields_missing_name_and_id(self, service):
        """Test validating lote with missing name and identifier."""
        result = service._validate_lote_required_fields(1, 5.0, '', '')
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_area_negative(self, service, finca):
        """Test validating negative area."""
        result = service._validate_lote_area(-1, finca)
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_area_exceeds_finca(self, service, finca):
        """Test validating area that exceeds finca area."""
        result = service._validate_lote_area(20.0, finca)
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_text_fields_duplicate_identifier(self, service, finca):
        """Test validating duplicate identifier."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        result = service._validate_lote_text_fields('Test', 'LOTE-001', 'Criollo', finca)
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_text_fields_short_name(self, service, finca):
        """Test validating short name."""
        result = service._validate_lote_text_fields('A', 'LOTE-001', 'Criollo', finca)
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_text_fields_missing_variedad(self, service, finca):
        """Test validating missing variedad."""
        result = service._validate_lote_text_fields('Test', 'LOTE-001', '', finca)
        
        assert result is not None
        assert not result.success
    
    def test_create_lote_success(self, service, user, finca):
        """Test creating lote successfully."""
        from datetime import date
        lote_data = {
            'finca_id': finca.id,
            'area_hectareas': 5.0,
            'nombre': 'Test Lote',
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'estado': 'activo',
            'fecha_plantacion': date.today()
        }
        
        result = service.create_lote(lote_data, user)
        
        assert result.success
        assert result.data['identificador'] == 'LOTE-001'
    
    def test_get_finca_lotes(self, service, user, finca):
        """Test getting finca lotes."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        result = service.get_finca_lotes(finca.id, user, page=1, page_size=20)
        
        assert result.success
        assert len(result.data['lotes']) >= 1
    
    def test_get_finca_lotes_with_filters(self, service, user, finca):
        """Test getting finca lotes with filters."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            estado='activo',
            fecha_plantacion=date.today()
        )
        
        filters = {'estado': 'activo', 'variedad': 'Criollo'}
        result = service.get_finca_lotes(finca.id, user, page=1, page_size=20, filters=filters)
        
        assert result.success
    
    def test_get_lote_details(self, service, user, finca):
        """Test getting lote details."""
        from fincas_app.models import Lote
        from datetime import date
        lote = Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        result = service.get_lote_details(lote.id, user)
        
        assert result.success
        assert result.data['id'] == lote.id
        assert 'finca' in result.data
    
    def test_get_lote_details_not_found(self, service, user):
        """Test getting lote details when not found."""
        result = service.get_lote_details(999, user)
        
        assert not result.success
    
    def test_update_lote_success(self, service, user, finca):
        """Test updating lote successfully."""
        from fincas_app.models import Lote
        from datetime import date
        lote = Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        lote_data = {
            'variedad': 'Forastero',
            'descripcion': 'Updated description'
        }
        
        result = service.update_lote(lote.id, user, lote_data)
        
        assert result.success
        lote.refresh_from_db()
        assert lote.variedad == 'Forastero'
    
    def test_update_lote_duplicate_identifier(self, service, user, finca):
        """Test updating lote with duplicate identifier."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote 1',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        lote2 = Lote.objects.create(
            finca=finca,
            nombre='Test Lote 2',
            identificador='LOTE-002',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        lote_data = {'identificador': 'LOTE-001'}
        
        result = service.update_lote(lote2.id, user, lote_data)
        
        assert not result.success
    
    def test_delete_lote_success(self, service, user, finca):
        """Test deleting lote successfully."""
        from fincas_app.models import Lote
        from datetime import date
        lote = Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        result = service.delete_lote(lote.id, user)
        
        assert result.success
        assert not Lote.objects.filter(id=lote.id).exists()
    
    def test_get_lote_statistics(self, service, user, finca):
        """Test getting lote statistics."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            estado='activo',
            fecha_plantacion=date.today()
        )
        
        result = service.get_lote_statistics(user)
        
        assert result.success
        assert 'total_lotes' in result.data
        assert result.data['total_lotes'] >= 1
    
    def test_get_finca_lotes_stats(self, service, user, finca):
        """Test getting finca lote statistics."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        result = service.get_finca_lotes_stats(finca.id, user)
        
        assert result.success
        assert 'lotes_stats' in result.data
    
    def test_count_finca_lotes(self, service, finca):
        """Test counting finca lotes."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        count = service.count_finca_lotes(finca.id)
        
        assert count == 1
    
    def test_serialize_lote(self, service, finca):
        """Test serializing lote."""
        from fincas_app.models import Lote
        from datetime import date
        lote = Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        result = service._serialize_lote(lote)
        
        assert result['id'] == lote.id
        assert result['identificador'] == 'LOTE-001'
        assert 'area_hectareas' in result
        assert 'area' in result  # Alias
        assert 'hectareas' in result  # Alias

