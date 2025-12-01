"""
Unit tests for registration service module (registration_service.py).
Tests user registration and pre-registration functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from api.services.auth.registration_service import RegistrationService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def registration_service():
    """Create a RegistrationService instance for testing."""
    return RegistrationService()


@pytest.fixture
def user_data():
    """Create sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = Mock()
    request.META = {
        'HTTP_X_FORWARDED_FOR': '192.168.1.1',
        'HTTP_USER_AGENT': 'Mozilla/5.0'
    }
    return request


class TestRegistrationService:
    """Tests for RegistrationService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = RegistrationService()
        assert service is not None
    
    @patch('api.services.auth.registration_service.User')
    @patch('api.services.auth.registration_service.RefreshToken')
    @patch('api.utils.model_imports.get_models_safely')
    @patch('core.utils.validate_password_strength')
    def test_register_user_success(self, mock_validate_password, mock_models, 
                                   mock_refresh_token, mock_user_model, 
                                   registration_service, user_data, mock_request):
        """Test successful user registration."""
        mock_validate_password.return_value = None  # No error
        mock_user_model.objects.filter.return_value.exists.return_value = False
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = user_data['username']
        mock_user.email = user_data['email']
        mock_user.first_name = user_data['first_name']
        mock_user.last_name = user_data['last_name']
        mock_user.is_staff = False
        mock_user.is_superuser = False
        mock_user.is_active = True
        mock_user.date_joined = Mock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_user_model.objects.create_user.return_value = mock_user
        
        mock_refresh = Mock()
        mock_access = Mock()
        mock_access.__str__ = lambda self: "access_token"
        mock_access.__getitem__ = lambda self, key: 1234567890 if key == 'exp' else None
        mock_refresh.__str__ = lambda self: "refresh_token"
        mock_refresh.__getitem__ = lambda self, key: 1234567890 if key == 'exp' else None
        mock_refresh.access_token = mock_access
        mock_refresh_token.for_user.return_value = mock_refresh
        
        mock_verification_token = Mock()
        mock_verification_token.token = "verification_token_string"
        mock_email_token_model = Mock()
        mock_email_token_model.create_for_user.return_value = mock_verification_token
        mock_models.return_value = {'EmailVerificationToken': mock_email_token_model}
        
        result = registration_service.register_user(user_data, mock_request)
        
        assert result.success is True
        assert 'access' in result.data
        assert 'refresh' in result.data
        assert 'user' in result.data
        assert result.data['user']['username'] == user_data['username']
    
    def test_register_user_missing_fields(self, registration_service, user_data):
        """Test registration with missing required fields."""
        incomplete_data = {'username': 'testuser'}
        
        result = registration_service.register_user(incomplete_data)
        
        assert result.success is False
        assert result.error is not None
    
    def test_register_user_password_mismatch(self, registration_service, user_data):
        """Test registration with password mismatch."""
        user_data['password_confirm'] = 'DifferentPassword123!'
        
        result = registration_service.register_user(user_data)
        
        assert result.success is False
        assert "no coinciden" in result.error.message
    
    @patch('core.utils.validate_password_strength')
    def test_register_user_weak_password(self, mock_validate_password, registration_service, user_data):
        """Test registration with weak password."""
        from core.utils import PasswordValidationError
        mock_validate_password.side_effect = PasswordValidationError("Password too weak")
        
        result = registration_service.register_user(user_data)
        
        assert result.success is False
        assert result.error is not None
    
    @patch('api.services.auth.registration_service.User')
    def test_register_user_email_exists(self, mock_user_model, registration_service, user_data):
        """Test registration with existing email."""
        mock_user_model.objects.filter.return_value.exists.return_value = True
        
        result = registration_service.register_user(user_data)
        
        assert result.success is False
        assert "ya está registrado" in result.error.message
    
    @patch('api.services.auth.registration_service.User')
    def test_register_user_username_exists(self, mock_user_model, registration_service, user_data):
        """Test registration with existing username."""
        mock_user_model.objects.filter.side_effect = [
            Mock(exists=Mock(return_value=False)),  # Email check
            Mock(exists=Mock(return_value=True))    # Username check
        ]
        
        result = registration_service.register_user(user_data)
        
        assert result.success is False
        assert "ya está en uso" in result.error.message
    
    @patch('api.services.auth.registration_service.User')
    @patch('api.utils.model_imports.get_models_safely')
    @patch('core.utils.validate_password_strength')
    @patch('api.services.email.email_service.send_custom_email')
    def test_register_user_with_email_verification_success(self, mock_send_email, mock_validate_password,
                                                           mock_models, mock_user_model,
                                                           registration_service, user_data, mock_request):
        """Test registration with email verification."""
        mock_validate_password.return_value = None
        mock_user_model.objects.filter.return_value.exists.return_value = False
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = user_data['email']
        mock_user.email = user_data['email']
        mock_user.first_name = user_data['first_name']
        mock_user.last_name = user_data['last_name']
        mock_user.is_active = True
        mock_user.date_joined = Mock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_user.get_full_name.return_value = f"{user_data['first_name']} {user_data['last_name']}"
        mock_user_model.objects.create_user.return_value = mock_user
        
        mock_verification_token = Mock()
        mock_verification_token.token = "verification_token_string"
        mock_email_token_model = Mock()
        mock_email_token_model.create_for_user.return_value = mock_verification_token
        mock_models.return_value = {'EmailVerificationToken': mock_email_token_model}
        
        mock_send_email.return_value = None
        
        result = registration_service.register_user_with_email_verification(user_data, mock_request)
        
        assert result.success is True
        assert 'user' in result.data
        assert result.data['verification_required'] is True
    
    @patch('personas.models.PendingRegistration')
    @patch('core.utils.validate_password_strength')
    @patch('api.services.auth.registration_service.User')
    def test_pre_register_user_success(self, mock_user_model, mock_validate_password,
                                       mock_pending_reg, registration_service, user_data):
        """Test successful pre-registration."""
        mock_validate_password.return_value = None
        mock_user_model.objects.filter.return_value.exists.return_value = False
        mock_pending_reg.objects.filter.return_value.first.return_value = None
        mock_pending = Mock()
        mock_pending_reg.objects.create.return_value = mock_pending
        
        # Mock _validate_pre_registration_data to return None (no errors)
        with patch.object(registration_service, '_validate_pre_registration_data', return_value=None), \
             patch.object(registration_service, '_send_pre_registration_verification_email', 
                         return_value={'success': True}):
            result = registration_service.pre_register_user(user_data)
            
            assert result.success is True
            assert result.data is not None
            assert 'email' in result.data
    
    @patch('personas.models.PendingRegistration')
    @patch('core.utils.validate_password_strength')
    @patch('api.services.auth.registration_service.User')
    def test_pre_register_user_existing_pending(self, mock_user_model, mock_validate_password,
                                                mock_pending_reg, registration_service, user_data):
        """Test pre-registration with existing pending registration."""
        mock_validate_password.return_value = None
        mock_user_model.objects.filter.return_value.exists.return_value = False
        existing_pending = Mock()
        existing_pending.is_expired.return_value = False
        mock_pending_reg.objects.filter.return_value.first.return_value = existing_pending
        
        with patch.object(registration_service, '_send_pre_registration_verification_email',
                         return_value={'success': True}):
            result = registration_service.pre_register_user(user_data)
            
            assert result.success is True
    
    @patch('personas.models.PendingRegistration')
    @patch('core.utils.validate_password_strength')
    def test_pre_register_user_validation_failure(self, mock_validate_password,
                                                   mock_pending_reg, registration_service):
        """Test pre-registration with validation failure."""
        from core.utils import PasswordValidationError
        mock_validate_password.side_effect = PasswordValidationError("Password too weak")
        
        user_data = {'email': 'test@example.com', 'password': 'weak'}
        result = registration_service.pre_register_user(user_data)
        
        assert result.success is False
    
    @patch('personas.models.PendingRegistration')
    @patch('personas.serializers.PersonaRegistroSerializer')
    @patch('api.services.auth.registration_service.User')
    @patch('api.services.auth.registration_service.transaction')
    def test_verify_pre_registration_and_create_user_success(self, mock_transaction, mock_user_model,
                                                             mock_persona_serializer, mock_pending_reg,
                                                             registration_service):
        """Test successful pre-registration verification and user creation."""
        import uuid
        token_uuid = uuid.uuid4()
        
        mock_pending = Mock()
        mock_pending.is_verified = False
        mock_pending.is_expired.return_value = False
        mock_pending.data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        mock_pending_reg.objects.get.return_value = mock_pending
        
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = 'test@example.com'
        mock_user.email = 'test@example.com'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.is_active = True
        mock_user.date_joined = Mock(isoformat=lambda: '2024-01-01T00:00:00')
        mock_user_model.objects.create_user.return_value = mock_user
        
        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = True
        mock_persona_serializer.return_value = mock_serializer
        
        result = registration_service.verify_pre_registration_and_create_user(str(token_uuid))
        
        assert result.success is True
        assert 'user' in result.data
        mock_pending.verify.assert_called_once()
    
    @patch('personas.models.PendingRegistration')
    def test_verify_pre_registration_invalid_token(self, mock_pending_reg, registration_service):
        """Test verification with invalid token."""
        mock_pending_reg.objects.get.side_effect = Exception("DoesNotExist")
        
        result = registration_service.verify_pre_registration_and_create_user("invalid_token")
        
        assert result.success is False
        assert "inválido" in result.error.message
    
    @patch('personas.models.PendingRegistration')
    def test_verify_pre_registration_already_verified(self, mock_pending_reg, registration_service):
        """Test verification with already verified token."""
        import uuid
        token_uuid = uuid.uuid4()
        
        mock_pending = Mock()
        mock_pending.is_verified = True
        mock_pending_reg.objects.get.return_value = mock_pending
        
        result = registration_service.verify_pre_registration_and_create_user(str(token_uuid))
        
        assert result.success is False
        assert "ya fue utilizado" in result.error.message
    
    @patch('personas.models.PendingRegistration')
    def test_verify_pre_registration_expired(self, mock_pending_reg, registration_service):
        """Test verification with expired token."""
        import uuid
        token_uuid = uuid.uuid4()
        
        mock_pending = Mock()
        mock_pending.is_verified = False
        mock_pending.is_expired.return_value = True
        mock_pending_reg.objects.get.return_value = mock_pending
        
        result = registration_service.verify_pre_registration_and_create_user(str(token_uuid))
        
        assert result.success is False
        assert "expirado" in result.error.message
        mock_pending.delete.assert_called_once()

