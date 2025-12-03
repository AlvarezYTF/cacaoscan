"""
Unit tests for improved dataloader (improved_dataloader.py).
Tests ImprovedCacaoDataset and TargetNormalizer.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from PIL import Image
from torch.utils.data import DataLoader
from unittest.mock import patch, Mock
import torchvision.transforms as transforms

from ml.data.improved_dataloader import (
    ImprovedCacaoDataset,
    TargetNormalizer,
    normalize_targets,
    denormalize_predictions,
    create_improved_dataloader
)


@pytest.fixture
def sample_image_paths(tmp_path):
    """Create sample image files."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    image_paths = []
    for i in range(5):
        img_path = images_dir / f"{i}.png"
        img = Image.new('RGB', (224, 224), color='red')
        img.save(img_path, format='PNG')
        image_paths.append(img_path)
    
    return image_paths


@pytest.fixture
def sample_targets():
    """Create sample target values."""
    return {
        'alto': np.array([20.0, 25.0, 30.0, 22.0, 28.0], dtype=np.float32),
        'ancho': np.array([12.0, 15.0, 18.0, 13.0, 16.0], dtype=np.float32),
        'grosor': np.array([8.0, 9.0, 10.0, 8.5, 9.5], dtype=np.float32),
        'peso': np.array([1.5, 1.8, 2.0, 1.6, 1.9], dtype=np.float32)
    }


@pytest.fixture
def sample_transform():
    """Create sample image transform."""
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


class TestTargetNormalizer:
    """Tests for TargetNormalizer class."""
    
    def test_initialization_default(self):
        """Test TargetNormalizer initialization with defaults."""
        normalizer = TargetNormalizer()
        
        assert normalizer.scaler_type == "standard"
        assert normalizer.is_fitted is False
        assert normalizer.target_order == ["alto", "ancho", "grosor", "peso"]
    
    def test_initialization_minmax(self):
        """Test TargetNormalizer initialization with minmax scaler."""
        normalizer = TargetNormalizer(scaler_type="minmax")
        
        assert normalizer.scaler_type == "minmax"
    
    def test_fit(self, sample_targets):
        """Test fitting the normalizer."""
        normalizer = TargetNormalizer()
        normalizer.fit(sample_targets)
        
        assert normalizer.is_fitted is True
        assert 'alto' in normalizer.scalers
        assert 'ancho' in normalizer.scalers
        assert 'grosor' in normalizer.scalers
        assert 'peso' in normalizer.scalers
    
    def test_fit_missing_target(self, sample_targets):
        """Test fitting with missing target."""
        normalizer = TargetNormalizer()
        incomplete_targets = {k: v for k, v in sample_targets.items() if k != 'alto'}
        
        with pytest.raises(ValueError, match="no encontrado"):
            normalizer.fit(incomplete_targets)
    
    def test_normalize(self, sample_targets):
        """Test normalizing targets."""
        normalizer = TargetNormalizer()
        normalizer.fit(sample_targets)
        
        normalized = normalizer.normalize(sample_targets)
        
        assert isinstance(normalized, dict)
        assert 'alto' in normalized
        assert len(normalized['alto']) == len(sample_targets['alto'])
        # Normalized values should be centered around 0 for standard scaler
        assert np.abs(np.mean(normalized['alto'])) < 1e-6
    
    def test_normalize_not_fitted(self, sample_targets):
        """Test normalizing without fitting."""
        normalizer = TargetNormalizer()
        
        with pytest.raises(ValueError, match="deben ser ajustados"):
            normalizer.normalize(sample_targets)
    
    def test_denormalize(self, sample_targets):
        """Test denormalizing targets."""
        normalizer = TargetNormalizer()
        normalizer.fit(sample_targets)
        
        normalized = normalizer.normalize(sample_targets)
        denormalized = normalizer.denormalize(normalized)
        
        assert isinstance(denormalized, dict)
        assert 'alto' in denormalized
        # Denormalized should be close to original (within numerical precision)
        assert np.allclose(denormalized['alto'], sample_targets['alto'], rtol=1e-5)
    
    def test_normalize_single(self, sample_targets):
        """Test normalizing a single value."""
        normalizer = TargetNormalizer()
        normalizer.fit(sample_targets)
        
        normalized_value = normalizer.normalize_single('alto', 25.0)
        
        assert isinstance(normalized_value, float)
        assert not np.isnan(normalized_value)
    
    def test_denormalize_single(self, sample_targets):
        """Test denormalizing a single value."""
        normalizer = TargetNormalizer()
        normalizer.fit(sample_targets)
        
        normalized_value = normalizer.normalize_single('alto', 25.0)
        denormalized_value = normalizer.denormalize_single('alto', normalized_value)
        
        assert isinstance(denormalized_value, float)
        assert abs(denormalized_value - 25.0) < 0.1  # Within reasonable precision


class TestNormalizationConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_normalize_targets(self, sample_targets):
        """Test normalize_targets function."""
        normalized, normalizer = normalize_targets(sample_targets)
        
        assert isinstance(normalized, dict)
        assert isinstance(normalizer, TargetNormalizer)
        assert normalizer.is_fitted is True
    
    def test_denormalize_predictions(self, sample_targets):
        """Test denormalize_predictions function."""
        normalizer = TargetNormalizer()
        normalizer.fit(sample_targets)
        normalized = normalizer.normalize(sample_targets)
        
        denormalized = denormalize_predictions(normalized, normalizer)
        
        assert isinstance(denormalized, dict)
        assert np.allclose(denormalized['alto'], sample_targets['alto'], rtol=1e-5)


class TestImprovedCacaoDataset:
    """Tests for ImprovedCacaoDataset class."""
    
    def test_initialization_success(
        self,
        sample_image_paths,
        sample_targets,
        sample_transform
    ):
        """Test successful dataset initialization."""
        dataset = ImprovedCacaoDataset(
            image_paths=sample_image_paths,
            targets=sample_targets,
            transform=sample_transform,
            validate_structure=True
        )
        
        assert len(dataset) == 5
        assert len(dataset.image_paths) == 5
        assert len(dataset.targets) == 4
    
    def test_initialization_inconsistent_lengths(
        self,
        sample_image_paths,
        sample_transform
    ):
        """Test initialization with inconsistent lengths."""
        incomplete_targets = {
            'alto': np.array([20.0, 25.0], dtype=np.float32),  # Only 2 values
            'ancho': np.array([12.0, 15.0], dtype=np.float32),
            'grosor': np.array([8.0, 9.0], dtype=np.float32),
            'peso': np.array([1.5, 1.8], dtype=np.float32)
        }
        
        with pytest.raises(ValueError, match="Longitudes inconsistentes"):
            ImprovedCacaoDataset(
                image_paths=sample_image_paths,  # 5 images
                targets=incomplete_targets,  # Only 2 values
                transform=sample_transform,
                validate_structure=True
            )
    
    def test_initialization_missing_targets(
        self,
        sample_image_paths,
        sample_transform
    ):
        """Test initialization with missing targets."""
        incomplete_targets = {
            'alto': np.array([20.0, 25.0, 30.0, 22.0, 28.0], dtype=np.float32),
            'ancho': np.array([12.0, 15.0, 18.0, 13.0, 16.0], dtype=np.float32)
            # Missing 'grosor' and 'peso'
        }
        
        with pytest.raises(ValueError, match="Targets faltantes"):
            ImprovedCacaoDataset(
                image_paths=sample_image_paths,
                targets=incomplete_targets,
                transform=sample_transform,
                validate_structure=True
            )
    
    def test_getitem(
        self,
        sample_image_paths,
        sample_targets,
        sample_transform
    ):
        """Test __getitem__ method."""
        dataset = ImprovedCacaoDataset(
            image_paths=sample_image_paths,
            targets=sample_targets,
            transform=sample_transform,
            validate_structure=False
        )
        
        image_tensor, target_tensor = dataset[0]
        
        assert isinstance(image_tensor, torch.Tensor)
        assert image_tensor.shape == (3, 224, 224)  # RGB, 224x224
        assert isinstance(target_tensor, torch.Tensor)
        assert target_tensor.shape == (4,)  # 4 targets
    
    def test_getitem_with_pixel_features(
        self,
        sample_image_paths,
        sample_targets,
        sample_transform
    ):
        """Test __getitem__ with pixel features."""
        pixel_features = {
            str(path): np.random.randn(10) for path in sample_image_paths
        }
        
        dataset = ImprovedCacaoDataset(
            image_paths=sample_image_paths,
            targets=sample_targets,
            transform=sample_transform,
            pixel_features=pixel_features,
            validate_structure=False
        )
        
        image_tensor, target_tensor, pixel_feature_tensor = dataset[0]
        
        assert isinstance(image_tensor, torch.Tensor)
        assert isinstance(target_tensor, torch.Tensor)
        assert isinstance(pixel_feature_tensor, torch.Tensor)
        assert pixel_feature_tensor.shape == (10,)
    
    def test_get_target_ranges(
        self,
        sample_image_paths,
        sample_targets,
        sample_transform
    ):
        """Test get_target_ranges method."""
        dataset = ImprovedCacaoDataset(
            image_paths=sample_image_paths,
            targets=sample_targets,
            transform=sample_transform,
            validate_structure=False
        )
        
        ranges = dataset.get_target_ranges()
        
        assert isinstance(ranges, dict)
        assert 'alto' in ranges
        assert 'min' in ranges['alto']
        assert 'max' in ranges['alto']
        assert ranges['alto']['min'] == 20.0
        assert ranges['alto']['max'] == 30.0


class TestCreateImprovedDataloader:
    """Tests for create_improved_dataloader function."""
    
    def test_create_improved_dataloader(
        self,
        sample_image_paths,
        sample_targets,
        sample_transform
    ):
        """Test creating improved dataloader."""
        dataloader = create_improved_dataloader(
            image_paths=sample_image_paths,
            targets=sample_targets,
            transform=sample_transform,
            batch_size=2,
            shuffle=True
        )
        
        assert isinstance(dataloader, DataLoader)
        assert dataloader.batch_size == 2
        assert dataloader.shuffle is True
        
        # Test that we can iterate
        batch = next(iter(dataloader))
        assert len(batch) == 2  # image, targets
        assert batch[0].shape[0] == 2  # batch size

