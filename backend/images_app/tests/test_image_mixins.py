"""
Tests for image permission mixins.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User, Group

from images_app.views.image.mixins import ImagePermissionMixin


class TestView(ImagePermissionMixin):
    """Test view with image permission mixin."""
    pass


@pytest.fixture
def view():
    """Create test view instance."""
    return TestView()


@pytest.fixture
def user(db):
    """Create regular user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create admin user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_superuser(
        username=f'admin_{unique_id}',
        email=f'admin_{unique_id}@example.com',
        password='adminpass123'
    )


@pytest.fixture
def analyst_user(db):
    """Create analyst user."""
    user = User.objects.create_user(
        username='analyst',
        email='analyst@example.com',
        password='pass123'
    )
    group, _ = Group.objects.get_or_create(name='analyst')
    user.groups.add(group)
    return user


@pytest.fixture
def image(user):
    """Create test image owned by user."""
    image = Mock()
    image.user = user
    image.id = 1
    return image


def test_can_access_image_owner(view, user, image):
    """Test can_access_image returns True for image owner."""
    assert view.can_access_image(user, image) is True


def test_can_access_image_admin(view, admin_user, image):
    """Test can_access_image returns True for admin."""
    assert view.can_access_image(admin_user, image) is True


def test_can_access_image_analyst(view, analyst_user, image):
    """Test can_access_image returns True for analyst."""
    assert view.can_access_image(analyst_user, image) is True


def test_can_access_image_other_user(view, user, db):
    """Test can_access_image returns False for other user."""
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='pass123'
    )
    image = Mock()
    image.user = user
    
    assert view.can_access_image(other_user, image) is False


@patch('images_app.views.image.mixins.CacaoImage')
def test_get_user_images_queryset_admin(mock_cacao_image, view, admin_user, db):
    """Test get_user_images_queryset returns all images for admin."""
    mock_queryset = Mock()
    mock_prefetch = Mock()
    mock_prefetch.prefetch_related.return_value = mock_queryset
    mock_cacao_image.objects.select_related.return_value = mock_prefetch
    
    result = view.get_user_images_queryset(admin_user)
    
    assert result == mock_queryset


@patch('images_app.views.image.mixins.CacaoImage')
def test_get_user_images_queryset_analyst(mock_cacao_image, view, analyst_user, db):
    """Test get_user_images_queryset returns all images for analyst."""
    mock_queryset = Mock()
    mock_prefetch = Mock()
    mock_prefetch.prefetch_related.return_value = mock_queryset
    mock_cacao_image.objects.select_related.return_value = mock_prefetch
    
    result = view.get_user_images_queryset(analyst_user)
    
    assert result == mock_queryset


@patch('images_app.views.image.mixins.CacaoImage')
def test_get_user_images_queryset_regular_user(mock_cacao_image, view, user, db):
    """Test get_user_images_queryset filters by user for regular user."""
    mock_base_queryset = Mock()
    mock_filtered_queryset = Mock()
    mock_prefetch = Mock()
    mock_prefetch.prefetch_related.return_value = mock_base_queryset
    mock_cacao_image.objects.select_related.return_value = mock_prefetch
    mock_base_queryset.filter.return_value = mock_filtered_queryset
    
    result = view.get_user_images_queryset(user)
    
    mock_base_queryset.filter.assert_called_once_with(user=user)
    assert result == mock_filtered_queryset


