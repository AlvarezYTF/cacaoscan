"""
Tests for Catalogos Serializers.
"""
import pytest

from catalogos.serializers import (
    ParametroSerializer,
    ParametroDetalleSerializer,
    TemaSerializer,
    TemaConParametrosSerializer,
    ParametroCreateSerializer,
    MunicipioSerializer,
    MunicipioDetalleSerializer,
    DepartamentoSerializer,
    DepartamentoConMunicipiosSerializer,
    MunicipioCreateSerializer
)
from catalogos.models import Tema, Parametro, Departamento, Municipio


@pytest.fixture
def tema():
    """Create a test tema."""
    return Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )


@pytest.fixture
def parametro(tema):
    """Create a test parametro."""
    return Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía'
    )


@pytest.fixture
def departamento():
    """Create a test departamento."""
    return Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )


@pytest.fixture
def municipio(departamento):
    """Create a test municipio."""
    return Municipio.objects.create(
        departamento=departamento,
        codigo='001',
        nombre='Medellín'
    )


@pytest.mark.django_db
class TestParametroSerializer:
    """Tests for ParametroSerializer."""

    def test_serialize_parametro(self, parametro):
        """Test serializing parametro."""
        serializer = ParametroSerializer(parametro)
        data = serializer.data
        
        assert data['id'] == parametro.id
        assert data['codigo'] == parametro.codigo
        assert data['nombre'] == parametro.nombre

    def test_create_parametro(self, tema):
        """Test creating parametro."""
        data = {
            'tema': tema.id,
            'codigo': 'CE',
            'nombre': 'Cédula de Extranjería',
            'activo': True
        }
        serializer = ParametroSerializer(data=data)
        assert serializer.is_valid()
        
        parametro = serializer.save()
        assert parametro.tema == tema
        assert parametro.codigo == 'CE'


@pytest.mark.django_db
class TestParametroDetalleSerializer:
    """Tests for ParametroDetalleSerializer."""

    def test_serialize_parametro_detalle(self, parametro):
        """Test serializing parametro with tema details."""
        serializer = ParametroDetalleSerializer(parametro)
        data = serializer.data
        
        assert data['id'] == parametro.id
        assert 'tema_nombre' in data
        assert 'tema_codigo' in data
        assert data['tema_nombre'] == parametro.tema.nombre


@pytest.mark.django_db
class TestTemaSerializer:
    """Tests for TemaSerializer."""

    def test_serialize_tema(self, tema):
        """Test serializing tema."""
        serializer = TemaSerializer(tema)
        data = serializer.data
        
        assert data['id'] == tema.id
        assert data['codigo'] == tema.codigo
        assert 'parametros_count' in data

    def test_create_tema(self):
        """Test creating tema."""
        data = {
            'codigo': 'SEXO',
            'nombre': 'Sexo',
            'activo': True
        }
        serializer = TemaSerializer(data=data)
        assert serializer.is_valid()
        
        tema = serializer.save()
        assert tema.codigo == 'SEXO'


@pytest.mark.django_db
class TestTemaConParametrosSerializer:
    """Tests for TemaConParametrosSerializer."""

    def test_serialize_tema_con_parametros(self, tema, parametro):
        """Test serializing tema with parametros."""
        serializer = TemaConParametrosSerializer(tema)
        data = serializer.data
        
        assert data['id'] == tema.id
        assert 'parametros' in data
        assert len(data['parametros']) >= 1
        assert 'parametros_activos' in data


@pytest.mark.django_db
class TestParametroCreateSerializer:
    """Tests for ParametroCreateSerializer."""

    def test_create_parametro_unique_code(self, tema):
        """Test creating parametro with unique code."""
        data = {
            'tema': tema.id,
            'codigo': 'CC',
            'nombre': 'Cédula de Ciudadanía'
        }
        serializer = ParametroCreateSerializer(data=data)
        assert serializer.is_valid()
        
        parametro = serializer.save()
        assert parametro.codigo == 'CC'

    def test_create_parametro_duplicate_code(self, tema, parametro):
        """Test creating parametro with duplicate code fails."""
        data = {
            'tema': tema.id,
            'codigo': 'CC',  # Duplicate
            'nombre': 'Another CC'
        }
        serializer = ParametroCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'codigo' in serializer.errors


@pytest.mark.django_db
class TestMunicipioSerializer:
    """Tests for MunicipioSerializer."""

    def test_serialize_municipio(self, municipio):
        """Test serializing municipio."""
        serializer = MunicipioSerializer(municipio)
        data = serializer.data
        
        assert data['id'] == municipio.id
        assert data['codigo'] == municipio.codigo
        assert data['nombre'] == municipio.nombre


@pytest.mark.django_db
class TestMunicipioDetalleSerializer:
    """Tests for MunicipioDetalleSerializer."""

    def test_serialize_municipio_detalle(self, municipio):
        """Test serializing municipio with departamento details."""
        serializer = MunicipioDetalleSerializer(municipio)
        data = serializer.data
        
        assert data['id'] == municipio.id
        assert 'departamento_nombre' in data
        assert 'departamento_codigo' in data
        assert data['departamento_nombre'] == municipio.departamento.nombre


@pytest.mark.django_db
class TestDepartamentoSerializer:
    """Tests for DepartamentoSerializer."""

    def test_serialize_departamento(self, departamento):
        """Test serializing departamento."""
        serializer = DepartamentoSerializer(departamento)
        data = serializer.data
        
        assert data['id'] == departamento.id
        assert data['codigo'] == departamento.codigo
        assert 'municipios_count' in data


@pytest.mark.django_db
class TestDepartamentoConMunicipiosSerializer:
    """Tests for DepartamentoConMunicipiosSerializer."""

    def test_serialize_departamento_con_municipios(self, departamento, municipio):
        """Test serializing departamento with municipios."""
        serializer = DepartamentoConMunicipiosSerializer(departamento)
        data = serializer.data
        
        assert data['id'] == departamento.id
        assert 'municipios' in data
        assert len(data['municipios']) >= 1


@pytest.mark.django_db
class TestMunicipioCreateSerializer:
    """Tests for MunicipioCreateSerializer."""

    def test_create_municipio_unique_code(self, departamento):
        """Test creating municipio with unique code."""
        data = {
            'departamento': departamento.id,
            'codigo': '002',
            'nombre': 'Bello'
        }
        serializer = MunicipioCreateSerializer(data=data)
        assert serializer.is_valid()
        
        municipio = serializer.save()
        assert municipio.codigo == '002'

    def test_create_municipio_duplicate_code(self, departamento, municipio):
        """Test creating municipio with duplicate code fails."""
        data = {
            'departamento': departamento.id,
            'codigo': '001',  # Duplicate
            'nombre': 'Another City'
        }
        serializer = MunicipioCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'codigo' in serializer.errors

