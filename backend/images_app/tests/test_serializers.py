"""
Tests for Images App Serializers.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from images_app.serializers import CacaoImageSerializer
from images_app.models import CacaoImage


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def image_file():
    """Create a test image file."""
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
def cacao_image(user, image_file):
    """Create a test CacaoImage."""
    return CacaoImage.objects.create(
        user=user,
        image=image_file,
        file_name='test_image.jpg',
        file_size=1024,
        file_type='image/jpeg'
    )


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.mark.django_db
class TestCacaoImageSerializer:
    """Tests for CacaoImageSerializer."""

    def test_serialize_cacao_image(self, cacao_image):
        """Test serializing CacaoImage."""
        serializer = CacaoImageSerializer(cacao_image)
        data = serializer.data
        
        assert data['id'] == cacao_image.id
        assert data['file_name'] == cacao_image.file_name
        assert 'image_url' in data

    def test_get_image_url_with_image(self, cacao_image, request_factory):
        """Test getting image URL when image exists."""
        request = request_factory.get('/')
        serializer = CacaoImageSerializer(cacao_image, context={'request': request})
        data = serializer.data
        
        assert 'image_url' in data
        assert data['image_url'] is not None

    def test_get_image_url_without_image(self, user):
        """Test getting image URL when no image."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            file_name='test.jpg'
        )
        
        serializer = CacaoImageSerializer(cacao_image)
        data = serializer.data
        
        assert data.get('image_url') is None

    def test_read_only_fields(self, cacao_image):
        """Test that read-only fields are properly set."""
        serializer = CacaoImageSerializer(cacao_image)
        data = serializer.data
        
        # These should be in data but not writable
        assert 'id' in data
        assert 'uploaded_at' in data
        assert 'created_at' in data

    def test_create_cacao_image(self, user, image_file):
        """Test creating CacaoImage through serializer."""
        data = {
            'user': user.id,
            'image': image_file,
            'file_name': 'test.jpg',
            'file_size': 1024,
            'file_type': 'image/jpeg'
        }
        serializer = CacaoImageSerializer(data=data)
        assert serializer.is_valid()
        
        cacao_image = serializer.save(user=user)
        assert cacao_image.user == user
        assert cacao_image.file_name == 'test.jpg'

