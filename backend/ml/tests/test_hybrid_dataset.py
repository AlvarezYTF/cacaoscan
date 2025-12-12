"""
Tests for hybrid dataset.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from unittest.mock import MagicMock, patch
from PIL import Image
import torchvision.transforms as transforms

from ml.data.hybrid_dataset import HybridCacaoDataset


class TestHybridCacaoDataset:
    """Tests for HybridCacaoDataset class."""
    
    @pytest.fixture
    def temp_image_dir(self, tmp_path):
        """Create temporary directory with test images."""
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        
        # Create a simple test image
        for i in range(3):
            img_path = img_dir / f"test_{i}.png"
            img = Image.new('RGB', (224, 224), color=(255, 0, 0))
            img.save(img_path)
        
        return img_dir
    
    @pytest.fixture
    def sample_targets(self):
        """Create sample target data."""
        return {
            'alto': np.array([10.0, 20.0, 30.0], dtype=np.float32),
            'ancho': np.array([15.0, 25.0, 35.0], dtype=np.float32),
            'grosor': np.array([5.0, 10.0, 15.0], dtype=np.float32),
            'peso': np.array([100.0, 200.0, 300.0], dtype=np.float32)
        }
    
    @pytest.fixture
    def transform(self):
        """Create image transform."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])
    
    def test_initialization(self, temp_image_dir, sample_targets, transform):
        """Test dataset initialization."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        dataset = HybridCacaoDataset(
            image_paths=image_paths,
            targets=sample_targets,
            transform=transform,
            validate=True
        )
        
        assert len(dataset) == 3
        assert len(dataset.image_paths) == 3
        assert len(dataset.targets) == 4
    
    def test_initialization_missing_targets(self, temp_image_dir, transform):
        """Test initialization with missing targets."""
        image_paths = list(temp_image_dir.glob("*.png"))
        incomplete_targets = {
            'alto': np.array([10.0, 20.0, 30.0]),
            'ancho': np.array([15.0, 25.0, 35.0])
        }
        
        with pytest.raises(ValueError, match="Missing targets"):
            HybridCacaoDataset(
                image_paths=image_paths,
                targets=incomplete_targets,
                transform=transform,
                validate=True
            )
    
    def test_initialization_inconsistent_lengths(self, temp_image_dir, transform):
        """Test initialization with inconsistent lengths."""
        image_paths = list(temp_image_dir.glob("*.png"))
        targets = {
            'alto': np.array([10.0, 20.0]),
            'ancho': np.array([15.0, 25.0]),
            'grosor': np.array([5.0, 10.0]),
            'peso': np.array([100.0, 200.0])
        }
        
        with pytest.raises(ValueError, match="Inconsistent lengths"):
            HybridCacaoDataset(
                image_paths=image_paths,
                targets=targets,
                transform=transform,
                validate=True
            )
    
    def test_getitem_without_pixel_features(self, temp_image_dir, sample_targets, transform):
        """Test __getitem__ without pixel features loader."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        dataset = HybridCacaoDataset(
            image_paths=image_paths,
            targets=sample_targets,
            transform=transform,
            validate=False
        )
        
        img_tensor, target_tensor, pixel_tensor = dataset[0]
        
        assert img_tensor.shape == (3, 224, 224)
        assert target_tensor.shape == (4,)
        assert pixel_tensor.shape == (10,)
        assert torch.all(pixel_tensor == 0)  # Should be zeros without loader
    
    def test_getitem_with_pixel_features(self, temp_image_dir, sample_targets, transform):
        """Test __getitem__ with pixel features loader."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        # Mock pixel features loader
        mock_loader = MagicMock()
        mock_loader.get_features_by_id.return_value = np.array([1.0] * 10, dtype=np.float32)
        
        dataset = HybridCacaoDataset(
            image_paths=image_paths,
            targets=sample_targets,
            transform=transform,
            pixel_features_loader=mock_loader,
            record_ids=[1, 2, 3],
            validate=False
        )
        
        img_tensor, target_tensor, pixel_tensor = dataset[0]
        
        assert img_tensor.shape == (3, 224, 224)
        assert target_tensor.shape == (4,)
        assert pixel_tensor.shape == (10,)
        assert torch.all(pixel_tensor != 0)  # Should have values
    
    def test_getitem_missing_pixel_features(self, temp_image_dir, sample_targets, transform):
        """Test __getitem__ when pixel features are missing."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        # Mock pixel features loader that returns None
        mock_loader = MagicMock()
        mock_loader.get_features_by_id.return_value = None
        
        dataset = HybridCacaoDataset(
            image_paths=image_paths,
            targets=sample_targets,
            transform=transform,
            pixel_features_loader=mock_loader,
            record_ids=[1, 2, 3],
            validate=False
        )
        
        img_tensor, target_tensor, pixel_tensor = dataset[0]
        
        assert img_tensor.shape == (3, 224, 224)
        assert target_tensor.shape == (4,)
        assert pixel_tensor.shape == (10,)
        assert torch.all(pixel_tensor == 0)  # Should use zeros when None
    
    def test_validation_with_pixel_loader_no_record_ids(self, temp_image_dir, sample_targets, transform):
        """Test validation fails when pixel loader provided without record_ids."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        mock_loader = MagicMock()
        
        with pytest.raises(ValueError, match="record_ids required"):
            HybridCacaoDataset(
                image_paths=image_paths,
                targets=sample_targets,
                transform=transform,
                pixel_features_loader=mock_loader,
                record_ids=None,
                validate=True
            )
    
    def test_validation_with_pixel_loader_inconsistent_record_ids(self, temp_image_dir, sample_targets, transform):
        """Test validation fails with inconsistent record_ids length."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        mock_loader = MagicMock()
        
        with pytest.raises(ValueError, match="Inconsistent lengths"):
            HybridCacaoDataset(
                image_paths=image_paths,
                targets=sample_targets,
                transform=transform,
                pixel_features_loader=mock_loader,
                record_ids=[1, 2],  # Wrong length
                validate=True
            )
    
    def test_target_order(self, temp_image_dir, sample_targets, transform):
        """Test that targets are returned in correct order."""
        image_paths = list(temp_image_dir.glob("*.png"))
        
        dataset = HybridCacaoDataset(
            image_paths=image_paths,
            targets=sample_targets,
            transform=transform,
            validate=False
        )
        
        _, target_tensor, _ = dataset[0]
        
        # Check order: alto, ancho, grosor, peso
        assert target_tensor[0].item() == pytest.approx(10.0)
        assert target_tensor[1].item() == pytest.approx(15.0)
        assert target_tensor[2].item() == pytest.approx(5.0)
        assert target_tensor[3].item() == pytest.approx(100.0)

