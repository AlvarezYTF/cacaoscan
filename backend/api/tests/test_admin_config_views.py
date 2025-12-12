"""
Tests for admin config views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework.response import Response
from api.views.admin.config_views import (
    SystemSettingsView,
    SystemGeneralConfigView,
    SystemSecurityConfigView,
    SystemMLConfigView,
    SystemInfoView
)


@pytest.mark.django_db
class TestSystemSettingsView:
    """Test cases for SystemSettingsView."""
    
    def test_get_without_admin_for_put(self, user):
        """Test PUT request without admin permission."""
        factory = RequestFactory()
        request = factory.put('/api/admin/config/settings/', {}, content_type='application/json')
        request.user = user
        request.data = {}
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_settings.get_singleton.return_value = Mock()
            
            view = SystemSettingsView()
            response = view.put(request)
            
            assert response.status_code == 403
    
    def test_get_settings(self, admin_user):
        """Test GET request for system settings."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/settings/')
        request.user = admin_user
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_singleton.__class__ = type('SystemSettings', (), {})
            mock_settings.get_singleton.return_value = mock_singleton
            
            with patch('api.views.admin.config_views.SystemSettingsSerializer') as mock_serializer:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {'key': 'value'}
                mock_serializer.return_value = mock_serializer_instance
                
                view = SystemSettingsView()
                response = view.get(request)
                
                assert response.status_code == 200
    
    def test_put_settings(self, admin_user):
        """Test PUT request to update system settings."""
        factory = RequestFactory()
        request = factory.put(
            '/api/admin/config/settings/',
            {'nombre_sistema': 'Test System'},
            content_type='application/json'
        )
        request.user = admin_user
        request.data = {'nombre_sistema': 'Test System'}
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_settings.get_singleton.return_value = mock_singleton
            
            with patch('api.views.admin.config_views.SystemSettingsSerializer') as mock_serializer:
                mock_serializer_instance = Mock()
                mock_serializer_instance.is_valid.return_value = True
                mock_serializer_instance.data = {'nombre_sistema': 'Test System'}
                mock_serializer.return_value = mock_serializer_instance
                
                view = SystemSettingsView()
                response = view.put(request)
                
                assert response.status_code == 200
    
    def test_put_settings_invalid(self, admin_user):
        """Test PUT request with invalid data."""
        factory = RequestFactory()
        request = factory.put(
            '/api/admin/config/settings/',
            {},
            content_type='application/json'
        )
        request.user = admin_user
        request.data = {}
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_settings.get_singleton.return_value = mock_singleton
            
            with patch('api.views.admin.config_views.SystemSettingsSerializer') as mock_serializer:
                mock_serializer_instance = Mock()
                mock_serializer_instance.is_valid.return_value = False
                mock_serializer_instance.errors = {'field': ['error']}
                mock_serializer.return_value = mock_serializer_instance
                
                view = SystemSettingsView()
                response = view.put(request)
                
                assert response.status_code == 400


@pytest.mark.django_db
class TestSystemGeneralConfigView:
    """Test cases for SystemGeneralConfigView."""
    
    def test_get_general_config(self):
        """Test GET request for general config."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/general/')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_singleton.nombre_sistema = 'Test System'
            mock_singleton.email_contacto = 'test@example.com'
            mock_singleton.lema = 'Test slogan'
            mock_singleton.logo = None
            mock_settings.get_singleton.return_value = mock_singleton
            
            view = SystemGeneralConfigView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert response.data['nombre_sistema'] == 'Test System'
    
    def test_get_general_config_no_settings(self):
        """Test GET request when no settings exist."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/general/')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_settings.get_singleton.return_value = None
            
            view = SystemGeneralConfigView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert response.data['nombre_sistema'] == 'CacaoScan'
    
    def test_put_general_config_without_admin(self, user):
        """Test PUT request without admin permission."""
        factory = RequestFactory()
        request = factory.put(
            '/api/admin/config/general/',
            {'nombre_sistema': 'Test'},
            content_type='application/json'
        )
        request.user = user
        request.data = {'nombre_sistema': 'Test'}
        
        view = SystemGeneralConfigView()
        response = view.put(request)
        
        assert response.status_code == 403
    
    def test_put_general_config(self, admin_user):
        """Test PUT request to update general config."""
        factory = RequestFactory()
        request = factory.put(
            '/api/admin/config/general/',
            {'nombre_sistema': 'Updated System'},
            content_type='application/json'
        )
        request.user = admin_user
        request.data = {'nombre_sistema': 'Updated System'}
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_singleton.nombre_sistema = 'Updated System'
            mock_singleton.email_contacto = 'test@example.com'
            mock_singleton.lema = 'Test slogan'
            mock_singleton.logo = None
            mock_singleton.save = Mock()
            mock_settings.get_singleton.return_value = mock_singleton
            
            view = SystemGeneralConfigView()
            response = view.put(request)
            
            assert response.status_code == 200
            assert mock_singleton.save.called


