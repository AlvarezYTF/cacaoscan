"""
Tests for utils losses module.
"""
import torch
import torch.nn as nn
from unittest import TestCase
from unittest.mock import patch

from ml.utils.losses import UncertaintyWeightedLoss


class UncertaintyWeightedLossTest(TestCase):
    """Tests for UncertaintyWeightedLoss class."""

    def test_uncertainty_weighted_loss_initialization(self):
        """Test UncertaintyWeightedLoss initialization."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        self.assertEqual(len(loss.log_sigmas), 4)
        self.assertIsInstance(loss.log_sigmas, nn.Parameter)

    def test_uncertainty_weighted_loss_forward(self):
        """Test UncertaintyWeightedLoss forward pass."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        batch_size = 4
        predictions = torch.randn(batch_size, 4)
        targets = torch.randn(batch_size, 4)

        with patch('builtins.print'):
            total_loss = loss(predictions, targets)
        
        self.assertIsInstance(total_loss, torch.Tensor)
        self.assertEqual(total_loss.dim(), 0)

    def test_uncertainty_weighted_loss_forward_1d(self):
        """Test UncertaintyWeightedLoss forward with 1D tensors."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.randn(4)
        targets = torch.randn(4)

        with patch('builtins.print'):
            total_loss = loss(predictions, targets)
        
        self.assertIsInstance(total_loss, torch.Tensor)

    def test_uncertainty_weighted_loss_get_sigmas(self):
        """Test getting sigmas from loss."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        sigmas = loss.get_sigmas()
        
        self.assertEqual(len(sigmas), 4)
        self.assertTrue(all(v > 0 for v in sigmas.values()))

