"""
Tests for hybrid v2 training pipeline.
"""
import pytest
from unittest.mock import patch, MagicMock
from ml.pipeline.hybrid_v2_training import train_hybrid_v2


class TestTrainHybridV2:
    """Tests for train_hybrid_v2 function."""
    
    @patch('ml.pipeline.hybrid_v2_training.train_hybrid_model')
    def test_train_hybrid_v2_basic(self, mock_train):
        """Test train_hybrid_v2 with basic config."""
        mock_train.return_value = {
            'best_val_loss': 0.5,
            'best_avg_r2': 0.9,
            'epochs_trained': 10
        }
        
        config = {
            'model': {
                'backbone_name': 'convnext_tiny',
                'pixel_dim': 10
            },
            'training': {
                'num_epochs': 10,
                'batch_size': 16,
                'learning_rate': 1e-4
            }
        }
        
        result = train_hybrid_v2(config)
        
        assert isinstance(result, dict)
        assert 'best_val_loss' in result or mock_train.called


