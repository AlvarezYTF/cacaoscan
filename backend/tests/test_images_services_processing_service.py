"""
Unit tests for image processing service module (processing_service.py).
Tests image validation, loading, and segmentation functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from images_app.services.image.processing_service import ImageProcessingService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def processing_service():
    """Create an ImageProcessingService instance for testing."""
    return ImageProcessingService()


@pytest.fixture
def valid_image_file():
    """Create a valid image file for testing."""
    img = Image.new('RGB', (512, 512), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=img_bytes.getvalue(),
        content_type="image/jpeg"
    )


@pytest.fixture
def invalid_image_file():
    """Create an invalid image file for testing."""
    return SimpleUploadedFile(
        name="test.txt",
        content=b"not an image",
        content_type="text/plain"
    )


@pytest.fixture
def large_image_file():
    """Create a large image file for testing."""
    # Create a file larger than max_file_size
    large_content = b"x" * (25 * 1024 * 1024)  # 25MB
    return SimpleUploadedFile(
        name="large_image.jpg",
        content=large_content,
        content_type="image/jpeg"
    )


class TestImageProcessingService:
    """Tests for ImageProcessingService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = ImageProcessingService()
        
        assert service.allowed_image_types == ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
        assert service.max_file_size == 20 * 1024 * 1024
        assert service.max_analysis_size == 8 * 1024 * 1024
    
    def test_validate_image_file_success(self, processing_service, valid_image_file):
        """Test successful image file validation."""
        result = processing_service.validate_image_file(valid_image_file)
        
        assert result.success is True
    
    def test_validate_image_file_invalid_type(self, processing_service, invalid_image_file):
        """Test validation with invalid file type."""
        result = processing_service.validate_image_file(invalid_image_file)
        
        assert result.success is False
        assert "not allowed" in result.error.message.lower()
    
    def test_validate_image_file_too_large(self, processing_service, large_image_file):
        """Test validation with file too large."""
        result = processing_service.validate_image_file(large_image_file)
        
        assert result.success is False
        assert "too large" in result.error.message.lower()
    
    def test_validate_image_file_corrupted(self, processing_service):
        """Test validation with corrupted image."""
        corrupted_file = SimpleUploadedFile(
            name="corrupted.jpg",
            content=b"corrupted image data",
            content_type="image/jpeg"
        )
        
        result = processing_service.validate_image_file(corrupted_file)
        
        assert result.success is False
        assert "invalid" in result.error.message.lower() or "corrupted" in result.error.message.lower()
    
    def test_validate_image_file_complete_success(self, processing_service, valid_image_file):
        """Test complete image file validation."""
        result = processing_service.validate_image_file_complete(valid_image_file)
        
        assert result.success is True
    
    def test_validate_image_file_complete_too_small(self, processing_service):
        """Test validation with image too small."""
        small_img = Image.new('RGB', (30, 30), color='red')
        img_bytes = io.BytesIO()
        small_img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        small_file = SimpleUploadedFile(
            name="small.jpg",
            content=img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        result = processing_service.validate_image_file_complete(small_file)
        
        assert result.success is False
        assert "too small" in result.error.message.lower()
    
    def test_validate_image_file_complete_invalid_filename(self, processing_service):
        """Test validation with invalid filename."""
        img = Image.new('RGB', (512, 512), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        invalid_name_file = SimpleUploadedFile(
            name="a" * 300,  # Too long filename
            content=img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        result = processing_service.validate_image_file_complete(invalid_name_file)
        
        assert result.success is False
        assert "filename" in result.error.message.lower()
    
    def test_load_image_success(self, processing_service, valid_image_file):
        """Test successful image loading."""
        result = processing_service.load_image(valid_image_file)
        
        assert result.success is True
        assert 'data' in result.data
        assert isinstance(result.data['data'], Image.Image)
    
    def test_load_image_converts_to_rgb(self, processing_service):
        """Test that non-RGB images are converted to RGB."""
        gray_img = Image.new('L', (512, 512))
        img_bytes = io.BytesIO()
        gray_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        gray_file = SimpleUploadedFile(
            name="gray.png",
            content=img_bytes.getvalue(),
            content_type="image/png"
        )
        
        result = processing_service.load_image(gray_file)
        
        assert result.success is True
        assert result.data['data'].mode == 'RGB'
    
    def test_load_image_failure(self, processing_service):
        """Test image loading failure."""
        corrupted_file = SimpleUploadedFile(
            name="corrupted.jpg",
            content=b"invalid image data",
            content_type="image/jpeg"
        )
        
        result = processing_service.load_image(corrupted_file)
        
        assert result.success is False
    
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_segment_image_success(self, mock_segment, processing_service, tmp_path):
        """Test successful image segmentation."""
        mock_segment.return_value = str(tmp_path / "segmented.png")
        
        result = processing_service.segment_image(str(tmp_path / "input.jpg"), method="opencv")
        
        assert result.success is True
        assert 'processed_png_path' in result.data
    
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_segment_image_failure(self, mock_segment, processing_service):
        """Test image segmentation failure."""
        mock_segment.return_value = None
        
        result = processing_service.segment_image("test_image.jpg", method="opencv")
        
        assert result.success is False
        assert "empty result" in result.error.message.lower()
    
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_segment_image_exception(self, mock_segment, processing_service):
        """Test image segmentation with exception."""
        mock_segment.side_effect = Exception("Segmentation error")
        
        result = processing_service.segment_image("test_image.jpg", method="opencv")
        
        assert result.success is False
        assert "error" in result.error.message.lower()

