"""
Unit tests for API utils ml_helpers module.
Tests ML helper functions for predictions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from api.utils.ml_helpers import (
    get_predictor,
    load_image_for_prediction,
    create_prediction_from_result
)


@pytest.fixture
def mock_ml_service():
    """Create a mock MLService for testing."""
    service = Mock()
    result = Mock()
    result.success = True
    result.data = Mock()
    result.data.models_loaded = True
    result.error = None
    service.get_predictor.return_value = result
    return service


@pytest.fixture
def mock_cacao_image():
    """Create a mock CacaoImage for testing."""
    image = Mock()
    image.image.path = "/path/to/image.jpg"
    return image


class TestGetPredictor:
    """Tests for get_predictor function."""
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_success(self, mock_ml_service_class, mock_ml_service):
        """Test successful predictor retrieval."""
        mock_ml_service_class.return_value = mock_ml_service
        
        predictor, error = get_predictor()
        
        assert predictor is not None
        assert error is None
        assert predictor.models_loaded is True
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_service_failure(self, mock_ml_service_class):
        """Test predictor retrieval when service fails."""
        service = Mock()
        result = Mock()
        result.success = False
        result.error = Mock()
        result.error.message = "Service error"
        service.get_predictor.return_value = result
        mock_ml_service_class.return_value = service
        
        predictor, error = get_predictor()
        
        assert predictor is None
        assert error is not None
        assert error['status'] == 'error'
        assert "Service error" in error['error']
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_models_not_loaded(self, mock_ml_service_class):
        """Test predictor retrieval when models are not loaded."""
        service = Mock()
        result = Mock()
        result.success = True
        result.data = Mock()
        result.data.models_loaded = False
        service.get_predictor.return_value = result
        mock_ml_service_class.return_value = service
        
        predictor, error = get_predictor()
        
        assert predictor is None
        assert error is not None
        assert error['status'] == 'error'
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_exception(self, mock_ml_service_class):
        """Test predictor retrieval when exception occurs."""
        mock_ml_service_class.side_effect = Exception("Unexpected error")
        
        predictor, error = get_predictor()
        
        assert predictor is None
        assert error is not None
        assert error['status'] == 'error'


class TestLoadImageForPrediction:
    """Tests for load_image_for_prediction function."""
    
    def test_load_image_from_file_object(self, mock_cacao_image):
        """Test loading image from file object."""
        img = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        result = load_image_for_prediction(img_bytes, mock_cacao_image)
        
        assert isinstance(result, Image.Image)
        assert result.size == (224, 224)
    
    @patch('api.utils.ml_helpers.Image')
    def test_load_image_from_path(self, mock_image, mock_cacao_image):
        """Test loading image from file path."""
        mock_file = Mock()
        mock_file.seek.side_effect = AttributeError()
        mock_image.open.return_value = Mock(spec=Image.Image)
        
        result = load_image_for_prediction(mock_file, mock_cacao_image)
        
        mock_image.open.assert_called_once_with(mock_cacao_image.image.path)
    
    def test_load_image_handles_io_error(self, mock_cacao_image):
        """Test that IO errors are handled gracefully."""
        invalid_file = Mock()
        invalid_file.seek = Mock(side_effect=IOError())
        invalid_file.read = Mock(side_effect=IOError())
        
        with patch('api.utils.ml_helpers.Image') as mock_image:
            mock_image.open.return_value = Mock(spec=Image.Image)
            result = load_image_for_prediction(invalid_file, mock_cacao_image)
            
            assert result is not None


class TestCreatePredictionFromResult:
    """Tests for create_prediction_from_result function."""
    
    @patch('api.utils.ml_helpers.CacaoPrediction')
    def test_create_prediction_basic(self, mock_prediction_class, mock_cacao_image):
        """Test creating prediction from result."""
        result = {
            'alto_mm': 10.5,
            'ancho_mm': 8.3,
            'grosor_mm': 5.2,
            'peso_g': 12.4,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'debug': {
                'device': 'cpu'
            }
        }
        
        mock_prediction = Mock()
        mock_prediction_class.return_value = mock_prediction
        
        prediction = create_prediction_from_result(mock_cacao_image, result, 100)
        
        assert prediction is not None
        mock_prediction_class.assert_called_once()
        mock_prediction.save.assert_called_once()
    
    @patch('api.utils.ml_helpers.CacaoPrediction')
    def test_create_prediction_with_gpu(self, mock_prediction_class, mock_cacao_image):
        """Test creating prediction with GPU device."""
        result = {
            'alto_mm': 10.5,
            'ancho_mm': 8.3,
            'grosor_mm': 5.2,
            'peso_g': 12.4,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'debug': {
                'device': 'cuda:0'
            }
        }
        
        mock_prediction = Mock()
        mock_prediction_class.return_value = mock_prediction
        
        prediction = create_prediction_from_result(mock_cacao_image, result, 100)
        
        assert prediction is not None
        # Verify device_used is extracted correctly
        call_kwargs = mock_prediction_class.call_args[1]
        assert call_kwargs['device_used'] == 'cuda'

