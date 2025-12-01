"""
Tests for ML metrics analysis views.
Covers ModelMetricsStatsView, ModelPerformanceTrendView, BestModelsView, and ProductionModelsView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from api.views.ml.metrics_analysis_views import (
    ModelMetricsStatsView,
    ModelPerformanceTrendView,
    BestModelsView,
    ProductionModelsView
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
def model_metrics_data(db, authenticated_user):
    """Create sample model metrics for tests."""
    from training.models import ModelMetrics
    
    metrics = ModelMetrics.objects.create(
        model_name='test_model',
        model_type='regression',
        target='alto',
        metric_type='validation',
        mae=1.5,
        rmse=2.0,
        r2_score=0.85,
        is_best_model=False,
        is_production_model=False,
        created_by=authenticated_user
    )
    return metrics


@pytest.mark.django_db
class TestModelMetricsStatsView:
    """Tests for ModelMetricsStatsView."""
    
    def test_stats_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/stats/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_stats_success(self, api_client, authenticated_user, model_metrics_data):
        """Test getting metrics stats successfully."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsStatsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        assert 'total_models' in response.data['data']
        assert 'models_by_type' in response.data['data']
        assert 'models_by_target' in response.data['data']
        assert 'average_r2_score' in response.data['data']
    
    def test_stats_empty_database(self, api_client, authenticated_user):
        """Test stats with empty database."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsStatsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['total_models'] == 0
    
    def test_stats_exception(self, api_client, authenticated_user):
        """Test exception handling in stats."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelMetricsStatsView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_analysis_views.ModelMetrics') as mock_metrics:
            mock_metrics.objects.count.side_effect = Exception("Database error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestModelPerformanceTrendView:
    """Tests for ModelPerformanceTrendView."""
    
    def test_trend_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/trend/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_trend_missing_parameters(self, api_client, authenticated_user):
        """Test trend with missing required parameters."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelPerformanceTrendView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'model_name y target son parámetros requeridos' in response.data['message']
    
    def test_trend_success(self, api_client, authenticated_user, model_metrics_data):
        """Test getting performance trend successfully."""
        from training.models import ModelMetrics
        
        # Mock the get_performance_trend method
        with patch.object(ModelMetrics, 'get_performance_trend') as mock_trend:
            mock_trend.return_value = [
                {
                    'created_at': '2024-01-01T00:00:00',
                    'r2_score': 0.80,
                    'mae': 1.8,
                    'rmse': 2.2
                },
                {
                    'created_at': '2024-01-02T00:00:00',
                    'r2_score': 0.85,
                    'mae': 1.5,
                    'rmse': 2.0
                }
            ]
            
            api_client.force_authenticate(user=authenticated_user)
            
            view = ModelPerformanceTrendView()
            request = Mock()
            request.user = authenticated_user
            request.GET = {
                'model_name': 'test_model',
                'target': 'alto',
                'metric_type': 'validation'
            }
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['success'] is True
            assert 'trend_data' in response.data['data']
            assert 'improvement_trend' in response.data['data']
    
    def test_trend_not_found(self, api_client, authenticated_user):
        """Test trend when no data found."""
        from training.models import ModelMetrics
        
        with patch.object(ModelMetrics, 'get_performance_trend') as mock_trend:
            mock_trend.return_value = None
            
            api_client.force_authenticate(user=authenticated_user)
            
            view = ModelPerformanceTrendView()
            request = Mock()
            request.user = authenticated_user
            request.GET = {
                'model_name': 'nonexistent',
                'target': 'alto'
            }
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert 'No se encontraron datos' in response.data['message']
    
    def test_trend_exception(self, api_client, authenticated_user):
        """Test exception handling in trend."""
        from training.models import ModelMetrics
        
        with patch.object(ModelMetrics, 'get_performance_trend') as mock_trend:
            mock_trend.side_effect = Exception("Database error")
            
            api_client.force_authenticate(user=authenticated_user)
            
            view = ModelPerformanceTrendView()
            request = Mock()
            request.user = authenticated_user
            request.GET = {
                'model_name': 'test_model',
                'target': 'alto'
            }
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestBestModelsView:
    """Tests for BestModelsView."""
    
    def test_best_models_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/best/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_best_models_success(self, api_client, authenticated_user, model_metrics_data):
        """Test getting best models successfully."""
        from training.models import ModelMetrics
        
        # Mark as best model
        model_metrics_data.is_best_model = True
        model_metrics_data.save()
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = BestModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        assert 'best_models' in response.data['data']
        assert 'count' in response.data['data']
    
    def test_best_models_empty(self, api_client, authenticated_user):
        """Test best models with no best models."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = BestModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['count'] == 0
    
    def test_best_models_exception(self, api_client, authenticated_user):
        """Test exception handling in best models."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = BestModelsView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_analysis_views.ModelMetrics') as mock_metrics:
            mock_metrics.get_best_models.side_effect = Exception("Database error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestProductionModelsView:
    """Tests for ProductionModelsView."""
    
    def test_production_models_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/production/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_production_models_success(self, api_client, authenticated_user, model_metrics_data):
        """Test getting production models successfully."""
        from training.models import ModelMetrics
        
        # Mark as production model
        model_metrics_data.is_production_model = True
        model_metrics_data.save()
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ProductionModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        assert 'production_models' in response.data['data']
        assert 'count' in response.data['data']
    
    def test_production_models_empty(self, api_client, authenticated_user):
        """Test production models with no production models."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ProductionModelsView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['count'] == 0
    
    def test_production_models_exception(self, api_client, authenticated_user):
        """Test exception handling in production models."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ProductionModelsView()
        request = Mock()
        request.user = authenticated_user
        
        with patch('api.views.ml.metrics_analysis_views.ModelMetrics') as mock_metrics:
            mock_metrics.get_production_models.side_effect = Exception("Database error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data

