"""
Unit tests for API realtime_middleware module.
Tests RealtimeAuditMiddleware functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone

from api.realtime_middleware import RealtimeAuditMiddleware


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
    request.method = 'POST'
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
    """Create a RealtimeAuditMiddleware instance for testing."""
    get_response = Mock(return_value=Mock(status_code=200))
    return RealtimeAuditMiddleware(get_response)


class TestRealtimeAuditMiddleware:
    """Tests for RealtimeAuditMiddleware class."""
    
    def test_middleware_initialization(self):
        """Test middleware initialization."""
        get_response = Mock()
        middleware = RealtimeAuditMiddleware(get_response)
        
        assert middleware.get_response == get_response
    
    def test_middleware_processes_request(self, middleware, mock_request, mock_response):
        """Test that middleware processes request."""
        middleware.get_response.return_value = mock_response
        
        response = middleware(mock_request)
        
        assert hasattr(mock_request, '_audit_start_time')
        assert hasattr(mock_request, '_audit_user')
        assert hasattr(mock_request, '_audit_ip')
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
    
    def test_get_action_type_get(self, middleware):
        """Test determining action type for GET."""
        action = middleware.get_action_type('GET')
        
        assert action == 'view'
    
    def test_get_action_type_post(self, middleware):
        """Test determining action type for POST."""
        action = middleware.get_action_type('POST')
        
        assert action == 'create'
    
    def test_get_action_type_put(self, middleware):
        """Test determining action type for PUT."""
        action = middleware.get_action_type('PUT')
        
        assert action == 'update'
    
    def test_get_action_type_patch(self, middleware):
        """Test determining action type for PATCH."""
        action = middleware.get_action_type('PATCH')
        
        assert action == 'update'
    
    def test_get_action_type_delete(self, middleware):
        """Test determining action type for DELETE."""
        action = middleware.get_action_type('DELETE')
        
        assert action == 'delete'
    
    def test_get_model_name_from_path(self, middleware):
        """Test extracting model name from path."""
        request = Mock()
        request.path = '/api/images/1/'
        
        model_name = middleware.get_model_name(request.path)
        
        assert model_name is not None
    
    def test_get_model_name_default(self, middleware):
        """Test default model name for unknown paths."""
        model_name = middleware.get_model_name('/unknown/path/')
        
        assert model_name == 'Unknown'
    
    @patch('api.realtime_middleware.realtime_service')
    def test_sends_activity_log_for_authenticated_user(self, mock_realtime_service, middleware, mock_request, mock_response):
        """Test that activity log is sent for authenticated users."""
        mock_request.user.is_authenticated = True
        mock_response.status_code = 200
        middleware.get_response.return_value = mock_response
        
        middleware(mock_request)
        
        mock_realtime_service.send_activity_log.assert_called_once()
    
    def test_no_activity_log_for_unauthenticated_user(self, middleware):
        """Test that activity log is not sent for unauthenticated users."""
        request = Mock()
        request.method = 'GET'
        request.path = '/api/images/'
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = Mock()
        response.status_code = 200
        middleware.get_response.return_value = response
        
        with patch('api.realtime_middleware.realtime_service') as mock_realtime_service:
            middleware(request)
            
            mock_realtime_service.send_activity_log.assert_not_called()
    
    def test_calculate_response_time(self, middleware, mock_request):
        """Test calculating response time."""
        mock_request._audit_start_time = timezone.now()
        
        response_time = middleware.calculate_response_time(mock_request)
        
        assert isinstance(response_time, (int, float))
        assert response_time >= 0

