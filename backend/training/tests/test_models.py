"""
Tests for Training Models.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from training.models import TrainingJob


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='trainer',
        email='trainer@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestTrainingJob:
    """Tests for TrainingJob model."""

    def test_create_training_job(self, user):
        """Test creating a training job."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='HybridCacaoRegression',
            dataset_size=1000,
            epochs=100,
            batch_size=16,
            learning_rate=0.001
        )
        
        assert job.job_id == 'job_123'
        assert job.job_type == 'regression'
        assert job.status == 'pending'
        assert job.created_by == user
        assert job.model_name == 'HybridCacaoRegression'

    def test_training_job_str_representation(self, user):
        """Test string representation."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        assert 'job_123' in str(job)
        assert 'regression' in str(job) or 'Regresión' in str(job)

    def test_duration_property_completed(self, user):
        """Test duration property when job is completed."""
        started = timezone.now() - timedelta(hours=2)
        completed = timezone.now() - timedelta(hours=1)
        
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='completed',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000,
            started_at=started,
            completed_at=completed
        )
        
        assert job.duration == 3600.0  # 1 hour in seconds

    def test_duration_property_running(self, user):
        """Test duration property when job is running."""
        started = timezone.now() - timedelta(hours=1)
        
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='running',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000,
            started_at=started
        )
        
        # Should calculate from started_at to now
        assert job.duration is not None
        assert job.duration >= 3600.0  # At least 1 hour

    def test_duration_property_not_started(self, user):
        """Test duration property when job hasn't started."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        assert job.duration is None

    def test_duration_formatted_completed(self, user):
        """Test duration_formatted property when completed."""
        started = timezone.now() - timedelta(hours=2, minutes=30, seconds=45)
        completed = timezone.now() - timedelta(hours=1, minutes=15, seconds=20)
        
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='completed',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000,
            started_at=started,
            completed_at=completed
        )
        
        formatted = job.duration_formatted
        assert 'h' in formatted or 'm' in formatted or 's' in formatted

    def test_duration_formatted_not_started(self, user):
        """Test duration_formatted property when not started."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        assert job.duration_formatted == "N/A"

    def test_is_active_pending(self, user):
        """Test is_active property when pending."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        assert job.is_active is True

    def test_is_active_running(self, user):
        """Test is_active property when running."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='running',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        assert job.is_active is True

    def test_is_active_completed(self, user):
        """Test is_active property when completed."""
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='completed',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        assert job.is_active is False

    def test_job_type_choices(self, user):
        """Test job_type choices."""
        valid_types = ['regression', 'vision', 'incremental']
        
        for job_type in valid_types:
            job = TrainingJob.objects.create(
                job_id=f'job_{job_type}',
                job_type=job_type,
                status='pending',
                created_by=user,
                model_name='TestModel',
                dataset_size=1000
            )
            assert job.job_type == job_type

    def test_status_choices(self, user):
        """Test status choices."""
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        
        for status in valid_statuses:
            job = TrainingJob.objects.create(
                job_id=f'job_{status}',
                job_type='regression',
                status=status,
                created_by=user,
                model_name='TestModel',
                dataset_size=1000
            )
            assert job.status == status

    def test_unique_job_id(self, user):
        """Test that job_id must be unique."""
        TrainingJob.objects.create(
            job_id='unique_job',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000
        )
        
        with pytest.raises(Exception):  # IntegrityError
            TrainingJob.objects.create(
                job_id='unique_job',  # Duplicate
                job_type='regression',
                status='pending',
                created_by=user,
                model_name='TestModel',
                dataset_size=1000
            )

    def test_config_params_json_field(self, user):
        """Test config_params JSON field."""
        config = {'param1': 'value1', 'param2': 123}
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='pending',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000,
            config_params=config
        )
        
        assert job.config_params == config

    def test_metrics_json_field(self, user):
        """Test metrics JSON field."""
        metrics = {'accuracy': 0.95, 'loss': 0.05}
        job = TrainingJob.objects.create(
            job_id='job_123',
            job_type='regression',
            status='completed',
            created_by=user,
            model_name='TestModel',
            dataset_size=1000,
            metrics=metrics
        )
        
        assert job.metrics == metrics

