"""
Tests for regression metrics module.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock
from ml.regression.metrics import (
    robust_r2_score,
    calculate_metrics_per_target,
    calculate_average_r2,
    denormalize_and_calculate_metrics,
    validate_predictions_targets_alignment
)


class TestRobustR2Score:
    """Tests for robust_r2_score function."""
    
    def test_perfect_prediction(self):
        """Test R² with perfect predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        assert r2 == pytest.approx(1.0, abs=1e-6)
    
    def test_with_errors(self):
        """Test R² with prediction errors."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        assert r2 > 0.0
        assert r2 < 1.0
    
    def test_empty_arrays(self):
        """Test R² with empty arrays."""
        y_true = np.array([])
        y_pred = np.array([])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        assert r2 == 0.0
    
    def test_shape_mismatch(self):
        """Test R² handles shape mismatch."""
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([[1.0], [2.0], [3.0]])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        assert isinstance(r2, float)
    
    def test_with_nan_values(self):
        """Test R² filters NaN values."""
        y_true = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        assert np.isfinite(r2)
    
    def test_with_inf_values(self):
        """Test R² filters Inf values."""
        y_true = np.array([1.0, 2.0, np.inf, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        assert np.isfinite(r2)
    
    def test_no_variation(self):
        """Test R² when there's no variation in targets."""
        y_true = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        y_pred = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        
        r2 = robust_r2_score(y_true, y_pred, target_name="test")
        
        # Should handle constant targets gracefully
        assert isinstance(r2, float)


class TestComputeAllMetrics:
    """Tests for compute_all_metrics function."""
    
    def test_compute_all_metrics_perfect(self):
        """Test compute_all_metrics with perfect predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        metrics = compute_all_metrics(y_true, y_pred, target_name="test")
        
        assert 'r2' in metrics
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert metrics['r2'] == pytest.approx(1.0, abs=1e-6)
        assert metrics['mae'] == pytest.approx(0.0, abs=1e-6)
    
    def test_compute_all_metrics_with_errors(self):
        """Test compute_all_metrics with prediction errors."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        metrics = compute_all_metrics(y_true, y_pred, target_name="test")
        
        assert 'r2' in metrics
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert metrics['mae'] == pytest.approx(0.5, abs=1e-6)


class TestCalculateMetricsPerTarget:
    """Tests for calculate_metrics_per_target function."""
    
    def test_calculate_metrics_per_target_success(self):
        """Test calculate_metrics_per_target with valid inputs."""
        predictions = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        targets = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        
        metrics = calculate_metrics_per_target(predictions, targets)
        
        assert 'alto' in metrics
        assert 'ancho' in metrics
        assert metrics['alto']['r2'] == pytest.approx(1.0, abs=1e-6)
    
    def test_calculate_metrics_per_target_missing_prediction(self):
        """Test calculate_metrics_per_target with missing prediction."""
        predictions = {
            'alto': np.array([1.0, 2.0, 3.0])
        }
        targets = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        
        metrics = calculate_metrics_per_target(predictions, targets)
        
        assert 'alto' in metrics
        assert 'ancho' not in metrics
    
    def test_calculate_metrics_per_target_with_nan(self):
        """Test calculate_metrics_per_target with NaN values."""
        predictions = {
            'alto': np.array([1.0, np.nan, 3.0])
        }
        targets = {
            'alto': np.array([1.0, 2.0, 3.0])
        }
        
        metrics = calculate_metrics_per_target(predictions, targets)
        
        assert 'alto' in metrics
        assert metrics['alto']['n_samples'] >= 0


class TestCalculateAverageR2:
    """Tests for calculate_average_r2 function."""
    
    def test_calculate_average_r2_success(self):
        """Test calculate_average_r2 with valid metrics."""
        metrics = {
            'alto': {'r2': 0.9, 'mae': 0.5},
            'ancho': {'r2': 0.8, 'mae': 0.6}
        }
        
        avg_r2 = calculate_average_r2(metrics)
        
        assert avg_r2 == pytest.approx(0.85, abs=1e-6)
    
    def test_calculate_average_r2_empty(self):
        """Test calculate_average_r2 with empty metrics."""
        metrics = {}
        
        avg_r2 = calculate_average_r2(metrics)
        
        assert avg_r2 == 0.0
    
    def test_calculate_average_r2_missing_r2(self):
        """Test calculate_average_r2 with metrics missing r2."""
        metrics = {
            'alto': {'mae': 0.5},
            'ancho': {'r2': 0.8}
        }
        
        avg_r2 = calculate_average_r2(metrics)
        
        assert avg_r2 == pytest.approx(0.8, abs=1e-6)


class TestDenormalizeAndCalculateMetrics:
    """Tests for denormalize_and_calculate_metrics function."""
    
    def test_denormalize_and_calculate_metrics_with_scalers(self):
        """Test denormalize_and_calculate_metrics with scalers."""
        predictions_norm = {
            'alto': np.array([0.0, 1.0, 2.0]),
            'ancho': np.array([0.0, 1.0, 2.0])
        }
        targets_norm = {
            'alto': np.array([0.0, 1.0, 2.0]),
            'ancho': np.array([0.0, 1.0, 2.0])
        }
        
        # Mock scaler
        mock_scaler = MagicMock()
        mock_scaler.is_fitted = True
        mock_scaler.inverse_transform = MagicMock(side_effect=lambda x: x)
        
        metrics, avg_r2 = denormalize_and_calculate_metrics(
            predictions_norm,
            targets_norm,
            mock_scaler
        )
        
        assert 'alto' in metrics
        assert 'ancho' in metrics
        assert isinstance(avg_r2, float)
    
    def test_denormalize_and_calculate_metrics_without_scalers(self):
        """Test denormalize_and_calculate_metrics without scalers."""
        predictions_norm = {
            'alto': np.array([0.0, 1.0, 2.0])
        }
        targets_norm = {
            'alto': np.array([0.0, 1.0, 2.0])
        }
        
        metrics, avg_r2 = denormalize_and_calculate_metrics(
            predictions_norm,
            targets_norm,
            None
        )
        
        assert 'alto' in metrics
        assert isinstance(avg_r2, float)


class TestValidatePredictionsTargetsAlignment:
    """Tests for validate_predictions_targets_alignment function."""
    
    def test_validate_alignment_success(self):
        """Test validation with aligned predictions and targets."""
        predictions = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        targets = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        
        result = validate_predictions_targets_alignment(predictions, targets)
        
        assert result is True
    
    def test_validate_alignment_missing_prediction(self):
        """Test validation with missing prediction."""
        predictions = {
            'alto': np.array([1.0, 2.0, 3.0])
        }
        targets = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        
        result = validate_predictions_targets_alignment(predictions, targets)
        
        assert result is False
    
    def test_validate_alignment_length_mismatch(self):
        """Test validation with length mismatch."""
        predictions = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0])
        }
        targets = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        
        result = validate_predictions_targets_alignment(predictions, targets)
        
        assert result is False

