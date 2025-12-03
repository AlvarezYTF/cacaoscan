"""
Tests for Auth App user management views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
    TEST_OTHER_USER_USERNAME,
    TEST_USER_EMAIL,
)


class UserListViewTest(APITestCase):
    """Tests for UserListView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.analyst_group = Group.objects.create(name='analyst')
        self.analyst_user = User.objects.create_user(
            username='analystuser',
            email='analyst@example.com',
            password=TEST_USER_PASSWORD
        )
        self.analyst_user.groups.add(self.analyst_group)
        
        self.url = reverse('user-list')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_users_as_admin_success(self):
        """Test admin listing users successfully."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 4)
    
    def test_list_users_with_role_filter(self):
        """Test listing users with role filter."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, {'role': 'admin'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_users_with_analyst_filter(self):
        """Test listing users with analyst filter."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, {'role': 'analyst'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_users_with_farmer_filter(self):
        """Test listing users with farmer filter."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, {'role': 'farmer'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_users_with_is_active_filter(self):
        """Test listing users with is_active filter."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, {'is_active': 'true'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_users_with_search(self):
        """Test listing users with search."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, {'search': TEST_USER_USERNAME}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_users_with_date_filters(self):
        """Test listing users with date filters."""
        headers = self._get_auth_headers(self.admin_user)
        
        today = timezone.now().date()
        date_from = (today - timedelta(days=7)).isoformat()
        date_to = today.isoformat()
        
        response = self.client.get(self.url, {'date_from': date_from, 'date_to': date_to}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_users_with_pagination(self):
        """Test listing users with pagination."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, {'page': 1, 'page_size': 2}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
    
    def test_list_users_permission_denied(self):
        """Test non-admin cannot list users."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_list_users_unauthenticated(self):
        """Test listing users without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewTest(APITestCase):
    """Tests for UserDetailView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_user_detail_success(self):
        """Test getting user detail successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-detail', kwargs={'user_id': self.user.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertIn('stats', response.data)
    
    def test_get_user_detail_not_found(self):
        """Test getting non-existent user."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-detail', kwargs={'user_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_user_detail_permission_denied(self):
        """Test non-admin cannot get user detail."""
        headers = self._get_auth_headers(self.user)
        url = reverse('user-detail', kwargs={'user_id': self.user.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)


class UserUpdateViewTest(APITestCase):
    """Tests for UserUpdateView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.analyst_group = Group.objects.create(name='analyst')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_update_user_success(self):
        """Test updating user successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-update', kwargs={'user_id': self.user.id})
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')
    
    def test_update_user_with_groups(self):
        """Test updating user with groups."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-update', kwargs={'user_id': self.user.id})
        
        update_data = {
            'groups': ['analyst']
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.groups.filter(name='analyst').exists())
    
    def test_update_user_self_deactivation(self):
        """Test user cannot deactivate themselves."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-update', kwargs={'user_id': self.admin_user.id})
        
        update_data = {
            'is_active': False
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_user_duplicate_email(self):
        """Test updating user with duplicate email."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=TEST_USER_PASSWORD
        )
        
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-update', kwargs={'user_id': self.user.id})
        
        update_data = {
            'email': 'other@example.com'
        }
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_user_permission_denied(self):
        """Test non-admin cannot update user."""
        headers = self._get_auth_headers(self.user)
        url = reverse('user-update', kwargs={'user_id': self.user.id})
        
        update_data = {'first_name': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_update_user_not_found(self):
        """Test updating non-existent user."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-update', kwargs={'user_id': 99999})
        
        update_data = {'first_name': 'Updated'}
        
        response = self.client.patch(url, update_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class UserDeleteViewTest(APITestCase):
    """Tests for UserDeleteView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.other_admin = User.objects.create_superuser(
            username='otheradmin',
            email='otheradmin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_delete_user_success(self):
        """Test deleting user successfully."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-delete', kwargs={'user_id': self.user.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('deleted_user', response.data)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
    
    def test_delete_user_self(self):
        """Test user cannot delete themselves."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-delete', kwargs={'user_id': self.admin_user.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())
    
    def test_delete_superuser_by_non_superuser(self):
        """Test non-superuser cannot delete superuser."""
        regular_admin = User.objects.create_user(
            username='regularadmin',
            email='regularadmin@example.com',
            password=TEST_USER_PASSWORD,
            is_staff=True,
            is_superuser=False
        )
        
        headers = self._get_auth_headers(regular_admin)
        url = reverse('user-delete', kwargs={'user_id': self.other_admin.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
        self.assertTrue(User.objects.filter(id=self.other_admin.id).exists())
    
    def test_delete_user_permission_denied(self):
        """Test non-admin cannot delete user."""
        headers = self._get_auth_headers(self.user)
        url = reverse('user-delete', kwargs={'user_id': self.user.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user."""
        headers = self._get_auth_headers(self.admin_user)
        url = reverse('user-delete', kwargs={'user_id': 99999})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class UserStatsViewTest(APITestCase):
    """Tests for UserStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.analyst_group = Group.objects.create(name='analyst')
        self.analyst_user = User.objects.create_user(
            username='analystuser',
            email='analyst@example.com',
            password=TEST_USER_PASSWORD
        )
        self.analyst_user.groups.add(self.analyst_group)
        
        self.url = reverse('users-stats')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_user_stats_success(self):
        """Test getting user stats successfully."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('active', response.data)
        self.assertIn('inactive', response.data)
        self.assertIn('online', response.data)
        self.assertIn('new_today', response.data)
        self.assertIn('new_this_week', response.data)
        self.assertIn('new_this_month', response.data)
        self.assertIn('by_role', response.data)
        self.assertIn('verified', response.data)
    
    def test_get_user_stats_values(self):
        """Test that user stats values are correct."""
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['total'], 3)
        self.assertGreaterEqual(response.data['active'], 0)
    
    def test_get_user_stats_permission_denied(self):
        """Test non-admin cannot get user stats."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_get_user_stats_unauthenticated(self):
        """Test getting user stats without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminStatsViewTest(APITestCase):
    """Tests for AdminStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.url = reverse('admin-stats')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    @patch('auth_app.views.auth.user_views.calculate_admin_stats_task')
    def test_get_admin_stats_success(self, mock_task):
        """Test getting admin stats successfully."""
        mock_task.delay.return_value = Mock(id='test-task-id')
        
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'processing')
        mock_task.delay.assert_called_once()
    
    def test_get_admin_stats_permission_denied(self):
        """Test non-admin cannot get admin stats."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    @patch('auth_app.views.auth.user_views.calculate_admin_stats_task')
    @patch('auth_app.views.auth.user_views.StatsService')
    def test_get_admin_stats_fallback_on_error(self, mock_stats_service, mock_task):
        """Test admin stats fallback to empty stats on error."""
        mock_task.delay.side_effect = Exception('Task error')
        mock_service_instance = Mock()
        mock_service_instance.get_empty_stats.return_value = {'total': 0}
        mock_stats_service.return_value = mock_service_instance
        
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
    
    def test_get_admin_stats_unauthenticated(self):
        """Test getting admin stats without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

