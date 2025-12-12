"""
Tests for catalogos views.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from catalogos.models import Tema, Parametro, Departamento, Municipio


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.mark.django_db
class TestTemaViewSet:
    """Tests for TemaViewSet."""
    
    @pytest.fixture
    def tema(self):
        """Create test tema."""
        return Tema.objects.create(
            codigo='TEST',
            nombre='Test Tema',
            descripcion='Test Description',
            activo=True
        )
    
    def test_list_temas(self, api_client, tema):
        """Test listing temas."""
        response = api_client.get('/api/v1/temas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(t['codigo'] == 'TEST' for t in response.data)
    
    def test_retrieve_tema(self, api_client, tema):
        """Test retrieving a tema."""
        response = api_client.get(f'/api/v1/temas/{tema.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'TEST'
        assert 'parametros' in response.data
    
    def test_tema_parametros_action(self, api_client, tema):
        """Test tema parametros custom action."""
        Parametro.objects.create(
            tema=tema,
            codigo='PARAM1',
            nombre='Param 1',
            activo=True
        )
        
        response = api_client.get(f'/api/v1/temas/{tema.id}/parametros/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_tema_parametros_filter_activos(self, api_client, tema):
        """Test tema parametros with activos filter."""
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
        
        response = api_client.get(f'/api/v1/temas/{tema.id}/parametros/?activos=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(p['activo'] for p in response.data)


@pytest.mark.django_db
class TestParametroViewSet:
    """Tests for ParametroViewSet."""
    
    @pytest.fixture
    def parametro(self):
        """Create test parametro."""
        tema = Tema.objects.create(codigo='TEST', nombre='Test Tema')
        return Parametro.objects.create(
            tema=tema,
            codigo='TEST_PARAM',
            nombre='Test Parametro',
            activo=True
        )
    
    def test_list_parametros(self, api_client, parametro):
        """Test listing parametros."""
        response = api_client.get('/api/v1/parametros/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_filter_parametros_by_tema_id(self, api_client, parametro):
        """Test filtering parametros by tema ID."""
        response = api_client.get(f'/api/v1/parametros/?tema={parametro.tema.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(p['id'] == parametro.id or p['tema'] == parametro.tema.id for p in response.data)
    
    def test_filter_parametros_by_tema_codigo(self, api_client, parametro):
        """Test filtering parametros by tema codigo."""
        response = api_client.get(f'/api/v1/parametros/?tema={parametro.tema.codigo}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_filter_parametros_activos(self, api_client, parametro):
        """Test filtering active parametros."""
        response = api_client.get('/api/v1/parametros/?activos=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(p['activo'] for p in response.data)
    
    def test_parametros_by_tema_action(self, api_client, parametro):
        """Test parametros by_tema custom action."""
        response = api_client.get(f'/api/v1/parametros/tema/{parametro.tema.codigo}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tema' in response.data
        assert 'parametros' in response.data
    
    def test_parametros_by_tema_not_found(self, api_client):
        """Test parametros by_tema with non-existent tema."""
        response = api_client.get('/api/v1/parametros/tema/NONEXISTENT/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDepartamentoViewSet:
    """Tests for DepartamentoViewSet."""
    
    @pytest.fixture
    def departamento(self):
        """Create test departamento."""
        return Departamento.objects.create(
            codigo='TEST',
            nombre='Test Departamento'
        )
    
    def test_list_departamentos(self, api_client, departamento):
        """Test listing departamentos."""
        response = api_client.get('/api/v1/departamentos/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_retrieve_departamento(self, api_client, departamento):
        """Test retrieving a departamento."""
        response = api_client.get(f'/api/v1/departamentos/{departamento.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'TEST'
        assert 'municipios' in response.data
    
    def test_departamento_municipios_action(self, api_client, departamento):
        """Test departamento municipios custom action."""
        Municipio.objects.create(
            departamento=departamento,
            codigo='MUN1',
            nombre='Test Municipio'
        )
        
        response = api_client.get(f'/api/v1/departamentos/{departamento.id}/municipios/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestMunicipioViewSet:
    """Tests for MunicipioViewSet."""
    
    @pytest.fixture
    def municipio(self):
        """Create test municipio."""
        dept = Departamento.objects.create(codigo='TEST', nombre='Test Dept')
        return Municipio.objects.create(
            departamento=dept,
            codigo='MUN1',
            nombre='Test Municipio'
        )
    
    def test_list_municipios(self, api_client, municipio):
        """Test listing municipios."""
        response = api_client.get('/api/v1/municipios/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_filter_municipios_by_departamento(self, api_client, municipio):
        """Test filtering municipios by departamento."""
        response = api_client.get(f'/api/v1/municipios/?departamento={municipio.departamento.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_filter_municipios_by_nombre(self, api_client, municipio):
        """Test filtering municipios by nombre."""
        response = api_client.get(f'/api/v1/municipios/?nombre=Test')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_municipios_by_departamento_action(self, api_client, municipio):
        """Test municipios by_departamento custom action."""
        response = api_client.get(f'/api/v1/municipios/departamento/{municipio.departamento.codigo}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'departamento' in response.data
        assert 'municipios' in response.data
    
    def test_municipios_by_departamento_not_found(self, api_client):
        """Test municipios by_departamento with non-existent departamento."""
        response = api_client.get('/api/v1/municipios/departamento/NONEXISTENT/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

