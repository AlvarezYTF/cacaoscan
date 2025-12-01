"""
Unit tests for training models (TrainingJob, ModelMetrics).
Tests cover model creation, properties, methods, and state management.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from training.models import TrainingJob, ModelMetrics


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def training_job(user):
    """Create a test training job."""
    return TrainingJob.objects.create(
        job_id='test-job-001',
        job_type='regression',
        status='pending',
        created_by=user,
        model_name='resnet18',
        dataset_size=1000,
        epochs=100,
        batch_size=16,
        learning_rate=0.001
    )


class TestTrainingJob:
    """Tests for TrainingJob model."""
    
    def test_training_job_creation(self, user):
        """Test basic training job creation."""
        job = TrainingJob.objects.create(
            job_id='test-job-001',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        assert job.job_id == 'test-job-001'
        assert job.job_type == 'regression'
        assert job.status == 'pending'
        assert job.created_by == user
        assert job.model_name == 'resnet18'
        assert job.dataset_size == 1000
        assert job.epochs == 100
        assert job.batch_size == 16
        assert job.learning_rate == 0.001
        assert job.created_at is not None
    
    def test_training_job_default_values(self, user):
        """Test training job default values."""
        job = TrainingJob.objects.create(
            job_id='test-job-002',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000
        )
        
        assert job.status == 'pending'
        assert job.epochs == 100
        assert job.batch_size == 16
        assert job.learning_rate == 0.001
        assert job.progress_percentage == 0.0
    
    def test_training_job_str_representation(self, training_job):
        """Test string representation of training job."""
        expected = f"Training Job {training_job.job_id} - Modelo de Regresión (pending)"
        assert str(training_job) == expected
    
    def test_training_job_duration_property_completed(self, user):
        """Test duration property when job is completed."""
        started = timezone.now() - timedelta(hours=2)
        completed = timezone.now() - timedelta(hours=1)
        
        job = TrainingJob.objects.create(
            job_id='test-job-duration',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            started_at=started,
            completed_at=completed
        )
        
        duration = job.duration
        assert duration == 3600.0  # 1 hour in seconds
    
    def test_training_job_duration_property_running(self, user):
        """Test duration property when job is running."""
        started = timezone.now() - timedelta(hours=1)
        
        job = TrainingJob.objects.create(
            job_id='test-job-running',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            started_at=started,
            status='running'
        )
        
        duration = job.duration
        assert duration is not None
        assert duration >= 3600.0  # At least 1 hour
    
    def test_training_job_duration_property_not_started(self, training_job):
        """Test duration property when job has not started."""
        assert training_job.duration is None
    
    def test_training_job_duration_formatted_property(self, user):
        """Test duration_formatted property."""
        started = timezone.now() - timedelta(hours=2, minutes=30, seconds=45)
        completed = timezone.now()
        
        job = TrainingJob.objects.create(
            job_id='test-job-formatted',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            started_at=started,
            completed_at=completed
        )
        
        formatted = job.duration_formatted
        assert '2h' in formatted
        assert '30m' in formatted
        assert '45s' in formatted
    
    def test_training_job_duration_formatted_minutes_only(self, user):
        """Test duration_formatted with minutes only."""
        started = timezone.now() - timedelta(minutes=5, seconds=30)
        completed = timezone.now()
        
        job = TrainingJob.objects.create(
            job_id='test-job-minutes',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            started_at=started,
            completed_at=completed
        )
        
        formatted = job.duration_formatted
        assert '5m' in formatted
        assert '30s' in formatted
        assert 'h' not in formatted
    
    def test_training_job_duration_formatted_seconds_only(self, user):
        """Test duration_formatted with seconds only."""
        started = timezone.now() - timedelta(seconds=45)
        completed = timezone.now()
        
        job = TrainingJob.objects.create(
            job_id='test-job-seconds',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            started_at=started,
            completed_at=completed
        )
        
        formatted = job.duration_formatted
        assert '45s' in formatted
        assert 'm' not in formatted
        assert 'h' not in formatted
    
    def test_training_job_duration_formatted_na(self, training_job):
        """Test duration_formatted returns N/A when no duration."""
        assert training_job.duration_formatted == "N/A"
    
    def test_training_job_is_active_property_pending(self, training_job):
        """Test is_active property for pending job."""
        assert training_job.is_active is True
    
    def test_training_job_is_active_property_running(self, user):
        """Test is_active property for running job."""
        job = TrainingJob.objects.create(
            job_id='test-job-running',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            status='running'
        )
        
        assert job.is_active is True
    
    def test_training_job_is_active_property_completed(self, user):
        """Test is_active property for completed job."""
        job = TrainingJob.objects.create(
            job_id='test-job-completed',
            job_type='regression',
            created_by=user,
            model_name='resnet18',
            dataset_size=1000,
            status='completed'
        )
        
        assert job.is_active is False
    
    def test_training_job_update_progress_method(self, training_job):
        """Test update_progress method."""
        training_job.update_progress(50.0, 'Epoch 50/100')
        
        training_job.refresh_from_db()
        assert training_job.progress_percentage == 50.0
        assert 'Epoch 50/100' in training_job.logs
    
    def test_training_job_update_progress_clamps_to_100(self, training_job):
        """Test update_progress clamps percentage to 100."""
        training_job.update_progress(150.0)
        
        training_job.refresh_from_db()
        assert training_job.progress_percentage == 100.0
    
    def test_training_job_update_progress_clamps_to_0(self, training_job):
        """Test update_progress clamps percentage to 0."""
        training_job.update_progress(-10.0)
        
        training_job.refresh_from_db()
        assert training_job.progress_percentage == 0.0
    
    def test_training_job_mark_started_method(self, training_job):
        """Test mark_started method."""
        training_job.mark_started()
        
        training_job.refresh_from_db()
        assert training_job.status == 'running'
        assert training_job.started_at is not None
    
    def test_training_job_mark_completed_method(self, training_job):
        """Test mark_completed method."""
        metrics = {'loss': 0.5, 'accuracy': 0.95}
        model_path = '/path/to/model.pth'
        
        training_job.mark_completed(metrics=metrics, model_path=model_path)
        
        training_job.refresh_from_db()
        assert training_job.status == 'completed'
        assert training_job.completed_at is not None
        assert training_job.progress_percentage == 100.0
        assert training_job.metrics == metrics
        assert training_job.model_path == model_path
    
    def test_training_job_mark_failed_method(self, training_job):
        """Test mark_failed method."""
        error_message = 'Training failed: Out of memory'
        
        training_job.mark_failed(error_message)
        
        training_job.refresh_from_db()
        assert training_job.status == 'failed'
        assert training_job.completed_at is not None
        assert training_job.error_message == error_message
    
    def test_training_job_mark_cancelled_method(self, training_job):
        """Test mark_cancelled method."""
        training_job.mark_cancelled()
        
        training_job.refresh_from_db()
        assert training_job.status == 'cancelled'
        assert training_job.completed_at is not None
    
    def test_training_job_job_type_choices(self, user):
        """Test that job_type accepts valid choices."""
        valid_types = ['regression', 'vision', 'incremental']
        
        for job_type in valid_types:
            job = TrainingJob.objects.create(
                job_id=f'test-{job_type}',
                job_type=job_type,
                created_by=user,
                model_name='test',
                dataset_size=1000
            )
            assert job.job_type == job_type
    
    def test_training_job_status_choices(self, user):
        """Test that status accepts valid choices."""
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        
        for status in valid_statuses:
            job = TrainingJob.objects.create(
                job_id=f'test-{status}',
                job_type='regression',
                created_by=user,
                model_name='test',
                dataset_size=1000,
                status=status
            )
            assert job.status == status
    
    def test_training_job_config_params_json_field(self, user):
        """Test config_params JSON field."""
        config = {
            'optimizer': 'adam',
            'scheduler': 'cosine',
            'early_stopping': True
        }
        
        job = TrainingJob.objects.create(
            job_id='test-config',
            job_type='regression',
            created_by=user,
            model_name='test',
            dataset_size=1000,
            config_params=config
        )
        
        assert job.config_params == config
    
    def test_training_job_metrics_json_field(self, user):
        """Test metrics JSON field."""
        metrics = {
            'train_loss': 0.5,
            'val_loss': 0.6,
            'r2_score': 0.85
        }
        
        job = TrainingJob.objects.create(
            job_id='test-metrics',
            job_type='regression',
            created_by=user,
            model_name='test',
            dataset_size=1000,
            metrics=metrics
        )
        
        assert job.metrics == metrics
    
    def test_training_job_unique_job_id(self, user):
        """Test that job_id is unique."""
        TrainingJob.objects.create(
            job_id='unique-job',
            job_type='regression',
            created_by=user,
            model_name='test',
            dataset_size=1000
        )
        
        with pytest.raises(Exception):  # IntegrityError
            TrainingJob.objects.create(
                job_id='unique-job',
                job_type='regression',
                created_by=user,
                model_name='test',
                dataset_size=1000
            )
    
    def test_training_job_cascade_delete_with_user(self, user):
        """Test that jobs are deleted when user is deleted."""
        job = TrainingJob.objects.create(
            job_id='test-cascade',
            job_type='regression',
            created_by=user,
            model_name='test',
            dataset_size=1000
        )
        job_id = job.id
        
        user.delete()
        
        assert not TrainingJob.objects.filter(id=job_id).exists()


class TestModelMetrics:
    """Tests for ModelMetrics model."""
    
    def test_model_metrics_creation(self, user):
        """Test basic model metrics creation."""
        metrics = ModelMetrics.objects.create(
            model_name='resnet18',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            mape=5.0,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        assert metrics.model_name == 'resnet18'
        assert metrics.model_type == 'regression'
        assert metrics.target == 'alto'
        assert metrics.version == 'v1.0'
        assert metrics.created_by == user
        assert metrics.metric_type == 'training'
        assert metrics.mae == 0.5
        assert metrics.mse == 0.25
        assert metrics.rmse == 0.5
        assert metrics.r2_score == 0.85
        assert metrics.mape == 5.0
        assert metrics.dataset_size == 1000
        assert metrics.train_size == 700
        assert metrics.validation_size == 200
        assert metrics.test_size == 100
        assert metrics.epochs == 100
        assert metrics.batch_size == 16
        assert metrics.learning_rate == 0.001
        assert metrics.created_at is not None
        assert metrics.updated_at is not None
    
    def test_model_metrics_optional_fields(self, user):
        """Test optional fields can be null."""
        metrics = ModelMetrics.objects.create(
            model_name='test',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        assert metrics.mape is None
        assert metrics.training_time_seconds is None
        assert metrics.inference_time_ms is None
        assert metrics.stability_score is None
        assert metrics.knowledge_retention is None
    
    def test_model_metrics_default_values(self, user):
        """Test default values."""
        metrics = ModelMetrics.objects.create(
            model_name='test',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        assert metrics.is_best_model is False
        assert metrics.is_production_model is False
        assert metrics.additional_metrics == {}
        assert metrics.model_params == {}
        assert metrics.notes == ''
    
    def test_model_metrics_model_type_choices(self, user):
        """Test that model_type accepts valid choices."""
        valid_types = ['regression', 'classification', 'segmentation', 'incremental']
        
        for model_type in valid_types:
            metrics = ModelMetrics.objects.create(
                model_name='test',
                model_type=model_type,
                target='alto',
                version='v1.0',
                created_by=user,
                metric_type='training',
                mae=0.5,
                mse=0.25,
                rmse=0.5,
                r2_score=0.85,
                dataset_size=1000,
                train_size=700,
                validation_size=200,
                test_size=100,
                epochs=100,
                batch_size=16,
                learning_rate=0.001
            )
            assert metrics.model_type == model_type
    
    def test_model_metrics_target_choices(self, user):
        """Test that target accepts valid choices."""
        valid_targets = ['alto', 'ancho', 'grosor', 'peso', 'calidad', 'variedad']
        
        for target in valid_targets:
            metrics = ModelMetrics.objects.create(
                model_name='test',
                model_type='regression',
                target=target,
                version='v1.0',
                created_by=user,
                metric_type='training',
                mae=0.5,
                mse=0.25,
                rmse=0.5,
                r2_score=0.85,
                dataset_size=1000,
                train_size=700,
                validation_size=200,
                test_size=100,
                epochs=100,
                batch_size=16,
                learning_rate=0.001
            )
            assert metrics.target == target
    
    def test_model_metrics_metric_type_choices(self, user):
        """Test that metric_type accepts valid choices."""
        valid_types = ['training', 'validation', 'test', 'incremental']
        
        for metric_type in valid_types:
            metrics = ModelMetrics.objects.create(
                model_name='test',
                model_type='regression',
                target='alto',
                version='v1.0',
                created_by=user,
                metric_type=metric_type,
                mae=0.5,
                mse=0.25,
                rmse=0.5,
                r2_score=0.85,
                dataset_size=1000,
                train_size=700,
                validation_size=200,
                test_size=100,
                epochs=100,
                batch_size=16,
                learning_rate=0.001
            )
            assert metrics.metric_type == metric_type
    
    def test_model_metrics_additional_metrics_json_field(self, user):
        """Test additional_metrics JSON field."""
        additional = {
            'precision': 0.92,
            'recall': 0.88,
            'f1_score': 0.90
        }
        
        metrics = ModelMetrics.objects.create(
            model_name='test',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001,
            additional_metrics=additional
        )
        
        assert metrics.additional_metrics == additional
    
    def test_model_metrics_model_params_json_field(self, user):
        """Test model_params JSON field."""
        params = {
            'num_layers': 18,
            'dropout': 0.3,
            'activation': 'relu'
        }
        
        metrics = ModelMetrics.objects.create(
            model_name='test',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001,
            model_params=params
        )
        
        assert metrics.model_params == params
    
    def test_model_metrics_cascade_delete_with_user(self, user):
        """Test that metrics are deleted when user is deleted."""
        metrics = ModelMetrics.objects.create(
            model_name='test',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        metrics_id = metrics.id
        
        user.delete()
        
        assert not ModelMetrics.objects.filter(id=metrics_id).exists()
    
    def test_model_metrics_ordering(self, user):
        """Test that metrics are ordered by created_at descending."""
        metrics1 = ModelMetrics.objects.create(
            model_name='test1',
            model_type='regression',
            target='alto',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.5,
            mse=0.25,
            rmse=0.5,
            r2_score=0.85,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        import time
        time.sleep(0.01)
        
        metrics2 = ModelMetrics.objects.create(
            model_name='test2',
            model_type='regression',
            target='ancho',
            version='v1.0',
            created_by=user,
            metric_type='training',
            mae=0.6,
            mse=0.30,
            rmse=0.55,
            r2_score=0.80,
            dataset_size=1000,
            train_size=700,
            validation_size=200,
            test_size=100,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        all_metrics = list(ModelMetrics.objects.filter(created_by=user))
        assert all_metrics[0].id == metrics2.id
        assert all_metrics[1].id == metrics1.id

