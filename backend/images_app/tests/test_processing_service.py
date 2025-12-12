"""
Tests for image processing service.
"""
import pytest
from unittest.mock import Mock, patch
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from images_app.services.image import ImageProcessingService
from api.services.base import ServiceResult


class TestImageProcessingService:
    """Tests for ImageProcessingService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ImageProcessingService()
    
    @pytest.fixture
    def valid_image_file(self):
        """Create valid image file."""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg",
            img_bytes.read(),
            content_type="image/jpeg"
        )
    
    @pytest.fixture
    def invalid_image_file(self):
        """Create invalid image file."""
        return SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )
    
    def test_validate_image_file_success(self, service, valid_image_file):
        """Test validating valid image file."""
        result = service.validate_image_file(valid_image_file)
        
        assert result.success
    
    def test_validate_image_file_invalid_type(self, service, invalid_image_file):
        """Test validating image file with invalid type."""
        result = service.validate_image_file(invalid_image_file)
        
        assert not result.success
    
    def test_validate_image_file_too_large(self, service):
        """Test validating image file that's too large."""
        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (21 * 1024 * 1024),  # 21MB
            content_type="image/jpeg"
        )
        
        result = service.validate_image_file(large_file)
        
        assert not result.success
    
    def test_validate_image_file_complete_success(self, service, valid_image_file):
        """Test complete validation of valid image file."""
        result = service.validate_image_file_complete(valid_image_file)
        
        assert result.success
    
    def test_validate_image_file_complete_too_small(self, service):
        """Test validating image file that's too small."""
        small_img = Image.new('RGB', (30, 30), color='red')
        img_bytes = io.BytesIO()
        small_img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        small_file = SimpleUploadedFile(
            "small.jpg",
            img_bytes.read(),
            content_type="image/jpeg"
        )
        
        result = service.validate_image_file_complete(small_file)
        
        assert not result.success
    
    def test_validate_image_file_complete_invalid_filename(self, service, valid_image_file):
        """Test validating image file with invalid filename."""
        # Create a mock file with empty name to test validation
        # We use a mock to avoid SuspiciousFileOperation during file creation
        from unittest.mock import Mock, MagicMock
        empty_name_file = MagicMock(spec=SimpleUploadedFile)
        empty_name_file.name = ''
        empty_name_file.content_type = 'image/jpeg'
        valid_image_file.seek(0)
        empty_name_file.size = len(valid_image_file.read())
        valid_image_file.seek(0)
        empty_name_file.read.return_value = valid_image_file.read()
        empty_name_file.seek = valid_image_file.seek
        
        # The service should catch the empty filename and return validation error
        # before Django tries to use it
        result = service.validate_image_file_complete(empty_name_file)
        
        assert not result.success
    
    def test_load_image_success(self, service, valid_image_file):
        """Test loading image successfully."""
        result = service.load_image(valid_image_file)
        
        assert result.success
        assert result.data is not None
        assert isinstance(result.data, Image.Image)
    
    def test_load_image_converts_to_rgb(self, service):
        """Test loading image converts to RGB."""
        # Create RGBA image
        rgba_img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        img_bytes = io.BytesIO()
        rgba_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        rgba_file = SimpleUploadedFile(
            "test.png",
            img_bytes.read(),
            content_type="image/png"
        )
        
        result = service.load_image(rgba_file)
        
        assert result.success
        assert result.data.mode == 'RGB'
    
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_segment_image_success(self, mock_segment, service, tmp_path):
        """Test segmenting image successfully."""
        image_path = str(tmp_path / "test.jpg")
        mock_segment.return_value = str(tmp_path / "segmented.png")
        
        result = service.segment_image(image_path, method="opencv")
        
        assert result.success
        assert 'processed_png_path' in result.data
    
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_segment_image_empty_result(self, mock_segment, service, tmp_path):
        """Test segmenting image with empty result."""
        image_path = str(tmp_path / "test.jpg")
        mock_segment.return_value = None
        
        result = service.segment_image(image_path, method="opencv")
        
        assert not result.success

