"""
Tests for images_app views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from io import BytesIO

# Import directly from views.py file (not from views/__init__.py)
import importlib.util
from pathlib import Path

# Load views.py directly
views_py_path = Path(__file__).parent.parent / 'views.py'
spec = importlib.util.spec_from_file_location("images_app.views_direct", views_py_path)
views_direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(views_direct)

CacaoImageUploadView = views_direct.CacaoImageUploadView
CacaoImageListView = views_direct.CacaoImageListView
from images_app.models import CacaoImage
from images_app.serializers import CacaoImageSerializer


@pytest.mark.django_db
class TestCacaoImageUploadView:
    """Tests for CacaoImageUploadView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
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
    
    def test_validate_file_size_valid(self, api_client, user):
        """Test validating file size with valid file."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        image_file = SimpleUploadedFile(
            'test.jpg',
            b'x' * (10 * 1024 * 1024),  # 10MB
            content_type='image/jpeg'
        )
        
        error = view._validate_file_size(image_file)
        assert error is None
    
    def test_validate_file_size_too_large(self, api_client, user):
        """Test validating file size with too large file."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        image_file = SimpleUploadedFile(
            'test.jpg',
            b'x' * (25 * 1024 * 1024),  # 25MB
            content_type='image/jpeg'
        )
        
        error = view._validate_file_size(image_file)
        assert error is not None
        assert '20MB' in error
    
    def test_validate_file_type_valid(self, api_client, user):
        """Test validating file type with valid types."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        for content_type in valid_types:
            image_file = SimpleUploadedFile(
                'test.jpg',
                b'fake image content',
                content_type=content_type
            )
            error = view._validate_file_type(image_file)
            assert error is None
    
    def test_validate_file_type_invalid(self, api_client, user):
        """Test validating file type with invalid type."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        image_file = SimpleUploadedFile(
            'test.gif',
            b'fake image content',
            content_type='image/gif'
        )
        
        error = view._validate_file_type(image_file)
        assert error is not None
        assert 'no permitido' in error
    
    def test_assign_finca_with_valid_id(self, api_client, user):
        """Test assigning finca with valid ID."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        from fincas_app.models import Finca
        finca = Finca.objects.create(
            nombre='Test Finca',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=10.0,
            agricultor=user
        )
        
        cacao_image = CacaoImage(user=user)
        view._assign_finca(cacao_image, finca.id)
        
        assert cacao_image.finca == finca
    
    def test_assign_finca_with_invalid_id(self, api_client, user):
        """Test assigning finca with invalid ID."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        cacao_image = CacaoImage(user=user)
        view._assign_finca(cacao_image, 999)
        
        assert cacao_image.finca is None
    
    def test_assign_finca_with_none(self, api_client, user):
        """Test assigning finca with None."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        cacao_image = CacaoImage(user=user)
        view._assign_finca(cacao_image, None)
        
        assert cacao_image.finca is None
    
    def test_process_single_image_success(self, api_client, user):
        """Test processing single image successfully."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        image_file = SimpleUploadedFile(
            'test.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        result, error = view._process_single_image(
            Mock(user=user, data={}),
            image_file,
            0
        )
        
        assert result is not None
        assert error is None
        assert 'id' in result
    
    def test_process_single_image_size_error(self, api_client, user):
        """Test processing single image with size error."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        image_file = SimpleUploadedFile(
            'test.jpg',
            b'x' * (25 * 1024 * 1024),  # 25MB
            content_type='image/jpeg'
        )
        
        result, error = view._process_single_image(
            Mock(user=user, data={}),
            image_file,
            0
        )
        
        assert result is None
        assert error is not None
        assert 'file' in error
        assert 'error' in error
    
    def test_process_single_image_type_error(self, api_client, user):
        """Test processing single image with type error."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        image_file = SimpleUploadedFile(
            'test.gif',
            b'fake image content',
            content_type='image/gif'
        )
        
        result, error = view._process_single_image(
            Mock(user=user, data={}),
            image_file,
            0
        )
        
        assert result is None
        assert error is not None
        assert 'file' in error
        assert 'error' in error
    
    def test_determine_http_status_all_success(self, api_client, user):
        """Test determining HTTP status with all successful."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        status_code = view._determine_http_status(5, 0)
        assert status_code == status.HTTP_201_CREATED
    
    def test_determine_http_status_partial_success(self, api_client, user):
        """Test determining HTTP status with partial success."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        status_code = view._determine_http_status(3, 2)
        assert status_code == status.HTTP_207_MULTI_STATUS
    
    def test_determine_http_status_all_failed(self, api_client, user):
        """Test determining HTTP status with all failed."""
        api_client.force_authenticate(user=user)
        view = CacaoImageUploadView()
        
        status_code = view._determine_http_status(0, 5)
        assert status_code == status.HTTP_400_BAD_REQUEST
    
    def test_post_single_image_success(self, api_client, user):
        """Test POST with single image successfully."""
        api_client.force_authenticate(user=user)
        
        image_file = SimpleUploadedFile(
            'test.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        response = api_client.post('/api/v1/images/upload/', {
            'images': [image_file]
        }, format='multipart')
        
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_207_MULTI_STATUS]
        assert 'uploaded' in response.data
        assert response.data['total_uploaded'] >= 1
    
    def test_post_multiple_images_success(self, api_client, user):
        """Test POST with multiple images successfully."""
        api_client.force_authenticate(user=user)
        
        image_files = [
            SimpleUploadedFile(
                f'test{i}.jpg',
                b'fake image content',
                content_type='image/jpeg'
            )
            for i in range(3)
        ]
        
        response = api_client.post('/api/v1/images/upload/', {
            'images': image_files
        }, format='multipart')
        
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_207_MULTI_STATUS]
        assert 'uploaded' in response.data
        assert response.data['total_uploaded'] >= 1
    
    def test_post_no_images(self, api_client, user):
        """Test POST with no images."""
        api_client.force_authenticate(user=user)
        
        response = api_client.post('/api/v1/images/upload/', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'No se proporcionaron imágenes' in response.data['error']


@pytest.mark.django_db
class TestCacaoImageListView:
    """Tests for CacaoImageListView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
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
    
    def test_get_list_empty(self, api_client, user):
        """Test getting empty list."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/images/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_get_list_with_images(self, api_client, user):
        """Test getting list with images."""
        api_client.force_authenticate(user=user)
        
        # Create test images
        for i in range(3):
            CacaoImage.objects.create(
                user=user,
                file_name=f'test{i}.jpg',
                file_size=1000,
                file_type='image/jpeg',
                processed=False
            )
        
        response = api_client.get('/api/v1/images/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
    
    def test_get_list_ordered_by_created_at(self, api_client, user):
        """Test that list is ordered by created_at descending."""
        api_client.force_authenticate(user=user)
        
        # Create test images
        images = []
        for i in range(3):
            img = CacaoImage.objects.create(
                user=user,
                file_name=f'test{i}.jpg',
                file_size=1000,
                file_type='image/jpeg',
                processed=False
            )
            images.append(img)
        
        response = api_client.get('/api/v1/images/')
        
        assert response.status_code == status.HTTP_200_OK
        # Most recent should be first
        assert response.data['results'][0]['id'] == images[-1].id
    
    def test_get_list_only_user_images(self, api_client, user):
        """Test that list only shows user's images."""
        api_client.force_authenticate(user=user)
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create images for both users
        CacaoImage.objects.create(
            user=user,
            file_name='user1.jpg',
            file_size=1000,
            file_type='image/jpeg',
            processed=False
        )
        CacaoImage.objects.create(
            user=other_user,
            file_name='user2.jpg',
            file_size=1000,
            file_type='image/jpeg',
            processed=False
        )
        
        response = api_client.get('/api/v1/images/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['file_name'] == 'user1.jpg'

