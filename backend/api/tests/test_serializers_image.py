"""
Unit tests for image serializers.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

from rest_framework import serializers
from api.serializers.image_serializers import (
    ConfidenceSerializer,
    DebugInfoSerializer,
    ScanMeasureResponseSerializer,
    CacaoImageSerializer,
    CacaoPredictionSerializer,
    CacaoImageDetailSerializer,
    ImagesListResponseSerializer,
    ImagesStatsResponseSerializer
)
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


class ConfidenceSerializerTest(TestCase):
    """Tests for ConfidenceSerializer."""
    
    def test_confidence_serialization_success(self):
        """Test successful confidence serialization."""
        serializer = ConfidenceSerializer(data={
            'alto': 0.95,
            'ancho': 0.92,
            'grosor': 0.88,
            'peso': 0.90
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['alto'], 0.95)
        self.assertEqual(serializer.validated_data['ancho'], 0.92)
    
    def test_confidence_missing_fields(self):
        """Test confidence with missing fields."""
        serializer = ConfidenceSerializer(data={
            'alto': 0.95
        })
        self.assertFalse(serializer.is_valid())


class DebugInfoSerializerTest(TestCase):
    """Tests for DebugInfoSerializer."""
    
    def test_debug_info_serialization_success(self):
        """Test successful debug info serialization."""
        serializer = DebugInfoSerializer(data={
            'segmented': True,
            'yolo_conf': 0.85,
            'latency_ms': 150,
            'models_version': '1.0.0',
            'device': 'cpu',
            'total_time_s': 0.5
        })
        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.validated_data['segmented'])
        self.assertEqual(serializer.validated_data['yolo_conf'], 0.85)
    
    def test_debug_info_optional_fields(self):
        """Test debug info with optional fields."""
        serializer = DebugInfoSerializer(data={
            'segmented': True,
            'yolo_conf': 0.85,
            'latency_ms': 150,
            'models_version': '1.0.0'
        })
        self.assertTrue(serializer.is_valid())


class ScanMeasureResponseSerializerTest(TestCase):
    """Tests for ScanMeasureResponseSerializer."""
    
    def test_scan_measure_response_serialization_success(self):
        """Test successful scan measure response serialization."""
        serializer = ScanMeasureResponseSerializer(data={
            'alto_mm': 25.5,
            'ancho_mm': 18.3,
            'grosor_mm': 12.1,
            'peso_g': 1.2,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'crop_url': 'http://example.com/crop.jpg',
            'debug': {
                'segmented': True,
                'yolo_conf': 0.85,
                'latency_ms': 150,
                'models_version': '1.0.0'
            },
            'image_id': 1,
            'prediction_id': 1,
            'saved_to_database': True
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['alto_mm'], 25.5)
        self.assertIn('confidences', serializer.validated_data)
        self.assertIn('debug', serializer.validated_data)
    
    def test_scan_measure_response_optional_fields(self):
        """Test scan measure response with optional fields."""
        serializer = ScanMeasureResponseSerializer(data={
            'alto_mm': 25.5,
            'ancho_mm': 18.3,
            'grosor_mm': 12.1,
            'peso_g': 1.2,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'crop_url': 'http://example.com/crop.jpg',
            'debug': {
                'segmented': True,
                'yolo_conf': 0.85,
                'latency_ms': 150,
                'models_version': '1.0.0'
            }
        })
        self.assertTrue(serializer.is_valid())


class CacaoImageSerializerTest(TestCase):
    """Tests for CacaoImageSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.image_serializers.CacaoImage')
    def test_cacao_image_serialization_success(self, mock_image_model):
        """Test successful cacao image serialization."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.user = self.user
        mock_image.user.get_full_name.return_value = 'Test User'
        mock_image.image = SimpleUploadedFile('test.jpg', b'fake content')
        mock_image.uploaded_at = None
        mock_image.processed = True
        mock_image.finca = None
        mock_image.region = 'Test Region'
        mock_image.lote_id = None
        mock_image.variedad = 'Criollo'
        mock_image.fecha_cosecha = None
        mock_image.notas = 'Test notes'
        mock_image.file_name = 'test.jpg'
        mock_image.file_size = 1024
        mock_image.file_size_mb = 0.001
        mock_image.file_type = 'image/jpeg'
        mock_image.has_prediction = True
        mock_image.created_at = None
        mock_image.updated_at = None
        
        serializer = CacaoImageSerializer(mock_image)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('user_name', data)
        self.assertIn('image', data)
        self.assertIn('file_size_mb', data)
        self.assertIn('has_prediction', data)
    
    def test_cacao_image_validation_invalid_harvest_date(self):
        """Test cacao image validation with invalid harvest date."""
        serializer = CacaoImageSerializer(data={
            'fecha_cosecha': date(1899, 1, 1)
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_cosecha', serializer.errors)
    
    def test_cacao_image_validation_valid_harvest_date(self):
        """Test cacao image validation with valid harvest date."""
        serializer = CacaoImageSerializer(data={
            'fecha_cosecha': date(2024, 1, 1)
        })
        # fecha_cosecha is optional, so this should be valid
        self.assertTrue(serializer.is_valid() or 'fecha_cosecha' not in serializer.errors)


class CacaoPredictionSerializerTest(TestCase):
    """Tests for CacaoPredictionSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.image_serializers.CacaoPrediction')
    def test_cacao_prediction_serialization_success(self, mock_prediction_model):
        """Test successful cacao prediction serialization."""
        mock_image = Mock()
        mock_image.image = SimpleUploadedFile('test.jpg', b'fake content')
        
        mock_prediction = Mock()
        mock_prediction.id = 1
        mock_prediction.image = mock_image
        mock_prediction.alto_mm = 25.5
        mock_prediction.ancho_mm = 18.3
        mock_prediction.grosor_mm = 12.1
        mock_prediction.peso_g = 1.2
        mock_prediction.confidence_alto = 0.95
        mock_prediction.confidence_ancho = 0.92
        mock_prediction.confidence_grosor = 0.88
        mock_prediction.confidence_peso = 0.90
        mock_prediction.average_confidence = 0.91
        mock_prediction.processing_time_ms = 150
        mock_prediction.crop_url = 'http://example.com/crop.jpg'
        mock_prediction.model_version = '1.0.0'
        mock_prediction.device_used = 'cpu'
        mock_prediction.volume_cm3 = 5.6
        mock_prediction.density_g_cm3 = 0.21
        mock_prediction.created_at = None
        
        mock_request = Mock()
        mock_request.build_absolute_uri.return_value = 'http://example.com/test.jpg'
        
        serializer = CacaoPredictionSerializer(
            mock_prediction,
            context={'request': mock_request}
        )
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('alto_mm', data)
        self.assertIn('ancho_mm', data)
        self.assertIn('grosor_mm', data)
        self.assertIn('peso_g', data)
        self.assertIn('average_confidence', data)
        self.assertIn('image_url', data)
    
    def test_cacao_prediction_validation_invalid_alto(self):
        """Test cacao prediction validation with invalid height."""
        serializer = CacaoPredictionSerializer(data={
            'alto_mm': -1.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('alto_mm', serializer.errors)
    
    def test_cacao_prediction_validation_alto_too_high(self):
        """Test cacao prediction validation with height too high."""
        serializer = CacaoPredictionSerializer(data={
            'alto_mm': 101.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('alto_mm', serializer.errors)
    
    def test_cacao_prediction_validation_invalid_ancho(self):
        """Test cacao prediction validation with invalid width."""
        serializer = CacaoPredictionSerializer(data={
            'ancho_mm': -1.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('ancho_mm', serializer.errors)
    
    def test_cacao_prediction_validation_ancho_too_high(self):
        """Test cacao prediction validation with width too high."""
        serializer = CacaoPredictionSerializer(data={
            'ancho_mm': 101.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('ancho_mm', serializer.errors)
    
    def test_cacao_prediction_validation_invalid_grosor(self):
        """Test cacao prediction validation with invalid thickness."""
        serializer = CacaoPredictionSerializer(data={
            'grosor_mm': -1.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('grosor_mm', serializer.errors)
    
    def test_cacao_prediction_validation_grosor_too_high(self):
        """Test cacao prediction validation with thickness too high."""
        serializer = CacaoPredictionSerializer(data={
            'grosor_mm': 51.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('grosor_mm', serializer.errors)
    
    def test_cacao_prediction_validation_invalid_peso(self):
        """Test cacao prediction validation with invalid weight."""
        serializer = CacaoPredictionSerializer(data={
            'peso_g': -1.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('peso_g', serializer.errors)
    
    def test_cacao_prediction_validation_peso_too_high(self):
        """Test cacao prediction validation with weight too high."""
        serializer = CacaoPredictionSerializer(data={
            'peso_g': 11.0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('peso_g', serializer.errors)


class CacaoImageDetailSerializerTest(TestCase):
    """Tests for CacaoImageDetailSerializer."""
    
    @patch('api.serializers.image_serializers.CacaoImage')
    def test_cacao_image_detail_serialization_success(self, mock_image_model):
        """Test successful cacao image detail serialization."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.prediction = None
        
        serializer = CacaoImageDetailSerializer(mock_image)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('prediction', data)


class ImagesListResponseSerializerTest(TestCase):
    """Tests for ImagesListResponseSerializer."""
    
    def test_images_list_response_serialization_success(self):
        """Test successful images list response serialization."""
        serializer = ImagesListResponseSerializer(data={
            'results': [],
            'count': 0,
            'page': 1,
            'page_size': 20,
            'total_pages': 0,
            'next': None,
            'previous': None
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['count'], 0)
        self.assertEqual(serializer.validated_data['page'], 1)
    
    def test_images_list_response_with_results(self):
        """Test images list response with results."""
        mock_image = Mock()
        mock_image.id = 1
        
        serializer = ImagesListResponseSerializer(data={
            'results': [{'id': 1}],
            'count': 1,
            'page': 1,
            'page_size': 20,
            'total_pages': 1,
            'next': None,
            'previous': None
        })
        self.assertTrue(serializer.is_valid())


class ImagesStatsResponseSerializerTest(TestCase):
    """Tests for ImagesStatsResponseSerializer."""
    
    def test_images_stats_response_serialization_success(self):
        """Test successful images stats response serialization."""
        serializer = ImagesStatsResponseSerializer(data={
            'total_images': 100,
            'processed_images': 80,
            'unprocessed_images': 20,
            'processed_today': 5,
            'processed_this_week': 15,
            'processed_this_month': 50,
            'average_confidence': 0.85,
            'average_processing_time_ms': 150.5,
            'region_stats': [{'region': 'Test', 'count': 30}],
            'top_fincas': [{'finca': 'Test Finca', 'count': 20}],
            'average_dimensions': {'alto': 25.0, 'ancho': 18.0}
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['total_images'], 100)
        self.assertEqual(serializer.validated_data['processed_images'], 80)
        self.assertIn('region_stats', serializer.validated_data)
        self.assertIn('average_dimensions', serializer.validated_data)

