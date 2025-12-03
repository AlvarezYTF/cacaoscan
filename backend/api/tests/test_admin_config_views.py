"""
Unit tests for admin config views.
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


class SystemSettingsViewTest(APITestCase):
    """Tests for SystemSettingsView."""
    
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
        self.url = reverse('system-settings')
    
    def test_system_settings_get_requires_authentication(self):
        """Test that system settings GET requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.admin.config_views.SystemSettings')
    @patch('api.views.admin.config_views.SystemSettingsSerializer')
    def test_system_settings_get_success(self, mock_serializer_class, mock_settings):
        """Test successful system settings retrieval."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_instance = Mock()
        mock_instance.logo = None
        mock_settings.get_singleton.return_value = mock_instance
        
        # Mock the serializer
        mock_serializer = Mock()
        mock_serializer.data = {'nombre_sistema': 'CacaoScan'}
        mock_serializer_class.return_value = mock_serializer
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_system_settings_put_requires_admin(self):
        """Test that system settings PUT requires admin."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.admin.config_views.SystemSettings')
    @patch('api.views.admin.config_views.SystemSettingsSerializer')
    def test_system_settings_put_success(self, mock_serializer_class, mock_settings):
        """Test successful system settings update."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        # Create a proper mock instance with necessary attributes
        mock_instance = Mock()
        mock_instance.nombre_sistema = 'Test System'
        mock_instance.logo = None
        mock_instance.save = Mock(return_value=mock_instance)
        mock_settings.get_singleton.return_value = mock_instance
        
        # Mock the serializer
        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.save.return_value = mock_instance
        mock_serializer.data = {'nombre_sistema': 'Test System'}
        mock_serializer_class.return_value = mock_serializer
        
        response = self.client.put(self.url, {
            'nombre_sistema': 'Test System'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SystemGeneralConfigViewTest(APITestCase):
    """Tests for SystemGeneralConfigView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('system-general-config')
    
    def test_system_general_config_get_public_access(self):
        """Test that general config GET is publicly accessible."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('nombre_sistema', response.data)
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_system_general_config_put_requires_admin(self, mock_settings):
        """Test that general config PUT requires admin."""
        user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_system_general_config_put_success(self, mock_settings):
        """Test successful general config update."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_instance = Mock()
        mock_instance.nombre_sistema = 'Updated System'
        mock_instance.email_contacto = 'test@example.com'
        mock_instance.lema = 'Test Lema'
        mock_instance.logo = None
        mock_instance.save = Mock(return_value=mock_instance)
        mock_settings.get_singleton.return_value = mock_instance
        
        response = self.client.put(self.url, {
            'nombre_sistema': 'Updated System'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SystemSecurityConfigViewTest(APITestCase):
    """Tests for SystemSecurityConfigView."""
    
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
        self.url = reverse('system-security-config')
    
    def test_security_config_get_requires_authentication(self):
        """Test that security config GET requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_security_config_get_success(self, mock_settings):
        """Test successful security config retrieval."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        # Create a simple object with the necessary attributes
        # This avoids issues with hasattr() on Mock objects
        class SettingsObject:
            def __init__(self):
                self.recaptcha_enabled = True
                self.session_timeout = 60
                self.login_attempts = 5
                self.two_factor_auth = False
        
        mock_instance = SettingsObject()
        mock_settings.get_singleton.return_value = mock_instance
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recaptcha_enabled', response.data)
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_security_config_put_success(self, mock_settings):
        """Test successful security config update."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_instance = Mock()
        mock_instance.recaptcha_enabled = True
        mock_instance.session_timeout = 60
        mock_instance.login_attempts = 5
        mock_instance.two_factor_auth = False
        mock_instance.save = Mock(return_value=mock_instance)
        mock_settings.get_singleton.return_value = mock_instance
        
        response = self.client.put(self.url, {
            'recaptcha_enabled': True,
            'session_timeout': 60
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SystemMLConfigViewTest(APITestCase):
    """Tests for SystemMLConfigView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('system-ml-config')
    
    def test_ml_config_get_requires_authentication(self):
        """Test that ML config GET requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_ml_config_get_success(self, mock_settings):
        """Test successful ML config retrieval."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        # Create a simple object with the necessary attributes
        # This avoids issues with hasattr() on Mock objects
        class SettingsObject:
            def __init__(self):
                self.active_model = 'yolov8'
                self.last_training = None
        
        mock_instance = SettingsObject()
        mock_settings.get_singleton.return_value = mock_instance
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('active_model', response.data)
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_ml_config_put_success(self, mock_settings):
        """Test successful ML config update."""
        admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
        token = RefreshToken.for_user(admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        from django.utils import timezone
        mock_instance = Mock()
        mock_instance.active_model = 'yolov8'
        mock_instance.last_training = None
        mock_instance.save = Mock(return_value=mock_instance)
        mock_settings.get_singleton.return_value = mock_instance
        
        response = self.client.put(self.url, {
            'active_model': 'yolov8'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SystemInfoViewTest(APITestCase):
    """Tests for SystemInfoView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('system-info')
    
    def test_system_info_public_access(self):
        """Test that system info is publicly accessible."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('system', response.data)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['system'], 'CacaoScan')

