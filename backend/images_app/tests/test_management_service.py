"""
Tests for image management service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
import io
from images_app.services.image import ImageManagementService
from api.services.base import ServiceResult


@pytest.mark.django_db
class TestImageManagementService:
    """Tests for ImageManagementService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ImageManagementService()
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
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
    
    @patch('django.core.files.storage.default_storage')
    def test_upload_image_success(self, mock_storage, service, user, valid_image_file):
        """Test uploading image successfully."""
        from images_app.models import CacaoImage
        from django.utils import timezone
        
        image_data = {'file': valid_image_file, 'filename': 'test_image.jpg'}
        
        mock_storage.save.return_value = 'cacao_images/test_image.jpg'
        service._default_storage = mock_storage
        
        # Mock _validate_image_file to return success
        with patch.object(service, '_validate_image_file', return_value=ServiceResult.success()):
            # Create a mock image object
            mock_image = Mock()
            mock_image.id = 1
            mock_image.user = user
            mock_image.file_name = 'test_image.jpg'
            mock_image.file_size = 1000
            mock_image.file_type = 'image/jpeg'
            mock_image.processed = False
            mock_image.image = Mock()
            mock_image.image.url = 'http://example.com/test_image.jpg'
            mock_image.created_at = timezone.now()
            mock_image.notas = ''
            mock_image.save = Mock()
            
            # Patch CacaoImage in service to return our mock when instantiated
            with patch('images_app.services.image.management_service.CacaoImage', return_value=mock_image):
                # Also patch create_audit_log to avoid database operations
                with patch.object(service, 'create_audit_log'):
                    result = service.upload_image(image_data, user)
                    
                    assert result.success
                    assert 'id' in result.data
                    assert result.data['id'] == 1
    
    def test_upload_image_no_file(self, service, user):
        """Test uploading image without file."""
        image_data = {}
        
        result = service.upload_image(image_data, user)
        
        assert not result.success
    
    def test_get_user_images(self, service, user):
        """Test getting user images."""
        result = service.get_user_images(user, page=1, page_size=20)
        
        assert result.success
        assert 'images' in result.data
    
    def test_get_user_images_with_filters(self, service, user):
        """Test getting user images with filters."""
        filters = {'processed': True, 'search': 'test'}
        
        result = service.get_user_images(user, page=1, page_size=20, filters=filters)
        
        assert result.success
    
    def test_get_image_details(self, service, user):
        """Test getting image details."""
        from images_app.models import CacaoImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create image with required image field - use real model
        image_file = SimpleUploadedFile('test.jpg', b'fake image content', content_type='image/jpeg')
        image = CacaoImage.objects.create(
            file_name='test.jpg',
            file_size=1000,
            file_type='image/jpeg',
            user=user,
            image=image_file
        )
        
        result = service.get_image_details(image.id, user)
        
        assert result.success
        assert result.data['id'] == image.id
    
    def test_get_image_details_not_found(self, service, user):
        """Test getting image details when not found."""
        result = service.get_image_details(999, user)
        
        assert not result.success
    
    def test_delete_image_success(self, service, user):
        """Test deleting image successfully."""
        from images_app.models import CacaoImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create and delete image - use real model
        image_file = SimpleUploadedFile('test.jpg', b'fake image content', content_type='image/jpeg')
        image = CacaoImage.objects.create(
            file_name='test.jpg',
            file_size=1000,
            file_type='image/jpeg',
            user=user,
            image=image_file
        )
        
        result = service.delete_image(image.id, user)
        
        assert result.success
        assert not CacaoImage.objects.filter(id=image.id).exists()
    
    def test_get_image_statistics(self, service, user):
        """Test getting image statistics."""
        # Create some test images
        from images_app.models import CacaoImage
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create some test images - use real model
        image_file1 = SimpleUploadedFile('test1.jpg', b'fake image content', content_type='image/jpeg')
        image_file2 = SimpleUploadedFile('test2.jpg', b'fake image content', content_type='image/jpeg')
        
        CacaoImage.objects.create(
            user=user,
            file_name='test1.jpg',
            file_size=1000,
            file_type='image/jpeg',
            processed=True,
            image=image_file1
        )
        CacaoImage.objects.create(
            user=user,
            file_name='test2.jpg',
            file_size=2000,
            file_type='image/jpeg',
            processed=False,
            image=image_file2
        )
        
        result = service.get_image_statistics(user)
        
        assert result.success
        assert 'total_images' in result.data
        assert 'processed_images' in result.data

