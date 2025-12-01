"""
Unit tests for loss functions (losses.py).
Tests UncertaintyWeightedLoss with various scenarios.
"""
import pytest
import torch
import numpy as np
from unittest.mock import patch

from ml.utils.losses import UncertaintyWeightedLoss


@pytest.fixture
def sample_predictions():
    """Create sample predictions tensor."""
    return torch.tensor([
        [20.0, 12.0, 8.0, 1.5],
        [25.0, 15.0, 9.0, 1.8],
        [30.0, 18.0, 10.0, 2.0]
    ], dtype=torch.float32)


@pytest.fixture
def sample_targets():
    """Create sample targets tensor."""
    return torch.tensor([
        [19.5, 11.8, 7.9, 1.4],
        [24.8, 14.9, 8.9, 1.7],
        [29.9, 17.8, 9.9, 1.9]
    ], dtype=torch.float32)


class TestUncertaintyWeightedLoss:
    """Tests for UncertaintyWeightedLoss class."""
    
    def test_initialization_default(self):
        """Test UncertaintyWeightedLoss initialization with defaults."""
        loss_fn = UncertaintyWeightedLoss()
        
        assert loss_fn.initial_sigma == 0.3
        assert len(loss_fn.log_sigmas) == 4  # 4 targets
        assert loss_fn.log_sigmas.requires_grad is True
    
    def test_initialization_custom_sigma(self):
        """Test UncertaintyWeightedLoss initialization with custom sigma."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.5)
        
        assert loss_fn.initial_sigma == 0.5
        sigmas = torch.exp(loss_fn.log_sigmas)
        # Check that sigmas are close to initial value
        assert torch.allclose(sigmas, torch.tensor([0.5]), atol=0.1)
    
    def test_initialization_independent_parameters(self):
        """Test that each target has independent sigma parameter."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        assert len(loss_fn.log_sigmas) == 4
        # All should be learnable parameters
        assert loss_fn.log_sigmas.requires_grad is True
    
    def test_forward_basic(self, sample_predictions, sample_targets):
        """Test basic forward pass."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        loss = loss_fn(sample_predictions, sample_targets)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.shape == ()  # Scalar
        assert loss.item() >= 0  # Loss should be non-negative
    
    def test_forward_perfect_predictions(self):
        """Test forward pass with perfect predictions."""
        predictions = torch.tensor([[20.0, 12.0, 8.0, 1.5]], dtype=torch.float32)
        targets = torch.tensor([[20.0, 12.0, 8.0, 1.5]], dtype=torch.float32)
        
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        loss = loss_fn(predictions, targets)
        
        # Loss should be small but not zero (due to log(sigma) term)
        assert loss.item() >= 0
        assert loss.item() < 10.0  # Should be relatively small
    
    def test_forward_different_batch_sizes(self):
        """Test forward pass with different batch sizes."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        for batch_size in [1, 2, 4, 8, 16]:
            predictions = torch.randn(batch_size, 4, dtype=torch.float32)
            targets = torch.randn(batch_size, 4, dtype=torch.float32)
            
            loss = loss_fn(predictions, targets)
            
            assert isinstance(loss, torch.Tensor)
            assert loss.shape == ()  # Scalar
            assert loss.item() >= 0
    
    def test_forward_handles_1d_tensors(self):
        """Test forward pass with 1D tensors (single sample)."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.tensor([20.0, 12.0, 8.0, 1.5], dtype=torch.float32)
        targets = torch.tensor([19.5, 11.8, 7.9, 1.4], dtype=torch.float32)
        
        loss = loss_fn(predictions, targets)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.shape == ()  # Scalar
    
    def test_forward_handles_extra_columns(self):
        """Test forward pass when predictions have extra columns."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.randn(2, 6, dtype=torch.float32)  # 6 columns
        targets = torch.randn(2, 4, dtype=torch.float32)      # 4 columns
        
        # Should handle gracefully by truncating
        loss = loss_fn(predictions, targets)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.shape == ()
    
    def test_forward_shape_mismatch_raises_error(self):
        """Test that shape mismatch raises assertion error."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.randn(2, 4, dtype=torch.float32)
        targets = torch.randn(3, 4, dtype=torch.float32)  # Different batch size
        
        with pytest.raises(AssertionError, match="Mismatch shapes"):
            loss_fn(predictions, targets)
    
    def test_get_sigmas(self):
        """Test get_sigmas method."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        sigmas = loss_fn.get_sigmas()
        
        assert isinstance(sigmas, dict)
        assert len(sigmas) == 4
        assert all(target in sigmas for target in ['alto', 'ancho', 'grosor', 'peso'])
        assert all(isinstance(v, float) for v in sigmas.values())
        assert all(v > 0 for v in sigmas.values())
    
    def test_get_sigmas_after_training_step(self, sample_predictions, sample_targets):
        """Test get_sigmas after a training step."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        # Get initial sigmas
        initial_sigmas = loss_fn.get_sigmas()
        
        # Forward pass
        loss = loss_fn(sample_predictions, sample_targets)
        
        # Backward pass (simulates training step)
        loss.backward()
        
        # Get sigmas after backward
        final_sigmas = loss_fn.get_sigmas()
        
        # Sigmas should still be valid
        assert isinstance(final_sigmas, dict)
        assert len(final_sigmas) == 4
        assert all(v > 0 for v in final_sigmas.values())
    
    def test_loss_decreases_with_better_predictions(self):
        """Test that loss decreases when predictions improve."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        targets = torch.tensor([[20.0, 12.0, 8.0, 1.5]], dtype=torch.float32)
        
        # Bad predictions
        bad_predictions = torch.tensor([[30.0, 20.0, 15.0, 3.0]], dtype=torch.float32)
        bad_loss = loss_fn(bad_predictions, targets)
        
        # Good predictions
        good_predictions = torch.tensor([[20.1, 12.1, 8.1, 1.6]], dtype=torch.float32)
        good_loss = loss_fn(good_predictions, targets)
        
        assert good_loss.item() < bad_loss.item()
    
    def test_loss_is_differentiable(self, sample_predictions, sample_targets):
        """Test that loss is differentiable."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        loss = loss_fn(sample_predictions, sample_targets)
        
        # Should be able to compute gradients
        loss.backward()
        
        # Check that gradients exist for log_sigmas
        assert loss_fn.log_sigmas.grad is not None
        assert not torch.isnan(loss_fn.log_sigmas.grad).any()
    
    def test_sigmas_are_learnable(self):
        """Test that sigmas are learnable parameters."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        initial_sigmas = loss_fn.get_sigmas()
        
        # Create optimizer
        optimizer = torch.optim.Adam([loss_fn.log_sigmas], lr=0.01)
        
        # Training step
        predictions = torch.randn(2, 4, dtype=torch.float32)
        targets = torch.randn(2, 4, dtype=torch.float32)
        
        for _ in range(10):
            optimizer.zero_grad()
            loss = loss_fn(predictions, targets)
            loss.backward()
            optimizer.step()
        
        final_sigmas = loss_fn.get_sigmas()
        
        # Sigmas should have changed (learned)
        assert initial_sigmas != final_sigmas
    
    def test_loss_handles_nan_predictions(self):
        """Test that loss handles NaN predictions gracefully."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.tensor([[float('nan'), 12.0, 8.0, 1.5]], dtype=torch.float32)
        targets = torch.tensor([[20.0, 12.0, 8.0, 1.5]], dtype=torch.float32)
        
        loss = loss_fn(predictions, targets)
        
        # Should either raise error or return NaN
        assert torch.isnan(loss) or torch.isinf(loss) or loss.item() > 0
    
    def test_loss_handles_inf_predictions(self):
        """Test that loss handles Inf predictions."""
        loss_fn = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        predictions = torch.tensor([[float('inf'), 12.0, 8.0, 1.5]], dtype=torch.float32)
        targets = torch.tensor([[20.0, 12.0, 8.0, 1.5]], dtype=torch.float32)
        
        loss = loss_fn(predictions, targets)
        
        # Should either raise error or return Inf/NaN
        assert torch.isnan(loss) or torch.isinf(loss) or loss.item() > 0
    
    def test_loss_with_state_dict(self):
        """Test that loss function can save/load state dict."""
        loss_fn1 = UncertaintyWeightedLoss(initial_sigma=0.3)
        
        # Modify sigmas
        with torch.no_grad():
            loss_fn1.log_sigmas.data += 0.1
        
        state_dict = loss_fn1.state_dict()
        
        # Create new loss function and load state
        loss_fn2 = UncertaintyWeightedLoss(initial_sigma=0.3)
        loss_fn2.load_state_dict(state_dict)
        
        # Check that sigmas match
        sigmas1 = loss_fn1.get_sigmas()
        sigmas2 = loss_fn2.get_sigmas()
        
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            assert abs(sigmas1[target] - sigmas2[target]) < 1e-6

