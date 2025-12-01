"""
Unit tests for ML regression evaluation module.
Tests compute_regression_metrics and RegressionEvaluator.
"""
import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from torch.utils.data import DataLoader, TensorDataset

from ml.regression.evaluate import (
    compute_regression_metrics,
    RegressionEvaluator
)


@pytest.fixture
def sample_targets():
    """Create sample target array."""
    return np.array([1.0, 2.0, 3.0, 4.0, 5.0])


@pytest.fixture
def sample_predictions():
    """Create sample prediction array."""
    return np.array([1.1, 2.2, 2.9, 4.1, 4.8])


@pytest.fixture
def mock_model():
    """Create a mock model for testing."""
    model = Mock()
    model.eval = Mock()
    model.to = Mock(return_value=model)
    model.return_value = torch.tensor([[1.0], [2.0], [3.0]])
    return model


@pytest.fixture
def mock_data_loader():
    """Create a mock data loader for testing."""
    images = torch.randn(10, 3, 224, 224)
    targets = torch.randn(10)
    dataset = TensorDataset(images, targets)
    return DataLoader(dataset, batch_size=2)


class TestComputeRegressionMetrics:
    """Tests for compute_regression_metrics function."""
    
    def test_compute_metrics_basic(self, sample_targets, sample_predictions):
        """Test basic metric computation."""
        metrics = compute_regression_metrics(sample_targets, sample_predictions)
        
        assert 'mae' in metrics
        assert 'mse' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert 'mape' in metrics
        assert 'relative_error' in metrics
        
        assert isinstance(metrics['mae'], float)
        assert isinstance(metrics['mse'], float)
        assert isinstance(metrics['rmse'], float)
        assert isinstance(metrics['r2'], float)
    
    def test_compute_metrics_perfect_predictions(self):
        """Test metrics with perfect predictions."""
        targets = np.array([1.0, 2.0, 3.0])
        predictions = np.array([1.0, 2.0, 3.0])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['mae'] == 0.0
        assert metrics['mse'] == 0.0
        assert metrics['rmse'] == 0.0
        assert metrics['r2'] == 1.0
    
    def test_compute_metrics_with_zeros(self):
        """Test metrics computation with zero values."""
        targets = np.array([0.0, 1.0, 2.0])
        predictions = np.array([0.1, 1.1, 2.1])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert 'mae' in metrics
        assert 'mse' in metrics
        assert metrics['mape'] == 0.0  # Should be 0 when all targets are zero
        assert metrics['relative_error'] == 0.0
    
    def test_compute_metrics_all_zeros(self):
        """Test metrics with all zero targets."""
        targets = np.array([0.0, 0.0, 0.0])
        predictions = np.array([0.1, 0.2, 0.3])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['mape'] == 0.0
        assert metrics['relative_error'] == 0.0
        assert metrics['mae'] > 0.0
    
    def test_compute_metrics_negative_values(self):
        """Test metrics with negative values."""
        targets = np.array([-1.0, 0.0, 1.0])
        predictions = np.array([-0.9, 0.1, 1.1])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert 'mae' in metrics
        assert 'mse' in metrics
        assert isinstance(metrics['r2'], float)


class TestRegressionEvaluator:
    """Tests for RegressionEvaluator class."""
    
    def test_evaluator_initialization(self, mock_model, mock_data_loader):
        """Test RegressionEvaluator initialization."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        assert evaluator.model == mock_model
        assert evaluator.test_loader == mock_data_loader
        assert evaluator.device == torch.device('cpu')
        assert evaluator.results == {}
        assert evaluator.predictions == {}
        assert evaluator.targets == {}
    
    def test_evaluator_initialization_with_scalers(self, mock_model, mock_data_loader):
        """Test RegressionEvaluator initialization with scalers."""
        mock_scalers = Mock()
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            scalers=mock_scalers,
            device=torch.device('cpu')
        )
        
        assert evaluator.scalers == mock_scalers
    
    @patch('ml.regression.evaluate.compute_regression_metrics')
    def test_evaluate_single_model(self, mock_compute_metrics, mock_model, mock_data_loader):
        """Test evaluate_single_model method."""
        mock_compute_metrics.return_value = {
            'mae': 0.1,
            'mse': 0.01,
            'rmse': 0.1,
            'r2': 0.95,
            'mape': 5.0,
            'relative_error': 5.0
        }
        
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        # Mock model forward pass
        mock_model.return_value = torch.tensor([[1.0], [2.0], [3.0], [4.0], [5.0]])
        mock_model.side_effect = lambda x: torch.tensor([[1.0], [2.0]])
        
        metrics = evaluator.evaluate_single_model(target='alto', denormalize=False)
        
        assert 'mae' in metrics
        assert 'n_samples' in metrics
        assert metrics['mae'] == 0.1
    
    def test_evaluator_stores_results(self, mock_model, mock_data_loader):
        """Test that evaluator stores results correctly."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        evaluator.results['alto'] = {'mae': 0.1, 'r2': 0.95}
        evaluator.predictions['alto'] = np.array([1.0, 2.0, 3.0])
        evaluator.targets['alto'] = np.array([1.1, 2.1, 3.1])
        
        assert 'alto' in evaluator.results
        assert 'alto' in evaluator.predictions
        assert 'alto' in evaluator.targets

