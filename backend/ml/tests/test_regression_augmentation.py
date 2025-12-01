"""
Tests for regression augmentation module.
"""
import torch
import torch.nn as nn
from unittest import TestCase
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image

from ml.regression.augmentation import (
    MixUp,
    CutMix,
    RandomErasing,
    create_advanced_train_transform,
    create_advanced_val_transform
)


class MixUpTest(TestCase):
    """Tests for MixUp augmentation."""

    def test_mixup_initialization(self):
        """Test MixUp initialization."""
        mixup = MixUp(alpha=0.4)
        self.assertEqual(mixup.alpha, 0.4)

    def test_mixup_call(self):
        """Test MixUp call."""
        mixup = MixUp(alpha=0.4)
        batch_size = 4
        images = torch.randn(batch_size, 3, 224, 224)
        targets = torch.randn(batch_size)

        mixed_images, mixed_targets = mixup(images, targets)

        self.assertEqual(mixed_images.shape, images.shape)
        self.assertEqual(mixed_targets.shape, targets.shape)

    def test_mixup_no_mixing(self):
        """Test MixUp when no mixing occurs."""
        with patch('ml.regression.augmentation.torch.rand') as mock_rand:
            mock_rand.return_value.item.return_value = 0.6
            mixup = MixUp(alpha=0.4)
            images = torch.randn(2, 3, 224, 224)
            targets = torch.randn(2)

            mixed_images, mixed_targets = mixup(images, targets)

            self.assertTrue(torch.equal(mixed_images, images))
            self.assertTrue(torch.equal(mixed_targets, targets))


class CutMixTest(TestCase):
    """Tests for CutMix augmentation."""

    def test_cutmix_initialization(self):
        """Test CutMix initialization."""
        cutmix = CutMix(alpha=1.0)
        self.assertEqual(cutmix.alpha, 1.0)

    def test_cutmix_call(self):
        """Test CutMix call."""
        cutmix = CutMix(alpha=1.0)
        batch_size = 4
        images = torch.randn(batch_size, 3, 224, 224)
        targets = torch.randn(batch_size)

        mixed_images, mixed_targets = cutmix(images, targets)

        self.assertEqual(mixed_images.shape, images.shape)
        self.assertEqual(mixed_targets.shape, targets.shape)


class RandomErasingTest(TestCase):
    """Tests for RandomErasing augmentation."""

    def test_random_erasing_initialization(self):
        """Test RandomErasing initialization."""
        re = RandomErasing(probability=0.5, sl=0.02, sh=0.4, r1=0.3)
        self.assertEqual(re.probability, 0.5)
        self.assertEqual(re.sl, 0.02)
        self.assertEqual(re.sh, 0.4)
        self.assertEqual(re.r1, 0.3)

    def test_random_erasing_call(self):
        """Test RandomErasing call."""
        re = RandomErasing(probability=0.5)
        image = torch.randn(3, 224, 224)

        result = re(image)

        self.assertEqual(result.shape, image.shape)


class TransformTest(TestCase):
    """Tests for transform creation functions."""

    def test_create_advanced_train_transform(self):
        """Test creating advanced train transform."""
        transform = create_advanced_train_transform(img_size=224)
        self.assertIsNotNone(transform)

        test_image = Image.new('RGB', (256, 256), color='red')
        transformed = transform(test_image)
        self.assertIsInstance(transformed, torch.Tensor)

    def test_create_advanced_val_transform(self):
        """Test creating advanced val transform."""
        transform = create_advanced_val_transform(img_size=224)
        self.assertIsNotNone(transform)

        test_image = Image.new('RGB', (256, 256), color='red')
        transformed = transform(test_image)
        self.assertIsInstance(transformed, torch.Tensor)

