"""
Unit tests for segmentation processor (processor.py).
Tests segment_and_crop_cacao_bean and related functions.
"""
import pytest
import numpy as np
from pathlib import Path
from PIL import Image
from unittest.mock import patch, MagicMock, Mock

from ml.segmentation.processor import (
    segment_and_crop_cacao_bean,
    SegmentationError,
    _remove_background_opencv,
    _remove_background_rembg,
    save_processed_png,
    convert_bmp_to_jpg
)


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a sample image file for testing."""
    img_path = tmp_path / "test_image.jpg"
    img = Image.new('RGB', (512, 512), color='red')
    img.save(img_path, format='JPEG')
    return str(img_path)


@pytest.fixture
def sample_bmp_path(tmp_path):
    """Create a sample BMP file for testing."""
    bmp_path = tmp_path / "test_image.bmp"
    img = Image.new('RGB', (512, 512), color='blue')
    img.save(bmp_path, format='BMP')
    return bmp_path


class TestSegmentAndCropCacaoBean:
    """Tests for segment_and_crop_cacao_bean function."""
    
    def test_segment_file_not_found(self):
        """Test segmentation with non-existent file."""
        with pytest.raises(FileNotFoundError, match="no existe"):
            segment_and_crop_cacao_bean("nonexistent.jpg", method="ai")
    
    def test_segment_method_opencv(self, sample_image_path):
        """Test segmentation with OpenCV method."""
        with patch('ml.segmentation.processor._process_with_opencv') as mock_opencv:
            mock_opencv.return_value = Image.new('RGBA', (100, 100), color='red')
            with patch('ml.segmentation.processor.save_processed_png', return_value=Path('/tmp/output.png')):
                result = segment_and_crop_cacao_bean(sample_image_path, method="opencv")
                
                assert isinstance(result, str)
                assert result.endswith('.png')
                mock_opencv.assert_called_once()
    
    def test_segment_method_ai(self, sample_image_path):
        """Test segmentation with AI method (priority chain)."""
        with patch('ml.segmentation.processor._process_with_priority_chain') as mock_chain:
            mock_chain.return_value = Image.new('RGBA', (100, 100), color='red')
            with patch('ml.segmentation.processor.save_processed_png', return_value=Path('/tmp/output.png')):
                result = segment_and_crop_cacao_bean(sample_image_path, method="ai")
                
                assert isinstance(result, str)
                mock_chain.assert_called_once()
    
    def test_segment_method_default(self, sample_image_path):
        """Test segmentation with default method (should use AI)."""
        with patch('ml.segmentation.processor._process_with_priority_chain') as mock_chain:
            mock_chain.return_value = Image.new('RGBA', (100, 100), color='red')
            with patch('ml.segmentation.processor.save_processed_png', return_value=Path('/tmp/output.png')):
                result = segment_and_crop_cacao_bean(sample_image_path, method=None)
                
                assert isinstance(result, str)
                mock_chain.assert_called_once()
    
    def test_segment_creates_output_file(self, sample_image_path):
        """Test that segmentation creates output file."""
        with patch('ml.segmentation.processor._process_with_priority_chain') as mock_chain:
            mock_chain.return_value = Image.new('RGBA', (100, 100), color='red')
            with patch('ml.segmentation.processor.save_processed_png') as mock_save:
                output_path = Path('/tmp/test_output.png')
                mock_save.return_value = output_path
                
                result = segment_and_crop_cacao_bean(sample_image_path, method="ai")
                
                assert result == str(output_path)
                mock_save.assert_called_once()


class TestRemoveBackgroundOpenCV:
    """Tests for _remove_background_opencv function."""
    
    def test_remove_background_opencv_success(self, sample_image_path):
        """Test successful background removal with OpenCV."""
        result = _remove_background_opencv(sample_image_path)
        
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGBA'
        assert result.size[0] > 0
        assert result.size[1] > 0
    
    def test_remove_background_opencv_file_not_found(self):
        """Test OpenCV background removal with non-existent file."""
        with pytest.raises(FileNotFoundError):
            _remove_background_opencv("nonexistent.jpg")
    
    def test_remove_background_opencv_returns_rgba(self, sample_image_path):
        """Test that OpenCV returns RGBA image."""
        result = _remove_background_opencv(sample_image_path)
        
        assert result.mode == 'RGBA'
        assert result.size[0] > 0
        assert result.size[1] > 0


class TestRemoveBackgroundRembg:
    """Tests for _remove_background_rembg function."""
    
    def test_remove_background_rembg_success(self, sample_image_path):
        """Test successful background removal with rembg."""
        try:
            result = _remove_background_rembg(sample_image_path)
            
            assert isinstance(result, Image.Image)
            assert result.mode == 'RGBA'
        except RuntimeError:
            # rembg might not be available
            pytest.skip("rembg not available")
    
    def test_remove_background_rembg_not_available(self, sample_image_path):
        """Test rembg when not available."""
        with patch('ml.segmentation.processor._HAS_REMBG', False):
            with pytest.raises(RuntimeError, match="rembg no disponible"):
                _remove_background_rembg(sample_image_path)


class TestSaveProcessedPNG:
    """Tests for save_processed_png function."""
    
    def test_save_processed_png_success(self, tmp_path):
        """Test successful PNG save."""
        img = Image.new('RGBA', (100, 100), color='red')
        output_path = save_processed_png(img, "test_output.png")
        
        assert isinstance(output_path, Path)
        assert output_path.exists()
        assert output_path.suffix == '.png'
        
        # Verify image can be loaded
        loaded = Image.open(output_path)
        assert loaded.mode == 'RGBA'
        assert loaded.size == (100, 100)
    
    def test_save_processed_png_creates_directory(self, tmp_path):
        """Test that save_processed_png creates nested directories."""
        img = Image.new('RGBA', (100, 100), color='red')
        
        # Should create year/month/day structure
        output_path = save_processed_png(img, "test_output.png")
        
        assert output_path.exists()
        assert output_path.parent.exists()
    
    def test_save_processed_png_preserves_rgba(self, tmp_path):
        """Test that RGBA mode is preserved."""
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        output_path = save_processed_png(img, "test_output.png")
        
        loaded = Image.open(output_path)
        assert loaded.mode == 'RGBA'


class TestConvertBMPToJPG:
    """Tests for convert_bmp_to_jpg function."""
    
    def test_convert_bmp_to_jpg_success(self, sample_bmp_path):
        """Test successful BMP to JPG conversion."""
        jpg_img, result = convert_bmp_to_jpg(sample_bmp_path)
        
        assert result['success'] is True
        assert jpg_img is not None
        assert isinstance(jpg_img, Image.Image)
        assert jpg_img.format == 'JPEG'
        assert jpg_img.mode == 'RGB'
    
    def test_convert_bmp_to_jpg_non_bmp(self, tmp_path):
        """Test conversion with non-BMP file."""
        jpg_path = tmp_path / "test.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(jpg_path, format='JPEG')
        
        # Should still work (converts to RGB)
        jpg_img, result = convert_bmp_to_jpg(jpg_path)
        
        assert result['success'] is True
        assert jpg_img is not None
    
    def test_convert_bmp_to_jpg_error(self, tmp_path):
        """Test conversion with invalid file."""
        invalid_path = tmp_path / "invalid.bmp"
        invalid_path.write_text("not an image")
        
        jpg_img, result = convert_bmp_to_jpg(invalid_path)
        
        assert result['success'] is False
        assert 'error' in result
        assert jpg_img is None
    
    def test_convert_bmp_to_jpg_preserves_size(self, sample_bmp_path):
        """Test that conversion preserves image size."""
        original = Image.open(sample_bmp_path)
        original_size = original.size
        
        jpg_img, result = convert_bmp_to_jpg(sample_bmp_path)
        
        assert result['success'] is True
        assert jpg_img.size == original_size
