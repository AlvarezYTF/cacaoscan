"""
Tests for error handler middleware.
"""
import pytest
from unittest.mock import Mock, MagicMock
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.test import RequestFactory
from core.middleware.error_handler import StandardErrorMiddleware


class TestStandardErrorMiddleware:
    """Test cases for StandardErrorMiddleware."""
    
    def test_middleware_initialization(self):
        """Test middleware initialization."""
        get_response = Mock()
        middleware = StandardErrorMiddleware(get_response)
        assert middleware.get_response == get_response
    
    def test_middleware_call_normal_request(self):
        """Test middleware call with normal request."""
        request = RequestFactory().get('/api/test/')
        response = HttpResponse(status=200)
        get_response = Mock(return_value=response)
        
        middleware = StandardErrorMiddleware(get_response)
        result = middleware(request)
        
        assert result == response
        get_response.assert_called_once_with(request)
    
    def test_process_exception_with_api_path(self):
        """Test process_exception for API paths."""
        request = RequestFactory().get('/api/test/')
        exception = Exception('Test error')
        get_response = Mock()
        
        middleware = StandardErrorMiddleware(get_response)
        result = middleware.process_exception(request, exception)
        
        assert isinstance(result, JsonResponse)
        assert result.status_code == 500
        import json
        data = json.loads(result.content)
        assert data['success'] is False
        assert data['message'] == 'Error interno del servidor'
        assert data['error_type'] == 'internal_server_error'
    
    def test_process_exception_with_non_api_path(self):
        """Test process_exception for non-API paths."""
        request = RequestFactory().get('/admin/login/')
        exception = Exception('Test error')
        get_response = Mock()
        
        middleware = StandardErrorMiddleware(get_response)
        result = middleware.process_exception(request, exception)
        
        assert result is None
    
    def test_process_exception_with_api_prefix_variations(self):
        """Test process_exception with different API path variations."""
        get_response = Mock()
        middleware = StandardErrorMiddleware(get_response)
        
        test_paths = [
            '/api/',
            '/api/test',
            '/api/v1/users',
            '/api/v2/images/upload'
        ]
        
        for path in test_paths:
            request = RequestFactory().get(path)
            exception = Exception('Test error')
            result = middleware.process_exception(request, exception)
            assert isinstance(result, JsonResponse)
            assert result.status_code == 500
    
    def test_process_exception_with_non_api_prefix_variations(self):
        """Test process_exception with non-API paths."""
        get_response = Mock()
        middleware = StandardErrorMiddleware(get_response)
        
        test_paths = [
            '/admin/',
            '/static/css/style.css',
            '/media/images/test.jpg',
            '/login',
            '/register'
        ]
        
        for path in test_paths:
            request = RequestFactory().get(path)
            exception = Exception('Test error')
            result = middleware.process_exception(request, exception)
            assert result is None
    
    def test_middleware_preserves_response(self):
        """Test that middleware preserves response from get_response."""
        request = RequestFactory().get('/api/test/')
        custom_response = JsonResponse({'data': 'test'}, status=201)
        get_response = Mock(return_value=custom_response)
        
        middleware = StandardErrorMiddleware(get_response)
        result = middleware(request)
        
        assert result == custom_response
        assert result.status_code == 201

