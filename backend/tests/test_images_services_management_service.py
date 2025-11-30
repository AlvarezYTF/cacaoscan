"""
Unit tests for image management service module (management_service.py).
Tests image upload, retrieval, update, and deletion functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from PIL import Image
import io

from images_app.services.image.management_service import ImageManagementService
from api.services.base import ServiceResult, ValidationServiceError, NotFoundServiceError


@pytest.fixture
def management_service():
    """Create an ImageManagementService instance for testing."""
    with patch('images_app.services.image.management_service.get_model_safely') as mock_get_model:
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        return ImageManagementService()


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
    image.created_at = Mock(isoformat=lambda: '2024-01-01T00:00:00')
    image.updated_at = Mock(isoformat=lambda: '2024-01-01T00:00:00')
    image.image = Mock(url='/media/test_image.jpg')
    image.metadata = {}
    image.predictions = Mock(all=Mock(return_value=[]))
    return image


class TestImageManagementService:
    """Tests for ImageManagementService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        with patch('images_app.services.image.management_service.get_model_safely'):
            service = ImageManagementService()
            
            assert service.allowed_image_types == ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
            assert service.max_file_size == 20 * 1024 * 1024
    
    @patch('images_app.services.image.management_service.CacaoImage')
    def test_upload_image_success(self, mock_cacao_image_model, management_service, mock_user, valid_image_file):
        """Test successful image upload."""
        mock_image = Mock()
        mock_image.id = 1
        mock_image.file_name = "test_image.jpg"
        mock_image.file_size = 1024
        mock_image.file_type = "image/jpeg"
        mock_image.processed = False
        mock_image.created_at = Mock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_image.image = Mock(url='/media/test_image.jpg')
        mock_image.metadata = {}
        mock_cacao_image_model.return_value = mock_image
        
        with patch.object(management_service, '_validate_image_file', return_value=ServiceResult.success()):
            result = management_service.upload_image(valid_image_file, mock_user)
            
            assert result.success is True
            assert 'id' in result.data
            assert 'file_name' in result.data
    
    @patch('images_app.services.image.management_service.CacaoImage')
    def test_upload_image_validation_failure(self, mock_cacao_image_model, management_service, 
                                             mock_user, valid_image_file):
        """Test image upload with validation failure."""
        with patch.object(management_service, '_validate_image_file', 
                         return_value=ServiceResult.validation_error("Invalid file")):
            result = management_service.upload_image(valid_image_file, mock_user)
            
            assert result.success is False
    
    @patch('images_app.services.image.management_service.CacaoImage')
    def test_get_user_images_success(self, mock_cacao_image_model, management_service, mock_user):
        """Test getting user images."""
        mock_images = [
            Mock(
                id=1,
                file_name="test1.jpg",
                file_size=1024,
                file_type="image/jpeg",
                processed=True,
                created_at=Mock(isoformat=lambda: '2024-01-01T00:00:00'),
                updated_at=Mock(isoformat=lambda: '2024-01-01T00:00:00'),
                image=Mock(url='/media/test1.jpg'),
                metadata={}
            )
        ]
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value.select_related.return_value.prefetch_related.return_value.order_by.return_value = mock_queryset
        mock_cacao_image_model.objects.filter.return_value = mock_queryset
        
        with patch.object(management_service, 'paginate_results', return_value={
            'results': mock_images,
            'pagination': {'page': 1, 'total': 1}
        }):
            result = management_service.get_user_images(mock_user, page=1, page_size=20)
            
            assert result.success is True
            assert 'images' in result.data
            assert 'pagination' in result.data
    
    @patch('images_app.services.image.management_service.CacaoImage')
    def test_get_user_images_with_filters(self, mock_cacao_image_model, management_service, mock_user):
        """Test getting user images with filters."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value.select_related.return_value.prefetch_related.return_value.order_by.return_value = mock_queryset
        mock_cacao_image_model.objects.filter.return_value = mock_queryset
        
        filters = {
            'processed': True,
            'date_from': '2024-01-01',
            'date_to': '2024-12-31'
        }
        
        with patch.object(management_service, 'paginate_results', return_value={
            'results': [],
            'pagination': {'page': 1, 'total': 0}
        }):
            result = management_service.get_user_images(mock_user, page=1, page_size=20, filters=filters)
            
            assert result.success is True
    
    @patch('images_app.services.image.management_service.get_model_safely')
    def test_get_image_details_success(self, mock_get_model, management_service, 
                                       mock_user, mock_cacao_image):
        """Test getting image details."""
        # Create a proper queryset mock that is iterable - use a list directly
        mock_predictions_queryset = Mock()
        mock_predictions_queryset.order_by.return_value = []  # Empty list is iterable
        mock_cacao_image.predictions = Mock()
        mock_cacao_image.predictions.all.return_value = mock_predictions_queryset
        
        mock_model = Mock()
        mock_model.objects.select_related.return_value.prefetch_related.return_value.get.return_value = mock_cacao_image
        mock_model.DoesNotExist = Exception
        mock_get_model.return_value = mock_model
        
        result = management_service.get_image_details(1, mock_user)
        
        assert result.success is True
        assert 'id' in result.data
        assert 'predictions' in result.data
    
    @patch('images_app.services.image.management_service.get_model_safely')
    def test_get_image_details_not_found(self, mock_get_model, management_service, mock_user):
        """Test getting image details when image doesn't exist."""
        class DoesNotExist(Exception):
            pass
        
        mock_model = Mock()
        mock_model.DoesNotExist = DoesNotExist
        mock_model.objects.select_related.return_value.prefetch_related.return_value.get.side_effect = DoesNotExist()
        mock_get_model.return_value = mock_model
        
        result = management_service.get_image_details(999, mock_user)
        
        assert result.success is False
        assert result.error is not None
    
    @patch('images_app.services.image.management_service.get_model_safely')
    def test_update_image_metadata_success(self, mock_get_model, management_service,
                                          mock_user, mock_cacao_image):
        """Test updating image metadata."""
        mock_cacao_image.metadata = {'old': 'value'}
        # Mock predictions queryset to be iterable
        mock_predictions_queryset = Mock()
        mock_predictions_queryset.order_by.return_value = []
        mock_cacao_image.predictions = Mock()
        mock_cacao_image.predictions.all.return_value = mock_predictions_queryset
        mock_model = Mock()
        mock_model.objects.select_related.return_value.prefetch_related.return_value.get.return_value = mock_cacao_image
        mock_model.DoesNotExist = Exception
        mock_get_model.return_value = mock_model
        
        new_metadata = {'new': 'value', 'key': 'data'}
        result = management_service.update_image_metadata(1, mock_user, new_metadata)
        
        assert result.success is True
        assert mock_cacao_image.metadata == new_metadata
        mock_cacao_image.save.assert_called_once()
    
    @patch('images_app.services.image.management_service.get_model_safely')
    def test_delete_image_success(self, mock_get_model, management_service,
                                  mock_user, mock_cacao_image):
        """Test deleting an image."""
        # Create a proper queryset mock that is iterable - use a list directly
        mock_predictions_queryset = Mock()
        mock_predictions_queryset.order_by.return_value = []  # Empty list is iterable
        mock_cacao_image.predictions = Mock()
        mock_cacao_image.predictions.count.return_value = 2
        mock_cacao_image.predictions.all.return_value = mock_predictions_queryset
        
        mock_model = Mock()
        mock_model.objects.select_related.return_value.prefetch_related.return_value.get.return_value = mock_cacao_image
        mock_model.DoesNotExist = Exception
        mock_get_model.return_value = mock_model
        
        result = management_service.delete_image(1, mock_user)
        
        assert result.success is True
        mock_cacao_image.delete.assert_called_once()
    
    @patch('images_app.services.image.management_service.get_model_safely')
    def test_bulk_delete_images_success(self, mock_get_model, management_service, mock_user):
        """Test bulk deleting images."""
        mock_images = [Mock(id=1), Mock(id=2)]
        mock_queryset = Mock()
        mock_queryset.filter.return_value.select_related.return_value.prefetch_related.return_value = mock_queryset
        mock_queryset.__len__ = Mock(return_value=2)
        mock_queryset.count.return_value = 2
        mock_model = Mock()
        mock_model.objects.filter.return_value = mock_queryset
        mock_get_model.return_value = mock_model
        
        result = management_service.bulk_delete_images([1, 2], mock_user)
        
        assert result.success is True
        assert result.data['deleted_count'] == 2
    
    def test_bulk_delete_images_empty_list(self, management_service, mock_user):
        """Test bulk delete with empty list."""
        result = management_service.bulk_delete_images([], mock_user)
        
        assert result.success is False
        assert "vacía" in result.error.message.lower()
    
    @patch('images_app.services.image.management_service.get_model_safely')
    def test_get_image_statistics_success(self, mock_get_model, management_service, mock_user):
        """Test getting image statistics."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.prefetch_related.return_value = mock_queryset
        mock_queryset.count.return_value = 10
        
        # Configure aggregate to return different values
        call_count = [0]
        def aggregate_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'total': 10240}
            elif call_count[0] == 2:
                return {'avg': 1024}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.values.return_value.annotate.return_value.values_list.return_value = [('image/jpeg', 8), ('image/png', 2)]
        mock_model = Mock()
        mock_model.objects.filter.return_value = mock_queryset
        mock_get_model.return_value = mock_model
        
        result = management_service.get_image_statistics(mock_user)
        
        assert result.success is True
        assert 'total_images' in result.data
        assert 'processed_images' in result.data
        assert 'file_types' in result.data

