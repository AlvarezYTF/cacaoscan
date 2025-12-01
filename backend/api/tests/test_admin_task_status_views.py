"""
Unit tests for admin task status views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)


class TaskStatusViewTest(APITestCase):
    """Tests for TaskStatusView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_task_status_requires_authentication(self):
        """Test that task status requires authentication."""
        url = reverse('admin-task-status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_pending(self, mock_async_result):
        """Test task status for pending task."""
        mock_result = Mock()
        mock_result.state = 'PENDING'
        mock_async_result.return_value = mock_result
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('admin-task-status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertIn('message', response.data)
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_progress(self, mock_async_result):
        """Test task status for task in progress."""
        mock_result = Mock()
        mock_result.state = 'PROGRESS'
        mock_result.info = {'current': 50, 'total': 100}
        mock_async_result.return_value = mock_result
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('admin-task-status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PROGRESS')
        self.assertIn('progress', response.data)
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_success(self, mock_async_result):
        """Test task status for successful task."""
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {'result': 'success'}
        mock_async_result.return_value = mock_result
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('admin-task-status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')
        self.assertIn('result', response.data)
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_failure(self, mock_async_result):
        """Test task status for failed task."""
        mock_result = Mock()
        mock_result.state = 'FAILURE'
        mock_result.info = 'Task failed with error'
        mock_async_result.return_value = mock_result
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('admin-task-status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'FAILURE')
        self.assertIn('error', response.data)
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_exception(self, mock_async_result):
        """Test task status with exception."""
        mock_async_result.side_effect = Exception('Task not found')
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('admin-task-status', kwargs={'task_id': 'invalid-task-id'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

