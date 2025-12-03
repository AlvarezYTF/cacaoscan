"""
Unit tests for notification views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_PASSWORD,
)


class NotificationListCreateViewTest(APITestCase):
    """Tests for NotificationListCreateView."""
    
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
        self.url = reverse('notifications-list')
    
    def test_notification_list_requires_authentication(self):
        """Test that notification list requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_list_success(self, mock_notification):
        """Test successful notification list retrieval."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_notification.objects.filter.return_value = mock_queryset
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_list_with_filters(self, mock_notification):
        """Test notification list with filters."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_notification.objects.filter.return_value = mock_queryset
        
        response = self.client.get(self.url, {
            'tipo': 'info',
            'leida': 'false',
            'search': 'test'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.notifications.notification_views.Notification', None)
    def test_notification_list_model_not_available(self):
        """Test notification list when model is not available."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
    
    def test_notification_create_requires_admin(self):
        """Test that notification create requires admin."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_create_success(self, mock_notification):
        """Test successful notification creation."""
        mock_notification.TIPO_CHOICES = [
            ('info', 'Información'),
            ('warning', 'Advertencia')
        ]
        mock_instance = Mock()
        mock_instance.id = 1
        mock_notification.objects.create.return_value = mock_instance
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {
            'user': self.user.id,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class NotificationDetailViewTest(APITestCase):
    """Tests for NotificationDetailView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('notification-detail', kwargs={'pk': 1})
    
    def test_notification_detail_requires_authentication(self):
        """Test that notification detail requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_detail_success(self, mock_notification):
        """Test successful notification detail retrieval."""
        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.user = self.user
        mock_notification.objects.get.return_value = mock_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_detail_not_found(self, mock_notification):
        """Test notification detail with non-existent notification."""
        mock_notification.DoesNotExist = Exception
        mock_notification.objects.get.side_effect = mock_notification.DoesNotExist
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class NotificationMarkReadViewTest(APITestCase):
    """Tests for NotificationMarkReadView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('notification-mark-read', kwargs={'pk': 1})
    
    def test_notification_mark_read_requires_authentication(self):
        """Test that mark read requires authentication."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_mark_read_success(self, mock_notification):
        """Test successful notification mark as read."""
        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.user = self.user
        mock_instance.leida = False
        mock_notification.objects.get.return_value = mock_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_instance.leida)


class NotificationMarkAllReadViewTest(APITestCase):
    """Tests for NotificationMarkAllReadView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('notification-mark-all-read')
    
    def test_notification_mark_all_read_requires_authentication(self):
        """Test that mark all read requires authentication."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_mark_all_read_success(self, mock_notification):
        """Test successful mark all notifications as read."""
        mock_queryset = Mock()
        mock_queryset.update.return_value = 5
        mock_notification.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('marked_count', response.data)


class NotificationUnreadCountViewTest(APITestCase):
    """Tests for NotificationUnreadCountView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('notification-unread-count')
    
    def test_notification_unread_count_requires_authentication(self):
        """Test that unread count requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_unread_count_success(self, mock_notification):
        """Test successful unread count retrieval."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 3
        mock_notification.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)
        self.assertEqual(response.data['unread_count'], 3)


class NotificationStatsViewTest(APITestCase):
    """Tests for NotificationStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('notification-stats')
    
    def test_notification_stats_requires_authentication(self):
        """Test that notification stats requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_stats_success(self, mock_notification):
        """Test successful notification stats retrieval."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 10
        mock_queryset.filter.return_value.count.return_value = 5
        mock_queryset.values.return_value.annotate.return_value = []
        mock_notification.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_notifications', response.data)


class NotificationCreateViewTest(APITestCase):
    """Tests for NotificationCreateView."""
    
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
        self.url = reverse('admin-notification-create')
    
    def test_notification_create_requires_admin(self):
        """Test that notification create requires admin."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.notifications.notification_views.Notification')
    def test_notification_create_success(self, mock_notification):
        """Test successful notification creation by admin."""
        mock_notification.TIPO_CHOICES = [
            ('info', 'Información'),
            ('warning', 'Advertencia')
        ]
        mock_instance = Mock()
        mock_instance.id = 1
        mock_notification.objects.create.return_value = mock_instance
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.post(self.url, {
            'user': self.user.id,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

