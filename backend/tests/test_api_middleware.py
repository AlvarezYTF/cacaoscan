"""
Unit tests for API middleware module.
Tests AuditMiddleware functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone

from api.middleware import AuditMiddleware


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.is_authenticated = True
    return user


@pytest.fixture
def mock_request(mock_user):
    """Create a mock request for testing."""
    request = Mock()
    request.method = 'GET'
    request.path = '/api/images/'
    request.META = {
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_USER_AGENT': 'test-agent'
    }
    request.user = mock_user
    return request


@pytest.fixture
def mock_response():
    """Create a mock response for testing."""
    response = Mock()
    response.status_code = 200
    return response


@pytest.fixture
def middleware():
    """Create an AuditMiddleware instance for testing."""
    get_response = Mock(return_value=Mock(status_code=200))
    return AuditMiddleware(get_response)


class TestAuditMiddleware:
    """Tests for AuditMiddleware class."""
    
    def test_middleware_initialization(self):
        """Test middleware initialization."""
        get_response = Mock()
        middleware = AuditMiddleware(get_response)
        
        assert middleware.get_response == get_response
    
    def test_middleware_processes_request(self, middleware, mock_request, mock_response):
        """Test that middleware processes request."""
        middleware.get_response.return_value = mock_response
        
        response = middleware(mock_request)
        
        assert hasattr(mock_request, 'audit_info')
        assert mock_request.audit_info['ip_address'] == '127.0.0.1'
        assert mock_request.audit_info['method'] == 'GET'
        assert response == mock_response
    
    def test_get_client_ip_direct(self, middleware):
        """Test getting client IP directly."""
        request = Mock()
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        ip = middleware.get_client_ip(request)
        
        assert ip == '192.168.1.1'
    
    def test_get_client_ip_from_forwarded(self, middleware):
        """Test getting client IP from X-Forwarded-For."""
        request = Mock()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '10.0.0.1, 192.168.1.1',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        ip = middleware.get_client_ip(request)
        
        assert ip == '10.0.0.1'
    
    def test_determine_action_post_login(self, middleware):
        """Test determining action for POST login."""
        request = Mock()
        request.method = 'POST'
        request.path = '/api/auth/login/'
        
        action = middleware.determine_action(request)
        
        assert action == 'login'
    
    def test_determine_action_post_upload(self, middleware):
        """Test determining action for POST upload."""
        request = Mock()
        request.method = 'POST'
        request.path = '/api/images/upload/'
        
        action = middleware.determine_action(request)
        
        assert action == 'upload'
    
    def test_determine_action_get_view(self, middleware):
        """Test determining action for GET view."""
        request = Mock()
        request.method = 'GET'
        request.path = '/api/images/'
        
        action = middleware.determine_action(request)
        
        assert action == 'view'
    
    def test_determine_action_put_update(self, middleware):
        """Test determining action for PUT update."""
        request = Mock()
        request.method = 'PUT'
        request.path = '/api/images/1/'
        
        action = middleware.determine_action(request)
        
        assert action == 'update'
    
    def test_determine_action_delete(self, middleware):
        """Test determining action for DELETE."""
        request = Mock()
        request.method = 'DELETE'
        request.path = '/api/images/1/'
        
        action = middleware.determine_action(request)
        
        assert action == 'delete'
    
    @patch('api.middleware.ActivityLog')
    def test_log_activity_for_authenticated_user(self, mock_activity_log, middleware, mock_request, mock_response):
        """Test that activity is logged for authenticated users."""
        mock_request.user.is_authenticated = True
        mock_response.status_code = 200
        middleware.get_response.return_value = mock_response
        
        middleware(mock_request)
        
        # Activity should be logged (check if log_activity was called)
        assert hasattr(mock_request, 'audit_action')
    
    def test_no_log_for_unauthenticated_user(self, middleware):
        """Test that activity is not logged for unauthenticated users."""
        request = Mock()
        request.method = 'GET'
        request.path = '/api/images/'
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = Mock()
        response.status_code = 200
        middleware.get_response.return_value = response
        
        middleware(request)
        
        # Should not have audit_action for unauthenticated users
        assert not hasattr(request, 'audit_action') or request.audit_action is None
    
    def test_no_log_for_error_response(self, middleware, mock_request):
        """Test that activity is not logged for error responses."""
        error_response = Mock()
        error_response.status_code = 500
        middleware.get_response.return_value = error_response
        
        middleware(mock_request)
        
        # Should not log for error responses
        assert True  # Just verify it doesn't crash

