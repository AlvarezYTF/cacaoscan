"""
Tests for Common Serializers.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from api.serializers.common_serializers import (
    ErrorResponseSerializer,
    DatasetStatsSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
    SystemSettingsSerializer
)
from notifications.models import Notification
from core.models import SystemSettings


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def notification(user):
    """Create a test notification."""
    return Notification.objects.create(
        user=user,
        tipo='info',
        titulo='Test Notification',
        mensaje='This is a test notification message'
    )


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.mark.django_db
class TestErrorResponseSerializer:
    """Tests for ErrorResponseSerializer."""

    def test_serialize_error_response(self):
        """Test serializing error response."""
        data = {
            'error': 'Test error',
            'status': '400'
        }
        serializer = ErrorResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['error'] == 'Test error'


@pytest.mark.django_db
class TestDatasetStatsSerializer:
    """Tests for DatasetStatsSerializer."""

    def test_serialize_dataset_stats(self):
        """Test serializing dataset statistics."""
        data = {
            'total_records': 100,
            'valid_records': 95,
            'missing_images': 5,
            'missing_ids': [1, 2, 3],
            'dimensions_stats': {'alto': {'mean': 20.5}}
        }
        serializer = DatasetStatsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['total_records'] == 100


@pytest.mark.django_db
class TestNotificationSerializer:
    """Tests for NotificationSerializer."""

    def test_serialize_notification(self, notification):
        """Test serializing notification."""
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        assert data['id'] == notification.id
        assert data['titulo'] == notification.titulo
        assert 'tiempo_transcurrido' in data

    def test_validate_titulo_too_short(self, user):
        """Test title validation with too short title."""
        data = {
            'user': user.id,
            'tipo': 'info',
            'titulo': 'AB',  # Too short
            'mensaje': 'This is a valid message with enough characters'
        }
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'titulo' in serializer.errors

    def test_validate_mensaje_too_short(self, user):
        """Test message validation with too short message."""
        data = {
            'user': user.id,
            'tipo': 'info',
            'titulo': 'Valid Title',
            'mensaje': 'Short'  # Too short
        }
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'mensaje' in serializer.errors

    def test_validate_titulo_valid(self, user):
        """Test title validation with valid title."""
        data = {
            'user': user.id,
            'tipo': 'info',
            'titulo': 'Valid Title',
            'mensaje': 'This is a valid message with enough characters'
        }
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestNotificationListSerializer:
    """Tests for NotificationListSerializer."""

    def test_serialize_notification_list(self, notification):
        """Test serializing notification for list."""
        serializer = NotificationListSerializer(notification)
        data = serializer.data
        
        assert data['id'] == notification.id
        assert data['titulo'] == notification.titulo
        assert 'tiempo_transcurrido' in data
        # Should not include all fields
        assert 'datos_extra' not in data


@pytest.mark.django_db
class TestNotificationCreateSerializer:
    """Tests for NotificationCreateSerializer."""

    def test_create_notification(self, user):
        """Test creating notification."""
        data = {
            'user': user.id,
            'tipo': 'info',
            'titulo': 'New Notification',
            'mensaje': 'This is a new notification message'
        }
        serializer = NotificationCreateSerializer(data=data)
        assert serializer.is_valid()
        
        notification = serializer.save()
        assert notification.user == user
        assert notification.titulo == 'New Notification'

    def test_validate_tipo_invalid(self, user):
        """Test type validation with invalid type."""
        data = {
            'user': user.id,
            'tipo': 'invalid_type',
            'titulo': 'Test',
            'mensaje': 'This is a valid message'
        }
        serializer = NotificationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'tipo' in serializer.errors


@pytest.mark.django_db
class TestNotificationStatsSerializer:
    """Tests for NotificationStatsSerializer."""

    def test_serialize_notification_stats(self):
        """Test serializing notification statistics."""
        data = {
            'total_notifications': 100,
            'unread_count': 25,
            'notifications_by_type': {'info': 50, 'warning': 30},
            'recent_notifications': []
        }
        serializer = NotificationStatsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['total_notifications'] == 100


@pytest.mark.django_db
class TestSystemSettingsSerializer:
    """Tests for SystemSettingsSerializer."""

    def test_serialize_system_settings(self):
        """Test serializing system settings."""
        settings = SystemSettings.get_singleton()
        serializer = SystemSettingsSerializer(settings)
        data = serializer.data
        
        assert data['nombre_sistema'] == settings.nombre_sistema
        assert 'logo_url' in data

    def test_get_logo_url_with_logo(self, request_factory):
        """Test getting logo URL when logo exists."""
        settings = SystemSettings.get_singleton()
        # Mock logo
        settings.logo = 'test_logo.png'
        
        request = request_factory.get('/')
        serializer = SystemSettingsSerializer(settings, context={'request': request})
        data = serializer.data
        
        # Logo URL should be in data
        assert 'logo_url' in data

    def test_get_logo_url_without_logo(self):
        """Test getting logo URL when no logo."""
        settings = SystemSettings.get_singleton()
        settings.logo = None
        
        serializer = SystemSettingsSerializer(settings)
        data = serializer.data
        
        assert data.get('logo_url') is None

