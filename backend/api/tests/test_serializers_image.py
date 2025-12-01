"""
Unit tests for image serializers (image_serializers.py).
Tests all serializers: ConfidenceSerializer, DebugInfoSerializer, ScanMeasureResponseSerializer,
CacaoImageSerializer, CacaoPredictionSerializer, CacaoImageDetailSerializer,
ImagesListResponseSerializer, ImagesStatsResponseSerializer.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

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
    TEST_USER_PASSWORD
)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD
    )


@pytest.fixture
def mock_cacao_image(test_user):
    """Create a mock cacao image object."""
    image = Mock()
    image.id = 1
    image.user = test_user
    image.image = Mock()
    image.image.url = '/media/cacao_images/test.jpg'
    image.uploaded_at = timezone.now()
    image.processed = True
    image.finca = None
    image.region = 'Test Region'
    image.lote_id = None
    image.variedad = 'Criollo'
    image.fecha_cosecha = date(2023, 1, 1)
    image.notas = 'Test notes'
    image.file_name = 'test.jpg'
    image.file_size = 1024000
    image.file_type = 'image/jpeg'
    image.created_at = timezone.now()
    image.updated_at = timezone.now()
    image.file_size_mb = 1.0
    image.has_prediction = True
    image.get_full_name = Mock(return_value='Test User')
    return image


@pytest.fixture
def mock_cacao_prediction(mock_cacao_image):
    """Create a mock cacao prediction object."""
    prediction = Mock()
    prediction.id = 1
    prediction.image = mock_cacao_image
    prediction.alto_mm = 15.5
    prediction.ancho_mm = 12.3
    prediction.grosor_mm = 8.7
    prediction.peso_g = 2.5
    prediction.confidence_alto = 0.95
    prediction.confidence_ancho = 0.92
    prediction.confidence_grosor = 0.88
    prediction.confidence_peso = 0.90
    prediction.average_confidence = 0.91
    prediction.processing_time_ms = 150
    prediction.crop_url = '/media/crops/test_crop.jpg'
    prediction.model_version = '1.0.0'
    prediction.device_used = 'CPU'
    prediction.volume_cm3 = 1650.0
    prediction.density_g_cm3 = 1.52
    prediction.created_at = timezone.now()
    return prediction


class TestConfidenceSerializer:
    """Tests for ConfidenceSerializer."""
    
    def test_serialize_confidence(self):
        """Test serialization of confidence data."""
        data = {
            'alto': 0.95,
            'ancho': 0.92,
            'grosor': 0.88,
            'peso': 0.90
        }
        serializer = ConfidenceSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['alto'] == 0.95
        assert serializer.validated_data['ancho'] == 0.92


class TestDebugInfoSerializer:
    """Tests for DebugInfoSerializer."""
    
    def test_serialize_debug_info(self):
        """Test serialization of debug info."""
        data = {
            'segmented': True,
            'yolo_conf': 0.95,
            'latency_ms': 150,
            'models_version': '1.0.0',
            'device': 'CPU',
            'total_time_s': 0.5
        }
        serializer = DebugInfoSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['segmented'] is True
        assert serializer.validated_data['yolo_conf'] == 0.95
    
    def test_serialize_debug_info_optional_fields(self):
        """Test serialization with optional fields."""
        data = {
            'segmented': True,
            'yolo_conf': 0.95,
            'latency_ms': 150,
            'models_version': '1.0.0'
        }
        serializer = DebugInfoSerializer(data=data)
        assert serializer.is_valid()


class TestScanMeasureResponseSerializer:
    """Tests for ScanMeasureResponseSerializer."""
    
    def test_serialize_scan_measure_response(self):
        """Test serialization of scan measure response."""
        data = {
            'alto_mm': 15.5,
            'ancho_mm': 12.3,
            'grosor_mm': 8.7,
            'peso_g': 2.5,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'crop_url': 'http://example.com/crop.jpg',
            'debug': {
                'segmented': True,
                'yolo_conf': 0.95,
                'latency_ms': 150,
                'models_version': '1.0.0'
            },
            'image_id': 1,
            'prediction_id': 1,
            'saved_to_database': True
        }
        serializer = ScanMeasureResponseSerializer(data=data)
        assert serializer.is_valid()


class TestCacaoImageSerializer:
    """Tests for CacaoImageSerializer."""
    
    def test_serialize_cacao_image(self, mock_cacao_image):
        """Test serialization of cacao image."""
        serializer = CacaoImageSerializer(mock_cacao_image)
        data = serializer.data
        
        assert data['id'] == 1
        assert 'user_name' in data
        assert 'file_size_mb' in data
        assert 'has_prediction' in data
    
    def test_validate_fecha_cosecha_valid(self):
        """Test successful fecha_cosecha validation."""
        serializer = CacaoImageSerializer()
        value = serializer.validate_fecha_cosecha(date(2023, 1, 1))
        assert value == date(2023, 1, 1)
    
    def test_validate_fecha_cosecha_before_1900(self):
        """Test validation error when fecha_cosecha is before 1900."""
        serializer = CacaoImageSerializer()
        with pytest.raises(Exception):
            serializer.validate_fecha_cosecha(date(1899, 1, 1))


class TestCacaoPredictionSerializer:
    """Tests for CacaoPredictionSerializer."""
    
    def test_serialize_cacao_prediction(self, mock_cacao_prediction):
        """Test serialization of cacao prediction."""
        serializer = CacaoPredictionSerializer(mock_cacao_prediction)
        data = serializer.data
        
        assert data['id'] == 1
        assert data['alto_mm'] == 15.5
        assert data['ancho_mm'] == 12.3
        assert 'average_confidence' in data
        assert 'volume_cm3' in data
        assert 'density_g_cm3' in data
        assert 'image_url' in data
    
    def test_get_image_url_with_request(self, mock_cacao_prediction):
        """Test get_image_url with request in context."""
        mock_request = Mock()
        mock_request.build_absolute_uri = Mock(return_value='http://example.com/media/cacao_images/test.jpg')
        
        serializer = CacaoPredictionSerializer(mock_cacao_prediction, context={'request': mock_request})
        image_url = serializer.get_image_url(mock_cacao_prediction)
        assert image_url == 'http://example.com/media/cacao_images/test.jpg'
    
    def test_get_image_url_no_request(self, mock_cacao_prediction):
        """Test get_image_url without request in context."""
        serializer = CacaoPredictionSerializer(mock_cacao_prediction)
        image_url = serializer.get_image_url(mock_cacao_prediction)
        assert image_url == '/media/cacao_images/test.jpg'
    
    def test_get_image_url_no_image(self, mock_cacao_prediction):
        """Test get_image_url when image is None."""
        mock_cacao_prediction.image = None
        serializer = CacaoPredictionSerializer(mock_cacao_prediction)
        image_url = serializer.get_image_url(mock_cacao_prediction)
        assert image_url is None
    
    def test_validate_alto_mm_valid(self):
        """Test successful alto_mm validation."""
        serializer = CacaoPredictionSerializer()
        value = serializer.validate_alto_mm(50.0)
        assert value == 50.0
    
    def test_validate_alto_mm_zero(self):
        """Test validation error when alto_mm is zero."""
        serializer = CacaoPredictionSerializer()
        with pytest.raises(Exception):
            serializer.validate_alto_mm(0)
    
    def test_validate_alto_mm_too_high(self):
        """Test validation error when alto_mm > 100."""
        serializer = CacaoPredictionSerializer()
        with pytest.raises(Exception):
            serializer.validate_alto_mm(101)
    
    def test_validate_ancho_mm_valid(self):
        """Test successful ancho_mm validation."""
        serializer = CacaoPredictionSerializer()
        value = serializer.validate_ancho_mm(50.0)
        assert value == 50.0
    
    def test_validate_ancho_mm_too_high(self):
        """Test validation error when ancho_mm > 100."""
        serializer = CacaoPredictionSerializer()
        with pytest.raises(Exception):
            serializer.validate_ancho_mm(101)
    
    def test_validate_grosor_mm_valid(self):
        """Test successful grosor_mm validation."""
        serializer = CacaoPredictionSerializer()
        value = serializer.validate_grosor_mm(25.0)
        assert value == 25.0
    
    def test_validate_grosor_mm_too_high(self):
        """Test validation error when grosor_mm > 50."""
        serializer = CacaoPredictionSerializer()
        with pytest.raises(Exception):
            serializer.validate_grosor_mm(51)
    
    def test_validate_peso_g_valid(self):
        """Test successful peso_g validation."""
        serializer = CacaoPredictionSerializer()
        value = serializer.validate_peso_g(5.0)
        assert value == 5.0
    
    def test_validate_peso_g_too_high(self):
        """Test validation error when peso_g > 10."""
        serializer = CacaoPredictionSerializer()
        with pytest.raises(Exception):
            serializer.validate_peso_g(11)


class TestCacaoImageDetailSerializer:
    """Tests for CacaoImageDetailSerializer."""
    
    def test_serialize_cacao_image_detail(self, mock_cacao_image, mock_cacao_prediction):
        """Test serialization of cacao image detail with prediction."""
        mock_cacao_image.prediction = mock_cacao_prediction
        serializer = CacaoImageDetailSerializer(mock_cacao_image)
        data = serializer.data
        
        assert 'prediction' in data
        assert data['prediction']['id'] == 1


class TestImagesListResponseSerializer:
    """Tests for ImagesListResponseSerializer."""
    
    def test_serialize_images_list_response(self):
        """Test serialization of images list response."""
        data = {
            'results': [
                {'id': 1, 'image': '/media/test1.jpg'},
                {'id': 2, 'image': '/media/test2.jpg'}
            ],
            'count': 2,
            'page': 1,
            'page_size': 10,
            'total_pages': 1,
            'next': None,
            'previous': None
        }
        serializer = ImagesListResponseSerializer(data=data)
        assert serializer.is_valid()


class TestImagesStatsResponseSerializer:
    """Tests for ImagesStatsResponseSerializer."""
    
    def test_serialize_images_stats_response(self):
        """Test serialization of images statistics response."""
        data = {
            'total_images': 100,
            'processed_images': 80,
            'unprocessed_images': 20,
            'processed_today': 10,
            'processed_this_week': 30,
            'processed_this_month': 50,
            'average_confidence': 0.85,
            'average_processing_time_ms': 150.5,
            'region_stats': [{'region': 'Test', 'count': 50}],
            'top_fincas': [{'finca': 'Test Finca', 'count': 20}],
            'average_dimensions': {'alto': 15.0, 'ancho': 12.0, 'grosor': 8.0}
        }
        serializer = ImagesStatsResponseSerializer(data=data)
        assert serializer.is_valid()

