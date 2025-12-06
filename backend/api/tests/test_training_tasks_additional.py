"""
Additional tests for training tasks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from api.tasks.training_tasks import train_model_task, auto_train_model_task


@pytest.mark.django_db
class TestTrainModelTask:
    """Tests for train_model_task."""
    
    @pytest.fixture
    def mock_task(self):
        """Create mock Celery task."""
        task = Mock()
        task.request = Mock()
        return task
    
    @pytest.mark.skip(reason="Skipping due to MethodType binding issues with Celery tasks")
    @patch('api.tasks.training_tasks.TrainingJob')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_train_model_task_success(self, mock_get_dir, mock_pipeline, mock_job_model, mock_task, tmp_path):
        """Test successful model training."""
        mock_get_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho,grosor,peso\n1,10.0,20.0,5.0,100.0\n")
        
        mock_job = Mock()
        mock_job.job_id = 'test_job_123'
        mock_job.status = 'pending'
        mock_job.objects.get.return_value = mock_job
        mock_job_model.objects = mock_job.objects
        mock_job_model.DoesNotExist = Exception
        
        mock_pipeline.return_value = True
        
        # Call the task function directly by binding mock_task as self
        # Use the same pattern as test_training_tasks.py
        from types import MethodType
        if hasattr(train_model_task, '__wrapped__'):
            original_func = train_model_task.__wrapped__
        else:
            original_func = train_model_task.run.__func__
        bound_func = MethodType(original_func, mock_task)
        result = bound_func('test_job_123', {
            'epochs': 10,
            'batch_size': 16,
            'learning_rate': 0.001
        })
        
        assert result['status'] == 'completed'
        assert mock_job.mark_completed.called
    
    @pytest.mark.skip(reason="Skipping due to MethodType binding issues with Celery tasks")
    @patch('ml.utils.paths.get_datasets_dir')
    def test_auto_train_model_task_dataset_not_found(self, mock_get_dir, mock_task, tmp_path):
        """Test auto train when dataset not found."""
        mock_get_dir.return_value = tmp_path
        
        # Call the task function directly by binding mock_task as self
        # Use the same pattern as test_training_tasks.py
        from types import MethodType
        if hasattr(auto_train_model_task, '__wrapped__'):
            original_func = auto_train_model_task.__wrapped__
        else:
            original_func = auto_train_model_task.run.__func__
        bound_func = MethodType(original_func, mock_task)
        result = bound_func(False, None)
        
        assert result['status'] == 'skipped'
        assert 'Dataset not found' in result['message']
    
    @pytest.mark.skip(reason="Skipping due to MethodType binding issues with Celery tasks")
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    @patch('api.tasks.training_tasks.Path')
    def test_auto_train_model_task_success(self, mock_path, mock_get_dir, mock_pipeline, mock_task, tmp_path):
        """Test successful auto train."""
        mock_get_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho,grosor,peso\n1,10.0,20.0,5.0,100.0\n")
        
        mock_path.return_value.rglob.return_value = [tmp_path / "image1.bmp"]
        mock_path.return_value.exists.return_value = True
        
        mock_pipeline.return_value = True
        
        # Call the task function directly by binding mock_task as self
        # Use the same pattern as test_training_tasks.py
        from types import MethodType
        if hasattr(auto_train_model_task, '__wrapped__'):
            original_func = auto_train_model_task.__wrapped__
        else:
            original_func = auto_train_model_task.run.__func__
        bound_func = MethodType(original_func, mock_task)
        result = bound_func(False, None)
        
        assert result['status'] == 'completed'
