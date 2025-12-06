"""
Tests for regression evaluation.
"""
import pytest
import numpy as np
import torch
import torch.nn as nn
from ml.regression.evaluate import (
    compute_regression_metrics,
    RegressionEvaluator
)


class TestComputeRegressionMetrics:
    """Tests for compute_regression_metrics function."""
    
    def test_compute_metrics_perfect_prediction(self):
        """Test metrics with perfect predictions."""
        targets = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        predictions = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['r2'] == pytest.approx(1.0, abs=1e-6)
        assert metrics['mae'] == pytest.approx(0.0, abs=1e-6)
        assert metrics['rmse'] == pytest.approx(0.0, abs=1e-6)
        assert metrics['mape'] == pytest.approx(0.0, abs=1e-6)
    
    def test_compute_metrics_with_errors(self):
        """Test metrics with prediction errors."""
        targets = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        predictions = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['r2'] > 0.0
        assert metrics['mae'] == pytest.approx(0.5, abs=1e-6)
        assert metrics['rmse'] > 0.0
        assert metrics['mape'] > 0.0
    
    def test_compute_metrics_with_zeros(self):
        """Test metrics when targets contain zeros."""
        targets = np.array([0.0, 1.0, 2.0, 0.0, 3.0])
        predictions = np.array([0.1, 1.1, 2.1, 0.1, 3.1])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert metrics['mape'] >= 0.0
        assert metrics['relative_error'] >= 0.0
    
    def test_compute_metrics_all_zeros(self):
        """Test metrics when all targets are zero."""
        targets = np.array([0.0, 0.0, 0.0])
        predictions = np.array([0.1, 0.2, 0.3])
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['mape'] == 0.0
        assert metrics['relative_error'] == 0.0
        assert 'mae' in metrics
        assert 'rmse' in metrics


class TestRegressionEvaluator:
    """Tests for RegressionEvaluator class."""
    
    @pytest.fixture
    def mock_model(self):
        """Create mock model."""
        model = nn.Sequential(
            nn.Linear(10, 5),
            nn.Linear(5, 4)
        )
        return model
    
    @pytest.fixture
    def mock_data_loader(self):
        """Create mock data loader."""
        # Create dummy data
        data = torch.randn(5, 10)
        targets = torch.randn(5, 4)
        
        dataset = torch.utils.data.TensorDataset(data, targets)
        loader = torch.utils.data.DataLoader(dataset, batch_size=2)
        return loader
    
    def test_initialization(self, mock_model, mock_data_loader):
        """Test evaluator initialization."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        assert evaluator.model == mock_model
        assert evaluator.test_loader == mock_data_loader
        assert evaluator.device.type == 'cpu'
    
    def test_evaluate_basic(self, mock_model, mock_data_loader):
        """Test basic evaluation."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        # Set model to eval mode
        evaluator.model.eval()
        
        # Run evaluation (should not crash)
        with torch.no_grad():
            for batch_data, batch_targets in mock_data_loader:
                outputs = evaluator.model(batch_data)
                assert outputs.shape[0] == batch_data.shape[0]
                break

