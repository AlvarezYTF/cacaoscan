"""
Tests for API middleware.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.http import JsonResponse

from api.middleware import (
    AuditMiddleware,
    LoginAuditMiddleware,
    TokenCleanupMiddleware,
    log_custom_activity,
    log_failed_login
)


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


@pytest.fixture
def get_response():
    """Create mock get_response function."""
    def _get_response(request):
        response = Mock()
        response.status_code = 200
        return response
    return _get_response


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


def test_audit_middleware_init(get_response):
    """Test AuditMiddleware initialization."""
    middleware = AuditMiddleware(get_response)
    assert middleware.get_response == get_response


def test_audit_middleware_get_client_ip_direct(request_factory, get_response):
    """Test getting client IP directly."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.get('/api/test/')
    request.META['REMOTE_ADDR'] = '192.168.1.1'
    
    ip = middleware.get_client_ip(request)
    assert ip == '192.168.1.1'


def test_audit_middleware_get_client_ip_forwarded(request_factory, get_response):
    """Test getting client IP from X-Forwarded-For."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.get('/api/test/')
    request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.2, 10.0.0.1'
    
    ip = middleware.get_client_ip(request)
    assert ip == '192.168.1.2'


def test_audit_middleware_determine_post_action_login(get_response):
    """Test determining POST action for login."""
    middleware = AuditMiddleware(get_response)
    action = middleware._determine_post_action('/api/auth/login/')
    assert action == 'login'


def test_audit_middleware_determine_post_action_register(get_response):
    """Test determining POST action for register."""
    middleware = AuditMiddleware(get_response)
    action = middleware._determine_post_action('/api/auth/register/')
    assert action == 'create'


def test_audit_middleware_determine_post_action_upload(get_response):
    """Test determining POST action for upload."""
    middleware = AuditMiddleware(get_response)
    action = middleware._determine_post_action('/api/images/upload/')
    assert action == 'upload'


def test_audit_middleware_determine_get_action_download(get_response):
    """Test determining GET action for download."""
    middleware = AuditMiddleware(get_response)
    action = middleware._determine_get_action('/api/reports/download/')
    assert action == 'download'


def test_audit_middleware_determine_action_post(request_factory, get_response):
    """Test determine_action for POST."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.post('/api/auth/login/')
    action = middleware.determine_action(request)
    assert action == 'login'


def test_audit_middleware_determine_action_put(request_factory, get_response):
    """Test determine_action for PUT."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.put('/api/test/')
    action = middleware.determine_action(request)
    assert action == 'update'


def test_audit_middleware_determine_action_delete(request_factory, get_response):
    """Test determine_action for DELETE."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.delete('/api/test/')
    action = middleware.determine_action(request)
    assert action == 'delete'


def test_audit_middleware_determine_model_fincas(get_response):
    """Test determine_model for fincas."""
    middleware = AuditMiddleware(get_response)
    request = Mock()
    request.path = '/api/fincas/'
    model = middleware.determine_model(request)
    assert model == 'Finca'


def test_audit_middleware_determine_model_images(get_response):
    """Test determine_model for images."""
    middleware = AuditMiddleware(get_response)
    request = Mock()
    request.path = '/api/images/'
    model = middleware.determine_model(request)
    assert model == 'CacaoImage'


def test_audit_middleware_extract_object_id(get_response):
    """Test extract_object_id from URL."""
    middleware = AuditMiddleware(get_response)
    request = Mock()
    request.path = '/api/fincas/123/'
    object_id = middleware.extract_object_id(request)
    assert object_id == '123'


def test_audit_middleware_extract_object_id_no_id(get_response):
    """Test extract_object_id when no ID in URL."""
    middleware = AuditMiddleware(get_response)
    request = Mock()
    request.path = '/api/fincas/'
    object_id = middleware.extract_object_id(request)
    assert object_id is None


def test_audit_middleware_create_description(get_response, user):
    """Test create_description."""
    middleware = AuditMiddleware(get_response)
    request = Mock()
    request.user = user
    request.method = 'POST'
    request.path = '/api/fincas/'
    
    description = middleware.create_description(request, 'create', 'Finca')
    assert user.username in description
    assert 'creó' in description


