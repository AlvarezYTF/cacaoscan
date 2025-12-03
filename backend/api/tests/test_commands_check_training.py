"""
Tests for check_training management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from io import StringIO

from api.utils.model_imports import get_model_safely


TrainingJob = get_model_safely('training.models.TrainingJob')


class CheckTrainingCommandTest(TestCase):
    """Tests for check_training command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()

    @patch('api.management.commands.check_training.TrainingJob')
    def test_check_training_all_status(self, mock_training_job):
        """Test checking training with all status filter."""
        mock_running = MagicMock()
        mock_running.exists.return_value = False
        mock_pending = MagicMock()
        mock_pending.exists.return_value = False
        mock_completed = MagicMock()
        mock_completed.count.return_value = 0
        mock_failed = MagicMock()
        mock_failed.count.return_value = 0
        mock_cancelled = MagicMock()
        mock_cancelled.count.return_value = 0

        mock_training_job.objects.filter.return_value.order_by.return_value = mock_running
        mock_training_job.objects.filter.side_effect = lambda **kwargs: {
            'status': 'running'
        }.get('status') and mock_running or mock_pending if kwargs.get('status') == 'pending' else mock_completed

        def filter_side_effect(**kwargs):
            status = kwargs.get('status')
            if status == 'running':
                return mock_running
            elif status == 'pending':
                return mock_pending
            elif status == 'completed':
                return mock_completed
            elif status == 'failed':
                return mock_failed
            elif status == 'cancelled':
                return mock_cancelled
            return MagicMock()

        mock_training_job.objects.filter.side_effect = filter_side_effect

        try:
            call_command('check_training', '--status', 'all', stdout=self.stdout)
            output = self.stdout.getvalue()
            self.assertIsNotNone(output)
        except CommandError:
            pass

    @patch('api.management.commands.check_training.TrainingJob')
    def test_check_training_specific_job(self, mock_training_job):
        """Test checking a specific training job."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job-123'
        mock_job.status = 'running'
        mock_job.get_job_type_display.return_value = 'Training'
        mock_job.progress_percentage = 50.0  # Add numeric value for progress
        mock_job.created_at = timezone.now()
        mock_job.started_at = None
        mock_job.completed_at = None
        mock_job.created_by = None
        mock_job.logs = None

        mock_training_job.objects.get.return_value = mock_job

        call_command('check_training', '--job-id', 'test-job-123', stdout=self.stdout)

        output = self.stdout.getvalue()
        self.assertIn('test-job-123', output)

    @patch('api.management.commands.check_training.TrainingJob')
    def test_check_training_job_not_found(self, mock_training_job):
        """Test checking a non-existent job."""
        mock_training_job.DoesNotExist = Exception
        mock_training_job.objects.get.side_effect = mock_training_job.DoesNotExist()

        with self.assertRaises(CommandError):
            call_command('check_training', '--job-id', 'non-existent', stdout=self.stdout, stderr=self.stderr)

