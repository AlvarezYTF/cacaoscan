"""
Unit tests for catalogos models (Departamento, Municipio, Tema, Parametro).
Tests cover model creation, properties, methods, and relationships.
"""
import pytest
from django.core.exceptions import ValidationError

from catalogos.models import Departamento, Municipio, Tema, Parametro


@pytest.fixture
def departamento():
    """Create a test department."""
    return Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )


@pytest.fixture
def municipio(departamento):
    """Create a test municipality."""
    return Municipio.objects.create(
        departamento=departamento,
        codigo='05001',
        nombre='Medellín'
    )


@pytest.fixture
def tema():
    """Create a test theme."""
    return Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento',
        descripcion='Tipos de documentos de identidad',
        activo=True
    )


@pytest.fixture
def parametro(tema):
    """Create a test parameter."""
    return Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía',
        descripcion='Documento de identidad colombiano',
        activo=True
    )


class TestDepartamento:
    """Tests for Departamento model."""
    
    def test_departamento_creation(self):
        """Test basic departamento creation."""
        dept = Departamento.objects.create(
            codigo='11',
            nombre='Bogotá D.C.'
        )
        
        assert dept.codigo == '11'
        assert dept.nombre == 'Bogotá D.C.'
    
    def test_departamento_str_representation(self, departamento):
        """Test string representation of departamento."""
        assert str(departamento) == 'Antioquia'
    
    def test_departamento_municipios_count_property_empty(self, departamento):
        """Test municipios_count property when no municipios exist."""
        assert departamento.municipios_count == 0
    
    def test_departamento_municipios_count_property_with_municipios(self, departamento):
        """Test municipios_count property with municipios."""
        Municipio.objects.create(
            departamento=departamento,
            codigo='05001',
            nombre='Medellín'
        )
        Municipio.objects.create(
            departamento=departamento,
            codigo='05002',
            nombre='Bello'
        )
        
        assert departamento.municipios_count == 2
    
    def test_departamento_unique_codigo(self):
        """Test that codigo is unique."""
        Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Departamento.objects.create(
                codigo='05',
                nombre='Another Department'
            )
    
    def test_departamento_ordering(self):
        """Test that departamentos are ordered by nombre."""
        dept1 = Departamento.objects.create(codigo='01', nombre='Amazonas')
        dept2 = Departamento.objects.create(codigo='02', nombre='Antioquia')
        dept3 = Departamento.objects.create(codigo='03', nombre='Arauca')
        
        departamentos = list(Departamento.objects.all())
        assert departamentos[0].nombre == 'Amazonas'
        assert departamentos[1].nombre == 'Antioquia'
        assert departamentos[2].nombre == 'Arauca'


