"""
Unit tests for admin audit views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

from api.views.admin.audit_views import (
    ActivityLogListView,
    LoginHistoryListView,
    AuditStatsView
)
from audit.models import LoginHistory
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_PASSWORD,
)


class ActivityLogListViewTest(APITestCase):
    """Tests for ActivityLogListView."""
    
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
        self.url = reverse('admin-activity-logs')
    
    def test_activity_log_list_requires_authentication(self):
        """Test that activity log list requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_activity_log_list_requires_admin(self):
        """Test that activity log list requires admin permissions."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_activity_log_list_success(self, mock_activity_log):
        """Test successful activity log list retrieval."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_queryset = Mock()
        mock_queryset.select_related.return_value.order_by.return_value = []
        mock_activity_log.objects.all.return_value = mock_queryset
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_activity_log_list_with_filters(self, mock_activity_log):
        """Test activity log list with filters."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value.order_by.return_value = mock_queryset
        mock_activity_log.objects.all.return_value = mock_queryset
        
        response = self.client.get(self.url, {
            'usuario': 'test',
            'accion': 'create',
            'modelo': 'Finca',
            'ip_address': '127.0.0.1'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_activity_log_list_invalid_date_format(self, mock_activity_log):
        """Test activity log list with invalid date format."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_queryset = Mock()
        mock_queryset.select_related.return_value.order_by.return_value = mock_queryset
        mock_activity_log.objects.all.return_value = mock_queryset
        
        response = self.client.get(self.url, {
            'fecha_desde': 'invalid-date'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_activity_log_list_with_date_filters(self, mock_activity_log):
        """Test activity log list with date filters."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value.order_by.return_value = mock_queryset
        mock_activity_log.objects.all.return_value = mock_queryset
        
        today = timezone.now().date()
        response = self.client.get(self.url, {
            'fecha_desde': today.isoformat(),
            'fecha_hasta': today.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.admin.audit_views.ActivityLog', None)
    def test_activity_log_list_model_not_available(self):
        """Test activity log list when model is not available."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class LoginHistoryListViewTest(APITestCase):
    """Tests for LoginHistoryListView."""
    
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
        self.url = reverse('admin-login-history')
    
    def test_login_history_list_requires_authentication(self):
        """Test that login history list requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_history_list_requires_admin(self):
        """Test that login history list requires admin permissions."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_login_history_list_success(self):
        """Test successful login history list retrieval."""
        LoginHistory.objects.create(
            usuario=self.user,
            ip_address='127.0.0.1',
            user_agent='test',
            login_time=timezone.now(),
            success=True
        )
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
    
    def test_login_history_list_with_filters(self):
        """Test login history list with filters."""
        LoginHistory.objects.create(
            usuario=self.user,
            ip_address='127.0.0.1',
            user_agent='test',
            login_time=timezone.now(),
            success=True
        )
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url, {
            'usuario': TEST_USER_USERNAME,
            'ip_address': '127.0.0.1',
            'success': 'true'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_history_list_invalid_date_format(self):
        """Test login history list with invalid date format."""
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url, {
            'fecha_desde': 'invalid-date'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class AuditStatsViewTest(APITestCase):
    """Tests for AuditStatsView."""
    
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
        self.url = reverse('admin-audit-stats')
    
    def test_audit_stats_requires_authentication(self):
        """Test that audit stats requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_audit_stats_requires_admin(self):
        """Test that audit stats requires admin permissions."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_audit_stats_success(self, mock_activity_log):
        """Test successful audit stats retrieval."""
        LoginHistory.objects.create(
            usuario=self.user,
            ip_address='127.0.0.1',
            user_agent='test',
            login_time=timezone.now(),
            success=True
        )
        
        mock_activity_log.objects.count.return_value = 0
        mock_activity_log.objects.filter.return_value.count.return_value = 0
        mock_activity_log.objects.values.return_value.annotate.return_value.values_list.return_value = []
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('activity_log', response.data)
        self.assertIn('login_history', response.data)
        self.assertIn('generated_at', response.data)
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_audit_stats_with_data(self, mock_activity_log):
        """Test audit stats with actual data."""
        LoginHistory.objects.create(
            usuario=self.user,
            ip_address='127.0.0.1',
            user_agent='test',
            login_time=timezone.now(),
            success=True,
            session_duration=timedelta(minutes=30)
        )
        
        LoginHistory.objects.create(
            usuario=self.user,
            ip_address='127.0.0.1',
            user_agent='test',
            login_time=timezone.now(),
            success=False
        )
        
        mock_activity_log.objects.count.return_value = 5
        mock_activity_log.objects.filter.return_value.count.return_value = 2
        mock_activity_log.objects.values.return_value.annotate.return_value.values_list.return_value = []
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['login_history']['total_logins'], 1)

