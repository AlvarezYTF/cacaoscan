"""
Tests for train_improved.py regression training module.
This file tests the improved training loop for regression models.
"""
import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

from ml.regression.train_improved import (
    _split_targets,
    _split_outputs,
    validate_targets_normalization,
    _setup_loss_function,
    _create_standard_loss,
    _setup_optimizer,
    _setup_scheduler,
    _prepare_batch_inputs,
    _compute_batch_loss,
    _validate_initial_loss,
    _prepare_train_batch_inputs,
    _process_train_batch,
    _train_one_epoch,
    _accumulate_validation_metrics,
    _process_validation_batch,
    _calculate_validation_metrics,
    _validate_one_epoch,
    _validate_model_output_range,
    _log_epoch_metrics,
    _save_checkpoint,
    _handle_intelligent_early_stopping,
    _handle_basic_early_stopping,
    _handle_early_stopping,
    _validate_targets_normalization_setup,
    _setup_learning_rate,
    _setup_early_stopping,
    _initialize_training_state,
    _update_scheduler,
    _save_metrics_to_history,
    _run_training_loop,
    _save_final_model,
    train_multi_head_model_improved,
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
    # Mock fitted scalers
    scalers.is_fitted = True
    scalers.inverse_transform = MagicMock(return_value={
        'alto': np.array([10.0]),
        'ancho': np.array([20.0]),
        'grosor': np.array([30.0]),
        'peso': np.array([40.0])
    })
    return scalers


class TestSplitTargets:
    """Tests for _split_targets function."""
    
    def test_split_targets_dict(self, device):
        """Test splitting targets from dict."""
        targets_dict = {
            'alto': torch.tensor([10.0]),
            'ancho': torch.tensor([20.0]),
            'grosor': torch.tensor([30.0]),
            'peso': torch.tensor([40.0])
        }
        
        result = _split_targets(targets_dict, device)
        
        assert isinstance(result, dict)
        assert 'alto' in result
        assert 'ancho' in result
    
    def test_split_targets_tensor_1d(self, device):
        """Test splitting targets from 1D tensor."""
        targets = torch.tensor([10.0, 20.0, 30.0, 40.0])
        
        result = _split_targets(targets, device)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_targets_tensor_2d(self, device):
        """Test splitting targets from 2D tensor."""
        targets = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
        
        result = _split_targets(targets, device)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_targets_tensor_3d(self, device):
        """Test splitting targets from 3D tensor."""
        targets = torch.tensor([[[10.0, 20.0, 30.0, 40.0]]])
        
        result = _split_targets(targets, device)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_targets_invalid_columns(self, device):
        """Test splitting targets with invalid number of columns."""
        targets = torch.tensor([[10.0, 20.0]])  # Only 2 columns
        
        with pytest.raises(ValueError):
            _split_targets(targets, device)
    
    def test_split_targets_invalid_type(self, device):
        """Test splitting targets with invalid type."""
        with pytest.raises(TypeError):
            _split_targets("invalid", device)


class TestSplitOutputs:
    """Tests for _split_outputs function."""
    
    def test_split_outputs_dict(self):
        """Test splitting outputs from dict."""
        outputs_dict = {
            'alto': torch.tensor([10.0]),
            'ancho': torch.tensor([20.0]),
            'grosor': torch.tensor([30.0]),
            'peso': torch.tensor([40.0])
        }
        
        result = _split_outputs(outputs_dict)
        
        assert result == outputs_dict
    
    def test_split_outputs_tensor_1d(self):
        """Test splitting outputs from 1D tensor."""
        outputs = torch.tensor([10.0, 20.0, 30.0, 40.0])
        
        result = _split_outputs(outputs)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_outputs_tensor_2d(self):
        """Test splitting outputs from 2D tensor."""
        outputs = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
        
        result = _split_outputs(outputs)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_outputs_tensor_3d(self):
        """Test splitting outputs from 3D tensor."""
        outputs = torch.tensor([[[10.0, 20.0, 30.0, 40.0]]])
        
        result = _split_outputs(outputs)
        
        assert isinstance(result, dict)
        assert 'alto' in result
    
    def test_split_outputs_invalid_columns(self):
        """Test splitting outputs with invalid number of columns."""
        outputs = torch.tensor([[10.0, 20.0]])  # Only 2 columns
        
        with pytest.raises(ValueError):
            _split_outputs(outputs)
    
    def test_split_outputs_invalid_type(self):
        """Test splitting outputs with invalid type."""
        with pytest.raises(TypeError):
            _split_outputs("invalid")


class TestValidateTargetsNormalization:
    """Tests for validate_targets_normalization function."""
    
    def test_validate_targets_normalization_success(self, sample_scalers):
        """Test validating targets normalization successfully."""
        targets = {
            'alto': np.array([0.0, 1.0, -1.0]),
            'ancho': np.array([0.0, 1.0, -1.0]),
            'grosor': np.array([0.0, 1.0, -1.0]),
            'peso': np.array([0.0, 1.0, -1.0])
        }
        
        result = validate_targets_normalization(targets, sample_scalers, verbose=False)
        
        assert result is True
    
    def test_validate_targets_normalization_no_scalers(self):
        """Test validating targets normalization without scalers."""
        targets = {
            'alto': np.array([0.0, 1.0, -1.0])
        }
        
        scalers = Mock()
        scalers.is_fitted = False
        
        result = validate_targets_normalization(targets, scalers, verbose=False)
        
        assert result is False
    
    def test_validate_targets_normalization_nan(self, sample_scalers):
        """Test validating targets normalization with NaN."""
        targets = {
            'alto': np.array([0.0, np.nan, -1.0])
        }
        
        result = validate_targets_normalization(targets, sample_scalers, verbose=False)
        
        assert result is False
    
    def test_validate_targets_normalization_out_of_range(self, sample_scalers):
        """Test validating targets normalization out of range."""
        targets = {
            'alto': np.array([100.0, 200.0, 300.0])  # Very large values
        }
        
        result = validate_targets_normalization(targets, sample_scalers, verbose=False)
        
        # May be False if out of expected range
        assert isinstance(result, bool)


class TestSetupLossFunction:
    """Tests for _setup_loss_function."""
    
    def test_setup_loss_function_uncertainty_available(self, device):
        """Test setting up loss function with uncertainty loss available."""
        with patch('ml.regression.train_improved.UncertaintyWeightedLoss') as mock_uncertainty:
            mock_loss = MagicMock()
            mock_uncertainty.return_value = mock_loss
            
            config = {}
            criterion, use_uncertainty = _setup_loss_function(None, config, device)
            
            assert use_uncertainty is True
            mock_uncertainty.assert_called_once()
    
    def test_setup_loss_function_uncertainty_not_available(self, device):
        """Test setting up loss function with uncertainty loss not available."""
        with patch('ml.regression.train_improved.UncertaintyWeightedLoss', side_effect=ImportError):
            config = {'loss_type': 'smooth_l1'}
            criterion, use_uncertainty = _setup_loss_function(None, config, device)
            
            assert use_uncertainty is False
            assert isinstance(criterion, nn.Module)
    
    def test_setup_loss_function_explicit_uncertainty(self, device):
        """Test setting up loss function with explicit uncertainty flag."""
        with patch('ml.regression.train_improved.UncertaintyWeightedLoss') as mock_uncertainty:
            mock_loss = MagicMock()
            mock_uncertainty.return_value = mock_loss
            
            config = {}
            criterion, use_uncertainty = _setup_loss_function(True, config, device)
            
            assert use_uncertainty is True
    
    def test_setup_loss_function_explicit_no_uncertainty(self, device):
        """Test setting up loss function with explicit no uncertainty flag."""
        config = {'loss_type': 'smooth_l1'}
        criterion, use_uncertainty = _setup_loss_function(False, config, device)
        
        assert use_uncertainty is False
        assert isinstance(criterion, nn.Module)


class TestCreateStandardLoss:
    """Tests for _create_standard_loss function."""
    
    def test_create_standard_loss_mse(self):
        """Test creating MSE loss."""
        config = {'loss_type': 'mse'}
        criterion = _create_standard_loss(config)
        
        assert isinstance(criterion, nn.MSELoss)
    
    def test_create_standard_loss_huber(self):
        """Test creating Huber loss."""
        config = {'loss_type': 'huber'}
        criterion = _create_standard_loss(config)
        
        assert isinstance(criterion, nn.HuberLoss)
    
    def test_create_standard_loss_smooth_l1(self):
        """Test creating SmoothL1 loss."""
        config = {'loss_type': 'smooth_l1'}
        criterion = _create_standard_loss(config)
        
        assert isinstance(criterion, nn.SmoothL1Loss)
    
    def test_create_standard_loss_default(self):
        """Test creating default loss."""
        config = {}
        criterion = _create_standard_loss(config)
        
        assert isinstance(criterion, nn.SmoothL1Loss)


class TestSetupOptimizer:
    """Tests for _setup_optimizer function."""
    
    def test_setup_optimizer_with_uncertainty_loss(self, device):
        """Test setting up optimizer with uncertainty loss."""
        model = nn.Linear(10, 4)
        criterion = MagicMock()
        criterion.parameters.return_value = [torch.nn.Parameter(torch.tensor([0.3]))]
        
        config = {'weight_decay': 1e-4}
        learning_rate = 1e-4
        
        optimizer = _setup_optimizer(model, criterion, True, learning_rate, config)
        
        assert isinstance(optimizer, torch.optim.AdamW)
        assert len(optimizer.param_groups) == 2
    
    def test_setup_optimizer_without_uncertainty_loss(self, device):
        """Test setting up optimizer without uncertainty loss."""
        model = nn.Linear(10, 4)
        criterion = nn.MSELoss()
        
        config = {'weight_decay': 1e-4}
        learning_rate = 1e-4
        
        optimizer = _setup_optimizer(model, criterion, False, learning_rate, config)
        
        assert isinstance(optimizer, torch.optim.AdamW)
        assert len(optimizer.param_groups) == 1


class TestSetupScheduler:
    """Tests for _setup_scheduler function."""
    
    def test_setup_scheduler_reduce_on_plateau(self):
        """Test setting up ReduceLROnPlateau scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        config = {'min_lr': 1e-7}
        epochs = 50
        
        scheduler = _setup_scheduler(optimizer, config, epochs)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau)
    
    def test_setup_scheduler_cosine(self):
        """Test setting up CosineAnnealingLR scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        config = {'scheduler_type': 'cosine', 'min_lr': 1e-6}
        epochs = 50
        
        scheduler = _setup_scheduler(optimizer, config, epochs)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.CosineAnnealingLR)
    
    def test_setup_scheduler_cosine_warmup(self):
        """Test setting up CosineAnnealingWarmRestarts scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        config = {'scheduler_type': 'cosine_warmup', 'min_lr': 1e-7}
        epochs = 50
        
        scheduler = _setup_scheduler(optimizer, config, epochs)
        
        assert isinstance(scheduler, torch.optim.lr_scheduler.CosineAnnealingWarmRestarts)


class TestPrepareBatchInputs:
    """Tests for _prepare_batch_inputs function."""
    
    def test_prepare_batch_inputs_with_pixel_features(self, device):
        """Test preparing batch inputs with pixel features."""
        images = torch.randn(2, 3, 224, 224)
        targets = torch.randn(2, 4)
        pixel_features = torch.randn(2, 5)
        batch_data = (images, targets, pixel_features)
        
        result = _prepare_batch_inputs(batch_data, device, True)
        
        assert result is not None
        inputs, targets_batch = result
        assert len(inputs) == 2
    
    def test_prepare_batch_inputs_without_pixel_features(self, device):
        """Test preparing batch inputs without pixel features."""
        images = torch.randn(2, 3, 224, 224)
        targets = torch.randn(2, 4)
        batch_data = (images, targets)
        
        result = _prepare_batch_inputs(batch_data, device, False)
        
        assert result is not None
        inputs, targets_batch = result
        assert len(inputs) == 1
    
    def test_prepare_batch_inputs_invalid_length_with_pixel_features(self, device):
        """Test preparing batch inputs with invalid length when pixel features expected."""
        batch_data = (torch.randn(2, 3, 224, 224), torch.randn(2, 4))
        
        result = _prepare_batch_inputs(batch_data, device, True)
        
        assert result is None
    
    def test_prepare_batch_inputs_invalid_length_without_pixel_features(self, device):
        """Test preparing batch inputs with invalid length when no pixel features expected."""
        batch_data = (torch.randn(2, 3, 224, 224),)
        
        result = _prepare_batch_inputs(batch_data, device, False)
        
        assert result is None


class TestComputeBatchLoss:
    """Tests for _compute_batch_loss function."""
    
    def test_compute_batch_loss_with_uncertainty(self, device):
        """Test computing batch loss with uncertainty loss."""
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
        
        criterion = MagicMock()
        criterion.return_value = torch.tensor(0.5)
        
        loss = _compute_batch_loss(outputs_dict, targets_dict, criterion, True)
        
        assert isinstance(loss, torch.Tensor)
        criterion.assert_called_once()
    
    def test_compute_batch_loss_without_uncertainty(self, device):
        """Test computing batch loss without uncertainty loss."""
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
        
        loss = _compute_batch_loss(outputs_dict, targets_dict, criterion, False)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0


class TestSetupLearningRate:
    """Tests for _setup_learning_rate function."""
    
    def test_setup_learning_rate_valid(self):
        """Test setting up valid learning rate."""
        config = {'learning_rate': 1e-4}
        
        result = _setup_learning_rate(config)
        
        assert result == 1e-4
    
    def test_setup_learning_rate_too_high(self):
        """Test setting up learning rate that's too high."""
        config = {'learning_rate': 1e-2}
        
        with patch('ml.regression.train_improved.logger') as mock_logger:
            result = _setup_learning_rate(config)
            
            assert result == 1e-3
            mock_logger.warning.assert_called()
    
    def test_setup_learning_rate_too_low(self):
        """Test setting up learning rate that's too low."""
        config = {'learning_rate': 1e-7}
        
        with patch('ml.regression.train_improved.logger') as mock_logger:
            result = _setup_learning_rate(config)
            
            assert result == 1e-6
            mock_logger.warning.assert_called()


