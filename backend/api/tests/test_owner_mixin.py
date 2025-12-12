"""
Tests for owner permission mixin.
"""
import pytest
from unittest.mock import Mock
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied

from api.views.mixins.owner_mixin import OwnerPermissionMixin


class TestView(OwnerPermissionMixin):
    """Test view with owner mixin."""
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
def resource(user):
    """Create test resource owned by user."""
    resource = Mock()
    resource.user = user
    resource.id = 1
    return resource


def test_get_owner_field_default(view):
    """Test getting default owner field."""
    assert view.get_owner_field() == 'user'


def test_is_owner_same_user(view, user, resource):
    """Test is_owner returns True for resource owner."""
    assert view.is_owner(user, resource) is True


def test_is_owner_different_user(view, user, db):
    """Test is_owner returns False for different user."""
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='pass123'
    )
    resource = Mock()
    resource.user = user
    
    assert view.is_owner(other_user, resource) is False


def test_is_owner_admin(view, admin_user, resource):
    """Test is_owner returns True for admin."""
    assert view.is_owner(admin_user, resource) is True


def test_is_owner_staff(view, user, resource, db):
    """Test is_owner returns True for staff."""
    user.is_staff = True
    user.save()
    
    assert view.is_owner(user, resource) is True


def test_is_owner_unauthenticated(view, resource):
    """Test is_owner returns False for unauthenticated user."""
    anonymous_user = Mock()
    anonymous_user.is_authenticated = False
    
    assert view.is_owner(anonymous_user, resource) is False


def test_is_owner_no_owner_field(view, user):
    """Test is_owner returns False when resource has no owner field."""
    resource = Mock()
    del resource.user
    
    assert view.is_owner(user, resource) is False


def test_is_owner_user_id_instead_of_user(view, user):
    """Test is_owner works with user ID instead of User object."""
    resource = Mock()
    resource.user = user.id
    
    assert view.is_owner(user, resource) is True


def test_check_owner_permission_allowed(view, user, resource):
    """Test check_owner_permission doesn't raise for owner."""
    # Should not raise
    view.check_owner_permission(user, resource)


def test_check_owner_permission_denied(view, user, db):
    """Test check_owner_permission raises for non-owner."""
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='pass123'
    )
    resource = Mock()
    resource.user = user
    
    with pytest.raises(PermissionDenied):
        view.check_owner_permission(other_user, resource)


def test_owner_permission_denied_default_message(view):
    """Test owner_permission_denied returns response with default message."""
    response = view.owner_permission_denied()
    
    assert response.status_code == 403
    assert 'error' in response.data
    assert 'No tienes permisos' in response.data['error']


def test_owner_permission_denied_custom_message(view):
    """Test owner_permission_denied returns response with custom message."""
    custom_message = "Custom error message"
    response = view.owner_permission_denied(message=custom_message)
    
    assert response.status_code == 403
    assert response.data['error'] == custom_message


def test_get_owner_queryset_owner(view, user, db):
    """Test get_owner_queryset filters for owner."""
    from django.contrib.auth.models import User
    
    # Create resources owned by different users
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='pass123'
    )
    
    # Mock queryset
    queryset = Mock()
    queryset.filter = Mock(return_value=Mock())
    queryset.none = Mock(return_value=Mock())
    
    result = view.get_owner_queryset(user, queryset)
    
    # Should call filter with user
    queryset.filter.assert_called_once_with(user=user)


def test_get_owner_queryset_admin(view, admin_user, db):
    """Test get_owner_queryset returns all for admin."""
    queryset = Mock()
    
    result = view.get_owner_queryset(admin_user, queryset)
    
    # Should return queryset as-is for admin
    assert result == queryset


def test_get_owner_queryset_unauthenticated(view, db):
    """Test get_owner_queryset returns none for unauthenticated user."""
    anonymous_user = Mock()
    anonymous_user.is_authenticated = False
    
    queryset = Mock()
    queryset.none = Mock(return_value=Mock())
    
    result = view.get_owner_queryset(anonymous_user, queryset)
    
    queryset.none.assert_called_once()