class TestMunicipio:
    """Tests for Municipio model."""
    
    def test_municipio_creation(self, departamento):
        """Test basic municipio creation."""
        mun = Municipio.objects.create(
            departamento=departamento,
            codigo='05002',
            nombre='Bello'
        )
        
        assert mun.departamento == departamento
        assert mun.codigo == '05002'
        assert mun.nombre == 'Bello'
    
    def test_municipio_str_representation(self, municipio):
        """Test string representation of municipio."""
        assert str(municipio) == 'Medellín, Antioquia'
    
    def test_municipio_unique_together_constraint(self, departamento):
        """Test unique_together constraint on (departamento, codigo)."""
        Municipio.objects.create(
            departamento=departamento,
            codigo='05001',
            nombre='Medellín'
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with pytest.raises(Exception):  # IntegrityError
            Municipio.objects.create(
                departamento=departamento,
                codigo='05001',
                nombre='Another City'
            )
    
    def test_municipio_same_codigo_different_departamento(self):
        """Test that same codigo can exist in different departamentos."""
        dept1 = Departamento.objects.create(codigo='05', nombre='Antioquia')
        dept2 = Departamento.objects.create(codigo='11', nombre='Bogotá')
        
        mun1 = Municipio.objects.create(
            departamento=dept1,
            codigo='05001',
            nombre='Medellín'
        )
        
        mun2 = Municipio.objects.create(
            departamento=dept2,
            codigo='05001',
            nombre='Bogotá'
        )
        
        assert mun1.codigo == mun2.codigo
        assert mun1.departamento != mun2.departamento
    
    def test_municipio_cascade_delete_with_departamento(self, departamento):
        """Test that municipios are deleted when departamento is deleted."""
        mun = Municipio.objects.create(
            departamento=departamento,
            codigo='05001',
            nombre='Medellín'
        )
        mun_id = mun.id
        
        departamento.delete()
        
        assert not Municipio.objects.filter(id=mun_id).exists()
    
    def test_municipio_ordering(self, departamento):
        """Test that municipios are ordered by departamento and nombre."""
        mun1 = Municipio.objects.create(
            departamento=departamento,
            codigo='05001',
            nombre='Medellín'
        )
        mun2 = Municipio.objects.create(
            departamento=departamento,
            codigo='05002',
            nombre='Bello'
        )
        
        municipios = list(Municipio.objects.filter(departamento=departamento))
        assert municipios[0].nombre == 'Bello'
        assert municipios[1].nombre == 'Medellín'


class TestTema:
    """Tests for Tema model."""
    
    def test_tema_creation(self):
        """Test basic tema creation."""
        tema = Tema.objects.create(
            codigo='SEXO',
            nombre='Sexo',
            descripcion='Género de la persona',
            activo=True
        )
        
        assert tema.codigo == 'SEXO'
        assert tema.nombre == 'Sexo'
        assert tema.descripcion == 'Género de la persona'
        assert tema.activo is True
    
    def test_tema_str_representation(self, tema):
        """Test string representation of tema."""
        assert str(tema) == 'TIPO_DOC - Tipo de Documento'
    
    def test_tema_default_activo(self):
        """Test default activo value."""
        tema = Tema.objects.create(
            codigo='TEST',
            nombre='Test Theme'
        )
        
        assert tema.activo is True
    
    def test_tema_parametros_count_property_empty(self, tema):
        """Test parametros_count property when no parametros exist."""
        assert tema.parametros_count == 0
    
    def test_tema_parametros_count_property_with_parametros(self, tema):
        """Test parametros_count property with parametros."""
        Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía',
            activo=True
        )
        Parametro.objects.create(
            tema=tema,
            codigo='CE',
            nombre='Cédula de Extranjería',
            activo=True
        )
        Parametro.objects.create(
            tema=tema,
            codigo='PA',
            nombre='Pasaporte',
            activo=False  # Inactive
        )
        
        # Should only count active parametros
        assert tema.parametros_count == 2
    
    def test_tema_unique_codigo(self):
        """Test that codigo is unique."""
        Tema.objects.create(
            codigo='TEST',
            nombre='Test Theme'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Tema.objects.create(
                codigo='TEST',
                nombre='Another Theme'
            )
    
    def test_tema_ordering(self):
        """Test that temas are ordered by nombre."""
        tema1 = Tema.objects.create(codigo='A', nombre='Alpha')
        tema2 = Tema.objects.create(codigo='B', nombre='Beta')
        tema3 = Tema.objects.create(codigo='C', nombre='Gamma')
        
        temas = list(Tema.objects.all())
        assert temas[0].nombre == 'Alpha'
        assert temas[1].nombre == 'Beta'
        assert temas[2].nombre == 'Gamma'


class TestParametro:
    """Tests for Parametro model."""
    
    def test_parametro_creation(self, tema):
        """Test basic parametro creation."""
        param = Parametro.objects.create(
            tema=tema,
            codigo='CE',
            nombre='Cédula de Extranjería',
            descripcion='Documento para extranjeros',
            activo=True
        )
        
        assert param.tema == tema
        assert param.codigo == 'CE'
        assert param.nombre == 'Cédula de Extranjería'
        assert param.descripcion == 'Documento para extranjeros'
        assert param.activo is True
    
    def test_parametro_str_representation(self, parametro):
        """Test string representation of parametro."""
        assert str(parametro) == 'TIPO_DOC - CC: Cédula de Ciudadanía'
    
    def test_parametro_default_activo(self, tema):
        """Test default activo value."""
        param = Parametro.objects.create(
            tema=tema,
            codigo='TEST',
            nombre='Test Parameter'
        )
        
        assert param.activo is True
    
    def test_parametro_unique_together_constraint(self, tema):
        """Test unique_together constraint on (tema, codigo)."""
        Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía'
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with pytest.raises(Exception):  # IntegrityError
            Parametro.objects.create(
                tema=tema,
                codigo='CC',
                nombre='Another Name'
            )
    
    def test_parametro_same_codigo_different_tema(self):
        """Test that same codigo can exist in different temas."""
        tema1 = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo Documento')
        tema2 = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        
        param1 = Parametro.objects.create(
            tema=tema1,
            codigo='M',
            nombre='Masculino'
        )
        
        param2 = Parametro.objects.create(
            tema=tema2,
            codigo='M',
            nombre='Masculino'
        )
        
        assert param1.codigo == param2.codigo
        assert param1.tema != param2.tema
    
    def test_parametro_cascade_delete_with_tema(self, tema):
        """Test that parametros are deleted when tema is deleted."""
        param = Parametro.objects.create(
            tema=tema,
            codigo='TEST',
            nombre='Test Parameter'
        )
        param_id = param.id
        
        tema.delete()
        
        assert not Parametro.objects.filter(id=param_id).exists()
    
    def test_parametro_ordering(self, tema):
        """Test that parametros are ordered by tema and codigo."""
        param1 = Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía'
        )
        param2 = Parametro.objects.create(
            tema=tema,
            codigo='CE',
            nombre='Cédula de Extranjería'
        )
        param3 = Parametro.objects.create(
            tema=tema,
            codigo='PA',
            nombre='Pasaporte'
        )
        
        parametros = list(Parametro.objects.filter(tema=tema))
        assert parametros[0].codigo == 'CC'
        assert parametros[1].codigo == 'CE'
        assert parametros[2].codigo == 'PA'

