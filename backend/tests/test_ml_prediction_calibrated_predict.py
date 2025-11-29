"""
Unit tests for calibrated prediction module (calibrated_predict.py).
Tests prediction with calibration functionality.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from ml.prediction.calibrated_predict import (
    CalibratedCacaoPredictor,
    get_calibrated_predictor
)
from ml.measurement.calibration import CalibrationMethod, ReferenceObject


@pytest.fixture
def mock_image():
    """Create a mock PIL Image for testing."""
    return Image.new('RGB', (512, 512), color='red')


@pytest.fixture
def calibrated_predictor():
    """Create a CalibratedCacaoPredictor instance for testing."""
    with patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir'), \
         patch('ml.prediction.calibrated_predict.get_yolo_artifacts_dir'), \
         patch('ml.prediction.calibrated_predict.ensure_dir_exists'):
        predictor = CalibratedCacaoPredictor(
            confidence_threshold=0.5,
            use_calibration=True
        )
        predictor.models_loaded = False
        return predictor


class TestCalibratedCacaoPredictor:
    """Tests for CalibratedCacaoPredictor class."""
    
    def test_predictor_initialization(self):
        """Test predictor initialization."""
        with patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir'), \
             patch('ml.prediction.calibrated_predict.get_yolo_artifacts_dir'), \
             patch('ml.prediction.calibrated_predict.ensure_dir_exists'), \
             patch('ml.prediction.calibrated_predict.get_calibration_manager'):
            
            predictor = CalibratedCacaoPredictor(
                confidence_threshold=0.6,
                use_calibration=True
            )
            
            assert predictor.confidence_threshold == 0.6
            assert predictor.use_calibration is True
            assert predictor.models_loaded is False
    
    def test_get_device_cpu(self, calibrated_predictor):
        """Test device detection when GPU is not available."""
        with patch('torch.cuda.is_available', return_value=False):
            device = calibrated_predictor._get_device()
            assert device.type == 'cpu'
    
    def test_get_device_gpu(self, calibrated_predictor):
        """Test device detection when GPU is available."""
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.get_device_name', return_value='Test GPU'):
            device = calibrated_predictor._get_device()
            assert device.type == 'cuda'
    
    def test_preprocess_image(self, calibrated_predictor, mock_image):
        """Test image preprocessing."""
        calibrated_predictor.device = torch.device('cpu')
        
        tensor = calibrated_predictor._preprocess_image(mock_image)
        
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape[0] == 1  # Batch dimension
        assert tensor.shape[1] == 3  # RGB channels
        assert tensor.shape[2] == 224  # Height
        assert tensor.shape[3] == 224  # Width
    
    def test_preprocess_image_converts_to_rgb(self, calibrated_predictor):
        """Test that non-RGB images are converted to RGB."""
        calibrated_predictor.device = torch.device('cpu')
        gray_image = Image.new('L', (224, 224))
        
        tensor = calibrated_predictor._preprocess_image(gray_image)
        
        assert tensor.shape[1] == 3  # Should be RGB
    
    def test_predict_single_target(self, calibrated_predictor):
        """Test prediction for a single target."""
        calibrated_predictor.device = torch.device('cpu')
        mock_model = Mock()
        mock_model.return_value = torch.tensor([[25.0]])
        calibrated_predictor.regression_models = {'alto': mock_model}
        
        image_tensor = torch.zeros(1, 3, 224, 224)
        
        pred_value, confidence = calibrated_predictor._predict_single_target(image_tensor, 'alto')
        
        assert isinstance(pred_value, float)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    def test_calibrate_image_with_calibration_disabled(self, calibrated_predictor, mock_image):
        """Test calibration when calibration is disabled."""
        calibrated_predictor.use_calibration = False
        
        result = calibrated_predictor.calibrate_image(mock_image)
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_calibrate_image_success(self, calibrated_predictor, mock_image):
        """Test successful image calibration."""
        calibrated_predictor.use_calibration = True
        mock_calibration_manager = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.pixels_per_mm = 0.035
        mock_result.confidence = 0.9
        mock_result.method = CalibrationMethod.COIN_DETECTION
        mock_result.reference_object = ReferenceObject.COIN_1000_COP
        mock_result.calibration_image_path = '/tmp/calibration.jpg'
        mock_calibration_manager.calibrate_image.return_value = mock_result
        mock_calibration_manager.save_calibration = Mock()
        calibrated_predictor.calibration_manager = mock_calibration_manager
        
        with patch('cv2.cvtColor'), \
             patch('numpy.array', return_value=np.zeros((512, 512, 3), dtype=np.uint8)):
            result = calibrated_predictor.calibrate_image(mock_image)
            
            assert result['success'] is True
            assert 'pixels_per_mm' in result
            assert result['pixels_per_mm'] == 0.035
    
    def test_calibrate_image_failure(self, calibrated_predictor, mock_image):
        """Test image calibration failure."""
        calibrated_predictor.use_calibration = True
        mock_calibration_manager = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "No coins detected"
        mock_calibration_manager.calibrate_image.return_value = mock_result
        calibrated_predictor.calibration_manager = mock_calibration_manager
        
        with patch('cv2.cvtColor'), \
             patch('numpy.array', return_value=np.zeros((512, 512, 3), dtype=np.uint8)):
            result = calibrated_predictor.calibrate_image(mock_image)
            
            assert result['success'] is False
            assert 'error' in result
    
    def test_predict_requires_loaded_models(self, calibrated_predictor, mock_image):
        """Test that predict raises error when models are not loaded."""
        calibrated_predictor.models_loaded = False
        
        with pytest.raises(ValueError, match="Modelos no cargados"):
            calibrated_predictor.predict(mock_image)
    
    def test_get_calibration_status_disabled(self, calibrated_predictor):
        """Test calibration status when calibration is disabled."""
        calibrated_predictor.use_calibration = False
        
        status = calibrated_predictor.get_calibration_status()
        
        assert status['calibration_enabled'] is False
    
    def test_get_calibration_status_no_calibration(self, calibrated_predictor):
        """Test calibration status when no calibration is loaded."""
        calibrated_predictor.use_calibration = True
        calibrated_predictor.calibration_manager = Mock()
        calibrated_predictor.calibration_manager.current_calibration = None
        
        status = calibrated_predictor.get_calibration_status()
        
        assert status['calibration_enabled'] is True
        assert status['calibration_loaded'] is False
    
    def test_get_calibration_status_loaded(self, calibrated_predictor):
        """Test calibration status when calibration is loaded."""
        calibrated_predictor.use_calibration = True
        mock_calibration = Mock()
        mock_calibration.pixels_per_mm = 0.035
        mock_calibration.method = CalibrationMethod.COIN_DETECTION
        mock_calibration.confidence = 0.9
        mock_calibration.timestamp = "2024-01-01"
        mock_calibration.validation_score = 0.95
        
        mock_calibration_manager = Mock()
        mock_calibration_manager.current_calibration = mock_calibration
        calibrated_predictor.calibration_manager = mock_calibration_manager
        
        status = calibrated_predictor.get_calibration_status()
        
        assert status['calibration_enabled'] is True
        assert status['calibration_loaded'] is True
        assert status['pixels_per_mm'] == 0.035


class TestCalibratedPredictorConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_calibrated_predictor(self):
        """Test get_calibrated_predictor function."""
        with patch('ml.prediction.calibrated_predict.CalibratedCacaoPredictor') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = get_calibrated_predictor(confidence_threshold=0.6, use_calibration=True)
            
            assert result == mock_instance
            mock_class.assert_called_once_with(confidence_threshold=0.6, use_calibration=True)

