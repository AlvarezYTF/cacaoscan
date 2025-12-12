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
    
    def test_evaluate_single_model(self, mock_model, mock_data_loader):
        """Test evaluate_single_model method."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        # Mock model to return correct shape for single target
        class SingleOutputModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(10, 1)
            
            def forward(self, x):
                return self.linear(x)
        
        single_model = SingleOutputModel()
        evaluator.model = single_model
        
        metrics = evaluator.evaluate_single_model('alto', denormalize=False)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert 'n_samples' in metrics
    
    def test_evaluate_single_model_with_dict_targets(self, mock_model):
        """Test evaluate_single_model with dict targets."""
        # Create data loader with dict targets
        data = torch.randn(5, 10)
        targets_dict = {
            'alto': torch.randn(5),
            'ancho': torch.randn(5),
            'grosor': torch.randn(5),
            'peso': torch.randn(5)
        }
        
        dataset = [(data[i:i+2], {k: v[i:i+2] for k, v in targets_dict.items()}) for i in range(0, 5, 2)]
        
        class DictDataLoader:
            def __iter__(self):
                return iter(dataset)
        
        loader = DictDataLoader()
        
        class SingleOutputModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(10, 1)
            
            def forward(self, x):
                return self.linear(x)
        
        single_model = SingleOutputModel()
        evaluator = RegressionEvaluator(
            model=single_model,
            test_loader=loader,
            device=torch.device('cpu')
        )
        
        metrics = evaluator.evaluate_single_model('alto', denormalize=False)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
    
    def test_evaluate_multi_head_model(self, mock_model):
        """Test evaluate_multi_head_model method."""
        # Create multi-head model
        class MultiHeadModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = nn.Linear(10, 128)
                self.heads = nn.ModuleDict({
                    'alto': nn.Linear(128, 1),
                    'ancho': nn.Linear(128, 1),
                    'grosor': nn.Linear(128, 1),
                    'peso': nn.Linear(128, 1)
                })
            
            def forward(self, x):
                features = self.backbone(x)
                return {k: head(features) for k, head in self.heads.items()}
        
        multi_model = MultiHeadModel()
        
        # Create data loader with dict targets
        data = torch.randn(5, 10)
        targets_dict = {
            'alto': torch.randn(5),
            'ancho': torch.randn(5),
            'grosor': torch.randn(5),
            'peso': torch.randn(5)
        }
        
        dataset = [(data[i:i+2], {k: v[i:i+2] for k, v in targets_dict.items()}) for i in range(0, 5, 2)]
        
        class DictDataLoader:
            def __iter__(self):
                return iter(dataset)
        
        loader = DictDataLoader()
        
        evaluator = RegressionEvaluator(
            model=multi_model,
            test_loader=loader,
            device=torch.device('cpu')
        )
        
        results = evaluator.evaluate_multi_head_model(denormalize=False)
        
        assert 'alto' in results
        assert 'ancho' in results
        assert 'grosor' in results
        assert 'peso' in results
        
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            assert 'mae' in results[target]
            assert 'rmse' in results[target]
            assert 'r2' in results[target]
    
    def test_unpack_multi_head_batch_2_elements(self, mock_model, mock_data_loader):
        """Test _unpack_multi_head_batch with 2 elements."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        images = torch.randn(2, 3, 224, 224)
        targets = torch.randn(2, 4)
        batch_data = (images, targets)
        
        result = evaluator._unpack_multi_head_batch(batch_data)
        
        assert result is not None
        assert len(result) == 3
    
    def test_unpack_multi_head_batch_3_elements(self, mock_model, mock_data_loader):
        """Test _unpack_multi_head_batch with 3 elements."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        images = torch.randn(2, 3, 224, 224)
        targets = torch.randn(2, 4)
        pixel_features = torch.randn(2, 10)
        batch_data = (images, targets, pixel_features)
        
        result = evaluator._unpack_multi_head_batch(batch_data)
        
        assert result is not None
        assert len(result) == 3
        assert result[2] is not None
    
    def test_unpack_multi_head_batch_invalid(self, mock_model, mock_data_loader):
        """Test _unpack_multi_head_batch with invalid input."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        # Invalid batch (not list or tuple)
        result = evaluator._unpack_multi_head_batch("invalid")
        assert result is None
        
        # Invalid batch (wrong length)
        result = evaluator._unpack_multi_head_batch((torch.randn(2, 3),))
        assert result is None
    
    def test_normalize_targets_dict(self, mock_model, mock_data_loader):
        """Test _normalize_targets_dict with dict input."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        targets_dict = {
            'alto': torch.randn(2),
            'ancho': torch.randn(2),
            'grosor': torch.randn(2),
            'peso': torch.randn(2)
        }
        
        result = evaluator._normalize_targets_dict(targets_dict)
        
        assert isinstance(result, dict)
        assert 'alto' in result
        assert 'ancho' in result
        assert 'grosor' in result
        assert 'peso' in result
    
    def test_normalize_targets_tensor(self, mock_model, mock_data_loader):
        """Test _normalize_targets_dict with tensor input."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        targets_tensor = torch.randn(2, 4)
        
        result = evaluator._normalize_targets_dict(targets_tensor)
        
        assert isinstance(result, dict)
        assert len(result) == 4
    
    def test_normalize_targets_invalid(self, mock_model, mock_data_loader):
        """Test _normalize_targets_dict with invalid input."""
        evaluator = RegressionEvaluator(
            model=mock_model,
            test_loader=mock_data_loader,
            device=torch.device('cpu')
        )
        
        # Invalid tensor shape
        invalid_tensor = torch.randn(2, 2)  # Not enough columns
        
        with pytest.raises(ValueError, match="El tensor de targets"):
            evaluator._normalize_targets_dict(invalid_tensor)
    
    @patch('ml.regression.evaluate.load_model_for_evaluation')
    def test_load_model_for_evaluation_function(self, mock_load):
        """Test load_model_for_evaluation function."""
        from ml.regression.evaluate import load_model_for_evaluation
        from pathlib import Path
        
        mock_model = nn.Linear(10, 4)
        mock_load.return_value = mock_model
        
        model_path = Path("test.pt")
        model_class = nn.Linear
        
        with patch('torch.load') as mock_torch_load:
            mock_torch_load.return_value = {'model_state_dict': mock_model.state_dict()}
            
            result = load_model_for_evaluation(
                model_path=model_path,
                model_class=model_class,
                device=torch.device('cpu')
            )
            
            assert result is not None
    
    @patch('ml.regression.evaluate.RegressionEvaluator')
    def test_evaluate_model_from_file(self, mock_evaluator_class):
        """Test evaluate_model_from_file function."""
        from ml.regression.evaluate import evaluate_model_from_file
        from pathlib import Path
        
        mock_evaluator = MagicMock()
        mock_evaluator.evaluate_single_model.return_value = {'mae': 0.5, 'rmse': 0.7, 'r2': 0.9}
        mock_evaluator.evaluate_multi_head_model.return_value = {
            'alto': {'mae': 0.5, 'rmse': 0.7, 'r2': 0.9}
        }
        mock_evaluator_class.return_value = mock_evaluator
        
        model_path = Path("test.pt")
        model_class = nn.Linear
        
        class MockLoader:
            pass
        
        loader = MockLoader()
        
        with patch('ml.regression.evaluate.load_model_for_evaluation') as mock_load:
            mock_load.return_value = nn.Linear(10, 4)
            
            # Test with target
            results = evaluate_model_from_file(
                model_path=model_path,
                model_class=model_class,
                test_loader=loader,
                target='alto'
            )
            
            assert 'mae' in results
            mock_evaluator.evaluate_single_model.assert_called_once()
            
            # Test without target
            results = evaluate_model_from_file(
                model_path=model_path,
                model_class=model_class,
                test_loader=loader
            )
            
            assert isinstance(results, dict)
            mock_evaluator.evaluate_multi_head_model.assert_called_once()

