"""
Tests for task status views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status
from celery.result import AsyncResult
from django.contrib.auth.models import User

from api.views.admin.task_status_views import TaskStatusView


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def user(db):
    """Create a test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestTaskStatusView:
    """Tests for TaskStatusView."""
    
    def test_get_task_status_pending(self, request_factory, user):
        """Test getting status of pending task."""
        view = TaskStatusView()
        request = request_factory.get('/api/admin/tasks/status/task-123/')
        request.user = user
        
        with patch('api.views.admin.task_status_views.AsyncResult') as mock_async_result:
            mock_result = Mock()
            mock_result.state = 'PENDING'
            mock_async_result.return_value = mock_result
            
            response = view.get(request, task_id='task-123')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'PENDING'
            assert 'message' in response.data
            assert 'Tarea pendiente' in response.data['message']
    
    def test_get_task_status_progress(self, request_factory, user):
        """Test getting status of task in progress."""
        view = TaskStatusView()
        request = request_factory.get('/api/admin/tasks/status/task-123/')
        request.user = user
        
        with patch('api.views.admin.task_status_views.AsyncResult') as mock_async_result:
            mock_result = Mock()
            mock_result.state = 'PROGRESS'
            mock_result.info = {'progress': 50, 'status': 'Processing...'}
            mock_async_result.return_value = mock_result
            
            response = view.get(request, task_id='task-123')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'PROGRESS'
            assert 'progress' in response.data
    
    def test_get_task_status_success(self, request_factory, user):
        """Test getting status of successful task."""
        view = TaskStatusView()
        request = request_factory.get('/api/admin/tasks/status/task-123/')
        request.user = user
        
        with patch('api.views.admin.task_status_views.AsyncResult') as mock_async_result:
            mock_result = Mock()
            mock_result.state = 'SUCCESS'
            mock_result.result = {'status': 'completed', 'data': 'result'}
            mock_async_result.return_value = mock_result
            
            response = view.get(request, task_id='task-123')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'SUCCESS'
            assert 'result' in response.data
            assert 'message' in response.data
            assert 'completada exitosamente' in response.data['message']
    
    def test_get_task_status_failure(self, request_factory, user):
        """Test getting status of failed task."""
        view = TaskStatusView()
        request = request_factory.get('/api/admin/tasks/status/task-123/')
        request.user = user
        
        with patch('api.views.admin.task_status_views.AsyncResult') as mock_async_result:
            mock_result = Mock()
            mock_result.state = 'FAILURE'
            mock_result.info = Exception("Task failed")
            mock_async_result.return_value = mock_result
            
            response = view.get(request, task_id='task-123')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'FAILURE'
            assert 'error' in response.data
            assert 'message' in response.data
            assert 'falló' in response.data['message']
    
    def test_get_task_status_unknown(self, request_factory, user):
        """Test getting status of task with unknown state."""
        view = TaskStatusView()
        request = request_factory.get('/api/admin/tasks/status/task-123/')
        request.user = user
        
        with patch('api.views.admin.task_status_views.AsyncResult') as mock_async_result:
            mock_result = Mock()
            mock_result.state = 'UNKNOWN_STATE'
            mock_async_result.return_value = mock_result
            
            response = view.get(request, task_id='task-123')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'UNKNOWN_STATE'
            assert 'message' in response.data
            assert 'Estado desconocido' in response.data['message']
    
    def test_get_task_status_error(self, request_factory, user):
        """Test error handling when getting task status."""
        view = TaskStatusView()
        request = request_factory.get('/api/admin/tasks/status/task-123/')
        request.user = user
        
        with patch('api.views.admin.task_status_views.AsyncResult', side_effect=Exception("Connection error")):
            response = view.get(request, task_id='task-123')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data
            assert 'details' in response.data


