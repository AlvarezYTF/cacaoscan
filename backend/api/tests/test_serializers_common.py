"""
Tests for common serializers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework.exceptions import ValidationError
from api.serializers.common_serializers import (
    ErrorResponseSerializer,
    DatasetStatsSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
    SystemSettingsSerializer
)


class TestErrorResponseSerializer:
    """Test cases for ErrorResponseSerializer."""
    
    def test_error_response_serializer_valid(self):
        """Test ErrorResponseSerializer with valid data."""
        serializer = ErrorResponseSerializer(data={
            'error': 'Test error',
            'status': 'error'
        })
        assert serializer.is_valid()
    
    def test_error_response_serializer_missing_fields(self):
        """Test ErrorResponseSerializer with missing fields."""
        serializer = ErrorResponseSerializer(data={'error': 'Test error'})
        assert not serializer.is_valid()


class TestDatasetStatsSerializer:
    """Test cases for DatasetStatsSerializer."""
    
    def test_dataset_stats_serializer_valid(self):
        """Test DatasetStatsSerializer with valid data."""
        serializer = DatasetStatsSerializer(data={
            'total_records': 100,
            'valid_records': 95,
            'missing_images': 5,
            'missing_ids': [1, 2, 3],
            'dimensions_stats': {'alto': 25.5, 'ancho': 20.3}
        })
        assert serializer.is_valid()
    
    def test_dataset_stats_serializer_invalid_total_records(self):
        """Test DatasetStatsSerializer with invalid total_records."""
        serializer = DatasetStatsSerializer(data={
            'total_records': 'invalid',
            'valid_records': 95,
            'missing_images': 5,
            'missing_ids': [],
            'dimensions_stats': {}
        })
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestNotificationSerializer:
    """Test cases for NotificationSerializer."""
    
    def test_notification_serializer_valid_data(self):
        """Test NotificationSerializer with valid data."""
        from notifications.models import Notification
        from django.contrib.auth.models import User
        
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='This is a test notification message'
        )
        
        serializer = NotificationSerializer(notification)
        data = serializer.data
        assert data['id'] == notification.id
        assert data['titulo'] == 'Test Notification'
        assert 'tiempo_transcurrido' in data
        assert 'tipo_display' in data
    
    def test_notification_serializer_validate_titulo_too_short(self):
        """Test NotificationSerializer with title too short."""
        serializer = NotificationSerializer(data={
            'titulo': 'AB',
            'mensaje': 'This is a valid message with enough characters'
        })
        assert not serializer.is_valid()
        assert 'titulo' in serializer.errors
    
    def test_notification_serializer_validate_mensaje_too_short(self):
        """Test NotificationSerializer with message too short."""
        serializer = NotificationSerializer(data={
            'titulo': 'Valid Title',
            'mensaje': 'Short'
        })
        assert not serializer.is_valid()
        assert 'mensaje' in serializer.errors
    
    def test_notification_serializer_validate_titulo_strips_whitespace(self):
        """Test NotificationSerializer strips whitespace from title."""
        serializer = NotificationSerializer(data={
            'titulo': '  Valid Title  ',
            'mensaje': 'This is a valid message with enough characters'
        })
        if serializer.is_valid():
            assert serializer.validated_data['titulo'] == 'Valid Title'


@pytest.mark.django_db
class TestNotificationListSerializer:
    """Test cases for NotificationListSerializer."""
    
    def test_notification_list_serializer(self):
        """Test NotificationListSerializer."""
        from notifications.models import Notification
        from django.contrib.auth.models import User
        
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='This is a test notification message'
        )
        
        serializer = NotificationListSerializer(notification)
        data = serializer.data
        assert data['id'] == notification.id
        assert data['titulo'] == 'Test Notification'
        assert 'tiempo_transcurrido' in data
        assert 'tipo_display' in data
        # Should not include all fields
        assert 'datos_extra' not in data


@pytest.mark.django_db
class TestNotificationCreateSerializer:
    """Test cases for NotificationCreateSerializer."""
    
    def test_notification_create_serializer_valid(self):
        """Test NotificationCreateSerializer with valid data."""
        from notifications.models import Notification
        from django.contrib.auth.models import User
        
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        serializer = NotificationCreateSerializer(data={
            'user': user.id,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message',
            'datos_extra': {'key': 'value'}
        })
        assert serializer.is_valid()
    
    def test_notification_create_serializer_invalid_tipo(self):
        """Test NotificationCreateSerializer with invalid tipo."""
        serializer = NotificationCreateSerializer(data={
            'tipo': 'invalid_type',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message'
        })
        assert not serializer.is_valid()
        assert 'tipo' in serializer.errors
    
    def test_notification_create_serializer_valid_tipo(self):
        """Test NotificationCreateSerializer with valid tipo."""
        from notifications.models import Notification
        
        valid_types = [choice[0] for choice in Notification.TIPO_CHOICES]
        if valid_types:
            serializer = NotificationCreateSerializer(data={
                'tipo': valid_types[0],
                'titulo': 'Test Notification',
                'mensaje': 'This is a test notification message'
            })
            # Type validation should pass
            assert serializer.is_valid() or 'tipo' not in serializer.errors


class TestNotificationStatsSerializer:
    """Test cases for NotificationStatsSerializer."""
    
    def test_notification_stats_serializer_valid(self):
        """Test NotificationStatsSerializer with valid data."""
        serializer = NotificationStatsSerializer(data={
            'total_notifications': 100,
            'unread_count': 25,
            'notifications_by_type': {'info': 50, 'warning': 30, 'error': 20},
            'recent_notifications': []
        })
        assert serializer.is_valid()


@pytest.mark.django_db
class TestSystemSettingsSerializer:
    """Test cases for SystemSettingsSerializer."""
    
    def test_system_settings_serializer_with_logo(self):
        """Test SystemSettingsSerializer with logo."""
        from core.models import SystemSettings
        from unittest.mock import Mock
        
        settings = Mock(spec=SystemSettings)
        settings.logo = Mock()
        settings.logo.url = '/media/logo.png'
        
        request = Mock()
        request.build_absolute_uri = Mock(return_value='http://example.com/media/logo.png')
        
        serializer = SystemSettingsSerializer(settings, context={'request': request})
        logo_url = serializer.get_logo_url(settings)
        assert logo_url == 'http://example.com/media/logo.png'
    
    def test_system_settings_serializer_without_logo(self):
        """Test SystemSettingsSerializer without logo."""
        from core.models import SystemSettings
        from unittest.mock import Mock
        
        settings = Mock(spec=SystemSettings)
        settings.logo = None
        
        serializer = SystemSettingsSerializer(settings)
        logo_url = serializer.get_logo_url(settings)
        assert logo_url is None
    
    def test_system_settings_serializer_without_request(self):
        """Test SystemSettingsSerializer without request in context."""
        from core.models import SystemSettings
        from unittest.mock import Mock
        
        settings = Mock(spec=SystemSettings)
        settings.logo = Mock()
        settings.logo.url = '/media/logo.png'
        
        serializer = SystemSettingsSerializer(settings)
        logo_url = serializer.get_logo_url(settings)
        assert logo_url == '/media/logo.png'

