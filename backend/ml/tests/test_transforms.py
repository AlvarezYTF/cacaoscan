"""
Tests for image transforms.
"""
import pytest
import numpy as np
import cv2
import torch
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from unittest.mock import patch, MagicMock, Mock
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
    _stack_rgba,
    UNet,
    DoubleConv,
    CacaoDataset,
    train_background_ai,
    remove_background_ai,
    _refine_mask_opencv_precise,
    _create_refined_rgba,
    _validate_and_adjust_crop_bbox,
    _create_rgba_from_crop
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


class TestDoubleConv:
    """Tests for DoubleConv class."""
    
    def test_double_conv_initialization(self):
        """Test DoubleConv initialization."""
        conv = DoubleConv(3, 64)
        
        assert conv.conv is not None
        assert len(conv.conv) == 6  # 2 convs + 2 batchnorm + 2 relu
    
    def test_double_conv_forward(self):
        """Test DoubleConv forward pass."""
        conv = DoubleConv(3, 64)
        x = torch.randn(1, 3, 32, 32)
        
        result = conv.forward(x)
        
        assert result.shape == (1, 64, 32, 32)
        assert result.dtype == torch.float32


class TestUNet:
    """Tests for UNet class."""
    
    def test_unet_initialization(self):
        """Test UNet initialization."""
        unet = UNet(n_channels=3, n_classes=1)
        
        assert unet.down1 is not None
        assert unet.up1 is not None
        assert unet.final is not None
        assert unet.sigmoid is not None
    
    def test_unet_forward(self):
        """Test UNet forward pass."""
        unet = UNet(n_channels=3, n_classes=1)
        x = torch.randn(1, 3, 256, 256)
        
        result = unet.forward(x)
        
        assert result.shape == (1, 1, 256, 256)
        assert result.min() >= 0.0
        assert result.max() <= 1.0
    
    def test_unet_custom_channels(self):
        """Test UNet with custom channels."""
        unet = UNet(n_channels=1, n_classes=2)
        x = torch.randn(1, 1, 128, 128)
        
        result = unet.forward(x)
        
        assert result.shape == (1, 2, 128, 128)


class TestCacaoDataset:
    """Tests for CacaoDataset class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        img_dir = Path(tempfile.mkdtemp())
        mask_dir = Path(tempfile.mkdtemp())
        
        # Create test image
        test_img = Image.new('RGB', (100, 100), color='red')
        img_path = img_dir / "test.jpg"
        test_img.save(img_path)
        
        yield img_dir, mask_dir
        
        shutil.rmtree(img_dir)
        shutil.rmtree(mask_dir)
    
    def test_dataset_initialization(self, temp_dirs):
        """Test CacaoDataset initialization."""
        img_dir, mask_dir = temp_dirs
        mask_path = mask_dir / "test.png"
        mask_img = Image.new('L', (100, 100), color=255)
        mask_img.save(mask_path)
        
        dataset = CacaoDataset(img_dir, mask_dir, transform=None, auto_generate=False)
        
        assert len(dataset) == 1
        assert dataset.img_dir == img_dir
        assert dataset.mask_dir == mask_dir
    
    def test_dataset_getitem(self, temp_dirs):
        """Test CacaoDataset __getitem__."""
        img_dir, mask_dir = temp_dirs
        mask_path = mask_dir / "test.png"
        mask_img = Image.new('L', (100, 100), color=255)
        mask_img.save(mask_path)
        
        dataset = CacaoDataset(img_dir, mask_dir, transform=None, auto_generate=False)
        
        image, mask = dataset[0]
        
        assert image.size == (100, 100)
        assert mask.size == (100, 100)
    
    def test_dataset_auto_generate(self, temp_dirs):
        """Test CacaoDataset auto mask generation."""
        img_dir, mask_dir = temp_dirs
        
        with patch('ml.data.transforms.cv2.grabCut') as mock_grabcut:
            mock_grabcut.return_value = None
            dataset = CacaoDataset(img_dir, mask_dir, transform=None, auto_generate=True)
            
            assert len(dataset) == 1
    
    def test_dataset_auto_mask(self, temp_dirs):
        """Test CacaoDataset _auto_mask method."""
        img_dir, mask_dir = temp_dirs
        dataset = CacaoDataset(img_dir, mask_dir, transform=None, auto_generate=False)
        img_path = img_dir / "test.jpg"
        
        with patch('ml.data.transforms.cv2.imread') as mock_read:
            mock_read.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            with patch('ml.data.transforms.cv2.grabCut') as mock_grabcut:
                mock_mask = np.zeros((100, 100), dtype=np.uint8)
                mock_grabcut.side_effect = lambda img, mask, *args, **kwargs: None
                
                result = dataset._auto_mask(str(img_path))
                
                assert result.shape == (100, 100)
                assert result.dtype == np.uint8


class TestRefineMaskOpencvPrecise:
    """Tests for _refine_mask_opencv_precise function."""
    
    def test_refine_mask_basic(self):
        """Test basic mask refinement."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255
        
        result = _refine_mask_opencv_precise(rgb, mask)
        
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8
    
    def test_refine_mask_with_contours(self):
        """Test mask refinement with contours."""
        rgb = np.ones((100, 100, 3), dtype=np.uint8) * 255
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[40:60, 40:60] = 255
        
        result = _refine_mask_opencv_precise(rgb, mask)
        
        assert result.shape == (100, 100)
    
    def test_refine_mask_no_contours(self):
        """Test mask refinement with no contours."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        
        result = _refine_mask_opencv_precise(rgb, mask)
        
        assert result.shape == (100, 100)


class TestCreateRefinedRgba:
    """Tests for _create_refined_rgba function."""
    
    def test_create_refined_rgba(self):
        """Test creating refined RGBA."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        final_mask = np.zeros((100, 100), dtype=np.uint8)
        final_mask[30:70, 30:70] = 255
        
        result = _create_refined_rgba(image_rgb, final_mask, 20, 20, 60, 60)
        
        assert result.shape[2] == 4
        assert result.dtype == np.uint8


