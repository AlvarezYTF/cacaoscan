"""
Tests for ML metrics CRUD views.
Covers ModelMetricsListView, ModelMetricsDetailView, ModelMetricsCreateView, 
ModelMetricsUpdateView, and ModelMetricsDeleteView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.views.ml.metrics_crud_views import (
    ModelMetricsListView,
    ModelMetricsDetailView,
    ModelMetricsCreateView,
    ModelMetricsUpdateView,
    ModelMetricsDeleteView
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
def model_metrics(db, authenticated_user):
    """Create sample model metrics for tests."""
    from training.models import ModelMetrics
    
    return ModelMetrics.objects.create(
        model_name='test_model',
        model_type='regression',
        target='alto',
        metric_type='validation',
        mae=1.5,
        rmse=2.0,
        r2_score=0.85,
        created_by=authenticated_user
    )


@pytest.mark.django_db
class TestModelMetricsListView:
    """Tests for ModelMetricsListView."""
    
    def test_list_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_success(self, api_client, authenticated_user, model_metrics):
        """Test listing metrics successfully."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsListView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {}
        
        with patch.object(view, 'paginate_queryset') as mock_paginate:
            mock_paginate.return_value = Mock(
                status_code=status.HTTP_200_OK,
                data={
                    'results': [{'id': model_metrics.id}],
                    'count': 1
                }
            )
            response = view.get(request)
            assert response.status_code == status.HTTP_200_OK
    
    def test_list_with_filters(self, api_client, authenticated_user, model_metrics):
        """Test listing metrics with filters."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsListView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'metric_type': 'validation',
            'is_best': 'false',
            'is_production': 'false'
        }
        
        with patch.object(view, 'paginate_queryset') as mock_paginate:
            mock_paginate.return_value = Mock(
                status_code=status.HTTP_200_OK,
                data={'results': [], 'count': 0}
            )
            response = view.get(request)
            assert response.status_code == status.HTTP_200_OK
    
    def test_list_exception(self, api_client, authenticated_user):
        """Test exception handling in list."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsListView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {}
        
        with patch('api.views.ml.metrics_crud_views.ModelMetrics') as mock_metrics:
            mock_metrics.objects.all.side_effect = Exception("Database error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestModelMetricsDetailView:
    """Tests for ModelMetricsDetailView."""
    
    def test_detail_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/1/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_detail_not_found(self, api_client, authenticated_user):
        """Test getting non-existent metrics."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsDetailView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, metrics_id=999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Métricas de modelo no encontradas' in response.data['message']
    
    def test_detail_success(self, api_client, authenticated_user, model_metrics):
        """Test getting metrics detail successfully."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsDetailView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.data = {
                'id': model_metrics.id,
                'model_name': 'test_model',
                'r2_score': 0.85
            }
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.get(request, metrics_id=model_metrics.id)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['success'] is True
            assert 'data' in response.data
    
    def test_detail_exception(self, api_client, authenticated_user):
        """Test exception handling in detail."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsDetailView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_crud_views.ModelMetrics') as mock_metrics:
            mock_metrics.objects.get.side_effect = Exception("Database error")
            
            response = view.get(request, metrics_id=1)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestModelMetricsCreateView:
    """Tests for ModelMetricsCreateView."""
    
    def test_create_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot create."""
        response = api_client.post('/api/v1/ml/metrics/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_invalid_data(self, api_client, authenticated_user):
        """Test creating metrics with invalid data."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsCreateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {}
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsCreateSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = False
            mock_serializer_instance.errors = {'model_name': 'This field is required.'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Datos de métricas inválidos' in response.data['message']
    
    def test_create_success(self, api_client, authenticated_user):
        """Test creating metrics successfully."""
        from training.models import ModelMetrics
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsCreateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {
            'model_name': 'new_model',
            'model_type': 'regression',
            'target': 'alto',
            'metric_type': 'validation',
            'mae': 1.5,
            'rmse': 2.0,
            'r2_score': 0.85
        }
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsCreateSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            new_metrics = ModelMetrics.objects.create(
                model_name='new_model',
                model_type='regression',
                target='alto',
                metric_type='validation',
                mae=1.5,
                rmse=2.0,
                r2_score=0.85,
                created_by=authenticated_user
            )
            mock_serializer_instance.save.return_value = new_metrics
            mock_serializer.return_value = mock_serializer_instance
            
            with patch('api.views.ml.metrics_crud_views.ModelMetricsSerializer') as mock_response_serializer:
                mock_response_serializer_instance = MagicMock()
                mock_response_serializer_instance.data = {'id': new_metrics.id}
                mock_response_serializer.return_value = mock_response_serializer_instance
                
                with patch('api.views.ml.metrics_crud_views.invalidate_latest_metrics_cache'):
                    response = view.post(request)
                    
                    assert response.status_code == status.HTTP_201_CREATED
                    assert response.data['success'] is True
    
    def test_create_mark_as_best(self, api_client, authenticated_user):
        """Test creating metrics and marking as best."""
        from training.models import ModelMetrics
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsCreateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {
            'model_name': 'best_model',
            'model_type': 'regression',
            'target': 'alto',
            'metric_type': 'validation',
            'mae': 1.0,
            'rmse': 1.5,
            'r2_score': 0.95,
            'is_best_model': True
        }
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsCreateSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            new_metrics = ModelMetrics.objects.create(
                model_name='best_model',
                model_type='regression',
                target='alto',
                metric_type='validation',
                mae=1.0,
                rmse=1.5,
                r2_score=0.95,
                is_best_model=True,
                created_by=authenticated_user
            )
            mock_serializer_instance.save.return_value = new_metrics
            mock_serializer.return_value = mock_serializer_instance
            
            with patch.object(new_metrics, 'mark_as_best') as mock_mark_best:
                with patch('api.views.ml.metrics_crud_views.ModelMetricsSerializer'):
                    with patch('api.views.ml.metrics_crud_views.invalidate_latest_metrics_cache'):
                        response = view.post(request)
                        
                        assert response.status_code == status.HTTP_201_CREATED
                        mock_mark_best.assert_called_once()
    
    def test_create_exception(self, api_client, authenticated_user):
        """Test exception handling in create."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsCreateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {}
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsCreateSerializer') as mock_serializer:
            mock_serializer.side_effect = Exception("Database error")
            
            response = view.post(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestModelMetricsUpdateView:
    """Tests for ModelMetricsUpdateView."""
    
    def test_update_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot update."""
        response = api_client.put('/api/v1/ml/metrics/1/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_not_found(self, api_client, authenticated_user):
        """Test updating non-existent metrics."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsUpdateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {'r2_score': 0.90}
        
        response = view.put(request, metrics_id=999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_invalid_data(self, api_client, authenticated_user, model_metrics):
        """Test updating metrics with invalid data."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsUpdateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {'r2_score': 'invalid'}
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsUpdateSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = False
            mock_serializer_instance.errors = {'r2_score': 'Invalid value'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.put(request, metrics_id=model_metrics.id)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_success(self, api_client, authenticated_user, model_metrics):
        """Test updating metrics successfully."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsUpdateView()
        request = Mock()
        request.user = authenticated_user
        request.data = {'r2_score': 0.90}
        
        with patch('api.views.ml.metrics_crud_views.ModelMetricsUpdateSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            model_metrics.r2_score = 0.90
            mock_serializer_instance.save.return_value = model_metrics
            mock_serializer.return_value = mock_serializer_instance
            
            with patch('api.views.ml.metrics_crud_views.ModelMetricsSerializer') as mock_response_serializer:
                mock_response_serializer_instance = MagicMock()
                mock_response_serializer_instance.data = {'r2_score': 0.90}
                mock_response_serializer.return_value = mock_response_serializer_instance
                
                with patch('api.views.ml.metrics_crud_views.invalidate_latest_metrics_cache'):
                    response = view.put(request, metrics_id=model_metrics.id)
                    
                    assert response.status_code == status.HTTP_200_OK
                    assert response.data['success'] is True


@pytest.mark.django_db
class TestModelMetricsDeleteView:
    """Tests for ModelMetricsDeleteView."""
    
    def test_delete_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot delete."""
        response = api_client.delete('/api/v1/ml/metrics/1/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_not_found(self, api_client, authenticated_user):
        """Test deleting non-existent metrics."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsDeleteView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.delete(request, metrics_id=999)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_success(self, api_client, authenticated_user, model_metrics):
        """Test deleting metrics successfully."""
        metrics_id = model_metrics.id
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsDeleteView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_crud_views.invalidate_latest_metrics_cache'):
            response = view.delete(request, metrics_id=metrics_id)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['success'] is True
            
            # Verify metrics was deleted
            from training.models import ModelMetrics
            assert not ModelMetrics.objects.filter(id=metrics_id).exists()
    
    def test_delete_exception(self, api_client, authenticated_user):
        """Test exception handling in delete."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsDeleteView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_crud_views.ModelMetrics') as mock_metrics:
            mock_metrics.objects.get.side_effect = Exception("Database error")
            
            response = view.delete(request, metrics_id=1)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data