@patch('api.middleware.ActivityLog')
def test_audit_middleware_log_activity(mock_activity_log, request_factory, get_response, user):
    """Test log_activity."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.get('/api/fincas/')
    request.user = user
    request.audit_action = 'view'
    request.audit_info = {
        'ip_address': '127.0.0.1',
        'user_agent': 'test-agent'
    }
    
    mock_activity_log.log_activity = Mock()
    middleware.log_activity(request)
    
    mock_activity_log.log_activity.assert_called_once()


def test_audit_middleware_call_unauthenticated(request_factory, get_response):
    """Test middleware call with unauthenticated user."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.get('/api/test/')
    request.user = Mock()
    request.user.is_authenticated = False
    
    response = middleware(request)
    
    assert response.status_code == 200
    assert not hasattr(request, 'audit_action') or request.audit_action is None


def test_audit_middleware_call_authenticated_success(request_factory, get_response, user):
    """Test middleware call with authenticated user and success response."""
    middleware = AuditMiddleware(get_response)
    request = request_factory.get('/api/test/')
    request.user = user
    
    with patch.object(middleware, 'log_activity') as mock_log:
        response = middleware(request)
        
        assert response.status_code == 200
        mock_log.assert_called_once()


def test_login_audit_middleware_init(get_response):
    """Test LoginAuditMiddleware initialization."""
    middleware = LoginAuditMiddleware(get_response)
    assert middleware.get_response == get_response


def test_login_audit_middleware_get_client_ip(request_factory, get_response):
    """Test LoginAuditMiddleware get_client_ip."""
    middleware = LoginAuditMiddleware(get_response)
    request = request_factory.get('/api/test/')
    request.META['REMOTE_ADDR'] = '192.168.1.1'
    
    ip = middleware.get_client_ip(request)
    assert ip == '192.168.1.1'


@patch('api.middleware.LoginHistory')
def test_login_audit_middleware_log_login(mock_login_history, request_factory, get_response, user):
    """Test log_login."""
    middleware = LoginAuditMiddleware(get_response)
    request = request_factory.get('/api/test/')
    request.user = user
    request.META['HTTP_USER_AGENT'] = 'test-agent'
    
    mock_login_history.log_login = Mock()
    middleware.log_login(request)
    
    mock_login_history.log_login.assert_called_once()


@patch('api.middleware.LoginHistory')
def test_login_audit_middleware_log_logout(mock_login_history, request_factory, get_response, user):
    """Test log_logout."""
    middleware = LoginAuditMiddleware(get_response)
    request = request_factory.get('/api/auth/logout/')
    request.user = user
    
    mock_login_history.log_logout = Mock()
    middleware.log_logout(request)
    
    mock_login_history.log_logout.assert_called_once()


def test_token_cleanup_middleware_init(get_response):
    """Test TokenCleanupMiddleware initialization."""
    middleware = TokenCleanupMiddleware(get_response)
    assert middleware.get_response == get_response


def test_token_cleanup_middleware_call(request_factory, get_response):
    """Test TokenCleanupMiddleware call."""
    middleware = TokenCleanupMiddleware(get_response)
    request = request_factory.get('/api/test/')
    
    response = middleware(request)
    
    assert response.status_code == 200


@patch('api.middleware.ActivityLog')
def test_log_custom_activity(mock_activity_log, user):
    """Test log_custom_activity function."""
    from api.middleware import log_custom_activity
    
    mock_activity_log.log_activity = Mock()
    log_custom_activity(
        user=user,
        action='test_action',
        model='TestModel',
        description='Test description'
    )
    
    mock_activity_log.log_activity.assert_called_once()


@patch('api.middleware.LoginHistory')
def test_log_failed_login(mock_login_history):
    """Test log_failed_login function."""
    from api.middleware import log_failed_login
    
    mock_login_history.log_login = Mock()
    log_failed_login(
        username='testuser',
        ip_address='127.0.0.1',
        user_agent='test-agent',
        failure_reason='Invalid password'
    )
    
    mock_login_history.log_login.assert_called_once()


