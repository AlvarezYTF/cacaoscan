"""
Tests for Catalogos Views (ViewSets).
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from catalogos.models import Tema, Parametro, Departamento, Municipio


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def tema():
    """Create a theme."""
    return Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento',
        descripcion='Tipos de documentos de identidad',
        activo=True
    )


@pytest.fixture
def parametro(tema):
    """Create a parameter."""
    return Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía',
        descripcion='Cédula de ciudadanía colombiana',
        activo=True
    )


@pytest.fixture
def departamento():
    """Create a department."""
    return Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )


@pytest.fixture
def municipio(departamento):
    """Create a municipality."""
    return Municipio.objects.create(
        departamento=departamento,
        codigo='05001',
        nombre='Medellín'
    )


@pytest.mark.django_db
class TestTemaViewSet:
    """Tests for TemaViewSet."""

    def test_list_temas(self, api_client, tema):
        """Test listing all themes."""
        response = api_client.get('/api/v1/temas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == 'TIPO_DOC'

    def test_retrieve_tema(self, api_client, tema, parametro):
        """Test retrieving a theme with parameters."""
        response = api_client.get(f'/api/v1/temas/{tema.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'TIPO_DOC'
        assert 'parametros' in response.data
        assert len(response.data['parametros']) == 1

    def test_create_tema(self, api_client):
        """Test creating a new theme."""
        data = {
            'codigo': 'SEXO',
            'nombre': 'Sexo',
            'descripcion': 'Género de la persona',
            'activo': True
        }
        
        response = api_client.post('/api/v1/temas/', data=data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == 'SEXO'
        
        # Verify in database
        tema = Tema.objects.get(codigo='SEXO')
        assert tema.nombre == 'Sexo'

    def test_update_tema(self, api_client, tema):
        """Test updating a theme."""
        data = {
            'codigo': 'TIPO_DOC',
            'nombre': 'Tipo de Documento Actualizado',
            'descripcion': 'Descripción actualizada',
            'activo': True
        }
        
        response = api_client.put(
            f'/api/v1/temas/{tema.id}/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'Tipo de Documento Actualizado'
        
        # Verify in database
        tema.refresh_from_db()
        assert tema.nombre == 'Tipo de Documento Actualizado'

    def test_delete_tema(self, api_client, tema):
        """Test deleting a theme."""
        response = api_client.delete(f'/api/v1/temas/{tema.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        assert not Tema.objects.filter(id=tema.id).exists()

    def test_parametros_action(self, api_client, tema, parametro):
        """Test custom parametros action."""
        # Create inactive parameter
        Parametro.objects.create(
            tema=tema,
            codigo='CE',
            nombre='Cédula de Extranjería',
            activo=False
        )
        
        # Get all parameters
        response = api_client.get(f'/api/v1/temas/{tema.id}/parametros/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Get only active parameters
        response = api_client.get(
            f'/api/v1/temas/{tema.id}/parametros/?activos=true'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == 'CC'


@pytest.mark.django_db
class TestParametroViewSet:
    """Tests for ParametroViewSet."""

    def test_list_parametros(self, api_client, tema, parametro):
        """Test listing all parameters."""
        response = api_client.get('/api/v1/parametros/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == 'CC'

    def test_retrieve_parametro(self, api_client, tema, parametro):
        """Test retrieving a parameter."""
        response = api_client.get(f'/api/v1/parametros/{parametro.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'CC'
        assert 'tema_nombre' in response.data
        assert response.data['tema_nombre'] == 'Tipo de Documento'

    def test_create_parametro(self, api_client, tema):
        """Test creating a new parameter."""
        data = {
            'tema': tema.id,
            'codigo': 'CE',
            'nombre': 'Cédula de Extranjería',
            'descripcion': 'Cédula de extranjería',
            'activo': True
        }
        
        response = api_client.post('/api/v1/parametros/', data=data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == 'CE'
        
        # Verify in database
        parametro = Parametro.objects.get(codigo='CE', tema=tema)
        assert parametro.nombre == 'Cédula de Extranjería'

    def test_create_parametro_codigo_duplicado(self, api_client, tema, parametro):
        """Test creating parameter with duplicate code fails."""
        data = {
            'tema': tema.id,
            'codigo': 'CC',  # Duplicate
            'nombre': 'Otro CC',
            'activo': True
        }
        
        response = api_client.post('/api/v1/parametros/', data=data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_by_tema_id(self, api_client, tema):
        """Test filtering parameters by tema ID."""
        # Create another theme and parameter
        otro_tema = Tema.objects.create(
            codigo='SEXO',
            nombre='Sexo',
            activo=True
        )
        Parametro.objects.create(
            tema=otro_tema,
            codigo='M',
            nombre='Masculino',
            activo=True
        )
        
        # Create parameter for first theme
        Parametro.objects.create(
            tema=tema,
            codigo='CE',
            nombre='Cédula de Extranjería',
            activo=True
        )
        
        response = api_client.get(f'/api/v1/parametros/?tema={tema.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == 'CE'

    def test_filter_by_tema_codigo(self, api_client, tema):
        """Test filtering parameters by tema code."""
        # Create another theme and parameter
        otro_tema = Tema.objects.create(
            codigo='SEXO',
            nombre='Sexo',
            activo=True
        )
        Parametro.objects.create(
            tema=otro_tema,
            codigo='M',
            nombre='Masculino',
            activo=True
        )
        
        # Create parameter for first theme
        Parametro.objects.create(
            tema=tema,
            codigo='CE',
            nombre='Cédula de Extranjería',
            activo=True
        )
        
        response = api_client.get('/api/v1/parametros/?tema=TIPO_DOC')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == 'CE'

    def test_filter_activos(self, api_client, tema):
        """Test filtering only active parameters."""
        # Create active and inactive parameters
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
            activo=False
        )
        
        response = api_client.get('/api/v1/parametros/?activos=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(p['activo'] for p in response.data)

    def test_by_tema_action(self, api_client, tema, parametro):
        """Test custom by_tema action."""
        response = api_client.get(f'/api/v1/parametros/tema/{tema.codigo}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tema' in response.data
        assert 'parametros' in response.data
        assert response.data['tema']['codigo'] == 'TIPO_DOC'
        assert len(response.data['parametros']) == 1

    def test_by_tema_action_not_found(self, api_client):
        """Test by_tema action with non-existent tema."""
        response = api_client.get('/api/v1/parametros/tema/INEXISTENTE/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrado' in response.data['error']

    def test_by_tema_action_filter_activos(self, api_client, tema):
        """Test by_tema action with activos filter."""
        # Create active and inactive parameters
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
            activo=False
        )
        
        response = api_client.get(
            f'/api/v1/parametros/tema/{tema.codigo}/?activos=true'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['parametros']) == 1
        assert response.data['parametros'][0]['codigo'] == 'CE'

    def test_update_parametro(self, api_client, tema, parametro):
        """Test updating a parameter."""
        data = {
            'tema': tema.id,
            'codigo': 'CC',
            'nombre': 'Cédula de Ciudadanía Actualizada',
            'descripcion': 'Descripción actualizada',
            'activo': True
        }
        
        response = api_client.put(
            f'/api/v1/parametros/{parametro.id}/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'Cédula de Ciudadanía Actualizada'
        
        # Verify in database
        parametro.refresh_from_db()
        assert parametro.nombre == 'Cédula de Ciudadanía Actualizada'

    def test_delete_parametro(self, api_client, tema, parametro):
        """Test deleting a parameter."""
        response = api_client.delete(f'/api/v1/parametros/{parametro.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        assert not Parametro.objects.filter(id=parametro.id).exists()


@pytest.mark.django_db
class TestDepartamentoViewSet:
    """Tests for DepartamentoViewSet."""

    def test_list_departamentos(self, api_client, departamento):
        """Test listing all departments."""
        response = api_client.get('/api/v1/departamentos/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == '05'

    def test_retrieve_departamento(self, api_client, departamento, municipio):
        """Test retrieving a department with municipalities."""
        response = api_client.get(f'/api/v1/departamentos/{departamento.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == '05'
        assert 'municipios' in response.data
        assert len(response.data['municipios']) == 1

    def test_create_departamento(self, api_client):
        """Test creating a new department."""
        data = {
            'codigo': '11',
            'nombre': 'Bogotá D.C.'
        }
        
        response = api_client.post('/api/v1/departamentos/', data=data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == '11'
        
        # Verify in database
        dept = Departamento.objects.get(codigo='11')
        assert dept.nombre == 'Bogotá D.C.'

    def test_update_departamento(self, api_client, departamento):
        """Test updating a department."""
        data = {
            'codigo': '05',
            'nombre': 'Antioquia Actualizado'
        }
        
        response = api_client.put(
            f'/api/v1/departamentos/{departamento.id}/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'Antioquia Actualizado'
        
        # Verify in database
        departamento.refresh_from_db()
        assert departamento.nombre == 'Antioquia Actualizado'

    def test_delete_departamento(self, api_client, departamento):
        """Test deleting a department."""
        response = api_client.delete(f'/api/v1/departamentos/{departamento.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        assert not Departamento.objects.filter(id=departamento.id).exists()

    def test_municipios_action(self, api_client, departamento, municipio):
        """Test custom municipios action."""
        # Create another municipality
        Municipio.objects.create(
            departamento=departamento,
            codigo='05002',
            nombre='Bello'
        )
        
        response = api_client.get(f'/api/v1/departamentos/{departamento.id}/municipios/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


@pytest.mark.django_db
class TestMunicipioViewSet:
    """Tests for MunicipioViewSet."""

    def test_list_municipios(self, api_client, departamento, municipio):
        """Test listing all municipalities."""
        response = api_client.get('/api/v1/municipios/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == '05001'

    def test_retrieve_municipio(self, api_client, departamento, municipio):
        """Test retrieving a municipality."""
        response = api_client.get(f'/api/v1/municipios/{municipio.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == '05001'
        assert 'departamento_nombre' in response.data
        assert response.data['departamento_nombre'] == 'Antioquia'

    def test_create_municipio(self, api_client, departamento):
        """Test creating a new municipality."""
        data = {
            'departamento': departamento.id,
            'codigo': '05002',
            'nombre': 'Bello'
        }
        
        response = api_client.post('/api/v1/municipios/', data=data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == '05002'
        
        # Verify in database
        mun = Municipio.objects.get(codigo='05002', departamento=departamento)
        assert mun.nombre == 'Bello'

    def test_create_municipio_codigo_duplicado(self, api_client, departamento, municipio):
        """Test creating municipality with duplicate code fails."""
        data = {
            'departamento': departamento.id,
            'codigo': '05001',  # Duplicate
            'nombre': 'Otro Medellín'
        }
        
        response = api_client.post('/api/v1/municipios/', data=data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_by_departamento(self, api_client, departamento):
        """Test filtering municipalities by department."""
        # Create another department and municipality
        otro_dept = Departamento.objects.create(
            codigo='11',
            nombre='Bogotá D.C.'
        )
        Municipio.objects.create(
            departamento=otro_dept,
            codigo='11001',
            nombre='Bogotá'
        )
        
        # Create municipality for first department
        Municipio.objects.create(
            departamento=departamento,
            codigo='05002',
            nombre='Bello'
        )
        
        response = api_client.get(f'/api/v1/municipios/?departamento={departamento.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == '05002'

    def test_filter_by_nombre(self, api_client, departamento, municipio):
        """Test filtering municipalities by name."""
        # Create another municipality
        Municipio.objects.create(
            departamento=departamento,
            codigo='05002',
            nombre='Bello'
        )
        
        response = api_client.get('/api/v1/municipios/?nombre=Medellín')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['codigo'] == '05001'

    def test_by_departamento_action(self, api_client, departamento, municipio):
        """Test custom by_departamento action."""
        response = api_client.get(f'/api/v1/municipios/departamento/{departamento.codigo}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'departamento' in response.data
        assert 'municipios' in response.data
        assert response.data['departamento']['codigo'] == '05'
        assert len(response.data['municipios']) == 1

    def test_by_departamento_action_not_found(self, api_client):
        """Test by_departamento action with non-existent department."""
        response = api_client.get('/api/v1/municipios/departamento/INEXISTENTE/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrado' in response.data['error']

    def test_update_municipio(self, api_client, departamento, municipio):
        """Test updating a municipality."""
        data = {
            'departamento': departamento.id,
            'codigo': '05001',
            'nombre': 'Medellín Actualizado'
        }
        
        response = api_client.put(
            f'/api/v1/municipios/{municipio.id}/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'Medellín Actualizado'
        
        # Verify in database
        municipio.refresh_from_db()
        assert municipio.nombre == 'Medellín Actualizado'

    def test_delete_municipio(self, api_client, departamento, municipio):
        """Test deleting a municipality."""
        response = api_client.delete(f'/api/v1/municipios/{municipio.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        assert not Municipio.objects.filter(id=municipio.id).exists()

