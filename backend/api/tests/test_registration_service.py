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
    
    def test_register_user_success(self, service):
        """Test successful user registration."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        user_data = {
            'username': f'newuser_{unique_id}',
            'email': email,
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data') as mock_create:
                mock_user = User.objects.create_user(
                    username=f'newuser_{unique_id}',
                    email=email,
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
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'username': f'newuser_{unique_id}',
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch.object(service, '_validate_user_registration_data') as mock_validate:
            mock_validate.return_value = ServiceResult.validation_error("Passwords don't match")
            
            result = service.register_user(user_data)
            
            assert not result.success
    
    def test_register_user_with_email_verification(self, service):
        """Test user registration with email verification."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        user_data = {
            'email': email,
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data') as mock_create:
                mock_user = User.objects.create_user(
                    username=email,
                    email=email,
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
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_pre_registration_data(user_data)
            
            assert result.success
    
    def test_validate_pre_registration_data_missing_fields(self, service):
        """Test validating pre-registration data with missing fields."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {'email': f'newuser_{unique_id}@example.com'}
        
        result = service._validate_pre_registration_data(user_data)
        
        assert not result.success
    
    def test_validate_pre_registration_data_duplicate_email(self, service):
        """Test validating pre-registration data with duplicate email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'existing_{unique_id}@example.com'
        User.objects.create_user(
            username=f'existing_{unique_id}',
            email=email,
            password='TestPass123!'
        )
        
        user_data = {
            'email': email,
            'password': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_pre_registration_data(user_data)
            
            assert not result.success
    
    def test_pre_register_user_success(self, service):
        """Test successful pre-registration."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
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
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            email = f'newuser_{unique_id}@example.com'
            mock_pending_instance.data = {
                'email': email,
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
                        username=email,
                        email=email,
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
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!'
        }
        
        result = service._validate_user_registration_data(user_data)
        
        assert result is not None
        assert not result.success
    
    def test_validate_user_registration_data_duplicate_email(self, service):
        """Test validating user registration data with duplicate email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'existing_{unique_id}@example.com'
        User.objects.create_user(
            username=f'existing_{unique_id}',
            email=email,
            password='TestPass123!'
        )
        
        user_data = {
            'email': email,
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_user_registration_data(user_data)
            
            assert result is not None
            assert not result.success
    
    def test_create_user_from_data_with_username(self, service):
        """Test creating user from data with username."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        user_data = {
            'username': f'newuser_{unique_id}',
            'email': email,
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user = service._create_user_from_data(user_data, use_email_as_username=False)
        
        assert user.username == f'newuser_{unique_id}'
        assert user.email == email
    
    def test_create_user_from_data_with_email_as_username(self, service):
        """Test creating user from data with email as username."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        user_data = {
            'email': email,
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user = service._create_user_from_data(user_data, use_email_as_username=True)
        
        assert user.username == email
        assert user.email == email
    
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
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'username': f'newuser_{unique_id}',
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch.object(service, 'register_user') as mock_register:
            mock_register.return_value = ServiceResult.success()
            
            result = service.register(user_data)
            
            mock_register.assert_called_once_with(user_data, None)
    
    def test_register_user_exception(self, service):
        """Test register_user with exception."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'username': f'newuser_{unique_id}',
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data', side_effect=Exception("Error")):
                result = service.register_user(user_data)
                assert not result.success
    
    def test_register_user_with_email_verification_email_error(self, service):
        """Test register_user_with_email_verification with email error."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        user_data = {
            'email': email,
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data') as mock_create:
                mock_user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='TestPass123!'
                )
                mock_create.return_value = mock_user
                
                with patch('api.utils.model_imports.get_models_safely') as mock_models:
                    mock_token = Mock()
                    mock_token.token = 'test-token'
                    mock_token_model = Mock()
                    mock_token_model.create_for_user.return_value = mock_token
                    mock_models.return_value = {'EmailVerificationToken': mock_token_model}
                    
                    with patch.object(service, '_send_verification_email', return_value={'success': False, 'error': 'Email error'}):
                        result = service.register_user_with_email_verification(user_data)
                        
                        assert result.success
                        assert 'verification_token' in result.data
    
    def test_register_user_with_email_verification_exception(self, service):
        """Test register_user_with_email_verification with exception."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch.object(service, '_validate_user_registration_data', return_value=None):
            with patch.object(service, '_create_user_from_data', side_effect=Exception("Error")):
                result = service.register_user_with_email_verification(user_data)
                assert not result.success
    
    def test_validate_pre_registration_data_password_error(self, service):
        """Test _validate_pre_registration_data with password error."""
        from core.utils import PasswordValidationError
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'weak'
        }
        
        with patch('core.utils.validate_password_strength', side_effect=PasswordValidationError("Weak password")):
            result = service._validate_pre_registration_data(user_data)
            assert not result.success
    
    def test_validate_pre_registration_data_password_generic_error(self, service):
        """Test _validate_pre_registration_data with generic password error."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'weak'
        }
        
        with patch('core.utils.validate_password_strength', side_effect=Exception("Generic error")):
            with pytest.raises(Exception):
                service._validate_pre_registration_data(user_data)
    
    def test_handle_existing_pending_registration_not_expired(self, service):
        """Test _handle_existing_pending_registration with not expired."""
        from personas.models import PendingRegistration
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'test_{unique_id}@example.com'
        
        pending_reg = Mock()
        pending_reg.is_expired.return_value = False
        
        with patch.object(service, '_send_pre_registration_verification_email', return_value={'success': True}):
            result = service._handle_existing_pending_registration(pending_reg, email)
            assert result is not None
            assert result.success
    
    def test_handle_existing_pending_registration_expired(self, service):
        """Test _handle_existing_pending_registration with expired."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'test_{unique_id}@example.com'
        pending_reg = Mock()
        pending_reg.is_expired.return_value = True
        pending_reg.delete = Mock()
        
        result = service._handle_existing_pending_registration(pending_reg, email)
        assert result is None
        pending_reg.delete.assert_called_once()
    
    def test_pre_register_user_existing_not_expired(self, service):
        """Test pre_register_user with existing not expired."""
        from personas.models import PendingRegistration
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!'
        }
        
        mock_pending = Mock()
        mock_pending.is_expired.return_value = False
        mock_pending.delete = Mock()
        
        with patch.object(service, '_validate_pre_registration_data', return_value=None):
            with patch('personas.models.PendingRegistration') as mock_pending_class:
                mock_pending_class.objects.filter.return_value.first.return_value = mock_pending
                
                with patch.object(service, '_send_pre_registration_verification_email', return_value={'success': True}):
                    result = service.pre_register_user(user_data)
                    assert result.success
    
    def test_pre_register_user_email_error(self, service):
        """Test pre_register_user with email error."""
        from personas.models import PendingRegistration
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!'
        }
        
        mock_pending = Mock()
        mock_pending.delete = Mock()
        
        with patch.object(service, '_validate_pre_registration_data', return_value=None):
            with patch('personas.models.PendingRegistration') as mock_pending_class:
                mock_pending_class.objects.filter.return_value.first.return_value = None
                mock_pending_class.objects.create.return_value = mock_pending
                
                with patch.object(service, '_send_pre_registration_verification_email', return_value={'success': False, 'error': 'Email error'}):
                    result = service.pre_register_user(user_data)
                    assert not result.success
                    mock_pending.delete.assert_called_once()
    
    def test_pre_register_user_exception(self, service):
        """Test pre_register_user with exception."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!'
        }
        
        with patch.object(service, '_validate_pre_registration_data', return_value=None):
            with patch('personas.models.PendingRegistration.objects.create', side_effect=Exception("Error")):
                result = service.pre_register_user(user_data)
                assert not result.success
    
    def test_verify_pre_registration_and_create_user_invalid_token_format(self, service):
        """Test verify_pre_registration_and_create_user with invalid token format."""
        result = service.verify_pre_registration_and_create_user('invalid-token')
        assert not result.success
    
    def test_verify_pre_registration_and_create_user_token_not_found(self, service):
        """Test verify_pre_registration_and_create_user with token not found."""
        import uuid
        from personas.models import PendingRegistration
        
        token = str(uuid.uuid4())
        
        with patch('personas.models.PendingRegistration') as mock_pending:
            class MockDoesNotExist(Exception):
                pass
            mock_pending.DoesNotExist = MockDoesNotExist
            mock_pending.objects.get.side_effect = MockDoesNotExist()
            
            result = service.verify_pre_registration_and_create_user(token)
            assert not result.success
    
    def test_verify_pre_registration_and_create_user_already_verified(self, service):
        """Test verify_pre_registration_and_create_user with already verified."""
        import uuid
        from personas.models import PendingRegistration
        
        token = str(uuid.uuid4())
        
        mock_pending = Mock()
        mock_pending.is_verified = True
        mock_pending.is_expired.return_value = False
        
        with patch('personas.models.PendingRegistration') as mock_pending_class:
            mock_pending_class.objects.get.return_value = mock_pending
            
            result = service.verify_pre_registration_and_create_user(token)
            assert not result.success
    
    def test_verify_pre_registration_and_create_user_expired(self, service):
        """Test verify_pre_registration_and_create_user with expired token."""
        import uuid
        from personas.models import PendingRegistration
        
        token = str(uuid.uuid4())
        
        mock_pending = Mock()
        mock_pending.is_verified = False
        mock_pending.is_expired.return_value = True
        mock_pending.delete = Mock()
        
        with patch('personas.models.PendingRegistration') as mock_pending_class:
            mock_pending_class.objects.get.return_value = mock_pending
            
            result = service.verify_pre_registration_and_create_user(token)
            assert not result.success
            mock_pending.delete.assert_called_once()
    
    def test_verify_pre_registration_and_create_user_with_persona_data(self, service):
        """Test verify_pre_registration_and_create_user with persona data."""
        import uuid
        from personas.models import PendingRegistration
        
        token = str(uuid.uuid4())
        
        mock_pending = Mock()
        mock_pending.is_verified = False
        mock_pending.is_expired.return_value = False
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        mock_pending.data = {
            'email': email,
            'password': 'TestPass123!',
            'tipo_documento': 'CC',
            'numero_documento': '1234567890'
        }
        mock_pending.verify = Mock()
        
        with patch('personas.models.PendingRegistration') as mock_pending_class:
            mock_pending_class.objects.get.return_value = mock_pending
            
            with patch('personas.serializers.PersonaRegistroSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_instance.is_valid.return_value = True
                mock_serializer_instance.save.return_value = Mock()
                mock_serializer_class.return_value = mock_serializer_instance
                
                with patch.object(service, '_create_user_from_data') as mock_create:
                    with patch.object(service, 'create_audit_log') as mock_audit:
                        with patch('core.utils.invalidate_system_stats_cache') as mock_cache:
                            mock_user = User.objects.create_user(
                                username=email,
                                email=email,
                                password='TestPass123!'
                            )
                            mock_create.return_value = mock_user
                            mock_audit.return_value = None
                            mock_cache.return_value = None
                            
                            result = service.verify_pre_registration_and_create_user(token)
                            assert result.success
    
    def test_verify_pre_registration_and_create_user_persona_error(self, service):
        """Test verify_pre_registration_and_create_user with persona error."""
        import uuid
        from personas.models import PendingRegistration
        
        token = str(uuid.uuid4())
        
        mock_pending = Mock()
        mock_pending.is_verified = False
        mock_pending.is_expired.return_value = False
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        mock_pending.data = {
            'email': email,
            'password': 'TestPass123!',
            'tipo_documento': 'CC',
            'numero_documento': '1234567890'
        }
        mock_pending.verify = Mock()
        
        with patch('personas.models.PendingRegistration') as mock_pending_class:
            mock_pending_class.objects.get.return_value = mock_pending
            
            with patch('personas.serializers.PersonaRegistroSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_instance.is_valid.return_value = False
                mock_serializer_instance.errors = {'error': 'Invalid'}
                mock_serializer_class.return_value = mock_serializer_instance
                
                with patch.object(service, '_create_user_from_data') as mock_create:
                    with patch.object(service, 'create_audit_log') as mock_audit:
                        with patch('core.utils.invalidate_system_stats_cache') as mock_cache:
                            mock_user = User.objects.create_user(
                                username=email,
                                email=email,
                                password='TestPass123!'
                            )
                            mock_create.return_value = mock_user
                            mock_audit.return_value = None
                            mock_cache.return_value = None
                            
                            result = service.verify_pre_registration_and_create_user(token)
                            assert result.success
    
    def test_verify_pre_registration_and_create_user_exception(self, service):
        """Test verify_pre_registration_and_create_user with exception."""
        import uuid
        
        token = str(uuid.uuid4())
        
        with patch('personas.models.PendingRegistration', side_effect=Exception("Error")):
            result = service.verify_pre_registration_and_create_user(token)
            assert not result.success
    
    def test_log_user_registration_with_request(self, service, user):
        """Test _log_user_registration with request."""
        from audit.models import LoginHistory
        
        request = Mock()
        request.META = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'Test Agent'
        }
        
        service._log_user_registration(user, request)
        
        assert LoginHistory.objects.filter(user=user).exists()
    
    @pytest.mark.django_db
    def test_log_user_registration_without_request(self, service, user):
        """Test _log_user_registration without request."""
        from audit.models import LoginHistory
        
        # Clear any existing records first
        LoginHistory.objects.filter(user=user).delete()
        
        # Call the method
        service._log_user_registration(user, None)
        
        # Verify the record was created
        assert LoginHistory.objects.filter(user=user).exists()
    
    def test_log_user_registration_exception(self, service, user):
        """Test _log_user_registration with exception."""
        request = Mock()
        request.META = {}
        
        with patch('audit.models.LoginHistory.objects.create', side_effect=Exception("Error")):
            service._log_user_registration(user, request)
            # Should not raise
    
    def test_send_verification_email_success(self, service, user):
        """Test _send_verification_email with success."""
        mock_token = Mock()
        mock_token.token = 'test-token'
        
        with patch('api.services.email.send_custom_email', return_value={'success': True}):
            result = service._send_verification_email(user, mock_token)
            assert result['success'] is True
    
    def test_send_verification_email_error(self, service, user):
        """Test _send_verification_email with error."""
        mock_token = Mock()
        mock_token.token = 'test-token'
        
        with patch('api.services.email.send_custom_email', side_effect=Exception("Email error")):
            result = service._send_verification_email(user, mock_token)
            assert result['success'] is False
            assert 'error' in result
    
    def test_send_pre_registration_verification_email_with_template(self, service):
        """Test _send_pre_registration_verification_email with template."""
        from personas.models import PendingRegistration
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'test_{unique_id}@example.com'
        
        pending_reg = Mock()
        pending_reg.verification_token = 'test-token'
        pending_reg.email = email
        pending_reg.data = {'first_name': 'Test'}
        
        with patch('django.template.loader.render_to_string', return_value='<html>Test</html>'):
            with patch('api.services.email.send_custom_email', return_value={'success': True}):
                result = service._send_pre_registration_verification_email(pending_reg)
                assert result['success'] is True
    
    def test_send_pre_registration_verification_email_without_template(self, service):
        """Test _send_pre_registration_verification_email without template."""
        from django.template import TemplateDoesNotExist
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'test_{unique_id}@example.com'
        
        pending_reg = Mock()
        pending_reg.verification_token = 'test-token'
        pending_reg.email = email
        pending_reg.data = {}
        
        from django.template import TemplateDoesNotExist
        with patch('django.template.loader.render_to_string', side_effect=TemplateDoesNotExist("Template")):
            with patch('api.services.email.send_custom_email', return_value={'success': True}):
                result = service._send_pre_registration_verification_email(pending_reg)
                assert result['success'] is True
    
    def test_send_pre_registration_verification_email_error(self, service):
        """Test _send_pre_registration_verification_email with error."""
        from django.template import TemplateDoesNotExist
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'test_{unique_id}@example.com'
        
        pending_reg = Mock()
        pending_reg.verification_token = 'test-token'
        pending_reg.email = email
        pending_reg.data = {}
        
        with patch('django.template.loader.render_to_string', side_effect=TemplateDoesNotExist("Template")):
            with patch('api.services.email.send_custom_email', side_effect=Exception("Email error")):
                result = service._send_pre_registration_verification_email(pending_reg)
                assert result['success'] is False
                assert 'error' in result
    
    def test_validate_user_registration_data_duplicate_username(self, service):
        """Test _validate_user_registration_data with duplicate username."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f'existing_{unique_id}'
        User.objects.create_user(
            username=username,
            email=f'existing_{unique_id}@example.com',
            password='TestPass123!'
        )
        
        user_data = {
            'username': username,
            'email': f'newuser_{unique_id}@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        with patch('core.utils.validate_password_strength'):
            result = service._validate_user_registration_data(user_data, check_username=True)
            assert result is not None
            assert not result.success
    
    def test_validate_user_registration_data_password_error(self, service):
        """Test _validate_user_registration_data with password error."""
        from core.utils import PasswordValidationError
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'weak',
            'password_confirm': 'weak'
        }
        
        with patch('core.utils.validate_password_strength', side_effect=PasswordValidationError("Weak password")):
            result = service._validate_user_registration_data(user_data)
            assert result is not None
            assert not result.success
    
    def test_validate_user_registration_data_password_generic_error(self, service):
        """Test _validate_user_registration_data with generic password error."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'email': f'newuser_{unique_id}@example.com',
            'password': 'weak',
            'password_confirm': 'weak'
        }
        
        with patch('core.utils.validate_password_strength', side_effect=Exception("Generic error")):
            with pytest.raises(Exception):
                service._validate_user_registration_data(user_data)
    
    def test_create_user_from_data_with_password_confirm(self, service):
        """Test _create_user_from_data with password_confirm."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f'newuser_{unique_id}@example.com'
        user_data = {
            'email': email,
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user = service._create_user_from_data(user_data, use_email_as_username=True)
        assert user.username == email
        assert user.email == email

