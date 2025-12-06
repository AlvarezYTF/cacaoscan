"""
Tests for image transforms.
"""
import pytest
import numpy as np
import cv2
from ml.data.transforms import (
    resize_crop_to_square,
    resize_with_padding,
    normalize_image,
    denormalize_image,
    validate_crop_quality,
    create_transparent_crop,
    _align_mask_to_image,
    _compute_padded_bbox,
    _render_primary_mask,
    _stack_rgba
)


class TestResizeCropToSquare:
    """Tests for resize_crop_to_square function."""
    
    def test_resize_crop_to_square_rgba(self):
        """Test resizing RGBA image to square."""
        image = np.zeros((100, 200, 4), dtype=np.uint8)
        image[:, :, 3] = 255  # Alpha channel
        
        result = resize_crop_to_square(image, target_size=256)
        
        assert result.shape == (256, 256, 4)
        assert result.dtype == np.uint8
    
    def test_resize_crop_to_square_with_fill_color(self):
        """Test resizing with custom fill color."""
        image = np.zeros((100, 200, 4), dtype=np.uint8)
        
        result = resize_crop_to_square(image, target_size=256, fill_color=(255, 0, 0, 128))
        
        assert result.shape == (256, 256, 4)
        assert result[0, 0, 0] == 255  # Red channel
    
    def test_resize_crop_to_square_none_raises_error(self):
        """Test that None image raises error."""
        with pytest.raises(ValueError, match="cannot be None"):
            resize_crop_to_square(None)


class TestResizeWithPadding:
    """Tests for resize_with_padding function."""
    
    def test_resize_with_padding_rgb(self):
        """Test resizing RGB image with padding."""
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        result = resize_with_padding(image, target_size=(256, 256))
        
        assert result.shape == (256, 256, 3)
    
    def test_resize_with_padding_grayscale(self):
        """Test resizing grayscale image with padding."""
        image = np.zeros((100, 200), dtype=np.uint8)
        
        result = resize_with_padding(image, target_size=(256, 256))
        
        assert result.shape == (256, 256)
    
    def test_resize_with_padding_rgba(self):
        """Test resizing RGBA image with padding."""
        image = np.zeros((100, 200, 4), dtype=np.uint8)
        
        result = resize_with_padding(image, target_size=(256, 256), fill_color=(255, 0, 0, 128))
        
        assert result.shape == (256, 256, 4)
    
    def test_resize_with_padding_none_raises_error(self):
        """Test that None image raises error."""
        with pytest.raises(ValueError, match="cannot be None"):
            resize_with_padding(None)


class TestNormalizeImage:
    """Tests for normalize_image function."""
    
    def test_normalize_uint8_image(self):
        """Test normalizing uint8 image."""
        image = np.array([[0, 128, 255]], dtype=np.uint8)
        
        result = normalize_image(image)
        
        assert result.dtype == np.float32
        assert result.max() <= 1.0
        assert result.min() >= 0.0
    
    def test_normalize_already_normalized(self):
        """Test normalizing already normalized image."""
        image = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
        
        result = normalize_image(image)
        
        assert result.dtype == np.float32
        assert result.max() <= 1.0
    
    def test_normalize_none_raises_error(self):
        """Test that None image raises error."""
        with pytest.raises(ValueError, match="cannot be None"):
            normalize_image(None)


class TestDenormalizeImage:
    """Tests for denormalize_image function."""
    
    def test_denormalize_float_image(self):
        """Test denormalizing float image."""
        image = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
        
        result = denormalize_image(image)
        
        assert result.dtype == np.uint8
        assert result.max() <= 255
        assert result.min() >= 0
    
    def test_denormalize_clips_values(self):
        """Test that denormalize clips values."""
        image = np.array([[-0.5, 1.5]], dtype=np.float32)
        
        result = denormalize_image(image)
        
        assert result.dtype == np.uint8
        assert result[0, 0] == 0
        assert result[0, 1] == 255
    
    def test_denormalize_none_raises_error(self):
        """Test that None image raises error."""
        with pytest.raises(ValueError, match="cannot be None"):
            denormalize_image(None)


class TestValidateCropQuality:
    """Tests for validate_crop_quality function."""
    
    def test_validate_crop_quality_valid(self):
        """Test validating valid crop."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:80, 20:80] = 255
        
        result = validate_crop_quality(image, mask)
        
        assert result is True
    
    def test_validate_crop_quality_invalid_area(self):
        """Test validating crop with invalid area."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[50:51, 50:51] = 255  # Very small area
        
        result = validate_crop_quality(image, mask, min_area=1000)
        
        assert result is False
    
    def test_validate_crop_quality_none_inputs(self):
        """Test validating with None inputs."""
        result = validate_crop_quality(None, None)
        assert result is False
        
        result = validate_crop_quality(np.zeros((10, 10, 3)), None)
        assert result is False


class TestCreateTransparentCrop:
    """Tests for create_transparent_crop function."""
    
    def test_create_transparent_crop(self):
        """Test creating transparent crop."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:80, 20:80] = 255
        
        result = create_transparent_crop(image, mask, padding=10)
        
        assert result.shape[2] == 4  # RGBA
        assert result.dtype == np.uint8
    
    def test_create_transparent_crop_crop_only(self):
        """Test creating transparent crop with crop_only=True."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:80, 20:80] = 255
        
        result = create_transparent_crop(image, mask, padding=10, crop_only=True)
        
        assert result.shape[2] == 4
    
    def test_create_transparent_crop_none_inputs(self):
        """Test creating crop with None inputs."""
        with pytest.raises(ValueError, match="no pueden ser None"):
            create_transparent_crop(None, None)


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_align_mask_to_image_same_size(self):
        """Test aligning mask of same size."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = _align_mask_to_image(mask, image)
        
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8
    
    def test_align_mask_to_image_different_size(self):
        """Test aligning mask of different size."""
        mask = np.zeros((50, 50), dtype=np.uint8)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = _align_mask_to_image(mask, image)
        
        assert result.shape == (100, 100)
    
    def test_align_mask_to_image_normalized(self):
        """Test aligning normalized mask."""
        mask = np.zeros((100, 100), dtype=np.float32)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = _align_mask_to_image(mask, image)
        
        assert result.dtype == np.uint8
        assert result.max() <= 255
    
    def test_compute_padded_bbox(self):
        """Test computing padded bounding box."""
        contour = np.array([[[10, 10]], [[50, 10]], [[50, 50]], [[10, 50]]], dtype=np.int32)
        image_shape = (100, 100, 3)
        
        x, y, w, h = _compute_padded_bbox(contour, padding=5, image_shape=image_shape)
        
        assert x >= 0
        assert y >= 0
        assert w > 0
        assert h > 0
    
    def test_render_primary_mask(self):
        """Test rendering primary mask."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        contour = np.array([[[10, 10]], [[50, 10]], [[50, 50]], [[10, 50]]], dtype=np.int32)
        
        result = _render_primary_mask(mask, contour)
        
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8
    
    def test_stack_rgba(self):
        """Test stacking RGB and alpha."""
        rgb = np.zeros((10, 10, 3), dtype=np.uint8)
        alpha = np.ones((10, 10), dtype=np.uint8) * 255
        
        result = _stack_rgba(rgb, alpha)
        
        assert result.shape == (10, 10, 4)
        assert result.dtype == np.uint8
        assert np.array_equal(result[:, :, 3], alpha)

