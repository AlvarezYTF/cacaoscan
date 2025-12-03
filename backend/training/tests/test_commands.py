"""
Tests for Training Management Commands.
"""
import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError

from training.management.commands.train_all_models import Command as TrainAllCommand
from training.management.commands.train_cacao_models import Command as TrainCacaoCommand
from training.management.commands.train_unet_background import Command as TrainUNetCommand
from training.management.commands.train_yolo_model import Command as TrainYOLOCommand


@pytest.mark.django_db
class TestTrainAllModelsCommand:
    """Tests for train_all_models command."""

    def test_command_help(self):
        """Test command help text."""
        command = TrainAllCommand()
        assert 'Entrena todos los modelos' in command.help

    def test_add_arguments(self):
        """Test that command adds all required arguments."""
        from argparse import ArgumentParser
        
        command = TrainAllCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        # Check that arguments are added
        args = parser.parse_args([
            '--yolo-dataset-size', '100',
            '--yolo-epochs', '50',
            '--regression-epochs', '100'
        ])
        
        assert args.yolo_dataset_size == 100
        assert args.yolo_epochs == 50
        assert args.regression_epochs == 100

    def test_determine_hybrid_mode_hybrid_flag(self):
        """Test determining hybrid mode from hybrid flag."""
        command = TrainAllCommand()
        options = {
            'regression_hybrid': True,
            'regression_model_type': 'resnet18'
        }
        
        assert command._determine_hybrid_mode(options) is True

    def test_determine_hybrid_mode_model_type(self):
        """Test determining hybrid mode from model type."""
        command = TrainAllCommand()
        options = {
            'regression_hybrid': False,
            'regression_model_type': 'hybrid'
        }
        
        assert command._determine_hybrid_mode(options) is True

    def test_prepare_yolo_config(self):
        """Test preparing YOLO configuration."""
        command = TrainAllCommand()
        options = {
            'yolo_dataset_size': 100,
            'yolo_epochs': 50,
            'yolo_batch_size': 16,
            'yolo_model_name': 'yolov8s-seg'
        }
        
        config = command._prepare_yolo_config(options)
        
        assert config['dataset_size'] == 100
        assert config['epochs'] == 50
        assert config['batch_size'] == 16
        assert config['model_name'] == 'yolov8s-seg'

    def test_prepare_regression_config(self):
        """Test preparing regression configuration."""
        command = TrainAllCommand()
        options = {
            'regression_epochs': 100,
            'regression_batch_size': 32,
            'regression_learning_rate': 0.001,
            'regression_model_type': 'hybrid',
            'regression_use_pixel_features': True
        }
        
        config = command._prepare_regression_config(options, is_hybrid=True)
        
        assert config['epochs'] == 100
        assert config['model_type'] == 'hybrid'
        assert config['hybrid'] is True
        assert config['use_pixel_features'] is True


@pytest.mark.django_db
class TestTrainCacaoModelsCommand:
    """Tests for train_cacao_models command."""

    def test_command_help(self):
        """Test command help text."""
        command = TrainCacaoCommand()
        assert 'Entrena modelos de regresión' in command.help

    def test_add_arguments(self):
        """Test that command adds all required arguments."""
        from argparse import ArgumentParser
        
        command = TrainCacaoCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        # Check that arguments are added
        args = parser.parse_args([
            '--epochs', '50',
            '--batch-size', '32',
            '--model-type', 'hybrid',
            '--hybrid'
        ])
        
        assert args.epochs == 50
        assert args.batch_size == 32
        assert args.model_type == 'hybrid'
        assert args.hybrid is True

    def test_validate_arguments_epochs_positive(self):
        """Test validation of epochs argument."""
        from argparse import ArgumentParser
        
        command = TrainCacaoCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        # Should accept positive epochs
        args = parser.parse_args(['--epochs', '50'])
        assert args.epochs == 50

    def test_validate_arguments_model_type_choices(self):
        """Test validation of model type choices."""
        from argparse import ArgumentParser
        
        command = TrainCacaoCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        # Should accept valid choices
        for model_type in ['resnet18', 'convnext_tiny', 'hybrid']:
            args = parser.parse_args(['--model-type', model_type])
            assert args.model_type == model_type


@pytest.mark.django_db
class TestTrainUNetCommand:
    """Tests for train_unet_background command."""

    def test_command_help(self):
        """Test command help text."""
        command = TrainUNetCommand()
        assert 'Entrena modelo U-Net' in command.help

    def test_add_arguments(self):
        """Test that command adds all required arguments."""
        from argparse import ArgumentParser
        
        command = TrainUNetCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        args = parser.parse_args([
            '--epochs', '20',
            '--batch-size', '4',
            '--learning-rate', '0.0001',
            '--force'
        ])
        
        assert args.epochs == 20
        assert args.batch_size == 4
        assert args.learning_rate == 0.0001
        assert args.force is True

    def test_check_existing_model_no_force(self, tmp_path):
        """Test checking existing model when not forcing."""
        with patch('training.management.commands.train_unet_background.get_project_root', return_value=tmp_path):
            command = TrainUNetCommand()
            
            # Create model file
            model_dir = tmp_path / "ml" / "segmentation"
            model_dir.mkdir(parents=True)
            model_path = model_dir / "cacao_unet.pth"
            model_path.write_bytes(b'fake model')
            
            options = {'force': False}
            result = command._check_existing_model(options)
            
            assert result == model_path

    def test_check_existing_model_with_force(self, tmp_path):
        """Test checking existing model when forcing."""
        with patch('training.management.commands.train_unet_background.get_project_root', return_value=tmp_path):
            command = TrainUNetCommand()
            
            # Create model file
            model_dir = tmp_path / "ml" / "segmentation"
            model_dir.mkdir(parents=True)
            model_path = model_dir / "cacao_unet.pth"
            model_path.write_bytes(b'fake model')
            
            options = {'force': True}
            result = command._check_existing_model(options)
            
            assert result is None


@pytest.mark.django_db
class TestTrainYOLOModelCommand:
    """Tests for train_yolo_model command."""

    def test_command_help(self):
        """Test command help text."""
        command = TrainYOLOCommand()
        assert 'Entrena modelo YOLOv8-seg' in command.help

    def test_add_arguments(self):
        """Test that command adds all required arguments."""
        from argparse import ArgumentParser
        
        command = TrainYOLOCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        args = parser.parse_args([
            '--dataset-size', '150',
            '--epochs', '100',
            '--batch-size', '16',
            '--model-name', 'yolov8s-seg',
            '--device', 'cpu'
        ])
        
        assert args.dataset_size == 150
        assert args.epochs == 100
        assert args.batch_size == 16
        assert args.model_name == 'yolov8s-seg'
        assert args.device == 'cpu'

    def test_validate_model_name_choices(self):
        """Test validation of model name choices."""
        from argparse import ArgumentParser
        
        command = TrainYOLOCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        valid_models = ['yolov8n-seg', 'yolov8s-seg', 'yolov8m-seg', 'yolov8l-seg', 'yolov8x-seg']
        for model_name in valid_models:
            args = parser.parse_args(['--model-name', model_name])
            assert args.model_name == model_name

    def test_validate_device_choices(self):
        """Test validation of device choices."""
        from argparse import ArgumentParser
        
        command = TrainYOLOCommand()
        parser = ArgumentParser()
        command.add_arguments(parser)
        
        for device in ['cpu', 'cuda', 'auto']:
            args = parser.parse_args(['--device', device])
            assert args.device == device

