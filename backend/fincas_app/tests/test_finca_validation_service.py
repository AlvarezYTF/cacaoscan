"""
Tests for FincaValidationService.
"""
import pytest
from unittest.mock import patch
from decimal import Decimal

from fincas_app.services.finca.finca_validation_service import FincaValidationService
from api.services.base import ValidationServiceError


@pytest.fixture
def service():
    """Create FincaValidationService instance."""
    return FincaValidationService()


@pytest.fixture
def valid_finca_data():
    """Create valid finca data."""
    return {
        'nombre': 'Test Finca',
        'ubicacion': 'Test Location Address',
        'municipio': 'Test Municipio',
        'departamento': 'Test Departamento',
        'hectareas': Decimal('10.5')
    }


class TestFincaValidationService:
    """Tests for FincaValidationService class."""
    
    def test_validate_finca_data_create_valid(self, service, valid_finca_data):
        """Test validate_finca_data for create with valid data."""
        result = service.validate_finca_data(valid_finca_data, is_create=True)
        assert result['valid'] is True
    
    def test_validate_finca_data_create_missing_required(self, service):
        """Test validate_finca_data for create with missing required fields."""
        data = {'nombre': 'Test'}
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
        assert 'error' in result
    
    def test_validate_finca_data_create_short_nombre(self, service):
        """Test validate_finca_data with too short nombre."""
        data = {
            'nombre': 'A',
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_long_nombre(self, service):
        """Test validate_finca_data with too long nombre."""
        data = {
            'nombre': 'A' * 201,
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_short_ubicacion(self, service):
        """Test validate_finca_data with too short ubicacion."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test',
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_long_ubicacion(self, service):
        """Test validate_finca_data with too long ubicacion."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'A' * 301,
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_short_municipio(self, service):
        """Test validate_finca_data with too short municipio."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'A',
            'departamento': 'Test',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_long_municipio(self, service):
        """Test validate_finca_data with too long municipio."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'A' * 101,
            'departamento': 'Test',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_short_departamento(self, service):
        """Test validate_finca_data with too short departamento."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'A',
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_long_departamento(self, service):
        """Test validate_finca_data with too long departamento."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'A' * 101,
            'hectareas': Decimal('10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_invalid_hectareas_type(self, service):
        """Test validate_finca_data with invalid hectareas type."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': 'not a number'
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_negative_hectareas(self, service):
        """Test validate_finca_data with negative hectareas."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': Decimal('-10.5')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_create_small_hectareas(self, service):
        """Test validate_finca_data with hectareas less than 0.01."""
        data = {
            'nombre': 'Test Finca',
            'ubicacion': 'Test Location',
            'municipio': 'Test',
            'departamento': 'Test',
            'hectareas': Decimal('0.001')
        }
        result = service.validate_finca_data(data, is_create=True)
        assert result['valid'] is False
    
    def test_validate_finca_data_update_valid(self, service, valid_finca_data):
        """Test validate_finca_data for update with valid data."""
        result = service.validate_finca_data(valid_finca_data, is_create=False)
        assert result['valid'] is True
    
    def test_validate_finca_data_update_partial(self, service):
        """Test validate_finca_data for update with partial data."""
        data = {'nombre': 'Updated Finca'}
        result = service.validate_finca_data(data, is_create=False)
        assert result['valid'] is True
    
    def test_validate_finca_data_update_invalid_nombre(self, service):
        """Test validate_finca_data for update with invalid nombre."""
        data = {'nombre': 'A'}
        result = service.validate_finca_data(data, is_create=False)
        assert result['valid'] is False
    
    def test_validate_finca_data_update_invalid_hectareas(self, service):
        """Test validate_finca_data for update with invalid hectareas."""
        data = {'hectareas': Decimal('-10.5')}
        result = service.validate_finca_data(data, is_create=False)
        assert result['valid'] is False
    
    def test_validate_finca_data_with_exception(self, service):
        """Test validate_finca_data with exception."""
        with patch.object(service, 'validate_required_fields', side_effect=Exception("Error")):
            data = {'nombre': 'Test'}
            result = service.validate_finca_data(data, is_create=True)
            assert result['valid'] is False
            assert 'error' in result

