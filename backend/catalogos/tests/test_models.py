"""
Tests for Catalogos Models.
"""
import pytest
from django.core.exceptions import ValidationError

from catalogos.models import Departamento, Municipio, Tema, Parametro


@pytest.mark.django_db
class TestDepartamento:
    """Tests for Departamento model."""

    def test_create_departamento(self):
        """Test creating a departamento."""
        dept = Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        
        assert dept.codigo == '05'
        assert dept.nombre == 'Antioquia'

    def test_departamento_str_representation(self):
        """Test string representation."""
        dept = Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        
        assert str(dept) == 'Antioquia'

    def test_municipios_count_property(self):
        """Test municipios_count property."""
        dept = Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        
        assert dept.municipios_count == 0
        
        Municipio.objects.create(
            departamento=dept,
            codigo='001',
            nombre='Medellín'
        )
        Municipio.objects.create(
            departamento=dept,
            codigo='002',
            nombre='Bello'
        )
        
        assert dept.municipios_count == 2

    def test_unique_codigo(self):
        """Test that codigo must be unique."""
        Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Departamento.objects.create(
                codigo='05',  # Duplicate
                nombre='Another Department'
            )


@pytest.mark.django_db
class TestMunicipio:
    """Tests for Municipio model."""

    def test_create_municipio(self):
        """Test creating a municipio."""
        dept = Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        
        muni = Municipio.objects.create(
            departamento=dept,
            codigo='001',
            nombre='Medellín'
        )
        
        assert muni.departamento == dept
        assert muni.codigo == '001'
        assert muni.nombre == 'Medellín'

    def test_municipio_str_representation(self):
        """Test string representation."""
        dept = Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        muni = Municipio.objects.create(
            departamento=dept,
            codigo='001',
            nombre='Medellín'
        )
        
        assert 'Medellín' in str(muni)
        assert 'Antioquia' in str(muni)

    def test_unique_together_departamento_codigo(self):
        """Test unique_together constraint for departamento and codigo."""
        dept1 = Departamento.objects.create(codigo='05', nombre='Antioquia')
        dept2 = Departamento.objects.create(codigo='11', nombre='Bogotá')
        
        Municipio.objects.create(
            departamento=dept1,
            codigo='001',
            nombre='Medellín'
        )
        
        # Same codigo in different departamento should be allowed
        Municipio.objects.create(
            departamento=dept2,
            codigo='001',
            nombre='Bogotá'
        )
        
        # Same codigo in same departamento should fail
        with pytest.raises(Exception):  # IntegrityError
            Municipio.objects.create(
                departamento=dept1,
                codigo='001',  # Duplicate in same departamento
                nombre='Another City'
            )

    def test_cascade_delete(self):
        """Test that municipios are deleted when departamento is deleted."""
        dept = Departamento.objects.create(
            codigo='05',
            nombre='Antioquia'
        )
        muni = Municipio.objects.create(
            departamento=dept,
            codigo='001',
            nombre='Medellín'
        )
        muni_id = muni.id
        
        dept.delete()
        
        assert not Municipio.objects.filter(id=muni_id).exists()


@pytest.mark.django_db
class TestTema:
    """Tests for Tema model."""

    def test_create_tema(self):
        """Test creating a tema."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento',
            descripcion='Tipos de documentos de identidad'
        )
        
        assert tema.codigo == 'TIPO_DOC'
        assert tema.nombre == 'Tipo de Documento'
        assert tema.activo is True  # Default

    def test_tema_str_representation(self):
        """Test string representation."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        
        assert 'TIPO_DOC' in str(tema)
        assert 'Tipo de Documento' in str(tema)

    def test_parametros_count_property(self):
        """Test parametros_count property."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        
        assert tema.parametros_count == 0
        
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
            codigo='INACTIVE',
            nombre='Inactive',
            activo=False  # Should not count
        )
        
        assert tema.parametros_count == 2

    def test_unique_codigo(self):
        """Test that codigo must be unique."""
        Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Tema.objects.create(
                codigo='TIPO_DOC',  # Duplicate
                nombre='Another Theme'
            )

    def test_activo_default(self):
        """Test that activo defaults to True."""
        tema = Tema.objects.create(
            codigo='TEST',
            nombre='Test'
        )
        
        assert tema.activo is True


@pytest.mark.django_db
class TestParametro:
    """Tests for Parametro model."""

    def test_create_parametro(self):
        """Test creating a parametro."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        
        param = Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía',
            descripcion='Documento nacional de identidad'
        )
        
        assert param.tema == tema
        assert param.codigo == 'CC'
        assert param.nombre == 'Cédula de Ciudadanía'
        assert param.activo is True  # Default

    def test_parametro_str_representation(self):
        """Test string representation."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        param = Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía'
        )
        
        assert 'CC' in str(param)
        assert 'Cédula' in str(param)

    def test_unique_together_tema_codigo(self):
        """Test unique_together constraint for tema and codigo."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        
        Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía'
        )
        
        # Same codigo in same tema should fail
        with pytest.raises(Exception):  # IntegrityError
            Parametro.objects.create(
                tema=tema,
                codigo='CC',  # Duplicate in same tema
                nombre='Another Parameter'
            )

    def test_cascade_delete(self):
        """Test that parametros are deleted when tema is deleted."""
        tema = Tema.objects.create(
            codigo='TIPO_DOC',
            nombre='Tipo de Documento'
        )
        param = Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Cédula de Ciudadanía'
        )
        param_id = param.id
        
        tema.delete()
        
        assert not Parametro.objects.filter(id=param_id).exists()

    def test_activo_default(self):
        """Test that activo defaults to True."""
        tema = Tema.objects.create(
            codigo='TEST',
            nombre='Test'
        )
        param = Parametro.objects.create(
            tema=tema,
            codigo='TEST_PARAM',
            nombre='Test Parameter'
        )
        
        assert param.activo is True

