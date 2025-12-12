"""
Tests for train.py regression training module.
This file tests the regression training functions and classes.
"""
import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

from ml.regression.train import (
    RegressionTrainer,
    train_single_model,
    _create_loss_function,
    _validate_learning_rate,
    _create_optimizer_with_loss_params,
    _create_scheduler,
    _split_targets,
    _split_outputs,
    _prepare_batch_data,
    _compute_loss,
    _train_one_epoch,
    _validate_one_epoch,
    _compute_validation_metrics,
    _update_history_with_metrics,
    _build_metrics_log_string,
    _log_detailed_metrics_if_needed,
    _calculate_and_log_metrics,
    _update_scheduler,
    _check_early_stopping,
    _save_model_file,
    _save_metrics_to_db,
    _try_use_improved_training,
    _detect_model_type,
    _initialize_training_components,
    _initialize_history,
    train_multi_head_model,
    get_device,
    create_training_job,
    update_training_job_metrics,
    TARGETS,
)


@pytest.fixture
def device():
    """Get device for testing."""
    return torch.device('cpu')


@pytest.fixture
def sample_model(device):
    """Create sample model for testing."""
    model = nn.Sequential(
        nn.Linear(10, 5),
        nn.Linear(5, 4)
    )
    return model.to(device)


@pytest.fixture
def sample_scalers():
    """Create sample scalers for testing."""
    from ml.regression.scalers import CacaoScalers
    
    scalers = CacaoScalers()
    scalers.is_fitted = True
    scalers.inverse_transform = MagicMock(return_value={
        'alto': np.array([10.0]),
        'ancho': np.array([20.0]),
        'grosor': np.array([30.0]),
        'peso': np.array([40.0])
    })
    return scalers


@pytest.fixture
def sample_data_loaders(device):
    """Create sample data loaders for testing."""
    train_data = TensorDataset(
        torch.randn(10, 3, 224, 224),
        torch.randn(10, 4)
    )
    val_data = TensorDataset(
        torch.randn(5, 3, 224, 224),
        torch.randn(5, 4)
    )
    
    train_loader = DataLoader(train_data, batch_size=2)
    val_loader = DataLoader(val_data, batch_size=2)
    
    return train_loader, val_loader


