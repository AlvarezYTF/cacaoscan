"""
Tests for ML metrics comparison views.
Covers ModelComparisonView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.views.ml.metrics_comparison_views import ModelComparisonView


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
def model_metrics_a(db, authenticated_user):
    """Create first model metrics for comparison."""
    from training.models import ModelMetrics
    
    return ModelMetrics.objects.create(
        model_name='model_a',
        model_type='regression',
        target='alto',
        metric_type='validation',
        mae=1.5,
        rmse=2.0,
        r2_score=0.85,
        created_by=authenticated_user
    )


@pytest.fixture
def model_metrics_b(db, authenticated_user):
    """Create second model metrics for comparison."""
    from training.models import ModelMetrics
    
    return ModelMetrics.objects.create(
        model_name='model_b',
        model_type='regression',
        target='alto',
        metric_type='validation',
        mae=2.0,
        rmse=2.5,
        r2_score=0.80,
        created_by=authenticated_user
    )


@pytest.mark.django_db
class TestModelComparisonView:
    """Tests for ModelComparisonView."""
    
    def test_comparison_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/ml/metrics/compare/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_comparison_missing_parameters(self, api_client, authenticated_user):
        """Test comparison with missing required parameters."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'model_a_id y model_b_id son parámetros requeridos' in response.data['message']
    
    def test_comparison_missing_model_a_id(self, api_client, authenticated_user):
        """Test comparison with missing model_a_id."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {'model_b_id': '1'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_comparison_missing_model_b_id(self, api_client, authenticated_user):
        """Test comparison with missing model_b_id."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {'model_a_id': '1'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_comparison_model_not_found(self, api_client, authenticated_user):
        """Test comparison when one or both models not found."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {'model_a_id': '999', 'model_b_id': '998'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Uno o ambos modelos no encontrados' in response.data['message']
    
    def test_comparison_success(self, api_client, authenticated_user, model_metrics_a, model_metrics_b):
        """Test comparing two models successfully."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {
            'model_a_id': str(model_metrics_a.id),
            'model_b_id': str(model_metrics_b.id)
        }
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        assert 'model_a' in response.data['data']
        assert 'model_b' in response.data['data']
        assert 'comparison_metrics' in response.data['data']
        assert 'winner' in response.data['data']
        assert 'improvement_percentage' in response.data['data']
        
        # Verify comparison metrics structure
        comparison = response.data['data']['comparison_metrics']
        assert 'mae' in comparison
        assert 'rmse' in comparison
        assert 'r2_score' in comparison
        
        # Verify winner determination (model_a should win with better r2_score)
        assert response.data['data']['winner'] == 'model_a'
    
    def test_comparison_model_b_wins(self, api_client, authenticated_user, model_metrics_a, model_metrics_b):
        """Test comparison where model_b wins."""
        # Update model_b to have better metrics
        model_metrics_b.mae = 1.0
        model_metrics_b.rmse = 1.5
        model_metrics_b.r2_score = 0.90
        model_metrics_b.save()
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {
            'model_a_id': str(model_metrics_a.id),
            'model_b_id': str(model_metrics_b.id)
        }
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['winner'] == 'model_b'
    
    def test_comparison_exception(self, api_client, authenticated_user):
        """Test exception handling in comparison."""
        api_client.force_authenticate(user=authenticated_user)
        
        view = ModelComparisonView()
        request = Mock()
        request.user = authenticated_user
        request.GET = {'model_a_id': '1', 'model_b_id': '2'}
        
        with patch('api.views.ml.metrics_comparison_views.ModelMetrics') as mock_metrics:
            mock_metrics.objects.get.side_effect = Exception("Database error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data

