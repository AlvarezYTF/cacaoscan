"""
Unit tests for segmentation processor module (processor.py).
Tests image segmentation and background removal functionality.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import cv2

from ml.segmentation.processor import (
    segment_and_crop_cacao_bean,
    save_processed_png,
    convert_bmp_to_jpg,
    SegmentationError,
    _remove_background_opencv,
    _remove_background_rembg,
    _clean_components,
    _deshadow_alpha,
    _guided_refine
)


@pytest.fixture
def mock_image_path(tmp_path):
    """Create a temporary image file for testing."""
    image_path = tmp_path / "test_image.jpg"
    img = Image.new('RGB', (512, 512), color='red')
    img.save(image_path)
    return str(image_path)


@pytest.fixture
def mock_rgba_image():
    """Create a mock RGBA PIL Image."""
    return Image.new('RGBA', (200, 200), color=(255, 0, 0, 255))


class TestSegmentationProcessor:
    """Tests for segmentation processor functions."""
    
    def test_segment_and_crop_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            segment_and_crop_cacao_bean("nonexistent_image.jpg")
    
    @patch('ml.segmentation.processor.remove_background_ai')
    @patch('ml.segmentation.processor.save_processed_png')
    def test_segment_and_crop_ai_method(self, mock_save, mock_ai, mock_image_path):
        """Test segmentation with AI method."""
        mock_processed = Image.new('RGBA', (200, 200))
        mock_ai.return_value = mock_processed
        mock_save.return_value = Path('/tmp/test_output.png')
        
        result = segment_and_crop_cacao_bean(mock_image_path, method="ai")
        
        assert isinstance(result, str)
        assert result.endswith('.png')
        mock_ai.assert_called_once()
    
    @patch('ml.segmentation.processor._remove_background_opencv')
    @patch('ml.segmentation.processor.save_processed_png')
    def test_segment_and_crop_opencv_method(self, mock_save, mock_opencv, mock_image_path):
        """Test segmentation with OpenCV method."""
        mock_processed = Image.new('RGBA', (200, 200))
        mock_opencv.return_value = mock_processed
        mock_save.return_value = Path('/tmp/test_output.png')
        
        result = segment_and_crop_cacao_bean(mock_image_path, method="opencv")
        
        assert isinstance(result, str)
        assert result.endswith('.png')
        mock_opencv.assert_called_once()
    
    @patch('ml.segmentation.processor.remove_background_ai')
    @patch('ml.segmentation.processor._HAS_REMBG', True)
    @patch('ml.segmentation.processor._remove_background_rembg')
    @patch('ml.segmentation.processor.save_processed_png')
    def test_segment_and_crop_fallback_chain(self, mock_save, mock_rembg, mock_ai, mock_image_path):
        """Test fallback chain when AI method fails."""
        mock_processed = Image.new('RGBA', (200, 200))
        mock_ai.side_effect = Exception("AI failed")
        mock_rembg.return_value = mock_processed
        mock_save.return_value = Path('/tmp/test_output.png')
        
        result = segment_and_crop_cacao_bean(mock_image_path, method="ai")
        
        assert isinstance(result, str)
        mock_ai.assert_called_once()
        mock_rembg.assert_called_once()
    
    @patch('ml.segmentation.processor.remove_background_ai')
    @patch('ml.segmentation.processor._HAS_REMBG', False)
    @patch('ml.segmentation.processor._remove_background_opencv')
    @patch('ml.segmentation.processor.save_processed_png')
    def test_segment_and_crop_fallback_to_opencv(self, mock_save, mock_opencv, mock_ai, mock_image_path):
        """Test fallback to OpenCV when rembg is not available."""
        mock_processed = Image.new('RGBA', (200, 200))
        mock_ai.side_effect = Exception("AI failed")
        mock_opencv.return_value = mock_processed
        mock_save.return_value = Path('/tmp/test_output.png')
        
        result = segment_and_crop_cacao_bean(mock_image_path, method="ai")
        
        assert isinstance(result, str)
        mock_opencv.assert_called_once()
    
    def test_remove_background_opencv_file_not_found(self):
        """Test OpenCV background removal with non-existent file."""
        with pytest.raises(FileNotFoundError):
            _remove_background_opencv("nonexistent_image.jpg")
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.threshold')
    @patch('cv2.grabCut')
    @patch('cv2.findContours')
    def test_remove_background_opencv_success(self, mock_contours, mock_grabcut, 
                                               mock_threshold, mock_cvt, mock_imread, mock_image_path):
        """Test successful OpenCV background removal."""
        # Mock OpenCV functions
        mock_imread.return_value = np.zeros((512, 512, 3), dtype=np.uint8)
        mock_cvt.return_value = np.zeros((512, 512, 3), dtype=np.uint8)
        mock_threshold.return_value = (127, np.zeros((512, 512), dtype=np.uint8))
        mock_grabcut.return_value = None
        mock_contours.return_value = ([np.array([[10, 10], [100, 10], [100, 100], [10, 100]])], None)
        
        with patch('ml.segmentation.processor._clean_components', return_value=np.ones((512, 512), dtype=np.uint8) * 255), \
             patch('ml.segmentation.processor._deshadow_alpha', return_value=np.ones((512, 512), dtype=np.uint8) * 255), \
             patch('ml.segmentation.processor._guided_refine', return_value=np.ones((512, 512), dtype=np.uint8) * 255):
            result = _remove_background_opencv(mock_image_path)
            
            assert isinstance(result, Image.Image)
            assert result.mode == 'RGBA'
    
    @patch('ml.segmentation.processor._HAS_REMBG', True)
    @patch('ml.segmentation.processor.rembg_remove')
    def test_remove_background_rembg_success(self, mock_rembg, mock_image_path):
        """Test successful rembg background removal."""
        # Create a valid PNG image bytes
        img = Image.new('RGBA', (200, 200), color=(255, 0, 0, 128))
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        mock_output = buffer.getvalue()
        mock_rembg.return_value = mock_output
        
        result = _remove_background_rembg(mock_image_path)
        
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGBA'
    
    @patch('ml.segmentation.processor._HAS_REMBG', False)
    def test_remove_background_rembg_not_available(self, mock_image_path):
        """Test rembg when not available."""
        with pytest.raises(RuntimeError, match="rembg no disponible"):
            _remove_background_rembg(mock_image_path)
    
    def test_clean_components_empty_mask(self):
        """Test clean_components with empty mask."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        result = _clean_components(mask)
        
        assert result.shape == mask.shape
    
    def test_clean_components_with_components(self):
        """Test clean_components with valid components."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:80, 20:80] = 255  # Create a square component
        
        result = _clean_components(mask, min_area_ratio=0.001)
        
        assert result.shape == mask.shape
        assert np.sum(result > 0) > 0
    
    def test_deshadow_alpha_no_background(self):
        """Test deshadow_alpha with no background."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.ones((100, 100), dtype=np.uint8) * 255
        
        result = _deshadow_alpha(rgb, alpha)
        
        assert result.shape == alpha.shape
    
    def test_guided_refine_without_ximgproc(self):
        """Test guided_refine without ximgproc."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.ones((100, 100), dtype=np.uint8) * 255
        
        with patch('ml.segmentation.processor._HAS_XIMGPROC', False):
            result = _guided_refine(rgb, alpha)
            
            assert result.shape == alpha.shape
    
    @patch('ml.segmentation.processor._HAS_XIMGPROC', True)
    @patch('ml.segmentation.processor.ximgproc')
    def test_guided_refine_with_ximgproc(self, mock_ximgproc_module, mock_image_path):
        """Test guided_refine with ximgproc available."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.ones((100, 100), dtype=np.uint8) * 255
        mock_ximgproc_module.guidedFilter.return_value = np.ones((100, 100), dtype=np.float32) * 0.5
        
        result = _guided_refine(rgb, alpha)
        
        assert result.shape == alpha.shape
        assert result.dtype == np.uint8
    
    @patch('ml.segmentation.processor._processed_dir_for_today')
    def test_save_processed_png(self, mock_dir, mock_rgba_image, tmp_path):
        """Test saving processed PNG."""
        mock_dir.return_value = tmp_path
        
        result = save_processed_png(mock_rgba_image, "test_output.png")
        
        assert isinstance(result, Path)
        assert result.exists()
        assert result.suffix == '.png'
    
    def test_convert_bmp_to_jpg_success(self, tmp_path):
        """Test successful BMP to JPG conversion."""
        bmp_path = tmp_path / "test.bmp"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(bmp_path, format='BMP')
        
        jpg_img, result = convert_bmp_to_jpg(bmp_path)
        
        assert result['success'] is True
        assert jpg_img is not None
        assert jpg_img.format == 'JPEG'
    
    def test_convert_bmp_to_jpg_failure(self, tmp_path):
        """Test BMP to JPG conversion failure."""
        invalid_path = tmp_path / "nonexistent.bmp"
        
        jpg_img, result = convert_bmp_to_jpg(invalid_path)
        
        assert result['success'] is False
        assert 'error' in result
        assert jpg_img is None

