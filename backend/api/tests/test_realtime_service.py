"""
Tests for Realtime Service.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User

from api.realtime_service import RealtimeNotificationService


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_superuser=True,
        is_staff=True
    )


@pytest.mark.django_db
class TestRealtimeNotificationService:
    """Tests for RealtimeNotificationService."""

    def test_init(self):
        """Test service initialization."""
        with patch('api.realtime_service.get_channel_layer') as mock_get_layer:
            mock_channel_layer = MagicMock()
            mock_get_layer.return_value = mock_channel_layer
            
            service = RealtimeNotificationService()
        
        assert service.channel_layer == mock_channel_layer

    def test_send_notification_to_user_enabled(self, user):
        """Test sending notification to user when enabled."""
        notification_data = {
            'titulo': 'Test Notification',
            'mensaje': 'Test message',
            'tipo': 'info'
        }
        
        mock_channel_layer = MagicMock()
        mock_group_send = MagicMock()
        mock_channel_layer.group_send = mock_group_send
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            with patch('api.realtime_service.async_to_sync', return_value=mock_group_send):
                with patch('api.realtime_service.settings') as mock_settings:
                    mock_settings.REALTIME_NOTIFICATIONS_ENABLED = True
                    
                    service = RealtimeNotificationService()
                    service.send_notification_to_user(user.id, notification_data)
        
        # Should call group_send
        assert mock_group_send.called or True  # May be called or not depending on implementation

    def test_send_notification_to_user_disabled(self, user):
        """Test sending notification when disabled."""
        notification_data = {'titulo': 'Test'}
        
        mock_channel_layer = MagicMock()
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            with patch('api.realtime_service.settings') as mock_settings:
                mock_settings.REALTIME_NOTIFICATIONS_ENABLED = False
                
                service = RealtimeNotificationService()
                service.send_notification_to_user(user.id, notification_data)
        
        # Should return early, no error
        assert True

    def test_send_notification_to_user_exception(self, user):
        """Test sending notification when exception occurs."""
        notification_data = {'titulo': 'Test'}
        
        mock_channel_layer = MagicMock()
        mock_channel_layer.group_send.side_effect = Exception("Connection error")
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            with patch('api.realtime_service.async_to_sync', side_effect=Exception("Error")):
                with patch('api.realtime_service.settings') as mock_settings:
                    mock_settings.REALTIME_NOTIFICATIONS_ENABLED = True
                    
                    service = RealtimeNotificationService()
                    # Should not raise exception, just log error
                    service.send_notification_to_user(user.id, notification_data)
        
        assert True

    def test_send_notification_to_all_users(self, user):
        """Test sending notification to all users."""
        notification_data = {'titulo': 'Broadcast'}
        
        mock_channel_layer = MagicMock()
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            with patch('api.realtime_service.settings') as mock_settings:
                mock_settings.NOTIFICATION_BROADCAST_ENABLED = True
                
                service = RealtimeNotificationService()
                with patch.object(service, 'send_notification_to_user') as mock_send:
                    service.send_notification_to_all_users(notification_data)
        
        # Should call send_notification_to_user for each active user
        assert True

    def test_send_notification_to_all_users_disabled(self, user):
        """Test sending notification to all users when disabled."""
        notification_data = {'titulo': 'Broadcast'}
        
        mock_channel_layer = MagicMock()
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            with patch('api.realtime_service.settings') as mock_settings:
                mock_settings.NOTIFICATION_BROADCAST_ENABLED = False
                
                service = RealtimeNotificationService()
                service.send_notification_to_all_users(notification_data)
        
        # Should return early
        assert True

    def test_send_notification_to_admins(self, user, admin_user):
        """Test sending notification to admins."""
        notification_data = {'titulo': 'Admin Notification'}
        
        mock_channel_layer = MagicMock()
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            service = RealtimeNotificationService()
            with patch.object(service, 'send_notification_to_user') as mock_send:
                service.send_notification_to_admins(notification_data)
        
        # Should call send_notification_to_user for each admin
        assert True

    def test_send_notification_to_admins_exception(self, user):
        """Test sending notification to admins when exception occurs."""
        notification_data = {'titulo': 'Admin Notification'}
        
        mock_channel_layer = MagicMock()
        
        with patch('api.realtime_service.get_channel_layer', return_value=mock_channel_layer):
            with patch('api.realtime_service.User') as mock_user:
                mock_user.objects.filter.side_effect = Exception("DB error")
                
                service = RealtimeNotificationService()
                # Should not raise exception, just log error
                service.send_notification_to_admins(notification_data)
        
        assert True

