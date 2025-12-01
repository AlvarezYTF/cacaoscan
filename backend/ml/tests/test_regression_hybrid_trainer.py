"""
Tests for regression hybrid_trainer module.
"""
import torch
import torch.nn as nn
from unittest import TestCase
from unittest.mock import MagicMock, patch
from pathlib import Path

from ml.regression.hybrid_trainer import HybridTrainer


class HybridTrainerTest(TestCase):
    """Tests for HybridTrainer class."""

    def test_hybrid_trainer_initialization(self):
        """Test HybridTrainer initialization."""
        model = nn.Linear(10, 4)
        train_loader = MagicMock()
        val_loader = MagicMock()
        device = torch.device('cpu')
        config = {
            'learning_rate': 1e-4,
            'early_stopping_patience': 15
        }

        trainer = HybridTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=config
        )

        self.assertEqual(trainer.model, model)
        self.assertEqual(trainer.train_loader, train_loader)
        self.assertEqual(trainer.val_loader, val_loader)
        self.assertEqual(trainer.device, device)
        self.assertIsNotNone(trainer.optimizer)
        self.assertIsNotNone(trainer.criterion)
        self.assertIsNotNone(trainer.scheduler)
        self.assertIsNotNone(trainer.early_stopping)

    def test_hybrid_trainer_with_save_dir(self):
        """Test HybridTrainer with save directory."""
        model = nn.Linear(10, 4)
        train_loader = MagicMock()
        val_loader = MagicMock()
        device = torch.device('cpu')
        config = {'learning_rate': 1e-4}
        save_dir = Path('/tmp/test_save')

        trainer = HybridTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=config,
            save_dir=save_dir
        )

        self.assertEqual(trainer.save_dir, save_dir)

    def test_hybrid_trainer_mixed_precision(self):
        """Test HybridTrainer with mixed precision."""
        model = nn.Linear(10, 4)
        train_loader = MagicMock()
        val_loader = MagicMock()
        device = torch.device('cpu')
        config = {'learning_rate': 1e-4}

        trainer = HybridTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            config=config,
            use_mixed_precision=False
        )

        self.assertFalse(trainer.use_mixed_precision)

