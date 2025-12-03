"""
Unit tests for admin email views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_PASSWORD,
)


class EmailStatusViewTest(APITestCase):
    """Tests for EmailStatusView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('admin-email-status')
    
    def test_email_status_requires_admin(self):
        """Test that email status requires admin."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('django.conf.settings')
    @patch('api.views.admin.email_views.email_service')
    def test_email_status_success(self, mock_email_service, mock_settings):
        """Test successful email status retrieval."""
        mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
        mock_settings.EMAIL_HOST_USER = 'test@example.com'
        mock_settings.EMAIL_HOST_PASSWORD = 'password'
        mock_settings.SENDGRID_API_KEY = None
        mock_settings.EMAIL_NOTIFICATION_TYPES = ['welcome', 'reset']
        mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
        mock_settings.EMAIL_HOST = 'smtp.example.com'
        mock_settings.EMAIL_PORT = 587
        
        mock_email_service.smtp_backend = Mock()
        mock_email_service.sendgrid_client = None
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # create_success_response does update(data), so keys are at top level, not in 'data'
        self.assertIn('email_enabled', response.data)
        self.assertTrue(response.data['success'])


class SendTestEmailViewTest(APITestCase):
    """Tests for SendTestEmailView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('admin-send-test-email')
    
    def test_send_test_email_requires_admin(self):
        """Test that send test email requires admin."""
        user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_send_test_email_missing_email(self):
        """Test send test email without email."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api.views.admin.email_views.send_custom_email')
    def test_send_test_email_success(self, mock_send_email):
        """Test successful test email sending."""
        mock_send_email.return_value = {
            'success': True,
            'backend_used': 'smtp',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {
            'to_email': 'test@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class SendBulkNotificationViewTest(APITestCase):
    """Tests for SendBulkNotificationView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('admin-send-bulk-notification')
    
    def test_send_bulk_notification_requires_admin(self):
        """Test that send bulk notification requires admin."""
        user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_send_bulk_notification_missing_fields(self):
        """Test send bulk notification with missing fields."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api.views.admin.email_views.send_bulk_email_notification')
    def test_send_bulk_notification_success(self, mock_send_bulk):
        """Test successful bulk notification sending."""
        mock_send_bulk.return_value = {
            'total_emails': 2,
            'successful': 2,
            'failed': 0,
            'batches_processed': 1,
            'errors': []
        }
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {
            'notification_type': 'welcome',
            'user_emails': ['test1@example.com', 'test2@example.com']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class EmailTemplatePreviewViewTest(APITestCase):
    """Tests for EmailTemplatePreviewView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('admin-email-template-preview')
    
    def test_email_template_preview_requires_admin(self):
        """Test that email template preview requires admin."""
        user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_email_template_preview_missing_template_type(self):
        """Test email template preview without template type."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api.views.admin.email_views.email_notification_service')
    def test_email_template_preview_success(self, mock_email_service):
        """Test successful email template preview."""
        mock_email_service.email_service._render_template.return_value = (
            '<html>Test</html>',
            'Test'
        )
        mock_email_service._get_default_subject.return_value = 'Test Subject'
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url, {
            'template_type': 'welcome'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # create_success_response does update(data), so keys are at top level, not in 'data'
        self.assertIn('html_content', response.data)


class EmailLogsViewTest(APITestCase):
    """Tests for EmailLogsView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('admin-email-logs')
    
    def test_email_logs_requires_admin(self):
        """Test that email logs requires admin."""
        user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_email_logs_success(self):
        """Test successful email logs retrieval."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # create_success_response does update(data), so keys are at top level, not in 'data'
        self.assertIn('total_emails', response.data)

