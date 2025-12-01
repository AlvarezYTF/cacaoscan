"""
Unit tests for finca serializers.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

from rest_framework import serializers
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
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


class FincaSerializerTest(TestCase):
    """Tests for FincaSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.finca_serializers.Finca')
    def test_finca_serialization_success(self, mock_finca_model):
        """Test successful finca serialization."""
        mock_finca = Mock()
        mock_finca.id = 1
        mock_finca.nombre = 'Test Finca'
        mock_finca.ubicacion = 'Test Location'
        mock_finca.municipio = 'Test Municipality'
        mock_finca.departamento = 'Test Department'
        mock_finca.hectareas = Decimal('10.5')
        mock_finca.agricultor = self.user
        mock_finca.agricultor.get_full_name.return_value = 'Test User'
        mock_finca.agricultor.email = TEST_USER_EMAIL
        mock_finca.descripcion = 'Test description'
        mock_finca.coordenadas_lat = Decimal('4.6097')
        mock_finca.coordenadas_lng = Decimal('-74.0817')
        mock_finca.fecha_registro = None
        mock_finca.activa = True
        mock_finca.ubicacion_completa = 'Test Municipality, Test Department'
        mock_finca.get_estadisticas.return_value = {
            'total_lotes': 5,
            'lotes_activos': 3,
            'total_analisis': 10,
            'calidad_promedio': 85.5
        }
        mock_finca.created_at = None
        mock_finca.updated_at = None
        
        serializer = FincaSerializer(mock_finca)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('nombre', data)
        self.assertIn('ubicacion', data)
        self.assertIn('municipio', data)
        self.assertIn('departamento', data)
        self.assertIn('hectareas', data)
        self.assertIn('agricultor_name', data)
        self.assertIn('agricultor_email', data)
        self.assertIn('estadisticas', data)
    
    def test_finca_validation_short_name(self):
        """Test finca validation with short name."""
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'AB',
            'municipio': 'Test Municipality',
            'departamento': 'Test Department',
            'hectareas': Decimal('10.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('nombre', serializer.errors)
    
    def test_finca_validation_invalid_hectares_negative(self):
        """Test finca validation with negative hectares."""
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'Test Finca',
            'municipio': 'Test Municipality',
            'departamento': 'Test Department',
            'hectareas': Decimal('-1.0'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('hectareas', serializer.errors)
    
    def test_finca_validation_invalid_hectares_too_high(self):
        """Test finca validation with too high hectares."""
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'Test Finca',
            'municipio': 'Test Municipality',
            'departamento': 'Test Department',
            'hectareas': Decimal('10001.0'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('hectareas', serializer.errors)
    
    def test_finca_validation_missing_municipio(self):
        """Test finca validation without municipio."""
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'Test Finca',
            'departamento': 'Test Department',
            'hectareas': Decimal('10.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_finca_validation_missing_departamento(self):
        """Test finca validation without departamento."""
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'Test Finca',
            'municipio': 'Test Municipality',
            'hectareas': Decimal('10.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    @patch('api.serializers.finca_serializers.validate_latitude')
    def test_finca_validation_invalid_latitude(self, mock_validate_lat):
        """Test finca validation with invalid latitude."""
        mock_validate_lat.side_effect = serializers.ValidationError('Invalid latitude')
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'Test Finca',
            'municipio': 'Test Municipality',
            'departamento': 'Test Department',
            'hectareas': Decimal('10.5'),
            'coordenadas_lat': Decimal('100.0'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('coordenadas_lat', serializer.errors)
    
    @patch('api.serializers.finca_serializers.validate_longitude')
    def test_finca_validation_invalid_longitude(self, mock_validate_lng):
        """Test finca validation with invalid longitude."""
        mock_validate_lng.side_effect = serializers.ValidationError('Invalid longitude')
        mock_request = Mock()
        mock_request.user = self.user
        
        serializer = FincaSerializer(data={
            'nombre': 'Test Finca',
            'municipio': 'Test Municipality',
            'departamento': 'Test Department',
            'hectareas': Decimal('10.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('200.0')
        }, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('coordenadas_lng', serializer.errors)


class FincaListSerializerTest(TestCase):
    """Tests for FincaListSerializer."""
    
    @patch('api.serializers.finca_serializers.Finca')
    def test_finca_list_serialization_success(self, mock_finca_model):
        """Test successful finca list serialization."""
        mock_finca = Mock()
        mock_finca.id = 1
        mock_finca.nombre = 'Test Finca'
        mock_finca.municipio = 'Test Municipality'
        mock_finca.departamento = 'Test Department'
        mock_finca.ubicacion = 'Test Location'
        mock_finca.hectareas = Decimal('10.5')
        mock_finca.activa = True
        mock_finca.fecha_registro = None
        mock_finca.agricultor_id = 1
        mock_finca.coordenadas_lat = Decimal('4.6097')
        mock_finca.coordenadas_lng = Decimal('-74.0817')
        
        serializer = FincaListSerializer(mock_finca)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('nombre', data)
        self.assertIn('municipio', data)
        self.assertIn('departamento', data)
        self.assertIn('ubicacion_completa', data)
        self.assertIn('hectareas', data)
        self.assertIn('activa', data)


class FincaDetailSerializerTest(TestCase):
    """Tests for FincaDetailSerializer."""
    
    @patch('api.serializers.finca_serializers.Finca')
    def test_finca_detail_serialization_success(self, mock_finca_model):
        """Test successful finca detail serialization."""
        mock_finca = Mock()
        mock_finca.id = 1
        mock_finca.nombre = 'Test Finca'
        mock_finca.lotes.all.return_value = []
        
        serializer = FincaDetailSerializer(mock_finca)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('lotes', data)


class FincaStatsSerializerTest(TestCase):
    """Tests for FincaStatsSerializer."""
    
    def test_finca_stats_serialization_success(self):
        """Test successful finca stats serialization."""
        serializer = FincaStatsSerializer(data={
            'total_fincas': 50,
            'fincas_activas': 45,
            'total_hectareas': Decimal('500.0'),
            'promedio_hectareas': Decimal('10.0'),
            'fincas_por_departamento': [{'departamento': 'Cundinamarca', 'count': 30}],
            'fincas_por_municipio': [{'municipio': 'Bogotá', 'count': 20}],
            'calidad_promedio_general': 85.5
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['total_fincas'], 50)
        self.assertEqual(serializer.validated_data['fincas_activas'], 45)


class LoteSerializerTest(TestCase):
    """Tests for LoteSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.finca_serializers.Lote')
    def test_lote_serialization_success(self, mock_lote_model):
        """Test successful lote serialization."""
        mock_finca = Mock()
        mock_finca.nombre = 'Test Finca'
        mock_finca.ubicacion_completa = 'Test Location'
        mock_finca.agricultor.get_full_name.return_value = 'Test User'
        
        mock_lote = Mock()
        mock_lote.id = 1
        mock_lote.finca = mock_finca
        mock_lote.identificador = 'LOTE-001'
        mock_lote.variedad = 'Criollo'
        mock_lote.fecha_plantacion = None
        mock_lote.fecha_cosecha = None
        mock_lote.area_hectareas = Decimal('2.5')
        mock_lote.estado = 'activo'
        mock_lote.descripcion = 'Test description'
        mock_lote.coordenadas_lat = Decimal('4.6097')
        mock_lote.coordenadas_lng = Decimal('-74.0817')
        mock_lote.fecha_registro = None
        mock_lote.activo = True
        mock_lote.ubicacion_completa = 'Test Location'
        mock_lote.get_estadisticas.return_value = {
            'total_analisis': 5,
            'calidad_promedio': 80.0
        }
        mock_lote.edad_meses = 24
        mock_lote.created_at = None
        mock_lote.updated_at = None
        
        serializer = LoteSerializer(mock_lote)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('identificador', data)
        self.assertIn('variedad', data)
        self.assertIn('finca_nombre', data)
        self.assertIn('estadisticas', data)
        self.assertIn('edad_meses', data)
    
    def test_lote_validation_short_identificador(self):
        """Test lote validation with short identificador."""
        serializer = LoteSerializer(data={
            'identificador': 'A',
            'variedad': 'Criollo',
            'area_hectareas': Decimal('2.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'finca': Mock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('identificador', serializer.errors)
    
    def test_lote_validation_invalid_area_negative(self):
        """Test lote validation with negative area."""
        serializer = LoteSerializer(data={
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'area_hectareas': Decimal('-1.0'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'finca': Mock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('area_hectareas', serializer.errors)
    
    def test_lote_validation_invalid_area_too_high(self):
        """Test lote validation with too high area."""
        serializer = LoteSerializer(data={
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'area_hectareas': Decimal('1001.0'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'finca': Mock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('area_hectareas', serializer.errors)
    
    def test_lote_validation_invalid_harvest_date(self):
        """Test lote validation with harvest date before planting date."""
        from datetime import date
        
        serializer = LoteSerializer(data={
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'fecha_plantacion': date(2024, 1, 1),
            'fecha_cosecha': date(2023, 12, 31),
            'area_hectareas': Decimal('2.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'finca': Mock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_cosecha', serializer.errors)
    
    def test_lote_validation_missing_variedad(self):
        """Test lote validation without variedad."""
        serializer = LoteSerializer(data={
            'identificador': 'LOTE-001',
            'area_hectareas': Decimal('2.5'),
            'coordenadas_lat': Decimal('4.6097'),
            'coordenadas_lng': Decimal('-74.0817')
        }, context={'finca': Mock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class LoteListSerializerTest(TestCase):
    """Tests for LoteListSerializer."""
    
    @patch('api.serializers.finca_serializers.Lote')
    def test_lote_list_serialization_success(self, mock_lote_model):
        """Test successful lote list serialization."""
        mock_finca = Mock()
        mock_finca.nombre = 'Test Finca'
        mock_finca.agricultor.get_full_name.return_value = 'Test User'
        
        mock_lote = Mock()
        mock_lote.id = 1
        mock_lote.identificador = 'LOTE-001'
        mock_lote.variedad = 'Criollo'
        mock_lote.finca = mock_finca
        mock_lote.area_hectareas = Decimal('2.5')
        mock_lote.estado = 'activo'
        mock_lote.total_analisis = 5
        mock_lote.analisis_procesados = 3
        mock_lote.edad_meses = 24
        mock_lote.activo = True
        mock_lote.fecha_plantacion = None
        mock_lote.fecha_cosecha = None
        mock_lote.ubicacion_completa = 'Test Location'
        
        serializer = LoteListSerializer(mock_lote)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('identificador', data)
        self.assertIn('variedad', data)
        self.assertIn('finca_nombre', data)
        self.assertIn('agricultor_nombre', data)


class LoteDetailSerializerTest(TestCase):
    """Tests for LoteDetailSerializer."""
    
    @patch('api.serializers.finca_serializers.Lote')
    def test_lote_detail_serialization_success(self, mock_lote_model):
        """Test successful lote detail serialization."""
        mock_lote = Mock()
        mock_lote.id = 1
        mock_lote.cacao_images.all.return_value = []
        
        serializer = LoteDetailSerializer(mock_lote)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('cacao_images', data)


class LoteStatsSerializerTest(TestCase):
    """Tests for LoteStatsSerializer."""
    
    def test_lote_stats_serialization_success(self):
        """Test successful lote stats serialization."""
        serializer = LoteStatsSerializer(data={
            'total_lotes': 100,
            'lotes_activos': 80,
            'lotes_por_estado': {'activo': 80, 'inactivo': 20},
            'total_area_hectareas': Decimal('200.0'),
            'promedio_area_hectareas': Decimal('2.0'),
            'variedades_mas_comunes': [{'variedad': 'Criollo', 'count': 50}],
            'calidad_promedio_general': 82.5
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['total_lotes'], 100)
        self.assertEqual(serializer.validated_data['lotes_activos'], 80)

