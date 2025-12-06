"""
Tests for registration service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from api.services.auth import RegistrationService
from api.services.base import ServiceResult


@pytest.mark.django_db
class TestRegistrationService:
    """Tests for RegistrationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return RegistrationService()
    
    def test_register_user_success(self, service):
        """Test successful user registration."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data') as mock_create:
                mock_user = User.objects.create_user(
                    username='newuser',
                    email='newuser@example.com',
                    password='TestPass123!'
                )
                mock_create.return_value = mock_user
                
                with patch('api.utils.model_imports.get_models_safely') as mock_models:
                    mock_token = Mock()
                    mock_token.token = 'test-token'
                    mock_token_model = Mock()
                    mock_token_model.create_for_user.return_value = mock_token
                    mock_models.return_value = {'EmailVerificationToken': mock_token_model}
                    
                    result = service.register_user(user_data)
                    
                    assert result.success
                    assert 'access' in result.data
                    assert 'refresh' in result.data
    
    def test_register_user_validation_error(self, service):
        """Test user registration with validation error."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch.object(service, '_validate_user_registration_data') as mock_validate:
            mock_validate.return_value = ServiceResult.validation_error("Passwords don't match")
            
            result = service.register_user(user_data)
            
            assert not result.success
    
    def test_register_user_with_email_verification(self, service):
        """Test user registration with email verification."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data') as mock_create:
                mock_user = User.objects.create_user(
                    username='newuser@example.com',
                    email='newuser@example.com',
                    password='TestPass123!'
                )
                mock_create.return_value = mock_user
                
                with patch('api.utils.model_imports.get_models_safely') as mock_models:
                    mock_token = Mock()
                    mock_token.token = 'test-token'
                    mock_token_model = Mock()
                    mock_token_model.create_for_user.return_value = mock_token
                    mock_models.return_value = {'EmailVerificationToken': mock_token_model}
                    
                    with patch.object(service, '_send_verification_email', return_value={'success': True}):
                        result = service.register_user_with_email_verification(user_data)
                        
                        assert result.success
                        assert 'verification_token' in result.data
    
    def test_validate_pre_registration_data_success(self, service):
        """Test validating pre-registration data successfully."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_pre_registration_data(user_data)
            
            assert result.success
    
    def test_validate_pre_registration_data_missing_fields(self, service):
        """Test validating pre-registration data with missing fields."""
        user_data = {'email': 'newuser@example.com'}
        
        result = service._validate_pre_registration_data(user_data)
        
        assert not result.success
    
    def test_validate_pre_registration_data_duplicate_email(self, service):
        """Test validating pre-registration data with duplicate email."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='TestPass123!'
        )
        
        user_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_pre_registration_data(user_data)
            
            assert not result.success
    
    def test_pre_register_user_success(self, service):
        """Test successful pre-registration."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!'
        }
        
        with patch('personas.models.PendingRegistration') as mock_pending:
            mock_pending_instance = Mock()
            mock_pending_instance.is_expired.return_value = False
            mock_pending_instance.delete = Mock()
            mock_pending.objects.filter.return_value.first.return_value = None
            mock_pending.objects.create.return_value = mock_pending_instance
            
            with patch.object(service, '_validate_pre_registration_data', return_value=None):
                with patch.object(service, '_send_pre_registration_verification_email', return_value={'success': True}):
                    result = service.pre_register_user(user_data)
                    
                    assert result.success
    
    def test_verify_pre_registration_and_create_user_success(self, service):
        """Test verifying pre-registration and creating user."""
        import uuid
        token = str(uuid.uuid4())
        
        with patch('personas.models.PendingRegistration') as mock_pending:
            # Create proper DoesNotExist exception
            class MockDoesNotExist(Exception):
                pass
            mock_pending.DoesNotExist = MockDoesNotExist
            
            mock_pending_instance = Mock()
            mock_pending_instance.is_verified = False
            mock_pending_instance.is_expired.return_value = False
            mock_pending_instance.delete = Mock()
            mock_pending_instance.data = {
                'email': 'newuser@example.com',
                'password': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
            mock_pending.objects.get.return_value = mock_pending_instance
            
            with patch('personas.serializers.PersonaRegistroSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_instance.is_valid.return_value = True
                mock_serializer_instance.validated_data = mock_pending_instance.data
                mock_serializer_class.return_value = mock_serializer_instance
                
                with patch.object(service, '_create_user_from_data') as mock_create:
                    mock_user = User.objects.create_user(
                        username='newuser@example.com',
                        email='newuser@example.com',
                        password='TestPass123!'
                    )
                    mock_create.return_value = mock_user
                    
                    with patch('rest_framework_simplejwt.tokens.RefreshToken') as mock_refresh:
                        mock_refresh_token = Mock()
                        mock_refresh_token.access_token = {'exp': 1234567890}
                        mock_refresh_token.__str__ = Mock(return_value='refresh_token')
                        mock_refresh.for_user.return_value = mock_refresh_token
                        
                        result = service.verify_pre_registration_and_create_user(token)
                        
                        assert result.success
                        assert 'user' in result.data
    
    def test_validate_user_registration_data_passwords_dont_match(self, service):
        """Test validating user registration data with mismatched passwords."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!'
        }
        
        result = service._validate_user_registration_data(user_data)
        
        assert result is not None
        assert not result.success
    
    def test_validate_user_registration_data_duplicate_email(self, service):
        """Test validating user registration data with duplicate email."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='TestPass123!'
        )
        
        user_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_user_registration_data(user_data)
            
            assert result is not None
            assert not result.success
    
    def test_create_user_from_data_with_username(self, service):
        """Test creating user from data with username."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user = service._create_user_from_data(user_data, use_email_as_username=False)
        
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
    
    def test_create_user_from_data_with_email_as_username(self, service):
        """Test creating user from data with email as username."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user = service._create_user_from_data(user_data, use_email_as_username=True)
        
        assert user.username == 'newuser@example.com'
        assert user.email == 'newuser@example.com'
    
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
    
    def test_register_alias(self, service):
        """Test register alias method."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch.object(service, 'register_user') as mock_register:
            mock_register.return_value = ServiceResult.success()
            
            result = service.register(user_data)
            
            mock_register.assert_called_once_with(user_data, None)