@pytest.mark.django_db
class TestSystemSecurityConfigView:
    """Test cases for SystemSecurityConfigView."""
    
    def test_get_security_config(self):
        """Test GET request for security config."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/security/')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_singleton.recaptcha_enabled = True
            mock_singleton.session_timeout = 60
            mock_singleton.login_attempts = 5
            mock_singleton.two_factor_auth = False
            mock_settings.get_singleton.return_value = mock_singleton
            
            view = SystemSecurityConfigView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert response.data['recaptcha_enabled'] is True
    
    def test_get_security_config_no_settings(self):
        """Test GET request when no settings exist."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/security/')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_settings.get_singleton.return_value = None
            
            view = SystemSecurityConfigView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert response.data['recaptcha_enabled'] is True
    
    def test_put_security_config(self, admin_user):
        """Test PUT request to update security config."""
        factory = RequestFactory()
        request = factory.put(
            '/api/admin/config/security/',
            {'recaptcha_enabled': False},
            content_type='application/json'
        )
        request.user = admin_user
        request.data = {'recaptcha_enabled': False}
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_singleton.recaptcha_enabled = False
            mock_singleton.session_timeout = 60
            mock_singleton.login_attempts = 5
            mock_singleton.two_factor_auth = False
            mock_singleton.save = Mock()
            mock_settings.get_singleton.return_value = mock_singleton
            
            view = SystemSecurityConfigView()
            response = view.put(request)
            
            assert response.status_code == 200
            assert mock_singleton.save.called


@pytest.mark.django_db
class TestSystemMLConfigView:
    """Test cases for SystemMLConfigView."""
    
    def test_get_ml_config(self):
        """Test GET request for ML config."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/ml/')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_singleton = Mock()
            mock_singleton.active_model = 'yolov8'
            mock_singleton.last_training = None
            mock_settings.get_singleton.return_value = mock_singleton
            
            view = SystemMLConfigView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert 'active_model' in response.data
    
    def test_get_ml_config_no_settings(self):
        """Test GET request when no settings exist."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/ml/')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_settings.get_singleton.return_value = None
            
            view = SystemMLConfigView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert response.data['active_model'] == 'yolov8'
    
    def test_put_ml_config(self, admin_user):
        """Test PUT request to update ML config."""
        from django.utils import timezone
        
        factory = RequestFactory()
        request = factory.put(
            '/api/admin/config/ml/',
            {'active_model': 'resnet18'},
            content_type='application/json'
        )
        request.user = admin_user
        request.data = {'active_model': 'resnet18'}
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            with patch('api.views.admin.config_views.timezone') as mock_timezone:
                mock_now = timezone.now()
                mock_timezone.now.return_value = mock_now
                
                mock_singleton = Mock()
                mock_singleton.active_model = 'resnet18'
                mock_singleton.last_training = mock_now
                mock_singleton.save = Mock()
                mock_settings.get_singleton.return_value = mock_singleton
                
                view = SystemMLConfigView()
                response = view.put(request)
                
                assert response.status_code == 200
                assert mock_singleton.save.called


@pytest.mark.django_db
class TestSystemInfoView:
    """Test cases for SystemInfoView."""
    
    def test_get_system_info(self):
        """Test GET request for system info."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/info/')
        
        view = SystemInfoView()
        response = view.get(request)
        
        assert response.status_code == 200
        assert response.data['system'] == 'CacaoScan'
        assert response.data['status'] == 'ok'
    
    def test_get_system_info_with_exception(self):
        """Test GET request with exception."""
        factory = RequestFactory()
        request = factory.get('/api/admin/config/info/')
        
        with patch('django.get_version', side_effect=Exception('Error')):
            view = SystemInfoView()
            response = view.get(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

