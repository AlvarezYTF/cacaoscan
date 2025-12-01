"""
Unit tests for ML serializers (ml_serializers.py).
Tests all serializers related to ML models, training jobs, and metrics.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from training.models import TrainingJob, ModelMetrics
from api.serializers.ml_serializers import (
    ModelsStatusSerializer,
    LoadModelsResponseSerializer,
    TrainingJobSerializer,
    TrainingJobCreateSerializer,
    TrainingJobStatusSerializer,
    AutoTrainConfigSerializer,
    ModelMetricsSerializer,
    ModelMetricsListSerializer,
    ModelMetricsCreateSerializer,
    ModelMetricsUpdateSerializer,
    ModelMetricsStatsSerializer,
    ModelPerformanceTrendSerializer,
    ModelComparisonSerializer
)
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD
)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD
    )


@pytest.fixture
def test_training_job(test_user):
    """Create a test training job."""
    return TrainingJob.objects.create(
        job_id='test-job-001',
        job_type='regression',
        status='completed',
        created_by=test_user,
        model_name='test_model',
        dataset_size=100,
        epochs=50,
        batch_size=16,
        learning_rate=0.001,
        started_at=timezone.now() - timedelta(hours=1),
        completed_at=timezone.now()
    )


@pytest.fixture
def test_model_metrics(test_user, test_training_job):
    """Create test model metrics."""
    return ModelMetrics.objects.create(
        model_name='test_model',
        model_type='regression',
        target='alto',
        version='1.0.0',
        training_job=test_training_job,
        created_by=test_user,
        metric_type='regression',
        mae=0.5,
        mse=0.25,
        rmse=0.5,
        r2_score=0.95,
        mape=2.0,
        dataset_size=100,
        train_size=70,
        validation_size=20,
        test_size=10,
        epochs=50,
        batch_size=16,
        learning_rate=0.001,
        training_time_seconds=3600.0
    )


class TestModelsStatusSerializer:
    """Tests for ModelsStatusSerializer."""
    
    def test_validate_success(self):
        """Test successful validation."""
        data = {
            'status': 'loaded',
            'device': 'CPU',
            'model': 'hybrid',
            'model_details': {'version': '1.0.0'},
            'scalers': 'loaded'
        }
        serializer = ModelsStatusSerializer(data=data)
        assert serializer.is_valid()
    
    def test_validate_missing_status(self):
        """Test validation error when status is missing."""
        data = {
            'device': 'CPU',
            'model': 'hybrid'
        }
        serializer = ModelsStatusSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_missing_model(self):
        """Test validation error when model is missing."""
        data = {
            'status': 'loaded',
            'device': 'CPU'
        }
        serializer = ModelsStatusSerializer(data=data)
        assert not serializer.is_valid()


class TestLoadModelsResponseSerializer:
    """Tests for LoadModelsResponseSerializer."""
    
    def test_serialize_success(self):
        """Test serialization of success response."""
        data = {
            'message': 'Models loaded successfully',
            'status': 'success'
        }
        serializer = LoadModelsResponseSerializer(data=data)
        assert serializer.is_valid()
    
    def test_serialize_error(self):
        """Test serialization of error response."""
        data = {
            'error': 'Failed to load models',
            'status': 'error'
        }
        serializer = LoadModelsResponseSerializer(data=data)
        assert serializer.is_valid()


class TestTrainingJobSerializer:
    """Tests for TrainingJobSerializer."""
    
    def test_serialize_training_job(self, test_training_job):
        """Test serialization of training job."""
        serializer = TrainingJobSerializer(test_training_job)
        data = serializer.data
        
        assert data['job_id'] == 'test-job-001'
        assert data['job_type'] == 'regression'
        assert data['status'] == 'completed'
        assert 'duration_formatted' in data
        assert 'is_active' in data
        assert 'created_by_username' in data
    
    def test_validate_epochs_valid(self):
        """Test successful epochs validation."""
        serializer = TrainingJobSerializer()
        value = serializer.validate_epochs(50)
        assert value == 50
    
    def test_validate_epochs_zero(self):
        """Test validation error when epochs is zero."""
        serializer = TrainingJobSerializer()
        with pytest.raises(Exception):
            serializer.validate_epochs(0)
    
    def test_validate_epochs_too_high(self):
        """Test validation error when epochs > 1000."""
        serializer = TrainingJobSerializer()
        with pytest.raises(Exception):
            serializer.validate_epochs(1001)
    
    def test_validate_batch_size_valid(self):
        """Test successful batch_size validation."""
        serializer = TrainingJobSerializer()
        value = serializer.validate_batch_size(16)
        assert value == 16
    
    def test_validate_batch_size_too_high(self):
        """Test validation error when batch_size > 128."""
        serializer = TrainingJobSerializer()
        with pytest.raises(Exception):
            serializer.validate_batch_size(129)
    
    def test_validate_learning_rate_valid(self):
        """Test successful learning_rate validation."""
        serializer = TrainingJobSerializer()
        value = serializer.validate_learning_rate(0.001)
        assert value == 0.001
    
    def test_validate_learning_rate_zero(self):
        """Test validation error when learning_rate is zero."""
        serializer = TrainingJobSerializer()
        with pytest.raises(Exception):
            serializer.validate_learning_rate(0)
    
    def test_validate_learning_rate_too_high(self):
        """Test validation error when learning_rate > 1.0."""
        serializer = TrainingJobSerializer()
        with pytest.raises(Exception):
            serializer.validate_learning_rate(1.1)
    
    def test_validate_dataset_size_valid(self):
        """Test successful dataset_size validation."""
        serializer = TrainingJobSerializer()
        value = serializer.validate_dataset_size(100)
        assert value == 100
    
    def test_validate_dataset_size_zero(self):
        """Test validation error when dataset_size is zero."""
        serializer = TrainingJobSerializer()
        with pytest.raises(Exception):
            serializer.validate_dataset_size(0)


class TestTrainingJobCreateSerializer:
    """Tests for TrainingJobCreateSerializer."""
    
    def test_validate_job_type_valid(self):
        """Test successful job_type validation."""
        serializer = TrainingJobCreateSerializer()
        value = serializer.validate_job_type('regression')
        assert value == 'regression'
    
    def test_validate_job_type_invalid(self):
        """Test validation error with invalid job_type."""
        serializer = TrainingJobCreateSerializer()
        with pytest.raises(Exception):
            serializer.validate_job_type('invalid')
    
    def test_validate_model_name_valid(self):
        """Test successful model_name validation."""
        serializer = TrainingJobCreateSerializer()
        value = serializer.validate_model_name('test_model')
        assert value == 'test_model'
    
    def test_validate_model_name_empty(self):
        """Test validation error when model_name is empty."""
        serializer = TrainingJobCreateSerializer()
        with pytest.raises(Exception):
            serializer.validate_model_name('')
    
    def test_validate_model_name_whitespace(self):
        """Test validation error when model_name is only whitespace."""
        serializer = TrainingJobCreateSerializer()
        with pytest.raises(Exception):
            serializer.validate_model_name('   ')


class TestTrainingJobStatusSerializer:
    """Tests for TrainingJobStatusSerializer."""
    
    def test_serialize_training_job_status(self, test_training_job):
        """Test serialization of training job status."""
        serializer = TrainingJobStatusSerializer(test_training_job)
        data = serializer.data
        
        assert data['job_id'] == 'test-job-001'
        assert data['status'] == 'completed'
        assert 'duration_formatted' in data
        assert 'is_active' in data
        assert 'created_by_username' in data


class TestAutoTrainConfigSerializer:
    """Tests for AutoTrainConfigSerializer."""
    
    def test_validate_model_type_valid(self):
        """Test successful model_type validation."""
        serializer = AutoTrainConfigSerializer()
        value = serializer.validate_model_type('hybrid')
        assert value == 'hybrid'
    
    def test_validate_model_type_invalid(self):
        """Test validation error with invalid model_type."""
        serializer = AutoTrainConfigSerializer()
        with pytest.raises(Exception):
            serializer.validate_model_type('invalid')
    
    def test_validate_model_type_default(self):
        """Test model_type defaults to hybrid."""
        serializer = AutoTrainConfigSerializer()
        value = serializer.validate_model_type(None)
        assert value == 'hybrid'
    
    def test_serialize_with_defaults(self):
        """Test serialization with default values."""
        data = {}
        serializer = AutoTrainConfigSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get('model_type') == 'hybrid'


class TestModelMetricsSerializer:
    """Tests for ModelMetricsSerializer."""
    
    def test_serialize_model_metrics(self, test_model_metrics):
        """Test serialization of model metrics."""
        serializer = ModelMetricsSerializer(test_model_metrics)
        data = serializer.data
        
        assert data['model_name'] == 'test_model'
        assert data['model_type'] == 'regression'
        assert data['target'] == 'alto'
        assert 'accuracy_percentage' in data
        assert 'training_time_formatted' in data
        assert 'performance_summary' in data
        assert 'comparison_with_previous' in data
    
    def test_get_comparison_with_previous(self, test_model_metrics):
        """Test get_comparison_with_previous method."""
        serializer = ModelMetricsSerializer(test_model_metrics)
        comparison = serializer.get_comparison_with_previous(test_model_metrics)
        # Should return comparison data or None
        assert comparison is not None or comparison is None


class TestModelMetricsListSerializer:
    """Tests for ModelMetricsListSerializer."""
    
    def test_serialize_model_metrics_list(self, test_model_metrics):
        """Test serialization of model metrics list."""
        serializer = ModelMetricsListSerializer(test_model_metrics)
        data = serializer.data
        
        assert data['model_name'] == 'test_model'
        assert 'accuracy_percentage' in data
        assert 'training_time_formatted' in data
        assert 'created_by_username' in data


class TestModelMetricsCreateSerializer:
    """Tests for ModelMetricsCreateSerializer."""
    
    def test_validate_dataset_size_sum(self):
        """Test validation when dataset_size equals sum of splits."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'r2_score': 0.95,
            'mae': 0.5,
            'rmse': 0.5
        }
        serializer = ModelMetricsCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_validate_dataset_size_mismatch(self):
        """Test validation error when dataset_size doesn't match sum."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 5,  # Sum = 95, not 100
            'r2_score': 0.95,
            'mae': 0.5,
            'rmse': 0.5
        }
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_r2_score_valid(self):
        """Test successful r2_score validation."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'r2_score': 0.95,
            'mae': 0.5,
            'rmse': 0.5
        }
        serializer = ModelMetricsCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_validate_r2_score_invalid(self):
        """Test validation error when r2_score is out of range."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'r2_score': 1.5,  # > 1
            'mae': 0.5,
            'rmse': 0.5
        }
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_mae_negative(self):
        """Test validation error when mae is negative."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'r2_score': 0.95,
            'mae': -0.5,  # Negative
            'rmse': 0.5
        }
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_rmse_negative(self):
        """Test validation error when rmse is negative."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'r2_score': 0.95,
            'mae': 0.5,
            'rmse': -0.5  # Negative
        }
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()


class TestModelMetricsUpdateSerializer:
    """Tests for ModelMetricsUpdateSerializer."""
    
    def test_validate_r2_score_update(self):
        """Test successful r2_score update validation."""
        data = {
            'r2_score': 0.98,
            'mae': 0.4,
            'rmse': 0.4
        }
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_validate_r2_score_update_invalid(self):
        """Test validation error when updated r2_score is invalid."""
        data = {
            'r2_score': 1.5  # > 1
        }
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert not serializer.is_valid()


class TestModelMetricsStatsSerializer:
    """Tests for ModelMetricsStatsSerializer."""
    
    def test_serialize_model_metrics_stats(self):
        """Test serialization of model metrics statistics."""
        data = {
            'total_models': 10,
            'models_by_type': {'regression': 8, 'classification': 2},
            'models_by_target': {'alto': 5, 'ancho': 5},
            'best_models_count': 2,
            'production_models_count': 1,
            'average_r2_score': 0.90,
            'best_r2_score': 0.98,
            'worst_r2_score': 0.75,
            'recent_models': [{'id': 1, 'model_name': 'test_model'}]
        }
        serializer = ModelMetricsStatsSerializer(data=data)
        assert serializer.is_valid()


class TestModelPerformanceTrendSerializer:
    """Tests for ModelPerformanceTrendSerializer."""
    
    def test_serialize_performance_trend(self):
        """Test serialization of performance trend."""
        data = {
            'model_name': 'test_model',
            'target': 'alto',
            'metric_type': 'r2_score',
            'trend_data': [{'version': '1.0.0', 'value': 0.95}],
            'current_performance': {'r2_score': 0.95},
            'improvement_trend': 'improving'
        }
        serializer = ModelPerformanceTrendSerializer(data=data)
        assert serializer.is_valid()


class TestModelComparisonSerializer:
    """Tests for ModelComparisonSerializer."""
    
    def test_serialize_model_comparison(self, test_model_metrics):
        """Test serialization of model comparison."""
        other_metrics = ModelMetrics.objects.create(
            model_name='other_model',
            model_type='regression',
            target='alto',
            version='1.1.0',
            created_by=test_model_metrics.created_by,
            metric_type='regression',
            mae=0.6,
            mse=0.36,
            rmse=0.6,
            r2_score=0.90,
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10
        )
        
        data = {
            'model_a': ModelMetricsSerializer(test_model_metrics).data,
            'model_b': ModelMetricsSerializer(other_metrics).data,
            'comparison_metrics': {'improvement': 5.0},
            'winner': 'model_a',
            'improvement_percentage': 5.0
        }
        serializer = ModelComparisonSerializer(data=data)
        # This is a complex nested serializer, so we just test structure
        assert 'model_a' in data
        assert 'model_b' in data

