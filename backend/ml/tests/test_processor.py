"""
Tests for segmentation processor.
"""
import pytest
import numpy as np
import cv2
from pathlib import Path
from PIL import Image
from unittest.mock import patch, Mock, MagicMock
from ml.segmentation.processor import (
    _deshadow_alpha,
    _guided_refine,
    _clean_components,
    _remove_background_opencv,
    _remove_background_rembg,
    _processed_dir_for_today,
    save_processed_png,
    _process_with_opencv,
    _process_with_priority_chain,
    _try_rembg_then_opencv,
    _try_opencv_fallback,
    segment_and_crop_cacao_bean,
    convert_bmp_to_jpg,
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


class TestRemoveBackgroundRembg:
    """Tests for _remove_background_rembg function."""
    
    @patch('ml.segmentation.processor._HAS_REMBG', True)
    @patch('ml.segmentation.processor.rembg_remove')
    def test_remove_background_rembg_success(self, mock_rembg, tmp_path):
        """Test removing background with rembg successfully."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        mock_rembg.return_value = mock_result.tobytes()
        
        result = _remove_background_rembg(str(image_path))
        
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGBA'
    
    @patch('ml.segmentation.processor._HAS_REMBG', False)
    def test_remove_background_rembg_not_available(self, tmp_path):
        """Test removing background when rembg is not available."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        with pytest.raises(RuntimeError, match="rembg no disponible"):
            _remove_background_rembg(str(image_path))


class TestProcessedDirForToday:
    """Tests for _processed_dir_for_today function."""
    
    @patch('ml.segmentation.processor.datetime')
    def test_processed_dir_for_today(self, mock_datetime, tmp_path):
        """Test getting processed directory for today."""
        from datetime import datetime
        
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        
        with patch('ml.segmentation.processor.Path') as mock_path:
            mock_path.return_value = tmp_path / "media" / "cacao_images" / "processed" / "2024" / "01" / "15"
            
            result = _processed_dir_for_today()
            
            assert result is not None


class TestSaveProcessedPng:
    """Tests for save_processed_png function."""
    
    @patch('ml.segmentation.processor._processed_dir_for_today')
    def test_save_processed_png(self, mock_dir, tmp_path):
        """Test saving processed PNG."""
        mock_dir.return_value = tmp_path
        
        pil_image = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        
        result = save_processed_png(pil_image, "test_output.png")
        
        assert isinstance(result, Path)
        assert (tmp_path / "test_output.png").exists()


class TestProcessWithOpencv:
    """Tests for _process_with_opencv function."""
    
    @patch('ml.segmentation.processor._remove_background_opencv')
    def test_process_with_opencv_success(self, mock_remove, tmp_path):
        """Test processing with OpenCV successfully."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_remove.return_value = mock_result
        
        result = _process_with_opencv(str(image_path), "test_image.jpg")
        
        assert isinstance(result, Image.Image)
    
    @patch('ml.segmentation.processor._remove_background_opencv')
    def test_process_with_opencv_error(self, mock_remove, tmp_path):
        """Test processing with OpenCV when error occurs."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_remove.side_effect = Exception("OpenCV error")
        
        with pytest.raises(FileNotFoundError):
            _process_with_opencv(str(image_path), "test_image.jpg")


class TestProcessWithPriorityChain:
    """Tests for _process_with_priority_chain function."""
    
    @patch('ml.segmentation.processor.remove_background_ai')
    def test_process_with_priority_chain_ai_success(self, mock_ai, tmp_path):
        """Test processing with priority chain using AI successfully."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_ai.return_value = mock_result
        
        result = _process_with_priority_chain(str(image_path), "test_image.jpg")
        
        assert isinstance(result, Image.Image)
        mock_ai.assert_called_once()
    
    @patch('ml.segmentation.processor._try_rembg_then_opencv')
    @patch('ml.segmentation.processor.remove_background_ai')
    def test_process_with_priority_chain_ai_fallback(self, mock_ai, mock_fallback, tmp_path):
        """Test processing with priority chain falling back when AI fails."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_ai.side_effect = Exception("AI error")
        mock_fallback.return_value = mock_result
        
        result = _process_with_priority_chain(str(image_path), "test_image.jpg")
        
        assert isinstance(result, Image.Image)
        mock_fallback.assert_called_once()


class TestTryRembgThenOpencv:
    """Tests for _try_rembg_then_opencv function."""
    
    @patch('ml.segmentation.processor._HAS_REMBG', True)
    @patch('ml.segmentation.processor._remove_background_rembg')
    def test_try_rembg_then_opencv_rembg_success(self, mock_rembg, tmp_path):
        """Test trying rembg then OpenCV with rembg success."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_rembg.return_value = mock_result
        
        result = _try_rembg_then_opencv(str(image_path), "test_image.jpg")
        
        assert isinstance(result, Image.Image)
    
    @patch('ml.segmentation.processor._try_opencv_fallback')
    @patch('ml.segmentation.processor._HAS_REMBG', True)
    @patch('ml.segmentation.processor._remove_background_rembg')
    def test_try_rembg_then_opencv_fallback(self, mock_rembg, mock_fallback, tmp_path):
        """Test trying rembg then OpenCV with fallback."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_rembg.side_effect = Exception("rembg error")
        mock_fallback.return_value = mock_result
        
        result = _try_rembg_then_opencv(str(image_path), "test_image.jpg")
        
        assert isinstance(result, Image.Image)
        mock_fallback.assert_called_once()


class TestTryOpencvFallback:
    """Tests for _try_opencv_fallback function."""
    
    @patch('ml.segmentation.processor._remove_background_opencv')
    def test_try_opencv_fallback_success(self, mock_opencv, tmp_path):
        """Test OpenCV fallback successfully."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_opencv.return_value = mock_result
        
        result = _try_opencv_fallback(str(image_path), "test_image.jpg")
        
        assert isinstance(result, Image.Image)
    
    @patch('ml.segmentation.processor._remove_background_opencv')
    def test_try_opencv_fallback_error(self, mock_opencv, tmp_path):
        """Test OpenCV fallback when error occurs."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_opencv.side_effect = Exception("OpenCV error")
        
        with pytest.raises(FileNotFoundError):
            _try_opencv_fallback(str(image_path), "test_image.jpg")


class TestSegmentAndCropCacaoBean:
    """Tests for segment_and_crop_cacao_bean function."""
    
    @patch('ml.segmentation.processor._process_with_opencv')
    @patch('ml.segmentation.processor.save_processed_png')
    def test_segment_and_crop_cacao_bean_opencv(self, mock_save, mock_process, tmp_path):
        """Test segmenting and cropping with OpenCV method."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_process.return_value = mock_result
        mock_save.return_value = tmp_path / "output.png"
        
        result = segment_and_crop_cacao_bean(str(image_path), method="opencv")
        
        assert isinstance(result, str)
        mock_process.assert_called_once()
    
    @patch('ml.segmentation.processor._process_with_priority_chain')
    @patch('ml.segmentation.processor.save_processed_png')
    def test_segment_and_crop_cacao_bean_ai(self, mock_save, mock_process, tmp_path):
        """Test segmenting and cropping with AI method."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image")
        
        mock_result = Image.new('RGBA', (100, 100))
        mock_process.return_value = mock_result
        mock_save.return_value = tmp_path / "output.png"
        
        result = segment_and_crop_cacao_bean(str(image_path), method="ai")
        
        assert isinstance(result, str)
        mock_process.assert_called_once()
    
    def test_segment_and_crop_cacao_bean_image_not_found(self, tmp_path):
        """Test segmenting and cropping when image doesn't exist."""
        image_path = tmp_path / "nonexistent.jpg"
        
        with pytest.raises(FileNotFoundError):
            segment_and_crop_cacao_bean(str(image_path))


