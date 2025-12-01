"""
Tests for ML incremental training views.
Covers IncrementalTrainingStatusView, IncrementalTrainingView, IncrementalDataUploadView,
IncrementalModelVersionsView, and IncrementalDataVersionsView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from api.views.ml.incremental_views import (
    IncrementalTrainingStatusView,
    IncrementalTrainingView,
    IncrementalDataUploadView,
    IncrementalModelVersionsView,
    IncrementalDataVersionsView
)


@pytest.fixture
def authenticated_user(db):
    """Create authenticated user for tests."""
    return User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123'
    )


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def csv_file():
    """Create a sample CSV file for testing."""
    csv_content = "ID,ALTO,ANCHO,GROSOR,PESO\n1,22.5,10.2,16.3,1.72\n2,23.0,10.5,16.5,1.80"
    return SimpleUploadedFile(
        "test_data.csv",
        csv_content.encode('utf-8'),
        content_type="text/csv"
    )


@pytest.mark.django_db
class TestIncrementalTrainingStatusView:
    """Tests for IncrementalTrainingStatusView."""
    
    def test_status_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/incremental/status/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.incremental_views.get_incremental_training_status')
    def test_status_success(self, mock_get_status, api_client, authenticated_user):
        """Test getting incremental training status successfully."""
        mock_get_status.return_value = {
            'system_ready': True,
            'models_loaded': True,
            'data_versions': 3,
            'model_versions': 2
        }
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
    
    @patch('api.views.ml.incremental_views.get_incremental_training_status')
    def test_status_exception(self, mock_get_status, api_client, authenticated_user):
        """Test exception handling in status."""
        mock_get_status.side_effect = Exception("ML service error")
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


@pytest.mark.django_db
class TestIncrementalTrainingView:
    """Tests for IncrementalTrainingView."""
    
    def test_training_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot train."""
        response = api_client.post('/api/v1/ml/incremental/train/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_training_missing_new_data(self, api_client, authenticated_user):
        """Test training without new_data."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingView()
        request = Mock()
        request.user = authenticated_user
        request.data = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_data es requerido' in response.data['message']
    
    def test_training_invalid_target(self, api_client, authenticated_user):
        """Test training with invalid target."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingView()
        request = Mock()
        request.user = authenticated_user
        request.data = {
            'new_data': [{'id': 1, 'image_path': 'test.jpg', 'alto': 22.5}],
            'target': 'invalid_target'
        }
        
        with patch('api.views.ml.incremental_views.validate_target') as mock_validate:
            from rest_framework.response import Response
            mock_validate.return_value = Response(
                {'error': 'Invalid target'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_training_invalid_data_structure(self, api_client, authenticated_user):
        """Test training with invalid data structure."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingView()
        request = Mock()
        request.user = authenticated_user
        request.data = {
            'new_data': [{'invalid': 'structure'}],
            'target': 'alto'
        }
        
        with patch('api.views.ml.incremental_views.validate_target') as mock_validate:
            mock_validate.return_value = None
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'faltan campos' in response.data['message']
    
    @patch('api.views.ml.incremental_views.run_incremental_training_pipeline')
    @patch('api.views.ml.incremental_views.TrainingJob')
    def test_training_success(self, mock_training_job, mock_run_pipeline, api_client, authenticated_user):
        """Test incremental training successfully."""
        mock_run_pipeline.return_value = True
        
        mock_job = MagicMock()
        mock_job.id = 1
        mock_training_job.objects.create.return_value = mock_job
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingView()
        request = Mock()
        request.user = authenticated_user
        request.data = {
            'new_data': [
                {
                    'id': 1,
                    'image_path': 'test.jpg',
                    'alto': 22.5,
                    'ancho': 10.2,
                    'grosor': 16.3,
                    'peso': 1.72
                }
            ],
            'target': 'alto',
            'epochs': 20,
            'batch_size': 16
        }
        
        with patch('api.views.ml.incremental_views.validate_target') as mock_validate:
            mock_validate.return_value = None
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['success'] is True
            assert 'job_id' in response.data['data']
            mock_run_pipeline.assert_called_once()
    
    @patch('api.views.ml.incremental_views.run_incremental_training_pipeline')
    @patch('api.views.ml.incremental_views.TrainingJob')
    def test_training_failure(self, mock_training_job, mock_run_pipeline, api_client, authenticated_user):
        """Test incremental training failure."""
        mock_run_pipeline.return_value = False
        
        mock_job = MagicMock()
        mock_training_job.objects.create.return_value = mock_job
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalTrainingView()
        request = Mock()
        request.user = authenticated_user
        request.data = {
            'new_data': [{'id': 1, 'image_path': 'test.jpg', 'alto': 22.5}],
            'target': 'alto'
        }
        
        with patch('api.views.ml.incremental_views.validate_target') as mock_validate:
            mock_validate.return_value = None
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Error en entrenamiento incremental' in response.data['message']


@pytest.mark.django_db
class TestIncrementalDataUploadView:
    """Tests for IncrementalDataUploadView."""
    
    def test_upload_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot upload."""
        response = api_client.post('/api/v1/ml/incremental/upload/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_upload_missing_csv(self, api_client, authenticated_user):
        """Test upload without CSV file."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalDataUploadView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {}
        request.POST = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'csv_file es requerido' in response.data['message']
    
    def test_upload_invalid_csv_columns(self, api_client, authenticated_user):
        """Test upload with CSV missing required columns."""
        invalid_csv = SimpleUploadedFile(
            "invalid.csv",
            b"ID,ALTO\n1,22.5",
            content_type="text/csv"
        )
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalDataUploadView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'csv_file': invalid_csv}
        request.POST = {'target': 'alto'}
        
        with patch('api.views.ml.incremental_views.validate_target') as mock_validate:
            mock_validate.return_value = None
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Columnas faltantes' in response.data['message']
    
    @patch('api.views.ml.incremental_views.IncrementalDataManager')
    @patch('api.views.ml.incremental_views.validate_target')
    def test_upload_success(self, mock_validate, mock_data_manager, api_client, authenticated_user, csv_file):
        """Test data upload successfully."""
        mock_validate.return_value = None
        
        mock_manager = MagicMock()
        mock_manager.add_new_data.return_value = 'v1.0'
        mock_data_manager.return_value = mock_manager
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalDataUploadView()
        request = Mock()
        request.user = authenticated_user
        request.FILES = {'csv_file': csv_file}
        request.POST = {'target': 'alto'}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'version' in response.data['data']
        assert 'samples_count' in response.data['data']


@pytest.mark.django_db
class TestIncrementalModelVersionsView:
    """Tests for IncrementalModelVersionsView."""
    
    def test_versions_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/incremental/models/versions/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.incremental_views.IncrementalModelManager')
    def test_versions_success(self, mock_model_manager, api_client, authenticated_user):
        """Test getting model versions successfully."""
        mock_manager = MagicMock()
        mock_manager.list_model_versions.return_value = [
            {'version': 'v1.0', 'performance_metrics': {'alto': 0.85}},
            {'version': 'v1.1', 'performance_metrics': {'alto': 0.87}}
        ]
        mock_manager.model_metadata = {'versions': ['v1.0', 'v1.1']}
        mock_manager.current_version = 'v1.1'
        mock_manager.model_metadata.get.return_value = {}
        mock_model_manager.return_value = mock_manager
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalModelVersionsView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'versions' in response.data['data']
    
    @patch('api.views.ml.incremental_views.IncrementalModelManager')
    def test_versions_with_target_filter(self, mock_model_manager, api_client, authenticated_user):
        """Test getting model versions with target filter."""
        mock_manager = MagicMock()
        mock_manager.list_model_versions.return_value = [
            {'version': 'v1.0', 'performance_metrics': {'alto': 0.85}}
        ]
        mock_manager.model_metadata = {'versions': ['v1.0']}
        mock_manager.current_version = 'v1.0'
        mock_manager.model_metadata.get.return_value = {}
        mock_model_manager.return_value = mock_manager
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalModelVersionsView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {'target': 'alto', 'limit': '5'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True


@pytest.mark.django_db
class TestIncrementalDataVersionsView:
    """Tests for IncrementalDataVersionsView."""
    
    def test_data_versions_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/incremental/data/versions/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.incremental_views.IncrementalDataManager')
    def test_data_versions_success(self, mock_data_manager, api_client, authenticated_user):
        """Test getting data versions successfully."""
        mock_manager = MagicMock()
        mock_manager.list_versions.return_value = [
            {'version': 'v1.0', 'samples': 100},
            {'version': 'v1.1', 'samples': 150}
        ]
        mock_manager.dataset_metadata = {'versions': ['v1.0', 'v1.1']}
        mock_manager.current_version = 'v1.1'
        mock_manager.dataset_metadata.get.return_value = 150
        mock_data_manager.return_value = mock_manager
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalDataVersionsView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'versions' in response.data['data']
        assert 'total_samples' in response.data['data']
    
    @patch('api.views.ml.incremental_views.IncrementalDataManager')
    def test_data_versions_with_limit(self, mock_data_manager, api_client, authenticated_user):
        """Test getting data versions with limit."""
        mock_manager = MagicMock()
        mock_manager.list_versions.return_value = [
            {'version': 'v1.0'},
            {'version': 'v1.1'},
            {'version': 'v1.2'}
        ]
        mock_manager.dataset_metadata = {'versions': ['v1.0', 'v1.1', 'v1.2']}
        mock_manager.current_version = 'v1.2'
        mock_manager.dataset_metadata.get.return_value = 200
        mock_data_manager.return_value = mock_manager
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = IncrementalDataVersionsView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {'limit': '2'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