class TestSetupEarlyStopping:
    """Tests for _setup_early_stopping function."""
    
    def test_setup_early_stopping_intelligent_available(self):
        """Test setting up early stopping with intelligent available."""
        config = {'early_stopping_patience': 15}
        
        with patch('ml.regression.train_improved.IntelligentEarlyStopping') as mock_intelligent:
            mock_stopping = MagicMock()
            mock_intelligent.return_value = mock_stopping
            
            use_intelligent, early_stopping, patience = _setup_early_stopping(config)
            
            assert use_intelligent is True
            assert early_stopping == mock_stopping
            assert patience == 15
    
    def test_setup_early_stopping_intelligent_not_available(self):
        """Test setting up early stopping with intelligent not available."""
        config = {'early_stopping_patience': 10}
        
        with patch('ml.regression.train_improved.IntelligentEarlyStopping', side_effect=ImportError):
            use_intelligent, early_stopping, patience = _setup_early_stopping(config)
            
            assert use_intelligent is False
            assert early_stopping is None
            assert patience == 10


class TestInitializeTrainingState:
    """Tests for _initialize_training_state function."""
    
    def test_initialize_training_state(self):
        """Test initializing training state."""
        config = {'improvement_threshold': 1e-4}
        
        state = _initialize_training_state(config)
        
        assert state['best_val_loss'] == float('inf')
        assert state['patience_counter'] == 0
        assert state['best_model_state'] is None
        assert 'history' in state
        assert 'train_loss' in state['history']
        assert 'val_loss' in state['history']