class TestConvertBmpToJpg:
    """Tests for convert_bmp_to_jpg function."""
    
    def test_convert_bmp_to_jpg_success(self, tmp_path):
        """Test converting BMP to JPG successfully."""
        bmp_path = tmp_path / "test_image.bmp"
        bmp_image = Image.new('RGB', (100, 100), color='red')
        bmp_image.save(bmp_path)
        
        jpg_img, info = convert_bmp_to_jpg(bmp_path)
        
        assert jpg_img is not None
        assert isinstance(jpg_img, Image.Image)
        assert info['success'] is True
        assert info['format'] == 'JPEG'
    
    def test_convert_bmp_to_jpg_non_rgb(self, tmp_path):
        """Test converting BMP to JPG with non-RGB mode."""
        bmp_path = tmp_path / "test_image.bmp"
        bmp_image = Image.new('L', (100, 100))  # Grayscale
        bmp_image.save(bmp_path)
        
        jpg_img, info = convert_bmp_to_jpg(bmp_path)
        
        assert jpg_img is not None
        assert jpg_img.mode == 'RGB'
        assert info['success'] is True
    
    def test_convert_bmp_to_jpg_error(self, tmp_path):
        """Test converting BMP to JPG when error occurs."""
        bmp_path = tmp_path / "nonexistent.bmp"
        
        jpg_img, info = convert_bmp_to_jpg(bmp_path)
        
        assert jpg_img is None
        assert info['success'] is False
        assert 'error' in info


class TestSegmentationError:
    """Tests for SegmentationError exception."""
    
    def test_segmentation_error_creation(self):
        """Test creating SegmentationError."""
        error = SegmentationError("Test error")
        
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

