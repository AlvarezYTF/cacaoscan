"""
Tests for ML serializers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
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


@pytest.mark.django_db
class TestModelsStatusSerializer:
    """Tests for ModelsStatusSerializer."""
    
    def test_validate_success(self):
        """Test validate with valid data."""
        data = {
            'status': 'loaded',
            'device': 'cpu',
            'model': 'hybrid',
            'model_details': {},
            'scalers': 'loaded'
        }
        
        serializer = ModelsStatusSerializer(data=data)
        assert serializer.is_valid()
    
    def test_validate_missing_status(self):
        """Test validate with missing status."""
        data = {
            'device': 'cpu',
            'model': 'hybrid'
        }
        
        serializer = ModelsStatusSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_missing_model(self):
        """Test validate with missing model."""
        data = {
            'status': 'loaded',
            'device': 'cpu'
        }
        
        serializer = ModelsStatusSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestLoadModelsResponseSerializer:
    """Tests for LoadModelsResponseSerializer."""
    
    def test_serialize_success(self):
        """Test serializing success response."""
        data = {
            'message': 'Models loaded successfully',
            'status': 'success'
        }
        
        serializer = LoadModelsResponseSerializer(data=data)
        assert serializer.is_valid()
    
    def test_serialize_error(self):
        """Test serializing error response."""
        data = {
            'error': 'Failed to load models',
            'status': 'error'
        }
        
        serializer = LoadModelsResponseSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestTrainingJobSerializer:
    """Tests for TrainingJobSerializer."""
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def training_job(self, user):
        """Create test training job."""
        from training.models import TrainingJob
        return TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='test_model',
            dataset_size=100,
            epochs=50,
            batch_size=16,
            learning_rate=0.001
        )
    
    def test_serialize_training_job(self, training_job):
        """Test serializing a training job."""
        serializer = TrainingJobSerializer(training_job)
        data = serializer.data
        
        assert data['job_id'] == 'job_123'
        assert data['job_type'] == 'regression'
        assert 'duration_formatted' in data
        assert 'is_active' in data
        assert 'created_by_username' in data
    
    def test_validate_epochs_too_small(self):
        """Test validate_epochs with value too small."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_epochs(0)
    
    def test_validate_epochs_too_large(self):
        """Test validate_epochs with value too large."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_epochs(1001)
    
    def test_validate_epochs_valid(self):
        """Test validate_epochs with valid value."""
        serializer = TrainingJobSerializer()
        
        result = serializer.validate_epochs(50)
        assert result == 50
    
    def test_validate_batch_size_too_small(self):
        """Test validate_batch_size with value too small."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_batch_size(0)
    
    def test_validate_batch_size_too_large(self):
        """Test validate_batch_size with value too large."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_batch_size(129)
    
    def test_validate_batch_size_valid(self):
        """Test validate_batch_size with valid value."""
        serializer = TrainingJobSerializer()
        
        result = serializer.validate_batch_size(32)
        assert result == 32
    
    def test_validate_learning_rate_too_small(self):
        """Test validate_learning_rate with value too small."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_learning_rate(0)
    
    def test_validate_learning_rate_too_large(self):
        """Test validate_learning_rate with value too large."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_learning_rate(1.1)
    
    def test_validate_learning_rate_valid(self):
        """Test validate_learning_rate with valid value."""
        serializer = TrainingJobSerializer()
        
        result = serializer.validate_learning_rate(0.001)
        assert result == 0.001
    
    def test_validate_dataset_size_too_small(self):
        """Test validate_dataset_size with value too small."""
        serializer = TrainingJobSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_dataset_size(0)
    
    def test_validate_dataset_size_valid(self):
        """Test validate_dataset_size with valid value."""
        serializer = TrainingJobSerializer()
        
        result = serializer.validate_dataset_size(100)
        assert result == 100


@pytest.mark.django_db
class TestTrainingJobCreateSerializer:
    """Tests for TrainingJobCreateSerializer."""
    
    def test_validate_job_type_invalid(self):
        """Test validate_job_type with invalid type."""
        serializer = TrainingJobCreateSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_job_type('invalid')
    
    def test_validate_job_type_valid(self):
        """Test validate_job_type with valid types."""
        serializer = TrainingJobCreateSerializer()
        
        for job_type in ['regression', 'vision', 'incremental']:
            result = serializer.validate_job_type(job_type)
            assert result == job_type
    
    def test_validate_model_name_empty(self):
        """Test validate_model_name with empty name."""
        serializer = TrainingJobCreateSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_model_name('')
    
    def test_validate_model_name_whitespace(self):
        """Test validate_model_name with whitespace only."""
        serializer = TrainingJobCreateSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_model_name('   ')
    
    def test_validate_model_name_valid(self):
        """Test validate_model_name with valid name."""
        serializer = TrainingJobCreateSerializer()
        
        result = serializer.validate_model_name('  test_model  ')
        assert result == 'test_model'


@pytest.mark.django_db
class TestTrainingJobStatusSerializer:
    """Tests for TrainingJobStatusSerializer."""
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def training_job(self, user):
        """Create test training job."""
        from training.models import TrainingJob
        return TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='test_model',
            dataset_size=100
        )
    
    def test_serialize_training_job_status(self, training_job):
        """Test serializing a training job status."""
        serializer = TrainingJobStatusSerializer(training_job)
        data = serializer.data
        
        assert data['job_id'] == 'job_123'
        assert 'duration_formatted' in data
        assert 'is_active' in data
        assert 'created_by_username' in data


@pytest.mark.django_db
class TestAutoTrainConfigSerializer:
    """Tests for AutoTrainConfigSerializer."""
    
    def test_validate_model_type_invalid(self):
        """Test validate_model_type with invalid type."""
        serializer = AutoTrainConfigSerializer()
        
        with pytest.raises(ValidationError):
            serializer.validate_model_type('invalid')
    
    def test_validate_model_type_valid(self):
        """Test validate_model_type with valid type."""
        serializer = AutoTrainConfigSerializer()
        
        result = serializer.validate_model_type('hybrid')
        assert result == 'hybrid'
    
    def test_validate_model_type_none(self):
        """Test validate_model_type with None (defaults to hybrid)."""
        serializer = AutoTrainConfigSerializer()
        
        result = serializer.validate_model_type(None)
        assert result == 'hybrid'
    
    def test_serialize_with_defaults(self):
        """Test serializing with default values."""
        data = {}
        
        serializer = AutoTrainConfigSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['model_type'] == 'hybrid'


@pytest.mark.django_db
class TestModelMetricsSerializer:
    """Tests for ModelMetricsSerializer."""
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def model_metrics(self, user):
        """Create test model metrics."""
        from training.models import ModelMetrics
        return ModelMetrics.objects.create(
            model_name='test_model',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.95,
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=16,
            learning_rate=0.001
        )
    
    def test_serialize_model_metrics(self, model_metrics):
        """Test serializing model metrics."""
        serializer = ModelMetricsSerializer(model_metrics)
        data = serializer.data
        
        assert data['model_name'] == 'test_model'
        assert 'accuracy_percentage' in data
        assert 'training_time_formatted' in data
        assert 'performance_summary' in data
        assert 'dataset_summary' in data
        assert 'model_summary' in data
        assert 'comparison_with_previous' in data
        assert 'created_by_username' in data
    
    def test_get_comparison_with_previous(self, model_metrics):
        """Test get_comparison_with_previous method."""
        with patch.object(model_metrics, 'get_comparison_with_previous', return_value={'improvement': 0.1}):
            serializer = ModelMetricsSerializer()
            comparison = serializer.get_comparison_with_previous(model_metrics)
            assert comparison['improvement'] == 0.1


@pytest.mark.django_db
class TestModelMetricsListSerializer:
    """Tests for ModelMetricsListSerializer."""
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def model_metrics(self, user):
        """Create test model metrics."""
        from training.models import ModelMetrics
        return ModelMetrics.objects.create(
            model_name='test_model',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.95,
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=16,
            learning_rate=0.001
        )
    
    def test_serialize_model_metrics_list(self, model_metrics):
        """Test serializing model metrics for list."""
        serializer = ModelMetricsListSerializer(model_metrics)
        data = serializer.data
        
        assert data['model_name'] == 'test_model'
        assert 'accuracy_percentage' in data
        assert 'training_time_formatted' in data
        assert 'created_by_username' in data


@pytest.mark.django_db
class TestModelMetricsCreateSerializer:
    """Tests for ModelMetricsCreateSerializer."""
    
    def test_validate_dataset_size_mismatch(self):
        """Test validate with dataset size mismatch."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0',
            'metric_type': 'training',
            'mae': 0.5,
            'mse': 0.25,
            'rmse': 0.5,
            'r2_score': 0.95,
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 5,  # Should be 10 to match
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.001
        }
        
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_r2_score_out_of_range(self):
        """Test validate with r2_score out of range."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0',
            'metric_type': 'training',
            'mae': 0.5,
            'mse': 0.25,
            'rmse': 0.5,
            'r2_score': 1.5,  # Out of range
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.001
        }
        
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_mae_negative(self):
        """Test validate with negative MAE."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0',
            'metric_type': 'training',
            'mae': -0.5,  # Negative
            'mse': 0.25,
            'rmse': 0.5,
            'r2_score': 0.95,
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.001
        }
        
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_mse_negative(self):
        """Test validate with negative MSE."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0',
            'metric_type': 'training',
            'mae': 0.5,
            'mse': -0.25,  # Negative
            'rmse': 0.5,
            'r2_score': 0.95,
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.001
        }
        
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_rmse_negative(self):
        """Test validate with negative RMSE."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0',
            'metric_type': 'training',
            'mae': 0.5,
            'mse': 0.25,
            'rmse': -0.5,  # Negative
            'r2_score': 0.95,
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.001
        }
        
        serializer = ModelMetricsCreateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_success(self):
        """Test validate with valid data."""
        data = {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0',
            'metric_type': 'training',
            'mae': 0.5,
            'mse': 0.25,
            'rmse': 0.5,
            'r2_score': 0.95,
            'dataset_size': 100,
            'train_size': 70,
            'validation_size': 20,
            'test_size': 10,
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.001
        }
        
        serializer = ModelMetricsCreateSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestModelMetricsUpdateSerializer:
    """Tests for ModelMetricsUpdateSerializer."""
    
    def test_validate_metric_value_none(self):
        """Test _validate_metric_value with None."""
        serializer = ModelMetricsUpdateSerializer()
        
        result = serializer._validate_metric_value(None, 'test_metric')
        assert result is None
    
    def test_validate_metric_value_below_min(self):
        """Test _validate_metric_value below minimum."""
        serializer = ModelMetricsUpdateSerializer()
        
        result = serializer._validate_metric_value(-1.0, 'test_metric', min_value=0.0)
        assert result is not None
        assert 'mayor o igual' in result
    
    def test_validate_metric_value_above_max(self):
        """Test _validate_metric_value above maximum."""
        serializer = ModelMetricsUpdateSerializer()
        
        result = serializer._validate_metric_value(2.0, 'test_metric', max_value=1.0)
        assert result is not None
        assert 'menor o igual' in result
    
    def test_validate_metric_value_valid(self):
        """Test _validate_metric_value with valid value."""
        serializer = ModelMetricsUpdateSerializer()
        
        result = serializer._validate_metric_value(0.5, 'test_metric', min_value=0.0, max_value=1.0)
        assert result is None
    
    def test_validate_r2_score_out_of_range(self):
        """Test validate with r2_score out of range."""
        data = {
            'r2_score': 1.5
        }
        
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_mae_negative(self):
        """Test validate with negative MAE."""
        data = {
            'mae': -0.5
        }
        
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_mse_negative(self):
        """Test validate with negative MSE."""
        data = {
            'mse': -0.25
        }
        
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_rmse_negative(self):
        """Test validate with negative RMSE."""
        data = {
            'rmse': -0.5
        }
        
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_validate_success(self):
        """Test validate with valid data."""
        data = {
            'mae': 0.5,
            'mse': 0.25,
            'rmse': 0.5,
            'r2_score': 0.95
        }
        
        serializer = ModelMetricsUpdateSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestModelMetricsStatsSerializer:
    """Tests for ModelMetricsStatsSerializer."""
    
    def test_serialize_model_metrics_stats(self):
        """Test serializing model metrics stats."""
        data = {
            'total_models': 10,
            'models_by_type': {},
            'models_by_target': {},
            'best_models_count': 2,
            'production_models_count': 1,
            'average_r2_score': 0.9,
            'best_r2_score': 0.95,
            'worst_r2_score': 0.8,
            'recent_models': []
        }
        
        serializer = ModelMetricsStatsSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestModelPerformanceTrendSerializer:
    """Tests for ModelPerformanceTrendSerializer."""
    
    def test_serialize_model_performance_trend(self):
        """Test serializing model performance trend."""
        data = {
            'model_name': 'test_model',
            'target': 'alto',
            'metric_type': 'training',
            'trend_data': [],
            'current_performance': {},
            'improvement_trend': 'improving'
        }
        
        serializer = ModelPerformanceTrendSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestModelComparisonSerializer:
    """Tests for ModelComparisonSerializer."""
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def model_metrics_a(self, user):
        """Create test model metrics A."""
        from training.models import ModelMetrics
        return ModelMetrics.objects.create(
            model_name='test_model',
            model_type='regression',
            target='alto',
            version='1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.95,
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=16,
            learning_rate=0.001
        )
    
    @pytest.fixture
    def model_metrics_b(self, user):
        """Create test model metrics B."""
        from training.models import ModelMetrics
        return ModelMetrics.objects.create(
            model_name='test_model',
            model_type='regression',
            target='alto',
            version='2.0',
            created_by=user,
            metric_type='training',
            mae=0.4,
            mse=0.16,
            rmse=0.4,
            r2_score=0.97,
            dataset_size=100,
            train_size=70,
            validation_size=20,
            test_size=10,
            epochs=50,
            batch_size=16,
            learning_rate=0.001
        )
    
    def test_serialize_model_comparison(self, model_metrics_a, model_metrics_b):
        """Test serializing model comparison."""
        data = {
            'model_a': ModelMetricsSerializer(model_metrics_a).data,
            'model_b': ModelMetricsSerializer(model_metrics_b).data,
            'comparison_metrics': {},
            'winner': 'model_b',
            'improvement_percentage': 2.1
        }
        
        serializer = ModelComparisonSerializer(data=data)
        assert serializer.is_valid()


