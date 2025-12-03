"""
Tests para gestión de fincas en CacaoScan.
"""
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Finca
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_FIRST_NAME,
    TEST_ADMIN_LAST_NAME,
    TEST_OTHER_USER_USERNAME,
    TEST_OTHER_USER_EMAIL,
)


class FincaModelTest(TestCase):
    """Tests para el modelo Finca."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME
        )
    
    def test_finca_creation(self):
        """Test de creación de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        self.assertEqual(finca.nombre, 'Finca Test')
        self.assertEqual(finca.agricultor, self.user)
        self.assertTrue(finca.activa)
        self.assertIsNotNone(finca.fecha_registro)
    
    def test_finca_str_representation(self):
        """Test de representación string de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        expected_str = 'Finca Test - Test Municipio, Test Departamento'
        self.assertEqual(str(finca), expected_str)
    
    def test_finca_properties(self):
        """Test de propiedades calculadas de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        # Test propiedades básicas
        self.assertEqual(finca.total_lotes, 0)
        self.assertEqual(finca.lotes_activos, 0)
        self.assertEqual(finca.total_analisis, 0)
        self.assertEqual(finca.calidad_promedio, 0)
        
        # Test ubicación completa
        expected_ubicacion = 'Vereda Test, Test Municipio, Test Departamento'
        self.assertEqual(finca.ubicacion_completa, expected_ubicacion)
    
    def test_finca_estadisticas(self):
        """Test de método get_estadisticas."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        stats = finca.get_estadisticas()
        
        self.assertIn('total_lotes', stats)
        self.assertIn('lotes_activos', stats)
        self.assertIn('total_analisis', stats)
        self.assertIn('calidad_promedio', stats)
        self.assertIn('hectareas', stats)
        self.assertIn('fecha_registro', stats)
        self.assertIn('activa', stats)
        
        self.assertEqual(stats['hectareas'], 5.5)
        self.assertTrue(stats['activa'])


class FincaAPITest(APITestCase):
    """Tests para la API de fincas."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME
        )
        
        self.admin_user = User.objects.create_user(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD,
            first_name=TEST_ADMIN_FIRST_NAME,
            last_name=TEST_ADMIN_LAST_NAME,
            is_staff=True,
            is_superuser=True
        )
        
        # Authentication tokens will be set in setUp if needed
        
        self.finca_data = {
            'nombre': 'Finca Test',
            'ubicacion': 'Vereda Test',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': 5.5,
            'descripcion': 'Finca de prueba para tests'
        }
    
    def test_create_finca_success(self):
        """Test de creación exitosa de finca."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        
        response = self.client.post('/api/v1/fincas/', self.finca_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Finca.objects.count(), 1)
        
        finca = Finca.objects.first()
        self.assertEqual(finca.nombre, 'Finca Test')
        self.assertEqual(finca.agricultor, self.user)
    
    def test_create_finca_unauthorized(self):
        """Test de creación de finca sin autenticación."""
        response = self.client.post('/api/v1/fincas/', self.finca_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_finca_invalid_data(self):
        """Test de creación de finca con datos inválidos."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        
        invalid_data = {
            'nombre': '',  # Nombre vacío
            'ubicacion': 'Vereda Test',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': -1  # Hectáreas negativas
        }
        
        response = self.client.post('/api/v1/fincas/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)
    
    def test_list_fincas_user(self):
        """Test de listado de fincas para usuario normal."""
        # Crear finca para el usuario
        Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        # Crear finca para otro usuario
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_OTHER_USER_PASSWORD  # NOSONAR(S2068)
        )
        Finca.objects.create(
            nombre='Otra Finca',
            ubicacion='Otra Vereda',
            municipio='Otro Municipio',
            departamento='Otro Departamento',
            hectareas=3.0,
            agricultor=other_user
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.get('/api/v1/fincas/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Finca Test')
    
    def test_list_fincas_admin(self):
        """Test de listado de fincas para administrador."""
        # Crear fincas para diferentes usuarios
        Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email=TEST_OTHER_USER_EMAIL,
            password=TEST_OTHER_USER_PASSWORD  # NOSONAR(S2068)
        )
        Finca.objects.create(
            nombre='Otra Finca',
            ubicacion='Otra Vereda',
            municipio='Otro Municipio',
            departamento='Otro Departamento',
            hectareas=3.0,
            agricultor=other_user
        )
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.get('/api/v1/fincas/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_finca_detail_success(self):
        """Test de obtención de detalles de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.get(f'/api/v1/fincas/{finca.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Finca Test')
        self.assertIn('estadisticas', response.data)
    
    def test_finca_detail_not_found(self):
        """Test de obtención de detalles de finca inexistente."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.get('/api/v1/fincas/999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_finca_update_success(self):
        """Test de actualización exitosa de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        update_data = {
            'nombre': 'Finca Actualizada',
            'ubicacion': 'Vereda Actualizada',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': 7.0
        }
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.put(f'/api/v1/fincas/{finca.id}/update/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        finca.refresh_from_db()
        self.assertEqual(finca.nombre, 'Finca Actualizada')
        self.assertEqual(finca.hectareas, 7.0)
    
    def test_finca_delete_success(self):
        """Test de eliminación exitosa de finca (soft delete)."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        # Verificar que la finca está activa inicialmente
        self.assertTrue(finca.activa)
        self.assertEqual(Finca.objects.filter(activa=True).count(), 1)
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.delete(f'/api/v1/fincas/{finca.id}/delete/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar soft delete: la finca existe pero está desactivada
        finca.refresh_from_db()
        self.assertFalse(finca.activa)
        self.assertEqual(Finca.objects.count(), 1)  # La finca sigue existiendo
        self.assertEqual(Finca.objects.filter(activa=True).count(), 0)  # Pero no hay fincas activas
    
    def test_finca_stats_success(self):
        """Test de obtención de estadísticas de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        response = self.client.get(f'/api/v1/fincas/{finca.id}/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_lotes', response.data)
        self.assertIn('calidad_promedio', response.data)
        self.assertIn('finca_nombre', response.data)
    
    def test_finca_search_filter(self):
        """Test de búsqueda y filtros en listado de fincas."""
        Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        Finca.objects.create(
            nombre='Otra Finca',
            ubicacion='Otra Vereda',
            municipio='Otro Municipio',
            departamento='Otro Departamento',
            hectareas=3.0,
            agricultor=self.user
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        
        # Test búsqueda por nombre
        response = self.client.get('/api/v1/fincas/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtro por municipio
        response = self.client.get('/api/v1/fincas/?municipio=Test Municipio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtro por departamento
        response = self.client.get('/api/v1/fincas/?departamento=Test Departamento')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_finca_pagination(self):
        """Test de paginación en listado de fincas."""
        # Crear múltiples fincas
        for i in range(25):
            Finca.objects.create(
                nombre=f'Finca {i}',
                ubicacion=f'Vereda {i}',
                municipio=f'Municipio {i}',
                departamento=f'Departamento {i}',
                hectareas=5.0 + i,
                agricultor=self.user
            )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        
        # Test primera página
        response = self.client.get('/api/v1/fincas/?page=1&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(response.data['total_pages'], 3)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Test segunda página
        response = self.client.get('/api/v1/fincas/?page=2&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])


