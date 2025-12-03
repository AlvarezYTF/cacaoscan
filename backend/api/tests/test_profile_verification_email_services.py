"""
Tests for ProfileService, VerificationService, and EmailService.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User

from api.services.auth.profile_service import ProfileService
from api.services.auth.verification_service import VerificationService
from api.services.email.email_service import EmailService, EmailNotificationService


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.mark.django_db
class TestProfileService:
    """Tests for ProfileService."""

    def test_get_user_profile_success(self, user):
        """Test getting user profile successfully."""
        service = ProfileService()
        
        with patch('api.services.auth.profile_service.get_models_safely') as mock_get_models:
            # Mock UserProfile model
            mock_profile = MagicMock()
            mock_profile.phone_number = '1234567890'
            mock_profile.region = 'Test Region'
            mock_profile.municipality = 'Test Municipality'
            mock_profile.farm_name = 'Test Farm'
            mock_profile.years_experience = 5
            mock_profile.farm_size_hectares = 10.5
            mock_profile.preferred_language = 'es'
            mock_profile.email_notifications = True
            mock_profile.role = 'farmer'
            
            mock_user_profile_model = MagicMock()
            mock_user_profile_model.DoesNotExist = type('DoesNotExist', (Exception,), {})
            
            # Mock user.profile access
            def get_profile():
                return mock_profile
            
            user.profile = property(lambda self: get_profile())
            
            mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
            
            result = service.get_user_profile(user)
        
        assert result.success is True
        assert result.data['username'] == 'testuser'
        assert result.data['email'] == 'test@example.com'
        assert 'phone_number' in result.data

    def test_get_user_profile_creates_if_not_exists(self, user):
        """Test that profile is created if it doesn't exist."""
        service = ProfileService()
        
        with patch('api.services.auth.profile_service.get_models_safely') as mock_get_models:
            mock_user_profile_model = MagicMock()
            mock_user_profile_model.DoesNotExist = type('DoesNotExist', (Exception,), {})
            
            # Simulate profile doesn't exist
            def get_profile():
                raise mock_user_profile_model.DoesNotExist()
            
            user.profile = property(lambda self: get_profile())
            
            mock_profile_instance = MagicMock()
            mock_profile_instance.phone_number = None
            mock_profile_instance.region = None
            mock_profile_instance.municipality = None
            mock_profile_instance.farm_name = None
            mock_profile_instance.years_experience = 0
            mock_profile_instance.farm_size_hectares = None
            mock_profile_instance.preferred_language = 'es'
            mock_profile_instance.email_notifications = True
            mock_profile_instance.role = 'farmer'
            
            mock_user_profile_model.objects.create.return_value = mock_profile_instance
            mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
            
            result = service.get_user_profile(user)
        
        assert result.success is True

    def test_update_user_profile_success(self, user):
        """Test updating user profile successfully."""
        service = ProfileService()
        
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '9876543210'
        }
        
        with patch('api.services.auth.profile_service.get_models_safely') as mock_get_models:
            mock_profile = MagicMock()
            mock_user_profile_model = MagicMock()
            mock_user_profile_model.objects.get_or_create.return_value = (mock_profile, True)
            mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
            
            result = service.update_user_profile(user, profile_data)
        
        assert result.success is True
        assert result.data['first_name'] == 'Updated'
        assert result.data['last_name'] == 'Name'

    def test_update_user_profile_invalid_field(self, user):
        """Test updating profile with invalid field."""
        service = ProfileService()
        
        profile_data = {
            'invalid_field': 'value'
        }
        
        result = service.update_user_profile(user, profile_data)
        
        assert result.success is False
        assert 'no permitido' in str(result.error).lower() or 'not allowed' in str(result.error).lower()

    def test_update_user_profile_duplicate_email(self, user):
        """Test updating profile with duplicate email."""
        service = ProfileService()
        
        # Create another user with the email
        User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        profile_data = {
            'email': 'other@example.com'
        }
        
        result = service.update_user_profile(user, profile_data)
        
        assert result.success is False
        assert 'email' in str(result.error).lower()

    def test_check_email_verified(self, user):
        """Test checking if email is verified."""
        service = ProfileService()
        
        # Mock user with email token
        mock_token = MagicMock()
        mock_token.is_verified = True
        user.auth_email_token = mock_token
        
        result = service._check_email_verified(user)
        
        assert result is True

    def test_check_email_verified_no_token(self, user):
        """Test checking email verified when no token exists."""
        service = ProfileService()
        
        result = service._check_email_verified(user)
        
        # Should default to is_active
        assert result == user.is_active


