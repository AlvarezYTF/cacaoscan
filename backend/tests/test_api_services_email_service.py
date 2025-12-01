"""
Unit tests for email service module (email_service.py).
Tests email sending functionality with SMTP and SendGrid backends.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.template.loader import render_to_string

from api.services.email.email_service import (
    EmailService,
    EmailNotificationService,
    send_email_notification,
    send_bulk_email_notification,
    send_custom_email,
    _validate_email_address,
    _get_email_subject,
    _render_email_templates,
    _get_smtp_connection,
    _build_email_message,
    _log_email_debug_info,
    _log_email_error
)


@pytest.fixture
def email_service():
    """Create an EmailService instance for testing."""
    return EmailService()


@pytest.fixture
def email_notification_service():
    """Create an EmailNotificationService instance for testing."""
    return EmailNotificationService()


@pytest.fixture
def mock_email_settings(settings):
    """Configure email settings for testing."""
    settings.EMAIL_HOST = 'smtp.example.com'
    settings.EMAIL_PORT = 587
    settings.EMAIL_HOST_USER = 'test@example.com'
    settings.EMAIL_HOST_PASSWORD = 'testpass'
    settings.EMAIL_USE_TLS = True
    settings.EMAIL_USE_SSL = False
    settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
    settings.EMAIL_NOTIFICATIONS_ENABLED = True
    settings.EMAIL_NOTIFICATION_TYPES = ['welcome', 'reset_request', 'analysis_complete']
    settings.EMAIL_BATCH_SIZE = 10
    settings.FRONTEND_URL = 'https://example.com'
    return settings


class TestEmailService:
    """Tests for EmailService class."""
    
    def test_service_initialization(self, email_service, mock_email_settings):
        """Test EmailService initialization."""
        assert email_service is not None
    
    @patch('api.services.email.email_service.EmailBackend')
    def test_initialize_backends_smtp(self, mock_backend, mock_email_settings):
        """Test backend initialization with SMTP."""
        service = EmailService()
        # Backend should be initialized if credentials are present
        assert service.smtp_backend is not None or service.sendgrid_client is None
    
    @patch('api.services.email.email_service.sendgrid')
    def test_initialize_backends_sendgrid(self, mock_sendgrid, mock_email_settings):
        """Test backend initialization with SendGrid."""
        mock_email_settings.SENDGRID_API_KEY = 'test_api_key'
        service = EmailService()
        # Should attempt to initialize SendGrid if API key is present
        assert service is not None
    
    @patch('api.services.email.email_service.get_connection')
    @patch('api.services.email.email_service.EmailMultiAlternatives')
    def test_send_email_smtp_success(self, mock_email_class, mock_get_connection, 
                                     email_service, mock_email_settings):
        """Test sending email via SMTP successfully."""
        mock_connection = Mock()
        mock_connection.send_messages.return_value = 1
        mock_get_connection.return_value = mock_connection
        
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        result = email_service.send_email(
            to_emails='test@example.com',
            subject='Test Subject',
            html_content='<p>Test HTML</p>',
            text_content='Test Text',
            use_sendgrid=False
        )
        
        assert result['success'] is True
        assert result['backend_used'] == 'smtp'
    
    @patch('api.services.email.email_service.sendgrid')
    def test_send_email_sendgrid_success(self, mock_sendgrid_module, email_service, mock_email_settings):
        """Test sending email via SendGrid successfully."""
        mock_email_settings.SENDGRID_API_KEY = 'test_api_key'
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client.send.return_value = mock_response
        mock_sendgrid_module.SendGridAPIClient.return_value = mock_client
        
        service = EmailService()
        service.sendgrid_client = mock_client
        
        result = service.send_email(
            to_emails='test@example.com',
            subject='Test Subject',
            html_content='<p>Test HTML</p>',
            text_content='Test Text',
            use_sendgrid=True
        )
        
        assert result['success'] is True
        assert result['backend_used'] == 'sendgrid'
    
    def test_send_email_no_backends(self, email_service, mock_email_settings):
        """Test sending email when no backends are configured."""
        email_service.smtp_backend = None
        email_service.sendgrid_client = None
        
        result = email_service.send_email(
            to_emails='test@example.com',
            subject='Test Subject',
            html_content='<p>Test HTML</p>'
        )
        
        assert result['success'] is False
        assert 'No hay backends' in result['error']
    
    def test_send_email_with_template(self, email_service, mock_email_settings):
        """Test sending email with template rendering."""
        with patch.object(email_service, '_render_template', return_value=('<p>HTML</p>', 'Text')):
            with patch.object(email_service, '_send_with_smtp', return_value={'success': True, 'backend_used': 'smtp'}):
                result = email_service.send_email(
                    to_emails='test@example.com',
                    subject='Test Subject',
                    template_name='welcome',
                    context={'user_name': 'Test User'}
                )
                
                assert result['success'] is True
    
    def test_send_email_multiple_recipients(self, email_service, mock_email_settings):
        """Test sending email to multiple recipients."""
        with patch.object(email_service, '_send_with_smtp', return_value={'success': True, 'backend_used': 'smtp'}):
            result = email_service.send_email(
                to_emails=['test1@example.com', 'test2@example.com'],
                subject='Test Subject',
                html_content='<p>Test</p>'
            )
            
            assert result['success'] is True
    
    def test_render_template_success(self, email_service, mock_email_settings):
        """Test template rendering."""
        with patch('api.services.email.email_service.render_to_string') as mock_render:
            mock_render.side_effect = ['<p>HTML</p>', 'Text content']
            
            html, text = email_service._render_template('welcome', {'user_name': 'Test'})
            
            assert html == '<p>HTML</p>'
            assert text == 'Text content'
            assert mock_render.call_count == 2
    
    def test_render_template_text_fallback(self, email_service, mock_email_settings):
        """Test template rendering with text template fallback."""
        from django.template import TemplateDoesNotExist
        
        with patch('api.services.email.email_service.render_to_string') as mock_render:
            mock_render.side_effect = ['<p>HTML</p>', TemplateDoesNotExist('template')]
            
            html, text = email_service._render_template('welcome', {'user_name': 'Test'})
            
            assert html == '<p>HTML</p>'
            assert text == 'HTML'  # Should strip tags from HTML
    
    @patch('api.services.email.email_service.get_connection')
    @patch('api.services.email.email_service.EmailMultiAlternatives')
    def test_send_with_smtp_with_attachments(self, mock_email_class, mock_get_connection,
                                             email_service, mock_email_settings):
        """Test sending email via SMTP with attachments."""
        mock_connection = Mock()
        mock_connection.send_messages.return_value = 1
        mock_get_connection.return_value = mock_connection
        
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        attachments = [
            {
                'filename': 'test.pdf',
                'content': b'PDF content',
                'content_type': 'application/pdf'
            }
        ]
        
        result = email_service._send_with_smtp(
            to_emails=['test@example.com'],
            subject='Test Subject',
            html_content='<p>Test</p>',
            text_content='Test',
            from_email='sender@example.com',
            attachments=attachments
        )
        
        assert result['success'] is True
        assert mock_email.attach.called or mock_email.attach_alternative.called
    
    def test_send_with_smtp_error(self, email_service, mock_email_settings):
        """Test SMTP sending with error."""
        with patch('api.services.email.email_service.get_connection') as mock_get_conn:
            mock_connection = Mock()
            mock_connection.send_messages.side_effect = Exception("SMTP error")
            mock_get_conn.return_value = mock_connection
            
            result = email_service._send_with_smtp(
                to_emails=['test@example.com'],
                subject='Test',
                html_content='<p>Test</p>',
                text_content='Test',
                from_email='sender@example.com'
            )
            
            assert result['success'] is False
            assert 'error' in result


class TestEmailNotificationService:
    """Tests for EmailNotificationService class."""
    
    def test_service_initialization(self, email_notification_service, mock_email_settings):
        """Test EmailNotificationService initialization."""
        assert email_notification_service is not None
        assert email_notification_service.email_service is not None
    
    @patch('api.services.email.email_service.settings.EMAIL_NOTIFICATIONS_ENABLED', False)
    def test_send_notification_email_disabled(self, email_notification_service):
        """Test sending notification when email notifications are disabled."""
        result = email_notification_service.send_notification_email(
            user_email='test@example.com',
            notification_type='welcome',
            context={'user_name': 'Test'}
        )
        
        assert result['success'] is False
        assert result['skipped'] is True
    
    def test_send_notification_email_unsupported_type(self, email_notification_service, mock_email_settings):
        """Test sending notification with unsupported type."""
        result = email_notification_service.send_notification_email(
            user_email='test@example.com',
            notification_type='unsupported_type',
            context={}
        )
        
        assert result['success'] is False
        assert result['skipped'] is True
    
    @patch.object(EmailNotificationService, 'email_service')
    def test_send_notification_email_success(self, mock_email_service, email_notification_service, mock_email_settings):
        """Test successful notification email sending."""
        mock_email_service.send_email.return_value = {'success': True, 'backend_used': 'smtp'}
        
        result = email_notification_service.send_notification_email(
            user_email='test@example.com',
            notification_type='welcome',
            context={'user_name': 'Test User'}
        )
        
        assert result['success'] is True
        mock_email_service.send_email.assert_called_once()
    
    def test_get_default_subject(self, email_notification_service, mock_email_settings):
        """Test getting default subject for notification type."""
        subject = email_notification_service._get_default_subject(
            'welcome',
            {'user_name': 'Test User'}
        )
        
        assert 'Bienvenido' in subject or 'CacaoScan' in subject
    
    @patch.object(EmailNotificationService, 'send_notification_email')
    def test_send_bulk_notification_success(self, mock_send, email_notification_service, mock_email_settings):
        """Test successful bulk notification sending."""
        mock_send.return_value = {'success': True}
        
        emails = [f'test{i}@example.com' for i in range(5)]
        result = email_notification_service.send_bulk_notification(
            user_emails=emails,
            notification_type='welcome',
            context={'user_name': 'Test'}
        )
        
        assert result['total_emails'] == 5
        assert result['successful'] == 5
        assert result['failed'] == 0
        assert mock_send.call_count == 5
    
    @patch.object(EmailNotificationService, 'send_notification_email')
    def test_send_bulk_notification_partial_failure(self, mock_send, email_notification_service, mock_email_settings):
        """Test bulk notification with partial failures."""
        mock_send.side_effect = [
            {'success': True},
            {'success': False, 'error': 'Error'},
            {'success': True},
            {'success': False, 'error': 'Error'},
            {'success': True}
        ]
        
        emails = [f'test{i}@example.com' for i in range(5)]
        result = email_notification_service.send_bulk_notification(
            user_emails=emails,
            notification_type='welcome',
            context={}
        )
        
        assert result['total_emails'] == 5
        assert result['successful'] == 3
        assert result['failed'] == 2
        assert len(result['errors']) == 2


class TestEmailHelperFunctions:
    """Tests for email helper functions."""
    
    def test_validate_email_address_valid(self):
        """Test email validation with valid email."""
        assert _validate_email_address('test@example.com') is True
    
    def test_validate_email_address_invalid(self):
        """Test email validation with invalid email."""
        assert _validate_email_address('invalid_email') is False
        assert _validate_email_address('') is False
        assert _validate_email_address(None) is False
    
    @patch('api.services.email.email_service.email_notification_service')
    def test_get_email_subject_default(self, mock_service, mock_email_settings):
        """Test getting email subject with default."""
        mock_service._get_default_subject.return_value = 'Default Subject'
        
        subject = _get_email_subject('welcome', {'user_name': 'Test'})
        
        assert subject == 'Default Subject'
    
    def test_get_email_subject_override(self, mock_email_settings):
        """Test getting email subject with override."""
        subject = _get_email_subject('welcome', {}, subject_override='Custom Subject')
        
        assert subject == 'Custom Subject'
    
    @patch('api.services.email.email_service.render_to_string')
    def test_render_email_templates_success(self, mock_render, mock_email_settings):
        """Test rendering email templates."""
        mock_render.side_effect = ['<p>HTML</p>', 'Text content']
        
        html, text = _render_email_templates('welcome', {'user_name': 'Test'})
        
        assert html == '<p>HTML</p>'
        assert text == 'Text content'
    
    @patch('api.services.email.email_service.get_connection')
    def test_get_smtp_connection(self, mock_get_conn, mock_email_settings):
        """Test getting SMTP connection."""
        mock_conn = Mock()
        mock_get_conn.return_value = mock_conn
        
        connection = _get_smtp_connection()
        
        assert connection is not None
        mock_get_conn.assert_called_once()
    
    @patch('api.services.email.email_service.get_connection')
    def test_build_email_message(self, mock_get_conn, mock_email_settings):
        """Test building email message."""
        mock_conn = Mock()
        mock_get_conn.return_value = mock_conn
        
        email = _build_email_message(
            user_email='test@example.com',
            subject='Test Subject',
            text_content='Text',
            html_content='<p>HTML</p>',
            connection=mock_conn
        )
        
        assert isinstance(email, EmailMultiAlternatives)
        assert email.subject == 'Test Subject'
    
    def test_log_email_debug_info(self, mock_email_settings):
        """Test logging email debug info."""
        with patch('api.services.email.email_service.logger') as mock_logger:
            _log_email_debug_info(
                user_email='test@example.com',
                notification_type='welcome',
                subject='Test Subject',
                context={'key': 'value'}
            )
            
            assert mock_logger.info.call_count > 0
    
    def test_log_email_error(self, mock_email_settings):
        """Test logging email error."""
        with patch('api.services.email.email_service.logger') as mock_logger:
            error = Exception("Test error")
            _log_email_error(error, 'test@example.com')
            
            assert mock_logger.error.call_count > 0


class TestSendEmailNotificationFunction:
    """Tests for send_email_notification function."""
    
    @patch('api.services.email.email_service._get_smtp_connection')
    @patch('api.services.email.email_service._render_email_templates')
    @patch('api.services.email.email_service._build_email_message')
    def test_send_email_notification_success(self, mock_build, mock_render, mock_conn, mock_email_settings):
        """Test successful email notification sending."""
        mock_render.return_value = ('<p>HTML</p>', 'Text')
        mock_connection = Mock()
        mock_conn.return_value = mock_connection
        
        mock_email = Mock()
        mock_email.send.return_value = 1
        mock_build.return_value = mock_email
        
        result = send_email_notification(
            user_email='test@example.com',
            notification_type='welcome',
            context={'user_name': 'Test'}
        )
        
        assert result['success'] is True
        assert 'sent_to' in result
    
    def test_send_email_notification_invalid_email(self, mock_email_settings):
        """Test sending notification with invalid email."""
        result = send_email_notification(
            user_email='invalid_email',
            notification_type='welcome',
            context={}
        )
        
        assert result['success'] is False
        assert 'inválido' in result['error'] or 'Correo inválido' in result['error']
    
    @patch('api.services.email.email_service._render_email_templates')
    def test_send_email_notification_template_error(self, mock_render, mock_email_settings):
        """Test sending notification with template rendering error."""
        mock_render.side_effect = Exception("Template error")
        
        result = send_email_notification(
            user_email='test@example.com',
            notification_type='welcome',
            context={}
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('api.services.email.email_service._get_smtp_connection')
    @patch('api.services.email.email_service._render_email_templates')
    @patch('api.services.email.email_service._build_email_message')
    def test_send_email_notification_send_error(self, mock_build, mock_render, mock_conn, mock_email_settings):
        """Test sending notification with send error."""
        mock_render.return_value = ('<p>HTML</p>', 'Text')
        mock_connection = Mock()
        mock_conn.return_value = mock_connection
        
        mock_email = Mock()
        mock_email.send.side_effect = Exception("Send error")
        mock_build.return_value = mock_email
        
        result = send_email_notification(
            user_email='test@example.com',
            notification_type='welcome',
            context={}
        )
        
        assert result['success'] is False


class TestSendCustomEmailFunction:
    """Tests for send_custom_email function."""
    
    @patch('api.services.email.email_service.email_service')
    def test_send_custom_email_success(self, mock_service, mock_email_settings):
        """Test successful custom email sending."""
        mock_service.send_email.return_value = {'success': True, 'backend_used': 'smtp'}
        
        result = send_custom_email(
            to_emails='test@example.com',
            subject='Test Subject',
            html_content='<p>Test</p>',
            text_content='Test'
        )
        
        assert result['success'] is True
        mock_service.send_email.assert_called_once()
    
    @patch('api.services.email.email_service.email_service')
    def test_send_custom_email_with_ssl_fallback(self, mock_service, mock_email_settings):
        """Test custom email with SSL fallback."""
        mock_email_settings.EMAIL_USE_SSL_FALLBACK = True
        mock_service.send_email.side_effect = [
            Exception("TLS error"),
            {'success': True, 'backend_used': 'smtp'}
        ]
        
        result = send_custom_email(
            to_emails='test@example.com',
            subject='Test Subject',
            html_content='<p>Test</p>'
        )
        
        assert result['success'] is True
        assert mock_service.send_email.call_count == 2

