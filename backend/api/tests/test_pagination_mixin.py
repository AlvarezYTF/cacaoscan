"""
Tests for pagination mixin.
"""
import pytest
from unittest.mock import Mock, MagicMock
from django.test import RequestFactory
from rest_framework.views import APIView
from rest_framework.serializers import Serializer

from api.views.mixins.pagination_mixin import PaginationMixin


class TestView(PaginationMixin, APIView):
    """Test view with pagination mixin."""
    default_page_size = 10
    max_page_size = 50


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


@pytest.fixture
def view():
    """Create test view instance."""
    return TestView()


def test_get_pagination_params_default(view, request_factory):
    """Test getting pagination params with defaults."""
    request = request_factory.get('/api/test/')
    page, page_size = view.get_pagination_params(request)
    
    assert page == 1
    assert page_size == 10  # Uses view's default_page_size


def test_get_pagination_params_custom(view, request_factory):
    """Test getting pagination params with custom values."""
    request = request_factory.get('/api/test/', {'page': '2', 'page_size': '25'})
    page, page_size = view.get_pagination_params(request)
    
    assert page == 2
    assert page_size == 25


def test_paginate_queryset_with_serializer_class(view, request_factory, db):
    """Test paginating queryset with serializer class."""
    from django.contrib.auth.models import User
    
    User.objects.create_user(username='user1', email='user1@test.com')
    User.objects.create_user(username='user2', email='user2@test.com')
    
    class UserSerializer(Serializer):
        class Meta:
            fields = ['id', 'username']
        
        def to_representation(self, instance):
            return {'id': instance.id, 'username': instance.username}
    
    request = request_factory.get('/api/test/', {'page': '1', 'page_size': '1'})
    queryset = User.objects.all()
    
    response = view.paginate_queryset(request, queryset, serializer_class=UserSerializer)
    
    assert response.status_code == 200
    assert 'results' in response.data
    assert 'count' in response.data


def test_paginate_queryset_with_serializer_func(view, request_factory, db):
    """Test paginating queryset with serializer function."""
    from django.contrib.auth.models import User
    
    User.objects.create_user(username='user1', email='user1@test.com')
    
    def serialize_func(items):
        return [{'id': item.id, 'username': item.username} for item in items]
    
    request = request_factory.get('/api/test/')
    queryset = User.objects.all()
    
    response = view.paginate_queryset(
        request, queryset, serializer_func=serialize_func
    )
    
    assert response.status_code == 200
    assert 'results' in response.data


def test_paginate_queryset_without_serializer(view, request_factory, db):
    """Test paginating queryset without serializer raises error."""
    from django.contrib.auth.models import User
    
    request = request_factory.get('/api/test/')
    queryset = User.objects.all()
    
    response = view.paginate_queryset(request, queryset)
    
    assert response.status_code == 400
    assert 'error' in response.data


def test_paginate_queryset_with_extra_data(view, request_factory, db):
    """Test paginating queryset with extra data."""
    from django.contrib.auth.models import User
    
    class UserSerializer(Serializer):
        def to_representation(self, instance):
            return {'id': instance.id}
    
    request = request_factory.get('/api/test/')
    queryset = User.objects.all()
    
    extra_data = {'custom': 'value'}
    response = view.paginate_queryset(
        request, queryset, serializer_class=UserSerializer, extra_data=extra_data
    )
    
    assert response.data['custom'] == 'value'


def test_paginate_queryset_with_serializer_context(view, request_factory, db):
    """Test paginating queryset with serializer context."""
    from django.contrib.auth.models import User
    
    class UserSerializer(Serializer):
        def to_representation(self, instance):
            context = self.context
            return {'id': instance.id, 'context_present': 'request' in context}
    
    request = request_factory.get('/api/test/')
    queryset = User.objects.all()
    
    context = {'custom': 'context'}
    response = view.paginate_queryset(
        request, queryset, serializer_class=UserSerializer, serializer_context=context
    )
    
    assert response.status_code == 200


