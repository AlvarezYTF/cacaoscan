"""
Tests for realtime middleware.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from api.realtime_middleware import (
    RealtimeAuditMiddleware,
    RealtimeLoginMiddleware
)


@pytest.fixture
def user(db):
    """Create test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


class TestRealtimeAuditMiddleware:
    """Tests for RealtimeAuditMiddleware."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        get_response = Mock(return_value=Mock(status_code=200))
        return RealtimeAuditMiddleware(get_response)
    
    def test_get_client_ip_direct(self, middleware, request_factory):
        """Test getting client IP directly."""
        request = request_factory.get('/api/images/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = middleware.get_client_ip(request)
        
        assert ip == '192.168.1.1'
    
    def test_get_client_ip_forwarded(self, middleware, request_factory):
        """Test getting client IP from X-Forwarded-For."""
        request = request_factory.get('/api/images/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        
        ip = middleware.get_client_ip(request)
        
        assert ip == '10.0.0.1'
    
    def test_get_action_type_get(self, middleware):
        """Test getting action type for GET."""
        action = middleware.get_action_type('GET')
        assert action == 'view'
    
    def test_get_action_type_post(self, middleware):
        """Test getting action type for POST."""
        action = middleware.get_action_type('POST')
        assert action == 'create'
    
    def test_get_action_type_put(self, middleware):
        """Test getting action type for PUT."""
        action = middleware.get_action_type('PUT')
        assert action == 'update'
    
    def test_get_action_type_delete(self, middleware):
        """Test getting action type for DELETE."""
        action = middleware.get_action_type('DELETE')
        assert action == 'delete'
    
    def test_get_model_name_images(self, middleware):
        """Test getting model name for images endpoint."""
        model = middleware.get_model_name('/api/images/')
        assert model == 'CacaoImage'
    
    def test_get_model_name_fincas(self, middleware):
        """Test getting model name for fincas endpoint."""
        model = middleware.get_model_name('/api/fincas/')
        assert model == 'Finca'
    
    def test_get_model_name_unknown(self, middleware):
        """Test getting model name for unknown endpoint."""
        model = middleware.get_model_name('/unknown/path/')
        assert model == 'Unknown'
    
    def test_create_action_description_get(self, middleware, request_factory):
        """Test creating action description for GET."""
        request = request_factory.get('/api/images/')
        description = middleware.create_action_description(request)
        assert 'Visualización' in description
    
    def test_create_action_description_post(self, middleware, request_factory):
        """Test creating action description for POST."""
        request = request_factory.post('/api/images/')
        description = middleware.create_action_description(request)
        assert 'Creación' in description
    
    def test_get_action_display(self, middleware):
        """Test getting action display name."""
        display = middleware.get_action_display('view')
        assert display == 'Visualización'
        
        display = middleware.get_action_display('create')
        assert display == 'Creación'
    
    def test_calculate_response_time(self, middleware, request_factory):
        """Test calculating response time."""
        from django.utils import timezone
        request = request_factory.get('/api/images/')
        start_time = timezone.now()
        request._audit_start_time = start_time
        
        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.001)
        time_ms = middleware.calculate_response_time(request)
        assert time_ms >= 0
    
    @patch('api.realtime_middleware.realtime_service')
    def test_middleware_call_authenticated(self, mock_service, middleware, request_factory, user):
        """Test middleware call with authenticated user."""
        request = request_factory.get('/api/images/')
        request.user = user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        
        response = middleware(request)
        
        assert response.status_code == 200
        mock_service.send_activity_log.assert_called_once()
    
    @patch('api.realtime_middleware.realtime_service')
    def test_middleware_call_unauthenticated(self, mock_service, middleware, request_factory):
        """Test middleware call with unauthenticated user."""
        request = request_factory.get('/api/images/')
        request.user = Mock(is_authenticated=False)
        
        response = middleware(request)
        
        assert response.status_code == 200
        mock_service.send_activity_log.assert_not_called()


class TestRealtimeLoginMiddleware:
    """Tests for RealtimeLoginMiddleware."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        get_response = Mock(return_value=Mock(status_code=200))
        return RealtimeLoginMiddleware(get_response)
    
    def test_get_client_ip(self, middleware, request_factory):
        """Test getting client IP."""
        request = request_factory.post('/api/auth/login/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = middleware.get_client_ip(request)
        
        assert ip == '192.168.1.1'
    
    @patch('api.realtime_middleware.realtime_service')
    def test_middleware_call_login_success(self, mock_service, middleware, request_factory, user):
        """Test middleware call with successful login."""
        request = request_factory.post('/api/auth/login/')
        request.user = user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        
        response = Mock(status_code=200)
        middleware.get_response = Mock(return_value=response)
        
        result = middleware(request)
        
        assert result.status_code == 200
        mock_service.send_login_activity.assert_called_once()
        call_args = mock_service.send_login_activity.call_args[0][0]
        assert call_args['success'] is True
        assert call_args['usuario'] == user.username
    
    @patch('api.realtime_middleware.realtime_service')
    def test_middleware_call_login_failure(self, mock_service, middleware, request_factory):
        """Test middleware call with failed login."""
        request = request_factory.post('/api/auth/login/')
        request.user = Mock(is_authenticated=False)
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        response = Mock(status_code=401)
        middleware.get_response = Mock(return_value=response)
        
        result = middleware(request)
        
        assert result.status_code == 401
        mock_service.send_login_activity.assert_called_once()
        call_args = mock_service.send_login_activity.call_args[0][0]
        assert call_args['success'] is False
    
    @patch('api.realtime_middleware.realtime_service')
    def test_middleware_call_non_login_path(self, mock_service, middleware, request_factory):
        """Test middleware call with non-login path."""
        request = request_factory.get('/api/images/')
        
        response = middleware(request)
        
        assert response.status_code == 200
        mock_service.send_login_activity.assert_not_called()

