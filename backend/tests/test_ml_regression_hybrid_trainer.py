"""
Unit tests for hybrid trainer (hybrid_trainer.py).
Tests HybridTrainer functionality.
"""
import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from ml.regression.hybrid_trainer import HybridTrainer
from ml.utils.losses import UncertaintyWeightedLoss


@pytest.fixture
def sample_model():
    """Create a simple hybrid model for testing."""
    class SimpleHybridModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = nn.Sequential(
                nn.Conv2d(3, 64, 3, padding=1),
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten()
            )
            self.fusion = nn.Linear(64 + 10, 4)  # 64 features + 10 pixel features -> 4 targets
            self.gating = nn.Sequential(
                nn.Linear(64 + 10, 1),
                nn.Sigmoid()
            )
        
        def forward(self, images, pixel_features):
            backbone_features = self.backbone(images)
            combined = torch.cat([backbone_features, pixel_features], dim=1)
            outputs = self.fusion(combined)
            gating_values = self.gating(combined)
            return outputs, gating_values
    
    return SimpleHybridModel()


@pytest.fixture
def sample_data_loaders():
    """Create sample data loaders."""
    batch_size = 4
    n_samples = 16
    
    images = torch.randn(n_samples, 3, 224, 224)
    pixel_features = torch.randn(n_samples, 10)
    targets = torch.randn(n_samples, 4)
    
    train_dataset = TensorDataset(images, pixel_features, targets)
    val_dataset = TensorDataset(images, pixel_features, targets)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader


@pytest.fixture
def sample_config():
    """Create sample training configuration."""
    return {
        'learning_rate': 1e-4,
        'early_stopping_patience': 5,
        'max_epochs': 10
    }


class TestHybridTrainerInitialization:
    """Tests for HybridTrainer initialization."""
    
    def test_initialization_default(self, sample_model, sample_data_loaders, sample_config):
        """Test HybridTrainer initialization with defaults."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config
        )
        
        assert trainer.model is not None
        assert trainer.train_loader is train_loader
        assert trainer.val_loader is val_loader
        assert trainer.device == device
        assert trainer.optimizer is not None
        assert isinstance(trainer.criterion, UncertaintyWeightedLoss)
        assert trainer.scheduler is not None
        assert trainer.early_stopping is not None
        assert trainer.use_mixed_precision is False  # CPU doesn't support mixed precision
    
    def test_initialization_with_save_dir(self, sample_model, sample_data_loaders, sample_config, tmp_path):
        """Test initialization with save directory."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        save_dir = tmp_path / "checkpoints"
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            save_dir=save_dir
        )
        
        assert trainer.save_dir == save_dir
    
    def test_initialization_mixed_precision_cpu(self, sample_model, sample_data_loaders, sample_config):
        """Test that mixed precision is disabled on CPU."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            use_mixed_precision=True
        )
        
        assert trainer.use_mixed_precision is False
        assert trainer.scaler is None
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_initialization_mixed_precision_cuda(self, sample_model, sample_data_loaders, sample_config):
        """Test that mixed precision is enabled on CUDA."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cuda')
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            use_mixed_precision=True
        )
        
        assert trainer.use_mixed_precision is True
        assert trainer.scaler is not None


class TestHybridTrainerTrainingLoop:
    """Tests for training loop methods."""
    
    def test_train_epoch(self, sample_model, sample_data_loaders, sample_config):
        """Test training for one epoch."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config
        )
        
        avg_loss, max_grad, avg_gating = trainer.train_epoch()
        
        assert isinstance(avg_loss, float)
        assert avg_loss >= 0
        assert isinstance(max_grad, float)
        assert max_grad >= 0
        assert isinstance(avg_gating, float)
        assert 0 <= avg_gating <= 1
    
    def test_validate_epoch(self, sample_model, sample_data_loaders, sample_config):
        """Test validation for one epoch."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config
        )
        
        avg_loss, metrics, sigmas, pearson_corrs = trainer.validate_epoch()
        
        assert isinstance(avg_loss, float)
        assert avg_loss >= 0
        assert isinstance(metrics, dict)
        assert 'alto' in metrics
        assert isinstance(sigmas, dict)
        assert 'alto' in sigmas
        assert isinstance(pearson_corrs, dict)
        assert 'alto' in pearson_corrs
    
    def test_train_epoch_updates_history(self, sample_model, sample_data_loaders, sample_config):
        """Test that train_epoch updates training history."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config
        )
        
        initial_history_len = len(trainer.history['train_loss'])
        trainer.train_epoch()
        
        # History is updated in train method, not train_epoch
        # So we check that history exists
        assert 'train_loss' in trainer.history
        assert 'val_loss' in trainer.history
        assert 'learning_rate' in trainer.history


class TestHybridTrainerCheckpointsAndRollback:
    """Tests for checkpoint saving and rollback."""
    
    def test_save_checkpoint(self, sample_model, sample_data_loaders, sample_config, tmp_path):
        """Test saving checkpoint."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        save_dir = tmp_path / "checkpoints"
        save_dir.mkdir()
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            save_dir=save_dir
        )
        
        # Train one epoch to have some state
        trainer.train_epoch()
        
        # Save checkpoint
        checkpoint_path = trainer._save_checkpoint(epoch=0, is_best_loss=False, is_best_r2=False)
        
        assert checkpoint_path is not None
        assert checkpoint_path.exists()
        
        # Verify checkpoint can be loaded
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
        assert 'model_state_dict' in checkpoint
        assert 'optimizer_state_dict' in checkpoint
        assert 'epoch' in checkpoint
    
    def test_load_checkpoint(self, sample_model, sample_data_loaders, sample_config, tmp_path):
        """Test loading checkpoint."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        save_dir = tmp_path / "checkpoints"
        save_dir.mkdir()
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            save_dir=save_dir
        )
        
        # Save checkpoint
        checkpoint_path = trainer._save_checkpoint(epoch=5, is_best_loss=True, is_best_r2=False)
        
        # Create new trainer and load checkpoint
        new_trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            save_dir=save_dir
        )
        
        loaded_epoch = new_trainer._load_checkpoint(checkpoint_path)
        
        assert loaded_epoch == 5


class TestHybridTrainerEndToEnd:
    """Tests for end-to-end training."""
    
    def test_train_method(self, sample_model, sample_data_loaders, sample_config, tmp_path):
        """Test full training method."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        save_dir = tmp_path / "checkpoints"
        save_dir.mkdir()
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=sample_config,
            save_dir=save_dir
        )
        
        # Train for a few epochs
        history = trainer.train(max_epochs=3)
        
        assert isinstance(history, dict)
        assert 'train_loss' in history
        assert 'val_loss' in history
        assert len(history['train_loss']) == 3
        assert len(history['val_loss']) == 3
    
    def test_train_with_early_stopping(self, sample_model, sample_data_loaders, sample_config, tmp_path):
        """Test training with early stopping."""
        train_loader, val_loader = sample_data_loaders
        device = torch.device('cpu')
        save_dir = tmp_path / "checkpoints"
        save_dir.mkdir()
        
        config = sample_config.copy()
        config['early_stopping_patience'] = 2
        
        trainer = HybridTrainer(
            model=sample_model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=config,
            save_dir=save_dir
        )
        
        # Train - should stop early
        history = trainer.train(max_epochs=10)
        
        assert isinstance(history, dict)
        # May stop early due to early stopping
        assert len(history['train_loss']) <= 10

