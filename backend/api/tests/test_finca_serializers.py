"""
Tests for finca serializers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
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


@pytest.mark.django_db
class TestFincaSerializer:
    """Tests for FincaSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create test user."""
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
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio=municipio,
            hectareas=10.5,
            agricultor=user,
            coordenadas_lat=4.5,
            coordenadas_lng=-73.5
        )
    
    def test_serialize_finca(self, finca):
        """Test serializing a finca."""
        serializer = FincaSerializer(finca)
        data = serializer.data
        
        assert data['id'] == finca.id
        assert data['nombre'] == 'Test Finca'
        assert data['hectareas'] == '10.50'
        assert 'area_total' in data
        assert 'propietario' in data
        assert 'agricultor_name' in data
        assert 'agricultor_email' in data
        assert 'ubicacion_completa' in data
        assert 'estadisticas' in data
    
    def test_get_estadisticas_success(self, finca):
        """Test get_estadisticas method with success."""
        with patch.object(finca, 'get_estadisticas', return_value={
            'total_lotes': 5,
            'lotes_activos': 3,
            'total_analisis': 10,
            'calidad_promedio': 8.5
        }):
            serializer = FincaSerializer(finca)
            stats = serializer.get_estadisticas(finca)
            assert stats['total_lotes'] == 5
    
    def test_get_estadisticas_exception(self, finca):
        """Test get_estadisticas method with exception."""
        with patch.object(finca, 'get_estadisticas', side_effect=Exception("Error")):
            serializer = FincaSerializer(finca)
            stats = serializer.get_estadisticas(finca)
            assert stats['total_lotes'] == 0
            assert stats['calidad_promedio'] == 0.0
    
    def test_validate_nombre_too_short(self, user):
        """Test validate_nombre with too short name."""
        request = Mock()
        request.user = user
        serializer = FincaSerializer(context={'request': request})
        
        with pytest.raises(ValidationError):
            serializer.validate_nombre('AB')
    
    def test_validate_nombre_duplicate_on_create(self, user, municipio):
        """Test validate_nombre with duplicate name on create."""
        from fincas_app.models import Finca
        Finca.objects.create(
            nombre='Existing Finca',
            municipio=municipio,
            hectareas=10,
            agricultor=user
        )
        
        request = Mock()
        request.user = user
        serializer = FincaSerializer(context={'request': request})
        
        with pytest.raises(ValidationError):
            serializer.validate_nombre('Existing Finca')
    
    def test_validate_nombre_duplicate_on_update(self, user, finca, municipio):
        """Test validate_nombre with duplicate name on update."""
        from fincas_app.models import Finca
        Finca.objects.create(
            nombre='Other Finca',
            municipio=municipio,
            hectareas=10,
            agricultor=user
        )
        
        request = Mock()
        request.user = user
        serializer = FincaSerializer(instance=finca, context={'request': request})
        
        with pytest.raises(ValidationError):
            serializer.validate_nombre('Other Finca')
    
    def test_validate_nombre_success(self, user):
        """Test validate_nombre with valid name."""
        request = Mock()
        request.user = user
        serializer = FincaSerializer(context={'request': request})
        
        result = serializer.validate_nombre('  Valid Finca Name  ')
        assert result == 'Valid Finca Name'
    
    def test_validate_hectareas_none(self):
        """Test validate_hectareas with None."""
        serializer = FincaSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_hectareas(None)
    
    def test_validate_hectareas_negative(self):
        """Test validate_hectareas with negative value."""
        serializer = FincaSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_hectareas(-10)
    
    def test_validate_hectareas_too_large(self):
        """Test validate_hectareas with too large value."""
        serializer = FincaSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_hectareas(10001)
    
    def test_validate_hectareas_valid(self):
        """Test validate_hectareas with valid value."""
        serializer = FincaSerializer()
        
        result = serializer.validate_hectareas(100.5)
        assert result == 100.5
    
    def test_validate_coordenadas_lat(self):
        """Test validate_coordenadas_lat."""
        serializer = FincaSerializer()
        
        with patch('core.utils.validate_latitude', return_value=4.5):
            result = serializer.validate_coordenadas_lat(4.5)
            assert result == 4.5
    
    def test_validate_coordenadas_lng(self):
        """Test validate_coordenadas_lng."""
        serializer = FincaSerializer()
        
        with patch('core.utils.validate_longitude', return_value=-73.5):
            result = serializer.validate_coordenadas_lng(-73.5)
            assert result == -73.5
    
    def test_validate_required_fields_partial_update(self):
        """Test _validate_required_fields in partial mode."""
        serializer = FincaSerializer()
        errors = {}
        
        serializer._validate_required_fields({'municipio': ''}, errors, is_partial=True)
        assert 'municipio' in errors
    
    def test_validate_required_fields_full_update(self):
        """Test _validate_required_fields in full mode."""
        serializer = FincaSerializer()
        errors = {}
        
        serializer._validate_required_fields({'municipio': ''}, errors, is_partial=False)
        assert 'municipio' in errors
    
    def test_handle_coordinate_validation_error_with_lat_lng(self):
        """Test _handle_coordinate_validation_error with lat/lng in error."""
        serializer = FincaSerializer()
        errors = {}
        
        exception = Exception("Error in coordenadas_lat")
        serializer._handle_coordinate_validation_error(exception, errors)
        assert 'non_field_errors' in errors
    
    def test_handle_coordinate_validation_error_generic(self):
        """Test _handle_coordinate_validation_error with generic error."""
        serializer = FincaSerializer()
        errors = {}
        
        exception = Exception("Generic validation error")
        serializer._handle_coordinate_validation_error(exception, errors)
        assert 'coordenadas_lat' in errors
        assert 'coordenadas_lng' in errors
        assert 'non_field_errors' in errors
    
    def test_validate_with_coordinate_error(self, user):
        """Test validate method with coordinate validation error."""
        request = Mock()
        request.user = user
        serializer = FincaSerializer(context={'request': request})
        
        attrs = {
            'municipio': 'Test',
            'departamento': 'Test',
            'coordenadas_lat': 4.5,
            'coordenadas_lng': -73.5
        }
        
        with patch('core.utils.validate_coordinates', side_effect=Exception("Coordinate error")):
            with pytest.raises(ValidationError):
                serializer.validate(attrs)
    
    def test_validate_with_required_fields_error(self, user):
        """Test validate method with required fields error."""
        request = Mock()
        request.user = user
        serializer = FincaSerializer(context={'request': request})
        
        attrs = {
            'municipio': '',
            'departamento': 'Test'
        }
        
        with patch('core.utils.validate_coordinates'):
            with pytest.raises(ValidationError):
                serializer.validate(attrs)
    
    def test_validate_success(self, user):
        """Test validate method with valid data."""
        request = Mock()
        request.user = user
        serializer = FincaSerializer(context={'request': request})
        
        attrs = {
            'municipio': 'Test',
            'departamento': 'Test',
            'coordenadas_lat': 4.5,
            'coordenadas_lng': -73.5
        }
        
        with patch('core.utils.validate_coordinates'):
            result = serializer.validate(attrs)
            assert result == attrs


@pytest.mark.django_db
class TestFincaListSerializer:
    """Tests for FincaListSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create test user."""
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
            nombre='Test Finca',
            municipio=municipio,
            hectareas=10.5,
            agricultor=user
        )
    
    def test_serialize_finca_list(self, finca):
        """Test serializing a finca for list."""
        serializer = FincaListSerializer(finca)
        data = serializer.data
        
        assert data['id'] == finca.id
        assert data['nombre'] == 'Test Finca'
        assert 'ubicacion_completa' in data
    
    def test_get_ubicacion_completa(self, finca):
        """Test get_ubicacion_completa method."""
        serializer = FincaListSerializer()
        result = serializer.get_ubicacion_completa(finca)
        assert "Test Municipio" in result
        assert "Test Departamento" in result


@pytest.mark.django_db
class TestFincaDetailSerializer:
    """Tests for FincaDetailSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create test user."""
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
            nombre='Test Finca',
            municipio=municipio,
            hectareas=10.5,
            agricultor=user
        )
    
    def test_serialize_finca_detail(self, finca):
        """Test serializing a finca detail."""
        serializer = FincaDetailSerializer(finca)
        data = serializer.data
        
        assert 'lotes' in data
    
    def test_get_lotes_success(self, finca, user):
        """Test get_lotes method with success."""
        from fincas_app.models import Lote
        from datetime import date
        lote = Lote.objects.create(
            finca=finca,
            identificador='L001',
            variedad='Criollo',
            area_hectareas=1.0,
            fecha_plantacion=date.today()
        )
        
        serializer = FincaDetailSerializer()
        lotes = serializer.get_lotes(finca)
        
        assert len(lotes) == 1
        assert lotes[0]['id'] == lote.id
        assert lotes[0]['identificador'] == 'L001'
    
    def test_get_lotes_exception(self, finca):
        """Test get_lotes method with exception."""
        serializer = FincaDetailSerializer()
        
        with patch('fincas_app.models.Lote', side_effect=Exception("Error")):
            lotes = serializer.get_lotes(finca)
            assert lotes == []


@pytest.mark.django_db
class TestFincaStatsSerializer:
    """Tests for FincaStatsSerializer."""
    
    def test_serialize_finca_stats(self):
        """Test serializing finca stats."""
        data = {
            'total_fincas': 10,
            'fincas_activas': 8,
            'total_hectareas': 100.5,
            'promedio_hectareas': 10.05,
            'fincas_por_departamento': [],
            'fincas_por_municipio': [],
            'calidad_promedio_general': 8.5
        }
        
        serializer = FincaStatsSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestLoteSerializer:
    """Tests for LoteSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create test user."""
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
            nombre='Test Finca',
            municipio=municipio,
            hectareas=10.5,
            agricultor=user
        )
    
    @pytest.fixture
    def lote(self, finca):
        """Create test lote."""
        from fincas_app.models import Lote
        from datetime import date
        return Lote.objects.create(
            finca=finca,
            identificador='L001',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 1),
            area_hectareas=1.0
        )
    
    def test_serialize_lote(self, lote):
        """Test serializing a lote."""
        serializer = LoteSerializer(lote)
        data = serializer.data
        
        assert data['id'] == lote.id
        assert data['identificador'] == 'L001'
        assert 'finca_nombre' in data
        assert 'finca_ubicacion' in data
        assert 'agricultor_nombre' in data
        assert 'ubicacion_completa' in data
        assert 'estadisticas' in data
        assert 'edad_meses' in data
        # Check that average_confidence is not accessed incorrectly
        # The serializer should handle this field properly
    
    def test_get_estadisticas(self, lote):
        """Test get_estadisticas method."""
        with patch.object(lote, 'get_estadisticas', return_value={'total_analisis': 5}):
            serializer = LoteSerializer(lote)
            stats = serializer.get_estadisticas(lote)
            assert stats['total_analisis'] == 5
    
    def test_validate_identificador_too_short(self, finca):
        """Test validate_identificador with too short identifier."""
        serializer = LoteSerializer(context={'finca': finca})
        
        with pytest.raises(ValidationError):
            serializer.validate_identificador('A')
    
    def test_validate_identificador_duplicate_on_create(self, finca):
        """Test validate_identificador with duplicate on create."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            identificador='L001',
            variedad='Criollo',
            area_hectareas=1.0,
            fecha_plantacion=date.today()
        )
        
        serializer = LoteSerializer(context={'finca': finca})
        
        with pytest.raises(ValidationError):
            serializer.validate_identificador('L001')
    
    def test_validate_identificador_duplicate_on_update(self, finca, lote):
        """Test validate_identificador with duplicate on update."""
        from fincas_app.models import Lote
        from datetime import date
        Lote.objects.create(
            finca=finca,
            identificador='L002',
            variedad='Criollo',
            area_hectareas=1.0,
            fecha_plantacion=date.today()
        )
        
        serializer = LoteSerializer(instance=lote, context={'finca': finca})
        
        with pytest.raises(ValidationError):
            serializer.validate_identificador('L002')
    
    def test_validate_area_hectareas_none(self):
        """Test validate_area_hectareas with None."""
        serializer = LoteSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_area_hectareas(None)
    
    def test_validate_area_hectareas_negative(self):
        """Test validate_area_hectareas with negative value."""
        serializer = LoteSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_area_hectareas(-10)
    
    def test_validate_area_hectareas_too_large(self):
        """Test validate_area_hectareas with too large value."""
        serializer = LoteSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_area_hectareas(1001)
    
    def test_validate_area_none(self):
        """Test validate_area with None."""
        serializer = LoteSerializer()
        
        result = serializer.validate_area(None)
        assert result is None
    
    def test_validate_area_negative(self):
        """Test validate_area with negative value."""
        serializer = LoteSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_area(-10)
    
    def test_validate_area_too_large(self):
        """Test validate_area with too large value."""
        serializer = LoteSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_area(1001)
    
    def test_parse_fecha_plantacion_string(self):
        """Test _parse_fecha_plantacion with string."""
        serializer = LoteSerializer()
        
        result = serializer._parse_fecha_plantacion('2020-01-01')
        assert result.year == 2020
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_fecha_plantacion_isoformat(self):
        """Test _parse_fecha_plantacion with isoformat."""
        serializer = LoteSerializer()
        
        result = serializer._parse_fecha_plantacion('2020-01-01T00:00:00')
        assert result.year == 2020
    
    def test_parse_fecha_plantacion_invalid(self):
        """Test _parse_fecha_plantacion with invalid format."""
        serializer = LoteSerializer()
        
        result = serializer._parse_fecha_plantacion('invalid')
        assert result is None
    
    def test_parse_fecha_plantacion_none(self):
        """Test _parse_fecha_plantacion with None."""
        serializer = LoteSerializer()
        
        result = serializer._parse_fecha_plantacion(None)
        assert result is None
    
    def test_parse_fecha_plantacion_date(self):
        """Test _parse_fecha_plantacion with date object."""
        from datetime import date
        serializer = LoteSerializer()
        
        fecha = date(2020, 1, 1)
        result = serializer._parse_fecha_plantacion(fecha)
        assert result == fecha
    
    def test_validate_fecha_cosecha_basic_year_too_old(self):
        """Test _validate_fecha_cosecha_basic with year too old."""
        from datetime import date
        serializer = LoteSerializer()
        
        with pytest.raises(ValidationError):
            serializer._validate_fecha_cosecha_basic(date(1899, 1, 1))
    
    def test_validate_fecha_cosecha_basic_future(self):
        """Test _validate_fecha_cosecha_basic with future date."""
        from datetime import date, timedelta
        from django.utils import timezone
        serializer = LoteSerializer()
        
        future_date = timezone.now().date() + timedelta(days=1)
        with pytest.raises(ValidationError):
            serializer._validate_fecha_cosecha_basic(future_date)
    
    def test_validate_fecha_cosecha_none(self):
        """Test validate_fecha_cosecha with None."""
        serializer = LoteSerializer()
        
        result = serializer.validate_fecha_cosecha(None)
        assert result is None
    
    def test_validate_fecha_cosecha_before_plantacion(self):
        """Test validate_fecha_cosecha before fecha_plantacion."""
        from datetime import date
        serializer = LoteSerializer()
        serializer.initial_data = {'fecha_plantacion': '2020-01-01'}
        
        with pytest.raises(ValidationError):
            serializer.validate_fecha_cosecha(date(2019, 12, 31))
    
    def test_validate_fecha_cosecha_valid(self):
        """Test validate_fecha_cosecha with valid date."""
        from datetime import date
        serializer = LoteSerializer()
        serializer.initial_data = {'fecha_plantacion': '2020-01-01'}
        
        result = serializer.validate_fecha_cosecha(date(2020, 6, 1))
        assert result == date(2020, 6, 1)
    
    def test_validate_coordenadas_lat(self):
        """Test validate_coordenadas_lat."""
        serializer = LoteSerializer()
        
        with patch('core.utils.validate_latitude', return_value=4.5):
            result = serializer.validate_coordenadas_lat(4.5)
            assert result == 4.5
    
    def test_validate_coordenadas_lng(self):
        """Test validate_coordenadas_lng."""
        serializer = LoteSerializer()
        
        with patch('core.utils.validate_longitude', return_value=-73.5):
            result = serializer.validate_coordenadas_lng(-73.5)
            assert result == -73.5
    
    def test_handle_area_alias_only_area(self):
        """Test _handle_area_alias with only area."""
        serializer = LoteSerializer()
        attrs = {'area': 10.5}
        
        serializer._handle_area_alias(attrs)
        assert 'area_hectareas' in attrs
        assert attrs['area_hectareas'] == 10.5
        assert 'area' not in attrs
    
    def test_handle_area_alias_both(self):
        """Test _handle_area_alias with both area and area_hectareas."""
        serializer = LoteSerializer()
        attrs = {'area': 10.5, 'area_hectareas': 11.0}
        
        serializer._handle_area_alias(attrs)
        assert 'area_hectareas' in attrs
        assert 'area' not in attrs
    
    def test_validate_with_variedad_error(self, finca):
        """Test validate method with variedad error."""
        serializer = LoteSerializer(context={'finca': finca})
        
        attrs = {
            'variedad': '',
            'coordenadas_lat': 4.5,
            'coordenadas_lng': -73.5
        }
        
        with patch('core.utils.validate_coordinates'):
            with pytest.raises(ValidationError):
                serializer.validate(attrs)
    
    def test_validate_with_coordinate_error(self, finca):
        """Test validate method with coordinate error."""
        serializer = LoteSerializer(context={'finca': finca})
        
        attrs = {
            'variedad': 'Criollo',
            'coordenadas_lat': 4.5,
            'coordenadas_lng': -73.5
        }
        
        with patch('core.utils.validate_coordinates', side_effect=Exception("Coordinate error")):
            with pytest.raises(ValidationError) as exc_info:
                serializer.validate(attrs)
            # Check that the error is properly handled
            assert exc_info.value is not None
    
    def test_validate_success(self, finca):
        """Test validate method with valid data."""
        serializer = LoteSerializer(context={'finca': finca})
        
        attrs = {
            'variedad': 'Criollo',
            'coordenadas_lat': 4.5,
            'coordenadas_lng': -73.5,
            'area': 10.5
        }
        
        with patch('core.utils.validate_coordinates'):
            result = serializer.validate(attrs)
            assert 'area_hectareas' in result


