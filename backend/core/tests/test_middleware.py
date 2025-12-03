"""
Tests for Core Middleware.
"""
import pytest
from unittest.mock import Mock, patch
from django.http import JsonResponse, HttpRequest
from django.test import RequestFactory

from core.middleware.error_handler import StandardErrorMiddleware


@pytest.fixture
def get_response():
    """Create a mock get_response function."""
    def _get_response(request):
        return JsonResponse({'success': True})
    return _get_response


@pytest.fixture
def middleware(get_response):
    """Create middleware instance."""
    return StandardErrorMiddleware(get_response)


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


@pytest.mark.django_db
class TestStandardErrorMiddleware:
    """Tests for StandardErrorMiddleware."""

    def test_init(self, get_response):
        """Test middleware initialization."""
        middleware = StandardErrorMiddleware(get_response)
        
        assert middleware.get_response == get_response

    def test_call_normal_request(self, middleware, request_factory):
        """Test processing normal request."""
        request = request_factory.get('/api/test/')
        
        response = middleware(request)
        
        assert response.status_code == 200

    def test_process_exception_api_path(self, middleware, request_factory):
        """Test processing exception for API path."""
        request = request_factory.get('/api/test/')
        exception = Exception("Test error")
        
        response = middleware.process_exception(request, exception)
        
        assert response is not None
        assert isinstance(response, JsonResponse)
        assert response.status_code == 500
        data = response.json()
        assert data['success'] is False
        assert 'error_type' in data

    def test_process_exception_non_api_path(self, middleware, request_factory):
        """Test processing exception for non-API path."""
        request = request_factory.get('/admin/')
        exception = Exception("Test error")
        
        response = middleware.process_exception(request, exception)
        
        # Should return None for non-API paths
        assert response is None

    def test_process_exception_error_message(self, middleware, request_factory):
        """Test that error message is standardized."""
        request = request_factory.get('/api/test/')
        exception = Exception("Test error")
        
        response = middleware.process_exception(request, exception)
        data = response.json()
        
        assert data['message'] == 'Error interno del servidor'
        assert data['error_type'] == 'internal_server_error'

    def test_call_with_exception(self, get_response, request_factory):
        """Test __call__ when get_response raises exception."""
        def failing_get_response(request):
            raise Exception("Test error")
        
        middleware = StandardErrorMiddleware(failing_get_response)
        request = request_factory.get('/api/test/')
        
        # Django middleware should handle this
        # In real Django, the exception would be caught by process_exception
        with pytest.raises(Exception):
            middleware(request)

