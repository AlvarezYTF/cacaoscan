"""
Unit tests for early stopping utility (early_stopping.py).
Tests IntelligentEarlyStopping with various conditions and scenarios.
"""
import pytest
import torch
import torch.optim as optim
from unittest.mock import Mock, MagicMock

from ml.utils.early_stopping import IntelligentEarlyStopping


@pytest.fixture
def sample_optimizer():
    """Create a sample optimizer for testing."""
    params = [torch.nn.Parameter(torch.randn(10, 10))]
    return optim.Adam(params, lr=0.001)


@pytest.fixture
def early_stopping():
    """Create an IntelligentEarlyStopping instance."""
    return IntelligentEarlyStopping(
        patience=8,
        min_delta_percent=0.01,
        r2_threshold=-2.0,
        r2_consecutive=2,
        val_loss_increase_epochs=3
    )


class TestIntelligentEarlyStopping:
    """Tests for IntelligentEarlyStopping class."""
    
    def test_initialization_default(self):
        """Test initialization with default parameters."""
        es = IntelligentEarlyStopping()
        
        assert es.patience == 8
        assert es.min_delta_percent == 0.01
        assert es.r2_threshold == -2.0
        assert es.r2_consecutive == 2
        assert es.val_loss_increase_epochs == 3
        assert es.best_val_loss == float('inf')
        assert es.best_epoch == 0
        assert es.counter == 0
    
    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        es = IntelligentEarlyStopping(
            patience=10,
            min_delta_percent=0.02,
            r2_threshold=-1.5,
            r2_consecutive=3,
            val_loss_increase_epochs=5
        )
        
        assert es.patience == 10
        assert es.min_delta_percent == 0.02
        assert es.r2_threshold == -1.5
        assert es.r2_consecutive == 3
        assert es.val_loss_increase_epochs == 5
    
    def test_check_improvement_first_epoch(self, early_stopping):
        """Test improvement check on first epoch."""
        is_best = early_stopping._check_improvement(0.5)
        assert is_best is True
    
    def test_check_improvement_positive_loss(self, early_stopping):
        """Test improvement check with positive loss values."""
        early_stopping.best_val_loss = 1.0
        
        # Better loss (smaller)
        is_best = early_stopping._check_improvement(0.9)
        assert is_best is True
        
        # Worse loss (larger, but within delta)
        is_best = early_stopping._check_improvement(1.005)
        assert is_best is False
        
        # Worse loss (larger, outside delta)
        is_best = early_stopping._check_improvement(1.02)
        assert is_best is False
    
    def test_check_improvement_negative_loss(self, early_stopping):
        """Test improvement check with negative loss values."""
        early_stopping.best_val_loss = -1.0
        
        # Better loss (larger, less negative)
        is_best = early_stopping._check_improvement(-0.9)
        assert is_best is True
        
        # Worse loss (smaller, more negative)
        is_best = early_stopping._check_improvement(-1.02)
        assert is_best is False
    
    def test_check_low_r2_no_low_r2(self, early_stopping):
        """Test low R² check when all R² scores are good."""
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': 0.6,
            'peso': 0.75
        }
        
        should_reduce = early_stopping._check_low_r2(r2_scores)
        assert should_reduce is False
        assert all(count == 0 for count in early_stopping.low_r2_count.values())
    
    def test_check_low_r2_one_target_low(self, early_stopping):
        """Test low R² check when one target has low R²."""
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': -2.5,  # Low R²
            'peso': 0.75
        }
        
        should_reduce = early_stopping._check_low_r2(r2_scores)
        assert should_reduce is False  # Not consecutive yet
        assert early_stopping.low_r2_count['grosor'] == 1
    
    def test_check_low_r2_consecutive_low(self, early_stopping):
        """Test low R² check with consecutive low R²."""
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': -2.5,  # Low R²
            'peso': 0.75
        }
        
        # First epoch
        should_reduce = early_stopping._check_low_r2(r2_scores)
        assert should_reduce is False
        
        # Second consecutive epoch
        should_reduce = early_stopping._check_low_r2(r2_scores)
        assert should_reduce is True
        assert early_stopping.low_r2_count['grosor'] == 2
    
    def test_check_low_r2_reset_on_improvement(self, early_stopping):
        """Test that low R² counter resets when R² improves."""
        r2_scores_low = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': -2.5,
            'peso': 0.75
        }
        
        # First epoch with low R²
        early_stopping._check_low_r2(r2_scores_low)
        assert early_stopping.low_r2_count['grosor'] == 1
        
        # Second epoch with good R²
        r2_scores_good = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': 0.6,  # Good R²
            'peso': 0.75
        }
        early_stopping._check_low_r2(r2_scores_good)
        assert early_stopping.low_r2_count['grosor'] == 0
    
    def test_check_val_loss_increase_first_epoch(self, early_stopping):
        """Test val loss increase check on first epoch."""
        should_rollback = early_stopping._check_val_loss_increase(0.5)
        assert should_rollback is False
    
    def test_check_val_loss_increase_positive_loss(self, early_stopping):
        """Test val loss increase check with positive loss."""
        early_stopping.last_val_loss = 1.0
        
        # Loss increases
        should_rollback = early_stopping._check_val_loss_increase(1.1)
        assert should_rollback is False  # Not consecutive yet
        assert early_stopping.val_loss_increase_count == 1
        
        # Loss increases again
        should_rollback = early_stopping._check_val_loss_increase(1.2)
        assert should_rollback is False
        assert early_stopping.val_loss_increase_count == 2
        
        # Loss increases third time
        should_rollback = early_stopping._check_val_loss_increase(1.3)
        assert should_rollback is True
        assert early_stopping.val_loss_increase_count == 3
    
    def test_check_val_loss_increase_reset_on_improvement(self, early_stopping):
        """Test that val loss increase counter resets on improvement."""
        early_stopping.last_val_loss = 1.0
        
        # Loss increases
        early_stopping._check_val_loss_increase(1.1)
        assert early_stopping.val_loss_increase_count == 1
        
        # Loss improves
        early_stopping._check_val_loss_increase(0.9)
        assert early_stopping.val_loss_increase_count == 0
    
    def test_update_best_model_first_epoch(self, early_stopping):
        """Test updating best model on first epoch."""
        early_stopping._update_best_model(epoch=1, val_loss=0.5, is_best=True)
        
        assert early_stopping.best_val_loss == 0.5
        assert early_stopping.best_epoch == 1
        assert early_stopping.counter == 0
    
    def test_update_best_model_new_best(self, early_stopping):
        """Test updating best model when new best is found."""
        early_stopping.best_val_loss = 1.0
        early_stopping.best_epoch = 5
        
        early_stopping._update_best_model(epoch=10, val_loss=0.8, is_best=True)
        
        assert early_stopping.best_val_loss == 0.8
        assert early_stopping.best_epoch == 10
        assert early_stopping.counter == 0
    
    def test_update_best_model_no_improvement(self, early_stopping):
        """Test updating when no improvement is made."""
        early_stopping.best_val_loss = 1.0
        early_stopping.best_epoch = 5
        early_stopping.counter = 2
        
        early_stopping._update_best_model(epoch=10, val_loss=1.1, is_best=False)
        
        assert early_stopping.best_val_loss == 1.0
        assert early_stopping.best_epoch == 5
        assert early_stopping.counter == 3
    
    def test_reduce_learning_rate(self, early_stopping, sample_optimizer):
        """Test learning rate reduction."""
        initial_lr = sample_optimizer.param_groups[0]['lr']
        
        early_stopping._reduce_learning_rate(sample_optimizer)
        
        new_lr = sample_optimizer.param_groups[0]['lr']
        assert new_lr == initial_lr * 0.5
    
    def test_call_first_epoch(self, early_stopping, sample_optimizer):
        """Test __call__ on first epoch."""
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': 0.6,
            'peso': 0.75
        }
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=0.5,
            r2_scores=r2_scores,
            optimizer=sample_optimizer
        )
        
        assert should_stop is False
        assert is_best is True
        assert should_reduce_lr is False
        assert should_rollback is False
        assert early_stopping.best_val_loss == 0.5
    
    def test_call_early_stopping_triggered(self, early_stopping, sample_optimizer):
        """Test __call__ when early stopping is triggered."""
        early_stopping.best_val_loss = 1.0
        early_stopping.counter = 8  # At patience limit
        
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': 0.6,
            'peso': 0.75
        }
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=10,
            val_loss=1.1,
            r2_scores=r2_scores,
            optimizer=sample_optimizer
        )
        
        assert should_stop is True
    
    def test_call_lr_reduction_triggered(self, early_stopping, sample_optimizer):
        """Test __call__ when LR reduction is triggered."""
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': -2.5,  # Low R²
            'peso': 0.75
        }
        
        # First epoch with low R²
        early_stopping(epoch=1, val_loss=0.5, r2_scores=r2_scores, optimizer=sample_optimizer)
        
        # Second consecutive epoch with low R²
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=2,
            val_loss=0.6,
            r2_scores=r2_scores,
            optimizer=sample_optimizer
        )
        
        assert should_reduce_lr is True
        assert sample_optimizer.param_groups[0]['lr'] < 0.001
    
    def test_call_rollback_triggered(self, early_stopping, sample_optimizer):
        """Test __call__ when rollback is triggered."""
        early_stopping.last_val_loss = 1.0
        
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': 0.6,
            'peso': 0.75
        }
        
        # Three consecutive epochs with increasing loss
        early_stopping(epoch=2, val_loss=1.1, r2_scores=r2_scores, optimizer=sample_optimizer)
        early_stopping(epoch=3, val_loss=1.2, r2_scores=r2_scores, optimizer=sample_optimizer)
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=4,
            val_loss=1.3,
            r2_scores=r2_scores,
            optimizer=sample_optimizer
        )
        
        assert should_rollback is True
    
    def test_reset(self, early_stopping):
        """Test reset method."""
        early_stopping.best_val_loss = 0.5
        early_stopping.best_epoch = 10
        early_stopping.counter = 5
        early_stopping.low_r2_count['alto'] = 2
        early_stopping.val_loss_increase_count = 2
        early_stopping.last_val_loss = 1.0
        
        early_stopping.reset()
        
        assert early_stopping.best_val_loss == float('inf')
        assert early_stopping.best_epoch == 0
        assert early_stopping.counter == 0
        assert all(count == 0 for count in early_stopping.low_r2_count.values())
        assert early_stopping.val_loss_increase_count == 0
        assert early_stopping.last_val_loss == float('inf')
    
    def test_call_without_optimizer(self, early_stopping):
        """Test __call__ without optimizer (should not crash)."""
        r2_scores = {
            'alto': 0.8,
            'ancho': 0.7,
            'grosor': -2.5,
            'peso': 0.75
        }
        
        # Should not raise error even if LR reduction is needed
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=0.5,
            r2_scores=r2_scores,
            optimizer=None
        )
        
        assert should_reduce_lr is False  # Can't reduce without optimizer

