"""
Tests for password service.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from api.services.auth import PasswordService
from api.services.base import ServiceResult


@pytest.mark.django_db
class TestPasswordService:
    """Tests for PasswordService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PasswordService()
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    def test_forgot_password_success(self, service, user):
        """Test successful password reset request."""
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_token = Mock()
            mock_token.token = 'test-token'
            mock_token.expires_at.isoformat.return_value = '2024-12-31T00:00:00'
            mock_token_model = Mock()
            mock_token_model.create_for_user.return_value = mock_token
            mock_models.return_value = {'EmailVerificationToken': mock_token_model}
            
            with patch('api.services.email.send_email_notification', return_value={'success': True}):
                result = service.forgot_password(user.email)
                
                assert result.success
                assert 'token' in result.data
    
    def test_forgot_password_user_not_found(self, service):
        """Test password reset request for non-existent user."""
        result = service.forgot_password('nonexistent@example.com')
        
        assert result.success  # Should not reveal if user exists
    
    def test_forgot_password_empty_email(self, service):
        """Test password reset request with empty email."""
        result = service.forgot_password('')
        
        assert not result.success
    
    def test_reset_password_success(self, service, user):
        """Test successful password reset."""
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_token = Mock()
            mock_token.user = user
            mock_token.is_expired.return_value = False
            mock_token_model = Mock()
            mock_token_model.objects.filter.return_value.first.return_value = mock_token
            mock_models.return_value = {'EmailVerificationToken': mock_token_model}
            
            with patch('core.utils.validate_password_strength'):
                result = service.reset_password('test-token', 'NewPass123!', 'NewPass123!')
                
                assert result.success
                assert user.check_password('NewPass123!')
    
    def test_reset_password_passwords_dont_match(self, service):
        """Test password reset with mismatched passwords."""
        result = service.reset_password('test-token', 'NewPass123!', 'DifferentPass123!')
        
        assert not result.success
    
    def test_reset_password_invalid_token(self, service):
        """Test password reset with invalid token."""
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_token_model = Mock()
            mock_token_model.objects.filter.return_value.first.return_value = None
            mock_models.return_value = {'EmailVerificationToken': mock_token_model}
            
            with patch('core.utils.validate_password_strength'):
                result = service.reset_password('invalid-token', 'NewPass123!', 'NewPass123!')
                
                assert not result.success
    
    def test_reset_password_expired_token(self, service, user):
        """Test password reset with expired token."""
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_token = Mock()
            mock_token.user = user
            mock_token.is_expired.return_value = True
            mock_token_model = Mock()
            mock_token_model.objects.filter.return_value.first.return_value = mock_token
            mock_models.return_value = {'EmailVerificationToken': mock_token_model}
            
            with patch('core.utils.validate_password_strength'):
                result = service.reset_password('expired-token', 'NewPass123!', 'NewPass123!')
                
                assert not result.success
    
    def test_get_client_ip_direct(self, service):
        """Test getting client IP directly."""
        request = Mock()
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        ip = service._get_client_ip(request)
        
        assert ip == '192.168.1.1'
    
    def test_get_client_ip_forwarded(self, service):
        """Test getting client IP from X-Forwarded-For."""
        request = Mock()
        request.META = {'HTTP_X_FORWARDED_FOR': '10.0.0.1, 192.168.1.1'}
        
        ip = service._get_client_ip(request)
        
        assert ip == '10.0.0.1'
    
    def test_log_password_reset_request(self, service, user):
        """Test logging password reset request."""
        request = Mock()
        request.META = {'REMOTE_ADDR': '192.168.1.1', 'HTTP_USER_AGENT': 'TestAgent'}
        
        service._log_password_reset_request(user, request)
        
        from audit.models import LoginHistory
        assert LoginHistory.objects.filter(user=user).exists()

