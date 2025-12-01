"""
Tests for ML model views.
Covers ModelsStatusView, DatasetValidationView, LoadModelsView, AutoInitializeView,
LatestMetricsView, PromoteModelView, and AutoTrainView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.views.ml.model_views import (
    ModelsStatusView,
    DatasetValidationView,
    LoadModelsView,
    AutoInitializeView,
    LatestMetricsView,
    PromoteModelView,
    AutoTrainView
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
class TestModelsStatusView:
    """Tests for ModelsStatusView."""
    
    def test_status_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/models/status/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.model_views.MLService')
    def test_status_success(self, mock_ml_service, api_client, authenticated_user):
        """Test getting models status successfully."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {
            'status': 'loaded',
            'device': 'cpu',
            'model': 'HybridCacaoRegression',
            'model_details': {},
            'scalers': 'loaded',
            'models_loaded': True
        }
        mock_service.get_model_status.return_value = mock_result
        mock_ml_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelsStatusView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.model_views.ModelsStatusSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.data = {'status': 'loaded'}
            mock_serializer.return_value = mock_serializer_instance
            mock_serializer_instance.is_valid.return_value = True
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_200_OK
    
    @patch('api.views.ml.model_views.MLService')
    def test_status_not_loaded(self, mock_ml_service, api_client, authenticated_user):
        """Test status when models are not loaded."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = MagicMock()
        mock_result.error.message = 'Models not loaded'
        mock_result.error.details = {}
        mock_service.get_model_status.return_value = mock_result
        mock_ml_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelsStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert 'error' in response.data


@pytest.mark.django_db
class TestDatasetValidationView:
    """Tests for DatasetValidationView."""
    
    def test_validation_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/dataset/validate/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.model_views.cache')
    @patch('api.views.ml.model_views.validate_dataset_task')
    def test_validation_cached(self, mock_task, mock_cache, api_client, authenticated_user):
        """Test dataset validation with cached result."""
        cached_result = {
            'valid': True,
            'stats': {'total_images': 100}
        }
        mock_cache.get.return_value = cached_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = DatasetValidationView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == cached_result
        mock_task.delay.assert_not_called()
    
    @patch('api.views.ml.model_views.cache')
    @patch('api.views.ml.model_views.validate_dataset_task')
    def test_validation_not_cached(self, mock_task, mock_cache, api_client, authenticated_user):
        """Test dataset validation when not cached."""
        mock_cache.get.return_value = None
        mock_task_result = MagicMock()
        mock_task_result.id = 'task-123'
        mock_task.delay.return_value = mock_task_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = DatasetValidationView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert 'task_id' in response.data
        assert response.data['task_id'] == 'task-123'
        mock_task.delay.assert_called_once()


@pytest.mark.django_db
class TestLoadModelsView:
    """Tests for LoadModelsView."""
    
    def test_load_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot load models."""
        response = api_client.post('/api/v1/ml/models/load/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.model_views.MLService')
    @patch('api.views.ml.model_views.invalidate_models_status_cache')
    def test_load_success(self, mock_invalidate, mock_ml_service, api_client, authenticated_user):
        """Test loading models successfully."""
        mock_service = MagicMock()
        mock_status_result = MagicMock()
        mock_status_result.success = True
        mock_status_result.data = {'models_loaded': False, 'load_state': 'not_loaded'}
        mock_service.get_model_status.return_value = mock_status_result
        
        mock_load_result = MagicMock()
        mock_load_result.success = True
        mock_service.load_models.return_value = mock_load_result
        mock_ml_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = LoadModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'Modelos cargados exitosamente' in response.data['message']
        mock_invalidate.assert_called_once()
    
    @patch('api.views.ml.model_views.MLService')
    @patch('api.views.ml.model_views.invalidate_models_status_cache')
    def test_load_already_loaded(self, mock_invalidate, mock_ml_service, api_client, authenticated_user):
        """Test loading when models are already loaded."""
        mock_service = MagicMock()
        mock_status_result = MagicMock()
        mock_status_result.success = True
        mock_status_result.data = {'models_loaded': True, 'load_state': 'loaded'}
        mock_service.get_model_status.return_value = mock_status_result
        mock_ml_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = LoadModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['already_loaded'] is True
    
    @patch('api.views.ml.model_views.MLService')
    def test_load_failure(self, mock_ml_service, api_client, authenticated_user):
        """Test loading models failure."""
        mock_service = MagicMock()
        mock_status_result = MagicMock()
        mock_status_result.success = True
        mock_status_result.data = {'models_loaded': False}
        mock_service.get_model_status.return_value = mock_status_result
        
        mock_load_result = MagicMock()
        mock_load_result.success = False
        mock_load_result.error = MagicMock()
        mock_load_result.error.message = 'Load failed'
        mock_load_result.error.details = {}
        mock_service.load_models.return_value = mock_load_result
        mock_ml_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = LoadModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


