"""
Tests unitarios para api.utils.ml_helpers.

Cubre todas las funciones de ML helpers:
- get_predictor
- load_image_for_prediction
- create_prediction_from_result
- calculate_prediction_statistics
- process_image_prediction
"""
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase
from PIL import Image
import io
import time

from api.utils.ml_helpers import (
    get_predictor,
    load_image_for_prediction,
    create_prediction_from_result,
    calculate_prediction_statistics,
    process_image_prediction
)


class MLHelpersTestCase(TestCase):
    """Tests para funciones de ML helpers."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test PIL image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        
        # Create mock cacao_image
        self.mock_cacao_image = Mock()
        self.mock_cacao_image.image.path = '/fake/path/to/image.jpg'
        self.mock_cacao_image.id = 1
        self.mock_cacao_image.processed = False

    @patch('api.utils.ml_helpers.logger')
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_success(self, mock_ml_service_class, mock_logger):
        """Test get_predictor returns predictor on success."""
        # Setup mocks
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        
        mock_service_result = Mock()
        mock_service_result.success = True
        mock_service_result.data = mock_predictor
        
        mock_ml_service = Mock()
        mock_ml_service.get_predictor.return_value = mock_service_result
        mock_ml_service_class.return_value = mock_ml_service
        
        predictor, error = get_predictor()
        
        self.assertIsNotNone(predictor)
        self.assertIsNone(error)
        self.assertEqual(predictor, mock_predictor)

    @patch('api.utils.ml_helpers.logger')
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_service_failure(self, mock_ml_service_class, mock_logger):
        """Test get_predictor returns error when service fails."""
        # Setup mocks
        mock_service_result = Mock()
        mock_service_result.success = False
        mock_error = Mock()
        mock_error.message = "Service unavailable"
        mock_service_result.error = mock_error
        
        mock_ml_service = Mock()
        mock_ml_service.get_predictor.return_value = mock_service_result
        mock_ml_service_class.return_value = mock_ml_service
        
        predictor, error = get_predictor()
        
        self.assertIsNone(predictor)
        self.assertIsNotNone(error)
        self.assertEqual(error['status'], 'error')
        self.assertIn('error', error)
        mock_logger.error.assert_called()

    @patch('api.utils.ml_helpers.logger')
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_models_not_loaded(self, mock_ml_service_class, mock_logger):
        """Test get_predictor returns error when models not loaded."""
        # Setup mocks
        mock_predictor = Mock()
        mock_predictor.models_loaded = False
        
        mock_service_result = Mock()
        mock_service_result.success = True
        mock_service_result.data = mock_predictor
        
        mock_ml_service = Mock()
        mock_ml_service.get_predictor.return_value = mock_service_result
        mock_ml_service_class.return_value = mock_ml_service
        
        predictor, error = get_predictor()
        
        self.assertIsNone(predictor)
        self.assertIsNotNone(error)
        self.assertEqual(error['status'], 'error')
        mock_logger.error.assert_called()

    @patch('api.utils.ml_helpers.logger')
    @patch('api.utils.ml_helpers.MLService')
    def test_get_predictor_exception(self, mock_ml_service_class, mock_logger):
        """Test get_predictor handles exceptions."""
        mock_ml_service_class.side_effect = Exception("Unexpected error")
        
        predictor, error = get_predictor()
        
        self.assertIsNone(predictor)
        self.assertIsNotNone(error)
        self.assertEqual(error['status'], 'error')
        mock_logger.error.assert_called()

    @patch('api.utils.ml_helpers.Image.open')
    def test_load_image_for_prediction_from_file_object(self, mock_image_open):
        """Test load_image_for_prediction loads from file object."""
        # Create mock file object
        mock_file = Mock()
        mock_file.seek = Mock()
        mock_file.read.return_value = b'fake_image_bytes'
        mock_image_open.return_value = self.test_image
        
        result = load_image_for_prediction(mock_file, self.mock_cacao_image)
        
        mock_file.seek.assert_called_once_with(0)
        mock_file.read.assert_called_once()
        mock_image_open.assert_called()

    @patch('api.utils.ml_helpers.Image.open')
    def test_load_image_for_prediction_falls_back_to_path(self, mock_image_open):
        """Test load_image_for_prediction falls back to path when file object fails."""
        # Create invalid file object (no seek/read methods)
        mock_file = Mock()
        del mock_file.seek
        del mock_file.read
        mock_image_open.return_value = self.test_image
        
        result = load_image_for_prediction(mock_file, self.mock_cacao_image)
        
        # Should fall back to opening from path
        mock_image_open.assert_called_with(self.mock_cacao_image.image.path)

    @patch('api.utils.ml_helpers.Image.open')
    def test_load_image_for_prediction_empty_file_object(self, mock_image_open):
        """Test load_image_for_prediction falls back when file object is empty."""
        mock_file = Mock()
        mock_file.seek = Mock()
        mock_file.read.return_value = b''  # Empty bytes
        mock_image_open.return_value = self.test_image
        
        result = load_image_for_prediction(mock_file, self.mock_cacao_image)
        
        # Should fall back to path
        mock_image_open.assert_called_with(self.mock_cacao_image.image.path)

    @patch('api.utils.ml_helpers.CacaoPrediction')
    def test_create_prediction_from_result(self, mock_prediction_class):
        """Test create_prediction_from_result creates and saves prediction."""
        mock_prediction_instance = Mock()
        mock_prediction_class.return_value = mock_prediction_instance
        
        result = {
            'alto_mm': 10.5,
            'ancho_mm': 8.3,
            'grosor_mm': 5.2,
            'peso_g': 12.5,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'crop_url': '/media/crops/image.jpg',
            'debug': {
                'device': 'cpu',
                'models_version': 'v1.0'
            }
        }
        
        prediction = create_prediction_from_result(
            self.mock_cacao_image,
            result,
            150
        )
        
        mock_prediction_class.assert_called_once()
        mock_prediction_instance.save.assert_called_once()
        self.assertTrue(self.mock_cacao_image.processed)
        self.mock_cacao_image.save.assert_called_once()

    @patch('api.utils.ml_helpers.CacaoPrediction')
    def test_create_prediction_from_result_with_gpu_device(self, mock_prediction_class):
        """Test create_prediction_from_result handles GPU device."""
        mock_prediction_instance = Mock()
        mock_prediction_class.return_value = mock_prediction_instance
        
        result = {
            'alto_mm': 10.5,
            'ancho_mm': 8.3,
            'grosor_mm': 5.2,
            'peso_g': 12.5,
            'confidences': {
                'alto': 0.95,
                'ancho': 0.92,
                'grosor': 0.88,
                'peso': 0.90
            },
            'debug': {
                'device': 'cuda:0',
                'models_version': 'v1.0'
            }
        }
        
        prediction = create_prediction_from_result(
            self.mock_cacao_image,
            result,
            150
        )
        
        # Should extract 'cuda' from 'cuda:0'
        call_kwargs = mock_prediction_class.call_args[1]
        self.assertEqual(call_kwargs['device_used'], 'cuda')

    def test_calculate_prediction_statistics_empty_results(self):
        """Test calculate_prediction_statistics with empty results."""
        results = []
        
        stats = calculate_prediction_statistics(results)
        
        self.assertEqual(stats['total_images'], 0)
        self.assertEqual(stats['processed_images'], 0)
        self.assertEqual(stats['failed_images'], 0)
        self.assertEqual(stats['average_confidence'], 0)
        self.assertEqual(stats['total_weight'], 0)

    def test_calculate_prediction_statistics_all_failed(self):
        """Test calculate_prediction_statistics with all failed results."""
        results = [
            {'success': False, 'error': 'Error 1'},
            {'success': False, 'error': 'Error 2'}
        ]
        
        stats = calculate_prediction_statistics(results)
        
        self.assertEqual(stats['total_images'], 2)
        self.assertEqual(stats['processed_images'], 0)
        self.assertEqual(stats['failed_images'], 2)

    def test_calculate_prediction_statistics_successful_results(self):
        """Test calculate_prediction_statistics with successful results."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 10.0,
                    'ancho_mm': 8.0,
                    'grosor_mm': 5.0,
                    'peso_g': 10.0,
                    'confidences': {
                        'alto': 0.9,
                        'ancho': 0.8,
                        'grosor': 0.85,
                        'peso': 0.95
                    }
                }
            },
            {
                'success': True,
                'prediction': {
                    'alto_mm': 12.0,
                    'ancho_mm': 10.0,
                    'grosor_mm': 6.0,
                    'peso_g': 15.0,
                    'confidences': {
                        'alto': 0.95,
                        'ancho': 0.85,
                        'grosor': 0.90,
                        'peso': 0.92
                    }
                }
            }
        ]
        
        stats = calculate_prediction_statistics(results)
        
        self.assertEqual(stats['total_images'], 2)
        self.assertEqual(stats['processed_images'], 2)
        self.assertEqual(stats['failed_images'], 0)
        self.assertGreater(stats['average_confidence'], 0)
        self.assertEqual(stats['total_weight'], 25.0)
        self.assertEqual(stats['average_dimensions']['alto'], 11.0)

    def test_calculate_prediction_statistics_mixed_results(self):
        """Test calculate_prediction_statistics with mixed success/failure."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 10.0,
                    'ancho_mm': 8.0,
                    'grosor_mm': 5.0,
                    'peso_g': 10.0,
                    'confidences': {
                        'alto': 0.9,
                        'ancho': 0.8,
                        'grosor': 0.85,
                        'peso': 0.95
                    }
                }
            },
            {'success': False, 'error': 'Error'}
        ]
        
        stats = calculate_prediction_statistics(results)
        
        self.assertEqual(stats['total_images'], 2)
        self.assertEqual(stats['processed_images'], 1)
        self.assertEqual(stats['failed_images'], 1)

    @patch('api.utils.ml_helpers.create_prediction_from_result')
    @patch('api.utils.ml_helpers.load_image_for_prediction')
    @patch('api.utils.ml_helpers.Image.open')
    @patch('api.utils.ml_helpers.time.time')
    def test_process_image_prediction_success(self, mock_time, mock_image_open,
                                              mock_load_image, mock_create_pred):
        """Test process_image_prediction with successful prediction."""
        # Setup mocks
        mock_time.side_effect = [100.0, 100.15]  # Start and end time
        mock_image_open.return_value = self.test_image
        
        mock_predictor = Mock()
        mock_prediction_result = {
            'alto_mm': 10.0,
            'ancho_mm': 8.0,
            'grosor_mm': 5.0,
            'peso_g': 10.0,
            'confidences': {
                'alto': 0.9,
                'ancho': 0.8,
                'grosor': 0.85,
                'peso': 0.95
            },
            'crop_url': '/crop.jpg',
            'debug': {'models_version': 'v1.0'}
        }
        mock_predictor.predict.return_value = mock_prediction_result
        
        mock_prediction = Mock()
        mock_prediction.id = 1
        mock_create_pred.return_value = mock_prediction
        
        result, error = process_image_prediction(
            mock_predictor,
            self.test_image,
            self.mock_cacao_image
        )
        
        self.assertIsNone(error)
        self.assertTrue(result['success'])
        self.assertEqual(result['image_id'], 1)
        self.assertIn('prediction', result)
        mock_predictor.predict.assert_called_once()

    @patch('api.utils.ml_helpers.logger')
    @patch('api.utils.ml_helpers.Image.open')
    def test_process_image_prediction_exception(self, mock_image_open, mock_logger):
        """Test process_image_prediction handles exceptions."""
        mock_image_open.return_value = self.test_image
        
        mock_predictor = Mock()
        mock_predictor.predict.side_effect = Exception("Prediction error")
        
        result, error = process_image_prediction(
            mock_predictor,
            self.test_image,
            self.mock_cacao_image
        )
        
        self.assertIsNotNone(error)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        mock_logger.error.assert_called()

    @patch('api.utils.ml_helpers.Image.open')
    def test_process_image_prediction_with_string_path(self, mock_image_open):
        """Test process_image_prediction with string image path."""
        mock_image_open.return_value = self.test_image
        
        mock_predictor = Mock()
        mock_predictor.predict.return_value = {
            'alto_mm': 10.0,
            'ancho_mm': 8.0,
            'grosor_mm': 5.0,
            'peso_g': 10.0,
            'confidences': {
                'alto': 0.9,
                'ancho': 0.8,
                'grosor': 0.85,
                'peso': 0.95
            }
        }
        
        with patch('api.utils.ml_helpers.create_prediction_from_result'):
            result, error = process_image_prediction(
                mock_predictor,
                '/path/to/image.jpg',
                self.mock_cacao_image
            )
            
            mock_image_open.assert_called_with('/path/to/image.jpg')

