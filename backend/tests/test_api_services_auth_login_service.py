"""
Unit tests for login service module (login_service.py).
Tests user authentication and login functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from api.services.auth.login_service import LoginService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_staff = False
    user.is_superuser = False
    user.is_active = True
    user.date_joined = Mock(isoformat=lambda: '2024-01-01T00:00:00')
    user.last_login = Mock(isoformat=lambda: '2024-01-01T00:00:00')
    return user


@pytest.fixture
def login_service():
    """Create a LoginService instance for testing."""
    return LoginService()


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = Mock()
    request.META = {
        'HTTP_X_FORWARDED_FOR': '192.168.1.1',
        'HTTP_USER_AGENT': 'Mozilla/5.0'
    }
    return request


class TestLoginService:
    """Tests for LoginService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = LoginService()
        assert service is not None
    
    @patch('api.services.auth.login_service.authenticate')
    @patch('api.services.auth.login_service.RefreshToken')
    @patch('api.services.auth.login_service.LoginHistory')
    def test_login_user_success(self, mock_login_history, mock_refresh_token, mock_authenticate, 
                                 login_service, mock_user, mock_request):
        """Test successful user login."""
        mock_authenticate.return_value = mock_user
        mock_refresh = Mock()
        mock_access = Mock()
        mock_access.__str__ = lambda self: "access_token"
        mock_access.__getitem__ = lambda self, key: 1234567890 if key == 'exp' else None
        mock_refresh.__str__ = lambda self: "refresh_token"
        mock_refresh.__getitem__ = lambda self, key: 1234567890 if key == 'exp' else None
        mock_refresh.access_token = mock_access
        mock_refresh_token.for_user.return_value = mock_refresh
        
        result = login_service.login_user("testuser", "password123", mock_request)
        
        assert result.success is True
        assert 'access' in result.data
        assert 'refresh' in result.data
        assert 'user' in result.data
        assert result.data['user']['username'] == "testuser"
    
    @patch('api.services.auth.login_service.authenticate')
    def test_login_user_invalid_credentials(self, mock_authenticate, login_service):
        """Test login with invalid credentials."""
        mock_authenticate.return_value = None
        
        result = login_service.login_user("testuser", "wrongpassword")
        
        assert result.success is False
        assert result.error is not None
        assert "Credenciales inválidas" in result.error.message
    
    @patch('api.services.auth.login_service.authenticate')
    def test_login_user_inactive(self, mock_authenticate, login_service, mock_user):
        """Test login with inactive user."""
        mock_user.is_active = False
        mock_authenticate.return_value = mock_user
        
        result = login_service.login_user("testuser", "password123")
        
        assert result.success is False
        assert "desactivada" in result.error.message
    
    @patch('api.services.auth.login_service.RefreshToken')
    def test_logout_user_success(self, mock_refresh_token, login_service, mock_user):
        """Test successful user logout."""
        mock_token = Mock()
        mock_refresh_token.return_value = mock_token
        
        result = login_service.logout_user(mock_user, "refresh_token_string")
        
        assert result.success is True
        mock_token.blacklist.assert_called_once()
    
    @patch('api.services.auth.login_service.RefreshToken')
    def test_logout_user_invalid_token(self, mock_refresh_token, login_service, mock_user):
        """Test logout with invalid token."""
        mock_refresh_token.side_effect = Exception("Invalid token")
        
        result = login_service.logout_user(mock_user, "invalid_token")
        
        # Should still succeed, just log warning
        assert result.success is True
    
    @patch('api.services.auth.login_service.RefreshToken')
    def test_refresh_token_success(self, mock_refresh_token, login_service):
        """Test successful token refresh."""
        mock_token = Mock()
        mock_access = Mock()
        mock_access.__str__ = lambda self: "new_access_token"
        mock_access.__getitem__ = lambda self, key: 1234567890 if key == 'exp' else None
        mock_token.access_token = mock_access
        mock_refresh_token.return_value = mock_token
        
        result = login_service.refresh_token("refresh_token_string")
        
        assert result.success is True
        assert 'access' in result.data
        assert 'access_expires_at' in result.data
    
    @patch('api.services.auth.login_service.RefreshToken')
    def test_refresh_token_invalid(self, mock_refresh_token, login_service):
        """Test refresh with invalid token."""
        mock_refresh_token.side_effect = Exception("Invalid token")
        
        result = login_service.refresh_token("invalid_token")
        
        assert result.success is False
        assert "inválido" in result.error.message
    
    def test_get_client_ip_from_forwarded_for(self, login_service, mock_request):
        """Test getting client IP from X-Forwarded-For header."""
        ip = login_service._get_client_ip(mock_request)
        
        assert ip == "192.168.1.1"
    
    def test_get_client_ip_from_remote_addr(self, login_service):
        """Test getting client IP from REMOTE_ADDR."""
        request = Mock()
        request.META = {'REMOTE_ADDR': '10.0.0.1'}
        
        ip = login_service._get_client_ip(request)
        
        assert ip == "10.0.0.1"
    
    @patch('api.services.auth.login_service.LoginHistory')
    def test_log_user_login_success(self, mock_login_history, login_service, mock_user, mock_request):
        """Test logging user login."""
        login_service._log_user_login(mock_user, mock_request)
        
        mock_login_history.objects.create.assert_called_once()
        call_args = mock_login_history.objects.create.call_args[1]
        assert call_args['usuario'] == mock_user
        assert call_args['success'] is True
    
    @patch('api.services.auth.login_service.LoginHistory')
    def test_log_user_login_no_request(self, mock_login_history, login_service, mock_user):
        """Test logging user login without request."""
        login_service._log_user_login(mock_user, None)
        
        mock_login_history.objects.create.assert_called_once()
        call_args = mock_login_history.objects.create.call_args[1]
        assert call_args['ip_address'] is None

