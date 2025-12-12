"""
Tests for training models.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from training.models import TrainingJob, ModelMetrics


@pytest.mark.django_db
class TestTrainingJob:
    """Tests for TrainingJob model."""
    
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
    
    def test_training_job_str(self, training_job):
        """Test TrainingJob __str__ method."""
        job_str = str(training_job)
        assert 'job_123' in job_str
        assert 'Regresión' in job_str or 'regression' in job_str.lower() or 'Modelo de Regresión' in job_str
        assert 'pending' in job_str
    
    def test_duration_with_both_times(self, training_job):
        """Test duration property with both started_at and completed_at."""
        training_job.started_at = timezone.now() - timedelta(hours=1)
        training_job.completed_at = timezone.now()
        training_job.save()
        
        duration = training_job.duration
        assert duration is not None
        assert duration == pytest.approx(3600, abs=10)  # Approximately 1 hour
    
    def test_duration_with_only_started_at(self, training_job):
        """Test duration property with only started_at."""
        training_job.started_at = timezone.now() - timedelta(hours=1)
        training_job.save()
        
        duration = training_job.duration
        assert duration is not None
        assert duration == pytest.approx(3600, abs=10)
    
    def test_duration_without_times(self, training_job):
        """Test duration property without times."""
        duration = training_job.duration
        assert duration is None
    
    def test_duration_formatted_with_hours(self, training_job):
        """Test duration_formatted property with hours."""
        training_job.started_at = timezone.now() - timedelta(hours=2, minutes=30, seconds=45)
        training_job.completed_at = timezone.now()
        training_job.save()
        
        formatted = training_job.duration_formatted
        assert '2h' in formatted
        assert '30m' in formatted
        assert '45s' in formatted
    
    def test_duration_formatted_with_minutes(self, training_job):
        """Test duration_formatted property with minutes only."""
        training_job.started_at = timezone.now() - timedelta(minutes=30, seconds=45)
        training_job.completed_at = timezone.now()
        training_job.save()
        
        formatted = training_job.duration_formatted
        assert '30m' in formatted
        assert '45s' in formatted
        assert 'h' not in formatted
    
    def test_duration_formatted_with_seconds_only(self, training_job):
        """Test duration_formatted property with seconds only."""
        training_job.started_at = timezone.now() - timedelta(seconds=45)
        training_job.completed_at = timezone.now()
        training_job.save()
        
        formatted = training_job.duration_formatted
        assert '45s' in formatted
        assert 'm' not in formatted
        assert 'h' not in formatted
    
    def test_duration_formatted_none(self, training_job):
        """Test duration_formatted property with None duration."""
        formatted = training_job.duration_formatted
        assert formatted == "N/A"
    
    def test_is_active_pending(self, training_job):
        """Test is_active property with pending status."""
        training_job.status = 'pending'
        training_job.save()
        
        assert training_job.is_active is True
    
    def test_is_active_running(self, training_job):
        """Test is_active property with running status."""
        training_job.status = 'running'
        training_job.save()
        
        assert training_job.is_active is True
    
    def test_is_active_completed(self, training_job):
        """Test is_active property with completed status."""
        training_job.status = 'completed'
        training_job.save()
        
        assert training_job.is_active is False
    
    def test_is_active_failed(self, training_job):
        """Test is_active property with failed status."""
        training_job.status = 'failed'
        training_job.save()
        
        assert training_job.is_active is False
    
    def test_is_active_cancelled(self, training_job):
        """Test is_active property with cancelled status."""
        training_job.status = 'cancelled'
        training_job.save()
        
        assert training_job.is_active is False
    
    def test_update_progress(self, training_job):
        """Test update_progress method."""
        training_job.update_progress(50.0, "Halfway done")
        
        assert training_job.progress_percentage == 50.0
        assert "Halfway done" in training_job.logs
    
    def test_update_progress_above_100(self, training_job):
        """Test update_progress with value above 100."""
        training_job.update_progress(150.0)
        
        assert training_job.progress_percentage == 100.0
    
    def test_update_progress_below_0(self, training_job):
        """Test update_progress with value below 0."""
        training_job.update_progress(-10.0)
        
        assert training_job.progress_percentage == 0.0
    
    def test_update_progress_without_logs(self, training_job):
        """Test update_progress without logs."""
        initial_logs = training_job.logs
        training_job.update_progress(50.0)
        
        assert training_job.progress_percentage == 50.0
        assert training_job.logs == initial_logs
    
    def test_mark_started(self, training_job):
        """Test mark_started method."""
        training_job.mark_started()
        
        assert training_job.status == 'running'
        assert training_job.started_at is not None
    
    def test_mark_completed(self, training_job):
        """Test mark_completed method."""
        metrics = {'r2_score': 0.95}
        model_path = '/path/to/model.pt'
        
        training_job.mark_completed(metrics=metrics, model_path=model_path)
        
        assert training_job.status == 'completed'
        assert training_job.completed_at is not None
        assert training_job.progress_percentage == 100.0
        assert training_job.metrics == metrics
        assert training_job.model_path == model_path
    
    def test_mark_completed_without_params(self, training_job):
        """Test mark_completed method without parameters."""
        training_job.mark_completed()
        
        assert training_job.status == 'completed'
        assert training_job.completed_at is not None
        assert training_job.progress_percentage == 100.0
    
    def test_mark_failed(self, training_job):
        """Test mark_failed method."""
        error_message = "Training failed"
        
        training_job.mark_failed(error_message)
        
        assert training_job.status == 'failed'
        assert training_job.completed_at is not None
        assert training_job.error_message == error_message
    
    def test_mark_cancelled(self, training_job):
        """Test mark_cancelled method."""
        training_job.mark_cancelled()
        
        assert training_job.status == 'cancelled'
        assert training_job.completed_at is not None


@pytest.mark.django_db
class TestModelMetrics:
    """Tests for ModelMetrics model."""
    
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
    
    def test_get_performance_trend_single(self, user):
        """Test get_performance_trend with single metric."""
        ModelMetrics.objects.create(
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
        
        trend = ModelMetrics.get_performance_trend('test_model', 'alto', 'training')
        
        assert len(trend) == 1
        assert trend[0]['r2_score'] == 0.95
        assert trend[0]['mae'] == 0.5
        assert trend[0]['rmse'] == 0.5
        assert trend[0]['mse'] == 0.25
    
    def test_get_performance_trend_multiple(self, user):
        """Test get_performance_trend with multiple metrics."""
        ModelMetrics.objects.create(
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
        
        ModelMetrics.objects.create(
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
        
        trend = ModelMetrics.get_performance_trend('test_model', 'alto', 'training')
        
        assert len(trend) == 2
        assert trend[0]['r2_score'] == 0.95
        assert trend[1]['r2_score'] == 0.97
    
    def test_get_performance_trend_empty(self):
        """Test get_performance_trend with no metrics."""
        trend = ModelMetrics.get_performance_trend('nonexistent', 'alto', 'training')
        
        assert len(trend) == 0
    
    def test_get_performance_trend_different_target(self, user):
        """Test get_performance_trend with different target."""
        ModelMetrics.objects.create(
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
        
        trend = ModelMetrics.get_performance_trend('test_model', 'ancho', 'training')
        
        assert len(trend) == 0
    
    def test_get_performance_trend_different_metric_type(self, user):
        """Test get_performance_trend with different metric type."""
        ModelMetrics.objects.create(
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
        
        trend = ModelMetrics.get_performance_trend('test_model', 'alto', 'validation')
        
        assert len(trend) == 0
    
    def test_get_performance_trend_ordered_by_created_at(self, user):
        """Test get_performance_trend returns metrics ordered by created_at."""
        first = ModelMetrics.objects.create(
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
        
        # Wait a bit to ensure different timestamps
        import time
        time.sleep(0.1)
        
        second = ModelMetrics.objects.create(
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
        
        trend = ModelMetrics.get_performance_trend('test_model', 'alto', 'training')
        
        assert len(trend) == 2
        # First should be older
        assert trend[0]['r2_score'] == 0.95
        assert trend[1]['r2_score'] == 0.97


