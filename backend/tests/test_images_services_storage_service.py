"""
Unit tests for image storage service module (storage_service.py).
Tests image and prediction persistence operations.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from PIL import Image
import io

from images_app.services.image.storage_service import ImageStorageService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def storage_service():
    """Create an ImageStorageService instance for testing."""
    with patch('images_app.services.image.storage_service.get_models_safely') as mock_get_model:
        mock_cacao_image = Mock()
        mock_cacao_prediction = Mock()
        mock_get_model.return_value = {
            'CacaoImage': mock_cacao_image,
            'CacaoPrediction': mock_cacao_prediction
        }
        return ImageStorageService()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    return user


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
def mock_cacao_image():
    """Create a mock CacaoImage instance."""
    image = Mock()
    image.id = 1
    image.file_name = "test_image.jpg"
    image.file_size = 1024
    image.file_type = "image/jpeg"
    image.processed = False
    image.image = Mock(path='/media/test_image.jpg')
    return image


@pytest.fixture
def prediction_result():
    """Create a sample prediction result."""
    return {
        'alto_mm': 15.5,
        'ancho_mm': 12.3,
        'grosor_mm': 8.7,
        'peso_g': 1.2,
        'confidences': {
            'alto_mm': 0.95,
            'ancho_mm': 0.92,
            'grosor_mm': 0.88,
            'peso_g': 0.90
        },
        'crop_url': '/media/crops/test_crop.png',
        'debug': {'model_version': '1.0'}
    }


class TestImageStorageService:
    """Tests for ImageStorageService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        with patch('images_app.services.image.storage_service.get_models_safely'):
            service = ImageStorageService()
            assert service is not None
    
    @patch('images_app.services.image.storage_service.CacaoImage')
    @patch('images_app.services.image.storage_service.invalidate_dataset_validation_cache')
    @patch('core.utils.invalidate_system_stats_cache')
    def test_save_uploaded_image_success(self, mock_invalidate_stats, mock_invalidate_dataset,
                                         mock_cacao_image_model, storage_service, mock_user, valid_image_file):
        """Test successful image upload."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.file_name = "test_image.jpg"
        mock_cacao_image_model.return_value = mock_image
        
        result = storage_service.save_uploaded_image(valid_image_file, mock_user)
        
        assert result.success is True
        assert result.data == mock_image
        mock_image.save.assert_called_once()
        mock_invalidate_dataset.assert_called_once()
        mock_invalidate_stats.assert_called_once()
    
    @patch('images_app.services.image.storage_service.CacaoImage')
    def test_save_uploaded_image_failure(self, mock_cacao_image_model, storage_service, mock_user, valid_image_file):
        """Test image upload failure."""
        mock_cacao_image_model.side_effect = Exception("Database error")
        
        result = storage_service.save_uploaded_image(valid_image_file, mock_user)
        
        assert result.success is False
        assert "error" in result.error.message.lower()
    
    @patch('images_app.services.image.storage_service.CacaoImage')
    @patch('images_app.services.image.storage_service.invalidate_dataset_validation_cache')
    @patch('core.utils.invalidate_system_stats_cache')
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_save_uploaded_image_with_segmentation_success(self, mock_segment, mock_invalidate_stats,
                                                           mock_invalidate_dataset, mock_cacao_image_model,
                                                           storage_service, mock_user, valid_image_file, tmp_path):
        """Test successful image upload with segmentation."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.file_name = "test_image.jpg"
        mock_image.image.path = str(tmp_path / "test_image.jpg")
        mock_cacao_image_model.return_value = mock_image
        
        processed_path = str(tmp_path / "processed.png")
        mock_segment.return_value = processed_path
        
        result = storage_service.save_uploaded_image_with_segmentation(valid_image_file, mock_user)
        
        assert result.success is True
        assert 'cacao_image' in result.data
        assert 'processed_png_path' in result.data
        mock_image.save.assert_called_once()
        mock_segment.assert_called_once()
    
    @patch('images_app.services.image.storage_service.CacaoImage')
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_save_uploaded_image_with_segmentation_no_segmentation(self, mock_segment, mock_cacao_image_model,
                                                                   storage_service, mock_user, valid_image_file, tmp_path):
        """Test image upload with segmentation when segmentation returns None."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.file_name = "test_image.jpg"
        mock_image.image.path = str(tmp_path / "test_image.jpg")
        mock_cacao_image_model.return_value = mock_image
        
        mock_segment.return_value = None
        
        result = storage_service.save_uploaded_image_with_segmentation(valid_image_file, mock_user)
        
        assert result.success is True
        assert result.data['processed_png_path'] is None
    
    @patch('images_app.services.image.storage_service.CacaoImage')
    @patch('ml.segmentation.processor.segment_and_crop_cacao_bean')
    def test_save_uploaded_image_with_segmentation_segmentation_error(self, mock_segment, mock_cacao_image_model,
                                                                       storage_service, mock_user, valid_image_file, tmp_path):
        """Test image upload with segmentation when segmentation fails."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.file_name = "test_image.jpg"
        mock_image.image.path = str(tmp_path / "test_image.jpg")
        mock_cacao_image_model.return_value = mock_image
        
        mock_segment.side_effect = Exception("Segmentation error")
        
        result = storage_service.save_uploaded_image_with_segmentation(valid_image_file, mock_user)
        
        assert result.success is True  # Image is still saved even if segmentation fails
        assert result.data['processed_png_path'] is None
    
    @patch('images_app.services.image.storage_service.CacaoImage')
    @patch('images_app.services.image.storage_service.invalidate_dataset_validation_cache')
    @patch('core.utils.invalidate_system_stats_cache')
    def test_save_uploaded_image_with_segmentation_cache_error(self, mock_invalidate_stats, mock_invalidate_dataset,
                                                                mock_cacao_image_model, storage_service,
                                                                mock_user, valid_image_file):
        """Test image upload with cache invalidation error (should still succeed)."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.file_name = "test_image.jpg"
        mock_image.image.path = '/media/test_image.jpg'
        mock_cacao_image_model.return_value = mock_image
        
        mock_invalidate_dataset.side_effect = Exception("Cache error")
        
        with patch('ml.segmentation.processor.segment_and_crop_cacao_bean', return_value=None):
            result = storage_service.save_uploaded_image_with_segmentation(valid_image_file, mock_user)
            
            assert result.success is True  # Should still succeed despite cache error
    
    @patch('images_app.services.image.storage_service.CacaoPrediction')
    @patch('core.utils.invalidate_system_stats_cache')
    def test_save_prediction_success(self, mock_invalidate_stats, mock_cacao_prediction_model,
                                    storage_service, mock_cacao_image, prediction_result):
        """Test successful prediction save."""
        mock_prediction = Mock()
        mock_prediction.id = 1
        mock_cacao_prediction_model.return_value = mock_prediction
        
        result = storage_service.save_prediction(mock_cacao_image, prediction_result, processing_time_ms=150)
        
        assert result.success is True
        assert result.data == mock_prediction
        mock_prediction.save.assert_called_once()
        assert mock_cacao_image.processed is True
        mock_cacao_image.save.assert_called_once()
        mock_invalidate_stats.assert_called_once()
    
    @patch('images_app.services.image.storage_service.CacaoPrediction')
    def test_save_prediction_calculates_average_confidence(self, mock_cacao_prediction_model,
                                                           storage_service, mock_cacao_image, prediction_result):
        """Test that average confidence is calculated correctly."""
        mock_prediction = Mock()
        mock_cacao_prediction_model.return_value = mock_prediction
        
        storage_service.save_prediction(mock_cacao_image, prediction_result, processing_time_ms=150)
        
        # Verify average_confidence was set
        call_args = mock_cacao_prediction_model.call_args[1]
        expected_avg = sum(prediction_result['confidences'].values()) / len(prediction_result['confidences'])
        assert call_args['average_confidence'] == pytest.approx(expected_avg, rel=1e-5)
    
    @patch('images_app.services.image.storage_service.CacaoPrediction')
    def test_save_prediction_with_debug_info(self, mock_cacao_prediction_model, storage_service,
                                             mock_cacao_image, prediction_result):
        """Test prediction save with debug info."""
        mock_prediction = Mock()
        mock_cacao_prediction_model.return_value = mock_prediction
        
        storage_service.save_prediction(mock_cacao_image, prediction_result, processing_time_ms=150)
        
        call_args = mock_cacao_prediction_model.call_args[1]
        assert call_args['debug_info'] == prediction_result['debug']
    
    @patch('images_app.services.image.storage_service.CacaoPrediction')
    def test_save_prediction_failure(self, mock_cacao_prediction_model, storage_service,
                                     mock_cacao_image, prediction_result):
        """Test prediction save failure."""
        mock_cacao_prediction_model.side_effect = Exception("Database error")
        
        result = storage_service.save_prediction(mock_cacao_image, prediction_result, processing_time_ms=150)
        
        assert result.success is False
        assert "error" in result.error.message.lower()
    
    @patch('images_app.services.image.storage_service.CacaoPrediction')
    @patch('core.utils.invalidate_system_stats_cache')
    def test_save_prediction_cache_error(self, mock_invalidate_stats, mock_cacao_prediction_model,
                                        storage_service, mock_cacao_image, prediction_result):
        """Test prediction save with cache invalidation error (should still succeed)."""
        mock_prediction = Mock()
        mock_cacao_prediction_model.return_value = mock_prediction
        
        mock_invalidate_stats.side_effect = Exception("Cache error")
        
        result = storage_service.save_prediction(mock_cacao_image, prediction_result, processing_time_ms=150)
        
        assert result.success is True  # Should still succeed despite cache error

