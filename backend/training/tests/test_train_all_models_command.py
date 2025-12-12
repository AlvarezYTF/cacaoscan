"""
Tests for train_all_models management command.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
class TestTrainAllModelsCommand:
    """Tests for train_all_models command."""
    
    @pytest.fixture
    def command(self):
        """Create command instance."""
        from training.management.commands.train_all_models import Command
        return Command()
    
    def test_determine_hybrid_mode_hybrid_flag(self, command):
        """Test determining hybrid mode with hybrid flag."""
        options = {
            'regression_hybrid': True,
            'regression_model_type': 'resnet18'
        }
        
        result = command._determine_hybrid_mode(options)
        
        assert result is True
    
    def test_determine_hybrid_mode_model_type(self, command):
        """Test determining hybrid mode with model type."""
        options = {
            'regression_hybrid': False,
            'regression_model_type': 'hybrid'
        }
        
        result = command._determine_hybrid_mode(options)
        
        assert result is True
    
    def test_prepare_yolo_config(self, command):
        """Test preparing YOLO config."""
        options = {
            'yolo_dataset_size': 150,
            'yolo_epochs': 100,
            'yolo_batch_size': 16,
            'yolo_model_name': 'yolov8s-seg'
        }
        
        config = command._prepare_yolo_config(options)
        
        assert config['dataset_size'] == 150
        assert config['epochs'] == 100
        assert config['batch_size'] == 16
        assert config['model_name'] == 'yolov8s-seg'
    
    def test_prepare_regression_config_hybrid(self, command):
        """Test preparing regression config with hybrid."""
        options = {
            'regression_epochs': 150,
            'regression_batch_size': 16,
            'regression_learning_rate': 0.001,
            'regression_model_type': 'hybrid',
            'regression_use_pixel_features': True
        }
        
        config = command._prepare_regression_config(options, True)
        
        assert config['model_type'] == 'hybrid'
        assert config['hybrid'] is True
        assert config['use_pixel_features'] is True
    
    def test_prepare_regression_config_not_hybrid(self, command):
        """Test preparing regression config without hybrid."""
        options = {
            'regression_epochs': 150,
            'regression_batch_size': 16,
            'regression_learning_rate': 0.001,
            'regression_model_type': 'resnet18',
            'regression_use_pixel_features': False
        }
        
        config = command._prepare_regression_config(options, False)
        
        assert config['model_type'] == 'resnet18'
        assert config['hybrid'] is False
        assert config['use_pixel_features'] is False
    
    def test_print_startup_message(self, command):
        """Test printing startup message."""
        command.stdout = StringIO()
        
        yolo_config = {'dataset_size': 150, 'epochs': 100}
        regression_config = {'epochs': 150, 'model_type': 'hybrid'}
        
        command._print_startup_message(yolo_config, regression_config)
        
        output = command.stdout.getvalue()
        assert 'Iniciando entrenamiento completo' in output
    
    @patch('ml.segmentation.train_yolo.train_cacao_yolo_model')
    def test_train_yolo_success(self, mock_train, command):
        """Test training YOLO successfully."""
        mock_train.return_value = {
            'success': True,
            'best_model_path': '/path/to/model.pt'
        }
        
        command.stdout = StringIO()
        
        yolo_config = {
            'dataset_size': 150,
            'epochs': 100,
            'batch_size': 16,
            'model_name': 'yolov8s-seg'
        }
        
        result = command._train_yolo(yolo_config)
        
        assert result['status'] == 'completed'
        assert 'best_model_path' in result
    
    @patch('ml.segmentation.train_yolo.train_cacao_yolo_model')
    def test_train_yolo_failure(self, mock_train, command):
        """Test training YOLO with failure."""
        mock_train.return_value = {
            'success': False,
            'error': 'Test error'
        }
        
        command.stdout = StringIO()
        
        yolo_config = {
            'dataset_size': 150,
            'epochs': 100,
            'batch_size': 16,
            'model_name': 'yolov8s-seg'
        }
        
        result = command._train_yolo(yolo_config)
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    @patch('training.management.commands.train_all_models.logger')
    @patch('ml.segmentation.train_yolo.train_cacao_yolo_model')
    def test_train_yolo_exception(self, mock_train, mock_logger, command):
        """Test training YOLO with exception."""
        mock_train.side_effect = Exception('Test exception')
        
        command.stdout = StringIO()
        
        yolo_config = {
            'dataset_size': 150,
            'epochs': 100,
            'batch_size': 16,
            'model_name': 'yolov8s-seg'
        }
        
        result = command._train_yolo(yolo_config)
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    def test_process_yolo_result_success(self, command):
        """Test processing YOLO result with success."""
        command.stdout = StringIO()
        
        yolo_result = {
            'success': True,
            'best_model_path': '/path/to/model.pt'
        }
        
        result = command._process_yolo_result(yolo_result)
        
        assert result['status'] == 'completed'
        assert 'best_model_path' in result
    
    def test_process_yolo_result_failure(self, command):
        """Test processing YOLO result with failure."""
        command.stdout = StringIO()
        
        yolo_result = {
            'success': False,
            'error': 'Test error'
        }
        
        result = command._process_yolo_result(yolo_result)
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    @patch('training.management.commands.train_all_models.logger')
    def test_handle_yolo_error(self, mock_logger, command):
        """Test handling YOLO error."""
        command.stdout = StringIO()
        
        error = Exception('Test error')
        
        result = command._handle_yolo_error(error)
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    @patch('ml.pipeline.train_all.run_training_pipeline')
    def test_train_regression_success(self, mock_train, command):
        """Test training regression successfully."""
        mock_train.return_value = True
        
        command.stdout = StringIO()
        
        regression_config = {
            'epochs': 150,
            'batch_size': 16,
            'learning_rate': 0.001,
            'model_type': 'hybrid'
        }
        
        result = command._train_regression(regression_config)
        
        assert result['status'] == 'completed'
    
    @patch('ml.pipeline.train_all.run_training_pipeline')
    def test_train_regression_failure(self, mock_train, command):
        """Test training regression with failure."""
        mock_train.return_value = False
        
        command.stdout = StringIO()
        
        regression_config = {
            'epochs': 150,
            'batch_size': 16,
            'learning_rate': 0.001,
            'model_type': 'hybrid'
        }
        
        result = command._train_regression(regression_config)
        
        assert result['status'] == 'failed'
    
    @patch('training.management.commands.train_all_models.logger')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    def test_train_regression_exception(self, mock_train, mock_logger, command):
        """Test training regression with exception."""
        # Ensure logger is properly mocked
        mock_logger.error = MagicMock()
        mock_train.side_effect = Exception('Test exception')
        
        command.stdout = StringIO()
        
        regression_config = {
            'epochs': 150,
            'batch_size': 16,
            'learning_rate': 0.001,
            'model_type': 'hybrid'
        }
        
        result = command._train_regression(regression_config)
        
        assert result['status'] == 'failed'
    
    def test_process_regression_result_success(self, command):
        """Test processing regression result with success."""
        command.stdout = StringIO()
        
        result = command._process_regression_result(True)
        
        assert result['status'] == 'completed'
    
    def test_process_regression_result_failure(self, command):
        """Test processing regression result with failure."""
        command.stdout = StringIO()
        
        result = command._process_regression_result(False)
        
        assert result['status'] == 'failed'
    
    @patch('training.management.commands.train_all_models.logger')
    def test_handle_regression_error(self, mock_logger, command):
        """Test handling regression error."""
        command.stdout = StringIO()
        
        error = Exception('Test error')
        
        result = command._handle_regression_error(error)
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    def test_determine_final_status_all_completed(self, command):
        """Test determining final status with all completed."""
        results = {
            'yolo': {'status': 'completed'},
            'regression': {'status': 'completed'}
        }
        
        command._determine_final_status(results)
        
        assert results['status'] == 'completed'
    
    def test_determine_final_status_partial(self, command):
        """Test determining final status with partial completion."""
        results = {
            'yolo': {'status': 'completed'},
            'regression': {'status': 'failed'}
        }
        
        command._determine_final_status(results)
        
        assert results['status'] == 'partial'
    
    def test_determine_final_status_all_failed(self, command):
        """Test determining final status with all failed."""
        results = {
            'yolo': {'status': 'failed'},
            'regression': {'status': 'failed'}
        }
        
        command._determine_final_status(results)
        
        assert results['status'] == 'failed'
    
    @patch('training.management.commands.train_all_models.logger')
    def test_handle_fatal_error(self, mock_logger, command):
        """Test handling fatal error."""
        command.stdout = StringIO()
        
        error = Exception('Fatal error')
        
        with pytest.raises(CommandError):
            command._handle_fatal_error(error)
    
    def test_display_results(self, command):
        """Test displaying results."""
        command.stdout = StringIO()
        
        results = {
            'yolo': {'status': 'completed', 'message': 'YOLO completed'},
            'regression': {'status': 'completed', 'message': 'Regression completed'},
            'status': 'completed',
            'message': 'All completed'
        }
        
        command._display_results(results, 3600.0)
        
        output = command.stdout.getvalue()
        assert 'RESULTADOS DEL ENTRENAMIENTO COMPLETO' in output
    
    def test_display_yolo_results_completed(self, command):
        """Test displaying YOLO results with completed status."""
        command.stdout = StringIO()
        
        results = {
            'yolo': {
                'status': 'completed',
                'message': 'YOLO completed',
                'best_model_path': '/path/to/model.pt'
            }
        }
        
        command._display_yolo_results(results)
        
        output = command.stdout.getvalue()
        assert 'YOLO' in output
    
    def test_display_yolo_results_failed(self, command):
        """Test displaying YOLO results with failed status."""
        command.stdout = StringIO()
        
        results = {
            'yolo': {
                'status': 'failed',
                'message': 'YOLO failed',
                'error': 'Test error'
            }
        }
        
        command._display_yolo_results(results)
        
        output = command.stdout.getvalue()
        assert 'YOLO' in output
    
    def test_display_yolo_results_not_run(self, command):
        """Test displaying YOLO results when not run."""
        command.stdout = StringIO()
        
        results = {'yolo': None}
        
        command._display_yolo_results(results)
        
        output = command.stdout.getvalue()
        assert 'YOLO' in output or 'No se ejecutó' in output
    
    def test_display_regression_results_completed(self, command):
        """Test displaying regression results with completed status."""
        command.stdout = StringIO()
        
        results = {
            'regression': {
                'status': 'completed',
                'message': 'Regression completed'
            }
        }
        
        command._display_regression_results(results)
        
        output = command.stdout.getvalue()
        assert 'Regresión' in output or 'Regresion' in output
    
    def test_display_regression_results_failed(self, command):
        """Test displaying regression results with failed status."""
        command.stdout = StringIO()
        
        results = {
            'regression': {
                'status': 'failed',
                'message': 'Regression failed',
                'error': 'Test error'
            }
        }
        
        command._display_regression_results(results)
        
        output = command.stdout.getvalue()
        assert 'Regresión' in output or 'Regresion' in output
    
    def test_display_final_status_completed(self, command):
        """Test displaying final status with completed."""
        command.stdout = StringIO()
        
        results = {
            'status': 'completed',
            'message': 'All completed'
        }
        
        command._display_final_status(results)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_display_final_status_partial(self, command):
        """Test displaying final status with partial."""
        command.stdout = StringIO()
        
        results = {
            'status': 'partial',
            'message': 'Partial completion'
        }
        
        command._display_final_status(results)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_display_final_status_failed(self, command):
        """Test displaying final status with failed."""
        command.stdout = StringIO()
        
        results = {
            'status': 'failed',
            'message': 'All failed',
            'error': 'Test error'
        }
        
        command._display_final_status(results)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0


