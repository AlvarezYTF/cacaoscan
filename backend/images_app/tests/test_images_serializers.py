"""
Tests for images_app serializers.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from images_app.models import CacaoImage
from images_app.serializers import CacaoImageSerializer


@pytest.mark.django_db
class TestCacaoImageSerializer:
    """Tests for CacaoImageSerializer."""
    
    @pytest.fixture
    def image_file(self):
        """Create test image file."""
        return SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        from django.contrib.auth.models import User
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    def test_serialize_cacao_image(self, image_file, user):
        """Test serializing a cacao image."""
        image = CacaoImage.objects.create(
            user=user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1000,
            file_type='image/jpeg'
        )
        
        serializer = CacaoImageSerializer(image)
        data = serializer.data
        
        assert data['id'] == image.id
        assert data['file_name'] == 'test_image.jpg'
        assert data['file_size'] == 1000
        assert 'image_url' in data
    
    def test_get_image_url_with_request(self, image_file, user):
        """Test getting image URL with request context."""
        image = CacaoImage.objects.create(
            user=user, 
            image=image_file,
            file_name='test_image.jpg',
            file_size=1000,
            file_type='image/jpeg'
        )
        
        request = type('Request', (), {
            'build_absolute_uri': lambda self, url: f'http://testserver{url}'
        })()
        
        serializer = CacaoImageSerializer(image, context={'request': request})
        data = serializer.data
        
        assert data['image_url'] is not None
        assert 'http://testserver' in data['image_url']
    
    def test_get_image_url_without_request(self, image_file, user):
        """Test getting image URL without request context."""
        image = CacaoImage.objects.create(
            user=user, 
            image=image_file,
            file_name='test_image.jpg',
            file_size=1000,
            file_type='image/jpeg'
        )
        
        serializer = CacaoImageSerializer(image)
        data = serializer.data
        
        assert data['image_url'] is not None
    
    def test_get_image_url_no_image(self, user):
        """Test getting image URL when image is None."""
        image = CacaoImage.objects.create(
            user=user,
            file_name='test_image.jpg',
            file_size=0,
            file_type='image/jpeg'
        )
        
        serializer = CacaoImageSerializer(image)
        data = serializer.data
        
        assert data['image_url'] is None