@pytest.mark.django_db
class TestVerificationService:
    """Tests for VerificationService."""

    def test_verify_email_success(self, user):
        """Test verifying email successfully."""
        service = VerificationService()
        
        with patch('api.services.auth.verification_service.get_models_safely') as mock_get_models:
            mock_token = MagicMock()
            mock_token.is_expired.return_value = False
            mock_token.user = user
            mock_token.verify = MagicMock()
            
            mock_email_verification_model = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.first.return_value = mock_token
            mock_email_verification_model.objects.filter.return_value = mock_queryset
            mock_get_models.return_value = {'EmailVerificationToken': mock_email_verification_model}
            
            # Patch EmailVerificationToken in the module namespace
            import api.services.auth.verification_service as verification_module
            verification_module.EmailVerificationToken = mock_email_verification_model
            
            result = service.verify_email('valid_token')
        
        assert result.success is True
        assert result.data['user']['id'] == user.id
        mock_token.verify.assert_called_once()

    def test_verify_email_invalid_token(self):
        """Test verifying email with invalid token."""
        service = VerificationService()
        
        with patch('api.services.auth.verification_service.get_models_safely') as mock_get_models:
            mock_email_verification_model = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.first.return_value = None
            mock_email_verification_model.objects.filter.return_value = mock_queryset
            mock_get_models.return_value = {'EmailVerificationToken': mock_email_verification_model}
            
            import api.services.auth.verification_service as verification_module
            verification_module.EmailVerificationToken = mock_email_verification_model
            
            result = service.verify_email('invalid_token')
        
        assert result.success is False
        assert 'inválido' in str(result.error).lower() or 'invalid' in str(result.error).lower()

    def test_verify_email_expired_token(self, user):
        """Test verifying email with expired token."""
        service = VerificationService()
        
        with patch('api.services.auth.verification_service.get_models_safely') as mock_get_models:
            mock_token = MagicMock()
            mock_token.is_expired.return_value = True
            mock_token.user = user
            
            mock_email_verification_model = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.first.return_value = mock_token
            mock_email_verification_model.objects.filter.return_value = mock_queryset
            mock_get_models.return_value = {'EmailVerificationToken': mock_email_verification_model}
            
            import api.services.auth.verification_service as verification_module
            verification_module.EmailVerificationToken = mock_email_verification_model
            
            result = service.verify_email('expired_token')
        
        assert result.success is False
        assert 'expirado' in str(result.error).lower() or 'expired' in str(result.error).lower()

    def test_resend_verification_success(self, user):
        """Test resending verification successfully."""
        service = VerificationService()
        
        with patch('api.services.auth.verification_service.get_models_safely') as mock_get_models:
            mock_token = MagicMock()
            mock_token.token = 'new_token'
            mock_token.expires_at.isoformat.return_value = '2024-01-01T00:00:00'
            
            mock_email_verification_model = MagicMock()
            mock_email_verification_model.create_for_user.return_value = mock_token
            mock_get_models.return_value = {'EmailVerificationToken': mock_email_verification_model}
            
            result = service.resend_verification(user.email)
        
        assert result.success is True
        assert 'token' in result.data

    def test_resend_verification_user_not_found(self):
        """Test resending verification for non-existent user."""
        service = VerificationService()
        
        result = service.resend_verification('nonexistent@example.com')
        
        # For security, should return success even if user doesn't exist
        assert result.success is True

    def test_resend_verification_empty_email(self):
        """Test resending verification with empty email."""
        service = VerificationService()
        
        result = service.resend_verification('')
        
        assert result.success is False
        assert 'email' in str(result.error).lower() or 'requerido' in str(result.error).lower()


