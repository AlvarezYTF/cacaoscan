"""
Tests for training views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User

from api.views.ml.training_views import (
    TrainingJobListView,
    TrainingJobCreateView,
    TrainingJobStatusView
)


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def admin_user(db):
    """Create an admin user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_superuser(
        username=f'admin_{unique_id}',
        email=f'admin_{unique_id}@example.com',
        password='adminpass123'
    )


@pytest.fixture
def regular_user():
    """Create a regular user."""
    return User.objects.create_user(
        username='user',
        email='user@example.com',
        password='userpass123'
    )


@pytest.mark.django_db
class TestTrainingJobListView:
    """Tests for TrainingJobListView."""
    
    def test_get_list_admin_success(self, request_factory, admin_user):
        """Test successful retrieval of training jobs list by admin."""
        view = TrainingJobListView()
        request = request_factory.get('/api/training/jobs/')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJob') as mock_job:
                mock_job.objects.all.return_value.select_related.return_value.filter.return_value.order_by.return_value = []
                
                with patch.object(view, 'paginate_queryset') as mock_paginate:
                    mock_paginate.return_value = Mock(status_code=200, data={'results': []})
                    
                    response = view.get(request)
                    
                    assert response.status_code == 200
    
    def test_get_list_non_admin(self, request_factory, regular_user):
        """Test that non-admin users cannot access training jobs list."""
        view = TrainingJobListView()
        request = request_factory.get('/api/training/jobs/')
        request.user = regular_user
        
        with patch.object(view, 'is_admin_user', return_value=False):
            response = view.get(request)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_list_model_unavailable(self, request_factory, admin_user):
        """Test list when TrainingJob model is unavailable."""
        view = TrainingJobListView()
        request = request_factory.get('/api/training/jobs/')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJob', None):
                response = view.get(request)
                
                assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    def test_get_list_with_filters(self, request_factory, admin_user):
        """Test list with query filters."""
        view = TrainingJobListView()
        request = request_factory.get('/api/training/jobs/?status=completed&job_type=regression')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJob') as mock_job:
                mock_qs = Mock()
                mock_job.objects.all.return_value.select_related.return_value = mock_qs
                mock_qs.filter.return_value = mock_qs
                mock_qs.order_by.return_value = []
                
                with patch.object(view, 'paginate_queryset') as mock_paginate:
                    mock_paginate.return_value = Mock(status_code=200, data={'results': []})
                    
                    response = view.get(request)
                    
                    assert response.status_code == 200
                    assert mock_qs.filter.called
    
    def test_get_list_error(self, request_factory, admin_user):
        """Test error handling in list retrieval."""
        view = TrainingJobListView()
        request = request_factory.get('/api/training/jobs/')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJob') as mock_job:
                mock_query = Mock()
                mock_query.select_related.side_effect = Exception("Database error")
                mock_job.objects.all.return_value = mock_query
                response = view.get(request)
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestTrainingJobCreateView:
    """Tests for TrainingJobCreateView."""
    
    def test_create_job_admin_success(self, request_factory, admin_user):
        """Test successful creation of training job by admin."""
        from rest_framework.test import APIRequestFactory, force_authenticate
        api_factory = APIRequestFactory()
        view = TrainingJobCreateView()
        request = api_factory.post('/api/training/jobs/', {
            'job_type': 'regression',
            'model_name': 'test_model',
            'epochs': 150,
            'batch_size': 16
        }, format='json')
        force_authenticate(request, user=admin_user)
        # Initialize request to convert to DRF Request with .data attribute
        request = view.initialize_request(request)
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJob') as mock_job:
                # Create a proper mock instance for TrainingJob
                mock_job_instance = Mock()
                mock_job_instance.job_id = 'job_123'
                mock_job_instance.id = 1
                mock_job.objects.create.return_value = mock_job_instance
                
                with patch('api.views.ml.training_views.TrainingJobCreateSerializer') as mock_serializer_class:
                    mock_serializer_instance = Mock()
                    mock_serializer_class.return_value = mock_serializer_instance
                    mock_serializer_instance.is_valid.return_value = True
                    mock_serializer_instance.validated_data = {
                        'job_type': 'regression',
                        'model_name': 'test_model',
                        'epochs': 150,
                        'batch_size': 16,
                        'config_params': {}
                    }
                    
                    with patch('api.views.ml.training_views.TrainingJobSerializer') as mock_response_serializer_class:
                        mock_response_serializer_instance = Mock()
                        mock_response_serializer_instance.data = {'id': 1, 'job_id': 'job_123'}
                        mock_response_serializer_class.return_value = mock_response_serializer_instance
                        
                        # Patch the import inside the post method
                        # The import is: from api.tasks import train_model_task
                        with patch('api.tasks.train_model_task') as mock_task_func:
                            mock_task_func.delay = Mock(return_value=Mock())
                            response = view.post(request)
                            
                            assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_job_non_admin(self, request_factory, regular_user):
        """Test that non-admin users cannot create training jobs."""
        view = TrainingJobCreateView()
        request = request_factory.post('/api/training/jobs/', {}, format='json')
        request.user = regular_user
        
        with patch.object(view, 'is_admin_user', return_value=False):
            response = view.post(request)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_job_invalid_data(self, request_factory, admin_user):
        """Test creation with invalid data."""
        from rest_framework.test import APIRequestFactory, force_authenticate
        api_factory = APIRequestFactory()
        view = TrainingJobCreateView()
        request = api_factory.post('/api/training/jobs/', {'invalid': 'data'}, format='json')
        force_authenticate(request, user=admin_user)
        # Initialize request to convert to DRF Request with .data attribute
        request = view.initialize_request(request)
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJobCreateSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_class.return_value = mock_serializer_instance
                mock_serializer_instance.is_valid.return_value = False
                mock_serializer_instance.errors = {'field': ['error']}
                
                response = view.post(request)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_job_model_unavailable(self, request_factory, admin_user):
        """Test creation when TrainingJob model is unavailable."""
        view = TrainingJobCreateView()
        request = request_factory.post('/api/training/jobs/', {}, format='json')
        request.user = admin_user
        
        with patch.object(view, 'is_admin_user', return_value=True):
            with patch('api.views.ml.training_views.TrainingJob', None):
                response = view.post(request)
                
                assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.django_db
