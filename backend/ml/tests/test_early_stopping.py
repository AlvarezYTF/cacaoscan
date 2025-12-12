"""
Tests for early stopping utilities.
"""
import pytest
from unittest.mock import MagicMock
from ml.utils.early_stopping import IntelligentEarlyStopping


class TestIntelligentEarlyStopping:
    """Tests for IntelligentEarlyStopping class."""
    
    @pytest.fixture
    def early_stopping(self):
        """Create early stopping instance."""
        return IntelligentEarlyStopping(
            patience=8,
            min_delta_percent=0.01,
            r2_threshold=-2.0,
            r2_consecutive=2,
            val_loss_increase_epochs=3
        )
    
    @pytest.fixture
    def optimizer(self):
        """Create mock optimizer."""
        optimizer = MagicMock()
        optimizer.param_groups = [{'lr': 0.001}]
        return optimizer
    
    def test_initialization(self, early_stopping):
        """Test early stopping initialization."""
        assert early_stopping.patience == 8
        assert early_stopping.min_delta_percent == 0.01
        assert early_stopping.best_val_loss == float('inf')
        assert early_stopping.counter == 0
        assert len(early_stopping.low_r2_count) == 4
    
    def test_first_epoch_is_best(self, early_stopping):
        """Test that first epoch is always considered best."""
        val_loss = 0.5
        r2_scores = {'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=val_loss,
            r2_scores=r2_scores
        )
        
        assert is_best
        assert not should_stop
        assert early_stopping.best_val_loss == val_loss
        assert early_stopping.best_epoch == 1
    
    def test_improvement_detection(self, early_stopping):
        """Test improvement detection."""
        # First epoch
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Second epoch with improvement
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=2,
            val_loss=0.9,  # Improved by more than 1%
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert is_best
        assert early_stopping.best_val_loss == 0.9
        assert early_stopping.counter == 0
    
    def test_no_improvement_increases_counter(self, early_stopping):
        """Test that no improvement increases counter."""
        # First epoch
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Second epoch without improvement
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=2,
            val_loss=1.01,  # No improvement
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert not is_best
        assert early_stopping.counter == 1
    
    def test_early_stopping_triggered(self, early_stopping):
        """Test that early stopping is triggered after patience."""
        # First epoch
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Run epochs without improvement
        for epoch in range(2, 10):
            should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
                epoch=epoch,
                val_loss=1.01,
                r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
            )
            
            if should_stop:
                assert epoch >= 9  # Should stop after patience (8) epochs
                break
        
        assert should_stop
    
    def test_low_r2_triggers_lr_reduction(self, early_stopping, optimizer):
        """Test that low R² triggers learning rate reduction."""
        # First epoch
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Two consecutive epochs with low R²
        for epoch in range(2, 4):
            should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
                epoch=epoch,
                val_loss=1.0,
                r2_scores={'alto': -3.0, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6},  # Low R² for alto
                optimizer=optimizer
            )
        
        assert should_reduce_lr
        assert optimizer.param_groups[0]['lr'] == 0.0005  # Reduced by half
    
    def test_val_loss_increase_triggers_rollback(self, early_stopping):
        """Test that increasing val loss triggers rollback."""
        # First epoch
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        # Three consecutive epochs with increasing loss
        for epoch in range(2, 5):
            should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
                epoch=epoch,
                val_loss=1.0 + (epoch - 1) * 0.1,  # Increasing loss
                r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
            )
        
        assert should_rollback
    
    def test_reset(self, early_stopping):
        """Test reset functionality."""
        # Run some epochs
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        early_stopping(epoch=2, val_loss=1.01, r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6})
        
        assert early_stopping.counter > 0
        
        early_stopping.reset()
        
        assert early_stopping.best_val_loss == float('inf')
        assert early_stopping.counter == 0
        assert early_stopping.best_epoch == 0
        assert all(count == 0 for count in early_stopping.low_r2_count.values())
    
    def test_negative_val_loss(self, early_stopping):
        """Test handling of negative validation loss."""
        # First epoch with negative loss
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=-1.0,
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert is_best
        assert early_stopping.best_val_loss == -1.0
        
        # Second epoch with better (more negative) loss
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=2,
            val_loss=-1.1,  # Better (more negative)
            r2_scores={'alto': 0.9, 'ancho': 0.8, 'grosor': 0.7, 'peso': 0.6}
        )
        
        assert is_best
        assert early_stopping.best_val_loss == -1.1

