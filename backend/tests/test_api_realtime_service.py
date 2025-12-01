"""
Tests unitarios para api.realtime_service.

Cubre la clase RealtimeNotificationService:
- send_notification_to_user
- send_notification_to_all_users
- send_notification_to_admins
- update_notification_stats
- send_activity_log
- send_login_activity
- send_system_status_update
- send_system_alert
- create_and_send_notification
"""
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from api.realtime_service import (
    RealtimeNotificationService,
    realtime_service
)


class RealtimeServiceTestCase(TestCase):
    """Tests para servicio de notificaciones en tiempo real."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = RealtimeNotificationService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True,
            is_staff=True
        )

    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.settings')
    @patch('api.realtime_service.logger')
    def test_send_notification_to_user_enabled(self, mock_logger, mock_settings,
                                               mock_async_to_sync, mock_get_channel):
        """Test send_notification_to_user when realtime is enabled."""
        mock_settings.REALTIME_NOTIFICATIONS_ENABLED = True
        mock_channel_layer = Mock()
        mock_get_channel.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        notification_data = {'titulo': 'Test Notification', 'mensaje': 'Test'}
        
        self.service.send_notification_to_user(self.user.id, notification_data)
        
        mock_group_send.assert_called_once()
        call_args = mock_group_send.call_args
        self.assertEqual(call_args[0][0], f'notifications_{self.user.id}')
        mock_logger.info.assert_called_once()

    @patch('api.realtime_service.settings')
    @patch('api.realtime_service.logger')
    def test_send_notification_to_user_disabled(self, mock_logger, mock_settings):
        """Test send_notification_to_user when realtime is disabled."""
        mock_settings.REALTIME_NOTIFICATIONS_ENABLED = False
        
        notification_data = {'titulo': 'Test Notification'}
        
        self.service.send_notification_to_user(self.user.id, notification_data)
        
        mock_logger.info.assert_not_called()

    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.settings')
    @patch('api.realtime_service.logger')
    def test_send_notification_to_user_handles_exception(self, mock_logger, mock_settings,
                                                         mock_async_to_sync, mock_get_channel):
        """Test send_notification_to_user handles exceptions."""
        mock_settings.REALTIME_NOTIFICATIONS_ENABLED = True
        mock_get_channel.side_effect = Exception("Channel error")
        
        notification_data = {'titulo': 'Test'}
        
        self.service.send_notification_to_user(self.user.id, notification_data)
        
        mock_logger.error.assert_called_once()

    @patch('api.realtime_service.RealtimeNotificationService.send_notification_to_user')
    @patch('api.realtime_service.User')
    @patch('api.realtime_service.settings')
    @patch('api.realtime_service.logger')
    def test_send_notification_to_all_users(self, mock_logger, mock_settings,
                                           mock_user_model, mock_send_to_user):
        """Test send_notification_to_all_users sends to all active users."""
        mock_settings.NOTIFICATION_BROADCAST_ENABLED = True
        mock_user_model.objects.filter.return_value.count.return_value = 2
        mock_user_model.objects.filter.return_value = [self.user, self.admin_user]
        
        notification_data = {'titulo': 'Broadcast'}
        
        self.service.send_notification_to_all_users(notification_data)
        
        self.assertEqual(mock_send_to_user.call_count, 2)

    @patch('api.realtime_service.settings')
    def test_send_notification_to_all_users_disabled(self, mock_settings):
        """Test send_notification_to_all_users does nothing when disabled."""
        mock_settings.NOTIFICATION_BROADCAST_ENABLED = False
        
        with patch.object(self.service, 'send_notification_to_user') as mock_send:
            self.service.send_notification_to_all_users({})
            mock_send.assert_not_called()

    @patch('api.realtime_service.RealtimeNotificationService.send_notification_to_user')
    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_send_notification_to_admins(self, mock_logger, mock_user_model,
                                        mock_send_to_user):
        """Test send_notification_to_admins sends only to admin users."""
        mock_user_model.objects.filter.return_value = [self.admin_user]
        
        notification_data = {'titulo': 'Admin Notification'}
        
        self.service.send_notification_to_admins(notification_data)
        
        mock_send_to_user.assert_called_once_with(self.admin_user.id, notification_data)

    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.Notification')
    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_update_notification_stats(self, mock_logger, mock_user_model,
                                      mock_notification_model, mock_async_to_sync,
                                      mock_get_channel):
        """Test update_notification_stats updates and sends stats."""
        mock_user_model.objects.get.return_value = self.user
        mock_notification_model.objects.filter.return_value.count.return_value = 5
        mock_notification_model.get_unread_count.return_value = 2
        mock_notification_model.TIPO_CHOICES = [('info', 'Info'), ('error', 'Error')]
        mock_notification_model.objects.filter.return_value.count.side_effect = [3, 2]
        
        mock_channel_layer = Mock()
        mock_get_channel.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        self.service.update_notification_stats(self.user.id)
        
        mock_group_send.assert_called_once()
        mock_logger.error.assert_not_called()

    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_update_notification_stats_user_not_found(self, mock_logger, mock_user_model):
        """Test update_notification_stats handles user not found."""
        mock_user_model.objects.get.side_effect = User.DoesNotExist()
        
        self.service.update_notification_stats(999)
        
        mock_logger.error.assert_called_once()

    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_send_activity_log(self, mock_logger, mock_user_model,
                               mock_async_to_sync, mock_get_channel):
        """Test send_activity_log sends to all admins."""
        mock_user_model.objects.filter.return_value = [self.admin_user]
        mock_channel_layer = Mock()
        mock_get_channel.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        activity_data = {'usuario': 'testuser', 'accion': 'create'}
        
        self.service.send_activity_log(activity_data)
        
        mock_group_send.assert_called_once()
        mock_logger.info.assert_called_once()

    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_send_login_activity(self, mock_logger, mock_user_model,
                                mock_async_to_sync, mock_get_channel):
        """Test send_login_activity sends to all admins."""
        mock_user_model.objects.filter.return_value = [self.admin_user]
        mock_channel_layer = Mock()
        mock_get_channel.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        login_data = {'usuario': 'testuser', 'success': True}
        
        self.service.send_login_activity(login_data)
        
        mock_group_send.assert_called_once()
        mock_logger.info.assert_called_once()

    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.logger')
    def test_send_system_status_update(self, mock_logger, mock_async_to_sync,
                                      mock_get_channel):
        """Test send_system_status_update sends status update."""
        mock_channel_layer = Mock()
        mock_get_channel.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        status_data = {'status': 'healthy', 'cpu': 50}
        
        self.service.send_system_status_update(status_data)
        
        mock_group_send.assert_called_once()
        mock_logger.info.assert_called_once()

    @patch('api.realtime_service.RealtimeNotificationService.send_notification_to_admins')
    @patch('api.realtime_service.get_channel_layer')
    @patch('api.realtime_service.async_to_sync')
    @patch('api.realtime_service.logger')
    def test_send_system_alert(self, mock_logger, mock_async_to_sync,
                               mock_get_channel, mock_send_to_admins):
        """Test send_system_alert sends alert and notification."""
        mock_channel_layer = Mock()
        mock_get_channel.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        alert_data = {'title': 'Alert', 'message': 'System error'}
        
        self.service.send_system_alert(alert_data)
        
        mock_group_send.assert_called_once()
        mock_send_to_admins.assert_called_once()
        mock_logger.info.assert_called_once()

    @patch('api.realtime_service.RealtimeNotificationService.send_notification_to_user')
    @patch('api.realtime_service.RealtimeNotificationService.update_notification_stats')
    @patch('api.realtime_service.Notification')
    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_create_and_send_notification(self, mock_logger, mock_user_model,
                                         mock_notification_model, mock_update_stats,
                                         mock_send_to_user):
        """Test create_and_send_notification creates and sends notification."""
        mock_user_model.objects.get.return_value = self.user
        mock_notification = Mock()
        mock_notification.id = 1
        mock_notification.tipo = 'info'
        mock_notification.titulo = 'Test'
        mock_notification.mensaje = 'Test message'
        mock_notification.fecha_creacion.isoformat.return_value = '2024-01-01T00:00:00'
        mock_notification.datos_extra = {}
        
        mock_notification_model.create_notification.return_value = mock_notification
        
        notification = self.service.create_and_send_notification(
            self.user.id, 'info', 'Test', 'Test message'
        )
        
        self.assertIsNotNone(notification)
        mock_notification_model.create_notification.assert_called_once()
        mock_send_to_user.assert_called_once()
        mock_update_stats.assert_called_once()

    @patch('api.realtime_service.User')
    @patch('api.realtime_service.logger')
    def test_create_and_send_notification_user_not_found(self, mock_logger, mock_user_model):
        """Test create_and_send_notification handles user not found."""
        mock_user_model.objects.get.side_effect = User.DoesNotExist()
        
        notification = self.service.create_and_send_notification(
            999, 'info', 'Test', 'Test message'
        )
        
        self.assertIsNone(notification)
        mock_logger.error.assert_called_once()

    @patch('api.realtime_service.Notification', None)
    @patch('api.realtime_service.logger')
    def test_create_and_send_notification_model_not_available(self, mock_logger):
        """Test create_and_send_notification handles Notification model not available."""
        notification = self.service.create_and_send_notification(
            self.user.id, 'info', 'Test', 'Test message'
        )
        
        self.assertIsNone(notification)
        mock_logger.debug.assert_called()

    def test_realtime_service_is_singleton(self):
        """Test that realtime_service is a singleton instance."""
        from api.realtime_service import realtime_service as service1
        from api.realtime_service import realtime_service as service2
        
        self.assertIs(service1, service2)
        self.assertIsInstance(service1, RealtimeNotificationService)

