"""
Tests for verification service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User

from api.services.auth.verification_service import VerificationService


@pytest.fixture
def verification_service():
    """Create a verification service instance."""
    return VerificationService()


@pytest.fixture
def user(db):
    """Create a test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestVerificationService:
    """Tests for VerificationService."""
    
    def test_verify_email_success(self, verification_service, user):
        """Test successful email verification."""
        with patch('api.utils.model_imports.get_models_safely') as mock_get_models:
            mock_token = Mock()
            mock_token.token = 'valid_token'
            mock_token.is_expired.return_value = False
            mock_token.verify = Mock()
            mock_token.user = user
            
            mock_model = Mock()
            mock_model.objects.filter.return_value.first.return_value = mock_token
            mock_get_models.return_value = {'EmailVerificationToken': mock_model}
            
            with patch.object(verification_service, 'create_audit_log'):
                result = verification_service.verify_email('valid_token')
                
                assert result.success is True
                assert 'user' in result.data
                assert mock_token.verify.called
    
    def test_verify_email_invalid_token(self, verification_service):
        """Test email verification with invalid token."""
        with patch('api.utils.model_imports.get_models_safely') as mock_get_models:
            mock_model = Mock()
            mock_model.objects.filter.return_value.first.return_value = None
            mock_get_models.return_value = {'EmailVerificationToken': mock_model}
            
            result = verification_service.verify_email('invalid_token')
            
            assert result.success is False
            assert result.error is not None
    
    def test_verify_email_expired_token(self, verification_service, user):
        """Test email verification with expired token."""
        with patch('api.utils.model_imports.get_models_safely') as mock_get_models:
            mock_token = Mock()
            mock_token.is_expired.return_value = True
            
            mock_model = Mock()
            mock_model.objects.filter.return_value.first.return_value = mock_token
            mock_get_models.return_value = {'EmailVerificationToken': mock_model}
            
            result = verification_service.verify_email('expired_token')
            
            assert result.success is False
            assert result.error is not None
    
    def test_verify_email_exception(self, verification_service):
        """Test email verification with exception."""
        # Patch get_models_safely where it's imported inside the method
        # The import is: from ...utils.model_imports import get_models_safely
        # So we need to patch it at the module level where it's used
        with patch('api.utils.model_imports.get_models_safely', side_effect=Exception("Database error")):
            result = verification_service.verify_email('token')
            
            assert result.success is False
            assert result.error is not None
    
    def test_resend_verification_success(self, verification_service, user):
        """Test successful verification resend."""
        with patch('api.utils.model_imports.get_models_safely') as mock_get_models:
            mock_token = Mock()
            mock_token.token = 'new_token'
            mock_token.expires_at = Mock()
            mock_token.expires_at.isoformat.return_value = '2024-01-01T00:00:00'
            
            mock_model = Mock()
            mock_model.create_for_user.return_value = mock_token
            mock_get_models.return_value = {'EmailVerificationToken': mock_model}
            
            with patch.object(verification_service, 'create_audit_log'):
                result = verification_service.resend_verification(user.email)
                
                assert result.success is True
                assert 'token' in result.data
                assert mock_model.create_for_user.called
    
    def test_resend_verification_user_not_found(self, verification_service):
        """Test verification resend when user not found."""
        with patch('django.contrib.auth.models.User') as mock_user:
            mock_user.DoesNotExist = User.DoesNotExist
            mock_user.objects.get.side_effect = User.DoesNotExist()
            
            result = verification_service.resend_verification('nonexistent@example.com')
            
            # Should still return success for security
            assert result.success is True
    
    def test_resend_verification_empty_email(self, verification_service):
        """Test verification resend with empty email."""
        result = verification_service.resend_verification('')
        
        assert result.success is False
        assert result.error is not None
    
    def test_resend_verification_exception(self, verification_service):
        """Test verification resend with exception."""
        with patch('api.services.auth.verification_service.User') as mock_user:
            mock_user.objects.get.side_effect = Exception("Database error")
            
            result = verification_service.resend_verification('test@example.com')
            
            assert result.success is False
            assert result.error is not None