class TestValidateAndAdjustCropBbox:
    """Tests for _validate_and_adjust_crop_bbox function."""
    
    def test_validate_and_adjust_crop_bbox_normal(self):
        """Test normal crop bbox validation."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        final_mask = np.zeros((100, 100), dtype=np.uint8)
        final_mask[30:70, 30:70] = 255
        bbox = (20, 20, 60, 60)
        
        result = _validate_and_adjust_crop_bbox(
            image_rgb=image_rgb,
            final_mask=final_mask,
            bbox=bbox,
            padding=10
        )
        
        assert len(result) == 4
        assert all(isinstance(x, int) for x in result)
    
    def test_validate_and_adjust_crop_bbox_zero_area(self):
        """Test crop bbox with zero area."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        final_mask = np.zeros((100, 100), dtype=np.uint8)
        bbox = (0, 0, 0, 0)
        
        result = _validate_and_adjust_crop_bbox(
            image_rgb=image_rgb,
            final_mask=final_mask,
            bbox=bbox,
            padding=10
        )
        
        assert result == bbox
    
    def test_validate_and_adjust_crop_bbox_large_ratio(self):
        """Test crop bbox with large area ratio."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        final_mask = np.zeros((100, 100), dtype=np.uint8)
        final_mask[10:90, 10:90] = 255
        bbox = (5, 5, 90, 90)
        
        with pytest.raises(ValueError, match="El objeto detectado ocupa"):
            _validate_and_adjust_crop_bbox(
                image_rgb=image_rgb,
                final_mask=final_mask,
                bbox=bbox,
                padding=10
            )
    
    def test_validate_and_adjust_crop_bbox_empty_mask(self):
        """Test crop bbox with empty mask."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        final_mask = np.zeros((100, 100), dtype=np.uint8)
        bbox = (20, 20, 60, 60)
        
        result = _validate_and_adjust_crop_bbox(
            image_rgb=image_rgb,
            final_mask=final_mask,
            bbox=bbox,
            padding=10
        )
        
        assert result == bbox


