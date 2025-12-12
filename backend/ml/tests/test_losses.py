"""
Tests for loss functions.
"""
import pytest
import torch
import torch.nn as nn
from ml.utils.losses import UncertaintyWeightedLoss


class TestUncertaintyWeightedLoss:
    """Tests for UncertaintyWeightedLoss class."""
    
    def test_initialization(self):
        """Test loss initialization."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        assert len(loss.log_sigmas) == 4
        assert loss.log_sigmas.requires_grad
        assert len(loss.TARGETS) == 4
    
    def test_forward_perfect_prediction(self):
        """Test forward pass with perfect predictions."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        batch_size = 5
        predictions = torch.randn(batch_size, 4)
        targets = predictions.clone()
        
        loss_value = loss(predictions, targets)
        
        assert isinstance(loss_value, torch.Tensor)
        assert loss_value.item() >= 0.0
        assert loss_value.requires_grad
    
    def test_forward_with_errors(self):
        """Test forward pass with prediction errors."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        batch_size = 5
        predictions = torch.randn(batch_size, 4)
        targets = torch.randn(batch_size, 4)
        
        loss_value = loss(predictions, targets)
        
        assert isinstance(loss_value, torch.Tensor)
        assert loss_value.item() > 0.0
    
    def test_forward_1d_arrays(self):
        """Test forward pass with 1D arrays."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.randn(4)
        targets = torch.randn(4)
        
        loss_value = loss(predictions, targets)
        
        assert isinstance(loss_value, torch.Tensor)
        assert loss_value.dim() == 0
    
    def test_forward_more_columns_than_targets(self):
        """Test forward pass with more columns than targets."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        batch_size = 5
        predictions = torch.randn(batch_size, 6)
        targets = torch.randn(batch_size, 6)
        
        loss_value = loss(predictions, targets)
        
        assert isinstance(loss_value, torch.Tensor)
        assert loss_value.item() >= 0.0
    
    def test_get_sigmas(self):
        """Test getting sigma values."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        sigmas = loss.get_sigmas()
        
        assert isinstance(sigmas, dict)
        assert len(sigmas) == 4
        assert all(target in sigmas for target in loss.TARGETS)
        assert all(isinstance(v, float) and v > 0 for v in sigmas.values())
    
    def test_loss_gradient_flow(self):
        """Test that loss allows gradient flow."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        batch_size = 5
        predictions = torch.randn(batch_size, 4, requires_grad=True)
        targets = torch.randn(batch_size, 4)
        
        loss_value = loss(predictions, targets)
        loss_value.backward()
        
        assert predictions.grad is not None
        assert loss.log_sigmas.grad is not None
    
    def test_different_initial_sigma(self):
        """Test initialization with different initial sigma."""
        loss = UncertaintyWeightedLoss(initial_sigma=0.5)
        
        sigmas = loss.get_sigmas()
        avg_sigma = sum(sigmas.values()) / len(sigmas)
        
        assert avg_sigma > 0.0

