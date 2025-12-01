"""
Tests for notification views.
Covers NotificationListCreateView, NotificationDetailView, NotificationMarkReadView, 
NotificationMarkAllReadView, NotificationUnreadCountView, NotificationStatsView, and NotificationCreateView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.views.notifications.notification_views import (
    NotificationListCreateView,
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationUnreadCountView,
    NotificationStatsView,
    NotificationCreateView
)


@pytest.fixture
def user(db):
    """Create user for tests."""
    return User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create admin user for tests."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.mark.django_db
class TestNotificationListCreateView:
    """Tests for NotificationListCreateView."""
    
    def test_list_notifications_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/notifications/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_list_notifications_model_not_available(self, mock_notification, api_client, user):
        """Test listing notifications when model is not available."""
        mock_notification.return_value = None
        mock_notification.objects = None
        
        api_client.force_authenticate(user=user)
        
        view = NotificationListCreateView()
        request = Mock()
        request.user = user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []
        assert response.data['count'] == 0
    
    def test_list_notifications_with_filters(self, api_client, user, db):
        """Test listing notifications with filters."""
        from notifications.models import Notification
        
        Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test Notification',
            mensaje='Test message',
            leida=False
        )
        
        api_client.force_authenticate(user=user)
        
        view = NotificationListCreateView()
        request = Mock()
        request.user = user
        request.GET = {'tipo': 'info', 'leida': 'false', 'search': 'Test'}
        
        with patch.object(view, 'paginate_queryset') as mock_paginate:
            mock_paginate.return_value = Mock(
                status_code=status.HTTP_200_OK,
                data={'results': [], 'count': 0}
            )
            response = view.get(request)
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestNotificationDetailView:
    """Tests for NotificationDetailView."""
    
    def test_get_notification_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/notifications/1/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_notification_not_found(self, api_client, user):
        """Test getting non-existent notification."""
        from notifications.models import Notification
        
        api_client.force_authenticate(user=user)
        
        view = NotificationDetailView()
        request = Mock()
        request.user = user
        
        response = view.get(request, notification_id=999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data
    
    def test_get_notification_success(self, api_client, user, db):
        """Test getting notification successfully."""
        from notifications.models import Notification
        
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test',
            mensaje='Test message'
        )
        
        api_client.force_authenticate(user=user)
        
        view = NotificationDetailView()
        request = Mock()
        request.user = user
        
        with patch('api.views.notifications.notification_views.NotificationSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.data = {'id': notification.id, 'titulo': 'Test'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.get(request, notification_id=notification.id)
            
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestNotificationMarkReadView:
    """Tests for NotificationMarkReadView."""
    
    def test_mark_read_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot mark notifications as read."""
        response = api_client.post('/api/v1/notifications/1/mark-read/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_mark_read_not_found(self, api_client, user):
        """Test marking non-existent notification as read."""
        api_client.force_authenticate(user=user)
        
        view = NotificationMarkReadView()
        request = Mock()
        request.user = user
        
        response = view.post(request, notification_id=999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_mark_read_success(self, api_client, user, db):
        """Test marking notification as read successfully."""
        from notifications.models import Notification
        
        notification = Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test',
            mensaje='Test message',
            leida=False
        )
        
        api_client.force_authenticate(user=user)
        
        view = NotificationMarkReadView()
        request = Mock()
        request.user = user
        
        response = view.post(request, notification_id=notification.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        notification.refresh_from_db()
        assert notification.leida is True


@pytest.mark.django_db
class TestNotificationMarkAllReadView:
    """Tests for NotificationMarkAllReadView."""
    
    def test_mark_all_read_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot mark all notifications as read."""
        response = api_client.post('/api/v1/notifications/mark-all-read/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_mark_all_read_success(self, api_client, user, db):
        """Test marking all notifications as read successfully."""
        from notifications.models import Notification
        
        Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test 1',
            mensaje='Message 1',
            leida=False
        )
        Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test 2',
            mensaje='Message 2',
            leida=False
        )
        
        api_client.force_authenticate(user=user)
        
        view = NotificationMarkAllReadView()
        request = Mock()
        request.user = user
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'


@pytest.mark.django_db
class TestNotificationUnreadCountView:
    """Tests for NotificationUnreadCountView."""
    
    def test_unread_count_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot get unread count."""
        response = api_client.get('/api/v1/notifications/unread-count/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unread_count_success(self, api_client, user, db):
        """Test getting unread count successfully."""
        from notifications.models import Notification
        
        Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test',
            mensaje='Test message',
            leida=False
        )
        
        api_client.force_authenticate(user=user)
        
        view = NotificationUnreadCountView()
        request = Mock()
        request.user = user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'unread_count' in response.data
        assert response.data['unread_count'] >= 1


@pytest.mark.django_db
class TestNotificationStatsView:
    """Tests for NotificationStatsView."""
    
    def test_stats_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot get stats."""
        response = api_client.get('/api/v1/notifications/stats/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_stats_success(self, api_client, user, db):
        """Test getting notification stats successfully."""
        from notifications.models import Notification
        
        Notification.objects.create(
            user=user,
            tipo='info',
            titulo='Test',
            mensaje='Test message'
        )
        
        api_client.force_authenticate(user=user)
        
        view = NotificationStatsView()
        request = Mock()
        request.user = user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_notifications' in response.data
        assert 'unread_count' in response.data


@pytest.mark.django_db
class TestNotificationCreateView:
    """Tests for NotificationCreateView."""
    
    def test_create_notification_requires_admin(self, api_client, user):
        """Test that non-admin users cannot create notifications."""
        api_client.force_authenticate(user=user)
        response = api_client.post('/api/v1/notifications/create/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_notification_success(self, api_client, admin_user, user, db):
        """Test creating notification successfully."""
        api_client.force_authenticate(user=admin_user)
        
        view = NotificationCreateView()
        request = Mock()
        request.user = admin_user
        request.data = {
            'user': user.id,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'Test message'
        }
        
        with patch('api.views.notifications.notification_views.NotificationCreateSerializer') as mock_serializer:
            from notifications.models import Notification
            
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            notification = Notification.objects.create(
                user=user,
                tipo='info',
                titulo='Test',
                mensaje='Test message'
            )
            mock_serializer_instance.save.return_value = notification
            mock_serializer.return_value = mock_serializer_instance
            
            with patch('api.views.notifications.notification_views.NotificationSerializer') as mock_response_serializer:
                mock_response_serializer_instance = MagicMock()
                mock_response_serializer_instance.data = {'id': notification.id}
                mock_response_serializer.return_value = mock_response_serializer_instance
                
                response = view.post(request)
                
                assert response.status_code == status.HTTP_201_CREATED

