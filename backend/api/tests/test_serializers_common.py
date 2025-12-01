"""
Unit tests for common serializers.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from rest_framework import serializers
from api.serializers.common_serializers import (
    ErrorResponseSerializer,
    DatasetStatsSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
    SystemSettingsSerializer
)
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


class ErrorResponseSerializerTest(TestCase):
    """Tests for ErrorResponseSerializer."""
    
    def test_error_response_serialization_success(self):
        """Test successful error response serialization."""
        serializer = ErrorResponseSerializer(data={
            'error': 'Test error message',
            'status': 'error'
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['error'], 'Test error message')
        self.assertEqual(serializer.validated_data['status'], 'error')
    
    def test_error_response_missing_fields(self):
        """Test error response with missing fields."""
        serializer = ErrorResponseSerializer(data={
            'error': 'Test error'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)


class DatasetStatsSerializerTest(TestCase):
    """Tests for DatasetStatsSerializer."""
    
    def test_dataset_stats_serialization_success(self):
        """Test successful dataset stats serialization."""
        serializer = DatasetStatsSerializer(data={
            'total_records': 100,
            'valid_records': 95,
            'missing_images': 5,
            'missing_ids': [1, 2, 3],
            'dimensions_stats': {'width': 512, 'height': 512}
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['total_records'], 100)
        self.assertEqual(serializer.validated_data['valid_records'], 95)
        self.assertEqual(serializer.validated_data['missing_images'], 5)
        self.assertEqual(len(serializer.validated_data['missing_ids']), 3)
        self.assertIn('dimensions_stats', serializer.validated_data)
    
    def test_dataset_stats_missing_fields(self):
        """Test dataset stats with missing required fields."""
        serializer = DatasetStatsSerializer(data={
            'total_records': 100
        })
        self.assertFalse(serializer.is_valid())


class NotificationSerializerTest(TestCase):
    """Tests for NotificationSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.common_serializers.Notification')
    def test_notification_serialization_success(self, mock_notification_model):
        """Test successful notification serialization."""
        mock_notification = Mock()
        mock_notification.id = 1
        mock_notification.tipo = 'info'
        mock_notification.get_tipo_display.return_value = 'Información'
        mock_notification.titulo = 'Test Notification'
        mock_notification.mensaje = 'This is a test notification message'
        mock_notification.leida = False
        mock_notification.fecha_creacion = timezone.now()
        mock_notification.fecha_lectura = None
        mock_notification.datos_extra = {}
        mock_notification.created_at = timezone.now()
        mock_notification.updated_at = timezone.now()
        mock_notification.tiempo_transcurrido = 'hace 5 minutos'
        
        serializer = NotificationSerializer(mock_notification)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('tipo', data)
        self.assertIn('tipo_display', data)
        self.assertIn('titulo', data)
        self.assertIn('mensaje', data)
        self.assertIn('leida', data)
        self.assertIn('tiempo_transcurrido', data)
    
    def test_notification_validation_short_title(self):
        """Test notification validation with short title."""
        serializer = NotificationSerializer(data={
            'tipo': 'info',
            'titulo': 'AB',
            'mensaje': 'This is a test notification message with enough characters'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('titulo', serializer.errors)
    
    def test_notification_validation_empty_title(self):
        """Test notification validation with empty title."""
        serializer = NotificationSerializer(data={
            'tipo': 'info',
            'titulo': '',
            'mensaje': 'This is a test notification message with enough characters'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('titulo', serializer.errors)
    
    def test_notification_validation_short_message(self):
        """Test notification validation with short message."""
        serializer = NotificationSerializer(data={
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'Short'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('mensaje', serializer.errors)
    
    def test_notification_validation_empty_message(self):
        """Test notification validation with empty message."""
        serializer = NotificationSerializer(data={
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': ''
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('mensaje', serializer.errors)
    
    def test_notification_validation_title_trimming(self):
        """Test notification title trimming."""
        serializer = NotificationSerializer(data={
            'tipo': 'info',
            'titulo': '  Test Notification  ',
            'mensaje': 'This is a test notification message with enough characters'
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['titulo'], 'Test Notification')
    
    def test_notification_validation_message_trimming(self):
        """Test notification message trimming."""
        serializer = NotificationSerializer(data={
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': '  This is a test notification message with enough characters  '
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['mensaje'], 'This is a test notification message with enough characters')


class NotificationListSerializerTest(TestCase):
    """Tests for NotificationListSerializer."""
    
    @patch('api.serializers.common_serializers.Notification')
    def test_notification_list_serialization_success(self, mock_notification_model):
        """Test successful notification list serialization."""
        mock_notification = Mock()
        mock_notification.id = 1
        mock_notification.tipo = 'info'
        mock_notification.get_tipo_display.return_value = 'Información'
        mock_notification.titulo = 'Test Notification'
        mock_notification.mensaje = 'Test message'
        mock_notification.leida = False
        mock_notification.fecha_creacion = timezone.now()
        mock_notification.tiempo_transcurrido = 'hace 5 minutos'
        
        serializer = NotificationListSerializer(mock_notification)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('tipo', data)
        self.assertIn('tipo_display', data)
        self.assertIn('titulo', data)
        self.assertIn('mensaje', data)
        self.assertIn('leida', data)
        self.assertIn('fecha_creacion', data)
        self.assertIn('tiempo_transcurrido', data)


class NotificationCreateSerializerTest(TestCase):
    """Tests for NotificationCreateSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.common_serializers.Notification')
    def test_notification_create_success(self, mock_notification_model):
        """Test successful notification creation."""
        mock_notification_model.TIPO_CHOICES = [
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
            ('success', 'Éxito')
        ]
        
        serializer = NotificationCreateSerializer(data={
            'user': self.user.id,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message'
        })
        self.assertTrue(serializer.is_valid())
    
    @patch('api.serializers.common_serializers.Notification')
    def test_notification_create_invalid_type(self, mock_notification_model):
        """Test notification creation with invalid type."""
        mock_notification_model.TIPO_CHOICES = [
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
            ('success', 'Éxito')
        ]
        
        serializer = NotificationCreateSerializer(data={
            'user': self.user.id,
            'tipo': 'invalid_type',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo', serializer.errors)
    
    @patch('api.serializers.common_serializers.Notification')
    def test_notification_create_with_extra_data(self, mock_notification_model):
        """Test notification creation with extra data."""
        mock_notification_model.TIPO_CHOICES = [
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
            ('success', 'Éxito')
        ]
        
        serializer = NotificationCreateSerializer(data={
            'user': self.user.id,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message',
            'datos_extra': {'key': 'value'}
        })
        self.assertTrue(serializer.is_valid())


class NotificationStatsSerializerTest(TestCase):
    """Tests for NotificationStatsSerializer."""
    
    def test_notification_stats_serialization_success(self):
        """Test successful notification stats serialization."""
        serializer = NotificationStatsSerializer(data={
            'total_notifications': 100,
            'unread_count': 25,
            'notifications_by_type': {'info': 50, 'warning': 30, 'error': 20},
            'recent_notifications': [
                {'id': 1, 'titulo': 'Notification 1'},
                {'id': 2, 'titulo': 'Notification 2'}
            ]
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['total_notifications'], 100)
        self.assertEqual(serializer.validated_data['unread_count'], 25)
        self.assertIn('notifications_by_type', serializer.validated_data)
        self.assertEqual(len(serializer.validated_data['recent_notifications']), 2)
    
    def test_notification_stats_missing_fields(self):
        """Test notification stats with missing required fields."""
        serializer = NotificationStatsSerializer(data={
            'total_notifications': 100
        })
        self.assertFalse(serializer.is_valid())


class SystemSettingsSerializerTest(TestCase):
    """Tests for SystemSettingsSerializer."""
    
    @patch('api.serializers.common_serializers.SystemSettings')
    def test_system_settings_serialization_success(self, mock_settings_model):
        """Test successful system settings serialization."""
        mock_settings = Mock()
        mock_settings.id = 1
        mock_settings.logo = None
        mock_settings.created_at = timezone.now()
        mock_settings.updated_at = timezone.now()
        
        serializer = SystemSettingsSerializer(mock_settings)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('logo_url', data)
    
    @patch('api.serializers.common_serializers.SystemSettings')
    def test_system_settings_logo_url_with_request(self, mock_settings_model):
        """Test system settings logo URL with request context."""
        mock_settings = Mock()
        mock_settings.id = 1
        mock_logo = Mock()
        mock_logo.url = '/media/logo.png'
        mock_settings.logo = mock_logo
        
        mock_request = Mock()
        mock_request.build_absolute_uri.return_value = 'http://example.com/media/logo.png'
        
        serializer = SystemSettingsSerializer(
            mock_settings,
            context={'request': mock_request}
        )
        data = serializer.data
        
        self.assertIn('logo_url', data)
        self.assertEqual(data['logo_url'], 'http://example.com/media/logo.png')
    
    @patch('api.serializers.common_serializers.SystemSettings')
    def test_system_settings_logo_url_without_request(self, mock_settings_model):
        """Test system settings logo URL without request context."""
        mock_settings = Mock()
        mock_settings.id = 1
        mock_logo = Mock()
        mock_logo.url = '/media/logo.png'
        mock_settings.logo = mock_logo
        
        serializer = SystemSettingsSerializer(mock_settings)
        data = serializer.data
        
        self.assertIn('logo_url', data)
        self.assertEqual(data['logo_url'], '/media/logo.png')
    
    @patch('api.serializers.common_serializers.SystemSettings')
    def test_system_settings_no_logo(self, mock_settings_model):
        """Test system settings without logo."""
        mock_settings = Mock()
        mock_settings.id = 1
        mock_settings.logo = None
        
        serializer = SystemSettingsSerializer(mock_settings)
        data = serializer.data
        
        self.assertIn('logo_url', data)
        self.assertIsNone(data['logo_url'])

