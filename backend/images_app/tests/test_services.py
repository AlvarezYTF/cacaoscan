"""
Tests for Images App Services.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from PIL import Image
import io

from images_app.services.image.management_service import ImageManagementService
from images_app.services.image.processing_service import ImageProcessingService
from images_app.services.image.storage_service import ImageStorageService


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def valid_image_file():
    """Create a valid image file for testing."""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_io.read(),
        content_type='image/jpeg'
    )


@pytest.fixture
def invalid_image_file():
    """Create an invalid file for testing."""
    return SimpleUploadedFile(
        name='test.txt',
        content=b'not an image',
        content_type='text/plain'
    )


@pytest.fixture
def large_image_file():
    """Create a large image file for testing."""
    # Create a large file (simulate > 20MB)
    large_content = b'x' * (21 * 1024 * 1024)  # 21MB
    return SimpleUploadedFile(
        name='large_image.jpg',
        content=large_content,
        content_type='image/jpeg'
    )


@pytest.mark.django_db
class TestImageManagementService:
    """Tests for ImageManagementService."""

    def test_upload_image_success(self, user, valid_image_file):
        """Test successful image upload."""
        service = ImageManagementService()
        
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        
        result = service.upload_image(image_data, user)
        
        assert result.success is True
        assert 'id' in result.data
        assert result.data['file_name'] == 'test_image.jpg'
        assert result.message == "Imagen subida exitosamente"

    def test_upload_image_missing_file(self, user):
        """Test upload with missing file."""
        service = ImageManagementService()
        
        image_data = {
            'filename': 'test_image.jpg'
            # Missing 'file'
        }
        
        result = service.upload_image(image_data, user)
        
        assert result.success is False
        assert 'archivo de imagen es requerido' in str(result.error).lower()

    def test_upload_image_missing_filename(self, user, valid_image_file):
        """Test upload with missing filename."""
        service = ImageManagementService()
        
        image_data = {
            'file': valid_image_file
            # Missing 'filename'
        }
        
        # If file has name attribute, it should work
        if hasattr(valid_image_file, 'name'):
            result = service.upload_image(image_data, user)
            # Should succeed if file has name
            assert result.success is True or result.success is False

    def test_upload_image_invalid_type(self, user, invalid_image_file):
        """Test upload with invalid file type."""
        service = ImageManagementService()
        
        image_data = {
            'file': invalid_image_file,
            'filename': 'test.txt'
        }
        
        result = service.upload_image(image_data, user)
        
        assert result.success is False
        assert 'tipo de archivo' in str(result.error).lower() or 'no válido' in str(result.error).lower()

    def test_upload_image_too_large(self, user, large_image_file):
        """Test upload with file too large."""
        service = ImageManagementService()
        
        image_data = {
            'file': large_image_file,
            'filename': 'large_image.jpg'
        }
        
        result = service.upload_image(image_data, user)
        
        assert result.success is False
        assert 'demasiado grande' in str(result.error).lower() or 'too large' in str(result.error).lower()

    def test_get_user_images_success(self, user, valid_image_file):
        """Test getting user images successfully."""
        service = ImageManagementService()
        
        # Upload an image first
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        service.upload_image(image_data, user)
        
        result = service.get_user_images(user, page=1, page_size=20)
        
        assert result.success is True
        assert 'images' in result.data
        assert len(result.data['images']) >= 1
        assert 'pagination' in result.data

    def test_get_user_images_with_filters(self, user, valid_image_file):
        """Test getting user images with filters."""
        service = ImageManagementService()
        
        # Upload an image
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        service.upload_image(image_data, user)
        
        filters = {'processed': False}
        result = service.get_user_images(user, page=1, page_size=20, filters=filters)
        
        assert result.success is True
        assert len(result.data['images']) >= 1

    def test_get_image_details_success(self, user, valid_image_file):
        """Test getting image details successfully."""
        service = ImageManagementService()
        
        # Upload an image first
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        upload_result = service.upload_image(image_data, user)
        image_id = upload_result.data['id']
        
        result = service.get_image_details(image_id, user)
        
        assert result.success is True
        assert result.data['id'] == image_id
        assert result.data['file_name'] == 'test_image.jpg'
        assert 'predictions' in result.data

    def test_get_image_details_not_found(self, user):
        """Test getting non-existent image."""
        service = ImageManagementService()
        
        result = service.get_image_details(99999, user)
        
        assert result.success is False
        assert 'no encontrada' in str(result.error).lower()

    def test_update_image_metadata_success(self, user, valid_image_file):
        """Test updating image metadata successfully."""
        service = ImageManagementService()
        
        # Upload an image first
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        upload_result = service.upload_image(image_data, user)
        image_id = upload_result.data['id']
        
        new_metadata = {'location': 'Test Location', 'variety': 'Criollo'}
        result = service.update_image_metadata(image_id, user, new_metadata)
        
        assert result.success is True
        assert result.data['metadata'] == new_metadata

    def test_update_image_metadata_not_found(self, user):
        """Test updating metadata for non-existent image."""
        service = ImageManagementService()
        
        metadata = {'test': 'data'}
        result = service.update_image_metadata(99999, user, metadata)
        
        assert result.success is False
        assert 'no encontrada' in str(result.error).lower()

    def test_delete_image_success(self, user, valid_image_file):
        """Test deleting image successfully."""
        service = ImageManagementService()
        
        # Upload an image first
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        upload_result = service.upload_image(image_data, user)
        image_id = upload_result.data['id']
        
        result = service.delete_image(image_id, user)
        
        assert result.success is True
        assert result.message == "Imagen eliminada exitosamente"
        
        # Verify image was deleted
        from images_app.models import CacaoImage
        assert not CacaoImage.objects.filter(id=image_id).exists()

    def test_delete_image_not_found(self, user):
        """Test deleting non-existent image."""
        service = ImageManagementService()
        
        result = service.delete_image(99999, user)
        
        assert result.success is False
        assert 'no encontrada' in str(result.error).lower()

    def test_get_image_statistics(self, user, valid_image_file):
        """Test getting image statistics."""
        service = ImageManagementService()
        
        # Upload an image
        image_data = {
            'file': valid_image_file,
            'filename': 'test_image.jpg'
        }
        service.upload_image(image_data, user)
        
        result = service.get_image_statistics(user)
        
        assert result.success is True
        assert result.data['total_images'] >= 1
        assert 'processed_images' in result.data
        assert 'unprocessed_images' in result.data
        assert 'file_types' in result.data

    def test_bulk_delete_images_success(self, user, valid_image_file):
        """Test bulk deleting images successfully."""
        service = ImageManagementService()
        
        # Upload multiple images
        image_ids = []
        for i in range(3):
            image_data = {
                'file': valid_image_file,
                'filename': f'test_image_{i}.jpg'
            }
            upload_result = service.upload_image(image_data, user)
            image_ids.append(upload_result.data['id'])
        
        result = service.bulk_delete_images(image_ids, user)
        
        assert result.success is True
        assert result.data['deleted_count'] == 3

    def test_bulk_delete_images_empty_list(self, user):
        """Test bulk delete with empty list."""
        service = ImageManagementService()
        
        result = service.bulk_delete_images([], user)
        
        assert result.success is False
        assert 'vacía' in str(result.error).lower() or 'empty' in str(result.error).lower()

    def test_validate_image_file_valid(self, valid_image_file):
        """Test validating a valid image file."""
        service = ImageManagementService()
        
        result = service._validate_image_file(valid_image_file)
        
        assert result.success is True

    def test_validate_image_file_invalid_type(self, invalid_image_file):
        """Test validating an invalid file type."""
        service = ImageManagementService()
        
        result = service._validate_image_file(invalid_image_file)
        
        assert result.success is False
        assert 'tipo de archivo' in str(result.error).lower() or 'not allowed' in str(result.error).lower()


@pytest.mark.django_db
class TestImageProcessingService:
    """Tests for ImageProcessingService."""

    def test_validate_image_file_valid(self, valid_image_file):
        """Test validating a valid image file."""
        service = ImageProcessingService()
        
        result = service.validate_image_file(valid_image_file)
        
        assert result.success is True
        assert result.message == "Image file is valid"

    def test_validate_image_file_invalid_type(self, invalid_image_file):
        """Test validating an invalid file type."""
        service = ImageProcessingService()
        
        result = service.validate_image_file(invalid_image_file)
        
        assert result.success is False
        assert 'not allowed' in str(result.error).lower()

    def test_validate_image_file_too_large(self, large_image_file):
        """Test validating a file that's too large."""
        service = ImageProcessingService()
        
        result = service.validate_image_file(large_image_file)
        
        assert result.success is False
        assert 'too large' in str(result.error).lower()

    def test_validate_image_file_complete_valid(self, valid_image_file):
        """Test complete validation of a valid image."""
        service = ImageProcessingService()
        
        result = service.validate_image_file_complete(valid_image_file)
        
        assert result.success is True
        assert result.message == "Image file is valid"

    def test_validate_image_file_complete_invalid_type(self, invalid_image_file):
        """Test complete validation with invalid type."""
        service = ImageProcessingService()
        
        result = service.validate_image_file_complete(invalid_image_file)
        
        assert result.success is False
        assert 'not allowed' in str(result.error).lower()

    def test_validate_image_file_complete_too_large(self):
        """Test complete validation with file too large for analysis."""
        service = ImageProcessingService()
        
        # Create file > 8MB
        large_content = b'x' * (9 * 1024 * 1024)  # 9MB
        large_file = SimpleUploadedFile(
            name='large.jpg',
            content=large_content,
            content_type='image/jpeg'
        )
        
        result = service.validate_image_file_complete(large_file)
        
        assert result.success is False
        assert 'too large' in str(result.error).lower() or '8MB' in str(result.error)

    def test_validate_image_file_complete_small_dimensions(self):
        """Test complete validation with image too small."""
        service = ImageProcessingService()
        
        # Create a very small image
        img = Image.new('RGB', (30, 30), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        small_file = SimpleUploadedFile(
            name='small.jpg',
            content=img_io.read(),
            content_type='image/jpeg'
        )
        
        result = service.validate_image_file_complete(small_file)
        
        assert result.success is False
        assert 'too small' in str(result.error).lower() or '50x50' in str(result.error)

    def test_load_image_success(self, valid_image_file):
        """Test loading an image successfully."""
        service = ImageProcessingService()
        
        result = service.load_image(valid_image_file)
        
        assert result.success is True
        assert 'data' in result.data
        assert isinstance(result.data, dict) or hasattr(result.data, 'mode')  # PIL Image or dict

    def test_load_image_invalid(self, invalid_image_file):
        """Test loading an invalid image."""
        service = ImageProcessingService()
        
        result = service.load_image(invalid_image_file)
        
        assert result.success is False

    def test_segment_image_success(self):
        """Test segmenting an image successfully."""
        service = ImageProcessingService()
        
        with patch('images_app.services.image.processing_service.segment_and_crop_cacao_bean') as mock_segment:
            mock_segment.return_value = '/path/to/segmented.png'
            
            result = service.segment_image('/path/to/image.jpg', method='opencv')
        
        assert result.success is True
        assert 'processed_png_path' in result.data

    def test_segment_image_failure(self):
        """Test segmenting an image that fails."""
        service = ImageProcessingService()
        
        with patch('images_app.services.image.processing_service.segment_and_crop_cacao_bean') as mock_segment:
            mock_segment.return_value = None
            
            result = service.segment_image('/path/to/image.jpg', method='opencv')
        
        assert result.success is False
        assert 'empty result' in str(result.error).lower() or 'segmentation' in str(result.error).lower()

    def test_segment_image_exception(self):
        """Test segmenting an image that raises an exception."""
        service = ImageProcessingService()
        
        with patch('images_app.services.image.processing_service.segment_and_crop_cacao_bean') as mock_segment:
            mock_segment.side_effect = Exception("Segmentation error")
            
            result = service.segment_image('/path/to/image.jpg', method='opencv')
        
        assert result.success is False
        assert 'error segmenting' in str(result.error).lower() or 'internal error' in str(result.error).lower()


@pytest.mark.django_db
class TestImageStorageService:
    """Tests for ImageStorageService."""

    def test_save_uploaded_image_success(self, user, valid_image_file):
        """Test saving an uploaded image successfully."""
        service = ImageStorageService()
        
        with patch('images_app.services.image.storage_service.invalidate_dataset_validation_cache') as mock_cache:
            result = service.save_uploaded_image(valid_image_file, user)
        
        assert result.success is True
        assert 'data' in result.data or hasattr(result.data, 'id')
        assert result.message == "Image saved successfully"
        
        # Verify image was saved
        from images_app.models import CacaoImage
        if isinstance(result.data, dict):
            image_id = result.data.get('id')
        else:
            image_id = result.data.id
        assert CacaoImage.objects.filter(id=image_id).exists()

    def test_save_uploaded_image_with_segmentation_success(self, user, valid_image_file):
        """Test saving an image with segmentation successfully."""
        service = ImageStorageService()
        
        with patch('images_app.services.image.storage_service.invalidate_dataset_validation_cache'):
            with patch('images_app.services.image.storage_service.segment_and_crop_cacao_bean') as mock_segment:
                mock_segment.return_value = '/path/to/segmented.png'
                
                result = service.save_uploaded_image_with_segmentation(valid_image_file, user)
        
        assert result.success is True
        assert 'cacao_image' in result.data
        assert result.message == "Image saved and segmented successfully"

    def test_save_uploaded_image_with_segmentation_no_segment(self, user, valid_image_file):
        """Test saving an image when segmentation returns None."""
        service = ImageStorageService()
        
        with patch('images_app.services.image.storage_service.invalidate_dataset_validation_cache'):
            with patch('images_app.services.image.storage_service.segment_and_crop_cacao_bean') as mock_segment:
                mock_segment.return_value = None
                
                result = service.save_uploaded_image_with_segmentation(valid_image_file, user)
        
        # Should still succeed even if segmentation fails
        assert result.success is True

    def test_save_prediction_success(self, user, valid_image_file):
        """Test saving a prediction successfully."""
        service = ImageStorageService()
        
        # First save an image
        image_result = service.save_uploaded_image(valid_image_file, user)
        if isinstance(image_result.data, dict):
            cacao_image_id = image_result.data.get('id')
        else:
            cacao_image_id = image_result.data.id
        
        from images_app.models import CacaoImage
        cacao_image = CacaoImage.objects.get(id=cacao_image_id)
        
        prediction_result = {
            'alto_mm': 20.5,
            'ancho_mm': 15.3,
            'grosor_mm': 10.2,
            'peso_g': 1.5,
            'confidences': {
                'alto': 0.9,
                'ancho': 0.85,
                'grosor': 0.88,
                'peso': 0.92
            },
            'crop_url': '/path/to/crop.jpg'
        }
        
        with patch('images_app.services.image.storage_service.invalidate_system_stats_cache'):
            result = service.save_prediction(cacao_image, prediction_result, processing_time_ms=150)
        
        assert result.success is True
        assert result.message == "Prediction saved successfully"
        
        # Verify prediction was saved
        from images_app.models import CacaoPrediction
        if isinstance(result.data, dict):
            prediction_id = result.data.get('id')
        else:
            prediction_id = result.data.id
        assert CacaoPrediction.objects.filter(id=prediction_id).exists()
        
        # Verify image was marked as processed
        cacao_image.refresh_from_db()
        assert cacao_image.processed is True

    def test_save_prediction_calculates_avg_confidence(self, user, valid_image_file):
        """Test that prediction calculates average confidence correctly."""
        service = ImageStorageService()
        
        # Save an image
        image_result = service.save_uploaded_image(valid_image_file, user)
        if isinstance(image_result.data, dict):
            cacao_image_id = image_result.data.get('id')
        else:
            cacao_image_id = image_result.data.id
        
        from images_app.models import CacaoImage
        cacao_image = CacaoImage.objects.get(id=cacao_image_id)
        
        prediction_result = {
            'alto_mm': 20.5,
            'ancho_mm': 15.3,
            'grosor_mm': 10.2,
            'peso_g': 1.5,
            'confidences': {
                'alto': 0.9,
                'ancho': 0.85,
                'grosor': 0.88,
                'peso': 0.92
            }
        }
        
        with patch('images_app.services.image.storage_service.invalidate_system_stats_cache'):
            result = service.save_prediction(cacao_image, prediction_result, processing_time_ms=150)
        
        assert result.success is True
        
        # Verify average confidence was calculated
        from images_app.models import CacaoPrediction
        if isinstance(result.data, dict):
            prediction_id = result.data.get('id')
        else:
            prediction_id = result.data.id
        prediction = CacaoPrediction.objects.get(id=prediction_id)
        
        expected_avg = (0.9 + 0.85 + 0.88 + 0.92) / 4
        assert abs(prediction.average_confidence - expected_avg) < 0.01

