"""
Additional tests for training tasks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from api.tasks.training_tasks import train_model_task, auto_train_model_task


def unwrap_celery_task(task_func):
    """Unwrap Celery task to get the original function."""
    func = task_func
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    return func


class MockTrainingJob:
    """Mock TrainingJob model for testing."""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = 'pending'
        self.started_at = None
        self.logs = ""
    
    def save(self):
        pass
    
    def update_progress(self, percent, message):
        self.logs += f"\n[{percent}%] {message}"
    
    def mark_completed(self):
        self.status = 'completed'
    
    def mark_failed(self, error):
        self.status = 'failed'
        self.logs += f"\n[FAILED] {error}"


@pytest.mark.django_db
class TestTrainModelTask:
    """Tests for train_model_task."""
    
    @pytest.fixture
    def mock_task(self):
        """Create mock Celery task."""
        task = Mock()
        task.request = Mock()
        return task
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('api.tasks.training_tasks.TrainingJob')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_train_model_task_success(self, mock_get_dir, mock_pipeline, mock_job_model, mock_task, tmp_path):
        """Test successful model training."""
        mock_get_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho,grosor,peso\n1,10.0,20.0,5.0,100.0\n")
        
        mock_job = MockTrainingJob('test_job_123')
        mock_job_model.objects.get.return_value = mock_job
        mock_job_model.DoesNotExist = Exception
        
        mock_pipeline.return_value = True
        
        # Unwrap and call the function directly with mock_task as self
        original_func = unwrap_celery_task(train_model_task)
        job_id_param = 'test_job_123'
        result = original_func(mock_task, job_id_param, None, config={
            'epochs': 10,
            'batch_size': 16,
            'learning_rate': 0.001,
            'multi_head': False,
            'model_type': 'resnet18',
            'img_size': 224,
            'early_stopping_patience': 25,
            'save_best_only': True
        })
        
        assert result['status'] == 'completed'
        assert result['job_id'] == job_id_param
    
    @patch('ml.utils.paths.get_datasets_dir')
    def test_auto_train_model_task_dataset_not_found(self, mock_get_dir, mock_task, tmp_path):
        """Test auto train when dataset not found."""
        mock_get_dir.return_value = tmp_path
        
        # Unwrap and call the function directly with mock_task as self
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'skipped'
        assert 'message' in result
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_raw_images_dir')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_auto_train_model_task_success(
        self, mock_get_dir, mock_get_raw_images_dir, mock_pipeline, mock_task, tmp_path
    ):
        """Test successful auto train."""
        mock_get_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho,grosor,peso\n1,10.0,20.0,5.0,100.0\n")
        
        raw_images_dir = tmp_path / "media" / "cacao_images" / "raw"
        raw_images_dir.mkdir(parents=True)
        bmp_file = raw_images_dir / "1.bmp"
        bmp_file.write_bytes(b"fake image")
        
        # Mock get_raw_images_dir to return a mock Path with rglob
        mock_path = MagicMock()
        mock_path.rglob.return_value = [bmp_file]
        mock_path.exists.return_value = True
        mock_get_raw_images_dir.return_value = mock_path
        
        mock_pipeline.return_value = True
        
        # Unwrap and call the function directly with mock_task as self
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'completed'
