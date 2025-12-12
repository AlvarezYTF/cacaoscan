"""
Tests for metrics utilities.
"""
import pytest
import numpy as np
from ml.regression.metrics import (
    calculate_metrics,
    calculate_metrics_per_target,
    print_metrics_summary
)


class TestCalculateMetrics:
    """Tests for calculate_metrics function."""
    
    def test_calculate_metrics_perfect_prediction(self):
        """Test metrics with perfect predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        metrics = calculate_metrics(y_true, y_pred)
        
        assert metrics['r2'] == pytest.approx(1.0, abs=1e-6)
        assert metrics['mae'] == pytest.approx(0.0, abs=1e-6)
        assert metrics['rmse'] == pytest.approx(0.0, abs=1e-6)
    
    def test_calculate_metrics_with_errors(self):
        """Test metrics with prediction errors."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        metrics = calculate_metrics(y_true, y_pred)
        
        assert metrics['r2'] > 0.0
        assert metrics['mae'] == pytest.approx(0.5, abs=1e-6)
        assert metrics['rmse'] > 0.0
    
    def test_calculate_metrics_with_nan_values(self):
        """Test metrics handling NaN values."""
        y_true = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        y_pred = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        metrics = calculate_metrics(y_true, y_pred, target_name="test")
        
        assert 'r2' in metrics
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert np.isfinite(metrics['r2'])
    
    def test_calculate_metrics_with_inf_values(self):
        """Test metrics handling Inf values."""
        y_true = np.array([1.0, 2.0, np.inf, 4.0, 5.0])
        y_pred = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        metrics = calculate_metrics(y_true, y_pred, target_name="test")
        
        assert 'r2' in metrics
        assert 'mae' in metrics
        assert 'rmse' in metrics
    
    def test_calculate_metrics_empty_arrays(self):
        """Test metrics with empty arrays."""
        y_true = np.array([])
        y_pred = np.array([])
        
        metrics = calculate_metrics(y_true, y_pred, target_name="test")
        
        assert metrics['r2'] == 0.0
        assert metrics['mae'] == 0.0
        assert metrics['rmse'] == 0.0
    
    def test_calculate_metrics_2d_arrays(self):
        """Test metrics with 2D arrays (should flatten)."""
        y_true = np.array([[1.0], [2.0], [3.0]])
        y_pred = np.array([[1.0], [2.0], [3.0]])
        
        metrics = calculate_metrics(y_true, y_pred)
        
        assert metrics['r2'] == pytest.approx(1.0, abs=1e-6)
        assert metrics['mae'] == pytest.approx(0.0, abs=1e-6)


class TestCalculateMetricsPerTarget:
    """Tests for calculate_metrics_per_target function."""
    
    def test_calculate_metrics_per_target_success(self):
        """Test metrics calculation for multiple targets."""
        y_true = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        y_pred = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        
        metrics = calculate_metrics_per_target(y_true, y_pred)
        
        assert 'alto' in metrics
        assert 'ancho' in metrics
        assert metrics['alto']['r2'] == pytest.approx(1.0, abs=1e-6)
        assert metrics['ancho']['r2'] == pytest.approx(1.0, abs=1e-6)
    
    def test_calculate_metrics_per_target_missing_target(self):
        """Test metrics when target is missing in predictions."""
        y_true = {
            'alto': np.array([1.0, 2.0, 3.0]),
            'ancho': np.array([2.0, 3.0, 4.0])
        }
        y_pred = {
            'alto': np.array([1.0, 2.0, 3.0])
        }
        
        metrics = calculate_metrics_per_target(y_true, y_pred)
        
        assert 'alto' in metrics
        assert 'ancho' not in metrics


class TestPrintMetricsSummary:
    """Tests for print_metrics_summary function."""
    
    def test_print_metrics_summary_without_epoch(self, caplog):
        """Test printing metrics summary without epoch."""
        metrics = {
            'alto': {'r2': 0.95, 'mae': 0.5, 'rmse': 0.7},
            'ancho': {'r2': 0.90, 'mae': 0.6, 'rmse': 0.8}
        }
        
        print_metrics_summary(metrics)
        
        assert 'Metrics Summary' in caplog.text
        assert 'ALTO' in caplog.text
        assert 'ANCHO' in caplog.text
    
    def test_print_metrics_summary_with_epoch(self, caplog):
        """Test printing metrics summary with epoch."""
        metrics = {
            'alto': {'r2': 0.95, 'mae': 0.5, 'rmse': 0.7}
        }
        
        print_metrics_summary(metrics, epoch=10)
        
        assert 'Metrics Epoch 10' in caplog.text
        assert 'ALTO' in caplog.text

