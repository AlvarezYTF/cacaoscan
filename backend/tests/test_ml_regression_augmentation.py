"""
Unit tests for ML regression augmentation module.
Tests MixUp, CutMix, RandomErasing and transform functions.
"""
import pytest
import torch
import numpy as np
from PIL import Image
from unittest.mock import patch, MagicMock

from ml.regression.augmentation import (
    MixUp,
    CutMix,
    RandomErasing,
    create_advanced_train_transform,
    create_advanced_val_transform,
    AugmentedDataset
)


@pytest.fixture
def sample_images():
    """Create sample image tensor for testing."""
    return torch.randn(4, 3, 224, 224)


@pytest.fixture
def sample_targets():
    """Create sample target tensor for testing."""
    return torch.randn(4)


@pytest.fixture
def sample_image():
    """Create sample single image tensor for testing."""
    return torch.randn(3, 224, 224)


class TestMixUp:
    """Tests for MixUp augmentation."""
    
    def test_mixup_initialization(self):
        """Test MixUp initialization with default alpha."""
        mixup = MixUp()
        assert mixup.alpha == 0.4
    
    def test_mixup_initialization_custom_alpha(self):
        """Test MixUp initialization with custom alpha."""
        mixup = MixUp(alpha=0.5)
        assert mixup.alpha == 0.5
    
    def test_mixup_application(self, sample_images, sample_targets):
        """Test MixUp application to batch."""
        mixup = MixUp(alpha=0.4)
        torch.manual_seed(42)
        
        mixed_images, mixed_targets = mixup(sample_images, sample_targets)
        
        assert mixed_images.shape == sample_images.shape
        assert mixed_targets.shape == sample_targets.shape
        assert not torch.equal(mixed_images, sample_images) or not torch.equal(mixed_targets, sample_targets)
    
    def test_mixup_preserves_shape(self, sample_images, sample_targets):
        """Test that MixUp preserves tensor shapes."""
        mixup = MixUp()
        mixed_images, mixed_targets = mixup(sample_images, sample_targets)
        
        assert mixed_images.shape == sample_images.shape
        assert mixed_targets.shape == sample_targets.shape


class TestCutMix:
    """Tests for CutMix augmentation."""
    
    def test_cutmix_initialization(self):
        """Test CutMix initialization with default alpha."""
        cutmix = CutMix()
        assert cutmix.alpha == 1.0
    
    def test_cutmix_initialization_custom_alpha(self):
        """Test CutMix initialization with custom alpha."""
        cutmix = CutMix(alpha=0.8)
        assert cutmix.alpha == 0.8
    
    def test_cutmix_application(self, sample_images, sample_targets):
        """Test CutMix application to batch."""
        cutmix = CutMix(alpha=1.0)
        torch.manual_seed(42)
        
        mixed_images, mixed_targets = cutmix(sample_images, sample_targets)
        
        assert mixed_images.shape == sample_images.shape
        assert mixed_targets.shape == sample_targets.shape
    
    def test_cutmix_preserves_shape(self, sample_images, sample_targets):
        """Test that CutMix preserves tensor shapes."""
        cutmix = CutMix()
        mixed_images, mixed_targets = cutmix(sample_images, sample_targets)
        
        assert mixed_images.shape == sample_images.shape
        assert mixed_targets.shape == sample_targets.shape


class TestRandomErasing:
    """Tests for RandomErasing augmentation."""
    
    def test_random_erasing_initialization(self):
        """Test RandomErasing initialization with default parameters."""
        re = RandomErasing()
        assert re.probability == 0.5
        assert re.sl == 0.02
        assert re.sh == 0.4
        assert re.r1 == 0.3
    
    def test_random_erasing_initialization_custom(self):
        """Test RandomErasing initialization with custom parameters."""
        re = RandomErasing(probability=0.3, sl=0.01, sh=0.3, r1=0.2)
        assert re.probability == 0.3
        assert re.sl == 0.01
        assert re.sh == 0.3
        assert re.r1 == 0.2
    
    def test_random_erasing_application(self, sample_image):
        """Test RandomErasing application to single image."""
        re = RandomErasing(probability=1.0)
        torch.manual_seed(42)
        
        erased_image = re(sample_image)
        
        assert erased_image.shape == sample_image.shape
    
    def test_random_erasing_preserves_shape(self, sample_image):
        """Test that RandomErasing preserves tensor shape."""
        re = RandomErasing(probability=1.0)
        erased_image = re(sample_image)
        
        assert erased_image.shape == sample_image.shape
    
    def test_random_erasing_with_zero_probability(self, sample_image):
        """Test RandomErasing with zero probability (should return original)."""
        re = RandomErasing(probability=0.0)
        torch.manual_seed(42)
        
        erased_image = re(sample_image)
        
        assert torch.equal(erased_image, sample_image)


class TestTransforms:
    """Tests for transform creation functions."""
    
    def test_create_advanced_train_transform(self):
        """Test creation of advanced training transform."""
        transform = create_advanced_train_transform(img_size=224)
        
        assert transform is not None
        assert hasattr(transform, 'transforms')
        assert len(transform.transforms) > 0
    
    def test_create_advanced_train_transform_custom_size(self):
        """Test creation of advanced training transform with custom size."""
        transform = create_advanced_train_transform(img_size=256)
        
        assert transform is not None
        assert hasattr(transform, 'transforms')
    
    def test_create_advanced_val_transform(self):
        """Test creation of advanced validation transform."""
        transform = create_advanced_val_transform(img_size=224)
        
        assert transform is not None
        assert hasattr(transform, 'transforms')
        assert len(transform.transforms) > 0
    
    def test_create_advanced_val_transform_custom_size(self):
        """Test creation of advanced validation transform with custom size."""
        transform = create_advanced_val_transform(img_size=256)
        
        assert transform is not None
        assert hasattr(transform, 'transforms')
    
    def test_train_transform_applies_to_image(self):
        """Test that training transform can be applied to PIL image."""
        transform = create_advanced_train_transform(img_size=224)
        img = Image.new('RGB', (256, 256), color='red')
        
        result = transform(img)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape[0] == 3  # RGB channels
    
    def test_val_transform_applies_to_image(self):
        """Test that validation transform can be applied to PIL image."""
        transform = create_advanced_val_transform(img_size=224)
        img = Image.new('RGB', (256, 256), color='red')
        
        result = transform(img)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape[0] == 3  # RGB channels