class TestRegressionTrainer:
    """Tests for RegressionTrainer class."""
    
    def test_regression_trainer_init(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test initializing RegressionTrainer."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 10
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        assert trainer.model == sample_model
        assert trainer.target == 'alto'
        assert trainer.device == device
    
    def test_regression_trainer_init_high_learning_rate(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test initializing RegressionTrainer with high learning rate."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-3,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 10
        }
        
        with patch('ml.regression.train.logger') as mock_logger:
            trainer = RegressionTrainer(
                sample_model,
                train_loader,
                val_loader,
                sample_scalers,
                'alto',
                device,
                config
            )
            
            assert trainer.optimizer.param_groups[0]['lr'] == 5e-4
            mock_logger.warning.assert_called()
    
    def test_regression_trainer_train_epoch(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test training one epoch."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 10
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        loss = trainer.train_epoch()
        
        assert isinstance(loss, float)
        assert loss >= 0
    
    def test_regression_trainer_validate_epoch(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test validating one epoch."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 10
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        val_loss, mae, rmse, r2 = trainer.validate_epoch()
        
        assert isinstance(val_loss, float)
        assert isinstance(mae, float)
        assert isinstance(rmse, float)
        assert isinstance(r2, float)
    
    def test_regression_trainer_validate_epoch_empty_loader(self, sample_model, sample_scalers, device):
        """Test validating epoch with empty loader."""
        empty_data = TensorDataset(torch.randn(0, 3, 224, 224), torch.randn(0, 4))
        empty_loader = DataLoader(empty_data, batch_size=2)
        
        train_loader, _ = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 10
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            empty_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        val_loss, mae, rmse, r2 = trainer.validate_epoch()
        
        assert val_loss == 0.0
        assert mae == 0.0
        assert rmse == 0.0
        assert r2 == 0.0
    
    def test_regression_trainer_train(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test training full model."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 2,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 10,
            'improvement_threshold': 1e-4
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        history = trainer.train()
        
        assert 'train_loss' in history
        assert 'val_loss' in history
        assert len(history['train_loss']) == 2
    
    def test_regression_trainer_train_early_stopping(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test training with early stopping."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'weight_decay': 1e-4,
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'loss_type': 'smooth_l1',
            'max_grad_norm': 1.0,
            'early_stopping_patience': 1,
            'improvement_threshold': 1e-4
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        # Mock validate_epoch to return increasing loss
        original_validate = trainer.validate_epoch
        call_count = [0]
        def mock_validate():
            call_count[0] += 1
            if call_count[0] == 1:
                return 0.5, 0.3, 0.4, 0.8
            else:
                return 0.6, 0.4, 0.5, 0.7  # Worse loss
        
        trainer.validate_epoch = mock_validate
        
        history = trainer.train()
        
        # Should stop early due to patience
        assert len(history['train_loss']) <= 3
    
    def test_regression_trainer_convert_to_native_types(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test converting to native types."""
        train_loader, val_loader = sample_data_loaders
        config = {'learning_rate': 1e-4, 'epochs': 50}
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        # Test numpy integer
        result = trainer._convert_to_native_types(np.int32(5))
        assert isinstance(result, float)
        
        # Test numpy float
        result = trainer._convert_to_native_types(np.float32(5.5))
        assert isinstance(result, float)
        
        # Test torch tensor
        result = trainer._convert_to_native_types(torch.tensor(5.5))
        assert isinstance(result, float)
        
        # Test dict
        result = trainer._convert_to_native_types({'key': np.int32(5)})
        assert isinstance(result, dict)
        assert isinstance(result['key'], float)
        
        # Test list
        result = trainer._convert_to_native_types([np.int32(5), np.float32(5.5)])
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)
    
    @patch('ml.regression.train.DJANGO_LOADED', True)
    @patch('ml.regression.train.ModelMetrics')
    @patch('ml.regression.train.User')
    def test_regression_trainer_save_metrics_to_db(self, mock_user, mock_metrics, sample_model, sample_data_loaders, sample_scalers, device):
        """Test saving metrics to database."""
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'epochs': 50,
            'model_type': 'resnet18',
            'pretrained': True,
            'dropout_rate': 0.2
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        trainer.history = {
            'val_mae': [0.5],
            'val_loss': [0.4],
            'val_rmse': [0.6],
            'val_r2': [0.8]
        }
        
        mock_user.objects.filter.return_value.first.return_value = MagicMock()
        mock_metrics.objects.create.return_value = MagicMock()
        
        dataset_info = {
            'train_size': 100,
            'val_size': 20,
            'test_size': 10
        }
        
        trainer.save_metrics_to_db(None, dataset_info)
        
        mock_metrics.objects.create.assert_called_once()
    
    @patch('ml.regression.train.DJANGO_LOADED', False)
    def test_regression_trainer_save_metrics_to_db_no_django(self, sample_model, sample_data_loaders, sample_scalers, device):
        """Test saving metrics to database when Django not loaded."""
        train_loader, val_loader = sample_data_loaders
        config = {'learning_rate': 1e-4, 'epochs': 50}
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        with patch('ml.regression.train.logger') as mock_logger:
            trainer.save_metrics_to_db(None, None)
            
            mock_logger.warning.assert_called()
    
    @patch('ml.regression.train.get_regressors_artifacts_dir')
    @patch('ml.regression.train.ensure_dir_exists')
    def test_regression_trainer_save_model(self, mock_ensure, mock_get_artifacts, sample_model, sample_data_loaders, sample_scalers, device, tmp_path):
        """Test saving model."""
        artifacts_dir = tmp_path / 'artifacts'
        artifacts_dir.mkdir()
        mock_get_artifacts.return_value = artifacts_dir
        
        train_loader, val_loader = sample_data_loaders
        config = {
            'learning_rate': 1e-4,
            'epochs': 50,
            'model_type': 'resnet18'
        }
        
        trainer = RegressionTrainer(
            sample_model,
            train_loader,
            val_loader,
            sample_scalers,
            'alto',
            device,
            config
        )
        
        model_path = artifacts_dir / 'alto.pt'
        trainer.save_model(model_path)
        
        assert model_path.exists()


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_create_loss_function_mse(self):
        """Test creating MSE loss function."""
        criterion = _create_loss_function('mse')
        assert isinstance(criterion, nn.MSELoss)
    
    def test_create_loss_function_huber(self):
        """Test creating Huber loss function."""
        criterion = _create_loss_function('huber')
        assert isinstance(criterion, nn.HuberLoss)
    
    def test_create_loss_function_smooth_l1(self):
        """Test creating SmoothL1 loss function."""
        criterion = _create_loss_function('smooth_l1')
        assert isinstance(criterion, nn.SmoothL1Loss)
    
    def test_validate_learning_rate_valid(self):
        """Test validating valid learning rate."""
        with patch('ml.regression.train.logger'):
            result = _validate_learning_rate(1e-4)
            assert result == 1e-4
    
    def test_validate_learning_rate_too_high(self):
        """Test validating learning rate that's too high."""
        with patch('ml.regression.train.logger') as mock_logger:
            result = _validate_learning_rate(1e-3)
            assert result == 5e-4
            mock_logger.warning.assert_called()
    
    def test_create_optimizer_with_loss_params_with_params(self, device):
        """Test creating optimizer with loss parameters."""
        model = nn.Linear(10, 4)
        criterion = MagicMock()
        criterion.parameters.return_value = [torch.nn.Parameter(torch.tensor([0.3]))]
        
        config = {'weight_decay': 1e-4}
        learning_rate = 1e-4
        
        optimizer = _create_optimizer_with_loss_params(model, criterion, learning_rate, config)
        
        assert isinstance(optimizer, torch.optim.AdamW)
        assert len(optimizer.param_groups) == 2
    
    def test_create_optimizer_with_loss_params_no_params(self, device):
        """Test creating optimizer without loss parameters."""
        model = nn.Linear(10, 4)
        criterion = nn.MSELoss()
        
        config = {'weight_decay': 1e-4}
        learning_rate = 1e-4
        
        optimizer = _create_optimizer_with_loss_params(model, criterion, learning_rate, config)
        
        assert isinstance(optimizer, torch.optim.AdamW)
        assert len(optimizer.param_groups) == 1
    
    def test_create_scheduler_reduce_on_plateau(self):
        """Test creating ReduceLROnPlateau scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        config = {'min_lr': 1e-7}
        
        scheduler = _create_scheduler(optimizer, 'reduce_on_plateau', 50, config)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau)
    
    def test_create_scheduler_cosine(self):
        """Test creating CosineAnnealingLR scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        config = {'min_lr': 1e-6}
        
        scheduler = _create_scheduler(optimizer, 'cosine', 50, config)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.CosineAnnealingLR)
    
    def test_create_scheduler_cosine_warmup(self):
        """Test creating CosineAnnealingWarmRestarts scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        config = {'min_lr': 1e-7}
        
        scheduler = _create_scheduler(optimizer, 'cosine_warmup', 50, config)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.CosineAnnealingWarmRestarts)
    
    def test_split_targets_dict(self, device):
        """Test splitting targets from dict."""
        targets = {
            'alto': torch.tensor([10.0]),
            'ancho': torch.tensor([20.0])
        }
        
        result = _split_targets(targets, device)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_targets_tensor(self, device):
        """Test splitting targets from tensor."""
        targets = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
        
        result = _split_targets(targets, device)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_outputs_dict(self):
        """Test splitting outputs from dict."""
        outputs = {
            'alto': torch.tensor([10.0]),
            'ancho': torch.tensor([20.0])
        }
        
        result = _split_outputs(outputs)
        
        assert result == outputs
    
    def test_split_outputs_tensor(self):
        """Test splitting outputs from tensor."""
        outputs = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
        
        result = _split_outputs(outputs)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_prepare_batch_data_with_pixel_features(self, device):
        """Test preparing batch data with pixel features."""
        images = torch.randn(2, 3, 224, 224)
        targets = torch.randn(2, 4)
        pixel_features = torch.randn(2, 5)
        batch_data = (images, targets, pixel_features)
        
        inputs, targets_batch = _prepare_batch_data(batch_data, True, device)
        
        assert inputs is not None
        assert len(inputs) == 2
    
    def test_prepare_batch_data_without_pixel_features(self, device):
        """Test preparing batch data without pixel features."""
        images = torch.randn(2, 3, 224, 224)
        targets = torch.randn(2, 4)
        batch_data = (images, targets)
        
        inputs, targets_batch = _prepare_batch_data(batch_data, False, device)
        
        assert inputs is not None
        assert len(inputs) == 1
    
    def test_compute_loss(self, device):
        """Test computing loss."""
        outputs_dict = {
            'alto': torch.tensor([10.0]),
            'ancho': torch.tensor([20.0]),
            'grosor': torch.tensor([30.0]),
            'peso': torch.tensor([40.0])
        }
        targets_dict = {
            'alto': torch.tensor([11.0]),
            'ancho': torch.tensor([21.0]),
            'grosor': torch.tensor([31.0]),
            'peso': torch.tensor([41.0])
        }
        
        criterion = nn.MSELoss()
        
        loss = _compute_loss(outputs_dict, targets_dict, criterion)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0
    
    def test_check_early_stopping_improvement(self):
        """Test checking early stopping with improvement."""
        is_best, new_patience, new_best_loss = _check_early_stopping(0.4, 0.5, 2, 1e-4)
        
        assert is_best is True
        assert new_patience == 0
        assert new_best_loss == 0.4
    
    def test_check_early_stopping_no_improvement(self):
        """Test checking early stopping without improvement."""
        is_best, new_patience, new_best_loss = _check_early_stopping(0.6, 0.5, 2, 1e-4)
        
        assert is_best is False
        assert new_patience == 3
        assert new_best_loss == 0.5
    
    def test_detect_model_type_hybrid(self):
        """Test detecting hybrid model type."""
        config = {'hybrid': True, 'use_pixel_features': True}
        
        is_hybrid, use_pixel_features = _detect_model_type(config)
        
        assert is_hybrid is True
        assert use_pixel_features is True
    
    def test_detect_model_type_model_type_hybrid(self):
        """Test detecting hybrid model type from model_type."""
        config = {'model_type': 'hybrid', 'use_pixel_features': True}
        
        is_hybrid, use_pixel_features = _detect_model_type(config)
        
        assert is_hybrid is True
        assert use_pixel_features is True
    
    def test_detect_model_type_not_hybrid(self):
        """Test detecting non-hybrid model type."""
        config = {'model_type': 'resnet18', 'use_pixel_features': False}
        
        is_hybrid, use_pixel_features = _detect_model_type(config)
        
        assert is_hybrid is False
        assert use_pixel_features is False
    
    def test_initialize_training_components(self, device):
        """Test initializing training components."""
        model = nn.Linear(10, 4)
        config = {
            'learning_rate': 1e-4,
            'loss_type': 'smooth_l1',
            'scheduler_type': 'reduce_on_plateau',
            'epochs': 50,
            'weight_decay': 1e-4,
            'min_lr': 1e-7
        }
        
        lr, loss_type, criterion, optimizer, scheduler = _initialize_training_components(model, config)
        
        assert lr == 1e-4
        assert loss_type == 'smooth_l1'
        assert isinstance(criterion, nn.Module)
        assert isinstance(optimizer, torch.optim.Optimizer)
        assert isinstance(scheduler, torch.optim.lr_scheduler._LRScheduler)
    
    def test_initialize_history(self):
        """Test initializing history."""
        history = _initialize_history()
        
        assert 'train_loss' in history
        assert 'val_loss' in history
        assert 'learning_rate' in history
        for target in TARGETS:
            assert f'val_mae_{target}' in history
            assert f'val_rmse_{target}' in history
            assert f'val_r2_{target}' in history
        assert 'val_r2_avg' in history


class TestGetDevice:
    """Tests for get_device function."""
    
    @patch('ml.regression.train.torch')
    def test_get_device_cuda(self, mock_torch):
        """Test getting CUDA device."""
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = 'Test GPU'
        
        device = get_device()
        
        assert device.type == 'cuda'
    
    @patch('ml.regression.train.torch')
    def test_get_device_cpu(self, mock_torch):
        """Test getting CPU device."""
        mock_torch.cuda.is_available.return_value = False
        
        device = get_device()
        
        assert device.type == 'cpu'


class TestCreateTrainingJob:
    """Tests for create_training_job function."""
    
    @patch('ml.regression.train.DJANGO_LOADED', True)
    @patch('ml.regression.train.TrainingJob')
    @patch('ml.regression.train.User')
    def test_create_training_job_success(self, mock_user, mock_job):
        """Test creating training job successfully."""
        mock_user.objects.filter.return_value.first.return_value = MagicMock()
        mock_job.objects.create.return_value = MagicMock()
        
        config = {'epochs': 50, 'batch_size': 32, 'learning_rate': 1e-4}
        
        result = create_training_job(
            job_type='regression',
            model_name='test_model',
            dataset_size=100,
            config=config
        )
        
        assert result is not None
        mock_job.objects.create.assert_called_once()
    
    @patch('ml.regression.train.DJANGO_LOADED', False)
    def test_create_training_job_no_django(self):
        """Test creating training job when Django not loaded."""
        with patch('ml.regression.train.logger') as mock_logger:
            result = create_training_job()
            
            assert result is None
            mock_logger.warning.assert_called()


class TestUpdateTrainingJobMetrics:
    """Tests for update_training_job_metrics function."""
    
    @patch('ml.regression.train.DJANGO_LOADED', True)
    def test_update_training_job_metrics_success(self):
        """Test updating training job metrics successfully."""
        mock_job = MagicMock()
        metrics = {'mae': 0.5, 'rmse': 0.6}
        
        with patch('ml.regression.train.logger'):
            update_training_job_metrics(mock_job, metrics, '/path/to/model.pt')
            
            mock_job.mark_completed.assert_called_once()
    
    @patch('ml.regression.train.DJANGO_LOADED', False)
    def test_update_training_job_metrics_no_django(self):
        """Test updating training job metrics when Django not loaded."""
        mock_job = MagicMock()
        metrics = {'mae': 0.5}
        
        update_training_job_metrics(mock_job, metrics)
        
        # Should not raise, just return
        assert True
    
    def test_update_training_job_metrics_no_job(self):
        """Test updating training job metrics with no job."""
        metrics = {'mae': 0.5}
        
        # Should not raise
        update_training_job_metrics(None, metrics)


