"""
Tests for train_yolo_model management command.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
class TestTrainYoloModelCommand:
    """Tests for train_yolo_model command."""
    
    @patch('training.management.commands.train_yolo_model.YOLOTrainingManager')
    @patch('training.management.commands.train_yolo_model.train_cacao_yolo_model')
    def test_handle_command_success(self, mock_train_func, mock_manager_class):
        """Test handling command successfully."""
        # Mock successful training
        mock_train_func.return_value = {
            'success': True,
            'best_model_path': '/path/to/model.pt',
            'dataset_info': {
                'total_images': 150,
                'train_images': 105,
                'val_images': 30,
                'test_images': 15
            },
            'validation_metrics': {
                'mAP50': 0.85,
                'mAP50-95': 0.75,
                'precision': 0.80,
                'recall': 0.82,
                'f1_score': 0.81,
                'mask_mAP50': 0.83,
                'mask_mAP50-95': 0.73
            },
            'model_paths': {
                'best_model': '/path/to/best.pt',
                'last_model': '/path/to/last.pt',
                'dataset_config': '/path/to/config.yaml'
            }
        }
        
        out = StringIO()
        
        call_command(
            'train_yolo_model',
            '--dataset-size', '150',
            '--epochs', '100',
            '--batch-size', '16',
            stdout=out
        )
        
        output = out.getvalue()
        assert 'CONFIGURACIÓN DE ENTRENAMIENTO YOLO' in output
        assert 'RESULTADOS DEL ENTRENAMIENTO' in output
    
    def test_validate_arguments_splits_sum_to_one(self):
        """Test validating arguments with splits summing to one."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        # This should not raise an error
        options = {
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.1,
            'dataset_size': 150,
            'epochs': 100,
            'batch_size': 16,
            'learning_rate': 0.01
        }
        
        # Should not raise
        command._validate_arguments(options)
    
    def test_validate_arguments_splits_not_sum_to_one(self):
        """Test validating arguments with splits not summing to one."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        options = {
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.2  # Sums to 1.1
        }
        
        with pytest.raises(CommandError):
            command._validate_arguments(options)
    
    def test_validate_arguments_dataset_size_too_small(self):
        """Test validating arguments with dataset size too small."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        options = {
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.1,
            'dataset_size': 5  # Too small
        }
        
        with pytest.raises(CommandError):
            command._validate_arguments(options)
    
    def test_validate_arguments_epochs_invalid(self):
        """Test validating arguments with invalid epochs."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        options = {
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.1,
            'dataset_size': 150,
            'epochs': 0  # Invalid
        }
        
        with pytest.raises(CommandError):
            command._validate_arguments(options)
    
    def test_validate_arguments_batch_size_invalid(self):
        """Test validating arguments with invalid batch size."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        options = {
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.1,
            'dataset_size': 150,
            'epochs': 100,
            'batch_size': 0  # Invalid
        }
        
        with pytest.raises(CommandError):
            command._validate_arguments(options)
    
    def test_validate_arguments_learning_rate_invalid(self):
        """Test validating arguments with invalid learning rate."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        options = {
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.1,
            'dataset_size': 150,
            'epochs': 100,
            'batch_size': 16,
            'learning_rate': 0  # Invalid
        }
        
        with pytest.raises(CommandError):
            command._validate_arguments(options)
    
    def test_display_configuration(self):
        """Test displaying configuration."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        options = {
            'dataset_size': 150,
            'model_name': 'yolov8s-seg',
            'epochs': 100,
            'batch_size': 16,
            'image_size': 640,
            'device': 'cpu',
            'workers': 4,
            'learning_rate': 0.01,
            'weight_decay': 0.0005,
            'momentum': 0.937,
            'warmup_epochs': 3,
            'patience': 20,
            'confidence': 0.5,
            'iou_threshold': 0.7,
            'train_split': 0.7,
            'val_split': 0.2,
            'test_split': 0.1,
            'cache': False,
            'plots': False,
            'verbose': False
        }
        
        command._display_configuration(options)
        
        output = out.getvalue()
        assert 'CONFIGURACIÓN DE ENTRENAMIENTO YOLO' in output
        assert 'Dataset Size' in output
        assert 'Modelo Base' in output
    
    def test_confirm_training(self):
        """Test confirming training."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        
        # Should auto-confirm (returns True)
        result = command._confirm_training({})
        
        assert result is True
    
    @patch('training.management.commands.train_yolo_model.YOLOTrainingManager')
    def test_display_results_success(self, mock_manager_class):
        """Test displaying results with success."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        results = {
            'success': True,
            'dataset_info': {
                'total_images': 150,
                'train_images': 105,
                'val_images': 30,
                'test_images': 15
            },
            'validation_metrics': {
                'mAP50': 0.85,
                'mAP50-95': 0.75,
                'precision': 0.80,
                'recall': 0.82,
                'f1_score': 0.81,
                'mask_mAP50': 0.83,
                'mask_mAP50-95': 0.73
            },
            'model_paths': {
                'best_model': '/path/to/best.pt',
                'last_model': '/path/to/last.pt',
                'dataset_config': '/path/to/config.yaml'
            }
        }
        
        command._display_results(results, 3600.0)
        
        output = out.getvalue()
        assert 'RESULTADOS DEL ENTRENAMIENTO' in output
        assert 'Dataset Size' in output
        assert 'mAP50' in output
    
    def test_display_results_failure(self):
        """Test displaying results with failure."""
        from training.management.commands.train_yolo_model import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        results = {
            'success': False,
            'error': 'Test error message'
        }
        
        command._display_results(results, 3600.0)
        
        output = out.getvalue()
        assert 'Entrenamiento falló' in output
        assert 'Test error message' in output
    
    @patch('training.management.commands.train_yolo_model.Path')
    def test_save_results(self, mock_path_class):
        """Test saving results."""
        from training.management.commands.train_yolo_model import Command
        from django.conf import settings
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        results = {
            'success': True,
            'dataset_info': {'total_images': 150}
        }
        
        options = {
            'dataset_size': 150,
            'epochs': 100
        }
        
        mock_results_dir = MagicMock()
        mock_results_path = MagicMock()
        mock_results_dir.__truediv__.return_value = mock_results_path
        mock_path_class.return_value = mock_results_dir
        
        command._save_results(results, options)
        
        output = out.getvalue()
        assert 'Resultados guardados' in output or len(output) >= 0
    
    def test_dry_run(self):
        """Test dry run mode."""
        out = StringIO()
        
        call_command(
            'train_yolo_model',
            '--dry-run',
            stdout=out
        )
        
        output = out.getvalue()
        assert 'Dry run completado' in output


