"""
Tests for check_training management command.
"""
import pytest
from io import StringIO
from unittest.mock import Mock, patch
from django.core.management.base import CommandError
from django.utils import timezone

from api.management.commands.check_training import Command


@pytest.mark.django_db
class TestCheckTrainingCommand:
    """Tests for check_training command."""
    
    def test_handle_training_job_not_available(self):
        """Test when TrainingJob model is not available."""
        with patch('api.management.commands.check_training.TrainingJob', None):
            command = Command()
            
            with pytest.raises(CommandError, match="no está disponible"):
                command.handle()
    
    def test_handle_single_job_not_found(self):
        """Test checking non-existent job."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            mock_training_job.DoesNotExist = Exception
            mock_training_job.objects.get.side_effect = Exception("Not found")
            
            command = Command()
            
            # The command should handle the exception and raise CommandError
            # job_id comes from --job-id option, status has default 'all'
            with pytest.raises(CommandError, match="no encontrado"):
                command.handle(job_id='nonexistent')
    
    def test_handle_single_job_found(self):
        """Test checking existing job."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            mock_job = Mock()
            mock_job.job_id = 'test-job'
            mock_job.status = 'running'
            mock_job.job_type = 'training'
            mock_job.created_at = timezone.now()
            mock_job.progress_percentage = 50.0
            mock_job.started_at = None
            mock_job.completed_at = None
            mock_job.created_by = None
            mock_job.logs = None
            mock_job.get_job_type_display = Mock(return_value='Training')
            
            mock_training_job.objects.get.return_value = mock_job
            
            command = Command()
            out = StringIO()
            command.stdout = out
            
            command.handle(job_id='test-job')
            
            output = out.getvalue()
            assert 'test-job' in output
            # Check that status is displayed (in Spanish as "Estado")
            assert 'Estado' in output or 'status' in output.lower() or 'running' in output.lower()
    
    def test_handle_all_jobs(self):
        """Test checking all jobs."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            # Mock different querysets for different status filters
            def mock_filter(**kwargs):
                mock_qs = Mock()
                mock_qs.exists.return_value = False
                mock_qs.count.return_value = 0
                mock_qs.order_by.return_value = mock_qs
                return mock_qs
            
            mock_training_job.objects.filter.side_effect = mock_filter
            
            command = Command()
            out = StringIO()
            command.stdout = out
            
            command.handle()
            
            output = out.getvalue()
            assert len(output) > 0
            # Verify that status filter is used
            assert mock_training_job.objects.filter.called
    
    def test_is_does_not_exist_exception_true(self):
        """Test detecting DoesNotExist exception."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            class MockDoesNotExist(Exception):
                pass
            
            mock_training_job.DoesNotExist = MockDoesNotExist
            
            command = Command()
            
            exception = MockDoesNotExist()
            result = command._is_does_not_exist_exception(exception)
            
            assert result is True
    
    def test_is_does_not_exist_exception_false(self):
        """Test detecting non-DoesNotExist exception."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            # Set DoesNotExist to a different exception type
            class MockDoesNotExist(Exception):
                pass
            mock_training_job.DoesNotExist = MockDoesNotExist
            
            command = Command()
            
            exception = ValueError("Other error")
            result = command._is_does_not_exist_exception(exception)
            
            assert result is False
    
    def test_display_running_jobs(self):
        """Test displaying running jobs."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            mock_job = Mock()
            mock_job.job_id = 'test-job'
            mock_job.job_type = 'training'
            mock_job.created_at = timezone.now()
            mock_job.progress_percentage = 50.0
            
            mock_queryset = Mock()
            mock_queryset.exists.return_value = True
            mock_queryset.count.return_value = 1
            mock_queryset.__iter__ = Mock(return_value=iter([mock_job]))
            mock_queryset.order_by.return_value = mock_queryset
            mock_training_job.objects.filter.return_value = mock_queryset
            
            command = Command()
            out = StringIO()
            command.stdout = out
            
            command._display_running_jobs('running')
            
            output = out.getvalue()
            assert len(output) > 0
    
    def test_display_pending_jobs(self):
        """Test displaying pending jobs."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            mock_job = Mock()
            mock_job.job_id = 'test-job'
            mock_job.job_type = 'training'
            mock_job.created_at = timezone.now()
            
            mock_queryset = Mock()
            mock_queryset.exists.return_value = True
            mock_queryset.count.return_value = 1
            mock_queryset.__iter__ = Mock(return_value=iter([mock_job]))
            mock_queryset.order_by.return_value = mock_queryset
            mock_training_job.objects.filter.return_value = mock_queryset
            
            command = Command()
            out = StringIO()
            command.stdout = out
            
            command._display_pending_jobs('pending')
            
            output = out.getvalue()
            assert len(output) > 0
    
    def test_display_summary(self):
        """Test displaying summary."""
        with patch('api.management.commands.check_training.TrainingJob') as mock_training_job:
            mock_queryset = Mock()
            mock_queryset.count.return_value = 0
            mock_training_job.objects.filter.return_value = mock_queryset
            
            command = Command()
            out = StringIO()
            command.stdout = out
            
            command._display_summary('all')
            
            output = out.getvalue()
            assert 'RESUMEN' in output or 'resumen' in output.lower()
    
    def test_display_job_summary(self):
        """Test displaying job summary."""
        mock_job = Mock()
        mock_job.job_id = 'test-job'
        mock_job.job_type = 'training'
        mock_job.created_at = timezone.now()
        mock_job.progress_percentage = 50.0
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        command._display_job_summary(mock_job, show_cancel=True)
        
        output = out.getvalue()
        assert 'test-job' in output
    
    def test_display_job_details(self):
        """Test displaying job details."""
        mock_job = Mock()
        mock_job.job_id = 'test-job'
        mock_job.status = 'running'
        mock_job.job_type = 'training'
        mock_job.created_at = timezone.now()
        mock_job.progress_percentage = 50.0
        mock_job.started_at = None
        mock_job.completed_at = None
        mock_job.created_by = None
        mock_job.logs = None
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        command._display_job_details(mock_job)
        
        output = out.getvalue()
        assert 'test-job' in output
        assert 'running' in output.lower()


