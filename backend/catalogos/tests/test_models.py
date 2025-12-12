"""
Tests for catalogos models.
"""
import pytest

from catalogos.models import Departamento, Municipio, Tema, Parametro


def test_departamento_str(db):
    """Test Departamento __str__ method."""
    dept = Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )
    
    assert str(dept) == 'Antioquia'


def test_departamento_municipios_count(db):
    """Test Departamento municipios_count property."""
    dept = Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )
    
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


def test_municipio_str(db):
    """Test Municipio __str__ method."""
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


def test_municipio_unique_together(db):
    """Test Municipio unique_together constraint."""
    dept = Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )
    
    Municipio.objects.create(
        departamento=dept,
        codigo='001',
        nombre='Medellín'
    )
    
    # Try to create duplicate
    with pytest.raises(Exception):  # IntegrityError or ValidationError
        Municipio.objects.create(
            departamento=dept,
            codigo='001',
            nombre='Another City'
        )


def test_tema_str(db):
    """Test Tema __str__ method."""
    tema = Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )
    
    assert 'TIPO_DOC' in str(tema)
    assert 'Tipo de Documento' in str(tema)


def test_tema_parametros_count(db):
    """Test Tema parametros_count property."""
    tema = Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )
    
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
        nombre='Inactive Param',
        activo=False
    )
    
    assert tema.parametros_count == 2  # Only active ones


def test_parametro_str(db):
    """Test Parametro __str__ method."""
    tema = Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )
    param = Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía'
    )
    
    assert 'TIPO_DOC' in str(param)
    assert 'CC' in str(param)
    assert 'Cédula de Ciudadanía' in str(param)


def test_parametro_unique_together(db):
    """Test Parametro unique_together constraint."""
    tema = Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )
    
    Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía'
    )
    
    # Try to create duplicate
    with pytest.raises(Exception):  # IntegrityError or ValidationError
        Parametro.objects.create(
            tema=tema,
            codigo='CC',
            nombre='Another Name'
        )


def test_parametro_default_activo(db):
    """Test Parametro default activo value."""
    tema = Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )
    param = Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía'
    )
    
    assert param.activo is True


def test_tema_default_activo(db):
    """Test Tema default activo value."""
    tema = Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento'
    )
    
    assert tema.activo is True