@pytest.mark.django_db
class TestAutoInitializeView:
    """Tests for AutoInitializeView."""
    
    def test_initialize_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot initialize."""
        response = api_client.post('/api/v1/ml/auto-initialize/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.ml.model_views.AnalysisService')
    def test_initialize_success(self, mock_analysis_service, api_client, authenticated_user):
        """Test auto initialization successfully."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.message = 'Initialization complete'
        mock_result.data = {
            'steps_completed': ['validation', 'training'],
            'training_metrics': {}
        }
        mock_service.initialize_ml_system.return_value = mock_result
        mock_analysis_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = AutoInitializeView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert 'steps_completed' in response.data
    
    @patch('api.views.ml.model_views.AnalysisService')
    def test_initialize_validation_error(self, mock_analysis_service, api_client, authenticated_user):
        """Test auto initialization with validation error."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = MagicMock()
        mock_result.error.error_code = 'validation_error'
        mock_result.error.message = 'Invalid dataset'
        mock_result.error.details = {}
        mock_service.initialize_ml_system.return_value = mock_result
        mock_analysis_service.return_value = mock_service
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = AutoInitializeView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data


@pytest.mark.django_db
class TestLatestMetricsView:
    """Tests for LatestMetricsView."""
    
    def test_latest_metrics_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/latest/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_latest_metrics_model_not_available(self, api_client, authenticated_user):
        """Test latest metrics when ModelMetrics is not available."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = LatestMetricsView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.model_views.ModelMetrics', None):
            response = view.get(request)
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert 'error' in response.data
    
    def test_latest_metrics_success(self, api_client, authenticated_user, db):
        """Test getting latest metrics successfully."""
        from training.models import ModelMetrics
        
        # Create test metrics
        ModelMetrics.objects.create(
            model_name='test_model',
            model_type='regression',
            target='alto',
            metric_type='validation',
            mae=1.5,
            rmse=2.0,
            r2_score=0.85,
            created_by=authenticated_user
        )
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = LatestMetricsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'metrics' in response.data
        assert 'alto' in response.data['metrics']


