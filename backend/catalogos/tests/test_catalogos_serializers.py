"""
Tests for catalogos serializers.
"""
import pytest
from rest_framework.exceptions import ValidationError
from catalogos.models import Tema, Parametro, Departamento, Municipio
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


@pytest.mark.django_db
class TestParametroSerializer:
    """Tests for ParametroSerializer."""
    
    def test_serialize_parametro(self):
        """Test serializing a parametro."""
        tema = Tema.objects.create(codigo='TEST', nombre='Test Tema')
        parametro = Parametro.objects.create(
            tema=tema,
            codigo='TEST_PARAM',
            nombre='Test Parametro',
            descripcion='Test Description',
            activo=True
        )
        
        serializer = ParametroSerializer(parametro)
        data = serializer.data
        
        assert data['id'] == parametro.id
        assert data['codigo'] == 'TEST_PARAM'
        assert data['nombre'] == 'Test Parametro'
        assert data['activo'] is True
    
    def test_serialize_parametro_detalle(self):
        """Test serializing parametro with tema info."""
        tema = Tema.objects.create(codigo='TEST', nombre='Test Tema')
        parametro = Parametro.objects.create(
            tema=tema,
            codigo='TEST_PARAM',
            nombre='Test Parametro',
            activo=True
        )
        
        serializer = ParametroDetalleSerializer(parametro)
        data = serializer.data
        
        assert data['tema_nombre'] == 'Test Tema'
        assert data['tema_codigo'] == 'TEST'


@pytest.mark.django_db
class TestTemaSerializer:
    """Tests for TemaSerializer."""
    
    def test_serialize_tema(self):
        """Test serializing a tema."""
        tema = Tema.objects.create(
            codigo='TEST',
            nombre='Test Tema',
            descripcion='Test Description',
            activo=True
        )
        
        serializer = TemaSerializer(tema)
        data = serializer.data
        
        assert data['codigo'] == 'TEST'
        assert data['nombre'] == 'Test Tema'
        assert 'parametros_count' in data
    
    def test_serialize_tema_con_parametros(self):
        """Test serializing tema with parametros."""
        tema = Tema.objects.create(codigo='TEST', nombre='Test Tema')
        Parametro.objects.create(
            tema=tema,
            codigo='PARAM1',
            nombre='Param 1',
            activo=True
        )
        Parametro.objects.create(
            tema=tema,
            codigo='PARAM2',
            nombre='Param 2',
            activo=False
        )
        
        serializer = TemaConParametrosSerializer(tema)
        data = serializer.data
        
        assert len(data['parametros']) == 2
        assert len(data['parametros_activos']) == 1


@pytest.mark.django_db
class TestParametroCreateSerializer:
    """Tests for ParametroCreateSerializer."""
    
    def test_create_parametro(self):
        """Test creating a parametro."""
        tema = Tema.objects.create(codigo='TEST', nombre='Test Tema')
        
        serializer = ParametroCreateSerializer(data={
            'tema': tema.id,
            'codigo': 'NEW_PARAM',
            'nombre': 'New Parametro',
            'activo': True
        })
        
        assert serializer.is_valid()
        parametro = serializer.save()
        
        assert parametro.codigo == 'NEW_PARAM'
        assert parametro.tema == tema
    
    def test_create_duplicate_codigo_same_tema(self):
        """Test creating parametro with duplicate codigo in same tema."""
        tema = Tema.objects.create(codigo='TEST', nombre='Test Tema')
        Parametro.objects.create(
            tema=tema,
            codigo='EXISTING',
            nombre='Existing'
        )
        
        serializer = ParametroCreateSerializer(data={
            'tema': tema.id,
            'codigo': 'EXISTING',
            'nombre': 'New Parametro'
        })
        
        assert not serializer.is_valid()
        # The error is in non_field_errors for unique constraint (tema, codigo)
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
class TestMunicipioSerializer:
    """Tests for MunicipioSerializer."""
    
    def test_serialize_municipio(self):
        """Test serializing a municipio."""
        dept = Departamento.objects.create(codigo='TEST', nombre='Test Dept')
        municipio = Municipio.objects.create(
            departamento=dept,
            codigo='MUN1',
            nombre='Test Municipio'
        )
        
        serializer = MunicipioSerializer(municipio)
        data = serializer.data
        
        assert data['codigo'] == 'MUN1'
        assert data['nombre'] == 'Test Municipio'
    
    def test_serialize_municipio_detalle(self):
        """Test serializing municipio with departamento info."""
        dept = Departamento.objects.create(codigo='TEST', nombre='Test Dept')
        municipio = Municipio.objects.create(
            departamento=dept,
            codigo='MUN1',
            nombre='Test Municipio'
        )
        
        serializer = MunicipioDetalleSerializer(municipio)
        data = serializer.data
        
        assert data['departamento_nombre'] == 'Test Dept'
        assert data['departamento_codigo'] == 'TEST'


@pytest.mark.django_db
class TestDepartamentoSerializer:
    """Tests for DepartamentoSerializer."""
    
    def test_serialize_departamento(self):
        """Test serializing a departamento."""
        dept = Departamento.objects.create(
            codigo='TEST',
            nombre='Test Departamento'
        )
        
        serializer = DepartamentoSerializer(dept)
        data = serializer.data
        
        assert data['codigo'] == 'TEST'
        assert data['nombre'] == 'Test Departamento'
        assert 'municipios_count' in data
    
    def test_serialize_departamento_con_municipios(self):
        """Test serializing departamento with municipios."""
        dept = Departamento.objects.create(codigo='TEST', nombre='Test Dept')
        Municipio.objects.create(
            departamento=dept,
            codigo='MUN1',
            nombre='Municipio 1'
        )
        Municipio.objects.create(
            departamento=dept,
            codigo='MUN2',
            nombre='Municipio 2'
        )
        
        serializer = DepartamentoConMunicipiosSerializer(dept)
        data = serializer.data
        
        assert len(data['municipios']) == 2


@pytest.mark.django_db
class TestMunicipioCreateSerializer:
    """Tests for MunicipioCreateSerializer."""
    
    def test_create_municipio(self):
        """Test creating a municipio."""
        dept = Departamento.objects.create(codigo='TEST', nombre='Test Dept')
        
        serializer = MunicipioCreateSerializer(data={
            'departamento': dept.id,
            'codigo': 'NEW_MUN',
            'nombre': 'New Municipio'
        })
        
        assert serializer.is_valid()
        municipio = serializer.save()
        
        assert municipio.codigo == 'NEW_MUN'
        assert municipio.departamento == dept
    
    def test_create_duplicate_codigo_same_departamento(self):
        """Test creating municipio with duplicate codigo in same departamento."""
        dept = Departamento.objects.create(codigo='TEST', nombre='Test Dept')
        Municipio.objects.create(
            departamento=dept,
            codigo='EXISTING',
            nombre='Existing'
        )
        
        serializer = MunicipioCreateSerializer(data={
            'departamento': dept.id,
            'codigo': 'EXISTING',
            'nombre': 'New Municipio'
        })
        
        assert not serializer.is_valid()
        # The error is in non_field_errors for unique constraint (departamento, codigo)
        assert 'non_field_errors' in serializer.errors

