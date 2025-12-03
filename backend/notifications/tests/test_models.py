"""
Tests for Notifications Models.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from notifications.models import Notification


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestNotification:
    """Tests for Notification model."""

    def test_create_notification(self, user):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='This is a test notification',
            leida=False
        )
        
        assert notification.user == user
        assert notification.tipo == 'info'
        assert notification.titulo == 'Test Notification'
        assert notification.leida is False

    def test_notification_str_representation(self, user):
        """Test string representation."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message'
        )
        
        assert user.username in str(notification)
        assert 'Test Notification' in str(notification)

    def test_mark_as_read(self, user):
        """Test mark_as_read method."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            leida=False
        )
        
        assert notification.leida is False
        assert notification.fecha_lectura is None
        
        notification.mark_as_read()
        
        assert notification.leida is True
        assert notification.fecha_lectura is not None

    def test_mark_as_read_already_read(self, user):
        """Test mark_as_read when already read."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            leida=True,
            fecha_lectura=timezone.now() - timedelta(hours=1)
        )
        
        old_fecha_lectura = notification.fecha_lectura
        
        notification.mark_as_read()
        
        # Should not change fecha_lectura if already read
        assert notification.fecha_lectura == old_fecha_lectura

    def test_tiempo_transcurrido_property_days(self, user):
        """Test tiempo_transcurrido property for days."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            fecha_creacion=timezone.now() - timedelta(days=2)
        )
        
        tiempo = notification.tiempo_transcurrido
        assert 'día' in tiempo or 'day' in tiempo.lower()

    def test_tiempo_transcurrido_property_hours(self, user):
        """Test tiempo_transcurrido property for hours."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            fecha_creacion=timezone.now() - timedelta(hours=2)
        )
        
        tiempo = notification.tiempo_transcurrido
        assert 'hora' in tiempo or 'hour' in tiempo.lower()

    def test_tiempo_transcurrido_property_minutes(self, user):
        """Test tiempo_transcurrido property for minutes."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            fecha_creacion=timezone.now() - timedelta(minutes=5)
        )
        
        tiempo = notification.tiempo_transcurrido
        assert 'minuto' in tiempo or 'minute' in tiempo.lower()

    def test_tiempo_transcurrido_property_moments(self, user):
        """Test tiempo_transcurrido property for recent notifications."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            fecha_creacion=timezone.now() - timedelta(seconds=30)
        )
        
        tiempo = notification.tiempo_transcurrido
        assert 'momentos' in tiempo or 'moment' in tiempo.lower()

    def test_tipo_choices(self, user):
        """Test tipo choices."""
        valid_types = ['info', 'warning', 'error', 'success', 'defect_alert',
                      'report_ready', 'training_complete', 'welcome']
        
        for tipo in valid_types:
            notification = Notification.objects.create(
                user=user,
                tipo=tipo,
                titulo=f'Test {tipo}',
                mensaje='Test message'
            )
            assert notification.tipo == tipo

    def test_datos_extra_json_field(self, user):
        """Test datos_extra JSON field."""
        datos = {'key1': 'value1', 'key2': 123, 'key3': [1, 2, 3]}
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            datos_extra=datos
        )
        
        assert notification.datos_extra == datos

    def test_fecha_creacion_auto_now_add(self, user):
        """Test that fecha_creacion is automatically set."""
        before = timezone.now()
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message'
        )
        after = timezone.now()
        
        assert before <= notification.fecha_creacion <= after

    def test_leida_default(self, user):
        """Test that leida defaults to False."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message'
        )
        
        assert notification.leida is False

    def test_fecha_lectura_none_when_not_read(self, user):
        """Test that fecha_lectura is None when not read."""
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message'
        )
        
        assert notification.fecha_lectura is None

