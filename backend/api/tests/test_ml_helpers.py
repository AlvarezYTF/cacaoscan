"""
Tests for ML helpers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
from api.utils.ml_helpers import (
    get_predictor,
    load_image_for_prediction,
    create_prediction_from_result,
    calculate_prediction_statistics,
    process_image_prediction
)


@pytest.mark.django_db
class TestGetPredictor:
    """Tests for get_predictor function."""
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_success(self, mock_ml_service):
        """Test getting predictor successfully."""
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        
        mock_service_instance = Mock()
        mock_service_instance.get_predictor.return_value = Mock(
            success=True,
            data=mock_predictor
        )
        mock_ml_service.return_value = mock_service_instance
        
        predictor, error = get_predictor()
        
        assert predictor is not None
        assert error is None
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_not_loaded(self, mock_ml_service):
        """Test getting predictor when models not loaded."""
        mock_predictor = Mock()
        mock_predictor.models_loaded = False
        
        mock_service_instance = Mock()
        mock_service_instance.get_predictor.return_value = Mock(
            success=True,
            data=mock_predictor
        )
        mock_ml_service.return_value = mock_service_instance
        
        predictor, error = get_predictor()
        
        assert predictor is None
        assert error is not None
    
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_service_error(self, mock_ml_service):
        """Test getting predictor when service fails."""
        mock_service_instance = Mock()
        mock_service_instance.get_predictor.return_value = Mock(
            success=False,
            error=Mock(message="Models not available")
        )
        mock_ml_service.return_value = mock_service_instance
        
        predictor, error = get_predictor()
        
        assert predictor is None
        assert error is not None


@pytest.mark.django_db
class TestLoadImageForPrediction:
    """Tests for load_image_for_prediction function."""
    
    def test_load_image_from_file_object(self):
        """Test loading image from file object."""
        image_bytes = b"fake image bytes"
        image_file = io.BytesIO(image_bytes)
        cacao_image = Mock()
        
        with patch('PIL.Image.open') as mock_open:
            mock_image = Mock()
            mock_open.return_value = mock_image
            
            result = load_image_for_prediction(image_file, cacao_image)
            
            assert result is not None
    
    def test_load_image_from_path(self):
        """Test loading image from path."""
        cacao_image = Mock()
        cacao_image.image.path = '/path/to/image.jpg'
        
        with patch('PIL.Image.open') as mock_open:
            mock_image = Mock()
            mock_open.return_value = mock_image
            
            result = load_image_for_prediction(None, cacao_image)
            
            assert result is not None


@pytest.mark.django_db
class TestCreatePredictionFromResult:
    """Tests for create_prediction_from_result function."""
    
    def test_create_prediction_from_result(self):
        """Test creating prediction from result."""
        cacao_image = Mock()
        cacao_image.id = 1
        cacao_image.processed = False
        
        result = {
            'alto_mm': 10.0,
            'ancho_mm': 20.0,
            'grosor_mm': 5.0,
            'peso_g': 100.0,
            'confidences': {
                'alto': 0.9,
                'ancho': 0.8,
                'grosor': 0.7,
                'peso': 0.6
            },
            'crop_url': '/crop/url',
            'debug': {
                'device': 'cpu',
                'models_version': 'v1.0'
            }
        }
        
        with patch('api.utils.ml_helpers.CacaoPrediction') as mock_prediction:
            mock_instance = Mock()
            mock_prediction.return_value = mock_instance
            
            prediction = create_prediction_from_result(cacao_image, result, 100)
            
            assert prediction is not None
            assert cacao_image.processed is True


class TestCalculatePredictionStatistics:
    """Tests for calculate_prediction_statistics function."""
    
    def test_calculate_statistics_successful_results(self):
        """Test calculating statistics with successful results."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 10.0,
                    'ancho_mm': 20.0,
                    'grosor_mm': 5.0,
                    'peso_g': 100.0,
                    'confidences': {
                        'alto': 0.9,
                        'ancho': 0.8,
                        'grosor': 0.7,
                        'peso': 0.6
                    }
                }
            },
            {
                'success': True,
                'prediction': {
                    'alto_mm': 12.0,
                    'ancho_mm': 22.0,
                    'grosor_mm': 6.0,
                    'peso_g': 120.0,
                    'confidences': {
                        'alto': 0.95,
                        'ancho': 0.85,
                        'grosor': 0.75,
                        'peso': 0.65
                    }
                }
            }
        ]
        
        stats = calculate_prediction_statistics(results)
        
        assert stats['total_images'] == 2
        assert stats['processed_images'] == 2
        assert stats['failed_images'] == 0
        assert stats['average_confidence'] > 0
        assert 'average_dimensions' in stats
        assert stats['total_weight'] > 0
    
    def test_calculate_statistics_no_successful_results(self):
        """Test calculating statistics with no successful results."""
        results = [
            {'success': False, 'error': 'Test error'}
        ]
        
        stats = calculate_prediction_statistics(results)
        
        assert stats['total_images'] == 1
        assert stats['processed_images'] == 0
        assert stats['failed_images'] == 1
        assert stats['average_confidence'] == 0
    
    def test_calculate_statistics_mixed_results(self):
        """Test calculating statistics with mixed results."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 10.0,
                    'ancho_mm': 20.0,
                    'grosor_mm': 5.0,
                    'peso_g': 100.0,
                    'confidences': {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
                }
            },
            {'success': False, 'error': 'Test error'}
        ]
        
        stats = calculate_prediction_statistics(results)
        
        assert stats['total_images'] == 2
        assert stats['processed_images'] == 1
        assert stats['failed_images'] == 1


@pytest.mark.django_db
class TestProcessImagePrediction:
    """Tests for process_image_prediction function."""
    
    def test_process_image_prediction_success(self):
        """Test processing image prediction successfully."""
        predictor = Mock()
        predictor.predict.return_value = {
            'alto_mm': 10.0,
            'ancho_mm': 20.0,
            'grosor_mm': 5.0,
            'peso_g': 100.0,
            'confidences': {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6},
            'crop_url': '/crop/url',
            'debug': {'models_version': 'v1.0'}
        }
        
        cacao_image = Mock()
        cacao_image.id = 1
        
        with patch('api.utils.ml_helpers.load_image_for_prediction') as mock_load:
            mock_image = Image.new('RGB', (100, 100))
            mock_load.return_value = mock_image
            
            with patch('api.utils.ml_helpers.create_prediction_from_result'):
                result, error = process_image_prediction(predictor, mock_image, cacao_image)
                
                assert result['success']
                assert error is None
                assert result['image_id'] == 1
    
    def test_process_image_prediction_with_string_path(self):
        """Test processing image prediction with string path."""
        predictor = Mock()
        predictor.predict.return_value = {
            'alto_mm': 10.0,
            'ancho_mm': 20.0,
            'grosor_mm': 5.0,
            'peso_g': 100.0,
            'confidences': {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6},
            'debug': {}
        }
        
        cacao_image = Mock()
        cacao_image.id = 1
        
        with patch('PIL.Image.open') as mock_open:
            mock_image = Image.new('RGB', (100, 100))
            mock_open.return_value = mock_image
            
            with patch('api.utils.ml_helpers.create_prediction_from_result'):
                result, error = process_image_prediction(predictor, '/path/to/image.jpg', cacao_image)
                
                assert result['success']
                assert error is None
    
    def test_process_image_prediction_error(self):
        """Test processing image prediction with error."""
        predictor = Mock()
        predictor.predict.side_effect = Exception("Prediction error")
        
        cacao_image = Mock()
        cacao_image.id = 1
        
        with patch('api.utils.ml_helpers.load_image_for_prediction') as mock_load:
            mock_image = Image.new('RGB', (100, 100))
            mock_load.return_value = mock_image
            
            result, error = process_image_prediction(predictor, mock_image, cacao_image)
            
            assert not result['success']
            assert error is not None

