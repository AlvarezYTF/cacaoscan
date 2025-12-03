"""
Tests for Training Services.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from PIL import Image

from training.services.ml.prediction_service import PredictionService
from training.services.ml.ml_service import MLService, ModelLoadState


@pytest.fixture
def mock_predictor():
    """Create a mock predictor."""
    predictor = MagicMock()
    predictor.models_loaded = True
    predictor.predict.return_value = {
        'alto_mm': 20.5,
        'ancho_mm': 15.3,
        'grosor_mm': 10.2,
        'peso_g': 1.5,
        'confidences': {
            'alto': 0.9,
            'ancho': 0.85,
            'grosor': 0.88,
            'peso': 0.92
        }
    }
    predictor.get_model_info.return_value = {
        'status': 'loaded',
        'device': 'cpu',
        'model': 'HybridCacaoRegression',
        'model_details': {},
        'scalers': 'loaded'
    }
    return predictor


@pytest.fixture
def test_image():
    """Create a test PIL Image."""
    return Image.new('RGB', (100, 100), color='red')


@pytest.mark.django_db
class TestMLService:
    """Tests for MLService."""

    def test_singleton_pattern(self):
        """Test that MLService is a singleton."""
        service1 = MLService()
        service2 = MLService()
        
        assert service1 is service2

    def test_get_predictor_success(self, mock_predictor):
        """Test getting predictor successfully."""
        service = MLService()
        
        with patch('training.services.ml.ml_service.get_predictor', return_value=mock_predictor):
            with patch('training.services.ml.ml_service.load_artifacts', return_value=True):
                result = service.get_predictor()
        
        assert result.success is True
        assert result.data is not None
        assert 'obtained' in result.message.lower()

    def test_get_predictor_already_loaded(self, mock_predictor):
        """Test getting predictor when already loaded."""
        service = MLService()
        
        # Set up as already loaded
        service._predictor_instance = mock_predictor
        service._load_state = ModelLoadState.LOADED
        
        result = service.get_predictor()
        
        assert result.success is True
        assert 'already loaded' in result.message.lower()

    def test_get_predictor_import_error(self):
        """Test getting predictor when import fails."""
        service = MLService()
        
        with patch('training.services.ml.ml_service.get_predictor', side_effect=ImportError("Module not found")):
            result = service.get_predictor()
        
        assert result.success is False
        assert 'not available' in str(result.error).lower() or 'module' in str(result.error).lower()

    def test_get_predictor_load_artifacts_fails(self, mock_predictor):
        """Test getting predictor when load_artifacts fails."""
        service = MLService()
        
        with patch('training.services.ml.ml_service.get_predictor', return_value=mock_predictor):
            with patch('training.services.ml.ml_service.load_artifacts', return_value=False):
                result = service.get_predictor()
        
        assert result.success is False
        assert 'not available' in str(result.error).lower() or 'initialize' in str(result.error).lower()

    def test_get_predictor_models_not_loaded_after_load(self, mock_predictor):
        """Test getting predictor when models fail to load after load_artifacts."""
        service = MLService()
        
        mock_predictor.models_loaded = False
        
        with patch('training.services.ml.ml_service.get_predictor', return_value=mock_predictor):
            with patch('training.services.ml.ml_service.load_artifacts', return_value=True):
                result = service.get_predictor()
        
        assert result.success is False
        assert 'error loading' in str(result.error).lower() or 'load_artifacts' in str(result.error).lower()

    def test_get_predictor_force_reload(self, mock_predictor):
        """Test getting predictor with force reload."""
        service = MLService()
        
        # Set up as already loaded
        service._predictor_instance = mock_predictor
        service._load_state = ModelLoadState.LOADED
        
        with patch('training.services.ml.ml_service.get_predictor', return_value=mock_predictor):
            with patch('training.services.ml.ml_service.load_artifacts', return_value=True):
                result = service.get_predictor(force_reload=True)
        
        assert result.success is True

    def test_load_models_success(self, mock_predictor):
        """Test loading models successfully."""
        service = MLService()
        
        with patch.object(service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.success(data=mock_predictor)
            
            result = service.load_models()
        
        assert result.success is True
        assert 'loaded successfully' in result.message.lower()

    def test_load_models_failure(self, mock_predictor):
        """Test loading models when it fails."""
        service = MLService()
        
        with patch.object(service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.error(
                ValidationServiceError("Failed to load")
            )
            
            result = service.load_models()
        
        assert result.success is False

    def test_load_models_force(self, mock_predictor):
        """Test loading models with force flag."""
        service = MLService()
        
        with patch.object(service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.success(data=mock_predictor)
            
            result = service.load_models(force=True)
        
        assert result.success is True
        mock_get.assert_called_once_with(force_reload=True)

    def test_get_model_status_success(self, mock_predictor):
        """Test getting model status successfully."""
        service = MLService()
        service._load_state = ModelLoadState.LOADED
        
        with patch('training.services.ml.ml_service.get_predictor', return_value=mock_predictor):
            result = service.get_model_status()
        
        assert result.success is True
        assert 'status' in result.data
        assert result.data['models_loaded'] is True
        assert result.data['load_state'] == 'loaded'

    def test_get_model_status_import_error(self):
        """Test getting model status when import fails."""
        service = MLService()
        
        with patch('training.services.ml.ml_service.get_predictor', side_effect=ImportError("Module not found")):
            result = service.get_model_status()
        
        assert result.success is False
        assert 'not available' in str(result.error).lower()

    def test_get_model_status_not_loaded(self, mock_predictor):
        """Test getting model status when models are not loaded."""
        service = MLService()
        service._load_state = ModelLoadState.NOT_LOADED
        mock_predictor.models_loaded = False
        
        with patch('training.services.ml.ml_service.get_predictor', return_value=mock_predictor):
            result = service.get_model_status()
        
        assert result.success is True
        assert result.data['models_loaded'] is False
        assert result.data['load_state'] == 'not_loaded'

    def test_reload_models(self, mock_predictor):
        """Test reloading models."""
        service = MLService()
        service._predictor_instance = mock_predictor
        service._load_state = ModelLoadState.LOADED
        
        with patch.object(service, 'load_models') as mock_load:
            mock_load.return_value = ServiceResult.success(message="Reloaded")
            
            result = service.reload_models()
        
        assert result.success is True
        mock_load.assert_called_once_with(force=True)
        
        # Verify state was reset
        assert service._predictor_instance is None
        assert service._load_state == ModelLoadState.NOT_LOADED

    def test_handle_loading_state(self, mock_predictor):
        """Test handling loading state."""
        service = MLService()
        service._load_state = ModelLoadState.LOADING
        
        def get_predictor():
            return mock_predictor
        
        result = service._handle_loading_state(get_predictor)
        
        assert result is not None
        assert result.success is True
        assert service._load_state == ModelLoadState.LOADED

    def test_handle_loading_state_models_not_loaded(self):
        """Test handling loading state when models are not loaded."""
        service = MLService()
        service._load_state = ModelLoadState.LOADING
        
        mock_predictor = MagicMock()
        mock_predictor.models_loaded = False
        
        def get_predictor():
            return mock_predictor
        
        result = service._handle_loading_state(get_predictor)
        
        assert result is None  # Should return None when models not loaded


@pytest.mark.django_db
class TestPredictionService:
    """Tests for PredictionService."""

    def test_get_predictor_success(self, mock_predictor):
        """Test getting predictor successfully."""
        service = PredictionService()
        
        with patch.object(service.ml_service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.success(data=mock_predictor)
            
            result = service.get_predictor()
        
        assert result.success is True
        assert result.data == mock_predictor

    def test_predict_success(self, test_image, mock_predictor):
        """Test performing prediction successfully."""
        service = PredictionService()
        
        with patch.object(service.ml_service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.success(data=mock_predictor)
            
            result = service.predict(test_image)
        
        assert result.success is True
        assert 'alto_mm' in result.data
        assert 'processing_time_ms' in result.data
        assert result.message == "Prediction completed successfully"
        
        # Verify predictor was called
        mock_predictor.predict.assert_called_once()

    def test_predict_predictor_not_available(self, test_image):
        """Test prediction when predictor is not available."""
        service = PredictionService()
        
        with patch.object(service.ml_service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.error(
                ValidationServiceError("Predictor not available")
            )
            
            result = service.predict(test_image)
        
        assert result.success is False
        assert 'not available' in str(result.error).lower() or 'predictor' in str(result.error).lower()

    def test_predict_exception(self, test_image, mock_predictor):
        """Test prediction when an exception occurs."""
        service = PredictionService()
        
        mock_predictor.predict.side_effect = Exception("Prediction error")
        
        with patch.object(service.ml_service, 'get_predictor') as mock_get:
            mock_get.return_value = ServiceResult.success(data=mock_predictor)
            
            result = service.predict(test_image)
        
        assert result.success is False
        assert 'error' in str(result.error).lower()

    def test_predict_includes_processing_time(self, test_image, mock_predictor):
        """Test that prediction includes processing time."""
        service = PredictionService()
        
        with patch.object(service.ml_service, 'get_predictor') as mock_get:
            with patch('time.time', side_effect=[0, 0.15]):  # 150ms
                mock_get.return_value = ServiceResult.success(data=mock_predictor)
                
                result = service.predict(test_image)
        
        assert result.success is True
        assert result.data['processing_time_ms'] == 150

    def test_check_models_status_success(self, mock_predictor):
        """Test checking models status successfully."""
        service = PredictionService()
        
        with patch.object(service.ml_service, 'get_model_status') as mock_status:
            mock_status.return_value = ServiceResult.success(
                data={
                    'load_state': 'loaded',
                    'models_loaded': True,
                    'status': 'loaded'
                }
            )
            
            result = service.check_models_status()
        
        assert result.success is True
        assert result.data['models_loaded'] is True

    def test_check_models_status_failure(self):
        """Test checking models status when it fails."""
        service = PredictionService()
        
        with patch.object(service.ml_service, 'get_model_status') as mock_status:
            mock_status.return_value = ServiceResult.error(
                ValidationServiceError("Status check failed")
            )
            
            result = service.check_models_status()
        
        assert result.success is False

