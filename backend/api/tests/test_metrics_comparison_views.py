"""
Tests for metrics comparison views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from training.models import ModelMetrics


@pytest.mark.django_db
class TestModelComparisonView:
    """Tests for ModelComparisonView."""
    
    @pytest.fixture
    def client(self):
        """Create API client."""
        return APIClient()
    
    @pytest.fixture
    def user(self):
        """Create test user."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'user_{unique_id}',
            email=f'user_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def model_a(self, user):
        """Create test model A."""
        return ModelMetrics.objects.create(
            mae=0.5,
            mse=0.49,
            rmse=0.7,
            r2_score=0.85,
            model_name='model_a',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='validation',
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
    
    @pytest.fixture
    def model_b(self, user):
        """Create test model B."""
        return ModelMetrics.objects.create(
            mae=0.6,
            mse=0.64,
            rmse=0.8,
            r2_score=0.80,
            model_name='model_b',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='validation',
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
    
    def test_compare_models_success(self, client, user, model_a, model_b):
        """Test successful model comparison."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'comparison_metrics' in response.data
        assert 'winner' in response.data
        assert 'improvement_percentage' in response.data
    
    def test_compare_models_missing_params(self, client, user):
        """Test comparison with missing parameters."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.data if hasattr(response, 'data') else response
        assert 'model_a_id y model_b_id son parámetros requeridos' in str(response_data)
    
    def test_compare_models_missing_model_a_id(self, client, user, model_b):
        """Test comparison with missing model_a_id."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_compare_models_missing_model_b_id(self, client, user, model_a):
        """Test comparison with missing model_b_id."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_compare_models_not_found(self, client, user):
        """Test comparison with non-existent models."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': 99999,
            'model_b_id': 99998
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Check response content
        if hasattr(response, 'data'):
            response_data = str(response.data)
        else:
            response_data = str(response.content)
        assert 'no encontrados' in response_data.lower() or 'not found' in response_data.lower()
    
    def test_compare_models_model_a_not_found(self, client, user, model_b):
        """Test comparison when model_a doesn't exist."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': 99999,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_compare_models_model_b_not_found(self, client, user, model_a):
        """Test comparison when model_b doesn't exist."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': 99999
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_compare_models_calculates_metrics(self, client, user, model_a, model_b):
        """Test that comparison calculates metrics correctly."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        comparison_metrics = response.data['comparison_metrics']
        
        assert 'mae' in comparison_metrics
        assert 'rmse' in comparison_metrics
        assert 'r2_score' in comparison_metrics
        
        assert 'model_a' in comparison_metrics['mae']
        assert 'model_b' in comparison_metrics['mae']
        assert 'difference' in comparison_metrics['mae']
        assert 'better' in comparison_metrics['mae']
    
    def test_compare_models_determines_winner(self, client, user, model_a, model_b):
        """Test that comparison determines winner correctly."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'winner' in response.data
        assert response.data['winner'] in ['model_a', 'model_b']
    
    def test_compare_models_calculates_improvement(self, client, user, model_a, model_b):
        """Test that comparison calculates improvement percentage."""
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'improvement_percentage' in response.data
        assert isinstance(response.data['improvement_percentage'], (int, float))
    
    @patch('api.views.ml.metrics_comparison_views.ModelMetrics')
    def test_compare_models_error(self, mock_model_metrics, client, user):
        """Test comparison with error."""
        from training.models import ModelMetrics as RealModelMetrics
        with patch('api.views.ml.metrics_comparison_views.ModelMetrics') as mock:
            mock.objects.get.side_effect = Exception("Database error")
            
            client.force_authenticate(user=user)
            response = client.get('/api/v1/ml/model-comparison/', {
                'model_a_id': 1,
                'model_b_id': 2
            })
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_compare_models_model_a_better(self, client, user):
        """Test comparison when model_a is better."""
        model_a = ModelMetrics.objects.create(
            mae=0.3,
            mse=0.25,
            rmse=0.5,
            r2_score=0.90,
            model_name='model_a',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='validation',
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
        model_b = ModelMetrics.objects.create(
            mae=0.6,
            mse=0.64,
            rmse=0.8,
            r2_score=0.75,
            model_name='model_b',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='validation',
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
        
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['winner'] == 'model_a'
    
    def test_compare_models_model_b_better(self, client, user):
        """Test comparison when model_b is better."""
        model_a = ModelMetrics.objects.create(
            mae=0.6,
            mse=0.64,
            rmse=0.8,
            r2_score=0.75,
            model_name='model_a',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='validation',
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
        model_b = ModelMetrics.objects.create(
            mae=0.3,
            mse=0.25,
            rmse=0.5,
            r2_score=0.90,
            model_name='model_b',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='validation',
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )
        
        client.force_authenticate(user=user)
        response = client.get('/api/v1/ml/model-comparison/', {
            'model_a_id': model_a.id,
            'model_b_id': model_b.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['winner'] == 'model_b'

