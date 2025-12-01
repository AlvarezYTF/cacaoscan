"""
Tests for utils early_stopping module.
"""
import torch
import torch.optim as optim
from unittest import TestCase
from unittest.mock import MagicMock

from ml.utils.early_stopping import IntelligentEarlyStopping


class IntelligentEarlyStoppingTest(TestCase):
    """Tests for IntelligentEarlyStopping class."""

    def test_early_stopping_initialization(self):
        """Test IntelligentEarlyStopping initialization."""
        early_stopping = IntelligentEarlyStopping(
            patience=8,
            min_delta_percent=0.01,
            r2_threshold=-2.0,
            r2_consecutive=2,
            val_loss_increase_epochs=3
        )

        self.assertEqual(early_stopping.patience, 8)
        self.assertEqual(early_stopping.min_delta_percent, 0.01)
        self.assertEqual(early_stopping.r2_threshold, -2.0)
        self.assertEqual(early_stopping.best_val_loss, float('inf'))

    def test_early_stopping_call_improvement(self):
        """Test early stopping with improvement."""
        early_stopping = IntelligentEarlyStopping(patience=8)
        
        should_stop, is_best, should_reduce_lr, should_rollback = early_stopping(
            epoch=1,
            val_loss=1.0,
            r2_scores={'alto': 0.5, 'ancho': 0.6, 'grosor': 0.4, 'peso': 0.7}
        )

        self.assertFalse(should_stop)
        self.assertTrue(is_best)
        self.assertFalse(should_reduce_lr)
        self.assertFalse(should_rollback)

    def test_early_stopping_call_no_improvement(self):
        """Test early stopping with no improvement."""
        early_stopping = IntelligentEarlyStopping(patience=2)
        
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.5, 'ancho': 0.6, 'grosor': 0.4, 'peso': 0.7})
        early_stopping(epoch=2, val_loss=1.1, r2_scores={'alto': 0.5, 'ancho': 0.6, 'grosor': 0.4, 'peso': 0.7})
        should_stop, is_best, _, _ = early_stopping(
            epoch=3,
            val_loss=1.2,
            r2_scores={'alto': 0.5, 'ancho': 0.6, 'grosor': 0.4, 'peso': 0.7}
        )

        self.assertTrue(should_stop)
        self.assertFalse(is_best)

    def test_early_stopping_reset(self):
        """Test resetting early stopping state."""
        early_stopping = IntelligentEarlyStopping(patience=8)
        early_stopping(epoch=1, val_loss=1.0, r2_scores={'alto': 0.5, 'ancho': 0.6, 'grosor': 0.4, 'peso': 0.7})
        
        early_stopping.reset()

        self.assertEqual(early_stopping.best_val_loss, float('inf'))
        self.assertEqual(early_stopping.counter, 0)

