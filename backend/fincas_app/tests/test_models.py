"""
Tests for Fincas App Models.
"""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from fincas_app.models import Finca, Lote


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='farmer',
        email='farmer@example.com',
        password='testpass123'
    )


@pytest.fixture
def finca(user):
    """Create a test finca."""
    return Finca.objects.create(
        nombre='Test Finca',
        ubicacion='Vereda El Test',
        municipio='Medellín',
        departamento='Antioquia',
        hectareas=Decimal('10.5'),
        agricultor=user,
        activa=True
    )


@pytest.mark.django_db
class TestFinca:
    """Tests for Finca model."""

    def test_create_finca(self, user):
        """Test creating a finca."""
        finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Vereda El Test',
            municipio='Medellín',
            departamento='Antioquia',
            hectareas=Decimal('10.5'),
            agricultor=user
        )
        
        assert finca.nombre == 'Test Finca'
        assert finca.hectareas == Decimal('10.5')
        assert finca.agricultor == user

    def test_finca_str_representation(self, finca):
        """Test string representation."""
        assert 'Test Finca' in str(finca)
        assert 'Medellín' in str(finca)

    def test_propietario_alias(self, finca, user):
        """Test propietario alias for backward compatibility."""
        assert finca.propietario == user
        
        new_user = User.objects.create_user(
            username='newfarmer',
            email='new@example.com',
            password='pass123'
        )
        finca.propietario = new_user
        assert finca.agricultor == new_user

    def test_area_total_alias(self, finca):
        """Test area_total alias for backward compatibility."""
        assert finca.area_total == Decimal('10.5')
        
        finca.area_total = Decimal('15.0')
        assert finca.hectareas == Decimal('15.0')

    def test_total_lotes_property(self, finca):
        """Test total_lotes property."""
        assert finca.total_lotes == 0
        
        Lote.objects.create(
            finca=finca,
            identificador='L1',
            nombre='Lote 1',
            variedad='Criollo',
            area_hectareas=Decimal('5.0')
        )
        
        assert finca.total_lotes == 1

    def test_lotes_activos_property(self, finca):
        """Test lotes_activos property."""
        assert finca.lotes_activos == 0
        
        Lote.objects.create(
            finca=finca,
            identificador='L1',
            nombre='Lote 1',
            variedad='Criollo',
            area_hectareas=Decimal('5.0'),
            activo=True
        )
        Lote.objects.create(
            finca=finca,
            identificador='L2',
            nombre='Lote 2',
            variedad='Trinitario',
            area_hectareas=Decimal('3.0'),
            activo=False
        )
        
        assert finca.lotes_activos == 1

    def test_total_analisis_property(self, finca):
        """Test total_analisis property."""
        # Should return 0 if no analyses
        assert finca.total_analisis == 0

    def test_calidad_promedio_property(self, finca):
        """Test calidad_promedio property."""
        # Should return 0 if no analyses
        assert finca.calidad_promedio == 0.0

    def test_ubicacion_completa_property(self, finca):
        """Test ubicacion_completa property."""
        ubicacion = finca.ubicacion_completa
        
        assert 'Medellín' in ubicacion
        assert 'Antioquia' in ubicacion

    def test_finca_hectareas_constraint(self, user):
        """Test that hectareas must be positive."""
        with pytest.raises((ValidationError, Exception)):
            finca = Finca(
                nombre='Test',
                ubicacion='Test',
                municipio='Test',
                departamento='Test',
                hectareas=Decimal('-5.0'),
                agricultor=user
            )
            finca.full_clean()
            finca.save()


@pytest.mark.django_db
class TestLote:
    """Tests for Lote model."""

    def test_create_lote(self, finca):
        """Test creating a lote."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='L1',
            nombre='Lote 1',
            variedad='Criollo',
            area_hectareas=Decimal('5.0')
        )
        
        assert lote.identificador == 'L1'
        assert lote.variedad == 'Criollo'
        assert lote.area_hectareas == Decimal('5.0')
        assert lote.finca == finca

    def test_lote_str_representation(self, finca):
        """Test string representation."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='L1',
            nombre='Lote 1',
            variedad='Criollo',
            area_hectareas=Decimal('5.0')
        )
        
        assert 'L1' in str(lote) or 'Lote 1' in str(lote)

    def test_area_alias(self, finca):
        """Test area alias for backward compatibility."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='L1',
            nombre='Lote 1',
            variedad='Criollo',
            area_hectareas=Decimal('5.0')
        )
        
        assert lote.area == Decimal('5.0')
        assert lote.hectareas == Decimal('5.0')

    def test_lote_estado_choices(self, finca):
        """Test lote estado choices."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='L1',
            nombre='Lote 1',
            variedad='Criollo',
            area_hectareas=Decimal('5.0'),
            estado='activo'
        )
        
        assert lote.estado == 'activo'
        
        lote.estado = 'cosechado'
        lote.save()
        
        assert lote.estado == 'cosechado'

    def test_lote_area_cannot_exceed_finca(self, finca):
        """Test that lote area cannot exceed finca area."""
        # Finca has 10.5 ha
        with pytest.raises((ValidationError, Exception)):
            lote = Lote(
                finca=finca,
                identificador='L1',
                nombre='Lote 1',
                variedad='Criollo',
                area_hectareas=Decimal('15.0')  # Exceeds finca
            )
            lote.full_clean()
            lote.save()