class TestTrainingJobStatusView:
    """Tests for TrainingJobStatusView."""
    
    def test_get_status_success(self, request_factory, admin_user):
        """Test successful retrieval of training job status."""
        from rest_framework.test import force_authenticate
        view = TrainingJobStatusView()
        request = request_factory.get('/api/training/jobs/job_123/')
        force_authenticate(request, user=admin_user)
        # Ensure request.user is set
        request.user = admin_user
        
        with patch('api.views.ml.training_views.TrainingJob') as mock_job:
            mock_job_instance = Mock()
            mock_job_instance.job_id = 'job_123'
            mock_job_instance.status = 'running'
            mock_job_instance.is_active = True
            mock_job_instance.logs = 'Log line 1\nLog line 2'
            mock_job_instance.created_by = admin_user
            mock_job_instance.progress_percentage = 50
            mock_job_instance.started_at = None
            # Create proper DoesNotExist exception
            class MockDoesNotExist(Exception):
                pass
            mock_job.DoesNotExist = MockDoesNotExist
            mock_query = Mock()
            mock_query.get.return_value = mock_job_instance
            mock_job.objects.select_related.return_value = mock_query
            
            with patch('api.views.ml.training_views.TrainingJobStatusSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {
                    'status': 'running',
                    'job_id': 'job_123',
                    'progress_percentage': 50
                }
                mock_serializer_class.return_value = mock_serializer_instance
                
                with patch.object(view, 'is_admin_user', return_value=True):
                    response = view.get(request, job_id='job_123')
                    
                    assert response.status_code == status.HTTP_200_OK
                    assert 'job' in response.data
    
    def test_get_status_not_found(self, request_factory, admin_user):
        """Test status retrieval when job not found."""
        view = TrainingJobStatusView()
        request = request_factory.get('/api/training/jobs/job_123/')
        request.user = admin_user
        
        with patch('api.views.ml.training_views.TrainingJob') as mock_job:
            # Create a proper DoesNotExist exception
            class MockDoesNotExist(Exception):
                pass
            mock_job.DoesNotExist = MockDoesNotExist
            mock_query = Mock()
            mock_query.get.side_effect = MockDoesNotExist()
            mock_job.objects.select_related.return_value = mock_query
            
            response = view.get(request, job_id='job_123')
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_status_permission_denied(self, request_factory, regular_user):
        """Test status retrieval when user doesn't have permission."""
        view = TrainingJobStatusView()
        request = request_factory.get('/api/training/jobs/job_123/')
        request.user = regular_user
        
        with patch('api.views.ml.training_views.TrainingJob') as mock_job:
            mock_job_instance = Mock()
            mock_job_instance.created_by = admin_user  # Different user
            mock_job.objects.select_related.return_value.get.return_value = mock_job_instance
            
            with patch.object(view, 'is_admin_user', return_value=False):
                response = view.get(request, job_id='job_123')
                
                assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_status_model_unavailable(self, request_factory, admin_user):
        """Test status retrieval when TrainingJob model is unavailable."""
        view = TrainingJobStatusView()
        request = request_factory.get('/api/training/jobs/job_123/')
        request.user = admin_user
        
        with patch('api.views.ml.training_views.TrainingJob', None):
            response = view.get(request, job_id='job_123')
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    def test_estimate_completion_completed(self, request_factory, admin_user):
        """Test completion estimation for completed job."""
        from rest_framework.test import force_authenticate
        view = TrainingJobStatusView()
        request = request_factory.get('/api/training/jobs/job_123/')
        force_authenticate(request, user=admin_user)
        # Ensure request.user is set
        request.user = admin_user
        
        with patch('api.views.ml.training_views.TrainingJob') as mock_job:
            mock_job_instance = Mock()
            mock_job_instance.job_id = 'job_123'
            mock_job_instance.status = 'completed'
            mock_job_instance.created_by = admin_user
            mock_job_instance.is_active = True
            mock_job_instance.logs = ''
            mock_job_instance.progress_percentage = 100
            mock_job_instance.started_at = None
            # Create proper DoesNotExist exception
            class MockDoesNotExist(Exception):
                pass
            mock_job.DoesNotExist = MockDoesNotExist
            mock_query = Mock()
            mock_query.get.return_value = mock_job_instance
            mock_job.objects.select_related.return_value = mock_query
            
            with patch('api.views.ml.training_views.TrainingJobStatusSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {
                    'status': 'completed',
                    'job_id': 'job_123',
                    'progress_percentage': 100
                }
                mock_serializer_class.return_value = mock_serializer_instance
                with patch.object(view, 'is_admin_user', return_value=True):
                    response = view.get(request, job_id='job_123')
                    
                    assert response.status_code == status.HTTP_200_OK
                    assert response.data['status_details']['estimated_completion'] == "Completado"
    
    def test_estimate_completion_in_progress(self, request_factory, admin_user):
        """Test completion estimation for job in progress."""
        from rest_framework.test import force_authenticate
        view = TrainingJobStatusView()
        request = request_factory.get('/api/training/jobs/job_123/')
        force_authenticate(request, user=admin_user)
        # Ensure request.user is set
        request.user = admin_user
        
        with patch('api.views.ml.training_views.TrainingJob') as mock_job:
            from django.utils import timezone
            from datetime import timedelta
            
            mock_job_instance = Mock()
            mock_job_instance.job_id = 'job_123'
            mock_job_instance.status = 'running'
            mock_job_instance.progress_percentage = 50
            mock_job_instance.started_at = timezone.now() - timedelta(minutes=30)
            mock_job_instance.created_by = admin_user
            mock_job_instance.is_active = True
            mock_job_instance.logs = ''
            # Create proper DoesNotExist exception
            class MockDoesNotExist(Exception):
                pass
            mock_job.DoesNotExist = MockDoesNotExist
            mock_query = Mock()
            mock_query.get.return_value = mock_job_instance
            mock_job.objects.select_related.return_value = mock_query
            
            with patch('api.views.ml.training_views.TrainingJobStatusSerializer') as mock_serializer_class:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {
                    'status': 'running',
                    'job_id': 'job_123',
                    'progress_percentage': 50
                }
                mock_serializer_class.return_value = mock_serializer_instance
                with patch.object(view, 'is_admin_user', return_value=True):
                    response = view.get(request, job_id='job_123')
                    
                    assert response.status_code == status.HTTP_200_OK
                    assert 'estimated_completion' in response.data['status_details']

