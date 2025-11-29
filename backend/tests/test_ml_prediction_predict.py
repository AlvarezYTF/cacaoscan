"""
Unit tests for ML prediction module (predict.py).
Tests critical prediction functionality including model loading, preprocessing, and prediction.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from ml.prediction.predict import (
    CacaoPredictor,
    PredictionError,
    ModelNotLoadedError,
    InvalidImageError,
    get_predictor,
    load_artifacts,
    predict_image,
    predict_image_bytes
)
from ml.prediction.predict import PredictionConfig
from ml.segmentation.processor import SegmentationError


@pytest.fixture
def mock_image():
    """Create a mock PIL Image for testing."""
    return Image.new('RGB', (224, 224), color='red')


@pytest.fixture
def mock_crop_image():
    """Create a mock RGBA crop image."""
    return Image.new('RGBA', (200, 200), color=(255, 0, 0, 255))


@pytest.fixture
def predictor_config():
    """Create a test prediction configuration."""
    return PredictionConfig(
        IMAGE_SIZE=(224, 224),
        TARGET_LIMITS={
            'alto': (5.0, 60.0),
            'ancho': (3.0, 30.0),
            'grosor': (1.0, 20.0),
            'peso': (0.2, 10.0)
        }
    )


@pytest.fixture
def predictor(predictor_config):
    """Create a CacaoPredictor instance for testing."""
    with patch('ml.prediction.predict.get_regressors_artifacts_dir'), \
         patch('ml.prediction.predict.get_datasets_dir'), \
         patch('ml.prediction.predict.ensure_dir_exists'), \
         patch('ml.prediction.predict.load_json'):
        predictor = CacaoPredictor(config=predictor_config)
        predictor.models_loaded = False
        return predictor


class TestPredictionConfig:
    """Tests for PredictionConfig dataclass."""
    
    def test_config_defaults(self):
        """Test that config has correct default values."""
        config = PredictionConfig()
        
        assert config.IMAGE_SIZE == (224, 224)
        assert config.IMAGENET_MEAN == [0.485, 0.456, 0.406]
        assert config.IMAGENET_STD == [0.229, 0.224, 0.225]
        assert config.MIN_CROP_SIZE == 50
        assert config.MIN_VISIBLE_RATIO == 0.2
        assert 'alto' in config.TARGET_LIMITS
        assert 'ancho' in config.TARGET_LIMITS
        assert 'grosor' in config.TARGET_LIMITS
        assert 'peso' in config.TARGET_LIMITS
    
    def test_config_custom_values(self):
        """Test config with custom values."""
        custom_limits = {
            'alto': (10.0, 50.0),
            'ancho': (5.0, 25.0),
            'grosor': (2.0, 15.0),
            'peso': (0.5, 8.0)
        }
        config = PredictionConfig(TARGET_LIMITS=custom_limits)
        
        assert config.TARGET_LIMITS == custom_limits


class TestCacaoPredictor:
    """Tests for CacaoPredictor class."""
    
    def test_predictor_initialization(self, predictor_config):
        """Test predictor initialization."""
        with patch('ml.prediction.predict.get_regressors_artifacts_dir'), \
             patch('ml.prediction.predict.get_datasets_dir'), \
             patch('ml.prediction.predict.ensure_dir_exists'), \
             patch('ml.prediction.predict.load_json'), \
             patch('ml.prediction.predict.MEDIA_ROOT', Path('/tmp')):
            
            predictor = CacaoPredictor(config=predictor_config)
            
            assert predictor.config == predictor_config
            assert predictor.confidence_threshold == 0.5
            assert predictor.models_loaded is False
            assert predictor.regression_model is None
            assert predictor.scalers is None
    
    def test_get_device_cpu(self, predictor):
        """Test device detection when GPU is not available."""
        with patch('torch.cuda.is_available', return_value=False):
            device = predictor._get_device()
            assert device.type == 'cpu'
    
    def test_get_device_gpu(self, predictor):
        """Test device detection when GPU is available."""
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.get_device_name', return_value='Test GPU'):
            device = predictor._get_device()
            assert device.type == 'cuda'
    
    def test_preprocess_image(self, predictor, mock_image):
        """Test image preprocessing."""
        predictor.device = torch.device('cpu')
        
        tensor = predictor._preprocess_image(mock_image)
        
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape[0] == 1  # Batch dimension
        assert tensor.shape[1] == 3  # RGB channels
        assert tensor.shape[2] == 224  # Height
        assert tensor.shape[3] == 224  # Width
    
    def test_preprocess_image_converts_to_rgb(self, predictor):
        """Test that non-RGB images are converted to RGB."""
        predictor.device = torch.device('cpu')
        gray_image = Image.new('L', (224, 224))
        
        tensor = predictor._preprocess_image(gray_image)
        
        assert tensor.shape[1] == 3  # Should be RGB
    
    def test_denormalize_predictions(self, predictor):
        """Test prediction denormalization."""
        mock_scalers = Mock()
        mock_scalers.inverse_transform = Mock(return_value={
            'alto': np.array([25.0]),
            'ancho': np.array([15.0]),
            'grosor': np.array([8.0]),
            'peso': np.array([1.5])
        })
        predictor.scalers = mock_scalers
        
        normalized = {
            'alto': 0.5,
            'ancho': 0.5,
            'grosor': 0.5,
            'peso': 0.5
        }
        
        result = predictor._denormalize_predictions(normalized)
        
        assert 'alto' in result
        assert 'ancho' in result
        assert 'grosor' in result
        assert 'peso' in result
        assert isinstance(result['alto'], float)
    
    def test_denormalize_predictions_no_scalers(self, predictor):
        """Test that denormalization raises error when scalers are not available."""
        predictor.scalers = None
        
        with pytest.raises(ValueError, match="No hay escaladores disponibles"):
            predictor._denormalize_predictions({'alto': 0.5})
    
    def test_calculate_pixel_to_mm_scale_factor_with_calibration(self, predictor):
        """Test scale factor calculation with calibration data."""
        predictor.pixel_calibration = {
            'calibration_records': [
                {
                    'pixel_measurements': {'width_pixels': 100, 'height_pixels': 150},
                    'scale_factors': {'average_mm_per_pixel': 0.035}
                }
            ],
            'statistics': {
                'scale_factors': {'mean': 0.035}
            }
        }
        
        scale_factor = predictor._calculate_pixel_to_mm_scale_factor(100, 150)
        
        assert scale_factor > 0
        assert isinstance(scale_factor, float)
    
    def test_calculate_pixel_to_mm_scale_factor_default(self, predictor):
        """Test scale factor calculation with default value."""
        predictor.pixel_calibration = None
        
        scale_factor = predictor._calculate_pixel_to_mm_scale_factor(100, 150)
        
        assert scale_factor == 0.035  # Default value
    
    def test_extract_crop_characteristics(self, predictor, mock_crop_image):
        """Test extraction of crop characteristics."""
        predictor.pixel_calibration = None
        
        features = predictor._extract_crop_characteristics(mock_crop_image)
        
        assert 'pixel_width' in features
        assert 'pixel_height' in features
        assert 'pixel_area' in features
        assert 'scale_factor' in features
        assert 'aspect_ratio' in features
        assert all(isinstance(v, float) for v in features.values())
    
    def test_predict_requires_loaded_models(self, predictor, mock_image):
        """Test that predict raises error when models are not loaded."""
        predictor.models_loaded = False
        
        with pytest.raises(ModelNotLoadedError):
            predictor.predict(mock_image)
    
    def test_predict_segmentation_error(self, predictor, mock_image):
        """Test that segmentation errors are properly handled."""
        predictor.models_loaded = True
        predictor._segment_and_crop = Mock(side_effect=SegmentationError("Segmentation failed"))
        
        with pytest.raises(SegmentationError):
            predictor.predict(mock_image)
    
    def test_predict_success(self, predictor, mock_image, mock_crop_image):
        """Test successful prediction flow."""
        predictor.models_loaded = True
        predictor.device = torch.device('cpu')
        
        # Mock _segment_and_crop to return crop image, URL, and confidence
        predictor._segment_and_crop = Mock(return_value=(
            mock_crop_image,
            '/media/test_crop.png',
            0.9
        ))
        
        with patch.object(predictor, '_extract_crop_characteristics', return_value={
            'pixel_width': 100.0,
            'pixel_height': 150.0,
            'pixel_area': 15000.0,
            'scale_factor': 0.035,
            'aspect_ratio': 0.67
        }), \
        patch.object(predictor, '_preprocess_image', return_value=torch.zeros(1, 3, 224, 224)), \
        patch.object(predictor, '_predict_hybrid', return_value=(
            {'alto': 25.0, 'ancho': 15.0, 'grosor': 8.0, 'peso': 1.5},
            {'alto': 0.9, 'ancho': 0.9, 'grosor': 0.9, 'peso': 0.9}
        )):
            
            result = predictor.predict(mock_image)
            
            assert 'alto_mm' in result
            assert 'ancho_mm' in result
            assert 'grosor_mm' in result
            assert 'peso_g' in result
            assert 'confidences' in result
            assert 'crop_url' in result
            assert 'debug' in result
    
    def test_predict_from_bytes(self, predictor, mock_image):
        """Test prediction from image bytes."""
        predictor.models_loaded = True
        
        image_bytes = io.BytesIO()
        mock_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        
        with patch.object(predictor, 'predict', return_value={
            'alto_mm': 25.0,
            'ancho_mm': 15.0,
            'grosor_mm': 8.0,
            'peso_g': 1.5,
            'confidences': {},
            'crop_url': '',
            'debug': {}
        }):
            result = predictor.predict_from_bytes(image_bytes.getvalue())
            
            assert 'alto_mm' in result
    
    def test_predict_from_bytes_invalid(self, predictor):
        """Test prediction from invalid image bytes."""
        predictor.models_loaded = True
        
        invalid_bytes = b'invalid image data'
        
        with pytest.raises(InvalidImageError):
            predictor.predict_from_bytes(invalid_bytes)
    
    def test_get_model_info_not_loaded(self, predictor):
        """Test model info when models are not loaded."""
        predictor.models_loaded = False
        
        info = predictor.get_model_info()
        
        assert info['status'] == 'not_loaded'
    
    def test_get_model_info_loaded(self, predictor):
        """Test model info when models are loaded."""
        predictor.models_loaded = True
        predictor.device = torch.device('cpu')
        predictor.regression_model = Mock()
        predictor.scalers = Mock()
        
        with patch('ml.prediction.predict.get_model_info', return_value={'type': 'hybrid'}):
            info = predictor.get_model_info()
            
            assert info['status'] == 'loaded'
            assert 'device' in info
            assert 'model' in info


class TestPredictorConvenienceFunctions:
    """Tests for convenience functions."""
    
    @patch('ml.prediction.predict.CacaoPredictor')
    def test_get_predictor(self, mock_predictor_class):
        """Test get_predictor function."""
        mock_instance = Mock()
        mock_predictor_class.return_value = mock_instance
        mock_instance.load_artifacts.return_value = True
        
        with patch('ml.prediction.predict._predictor_instance', None):
            result = get_predictor()
            
            assert result == mock_instance
            mock_instance.load_artifacts.assert_called_once()
    
    @patch('ml.prediction.predict.get_predictor')
    def test_load_artifacts_function(self, mock_get_predictor):
        """Test load_artifacts convenience function."""
        mock_predictor = Mock()
        mock_predictor.load_artifacts.return_value = True
        mock_get_predictor.return_value = mock_predictor
        
        result = load_artifacts()
        
        assert result is True
        mock_predictor.load_artifacts.assert_called_once()
    
    @patch('ml.prediction.predict.get_predictor')
    def test_predict_image_function(self, mock_get_predictor, mock_image):
        """Test predict_image convenience function."""
        mock_predictor = Mock()
        mock_predictor.predict.return_value = {
            'alto_mm': 25.0,
            'ancho_mm': 15.0,
            'grosor_mm': 8.0,
            'peso_g': 1.5,
            'confidences': {},
            'crop_url': '',
            'debug': {}
        }
        mock_get_predictor.return_value = mock_predictor
        
        result = predict_image(mock_image)
        
        assert 'alto_mm' in result
        mock_predictor.predict.assert_called_once_with(mock_image)
    
    @patch('ml.prediction.predict.get_predictor')
    def test_predict_image_bytes_function(self, mock_get_predictor):
        """Test predict_image_bytes convenience function."""
        mock_predictor = Mock()
        mock_predictor.predict_from_bytes.return_value = {
            'alto_mm': 25.0,
            'ancho_mm': 15.0,
            'grosor_mm': 8.0,
            'peso_g': 1.5,
            'confidences': {},
            'crop_url': '',
            'debug': {}
        }
        mock_get_predictor.return_value = mock_predictor
        
        image_bytes = b'fake image data'
        result = predict_image_bytes(image_bytes)
        
        assert 'alto_mm' in result
        mock_predictor.predict_from_bytes.assert_called_once_with(image_bytes)


class TestPredictionErrorHandling:
    """Tests for error handling in prediction module."""
    
    def test_prediction_error_inheritance(self):
        """Test that PredictionError is a proper exception."""
        error = PredictionError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_model_not_loaded_error(self):
        """Test ModelNotLoadedError."""
        error = ModelNotLoadedError("Models not loaded")
        assert isinstance(error, PredictionError)
    
    def test_invalid_image_error(self):
        """Test InvalidImageError."""
        error = InvalidImageError("Invalid image")
        assert isinstance(error, PredictionError)

