"""
Unit tests for ML serializers.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import serializers
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
    TEST_USER_PASSWORD,
)


class ModelsStatusSerializerTest(TestCase):
    """Tests for ModelsStatusSerializer."""
    
    def test_models_status_serialization_success(self):
        """Test successful models status serialization."""
        serializer = ModelsStatusSerializer(data={
            'status': 'loaded',
            'device': 'cpu',
            'model': 'hybrid',
            'model_details': {'version': '1.0.0'},
            'scalers': 'loaded'
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['status'], 'loaded')
    
    def test_models_status_missing_status(self):
        """Test models status without status field."""
        serializer = ModelsStatusSerializer(data={
            'device': 'cpu',
            'model': 'hybrid'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_models_status_missing_model(self):
        """Test models status without model field."""
        serializer = ModelsStatusSerializer(data={
            'status': 'loaded',
            'device': 'cpu'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class LoadModelsResponseSerializerTest(TestCase):
    """Tests for LoadModelsResponseSerializer."""
    
    def test_load_models_response_success(self):
        """Test successful load models response."""
        serializer = LoadModelsResponseSerializer(data={
            'status': 'success',
            'message': 'Models loaded successfully'
        })
        self.assertTrue(serializer.is_valid())
    
    def test_load_models_response_with_error(self):
        """Test load models response with error."""
        serializer = LoadModelsResponseSerializer(data={
            'status': 'error',
            'error': 'Failed to load models'
        })
        self.assertTrue(serializer.is_valid())


class TrainingJobSerializerTest(TestCase):
    """Tests for TrainingJobSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    @patch('api.serializers.ml_serializers.TrainingJob')
    def test_training_job_serialization_success(self, mock_job_model):
        """Test successful training job serialization."""
        mock_job = Mock()
        mock_job.id = 1
        mock_job.job_id = 'job-123'
        mock_job.job_type = 'regression'
        mock_job.status = 'running'
        mock_job.created_by = self.user
        mock_job.created_by.username = TEST_USER_USERNAME
        mock_job.model_name = 'test_model'
        mock_job.dataset_size = 1000
        mock_job.epochs = 50
        mock_job.batch_size = 32
        mock_job.learning_rate = 0.001
        mock_job.config_params = {}
        mock_job.metrics = {}
        mock_job.model_path = None
        mock_job.logs = None
        mock_job.created_at = timezone.now()
        mock_job.started_at = None
        mock_job.completed_at = None
        mock_job.error_message = None
        mock_job.progress_percentage = 50
        mock_job.duration_formatted = '1h 30m'
        mock_job.is_active = True
        
        serializer = TrainingJobSerializer(mock_job)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('job_id', data)
        self.assertIn('job_type', data)
        self.assertIn('status', data)
        self.assertIn('created_by_username', data)
    
    def test_training_job_validation_invalid_epochs(self):
        """Test training job validation with invalid epochs."""
        serializer = TrainingJobSerializer(data={
            'epochs': 0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('epochs', serializer.errors)
    
    def test_training_job_validation_epochs_too_high(self):
        """Test training job validation with epochs too high."""
        serializer = TrainingJobSerializer(data={
            'epochs': 1001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('epochs', serializer.errors)
    
    def test_training_job_validation_invalid_batch_size(self):
        """Test training job validation with invalid batch size."""
        serializer = TrainingJobSerializer(data={
            'batch_size': 0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('batch_size', serializer.errors)
    
    def test_training_job_validation_batch_size_too_high(self):
        """Test training job validation with batch size too high."""
        serializer = TrainingJobSerializer(data={
            'batch_size': 129
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('batch_size', serializer.errors)
    
    def test_training_job_validation_invalid_learning_rate(self):
        """Test training job validation with invalid learning rate."""
        serializer = TrainingJobSerializer(data={
            'learning_rate': -0.1
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('learning_rate', serializer.errors)
    
    def test_training_job_validation_learning_rate_too_high(self):
        """Test training job validation with learning rate too high."""
        serializer = TrainingJobSerializer(data={
            'learning_rate': 1.1
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('learning_rate', serializer.errors)
    
    def test_training_job_validation_invalid_dataset_size(self):
        """Test training job validation with invalid dataset size."""
        serializer = TrainingJobSerializer(data={
            'dataset_size': 0
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('dataset_size', serializer.errors)


class TrainingJobCreateSerializerTest(TestCase):
    """Tests for TrainingJobCreateSerializer."""
    
    def test_training_job_create_success(self):
        """Test successful training job creation."""
        serializer = TrainingJobCreateSerializer(data={
            'job_type': 'regression',
            'model_name': 'test_model',
            'dataset_size': 1000,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertTrue(serializer.is_valid())
    
    def test_training_job_create_invalid_job_type(self):
        """Test training job creation with invalid job type."""
        serializer = TrainingJobCreateSerializer(data={
            'job_type': 'invalid_type',
            'model_name': 'test_model',
            'dataset_size': 1000,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('job_type', serializer.errors)
    
    def test_training_job_create_empty_model_name(self):
        """Test training job creation with empty model name."""
        serializer = TrainingJobCreateSerializer(data={
            'job_type': 'regression',
            'model_name': '',
            'dataset_size': 1000,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('model_name', serializer.errors)


class TrainingJobStatusSerializerTest(TestCase):
    """Tests for TrainingJobStatusSerializer."""
    
    @patch('api.serializers.ml_serializers.TrainingJob')
    def test_training_job_status_serialization_success(self, mock_job_model):
        """Test successful training job status serialization."""
        mock_job = Mock()
        mock_job.id = 1
        mock_job.job_id = 'job-123'
        mock_job.job_type = 'regression'
        mock_job.status = 'running'
        mock_job.created_by.username = TEST_USER_USERNAME
        mock_job.model_name = 'test_model'
        mock_job.progress_percentage = 50
        mock_job.created_at = timezone.now()
        mock_job.started_at = None
        mock_job.completed_at = None
        mock_job.duration_formatted = '1h 30m'
        mock_job.is_active = True
        
        serializer = TrainingJobStatusSerializer(mock_job)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('job_id', data)
        self.assertIn('status', data)
        self.assertIn('progress_percentage', data)


class AutoTrainConfigSerializerTest(TestCase):
    """Tests for AutoTrainConfigSerializer."""
    
    def test_auto_train_config_success(self):
        """Test successful auto train config."""
        serializer = AutoTrainConfigSerializer(data={
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.0001,
            'model_type': 'hybrid'
        })
        self.assertTrue(serializer.is_valid())
    
    def test_auto_train_config_defaults(self):
        """Test auto train config with defaults."""
        serializer = AutoTrainConfigSerializer(data={})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['epochs'], 50)
        self.assertEqual(serializer.validated_data['batch_size'], 16)
        self.assertEqual(serializer.validated_data['model_type'], 'hybrid')
    
    def test_auto_train_config_invalid_model_type(self):
        """Test auto train config with invalid model type."""
        serializer = AutoTrainConfigSerializer(data={
            'model_type': 'invalid'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('model_type', serializer.errors)
    
    def test_auto_train_config_invalid_epochs(self):
        """Test auto train config with invalid epochs."""
        serializer = AutoTrainConfigSerializer(data={
            'epochs': 501
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('epochs', serializer.errors)


class ModelMetricsSerializerTest(TestCase):
    """Tests for ModelMetricsSerializer."""
    
    @patch('api.serializers.ml_serializers.ModelMetrics')
    def test_model_metrics_serialization_success(self, mock_metrics_model):
        """Test successful model metrics serialization."""
        mock_metrics = Mock()
        mock_metrics.id = 1
        mock_metrics.model_name = 'test_model'
        mock_metrics.model_type = 'regression'
        mock_metrics.target = 'alto'
        mock_metrics.version = '1.0.0'
        mock_metrics.training_job = None
        mock_metrics.created_by = None
        mock_metrics.created_by.username = TEST_USER_USERNAME if mock_metrics.created_by else None
        mock_metrics.metric_type = 'regression'
        mock_metrics.mae = 2.5
        mock_metrics.mse = 6.25
        mock_metrics.rmse = 2.5
        mock_metrics.r2_score = 0.85
        mock_metrics.mape = 5.0
        mock_metrics.additional_metrics = {}
        mock_metrics.dataset_size = 1000
        mock_metrics.train_size = 700
        mock_metrics.validation_size = 200
        mock_metrics.test_size = 100
        mock_metrics.epochs = 50
        mock_metrics.batch_size = 32
        mock_metrics.learning_rate = 0.001
        mock_metrics.model_params = {}
        mock_metrics.training_time_seconds = 3600
        mock_metrics.inference_time_ms = 50
        mock_metrics.stability_score = 0.9
        mock_metrics.knowledge_retention = 0.95
        mock_metrics.notes = 'Test notes'
        mock_metrics.is_best_model = False
        mock_metrics.is_production_model = False
        mock_metrics.created_at = timezone.now()
        mock_metrics.updated_at = timezone.now()
        mock_metrics.accuracy_percentage = 85.0
        mock_metrics.training_time_formatted = '1h 0m'
        mock_metrics.performance_summary = {}
        mock_metrics.dataset_summary = {}
        mock_metrics.model_summary = {}
        mock_metrics.get_comparison_with_previous.return_value = {}
        
        serializer = ModelMetricsSerializer(mock_metrics)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('model_name', data)
        self.assertIn('r2_score', data)
        self.assertIn('accuracy_percentage', data)


class ModelMetricsCreateSerializerTest(TestCase):
    """Tests for ModelMetricsCreateSerializer."""
    
    def test_model_metrics_create_success(self):
        """Test successful model metrics creation."""
        serializer = ModelMetricsCreateSerializer(data={
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'metric_type': 'regression',
            'mae': 2.5,
            'mse': 6.25,
            'rmse': 2.5,
            'r2_score': 0.85,
            'mape': 5.0,
            'dataset_size': 1000,
            'train_size': 700,
            'validation_size': 200,
            'test_size': 100,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertTrue(serializer.is_valid())
    
    def test_model_metrics_create_dataset_size_mismatch(self):
        """Test model metrics creation with dataset size mismatch."""
        serializer = ModelMetricsCreateSerializer(data={
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'metric_type': 'regression',
            'mae': 2.5,
            'mse': 6.25,
            'rmse': 2.5,
            'r2_score': 0.85,
            'dataset_size': 1000,
            'train_size': 700,
            'validation_size': 200,
            'test_size': 50,  # Should be 100
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_model_metrics_create_invalid_r2_score(self):
        """Test model metrics creation with invalid R² score."""
        serializer = ModelMetricsCreateSerializer(data={
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'metric_type': 'regression',
            'mae': 2.5,
            'mse': 6.25,
            'rmse': 2.5,
            'r2_score': 1.5,  # Invalid: > 1
            'dataset_size': 1000,
            'train_size': 700,
            'validation_size': 200,
            'test_size': 100,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_model_metrics_create_negative_mae(self):
        """Test model metrics creation with negative MAE."""
        serializer = ModelMetricsCreateSerializer(data={
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'metric_type': 'regression',
            'mae': -1.0,  # Invalid: negative
            'mse': 6.25,
            'rmse': 2.5,
            'r2_score': 0.85,
            'dataset_size': 1000,
            'train_size': 700,
            'validation_size': 200,
            'test_size': 100,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class ModelMetricsUpdateSerializerTest(TestCase):
    """Tests for ModelMetricsUpdateSerializer."""
    
    def test_model_metrics_update_success(self):
        """Test successful model metrics update."""
        serializer = ModelMetricsUpdateSerializer(data={
            'mae': 2.3,
            'mse': 5.29,
            'rmse': 2.3,
            'r2_score': 0.87
        })
        self.assertTrue(serializer.is_valid())
    
    def test_model_metrics_update_invalid_r2_score(self):
        """Test model metrics update with invalid R² score."""
        serializer = ModelMetricsUpdateSerializer(data={
            'r2_score': 1.5
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class ModelMetricsStatsSerializerTest(TestCase):
    """Tests for ModelMetricsStatsSerializer."""
    
    def test_model_metrics_stats_serialization_success(self):
        """Test successful model metrics stats serialization."""
        serializer = ModelMetricsStatsSerializer(data={
            'total_models': 50,
            'models_by_type': {'regression': 30, 'vision': 20},
            'models_by_target': {'alto': 15, 'ancho': 15, 'grosor': 10, 'peso': 10},
            'best_models_count': 5,
            'production_models_count': 3,
            'average_r2_score': 0.85,
            'best_r2_score': 0.95,
            'worst_r2_score': 0.70,
            'recent_models': []
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['total_models'], 50)


class ModelPerformanceTrendSerializerTest(TestCase):
    """Tests for ModelPerformanceTrendSerializer."""
    
    def test_model_performance_trend_serialization_success(self):
        """Test successful model performance trend serialization."""
        serializer = ModelPerformanceTrendSerializer(data={
            'model_name': 'test_model',
            'target': 'alto',
            'metric_type': 'r2_score',
            'trend_data': [{'date': '2024-01-01', 'value': 0.80}],
            'current_performance': {'r2_score': 0.85},
            'improvement_trend': 'improving'
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['model_name'], 'test_model')


class ModelComparisonSerializerTest(TestCase):
    """Tests for ModelComparisonSerializer."""
    
    def test_model_comparison_serialization_success(self):
        """Test successful model comparison serialization."""
        model_a_data = {
            'id': 1,
            'model_name': 'model_a',
            'r2_score': 0.80
        }
        model_b_data = {
            'id': 2,
            'model_name': 'model_b',
            'r2_score': 0.85
        }
        
        serializer = ModelComparisonSerializer(data={
            'model_a': model_a_data,
            'model_b': model_b_data,
            'comparison_metrics': {'r2_improvement': 0.05},
            'winner': 'model_b',
            'improvement_percentage': 6.25
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['winner'], 'model_b')

