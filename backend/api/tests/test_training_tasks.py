"""
Tests for training tasks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone
from api.utils.model_imports import get_model_safely

# Mock TrainingJob model
TrainingJob = get_model_safely('training.models.TrainingJob')


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


@pytest.fixture
def mock_training_job():
    """Create mock training job."""
    return MockTrainingJob('test-job-id')


class TestTrainModelTask:
    """Tests for train_model_task."""
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('api.tasks.training_tasks.TrainingJob')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_train_model_task_success(
        self, mock_get_datasets_dir, mock_run_pipeline, mock_job_model, tmp_path
    ):
        """Test successful model training task."""
        from api.tasks.training_tasks import train_model_task
        
        # Setup mocks
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        mock_job = MockTrainingJob('test-job-id')
        mock_job_model.objects.get.return_value = mock_job
        mock_job_model.DoesNotExist = Exception
        
        mock_run_pipeline.return_value = True
        
        # Mock the task instance (self parameter for @shared_task with bind=True)
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(train_model_task)
        job_id_param = 'test-job-id'
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
    
    @patch('api.tasks.training_tasks.TrainingJob')
    def test_train_model_task_job_not_found(self, mock_job_model):
        """Test training task when job is not found."""
        from api.tasks.training_tasks import train_model_task
        
        class MockDoesNotExist(Exception):
            pass
        mock_job_model.DoesNotExist = MockDoesNotExist
        mock_job_model.objects.get.side_effect = MockDoesNotExist()
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(train_model_task)
        result = original_func(mock_task, 'non-existent-job', {})
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    @patch('api.tasks.training_tasks.TrainingJob')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_train_model_task_dataset_not_found(
        self, mock_get_datasets_dir, mock_run_pipeline, mock_job_model, tmp_path
    ):
        """Test training task when dataset is not found."""
        from api.tasks.training_tasks import train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        mock_job = MockTrainingJob('test-job-id')
        mock_job_model.objects.get.return_value = mock_job
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(train_model_task)
        result = original_func(mock_task, 'test-job-id', {})
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    @patch('api.tasks.training_tasks.TrainingJob')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_train_model_task_training_failed(
        self, mock_get_datasets_dir, mock_run_pipeline, mock_job_model, tmp_path
    ):
        """Test training task when training fails."""
        from api.tasks.training_tasks import train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        mock_job = MockTrainingJob('test-job-id')
        mock_job_model.objects.get.return_value = mock_job
        
        mock_run_pipeline.return_value = False
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(train_model_task)
        result = original_func(mock_task, 'test-job-id', {})
        
        assert result['status'] == 'failed'
    
    @patch('api.tasks.training_tasks.TrainingJob')
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_train_model_task_exception(
        self, mock_get_datasets_dir, mock_run_pipeline, mock_job_model, tmp_path
    ):
        """Test training task when exception occurs."""
        from api.tasks.training_tasks import train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        mock_job = MockTrainingJob('test-job-id')
        mock_job_model.objects.get.return_value = mock_job
        
        mock_run_pipeline.side_effect = Exception("Training error")
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(train_model_task)
        result = original_func(mock_task, 'test-job-id', {})
        
        assert result['status'] == 'failed'
        assert 'error' in result
    
    @patch('api.tasks.training_tasks.TrainingJob')
    def test_train_model_task_training_job_not_available(self, mock_job_model):
        """Test training task when TrainingJob model is not available."""
        from api.tasks.training_tasks import train_model_task
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(train_model_task)
        
        with patch('api.tasks.training_tasks.TrainingJob', None):
            result = original_func(mock_task, 'test-job-id', {})
            
            assert result['status'] == 'failed'
            assert 'error' in result


class TestAutoTrainModelTask:
    """Tests for auto_train_model_task."""
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_raw_images_dir')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_auto_train_model_task_success(
        self, mock_get_datasets_dir, mock_get_raw_images_dir, mock_run_pipeline, tmp_path
    ):
        """Test successful automatic training task."""
        from api.tasks.training_tasks import auto_train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        raw_images_dir = tmp_path / "media" / "cacao_images" / "raw"
        raw_images_dir.mkdir(parents=True)
        bmp_file = raw_images_dir / "1.bmp"
        bmp_file.write_bytes(b"fake image")
        
        # Mock get_raw_images_dir to return the test directory
        mock_get_raw_images_dir.return_value = raw_images_dir
        
        # Mock rglob on the Path object
        mock_path = MagicMock()
        mock_path.rglob.return_value = [bmp_file]
        mock_path.exists.return_value = True
        mock_get_raw_images_dir.return_value = mock_path
        
        mock_run_pipeline.return_value = True
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'completed'
    
    @patch('ml.utils.paths.get_datasets_dir')
    def test_auto_train_model_task_dataset_not_found(
        self, mock_get_datasets_dir, tmp_path
    ):
        """Test automatic training when dataset is not found."""
        from api.tasks.training_tasks import auto_train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'skipped'
        assert 'message' in result
    
    @patch('ml.utils.paths.get_datasets_dir')
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_auto_train_model_task_no_images(
        self, mock_exists, mock_rglob, mock_get_datasets_dir, tmp_path
    ):
        """Test automatic training when no images are found."""
        from api.tasks.training_tasks import auto_train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        # Mock Path.exists and rglob
        mock_exists.return_value = True
        mock_rglob.return_value = []
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'skipped'
        assert 'message' in result
    
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_auto_train_model_task_training_failed(
        self, mock_exists, mock_rglob, mock_get_datasets_dir, mock_run_pipeline, tmp_path
    ):
        """Test automatic training when training fails."""
        from api.tasks.training_tasks import auto_train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        raw_images_dir = tmp_path / "media" / "cacao_images" / "raw"
        raw_images_dir.mkdir(parents=True)
        (raw_images_dir / "1.bmp").write_bytes(b"fake image")
        
        # Mock Path.exists and rglob
        mock_exists.return_value = True
        mock_rglob.return_value = [raw_images_dir / "1.bmp"]
        
        mock_run_pipeline.return_value = False
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'failed'
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_raw_images_dir')
    @patch('ml.utils.paths.get_datasets_dir')
    def test_auto_train_model_task_with_custom_config(
        self, mock_get_datasets_dir, mock_get_raw_images_dir, mock_run_pipeline, tmp_path
    ):
        """Test automatic training with custom configuration."""
        from api.tasks.training_tasks import auto_train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        raw_images_dir = tmp_path / "media" / "cacao_images" / "raw"
        raw_images_dir.mkdir(parents=True)
        bmp_file = raw_images_dir / "1.bmp"
        bmp_file.write_bytes(b"fake image")
        
        # Mock get_raw_images_dir to return a mock Path with rglob
        mock_path = MagicMock()
        mock_path.rglob.return_value = [bmp_file]
        mock_path.exists.return_value = True
        mock_get_raw_images_dir.return_value = mock_path
        
        mock_run_pipeline.return_value = True
        
        config = {
            'epochs': 200,
            'batch_size': 32,
            'learning_rate': 0.0001
        }
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False, config)
        
        assert result['status'] == 'completed'
        mock_run_pipeline.assert_called_once()
        call_args = mock_run_pipeline.call_args[1]
        assert call_args['epochs'] == 200
        assert call_args['batch_size'] == 32
    
    @patch('ml.pipeline.train_all.run_training_pipeline')
    @patch('ml.utils.paths.get_datasets_dir')
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_auto_train_model_task_exception(
        self, mock_exists, mock_rglob, mock_get_datasets_dir, mock_run_pipeline, tmp_path
    ):
        """Test automatic training when exception occurs."""
        from api.tasks.training_tasks import auto_train_model_task
        
        mock_get_datasets_dir.return_value = tmp_path
        csv_path = tmp_path / "dataset_cacao.clean.csv"
        csv_path.write_text("id,alto,ancho\n1,10,20")
        
        raw_images_dir = tmp_path / "media" / "cacao_images" / "raw"
        raw_images_dir.mkdir(parents=True)
        (raw_images_dir / "1.bmp").write_bytes(b"fake image")
        
        # Mock Path.exists and rglob
        mock_exists.return_value = True
        mock_rglob.return_value = [raw_images_dir / "1.bmp"]
        
        mock_run_pipeline.side_effect = Exception("Training error")
        
        # Mock the task instance
        mock_task = Mock()
        
        # Unwrap and call the function directly
        original_func = unwrap_celery_task(auto_train_model_task)
        result = original_func(mock_task, False)
        
        assert result['status'] == 'failed'
        assert 'error' in result
