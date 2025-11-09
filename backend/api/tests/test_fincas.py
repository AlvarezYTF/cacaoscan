"""
Tests para gestión de fincas en CacaoScan.
"""
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from api.models import Finca


class FincaModelTest(TestCase):
    """Tests para el modelo Finca."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
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
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        self.token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin_user)
        
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
        self.client.force_authenticate(user=self.user, token=self.token)
        
        response = self.client.post('/api/fincas/', self.finca_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Finca.objects.count(), 1)
        
        finca = Finca.objects.first()
        self.assertEqual(finca.nombre, 'Finca Test')
        self.assertEqual(finca.agricultor, self.user)
    
    def test_create_finca_unauthorized(self):
        """Test de creación de finca sin autenticación."""
        response = self.client.post('/api/fincas/', self.finca_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_finca_invalid_data(self):
        """Test de creación de finca con datos inválidos."""
        self.client.force_authenticate(user=self.user, token=self.token)
        
        invalid_data = {
            'nombre': '',  # Nombre vacío
            'ubicacion': 'Vereda Test',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': -1  # Hectáreas negativas
        }
        
        response = self.client.post('/api/fincas/', invalid_data, format='json')
        
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
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        Finca.objects.create(
            nombre='Otra Finca',
            ubicacion='Otra Vereda',
            municipio='Otro Municipio',
            departamento='Otro Departamento',
            hectareas=3.0,
            agricultor=other_user
        )
        
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get('/api/fincas/')
        
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
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        Finca.objects.create(
            nombre='Otra Finca',
            ubicacion='Otra Vereda',
            municipio='Otro Municipio',
            departamento='Otro Departamento',
            hectareas=3.0,
            agricultor=other_user
        )
        
        self.client.force_authenticate(user=self.admin_user, token=self.admin_token)
        response = self.client.get('/api/fincas/')
        
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
        
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(f'/api/fincas/{finca.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Finca Test')
        self.assertIn('estadisticas', response.data)
    
    def test_finca_detail_not_found(self):
        """Test de obtención de detalles de finca inexistente."""
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get('/api/fincas/999/')
        
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
        
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.put(f'/api/fincas/{finca.id}/update/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        finca.refresh_from_db()
        self.assertEqual(finca.nombre, 'Finca Actualizada')
        self.assertEqual(finca.hectareas, 7.0)
    
    def test_finca_delete_success(self):
        """Test de eliminación exitosa de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Vereda Test',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.5,
            agricultor=self.user
        )
        
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.delete(f'/api/fincas/{finca.id}/delete/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Finca.objects.count(), 0)
    
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
        
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(f'/api/fincas/{finca.id}/stats/')
        
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
        
        self.client.force_authenticate(user=self.user, token=self.token)
        
        # Test búsqueda por nombre
        response = self.client.get('/api/fincas/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtro por municipio
        response = self.client.get('/api/fincas/?municipio=Test Municipio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtro por departamento
        response = self.client.get('/api/fincas/?departamento=Test Departamento')
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
        
        self.client.force_authenticate(user=self.user, token=self.token)
        
        # Test primera página
        response = self.client.get('/api/fincas/?page=1&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(response.data['total_pages'], 3)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Test segunda página
        response = self.client.get('/api/fincas/?page=2&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])