@pytest.mark.django_db
class TestPromoteModelView:
    """Tests for PromoteModelView."""
    
    def test_promote_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot promote."""
        response = api_client.post('/api/v1/ml/models/promote/v1.0/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_promote_requires_admin(self, api_client, authenticated_user):
        """Test that non-admin users cannot promote."""
        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post('/api/v1/ml/models/promote/v1.0/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_promote_missing_parameters(self, api_client, admin_user):
        """Test promote with missing parameters."""
        api_client.force_authenticate(user=admin_user)
        
        view = PromoteModelView()
        request = Mock()
        request.user = admin_user
        request.data = {}
        
        with patch('api.views.ml.model_views.ModelMetrics', MagicMock()):
            response = view.post(request, version='v1.0')
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'model_name y target son requeridos' in response.data['error']
    
    def test_promote_model_not_found(self, api_client, admin_user):
        """Test promote when model not found."""
        from training.models import ModelMetrics
        
        api_client.force_authenticate(user=admin_user)
        
        view = PromoteModelView()
        request = Mock()
        request.user = admin_user
        request.data = {'model_name': 'nonexistent', 'target': 'alto'}
        
        response = view.post(request, version='v1.0')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrado' in response.data['error']
    
    def test_promote_success(self, api_client, admin_user, db):
        """Test promoting model successfully."""
        from training.models import ModelMetrics
        
        metrics = ModelMetrics.objects.create(
            model_name='test_model',
            model_type='regression',
            target='alto',
            metric_type='validation',
            version='v1.0',
            mae=1.5,
            rmse=2.0,
            r2_score=0.85,
            created_by=admin_user
        )
        
        api_client.force_authenticate(user=admin_user)
        
        view = PromoteModelView()
        request = Mock()
        request.user = admin_user
        request.data = {'model_name': 'test_model', 'target': 'alto'}
        
        with patch.object(metrics, 'mark_as_production') as mock_mark:
            with patch('api.views.ml.model_views.ModelMetricsListSerializer') as mock_serializer:
                mock_serializer_instance = MagicMock()
                mock_serializer_instance.data = {'id': metrics.id}
                mock_serializer.return_value = mock_serializer_instance
                
                response = view.post(request, version='v1.0')
                
                assert response.status_code == status.HTTP_200_OK
                assert 'message' in response.data
                mock_mark.assert_called_once()


@pytest.mark.django_db
class TestAutoTrainView:
    """Tests for AutoTrainView."""
    
    def test_autotrain_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot train."""
        response = api_client.post('/api/v1/ml/train/auto/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_autotrain_requires_admin(self, api_client, authenticated_user):
        """Test that non-admin users cannot train."""
        api_client.force_authenticate(user=authenticated_user)
        response = api_client.post('/api/v1/ml/train/auto/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_autotrain_invalid_config(self, api_client, admin_user):
        """Test autotrain with invalid configuration."""
        api_client.force_authenticate(user=admin_user)
        
        view = AutoTrainView()
        request = Mock()
        request.user = admin_user
        request.data = {'invalid': 'config'}
        
        with patch('api.views.ml.model_views.AutoTrainConfigSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = False
            mock_serializer_instance.errors = {'epochs': 'Invalid'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Configuración inválida' in response.data['error']
    
    @patch('api.views.ml.model_views.run_training_pipeline')
    def test_autotrain_success(self, mock_run_pipeline, api_client, admin_user):
        """Test autotrain successfully."""
        mock_run_pipeline.return_value = True
        
        api_client.force_authenticate(user=admin_user)
        
        view = AutoTrainView()
        request = Mock()
        request.user = admin_user
        request.data = {
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 1e-4
        }
        
        with patch('api.views.ml.model_views.AutoTrainConfigSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            mock_serializer_instance.validated_data = request.data
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['status'] == 'completed'
            mock_run_pipeline.assert_called_once()
    
    @patch('api.views.ml.model_views.run_training_pipeline')
    def test_autotrain_failure(self, mock_run_pipeline, api_client, admin_user):
        """Test autotrain failure."""
        mock_run_pipeline.return_value = False
        
        api_client.force_authenticate(user=admin_user)
        
        view = AutoTrainView()
        request = Mock()
        request.user = admin_user
        request.data = {'epochs': 50}
        
        with patch('api.views.ml.model_views.AutoTrainConfigSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            mock_serializer_instance.validated_data = request.data
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.data['status'] == 'failed'
    
    def test_autotrain_import_error(self, api_client, admin_user):
        """Test autotrain with import error."""
        api_client.force_authenticate(user=admin_user)
        
        view = AutoTrainView()
        request = Mock()
        request.user = admin_user
        request.data = {'epochs': 50}
        
        with patch('api.views.ml.model_views.AutoTrainConfigSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            mock_serializer_instance.validated_data = request.data
            mock_serializer.return_value = mock_serializer_instance
            
            with patch('api.views.ml.model_views.run_training_pipeline', side_effect=ImportError("Module not found")):
                response = view.post(request)
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert 'Pipeline de entrenamiento no encontrado' in response.data['error']

