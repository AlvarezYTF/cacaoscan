"""
Unit tests for finca serializers (finca_serializers.py).
Tests all serializers: FincaSerializer, FincaListSerializer, FincaDetailSerializer,
FincaStatsSerializer, LoteSerializer, LoteListSerializer, LoteDetailSerializer, LoteStatsSerializer.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from fincas_app.models import Finca, Lote
from api.serializers.finca_serializers import (
    FincaSerializer,
    FincaListSerializer,
    FincaDetailSerializer,
    FincaStatsSerializer,
    LoteSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    LoteStatsSerializer
)
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME
)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD,
        first_name=TEST_USER_FIRST_NAME,
        last_name=TEST_USER_LAST_NAME
    )


@pytest.fixture
def test_finca(test_user):
    """Create a test finca."""
    return Finca.objects.create(
        nombre='Finca Test',
        ubicacion='Vereda Test',
        municipio='Test Municipio',
        departamento='Test Departamento',
        hectareas=Decimal('10.5'),
        agricultor=test_user,
        coordenadas_lat=Decimal('4.6097'),
        coordenadas_lng=Decimal('-74.0817')
    )


@pytest.fixture
def test_lote(test_finca):
    """Create a test lote."""
    return Lote.objects.create(
        finca=test_finca,
        identificador='LOTE-001',
        variedad='Criollo',
        fecha_plantacion=date(2020, 1, 1),
        area_hectareas=Decimal('2.5'),
        estado='activo',
        coordenadas_lat=Decimal('4.6097'),
        coordenadas_lng=Decimal('-74.0817')
    )


class TestFincaSerializer:
    """Tests for FincaSerializer."""
    
    def test_serialize_finca_success(self, test_finca, test_user):
        """Test successful finca serialization."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(test_finca, context={'request': request})
        data = serializer.data
        
        assert data['id'] == test_finca.id
        assert data['nombre'] == 'Finca Test'
        assert data['municipio'] == 'Test Municipio'
        assert data['departamento'] == 'Test Departamento'
        assert 'agricultor_name' in data
        assert 'agricultor_email' in data
        assert 'ubicacion_completa' in data
        assert 'estadisticas' in data
    
    def test_get_estadisticas_success(self, test_finca, test_user):
        """Test get_estadisticas method."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(test_finca, context={'request': request})
        stats = serializer.get_estadisticas(test_finca)
        
        assert 'total_lotes' in stats
        assert 'lotes_activos' in stats
        assert 'total_analisis' in stats
        assert 'calidad_promedio' in stats
        assert stats['hectareas'] == 10.5
    
    @patch('fincas_app.models.Finca.get_estadisticas')
    def test_get_estadisticas_error_handling(self, mock_get_stats, test_finca, test_user):
        """Test get_estadisticas error handling."""
        mock_get_stats.side_effect = Exception("Error")
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(test_finca, context={'request': request})
        stats = serializer.get_estadisticas(test_finca)
        
        assert stats['total_lotes'] == 0
        assert stats['lotes_activos'] == 0
        assert stats['total_analisis'] == 0
        assert stats['calidad_promedio'] == 0.0
    
    def test_validate_nombre_success(self, test_user):
        """Test successful nombre validation."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        value = serializer.validate_nombre('Valid Finca Name')
        assert value == 'Valid Finca Name'
    
    def test_validate_nombre_too_short(self, test_user):
        """Test validation error when nombre is too short."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_nombre('Ab')
    
    def test_validate_nombre_duplicate_creation(self, test_user, test_finca):
        """Test validation error when nombre is duplicate on creation."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_nombre('Finca Test')
    
    def test_validate_nombre_duplicate_update(self, test_user, test_finca):
        """Test validation error when nombre is duplicate on update."""
        request = Mock()
        request.user = test_user
        other_finca = Finca.objects.create(
            nombre='Other Finca',
            ubicacion='Other Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=Decimal('5.0'),
            agricultor=test_user
        )
        serializer = FincaSerializer(test_finca, context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_nombre('Other Finca')
    
    def test_validate_hectareas_positive(self, test_user):
        """Test successful hectareas validation."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        value = serializer.validate_hectareas(Decimal('10.5'))
        assert value == Decimal('10.5')
    
    def test_validate_hectareas_zero(self, test_user):
        """Test validation error when hectareas is zero."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_hectareas(Decimal('0'))
    
    def test_validate_hectareas_negative(self, test_user):
        """Test validation error when hectareas is negative."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_hectareas(Decimal('-1'))
    
    def test_validate_hectareas_too_high(self, test_user):
        """Test validation error when hectareas > 10000."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_hectareas(Decimal('10001'))
    
    def test_validate_coordenadas_lat_valid(self, test_user):
        """Test successful latitude validation."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        value = serializer.validate_coordenadas_lat(Decimal('4.6097'))
        assert value == Decimal('4.6097')
    
    def test_validate_coordenadas_lat_invalid(self, test_user):
        """Test validation error with invalid latitude."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_coordenadas_lat(Decimal('91'))
    
    def test_validate_coordenadas_lng_valid(self, test_user):
        """Test successful longitude validation."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        value = serializer.validate_coordenadas_lng(Decimal('-74.0817'))
        assert value == Decimal('-74.0817')
    
    def test_validate_coordenadas_lng_invalid(self, test_user):
        """Test validation error with invalid longitude."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        with pytest.raises(Exception):
            serializer.validate_coordenadas_lng(Decimal('181'))
    
    def test_validate_municipio_required(self, test_user):
        """Test validation error when municipio is missing."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        attrs = {'departamento': 'Test Departamento'}
        with pytest.raises(Exception):
            serializer.validate(attrs)
    
    def test_validate_departamento_required(self, test_user):
        """Test validation error when departamento is missing."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        attrs = {'municipio': 'Test Municipio'}
        with pytest.raises(Exception):
            serializer.validate(attrs)
    
    def test_validate_coordinates_pair(self, test_user):
        """Test validation error when only one coordinate is provided."""
        request = Mock()
        request.user = test_user
        serializer = FincaSerializer(context={'request': request})
        attrs = {
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'coordenadas_lat': Decimal('4.6097')
        }
        with pytest.raises(Exception):
            serializer.validate(attrs)


class TestFincaListSerializer:
    """Tests for FincaListSerializer."""
    
    def test_serialize_finca_list(self, test_finca):
        """Test serialization of finca list."""
        serializer = FincaListSerializer(test_finca)
        data = serializer.data
        
        assert data['id'] == test_finca.id
        assert data['nombre'] == 'Finca Test'
        assert 'ubicacion_completa' in data
        assert data['ubicacion_completa'] == 'Test Municipio, Test Departamento'
    
    def test_get_ubicacion_completa(self, test_finca):
        """Test get_ubicacion_completa method."""
        serializer = FincaListSerializer(test_finca)
        ubicacion = serializer.get_ubicacion_completa(test_finca)
        assert ubicacion == 'Test Municipio, Test Departamento'


class TestFincaDetailSerializer:
    """Tests for FincaDetailSerializer."""
    
    def test_serialize_finca_detail_with_lotes(self, test_finca, test_lote, test_user):
        """Test serialization of finca detail with lotes."""
        request = Mock()
        request.user = test_user
        serializer = FincaDetailSerializer(test_finca, context={'request': request})
        data = serializer.data
        
        assert 'lotes' in data
        assert len(data['lotes']) == 1
        assert data['lotes'][0]['id'] == test_lote.id
        assert data['lotes'][0]['identificador'] == 'LOTE-001'
    
    @patch('fincas_app.models.Lote')
    def test_get_lotes_error_handling(self, mock_lote, test_finca, test_user):
        """Test get_lotes error handling."""
        mock_lote.objects.filter.side_effect = Exception("Error")
        request = Mock()
        request.user = test_user
        serializer = FincaDetailSerializer(test_finca, context={'request': request})
        lotes = serializer.get_lotes(test_finca)
        assert lotes == []


class TestFincaStatsSerializer:
    """Tests for FincaStatsSerializer."""
    
    def test_serialize_finca_stats(self):
        """Test serialization of finca statistics."""
        data = {
            'total_fincas': 10,
            'fincas_activas': 8,
            'total_hectareas': Decimal('100.50'),
            'promedio_hectareas': Decimal('10.05'),
            'fincas_por_departamento': [{'departamento': 'Cundinamarca', 'count': 5}],
            'fincas_por_municipio': [{'municipio': 'Bogotá', 'count': 3}],
            'calidad_promedio_general': 85.5
        }
        serializer = FincaStatsSerializer(data=data)
        assert serializer.is_valid()


class TestLoteSerializer:
    """Tests for LoteSerializer."""
    
    def test_serialize_lote_success(self, test_lote):
        """Test successful lote serialization."""
        serializer = LoteSerializer(test_lote)
        data = serializer.data
        
        assert data['id'] == test_lote.id
        assert data['identificador'] == 'LOTE-001'
        assert data['variedad'] == 'Criollo'
        assert 'finca_nombre' in data
        assert 'ubicacion_completa' in data
        assert 'estadisticas' in data
        assert 'edad_meses' in data
    
    def test_validate_identificador_success(self, test_finca):
        """Test successful identificador validation."""
        serializer = LoteSerializer(context={'finca': test_finca})
        value = serializer.validate_identificador('LOTE-002')
        assert value == 'LOTE-002'
    
    def test_validate_identificador_too_short(self, test_finca):
        """Test validation error when identificador is too short."""
        serializer = LoteSerializer(context={'finca': test_finca})
        with pytest.raises(Exception):
            serializer.validate_identificador('A')
    
    def test_validate_identificador_duplicate(self, test_finca, test_lote):
        """Test validation error when identificador is duplicate."""
        serializer = LoteSerializer(context={'finca': test_finca})
        with pytest.raises(Exception):
            serializer.validate_identificador('LOTE-001')
    
    def test_validate_area_hectareas_positive(self, test_finca):
        """Test successful area validation."""
        serializer = LoteSerializer(context={'finca': test_finca})
        value = serializer.validate_area_hectareas(Decimal('2.5'))
        assert value == Decimal('2.5')
    
    def test_validate_area_hectareas_zero(self, test_finca):
        """Test validation error when area is zero."""
        serializer = LoteSerializer(context={'finca': test_finca})
        with pytest.raises(Exception):
            serializer.validate_area_hectareas(Decimal('0'))
    
    def test_validate_area_hectareas_too_high(self, test_finca):
        """Test validation error when area > 1000."""
        serializer = LoteSerializer(context={'finca': test_finca})
        with pytest.raises(Exception):
            serializer.validate_area_hectareas(Decimal('1001'))
    
    def test_validate_fecha_cosecha_valid(self, test_finca):
        """Test successful fecha_cosecha validation."""
        serializer = LoteSerializer(context={'finca': test_finca})
        serializer.initial_data = {'fecha_plantacion': date(2020, 1, 1)}
        value = serializer.validate_fecha_cosecha(date(2021, 1, 1))
        assert value == date(2021, 1, 1)
    
    def test_validate_fecha_cosecha_before_plantacion(self, test_finca):
        """Test validation error when fecha_cosecha is before fecha_plantacion."""
        serializer = LoteSerializer(context={'finca': test_finca})
        serializer.initial_data = {'fecha_plantacion': date(2021, 1, 1)}
        with pytest.raises(Exception):
            serializer.validate_fecha_cosecha(date(2020, 1, 1))
    
    def test_validate_variedad_required(self, test_finca):
        """Test validation error when variedad is missing."""
        serializer = LoteSerializer(context={'finca': test_finca})
        attrs = {}
        with pytest.raises(Exception):
            serializer.validate(attrs)


class TestLoteListSerializer:
    """Tests for LoteListSerializer."""
    
    def test_serialize_lote_list(self, test_lote):
        """Test serialization of lote list."""
        serializer = LoteListSerializer(test_lote)
        data = serializer.data
        
        assert data['id'] == test_lote.id
        assert data['identificador'] == 'LOTE-001'
        assert 'finca_nombre' in data
        assert 'agricultor_nombre' in data
        assert 'ubicacion_completa' in data


class TestLoteDetailSerializer:
    """Tests for LoteDetailSerializer."""
    
    @patch('api.serializers.finca_serializers.CacaoImageSerializer')
    def test_get_cacao_images(self, mock_serializer, test_lote):
        """Test get_cacao_images method."""
        mock_serializer.return_value.data = [{'id': 1, 'image': 'test.jpg'}]
        serializer = LoteDetailSerializer(test_lote)
        images = serializer.get_cacao_images(test_lote)
        # Should return serialized images or empty list
        assert isinstance(images, list)


class TestLoteStatsSerializer:
    """Tests for LoteStatsSerializer."""
    
    def test_serialize_lote_stats(self):
        """Test serialization of lote statistics."""
        data = {
            'total_lotes': 20,
            'lotes_activos': 15,
            'lotes_por_estado': {'activo': 15, 'inactivo': 5},
            'total_area_hectareas': Decimal('50.0'),
            'promedio_area_hectareas': Decimal('2.5'),
            'variedades_mas_comunes': [{'variedad': 'Criollo', 'count': 10}],
            'calidad_promedio_general': 80.5
        }
        serializer = LoteStatsSerializer(data=data)
        assert serializer.is_valid()

