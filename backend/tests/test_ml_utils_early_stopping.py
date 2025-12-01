"""
Unit tests for ML utils early stopping module.
Tests IntelligentEarlyStopping class.
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict

from ml.utils.early_stopping import IntelligentEarlyStopping


@pytest.fixture
def mock_optimizer():
    """Create a mock optimizer for testing."""
    optimizer = Mock()
    optimizer.param_groups = [{'lr': 0.001}]
    return optimizer


@pytest.fixture
def early_stopping():
    """Create an IntelligentEarlyStopping instance for testing."""
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
    
    def test_first_epoch_is_best(self, early_stopping):
        """Test that first epoch is always considered best."""
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=0,
            val_loss=1.0,
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert is_best is True
        assert should_stop is False
        assert early_stopping.best_val_loss == 1.0
        assert early_stopping.best_epoch == 0
    
    def test_improvement_detection(self, early_stopping):
        """Test improvement detection."""
        # First epoch
        early_stopping(epoch=0, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Second epoch with improvement
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=0.9,
            r2_scores={'alto': 0.95, 'ancho': 0.85, 'grosor': 0.75, 'peso': 0.65}
        )
        
        assert is_best is True
        assert early_stopping.best_val_loss == 0.9
        assert early_stopping.best_epoch == 1
    
    def test_no_improvement_increments_counter(self, early_stopping):
        """Test that no improvement increments counter."""
        # First epoch
        early_stopping(epoch=0, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Second epoch without significant improvement
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=1.005,  # Less than 1% improvement
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert is_best is False
        assert early_stopping.counter == 1
    
    def test_patience_exceeded_stops_training(self, early_stopping):
        """Test that exceeding patience stops training."""
        # First epoch
        early_stopping(epoch=0, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Simulate 8 epochs without improvement
        for epoch in range(1, 9):
            should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
                epoch=epoch,
                val_loss=1.01,
                r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
            )
        
        assert should_stop is True
        assert early_stopping.counter == 8
    
    def test_low_r2_triggers_lr_reduction(self, early_stopping, mock_optimizer):
        """Test that low R² triggers learning rate reduction."""
        # First epoch
        early_stopping(epoch=0, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Two consecutive epochs with low R²
        early_stopping(
            epoch=1,
            val_loss=1.0,
            r2_scores={'alto': -2.5, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6},
            optimizer=mock_optimizer
        )
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=2,
            val_loss=1.0,
            r2_scores={'alto': -2.5, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6},
            optimizer=mock_optimizer
        )
        
        assert should_reduce_lr is True
        assert mock_optimizer.param_groups[0]['lr'] == 0.0005  # Half of 0.001
    
    def test_val_loss_increase_triggers_rollback(self, early_stopping):
        """Test that consecutive val loss increases trigger rollback."""
        # First epoch
        early_stopping(epoch=0, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Three consecutive epochs with increasing val loss
        early_stopping(epoch=1, val_loss=1.1, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        early_stopping(epoch=2, val_loss=1.2, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=3,
            val_loss=1.3,
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert should_rollback is True
    
    def test_reset_functionality(self, early_stopping):
        """Test reset functionality."""
        # Run some epochs
        early_stopping(epoch=0, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        early_stopping(epoch=1, val_loss=1.01, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Reset
        early_stopping.reset()
        
        assert early_stopping.best_val_loss == float('inf')
        assert early_stopping.best_epoch == 0
        assert early_stopping.counter == 0
        assert all(count == 0 for count in early_stopping.low_r2_count.values())