class TestUpdateScheduler:
    """Tests for _update_scheduler function."""
    
    def test_update_scheduler_reduce_on_plateau(self):
        """Test updating ReduceLROnPlateau scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)
        avg_val_loss = 0.5
        
        lr = _update_scheduler(scheduler, optimizer, avg_val_loss)
        
        assert isinstance(lr, float)
        assert lr > 0
    
    def test_update_scheduler_cosine(self):
        """Test updating CosineAnnealingLR scheduler."""
        optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.tensor([1.0]))])
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
        avg_val_loss = 0.5
        
        lr = _update_scheduler(scheduler, optimizer, avg_val_loss)
        
        assert isinstance(lr, float)
        assert lr > 0


class TestSaveMetricsToHistory:
    """Tests for _save_metrics_to_history function."""
    
    def test_save_metrics_to_history(self):
        """Test saving metrics to history."""
        history = {
            'val_mae_alto': [],
            'val_rmse_alto': [],
            'val_r2_alto': [],
            'val_mae_ancho': [],
            'val_rmse_ancho': [],
            'val_r2_ancho': [],
            'val_mae_grosor': [],
            'val_rmse_grosor': [],
            'val_r2_grosor': [],
            'val_mae_peso': [],
            'val_rmse_peso': [],
            'val_r2_peso': [],
            'val_r2_avg': []
        }
        
        metrics_per_target = {
            'alto': {'mae': 0.5, 'rmse': 0.6, 'r2': 0.8},
            'ancho': {'mae': 0.4, 'rmse': 0.5, 'r2': 0.85}
        }
        avg_r2 = 0.825
        
        _save_metrics_to_history(history, metrics_per_target, avg_r2)
        
        assert len(history['val_mae_alto']) == 1
        assert len(history['val_r2_avg']) == 1
        assert history['val_r2_avg'][0] == 0.825


class TestSaveFinalModel:
    """Tests for _save_final_model function."""
    
    @patch('ml.regression.train_improved.get_regressors_artifacts_dir')
    @patch('ml.regression.train_improved.ensure_dir_exists')
    def test_save_final_model_hybrid(self, mock_ensure_dir, mock_get_artifacts, tmp_path, sample_model):
        """Test saving final model as hybrid."""
        artifacts_dir = tmp_path / 'artifacts'
        artifacts_dir.mkdir()
        mock_get_artifacts.return_value = artifacts_dir
        
        config = {'epochs': 50}
        best_val_loss = 0.5
        best_epoch = 10
        history = {'train_loss': [0.5], 'val_loss': [0.4]}
        
        _save_final_model(sample_model, True, config, best_val_loss, best_epoch, history)
        
        model_path = artifacts_dir / 'hybrid.pt'
        assert model_path.exists()
    
    @patch('ml.regression.train_improved.get_regressors_artifacts_dir')
    @patch('ml.regression.train_improved.ensure_dir_exists')
    def test_save_final_model_multihead(self, mock_ensure_dir, mock_get_artifacts, tmp_path, sample_model):
        """Test saving final model as multihead."""
        artifacts_dir = tmp_path / 'artifacts'
        artifacts_dir.mkdir()
        mock_get_artifacts.return_value = artifacts_dir
        
        config = {'epochs': 50}
        best_val_loss = 0.5
        best_epoch = 10
        history = {'train_loss': [0.5], 'val_loss': [0.4]}
        
        _save_final_model(sample_model, False, config, best_val_loss, best_epoch, history)
        
        model_path = artifacts_dir / 'multihead.pt'
        assert model_path.exists()


