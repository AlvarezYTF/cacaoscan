"""
Tests for segmentation processor.
"""
import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import patch, Mock
from ml.segmentation.processor import (
    _deshadow_alpha,
    _guided_refine,
    _clean_components,
    _remove_background_opencv,
    SegmentationError
)


class TestDeshadowAlpha:
    """Tests for _deshadow_alpha function."""
    
    def test_deshadow_alpha_basic(self):
        """Test basic deshadow alpha."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[20:80, 20:80] = 255
        
        result = _deshadow_alpha(rgb, alpha)
        
        assert result.shape == alpha.shape
        assert result.dtype == np.uint8
    
    def test_deshadow_alpha_no_background(self):
        """Test deshadow alpha with no background."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.ones((100, 100), dtype=np.uint8) * 255
        
        result = _deshadow_alpha(rgb, alpha)
        
        assert np.array_equal(result, alpha)
    
    def test_deshadow_alpha_with_shadow(self):
        """Test deshadow alpha with shadow region."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        rgb[50:70, 50:70] = [200, 200, 200]  # Light region
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[20:80, 20:80] = 255
        
        result = _deshadow_alpha(rgb, alpha)
        
        assert result.shape == alpha.shape


class TestGuidedRefine:
    """Tests for _guided_refine function."""
    
    def test_guided_refine_basic(self):
        """Test basic guided refine."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[20:80, 20:80] = 255
        
        result = _guided_refine(rgb, alpha)
        
        assert result.shape == alpha.shape
        assert result.dtype == np.uint8
    
    def test_guided_refine_with_ximgproc(self):
        """Test guided refine with ximgproc available."""
        rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[20:80, 20:80] = 255
        
        with patch('ml.segmentation.processor._HAS_XIMGPROC', True):
            with patch('cv2.ximgproc.guidedFilter') as mock_guided:
                mock_guided.return_value = alpha
                
                result = _guided_refine(rgb, alpha)
                
                assert result.shape == alpha.shape


class TestCleanComponents:
    """Tests for _clean_components function."""
    
    def test_clean_components_single_component(self):
        """Test cleaning components with single component."""
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[20:80, 20:80] = 255
        
        result = _clean_components(alpha)
        
        assert result.shape == alpha.shape
        assert result.dtype == np.uint8
    
    def test_clean_components_multiple_components(self):
        """Test cleaning components with multiple components."""
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[10:30, 10:30] = 255  # Small component
        alpha[50:90, 50:90] = 255  # Large component
        
        result = _clean_components(alpha)
        
        assert result.shape == alpha.shape
        # Should keep only the largest component
        assert np.sum(result > 0) > 0


class TestRemoveBackgroundOpencv:
    """Tests for _remove_background_opencv function."""
    
    @patch('ml.segmentation.processor.cv2.imread')
    @patch('ml.segmentation.processor.cv2.grabCut')
    def test_remove_background_opencv_success(self, mock_grabcut, mock_imread, tmp_path):
        """Test removing background with OpenCV successfully."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        
        mock_mask = np.zeros((100, 100), dtype=np.uint8)
        mock_mask[20:80, 20:80] = cv2.GC_PR_FGD
        mock_grabcut.side_effect = lambda img, mask, rect, bgd, fgd, iter, mode: None
        
        with patch('ml.segmentation.processor._HAS_REMBG', False):
            result = _remove_background_opencv(str(image_path))
            
            assert result is not None
    
    @patch('ml.segmentation.processor.cv2.imread')
    def test_remove_background_opencv_image_not_found(self, mock_imread, tmp_path):
        """Test removing background when image not found."""
        image_path = tmp_path / "nonexistent.jpg"
        mock_imread.return_value = None
        
        with pytest.raises((ValueError, FileNotFoundError)):
            _remove_background_opencv(str(image_path))
    
    @patch('ml.segmentation.processor.rembg_remove')
    @patch('ml.segmentation.processor.cv2.imread')
    def test_remove_background_opencv_with_rembg(self, mock_imread, mock_rembg, tmp_path):
        """Test removing background with rembg available."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        
        mock_rembg_result = np.zeros((100, 100, 4), dtype=np.uint8)
        mock_rembg.return_value = mock_rembg_result
        
        with patch('ml.segmentation.processor._HAS_REMBG', True):
            result = _remove_background_opencv(str(image_path))
            
            assert result is not None


class TestSegmentationError:
    """Tests for SegmentationError exception."""
    
    def test_segmentation_error_creation(self):
        """Test creating SegmentationError."""
        error = SegmentationError("Test error")
        
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

