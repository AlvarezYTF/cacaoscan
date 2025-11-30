"""
Unit tests for password service module (password_service.py).
Tests password reset and recovery functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User

from api.services.auth.password_service import PasswordService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def password_service():
    """Create a PasswordService instance for testing."""
    return PasswordService()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.get_full_name.return_value = "Test User"
    return user


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = Mock()
    request.META = {
        'HTTP_X_FORWARDED_FOR': '192.168.1.1',
        'HTTP_USER_AGENT': 'Mozilla/5.0'
    }
    return request


class TestPasswordService:
    """Tests for PasswordService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = PasswordService()
        assert service is not None
    
    @patch('api.services.auth.password_service.User')
    @patch('api.utils.model_imports.get_models_safely')
    @patch('api.services.email.send_email_notification')
    def test_forgot_password_success(self, mock_send_email, mock_models, mock_user_model,
                                     password_service, mock_user, mock_request):
        """Test successful password reset request."""
        mock_user_model.objects.get.return_value = mock_user
        
        mock_token = Mock()
        mock_token.token = "reset_token_string"
        mock_token.expires_at = Mock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_email_token_model = Mock()
        mock_email_token_model.create_for_user.return_value = mock_token
        mock_models.return_value = {'EmailVerificationToken': mock_email_token_model}
        
        mock_send_email.return_value = {"success": True}
        
        result = password_service.forgot_password("test@example.com", mock_request)
        
        assert result.success is True
        assert 'token' in result.data
        mock_send_email.assert_called_once()
    
    @patch('api.services.auth.password_service.User')
    def test_forgot_password_user_not_found(self, mock_user_model, password_service):
        """Test password reset request for non-existent user."""
        # Create a proper DoesNotExist exception
        class DoesNotExist(Exception):
            pass
        mock_user_model.DoesNotExist = DoesNotExist
        mock_user_model.objects.get.side_effect = DoesNotExist()
        
        result = password_service.forgot_password("nonexistent@example.com")
        
        # Should still return success for security (don't reveal if email exists)
        assert result.success is True
    
    def test_forgot_password_empty_email(self, password_service):
        """Test password reset request with empty email."""
        result = password_service.forgot_password("")
        
        assert result.success is False
        assert "Email es requerido" in result.error.message
    
    @patch('api.services.auth.password_service.User')
    @patch('api.utils.model_imports.get_models_safely')
    @patch('core.utils.validate_password_strength')
    def test_reset_password_success(self, mock_validate_password, mock_models, mock_user_model,
                                    password_service, mock_user):
        """Test successful password reset."""
        mock_validate_password.return_value = None
        
        mock_token_obj = Mock()
        mock_token_obj.is_expired.return_value = False
        mock_token_obj.user = mock_user
        mock_token_obj.delete = Mock()
        
        mock_email_token_model = Mock()
        mock_email_token_model.objects.filter.return_value.first.return_value = mock_token_obj
        mock_models.return_value = {'EmailVerificationToken': mock_email_token_model}
        
        result = password_service.reset_password(
            "reset_token_string",
            "NewSecurePass123!",
            "NewSecurePass123!"
        )
        
        assert result.success is True
        mock_user.set_password.assert_called_once_with("NewSecurePass123!")
        mock_user.save.assert_called_once()
        mock_token_obj.delete.assert_called_once()
    
    def test_reset_password_password_mismatch(self, password_service):
        """Test password reset with password mismatch."""
        result = password_service.reset_password(
            "token",
            "NewPassword123!",
            "DifferentPassword123!"
        )
        
        assert result.success is False
        assert "no coinciden" in result.error.message
    
    @patch('core.utils.validate_password_strength')
    def test_reset_password_weak_password(self, mock_validate_password, password_service):
        """Test password reset with weak password."""
        from core.utils import PasswordValidationError
        mock_validate_password.side_effect = PasswordValidationError("Password too weak")
        
        result = password_service.reset_password(
            "token",
            "weak",
            "weak"
        )
        
        assert result.success is False
        assert result.error is not None
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_reset_password_invalid_token(self, mock_models, password_service):
        """Test password reset with invalid token."""
        mock_email_token_model = Mock()
        mock_email_token_model.objects.filter.return_value.first.return_value = None
        mock_models.return_value = {'EmailVerificationToken': mock_email_token_model}
        
        result = password_service.reset_password(
            "invalid_token",
            "NewPassword123!",
            "NewPassword123!"
        )
        
        assert result.success is False
        assert "inválido" in result.error.message
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_reset_password_expired_token(self, mock_models, password_service):
        """Test password reset with expired token."""
        mock_token_obj = Mock()
        mock_token_obj.is_expired.return_value = True
        
        mock_email_token_model = Mock()
        mock_email_token_model.objects.filter.return_value.first.return_value = mock_token_obj
        mock_models.return_value = {'EmailVerificationToken': mock_email_token_model}
        
        result = password_service.reset_password(
            "expired_token",
            "NewPassword123!",
            "NewPassword123!"
        )
        
        assert result.success is False
        assert "expirado" in result.error.message
    
    def test_get_client_ip_from_forwarded_for(self, password_service, mock_request):
        """Test getting client IP from X-Forwarded-For header."""
        ip = password_service._get_client_ip(mock_request)
        
        assert ip == "192.168.1.1"
    
    def test_get_client_ip_from_remote_addr(self, password_service):
        """Test getting client IP from REMOTE_ADDR."""
        request = Mock()
        request.META = {'REMOTE_ADDR': '10.0.0.1'}
        
        ip = password_service._get_client_ip(request)
        
        assert ip == "10.0.0.1"
    
    @patch('api.services.auth.password_service.LoginHistory')
    def test_log_password_reset_request(self, mock_login_history, password_service, mock_user, mock_request):
        """Test logging password reset request."""
        password_service._log_password_reset_request(mock_user, mock_request)
        
        mock_login_history.objects.create.assert_called_once()
        call_args = mock_login_history.objects.create.call_args[1]
        assert call_args['usuario'] == mock_user
        assert call_args['success'] is True

