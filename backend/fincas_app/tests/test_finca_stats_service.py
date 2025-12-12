"""
Tests for FincaStatsService.
"""
import pytest
from unittest.mock import patch
from decimal import Decimal
from django.contrib.auth.models import User

from fincas_app.services.finca.finca_stats_service import FincaStatsService


@pytest.fixture
def service():
    """Create FincaStatsService instance."""
    return FincaStatsService()


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


class TestFincaStatsService:
    """Tests for FincaStatsService class."""
    
    def test_get_finca_statistics(self, service, user, finca):
        """Test get_finca_statistics method."""
        result = service.get_finca_statistics(user)
        assert result.success is True
        assert 'total_fincas' in result.data
        assert 'fincas_activas' in result.data
        assert 'fincas_inactivas' in result.data
        assert 'total_hectareas' in result.data
        assert 'total_area' in result.data
        assert 'promedio_hectareas' in result.data
        assert 'departamentos' in result.data
        assert 'municipios' in result.data
        assert 'recent_fincas' in result.data
        assert 'hectareas_distribution' in result.data
    
    def test_get_finca_statistics_admin(self, service, admin_user, finca):
        """Test get_finca_statistics for admin user."""
        result = service.get_finca_statistics(admin_user)
        assert result.success is True
        assert result.data['total_fincas'] >= 0
    
    def test_get_finca_statistics_with_departamento_filter(self, service, user, finca):
        """Test get_finca_statistics with departamento filter."""
        filters = {'departamento': 'Test Departamento'}
        result = service.get_finca_statistics(user, filters=filters)
        assert result.success is True
    
    def test_get_finca_statistics_with_activa_filter(self, service, user, finca):
        """Test get_finca_statistics with activa filter."""
        filters = {'activa': True}
        result = service.get_finca_statistics(user, filters=filters)
        assert result.success is True
    
    def test_get_finca_statistics_with_multiple_filters(self, service, user, finca):
        """Test get_finca_statistics with multiple filters."""
        filters = {
            'departamento': 'Test Departamento',
            'activa': True
        }
        result = service.get_finca_statistics(user, filters=filters)
        assert result.success is True
    
    def test_get_finca_statistics_no_fincas(self, service, user):
        """Test get_finca_statistics with no fincas."""
        result = service.get_finca_statistics(user)
        assert result.success is True
        assert result.data['total_fincas'] == 0
        assert result.data['total_hectareas'] == Decimal('0')
    
    def test_get_finca_statistics_hectareas_distribution(self, service, user, municipio):
        """Test get_finca_statistics hectareas distribution."""
        from fincas_app.models import Finca
        
        # Create fincas with different sizes
        Finca.objects.create(
            nombre='Small Finca',
            ubicacion='Test',
            municipio=municipio,
            hectareas=Decimal('3.0'),
            agricultor=user,
            activa=True
        )
        Finca.objects.create(
            nombre='Medium Finca',
            ubicacion='Test',
            municipio=municipio,
            hectareas=Decimal('10.0'),
            agricultor=user,
            activa=True
        )
        Finca.objects.create(
            nombre='Large Finca',
            ubicacion='Test',
            municipio=municipio,
            hectareas=Decimal('25.0'),
            agricultor=user,
            activa=True
        )
        
        result = service.get_finca_statistics(user)
        assert result.success is True
        assert 'small' in result.data['hectareas_distribution']
        assert 'medium' in result.data['hectareas_distribution']
        assert 'large' in result.data['hectareas_distribution']
    
    def test_get_finca_statistics_with_error(self, service, user):
        """Test get_finca_statistics with error."""
        with patch('fincas_app.models.Finca.objects.filter', side_effect=Exception("Error")):
            result = service.get_finca_statistics(user)
            assert result.success is False

