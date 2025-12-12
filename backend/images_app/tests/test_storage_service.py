"""
Tests for image storage service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from images_app.services.image.storage_service import ImageStorageService


@pytest.fixture
def storage_service():
    """Create a storage service instance."""
    return ImageStorageService()


@pytest.fixture
def mock_image_file():
    """Create a mock image file."""
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'fake image content',
        content_type='image/jpeg'
    )


@pytest.fixture
def user(db):
    """Create a test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestImageStorageService:
    """Tests for ImageStorageService."""
    
    def test_save_uploaded_image_success(self, storage_service, mock_image_file, user):
        """Test successful image save."""
        with patch('images_app.services.image.storage_service.CacaoImage') as mock_model:
            mock_instance = Mock()
            mock_instance.id = 1
            mock_instance.save = Mock()
            mock_model.return_value = mock_instance
            
            with patch('core.utils.invalidate_dataset_validation_cache'):
                with patch('core.utils.invalidate_system_stats_cache'):
                    result = storage_service.save_uploaded_image(mock_image_file, user)
                    
                    assert result.success is True
                    assert result.data == mock_instance
                    assert mock_instance.save.called
    
    def test_save_uploaded_image_error(self, storage_service, mock_image_file, user):
        """Test image save with error."""
        with patch('images_app.services.image.storage_service.CacaoImage') as mock_model:
            mock_model.side_effect = Exception("Database error")
            
            result = storage_service.save_uploaded_image(mock_image_file, user)
            
            assert result.success is False
            assert result.error is not None
    
    def test_save_uploaded_image_with_segmentation_success(self, storage_service, mock_image_file, user):
        """Test successful image save with segmentation."""
        # Patch CacaoImage to return a mock instance when instantiated
        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.image = Mock()
        mock_instance.image.path = '/path/to/image.jpg'
        mock_instance.save = Mock()
        
        # Create a mock class that returns mock_instance when instantiated
        mock_cacao_image_class = Mock(return_value=mock_instance)
        
        with patch('images_app.services.image.storage_service.CacaoImage', mock_cacao_image_class):
            with patch('core.utils.invalidate_dataset_validation_cache'):
                with patch('core.utils.invalidate_system_stats_cache'):
                    with patch('ml.segmentation.processor.segment_and_crop_cacao_bean', return_value='/path/to/segmented.png'):
                        result = storage_service.save_uploaded_image_with_segmentation(mock_image_file, user)
                        
                        assert result.success is True
                        assert 'cacao_image' in result.data
                        assert 'processed_png_path' in result.data
    
    def test_save_uploaded_image_with_segmentation_segmentation_error(self, storage_service, mock_image_file, user):
        """Test image save with segmentation error."""
        # Patch CacaoImage to return a mock instance when instantiated
        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.image = Mock()
        mock_instance.image.path = '/path/to/image.jpg'
        mock_instance.save = Mock()
        
        # Create a mock class that returns mock_instance when instantiated
        mock_cacao_image_class = Mock(return_value=mock_instance)
        
        with patch('images_app.services.image.storage_service.CacaoImage', mock_cacao_image_class):
            with patch('core.utils.invalidate_dataset_validation_cache'):
                with patch('core.utils.invalidate_system_stats_cache'):
                    with patch('ml.segmentation.processor.segment_and_crop_cacao_bean', side_effect=Exception("Segmentation error")):
                        result = storage_service.save_uploaded_image_with_segmentation(mock_image_file, user)
                        
                        # Should still succeed but without segmentation
                        assert result.success is True
    
    def test_save_prediction_success(self, storage_service, user):
        """Test successful prediction save."""
        with patch('images_app.services.image.storage_service.CacaoImage') as mock_image_model:
            with patch('images_app.services.image.storage_service.CacaoPrediction') as mock_prediction_model:
                mock_image = Mock()
                mock_image.id = 1
                mock_image.processed = False
                mock_image.save = Mock()
                
                mock_prediction = Mock()
                mock_prediction.id = 1
                mock_prediction.save = Mock()
                mock_prediction_model.return_value = mock_prediction
                
                with patch('core.utils.invalidate_system_stats_cache'):
                    prediction_result = {
                        'alto_mm': 25.5,
                        'ancho_mm': 20.3,
                        'grosor_mm': 15.2,
                        'peso_g': 8.5,
                        'confidences': {
                            'alto': 0.95,
                            'ancho': 0.92,
                            'grosor': 0.88,
                            'peso': 0.90
                        },
                        'crop_url': '/path/to/crop.jpg'
                    }
                    
                    result = storage_service.save_prediction(mock_image, prediction_result, 150)
                    
                    assert result.success is True
                    assert result.data == mock_prediction
                    assert mock_prediction.save.called
                    assert mock_image.processed is True
                    assert mock_image.save.called
    
    def test_save_prediction_error(self, storage_service, user):
        """Test prediction save with error."""
        with patch('images_app.services.image.storage_service.CacaoPrediction') as mock_prediction_model:
            mock_prediction_model.side_effect = Exception("Database error")
            
            mock_image = Mock()
            prediction_result = {
                'alto_mm': 25.5,
                'ancho_mm': 20.3,
                'grosor_mm': 15.2,
                'peso_g': 8.5,
                'confidences': {
                    'alto': 0.95,
                    'ancho': 0.92,
                    'grosor': 0.88,
                    'peso': 0.90
                }
            }
            
            result = storage_service.save_prediction(mock_image, prediction_result, 150)
            
            assert result.success is False
            assert result.error is not None

