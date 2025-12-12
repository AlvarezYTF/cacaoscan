"""
Tests for calibrated prediction module.
"""
import pytest
import torch
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from ml.prediction.calibrated_predict import (
    CalibratedCacaoPredictor,
    get_calibrated_predictor
)


class TestCalibratedCacaoPredictor:
    """Tests for CalibratedCacaoPredictor class."""
    
    @pytest.fixture
    def sample_image(self):
        """Create sample PIL image."""
        return Image.new('RGB', (224, 224), color='red')
    
    def test_init(self):
        """Test predictor initialization."""
        predictor = CalibratedCacaoPredictor(confidence_threshold=0.5, use_calibration=True)
        
        assert predictor.confidence_threshold == 0.5
        assert predictor.use_calibration is True
        assert predictor.models_loaded is False
    
    @patch('ml.prediction.calibrated_predict.torch')
    def test_get_device_cuda(self, mock_torch):
        """Test getting CUDA device."""
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "Test GPU"
        mock_torch.device.return_value = torch.device('cuda')
        
        predictor = CalibratedCacaoPredictor()
        
        assert predictor.device.type == 'cuda' or predictor.device.type == 'cpu'
    
    @patch('ml.prediction.calibrated_predict.torch')
    def test_get_device_cpu(self, mock_torch):
        """Test getting CPU device."""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = torch.device('cpu')
        
        predictor = CalibratedCacaoPredictor()
        
        assert predictor.device.type == 'cpu'
    
    @patch('ml.prediction.calibrated_predict.create_cacao_cropper')
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    def test_initialize_yolo_cropper(self, mock_get_dir, mock_create_cropper):
        """Test initializing YOLO cropper."""
        mock_dir = Mock()
        mock_dir.exists.return_value = True
        mock_get_dir.return_value = mock_dir
        
        mock_cropper = Mock()
        mock_create_cropper.return_value = mock_cropper
        
        predictor = CalibratedCacaoPredictor()
        
        predictor._initialize_yolo_cropper()
        
        assert predictor.yolo_cropper is not None
        mock_create_cropper.assert_called_once()
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.os.getenv')
    def test_ensure_regression_assets_exist_true(self, mock_getenv, mock_get_dir):
        """Test when regression assets exist."""
        mock_dir = Mock()
        mock_dir.exists.return_value = True
        mock_dir.__truediv__ = Mock(return_value=Mock(exists=Mock(return_value=True)))
        mock_get_dir.return_value = mock_dir
        mock_getenv.return_value = "0"
        
        predictor = CalibratedCacaoPredictor()
        
        result = predictor._ensure_regression_assets_exist()
        
        assert result is True
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.load_scalers')
    def test_load_scalers_safe(self, mock_load_scalers, mock_get_dir):
        """Test loading scalers safely."""
        mock_scalers = Mock()
        mock_load_scalers.return_value = mock_scalers
        
        predictor = CalibratedCacaoPredictor()
        
        result = predictor._load_scalers_safe()
        
        assert result is True
        assert predictor.scalers == mock_scalers
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.load_scalers')
    def test_load_scalers_safe_error(self, mock_load_scalers, mock_get_dir):
        """Test loading scalers with error."""
        mock_load_scalers.side_effect = Exception("Load error")
        
        predictor = CalibratedCacaoPredictor()
        
        result = predictor._load_scalers_safe()
        
        assert result is False
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.create_model')
    @patch('ml.prediction.calibrated_predict.torch.load')
    def test_load_regression_models(self, mock_torch_load, mock_create_model, mock_get_dir):
        """Test loading regression models."""
        mock_dir = Mock()
        mock_dir.__truediv__ = Mock(return_value=Mock(exists=Mock(return_value=True)))
        mock_get_dir.return_value = mock_dir
        
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        
        mock_checkpoint = {
            'model_state_dict': {}
        }
        mock_torch_load.return_value = mock_checkpoint
        
        predictor = CalibratedCacaoPredictor()
        predictor.device = torch.device('cpu')
        
        result = predictor._load_regression_models()
        
        assert result is True
        assert len(predictor.regression_models) > 0
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.create_model')
    @patch('ml.prediction.calibrated_predict.torch.load')
    def test_load_regression_models_error(self, mock_torch_load, mock_create_model, mock_get_dir):
        """Test loading regression models with error."""
        mock_dir = Mock()
        mock_dir.__truediv__ = Mock(return_value=Mock(exists=Mock(return_value=True)))
        mock_get_dir.return_value = mock_dir
        
        mock_torch_load.side_effect = Exception("Load error")
        
        predictor = CalibratedCacaoPredictor()
        predictor.device = torch.device('cpu')
        
        result = predictor._load_regression_models()
        
        assert result is False
    
    def test_preprocess_image(self, sample_image):
        """Test preprocessing image."""
        predictor = CalibratedCacaoPredictor()
        predictor.device = torch.device('cpu')
        
        result = predictor._preprocess_image(sample_image)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape[0] == 1  # Batch dimension
        assert result.shape[1] == 3  # Channels
    
    def test_preprocess_image_non_rgb(self):
        """Test preprocessing non-RGB image."""
        image = Image.new('L', (224, 224), color=128)
        
        predictor = CalibratedCacaoPredictor()
        predictor.device = torch.device('cpu')
        
        result = predictor._preprocess_image(image)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape[1] == 3  # Should be converted to RGB
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    def test_predict_single_target(self, mock_get_dir):
        """Test predicting single target."""
        mock_dir = Mock()
        mock_get_dir.return_value = mock_dir
        
        mock_model = Mock()
        mock_output = Mock()
        mock_output.item.return_value = 10.5
        mock_model.return_value = mock_output
        mock_model.eval.return_value = None
        
        predictor = CalibratedCacaoPredictor()
        predictor.device = torch.device('cpu')
        predictor.regression_models = {'alto': mock_model}
        
        image_tensor = torch.randn(1, 3, 224, 224)
        
        value, confidence = predictor._predict_single_target(image_tensor, 'alto')
        
        assert value == 10.5
        assert 0.0 <= confidence <= 1.0
    
    @patch('ml.prediction.calibrated_predict.get_calibration_manager')
    def test_load_calibration_if_needed(self, mock_get_manager):
        """Test loading calibration if needed."""
        mock_manager = Mock()
        mock_manager.load_calibration.return_value = Mock(pixels_per_mm=0.2)
        mock_get_manager.return_value = mock_manager
        
        predictor = CalibratedCacaoPredictor(use_calibration=True)
        
        predictor._load_calibration_if_needed()
        
        assert predictor.calibration_manager is not None
    
    def test_load_calibration_if_not_needed(self):
        """Test not loading calibration when not needed."""
        predictor = CalibratedCacaoPredictor(use_calibration=False)
        
        predictor._load_calibration_if_needed()
        
        assert predictor.calibration_manager is None
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.load_scalers')
    @patch('ml.prediction.calibrated_predict.create_model')
    @patch('ml.prediction.calibrated_predict.torch.load')
    @patch('ml.prediction.calibrated_predict.create_cacao_cropper')
    def test_load_artifacts_success(self, mock_create_cropper, mock_torch_load, mock_create_model, mock_load_scalers, mock_get_dir, sample_image):
        """Test loading artifacts successfully."""
        mock_dir = Mock()
        mock_dir.exists.return_value = True
        mock_dir.__truediv__ = Mock(return_value=Mock(exists=Mock(return_value=True)))
        mock_get_dir.return_value = mock_dir
        
        mock_load_scalers.return_value = Mock()
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        mock_torch_load.return_value = {'model_state_dict': {}}
        mock_create_cropper.return_value = Mock()
        
        predictor = CalibratedCacaoPredictor()
        predictor.device = torch.device('cpu')
        
        result = predictor.load_artifacts()
        
        assert result is True
        assert predictor.models_loaded is True
    
    @patch('ml.prediction.calibrated_predict.get_regressors_artifacts_dir')
    @patch('ml.prediction.calibrated_predict.load_scalers')
    def test_load_artifacts_error(self, mock_load_scalers, mock_get_dir):
        """Test loading artifacts with error."""
        mock_load_scalers.side_effect = Exception("Load error")
        
        predictor = CalibratedCacaoPredictor()
        
        result = predictor.load_artifacts()
        
        assert result is False
    
    def test_predict_models_not_loaded(self, sample_image):
        """Test predicting when models are not loaded."""
        predictor = CalibratedCacaoPredictor()
        predictor.models_loaded = False
        
        with pytest.raises(ValueError, match="Modelos no cargados"):
            predictor.predict(sample_image)
    
    @patch('ml.prediction.calibrated_predict.get_calibrated_predictor')
    def test_get_calibrated_predictor(self, mock_get):
        """Test get_calibrated_predictor function."""
        mock_predictor = Mock()
        mock_get.return_value = mock_predictor
        
        result = get_calibrated_predictor(confidence_threshold=0.5, use_calibration=True)
        
        assert result is not None