@pytest.mark.django_db
class TestLoteListSerializer:
    """Tests for LoteListSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create test user."""
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
            nombre='Test Finca',
            municipio=municipio,
            hectareas=10.5,
            agricultor=user
        )
    
    @pytest.fixture
    def lote(self, finca):
        """Create test lote."""
        from fincas_app.models import Lote
        from datetime import date
        return Lote.objects.create(
            finca=finca,
            identificador='L001',
            variedad='Criollo',
            area_hectareas=1.0,
            fecha_plantacion=date.today()
        )
    
    def test_serialize_lote_list(self, lote):
        """Test serializing a lote for list."""
        serializer = LoteListSerializer(lote)
        data = serializer.data
        
        assert data['id'] == lote.id
        assert data['identificador'] == 'L001'
        assert 'finca_nombre' in data
        assert 'agricultor_nombre' in data


@pytest.mark.django_db
class TestLoteDetailSerializer:
    """Tests for LoteDetailSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create test user."""
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
            nombre='Test Finca',
            municipio=municipio,
            hectareas=10.5,
            agricultor=user
        )
    
    @pytest.fixture
    def lote(self, finca):
        """Create test lote."""
        from fincas_app.models import Lote
        from datetime import date
        return Lote.objects.create(
            finca=finca,
            identificador='L001',
            variedad='Criollo',
            area_hectareas=1.0,
            fecha_plantacion=date.today()
        )
    
    def test_serialize_lote_detail(self, lote):
        """Test serializing a lote detail."""
        serializer = LoteDetailSerializer(lote)
        data = serializer.data
        
        assert 'cacao_images' in data
    
    def test_get_cacao_images(self, lote):
        """Test get_cacao_images method."""
        from api.serializers.finca_serializers import LoteDetailSerializer
        
        # Mock CacaoImageSerializer at the point where it's imported (image_serializers module)
        with patch('api.serializers.image_serializers.CacaoImageSerializer') as mock_serializer_class:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = []
            mock_serializer_class.return_value = mock_serializer_instance
            
            serializer = LoteDetailSerializer()
            images = serializer.get_cacao_images(lote)
            
            # Should return empty list if no images
            assert isinstance(images, list)
            mock_serializer_class.assert_called_once()


@pytest.mark.django_db
class TestLoteStatsSerializer:
    """Tests for LoteStatsSerializer."""
    
    def test_serialize_lote_stats(self):
        """Test serializing lote stats."""
        data = {
            'total_lotes': 10,
            'lotes_activos': 8,
            'lotes_por_estado': {},
            'total_area_hectareas': 100.5,
            'promedio_area_hectareas': 10.05,
            'variedades_mas_comunes': [],
            'calidad_promedio_general': 8.5
        }
        
        serializer = LoteStatsSerializer(data=data)
        assert serializer.is_valid()

