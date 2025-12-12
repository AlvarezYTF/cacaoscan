"""
Tests for hybrid trainer.
"""
import pytest
import torch
import torch.nn as nn
from pathlib import Path
from unittest.mock import patch, MagicMock
from ml.regression.hybrid_trainer import HybridTrainer


class TestHybridTrainer:
    """Tests for HybridTrainer class."""
    
    @pytest.fixture
    def mock_model(self):
        """Create mock hybrid model."""
        class MockHybridModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(10, 4)
            
            def forward(self, images, pixel_features=None):
                if pixel_features is not None:
                    x = torch.cat([images.mean(dim=(2,3)), pixel_features], dim=1)
                else:
                    x = images.mean(dim=(2,3))
                return {
                    'alto': self.fc(x)[:, 0],
                    'ancho': self.fc(x)[:, 1],
                    'grosor': self.fc(x)[:, 2],
                    'peso': self.fc(x)[:, 3]
                }
        
        return MockHybridModel()
    
    @pytest.fixture
    def mock_data_loader(self):
        """Create mock data loader."""
        images = torch.randn(4, 3, 224, 224)
        pixel_features = torch.randn(4, 10)
        targets = {
            'alto': torch.randn(4),
            'ancho': torch.randn(4),
            'grosor': torch.randn(4),
            'peso': torch.randn(4)
        }
        
        dataset = [(images[i:i+2], targets, pixel_features[i:i+2]) for i in range(0, 4, 2)]
        
        class MockLoader:
            def __iter__(self):
                return iter(dataset)
        
        return MockLoader()
    
    @pytest.fixture
    def config(self):
        """Create training config."""
        return {
            'learning_rate': 1e-4,
            'num_epochs': 2,
            'batch_size': 2
        }
    
    def test_initialization(self, mock_model, mock_data_loader, config):
        """Test trainer initialization."""
        device = torch.device('cpu')
        trainer = HybridTrainer(
            model=mock_model,
            train_loader=mock_data_loader,
            val_loader=mock_data_loader,
            device=device,
            config=config,
            use_mixed_precision=False
        )
        
        assert trainer.model == mock_model
        assert trainer.device == device
        assert trainer.config == config
        assert trainer.optimizer is not None
        assert trainer.criterion is not None
    
    def test_initialization_with_save_dir(self, mock_model, mock_data_loader, config, tmp_path):
        """Test trainer initialization with save directory."""
        device = torch.device('cpu')
        save_dir = tmp_path / "checkpoints"
        
        trainer = HybridTrainer(
            model=mock_model,
            train_loader=mock_data_loader,
            val_loader=mock_data_loader,
            device=device,
            config=config,
            save_dir=save_dir,
            use_mixed_precision=False
        )
        
        assert trainer.save_dir == save_dir


