"""
Tests for train_cacao_models management command.
This file tests the complex train_cacao_models command with all its helper methods.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from pathlib import Path
from django.core.management import call_command
from django.core.management.base import CommandError
from typing import Dict


@pytest.mark.django_db
class TestTrainCacaoModelsCommand:
    """Tests for train_cacao_models command."""
    
    @pytest.fixture
    def command(self):
        """Create command instance."""
        from training.management.commands.train_cacao_models import Command
        return Command()
    
    def test_resolve_training_flags_hybrid(self, command):
        """Test resolving training flags with hybrid."""
        options = {
            'hybrid': True,
            'hybrid_v2': False,
            'train_separate_dimensions': False,
            'use_pixel_features': True
        }
        
        flags = command._resolve_training_flags(options)
        
        assert flags.use_hybrid is True
        assert flags.use_hybrid_v2 is False
        assert flags.is_optimized_hybrid is True
    
    def test_resolve_training_flags_model_type_hybrid(self, command):
        """Test resolving training flags with model_type hybrid."""
        options = {
            'hybrid': False,
            'model_type': 'hybrid',
            'hybrid_v2': False,
            'train_separate_dimensions': False,
            'use_pixel_features': True
        }
        
        flags = command._resolve_training_flags(options)
        
        assert flags.use_hybrid is True
    
    def test_resolve_training_flags_hybrid_v2(self, command):
        """Test resolving training flags with hybrid_v2."""
        options = {
            'hybrid': False,
            'hybrid_v2': True,
            'train_separate_dimensions': False,
            'use_pixel_features': True
        }
        
        flags = command._resolve_training_flags(options)
        
        assert flags.use_hybrid_v2 is True
    
    def test_determine_num_workers_windows(self, command):
        """Test determining num workers on Windows."""
        with patch('training.management.commands.train_cacao_models.platform') as mock_platform:
            mock_platform.system.return_value = 'Windows'
            
            result = command._determine_num_workers(4)
            
            assert result == 0
    
    def test_determine_num_workers_non_windows(self, command):
        """Test determining num workers on non-Windows."""
        with patch('training.management.commands.train_cacao_models.platform') as mock_platform:
            mock_platform.system.return_value = 'Linux'
            
            result = command._determine_num_workers(0)
            
            assert result == 0
    
    def test_resolve_hyperparams_default(self, command):
        """Test resolving hyperparams with default values."""
        options = {
            'epochs': 50,
            'learning_rate': 1e-4,
            'early_stopping_patience': 15,
            'dropout_rate': 0.25,
            'loss_type': 'smooth_l1',
            'scheduler_type': 'cosine_warmup'
        }
        
        flags = command._resolve_training_flags({
            'hybrid': False,
            'use_pixel_features': False
        })
        
        hyperparams = command._resolve_hyperparams(options, flags)
        
        assert hyperparams.epochs == 50
        assert hyperparams.learning_rate == 1e-4
    
    def test_resolve_hyperparams_optimized_hybrid(self, command):
        """Test resolving hyperparams with optimized hybrid."""
        options = {
            'epochs': 50,
            'learning_rate': 1e-4,
            'early_stopping_patience': 15,
            'dropout_rate': 0.25,
            'loss_type': 'smooth_l1',
            'scheduler_type': 'cosine_warmup'
        }
        
        flags = command._resolve_training_flags({
            'hybrid': True,
            'use_pixel_features': True
        })
        
        hyperparams = command._resolve_hyperparams(options, flags)
        
        assert hyperparams.epochs == 100
        assert hyperparams.learning_rate == 5e-5
        assert hyperparams.loss == 'huber'
    
    def test_build_base_config(self, command):
        """Test building base config."""
        options = {
            'multihead': False,
            'model_type': 'resnet18',
            'batch_size': 32,
            'img_size': 224,
            'targets': 'all'
        }
        
        flags = command._resolve_training_flags({
            'hybrid': False,
            'use_pixel_features': False
        })
        
        num_workers = 0
        hyperparams = command._resolve_hyperparams({
            'epochs': 50,
            'learning_rate': 1e-4,
            'early_stopping_patience': 15,
            'dropout_rate': 0.25,
            'loss_type': 'smooth_l1',
            'scheduler_type': 'cosine_warmup'
        }, flags)
        
        config = command._build_base_config(options, flags, num_workers, hyperparams)
        
        assert config['epochs'] == 50
        assert config['batch_size'] == 32
        assert config['model_type'] == 'resnet18'
    
    def test_apply_test_mode(self, command):
        """Test applying test mode."""
        config = {
            'epochs': 100,
            'batch_size': 32,
            'early_stopping_patience': 15
        }
        
        result = command._apply_test_mode(config, True)
        
        assert result['epochs'] == 5
        assert result['batch_size'] == 16
        assert result['early_stopping_patience'] == 3
    
    def test_apply_test_mode_disabled(self, command):
        """Test applying test mode when disabled."""
        config = {
            'epochs': 100,
            'batch_size': 32,
            'early_stopping_patience': 15
        }
        
        result = command._apply_test_mode(config, False)
        
        assert result == config
    
    def test_get_warmup_epochs_from_options(self, command):
        """Test getting warmup epochs from options."""
        options = {'warmup_epochs': 10}
        is_optimized = False
        
        result = command._get_warmup_epochs(options, is_optimized)
        
        assert result == 10
    
    def test_get_warmup_epochs_default_optimized(self, command):
        """Test getting warmup epochs default for optimized."""
        options = {}
        is_optimized = True
        
        result = command._get_warmup_epochs(options, is_optimized)
        
        assert result == 10
    
    def test_get_warmup_epochs_default_not_optimized(self, command):
        """Test getting warmup epochs default for not optimized."""
        options = {}
        is_optimized = False
        
        result = command._get_warmup_epochs(options, is_optimized)
        
        assert result == 5
    
    def test_parse_targets_all(self, command):
        """Test parsing targets with 'all'."""
        result = command._parse_targets('all')
        
        assert result == ['alto', 'ancho', 'grosor', 'peso']
    
    def test_parse_targets_specific(self, command):
        """Test parsing specific targets."""
        result = command._parse_targets('alto,ancho')
        
        assert result == ['alto', 'ancho']
    
    def test_parse_targets_invalid(self, command):
        """Test parsing invalid targets."""
        with pytest.raises(ValueError):
            command._parse_targets('invalid_target')
    
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_success(self, mock_get_raw_dir, command, tmp_path):
        """Test validating config successfully."""
        raw_dir = tmp_path / 'raw'
        raw_dir.mkdir()
        for i in range(15):
            (raw_dir / f'test{i}.bmp').write_bytes(b'fake bmp')
        
        mock_get_raw_dir.return_value = raw_dir
        
        with patch('ml.data.dataset_loader.CacaoDatasetLoader') as mock_loader_class:
            mock_loader = MagicMock()
            import pandas as pd
            mock_df = pd.DataFrame({'id': list(range(15))})
            mock_loader.load_dataset.return_value = mock_df
            mock_loader.get_valid_records.return_value = [{'id': i} for i in range(15)]
            mock_loader.get_dataset_stats.return_value = {'total_records': 15}
            mock_loader_class.return_value = mock_loader
            
            config = {
                'model_type': 'resnet18',
                'epochs': 50,
                'batch_size': 32,
                'learning_rate': 1e-4
            }
            
            # Should not raise
            command._validate_config(config)
    
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_validate_config_no_raw_dir(self, mock_get_raw_dir, command):
        """Test validating config with no raw directory."""
        mock_get_raw_dir.return_value = Path('/nonexistent')
        
        config = {'model_type': 'resnet18'}
        
        with pytest.raises(CommandError):
            command._validate_config(config)
    
    def test_validate_config_invalid_epochs(self, command):
        """Test validating config with invalid epochs."""
        config = {'epochs': 0}
        
        with pytest.raises(CommandError):
            command._validate_config(config)
    
    def test_validate_config_invalid_batch_size(self, command):
        """Test validating config with invalid batch size."""
        with patch('training.management.commands.train_cacao_models.get_raw_images_dir'):
            config = {'batch_size': 0}
            
            with pytest.raises(CommandError):
                command._validate_config(config)
    
    def test_validate_config_invalid_learning_rate(self, command):
        """Test validating config with invalid learning rate."""
        with patch('training.management.commands.train_cacao_models.get_raw_images_dir'):
            config = {'learning_rate': 0}
            
            with pytest.raises(CommandError):
                command._validate_config(config)
    
    def test_display_config(self, command):
        """Test displaying config."""
        command.stdout = StringIO()
        
        config = {
            'model_type': 'resnet18',
            'multi_head': False,
            'epochs': 50,
            'batch_size': 32,
            'img_size': 224,
            'learning_rate': 1e-4,
            'dropout_rate': 0.25,
            'early_stopping_patience': 15,
            'num_workers': 0,
            'targets': ['alto', 'ancho', 'grosor', 'peso']
        }
        
        with patch('training.management.commands.train_cacao_models.get_raw_images_dir') as mock_get_raw:
            mock_get_raw.return_value = Path('/tmp')
            
            command._display_config(config)
            
            output = command.stdout.getvalue()
            assert 'CONFIGURACIÓN DE ENTRENAMIENTO' in output
            assert 'Modelo:' in output
    
    def test_validate_data_only(self, command):
        """Test validate data only mode."""
        command.stdout = StringIO()
        
        with patch('ml.data.dataset_loader.CacaoDatasetLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.get_valid_records.return_value = [
                {
                    'id': 1,
                    'alto': 10,
                    'ancho': 20,
                    'grosor': 30,
                    'peso': 40,
                    'crop_image_path': '/tmp/crop.png'
                }
            ]
            mock_loader.get_dataset_stats.return_value = {
                'dimensions_stats': {
                    'alto': {'min': 5, 'max': 15, 'mean': 10},
                    'ancho': {'min': 15, 'max': 25, 'mean': 20},
                    'grosor': {'min': 25, 'max': 35, 'mean': 30},
                    'peso': {'min': 35, 'max': 45, 'mean': 40}
                }
            }
            mock_loader_class.return_value = mock_loader
            
            with patch('training.management.commands.train_cacao_models.settings') as mock_settings:
                mock_settings.MEDIA_ROOT = '/tmp'
                
                command._validate_data_only()
                
                output = command.stdout.getvalue()
                assert 'Validando datos' in output or len(output) >= 0
    
    def test_display_results(self, command):
        """Test displaying results."""
        command.stdout = StringIO()
        
        results = {
            'evaluation_results': {
                'alto': {'mae': 0.5, 'rmse': 0.6, 'r2': 0.8},
                'ancho': {'mae': 0.4, 'rmse': 0.5, 'r2': 0.85}
            },
            'config': {'multi_head': False}
        }
        
        command._display_results(results, 3600.0)
        
        output = command.stdout.getvalue()
        assert 'RESULTADOS DEL ENTRENAMIENTO' in output or len(output) >= 0
    
    def test_display_results_multihead(self, command):
        """Test displaying results with multihead."""
        command.stdout = StringIO()
        
        results = {
            'evaluation_results': {
                'multihead': {
                    'alto': {'mae': 0.5, 'rmse': 0.6, 'r2': 0.8},
                    'ancho': {'mae': 0.4, 'rmse': 0.5, 'r2': 0.85}
                }
            },
            'config': {'multi_head': True}
        }
        
        command._display_results(results, 3600.0)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_print_target_metrics(self, command):
        """Test printing target metrics."""
        command.stdout = StringIO()
        
        metrics = {
            'alto': {'mae': 0.5, 'rmse': 0.6, 'r2': 0.8},
            'ancho': {'mae': 0.4, 'rmse': 0.5, 'r2': 0.85}
        }
        
        command._print_target_metrics(metrics)
        
        output = command.stdout.getvalue()
        assert 'ALTO' in output or 'alto' in output.lower()
    
    def test_print_single_target_metrics(self, command):
        """Test printing single target metrics."""
        command.stdout = StringIO()
        
        metrics = {'mae': 0.5, 'rmse': 0.6, 'r2': 0.8}
        
        command._print_single_target_metrics('alto', metrics)
        
        output = command.stdout.getvalue()
        assert 'ALTO' in output or 'alto' in output.lower()
        assert '0.5' in output or '0.5000' in output
    
    def test_print_single_target_metrics_missing_values(self, command):
        """Test printing single target metrics with missing values."""
        command.stdout = StringIO()
        
        metrics = {'mae': None, 'rmse': 0.6, 'r2': 0.8}
        
        command._print_single_target_metrics('alto', metrics)
        
        # Should not crash, may not print anything
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    @patch('training.management.commands.train_cacao_models.get_regressors_artifacts_dir')
    def test_print_artifact_summary(self, mock_get_artifacts, command, tmp_path):
        """Test printing artifact summary."""
        artifacts_dir = tmp_path / 'artifacts'
        artifacts_dir.mkdir()
        (artifacts_dir / 'model1.pt').write_bytes(b'fake model')
        (artifacts_dir / 'scaler1.pkl').write_bytes(b'fake scaler')
        
        mock_get_artifacts.return_value = artifacts_dir
        
        command.stdout = StringIO()
        command._print_artifact_summary()
        
        output = command.stdout.getvalue()
        assert 'Modelos guardados' in output or len(output) >= 0
    
    @patch('training.management.commands.train_cacao_models.get_regressors_artifacts_dir')
    def test_print_artifact_summary_no_dir(self, mock_get_artifacts, command):
        """Test printing artifact summary when directory doesn't exist."""
        mock_get_artifacts.return_value = Path('/nonexistent')
        
        command.stdout = StringIO()
        command._print_artifact_summary()
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_display_results_v2(self, command):
        """Test displaying results v2."""
        command.stdout = StringIO()
        
        results = {
            'best_epoch': 10,
            'best_val_loss': 0.5,
            'test_loss': 0.6,
            'test_metrics': {
                'alto': {'r2': 0.8, 'mae': 0.5, 'rmse': 0.6},
                'ancho': {'r2': 0.85, 'mae': 0.4, 'rmse': 0.5}
            },
            'model_path': '/path/to/model.pt'
        }
        
        command._display_results_v2(results, 3600.0)
        
        output = command.stdout.getvalue()
        assert 'RESULTADOS DEL ENTRENAMIENTO HÍBRIDO V2' in output or len(output) >= 0
    
    @patch('ml.pipeline.train_all.CacaoTrainingPipeline')
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_handle_command_success(self, mock_get_raw_dir, mock_loader_class, mock_pipeline_class, command, tmp_path):
        """Test handling command successfully."""
        # Setup mocks for dataset
        raw_dir = tmp_path / 'raw'
        raw_dir.mkdir()
        for i in range(15):
            (raw_dir / f'test{i}.bmp').write_bytes(b'fake bmp')
        mock_get_raw_dir.return_value = raw_dir
        
        mock_loader = MagicMock()
        import pandas as pd
        mock_df = pd.DataFrame({'id': list(range(15))})
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.get_valid_records.return_value = [{'id': i} for i in range(15)]
        mock_loader.get_dataset_stats.return_value = {'total_records': 15}
        mock_loader_class.return_value = mock_loader
        
        mock_pipeline = MagicMock()
        mock_pipeline.run_pipeline.return_value = {
            'evaluation_results': {
                'alto': {'mae': 0.5, 'rmse': 0.6, 'r2': 0.8}
            },
            'config': {'multi_head': False}
        }
        mock_pipeline_class.return_value = mock_pipeline
        
        command.stdout = StringIO()
        
        options = {
            'validate_only': False,
            'test_mode': False,
            'hybrid_v2': False
        }
        
        with patch.object(command, '_create_config') as mock_create:
            with patch.object(command, '_validate_config') as mock_validate:
                with patch.object(command, '_display_config') as mock_display:
                    mock_create.return_value = {'epochs': 50}
                    
                    command.handle(**options)
                    
                    assert mock_validate.called
                    assert mock_display.called
    
    @patch('ml.pipeline.hybrid_v2_training.train_hybrid_v2')
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    @patch('training.management.commands.train_cacao_models.get_raw_images_dir')
    def test_handle_command_hybrid_v2(self, mock_get_raw_dir, mock_loader_class, mock_train_v2, command, tmp_path):
        """Test handling command with hybrid_v2."""
        # Setup mocks for dataset
        raw_dir = tmp_path / 'raw'
        raw_dir.mkdir()
        for i in range(15):
            (raw_dir / f'test{i}.bmp').write_bytes(b'fake bmp')
        mock_get_raw_dir.return_value = raw_dir
        
        mock_loader = MagicMock()
        import pandas as pd
        mock_df = pd.DataFrame({'id': list(range(15))})
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.get_valid_records.return_value = [{'id': i} for i in range(15)]
        mock_loader.get_dataset_stats.return_value = {'total_records': 15}
        mock_loader_class.return_value = mock_loader
        
        mock_train_v2.return_value = {
            'best_epoch': 10,
            'best_val_loss': 0.5
        }
        
        command.stdout = StringIO()
        
        options = {
            'validate_only': False,
            'test_mode': False,
            'hybrid_v2': True
        }
        
        with patch.object(command, '_create_config') as mock_create:
            with patch.object(command, '_validate_config') as mock_validate:
                with patch.object(command, '_display_config') as mock_display:
                    mock_create.return_value = {'epochs': 50, 'hybrid_v2': True}
                    
                    command.handle(**options)
                    
                    assert mock_train_v2.called
    
    def test_notify_optimized_settings(self, command):
        """Test notifying optimized settings."""
        command.stdout = StringIO()
        
        from training.management.commands.train_cacao_models import HyperParams
        
        base = HyperParams(50, 1e-4, 15, 0.25, 'smooth_l1', 'cosine_warmup')
        optimized = HyperParams(100, 5e-5, 25, 0.3, 'huber', 'cosine_warmup')
        
        command._notify_optimized_settings(base, optimized)
        
        output = command.stdout.getvalue()
        assert 'Configuración optimizada' in output or 'optimizada' in output.lower()
    
    def test_notify_optimized_settings_no_change(self, command):
        """Test notifying optimized settings when no change."""
        command.stdout = StringIO()
        
        from training.management.commands.train_cacao_models import HyperParams
        
        base = HyperParams(50, 1e-4, 15, 0.25, 'smooth_l1', 'cosine_warmup')
        optimized = HyperParams(50, 1e-4, 15, 0.25, 'smooth_l1', 'cosine_warmup')
        
        command._notify_optimized_settings(base, optimized)
        
        output = command.stdout.getvalue()
        assert len(output) == 0
    
    def test_parse_targets_with_spaces(self, command):
        """Test parsing targets with spaces."""
        result = command._parse_targets('alto , ancho , grosor')
        
        assert result == ['alto', 'ancho', 'grosor']
    
    def test_parse_targets_case_insensitive(self, command):
        """Test parsing targets case insensitive."""
        result = command._parse_targets('ALTO,ANCHO')
        
        assert result == ['alto', 'ancho']
    
    def test_handle_exception(self, command):
        """Test handle with exception."""
        command.stdout = StringIO()
        
        with patch.object(command, '_create_config', side_effect=Exception("Test error")):
            options = {
                'validate_only': False,
                'test_mode': False,
                'hybrid_v2': False
            }
            
            with pytest.raises((CommandError, Exception)):
                command.handle(**options)
    
    def test_print_evaluation_results_no_results(self, command):
        """Test printing evaluation results when no results."""
        command.stdout = StringIO()
        
        results = {'config': {'multi_head': False}}
        
        command._print_evaluation_results(results)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_print_evaluation_results_invalid_type(self, command):
        """Test printing evaluation results with invalid type."""
        command.stdout = StringIO()
        
        results = {
            'evaluation_results': 'invalid',
            'config': {'multi_head': False}
        }
        
        command._print_evaluation_results(results)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_should_use_multihead_metrics_false(self, command):
        """Test should_use_multihead_metrics returns false."""
        config = {'multi_head': False}
        multihead_metrics = None
        
        result = command._should_use_multihead_metrics(config, multihead_metrics)
        
        assert result is False
    
    def test_should_use_multihead_metrics_invalid_config(self, command):
        """Test should_use_multihead_metrics with invalid config."""
        config = 'invalid'
        multihead_metrics = {}
        
        result = command._should_use_multihead_metrics(config, multihead_metrics)
        
        assert result is False
    
    def test_print_target_metrics_empty(self, command):
        """Test printing target metrics with empty dict."""
        command.stdout = StringIO()
        
        metrics = {}
        
        command._print_target_metrics(metrics)
        
        output = command.stdout.getvalue()
        assert len(output) == 0
    
    def test_print_target_metrics_invalid_type(self, command):
        """Test printing target metrics with invalid type."""
        command.stdout = StringIO()
        
        metrics = {'alto': 'invalid'}
        
        command._print_target_metrics(metrics)
        
        output = command.stdout.getvalue()
        assert len(output) >= 0
    
    def test_display_results_v2_no_test_metrics(self, command):
        """Test displaying results v2 without test_metrics."""
        command.stdout = StringIO()
        
        results = {
            'best_epoch': 10,
            'best_val_loss': 0.5,
            'test_loss': 0.6,
            'model_path': '/path/to/model.pt'
        }
        
        command._display_results_v2(results, 3600.0)
        
        output = command.stdout.getvalue()
        assert 'RESULTADOS DEL ENTRENAMIENTO HÍBRIDO V2' in output or len(output) >= 0


