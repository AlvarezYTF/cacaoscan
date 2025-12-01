"""
Tests for cancel_training management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from io import StringIO

from api.utils.model_imports import get_model_safely


TrainingJob = get_model_safely('training.models.TrainingJob')


class CancelTrainingCommandTest(TestCase):
    """Tests for cancel_training command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()

    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_list_running_jobs_no_jobs(self, mock_training_job):
        """Test listing running jobs when there are none."""
        mock_training_job.objects.filter.return_value.exists.return_value = False
        mock_training_job.objects.filter.return_value.order_by.return_value = mock_training_job.objects.filter.return_value

        call_command('cancel_training', stdout=self.stdout)

        output = self.stdout.getvalue()
        self.assertIn('No hay trabajos en ejecución o pendientes', output)

    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_job_success(self, mock_training_job):
        """Test successfully canceling a training job."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job-123'
        mock_job.status = 'running'
        mock_job.completed_at = None
        mock_job.get_job_type_display.return_value = 'Training'
        mock_job.created_at = timezone.now()

        mock_training_job.objects.select_for_update.return_value.get.return_value = mock_job

        call_command('cancel_training', 'test-job-123', stdout=self.stdout)

        self.assertEqual(mock_job.status, 'cancelled')
        self.assertTrue(mock_job.save.called)

    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_job_not_found(self, mock_training_job):
        """Test canceling a non-existent job."""
        mock_training_job.DoesNotExist = Exception
        mock_training_job.objects.select_for_update.return_value.get.side_effect = mock_training_job.DoesNotExist()

        with self.assertRaises(CommandError):
            call_command('cancel_training', 'non-existent', stdout=self.stdout, stderr=self.stderr)

    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_job_wrong_status(self, mock_training_job):
        """Test canceling a job with wrong status without force."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job-123'
        mock_job.status = 'completed'

        mock_training_job.objects.select_for_update.return_value.get.return_value = mock_job

        with self.assertRaises(CommandError):
            call_command('cancel_training', 'test-job-123', stdout=self.stdout, stderr=self.stderr)

    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_job_with_force(self, mock_training_job):
        """Test canceling a job with force flag."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job-123'
        mock_job.status = 'completed'
        mock_job.completed_at = None

        mock_training_job.objects.select_for_update.return_value.get.return_value = mock_job

        call_command('cancel_training', 'test-job-123', '--force', stdout=self.stdout)

        self.assertEqual(mock_job.status, 'cancelled')
        self.assertTrue(mock_job.save.called)