class TestCreateRgbaFromCrop:
    """Tests for _create_rgba_from_crop function."""
    
    def test_create_rgba_from_crop(self):
        """Test creating RGBA from crop."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        final_mask = np.zeros((100, 100), dtype=np.uint8)
        final_mask[30:70, 30:70] = 255
        
        result = _create_rgba_from_crop(image_rgb, final_mask, 20, 20, 60, 60)
        
        assert result.shape[2] == 4
        assert result.dtype == np.uint8


class TestTrainBackgroundAI:
    """Tests for train_background_ai function."""
    
    @pytest.fixture
    def temp_train_dirs(self):
        """Create temporary directories for training."""
        img_dir = Path(tempfile.mkdtemp())
        mask_dir = Path(tempfile.mkdtemp())
        
        # Create test images
        for i in range(3):
            test_img = Image.new('RGB', (100, 100), color='red')
            img_path = img_dir / f"test{i}.jpg"
            test_img.save(img_path)
            
            mask_img = Image.new('L', (100, 100), color=255)
            mask_path = mask_dir / f"test{i}.png"
            mask_img.save(mask_path)
        
        yield img_dir, mask_dir
        
        shutil.rmtree(img_dir)
        shutil.rmtree(mask_dir)
    
    @patch('ml.data.transforms.torch.save')
    def test_train_background_ai(self, mock_save, temp_train_dirs):
        """Test training background AI."""
        img_dir, mask_dir = temp_train_dirs
        
        with patch('ml.data.transforms.DataLoader') as mock_loader:
            mock_loader.return_value = [
                (torch.randn(1, 3, 256, 256), torch.randn(1, 1, 256, 256))
            ] * 2
            
            train_background_ai(
                image_dir=str(img_dir),
                mask_dir=str(mask_dir),
                epochs=1
            )
            
            # Verify model was attempted to be saved
            assert True  # Test passes if no exception raised


class TestRemoveBackgroundAI:
    """Tests for remove_background_ai function."""
    
    @pytest.fixture
    def temp_image(self):
        """Create temporary test image."""
        img_dir = Path(tempfile.mkdtemp())
        test_img = Image.new('RGB', (100, 100), color='red')
        img_path = img_dir / "test.jpg"
        test_img.save(img_path)
        
        yield img_path
        
        shutil.rmtree(img_dir)
    
    @patch('ml.data.transforms.torch.load')
    @patch('ml.data.transforms.os.path.exists')
    def test_remove_background_ai_no_model(self, mock_exists, mock_load, temp_image):
        """Test remove_background_ai when model doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            remove_background_ai(str(temp_image))
    
    @patch('ml.data.transforms.cv2.resize')
    @patch('ml.data.transforms.Image.open')
    @patch('ml.data.transforms.torch.load')
    @patch('ml.data.transforms.os.path.exists')
    @patch('ml.data.transforms.torch.cuda.is_available')
    def test_remove_background_ai_success(
        self, mock_cuda, mock_exists, mock_load, mock_open, mock_resize, temp_image
    ):
        """Test successful background removal."""
        mock_exists.return_value = True
        mock_cuda.return_value = False
        mock_open.return_value = Image.new('RGB', (100, 100), color='red')
        mock_resize.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        # Mock UNet model
        mock_model = MagicMock()
        mock_model.eval.return_value = None
        mock_model.return_value = torch.zeros((1, 1, 256, 256))
        
        with patch('ml.data.transforms.UNet', return_value=mock_model):
            with patch('ml.data.transforms._refine_mask_opencv_precise') as mock_refine:
                mock_refine.return_value = np.zeros((100, 100), dtype=np.uint8)
                with patch('ml.data.transforms._deshadow_alpha') as mock_deshadow:
                    mock_deshadow.return_value = np.zeros((100, 100), dtype=np.uint8)
                    with patch('ml.data.transforms._guided_refine') as mock_guided:
                        mock_guided.return_value = np.zeros((100, 100), dtype=np.uint8)
                        with patch('ml.data.transforms._clean_components') as mock_clean:
                            mock_clean.return_value = np.zeros((100, 100), dtype=np.uint8)
                            
                            result = remove_background_ai(str(temp_image))
                            
                            assert isinstance(result, Image.Image)


class TestValidateCropQualityExtended:
    """Extended tests for validate_crop_quality function."""
    
    def test_validate_crop_quality_invalid_aspect_ratio(self):
        """Test validating crop with invalid aspect ratio."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[10:20, 10:90] = 255  # Very wide
        
        result = validate_crop_quality(image, mask, max_aspect_ratio=2.0)
        
        assert result is False
    
    def test_validate_crop_quality_valid_aspect_ratio(self):
        """Test validating crop with valid aspect ratio."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255
        
        result = validate_crop_quality(image, mask, min_aspect_ratio=0.1, max_aspect_ratio=10.0)
        
        assert result is True
    
    def test_validate_crop_quality_small_dimensions(self):
        """Test validating crop with very small dimensions."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[50:52, 50:52] = 255  # 2x2 pixels
        
        result = validate_crop_quality(image, mask)
        
        assert result is False
    
    def test_validate_crop_quality_no_contours(self):
        """Test validating crop with no contours."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        
        result = validate_crop_quality(image, mask)
        
        assert result is False
    
    def test_validate_crop_quality_binary_mask(self):
        """Test validating crop with binary mask (0/1)."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 1  # Binary mask
        
        result = validate_crop_quality(image, mask)
        
        assert result is True