@pytest.mark.django_db
class TestEmailService:
    """Tests for EmailService."""

    def test_send_email_success_smtp(self):
        """Test sending email successfully via SMTP."""
        service = EmailService()
        
        with patch.object(service, '_send_with_smtp') as mock_smtp:
            mock_smtp.return_value = {
                'success': True,
                'backend_used': 'smtp',
                'recipients': ['test@example.com']
            }
            
            result = service.send_email(
                to_emails='test@example.com',
                subject='Test Subject',
                html_content='<p>Test</p>',
                text_content='Test'
            )
        
        assert result['success'] is True
        assert result['backend_used'] == 'smtp'

    def test_send_email_success_sendgrid(self):
        """Test sending email successfully via SendGrid."""
        service = EmailService()
        service.sendgrid_client = MagicMock()
        
        with patch.object(service, '_send_with_sendgrid') as mock_sendgrid:
            mock_sendgrid.return_value = {
                'success': True,
                'backend_used': 'sendgrid',
                'recipients': ['test@example.com']
            }
            
            result = service.send_email(
                to_emails='test@example.com',
                subject='Test Subject',
                html_content='<p>Test</p>',
                use_sendgrid=True
            )
        
        assert result['success'] is True
        assert result['backend_used'] == 'sendgrid'

    def test_send_email_no_backends(self):
        """Test sending email when no backends are configured."""
        service = EmailService()
        service.smtp_backend = None
        service.sendgrid_client = None
        
        result = service.send_email(
            to_emails='test@example.com',
            subject='Test Subject',
            html_content='<p>Test</p>'
        )
        
        assert result['success'] is False
        assert 'no hay backends' in result['error'].lower() or 'no backends' in result['error'].lower()

    def test_send_email_with_template(self):
        """Test sending email with template."""
        service = EmailService()
        
        with patch.object(service, '_render_template') as mock_render:
            with patch.object(service, '_send_with_smtp') as mock_smtp:
                mock_render.return_value = ('<p>HTML</p>', 'Text')
                mock_smtp.return_value = {'success': True, 'backend_used': 'smtp'}
                
                result = service.send_email(
                    to_emails='test@example.com',
                    subject='Test',
                    template_name='welcome',
                    context={'user_name': 'Test User'}
                )
        
        assert result['success'] is True
        mock_render.assert_called_once()

    def test_send_email_multiple_recipients(self):
        """Test sending email to multiple recipients."""
        service = EmailService()
        
        with patch.object(service, '_send_with_smtp') as mock_smtp:
            mock_smtp.return_value = {
                'success': True,
                'backend_used': 'smtp',
                'recipients': ['test1@example.com', 'test2@example.com']
            }
            
            result = service.send_email(
                to_emails=['test1@example.com', 'test2@example.com'],
                subject='Test Subject',
                html_content='<p>Test</p>'
            )
        
        assert result['success'] is True

    def test_render_template_success(self):
        """Test rendering email template successfully."""
        service = EmailService()
        
        with patch('api.services.email.email_service.render_to_string') as mock_render:
            mock_render.return_value = '<p>HTML Content</p>'
            
            html, text = service._render_template('welcome', {'user_name': 'Test'})
        
        assert html == '<p>HTML Content</p>'
        assert text is not None

    def test_render_template_text_fallback(self):
        """Test rendering template with text fallback."""
        service = EmailService()
        
        with patch('api.services.email.email_service.render_to_string') as mock_render:
            # HTML template exists, text doesn't
            def render_side_effect(template, context):
                if 'html' in template:
                    return '<p>HTML</p>'
                raise Exception("Template not found")
            
            mock_render.side_effect = render_side_effect
            
            html, text = service._render_template('welcome', {'user_name': 'Test'})
        
        assert html == '<p>HTML</p>'
        assert text is not None  # Should be generated from HTML


@pytest.mark.django_db
class TestEmailNotificationService:
    """Tests for EmailNotificationService."""

    def test_send_notification_email_success(self):
        """Test sending notification email successfully."""
        notification_service = EmailNotificationService()
        
        with patch.object(notification_service.email_service, 'send_email') as mock_send:
            with patch('api.services.email.email_service.settings') as mock_settings:
                mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
                mock_settings.EMAIL_NOTIFICATION_TYPES = ['welcome']
                mock_settings.SENDGRID_API_KEY = None
                
                mock_send.return_value = {
                    'success': True,
                    'backend_used': 'smtp'
                }
                
                result = notification_service.send_notification_email(
                    user_email='test@example.com',
                    notification_type='welcome',
                    context={'user_name': 'Test User'}
                )
        
        assert result['success'] is True

    def test_send_notification_email_disabled(self):
        """Test sending notification when disabled."""
        notification_service = EmailNotificationService()
        
        with patch('api.services.email.email_service.settings') as mock_settings:
            mock_settings.EMAIL_NOTIFICATIONS_ENABLED = False
            
            result = notification_service.send_notification_email(
                user_email='test@example.com',
                notification_type='welcome',
                context={}
            )
        
        assert result['success'] is False
        assert 'deshabilitadas' in result['error'].lower() or 'disabled' in result['error'].lower()

    def test_send_notification_email_unsupported_type(self):
        """Test sending notification with unsupported type."""
        notification_service = EmailNotificationService()
        
        with patch('api.services.email.email_service.settings') as mock_settings:
            mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
            mock_settings.EMAIL_NOTIFICATION_TYPES = ['welcome']
            
            result = notification_service.send_notification_email(
                user_email='test@example.com',
                notification_type='unsupported',
                context={}
            )
        
        assert result['success'] is False
        assert 'no soportado' in result['error'].lower() or 'not supported' in result['error'].lower()

