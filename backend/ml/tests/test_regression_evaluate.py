"""
Tests for regression evaluate module.
"""
import torch
import torch.nn as nn
import numpy as np
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ml.regression.evaluate import (
    compute_regression_metrics,
    RegressionEvaluator
)


class ComputeRegressionMetricsTest(TestCase):
    """Tests for compute_regression_metrics function."""

    def test_compute_regression_metrics_basic(self):
        """Test computing basic regression metrics."""
        targets = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        predictions = np.array([1.1, 2.1, 2.9, 4.1, 4.9])

        metrics = compute_regression_metrics(targets, predictions)

        self.assertIn('mae', metrics)
        self.assertIn('mse', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('r2', metrics)
        self.assertIn('mape', metrics)
        self.assertIn('relative_error', metrics)

        self.assertIsInstance(metrics['mae'], float)
        self.assertIsInstance(metrics['mse'], float)
        self.assertIsInstance(metrics['rmse'], float)
        self.assertIsInstance(metrics['r2'], float)

    def test_compute_regression_metrics_zero_targets(self):
        """Test computing metrics with zero targets."""
        targets = np.array([0.0, 0.0, 0.0])
        predictions = np.array([0.1, 0.2, 0.3])

        metrics = compute_regression_metrics(targets, predictions)

        self.assertEqual(metrics['mape'], 0.0)
        self.assertEqual(metrics['relative_error'], 0.0)


class RegressionEvaluatorTest(TestCase):
    """Tests for RegressionEvaluator class."""

    def test_regression_evaluator_initialization(self):
        """Test RegressionEvaluator initialization."""
        model = nn.Linear(10, 4)
        test_loader = MagicMock()
        device = torch.device('cpu')

        evaluator = RegressionEvaluator(model, test_loader, device=device)

        self.assertEqual(evaluator.model, model)
        self.assertEqual(evaluator.test_loader, test_loader)
        self.assertEqual(evaluator.device, device)

    def test_regression_evaluator_with_scalers(self):
        """Test RegressionEvaluator with scalers."""
        model = nn.Linear(10, 4)
        test_loader = MagicMock()
        scalers = MagicMock()
        device = torch.device('cpu')

        evaluator = RegressionEvaluator(model, test_loader, scalers=scalers, device=device)

        self.assertEqual(evaluator.scalers, scalers)

