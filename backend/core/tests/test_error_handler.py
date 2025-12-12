"""
Tests for error handler middleware.
"""
import pytest
from django.test import RequestFactory
from django.http import JsonResponse
from core.middleware.error_handler import StandardErrorMiddleware


@pytest.fixture
def middleware():
    """Create middleware instance."""
    def get_response(request):
        return JsonResponse({'test': 'ok'})
    return StandardErrorMiddleware(get_response)


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


def test_middleware_init(middleware):
    """Test middleware initialization."""
    assert middleware is not None
    assert middleware.get_response is not None


def test_middleware_call_api_path(middleware, request_factory):
    """Test middleware call with API path."""
    request = request_factory.get('/api/test/')
    response = middleware(request)
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'


def test_middleware_call_non_api_path(middleware, request_factory):
    """Test middleware call with non-API path."""
    request = request_factory.get('/admin/')
    response = middleware(request)
    assert response.status_code == 200


def test_process_exception_api_path(middleware, request_factory):
    """Test process_exception with API path."""
    request = request_factory.get('/api/test/')
    exception = Exception("Test exception")
    response = middleware.process_exception(request, exception)
    assert response is not None
    assert isinstance(response, JsonResponse)
    assert response.status_code == 500
    import json
    data = json.loads(response.content)
    assert data['success'] is False
    assert 'message' in data
    assert 'error_type' in data


def test_process_exception_non_api_path(middleware, request_factory):
    """Test process_exception with non-API path."""
    request = request_factory.get('/admin/')
    exception = Exception("Test exception")
    response = middleware.process_exception(request, exception)
    assert response is None


