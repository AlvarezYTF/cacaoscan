"""
Tests for pagination utilities.
"""
import pytest
from unittest.mock import Mock, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework.response import Response

from api.utils.pagination import (
    get_pagination_params,
    paginate_queryset,
    build_pagination_urls,
    create_paginated_response
)


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


def test_get_pagination_params_default(request_factory):
    """Test getting pagination params with defaults."""
    request = request_factory.get('/api/test/')
    page, page_size = get_pagination_params(request)
    
    assert page == 1
    assert page_size == 20


def test_get_pagination_params_custom(request_factory):
    """Test getting pagination params with custom values."""
    request = request_factory.get('/api/test/', {'page': '2', 'page_size': '50'})
    page, page_size = get_pagination_params(request)
    
    assert page == 2
    assert page_size == 50


def test_get_pagination_params_invalid_page(request_factory):
    """Test getting pagination params with invalid page."""
    request = request_factory.get('/api/test/', {'page': '0'})
    page, page_size = get_pagination_params(request)
    
    assert page == 1  # Should default to 1


def test_get_pagination_params_exceeds_max(request_factory):
    """Test getting pagination params that exceed max page size."""
    request = request_factory.get('/api/test/', {'page_size': '200'})
    page, page_size = get_pagination_params(request, max_page_size=100)
    
    assert page_size == 100  # Should be limited to max


def test_get_pagination_params_invalid_values(request_factory):
    """Test getting pagination params with invalid values."""
    request = request_factory.get('/api/test/', {'page': 'invalid', 'page_size': 'invalid'})
    page, page_size = get_pagination_params(request, default_page_size=20)
    
    # Should return defaults on error: page=1, page_size=default_page_size
    assert page == 1
    assert page_size == 20


def test_paginate_queryset_real_queryset(request_factory, db):
    """Test paginating a real queryset."""
    # Create some test users with unique usernames
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user1 = User.objects.create_user(username=f'user1_{unique_id}', email=f'user1_{unique_id}@test.com')
    user2 = User.objects.create_user(username=f'user2_{unique_id}', email=f'user2_{unique_id}@test.com')
    user3 = User.objects.create_user(username=f'user3_{unique_id}', email=f'user3_{unique_id}@test.com')
    
    # Filter to only our test users using exact usernames to avoid conflicts
    from django.db.models import Q
    queryset = User.objects.filter(
        Q(username=f'user1_{unique_id}') | 
        Q(username=f'user2_{unique_id}') | 
        Q(username=f'user3_{unique_id}')
    )
    page_obj, paginator = paginate_queryset(queryset, page=1, page_size=2)
    
    assert paginator.count == 3
    assert paginator.num_pages == 2
    assert len(page_obj.object_list) == 2


def test_paginate_queryset_mock_queryset():
    """Test paginating a mocked queryset."""
    mock_queryset = Mock()
    mock_queryset.count.return_value = 0
    mock_queryset.__len__ = Mock(return_value=0)
    
    page_obj, paginator = paginate_queryset(mock_queryset, page=1, page_size=10)
    
    assert paginator.count == 0
    assert paginator.num_pages == 1


def test_paginate_queryset_invalid_page(request_factory, db):
    """Test paginating with invalid page number."""
    User.objects.create_user(username='user1', email='user1@test.com')
    queryset = User.objects.all()
    
    with pytest.raises(ValueError, match="no existe"):
        paginate_queryset(queryset, page=999, page_size=10)


def test_build_pagination_urls_with_next(request_factory):
    """Test building pagination URLs with next page."""
    request = request_factory.get('/api/test/', {'page': '1', 'page_size': '20'})
    urls = build_pagination_urls(request, page=1, page_size=20, has_next=True, has_previous=False)
    
    assert urls['next'] is not None
    assert 'page=2' in urls['next']
    assert urls['previous'] is None


def test_build_pagination_urls_with_previous(request_factory):
    """Test building pagination URLs with previous page."""
    request = request_factory.get('/api/test/', {'page': '2', 'page_size': '20'})
    urls = build_pagination_urls(request, page=2, page_size=20, has_next=False, has_previous=True)
    
    assert urls['previous'] is not None
    assert 'page=1' in urls['previous']
    assert urls['next'] is None


def test_build_pagination_urls_both(request_factory):
    """Test building pagination URLs with both next and previous."""
    request = request_factory.get('/api/test/', {'page': '2', 'page_size': '20'})
    urls = build_pagination_urls(request, page=2, page_size=20, has_next=True, has_previous=True)
    
    assert urls['next'] is not None
    assert urls['previous'] is not None


def test_build_pagination_urls_none(request_factory):
    """Test building pagination URLs with no next or previous."""
    request = request_factory.get('/api/test/')
    urls = build_pagination_urls(request, page=1, page_size=20, has_next=False, has_previous=False)
    
    assert urls['next'] is None
    assert urls['previous'] is None


def test_create_paginated_response_success(request_factory, db):
    """Test creating a paginated response successfully."""
    from rest_framework.serializers import Serializer
    
    # Create test users
    User.objects.create_user(username='user1', email='user1@test.com')
    User.objects.create_user(username='user2', email='user2@test.com')
    
    class UserSerializer(Serializer):
        class Meta:
            fields = ['id', 'username']
        
        def to_representation(self, instance):
            return {'id': instance.id, 'username': instance.username}
    
    request = request_factory.get('/api/test/', {'page': '1', 'page_size': '1'})
    queryset = User.objects.all()
    
    response = create_paginated_response(
        request, queryset, UserSerializer, default_page_size=10
    )
    
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert 'results' in response.data
    assert 'count' in response.data
    assert 'page' in response.data


def test_create_paginated_response_with_extra_data(request_factory, db):
    """Test creating a paginated response with extra data."""
    from rest_framework.serializers import Serializer
    
    class UserSerializer(Serializer):
        def to_representation(self, instance):
            return {'id': instance.id}
    
    request = request_factory.get('/api/test/')
    queryset = User.objects.all()
    
    extra_data = {'custom_field': 'custom_value'}
    response = create_paginated_response(
        request, queryset, UserSerializer, extra_data=extra_data
    )
    
    assert response.data['custom_field'] == 'custom_value'


