"""
Tests for API Celery Tasks.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.contrib.auth.models import User

from api.tasks.image_tasks import process_batch_analysis_task
from api.tasks.ml_tasks import validate_dataset_task
from api.tasks.stats_tasks import calculate_admin_stats_task
from fincas_app.models import Finca, Lote
from images_app.models import CacaoImage


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def finca(user):
    """Create a test finca."""
    return Finca.objects.create(
        nombre='Test Finca',
        ubicacion='Test Location',
        municipio='Test',
        departamento='Test',
        hectareas=10.0,
        agricultor=user
    )


@pytest.fixture
def lote(finca):
    """Create a test lote."""
    return Lote.objects.create(
        finca=finca,
        identificador='L1',
        nombre='Lote 1',
        variedad='Criollo',
        area_hectareas=5.0
    )


@pytest.mark.django_db
class TestImageTasks:
    """Tests for image processing tasks."""

    def test_process_batch_analysis_task_success(self, user, lote, tmp_path):
        """Test processing batch analysis successfully."""
        # Create temporary image file
        image_file = tmp_path / "test_image.jpg"
        image_file.write_bytes(b'fake image data')
        
        images_data = [{
            'file_name': 'test_image.jpg',
            'file_size': 1024,
            'file_type': 'image/jpeg',
            'temp_path': str(image_file)
        }]
        
        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = {
            'alto_mm': 20.5,
            'ancho_mm': 15.3,
            'grosor_mm': 10.2,
            'peso_g': 1.5,
            'confidences': {
                'alto': 0.9,
                'ancho': 0.85,
                'grosor': 0.88,
                'peso': 0.92
            }
        }
        
        mock_task = MagicMock()
        mock_task.update_state = MagicMock()
        
        with patch('api.tasks.image_tasks.get_predictor', return_value=(mock_predictor, None)):
            with patch('api.tasks.image_tasks.process_image_prediction') as mock_process:
                mock_process.return_value = ({
                    'success': True,
                    'prediction': {
                        'alto_mm': 20.5,
                        'ancho_mm': 15.3,
                        'grosor_mm': 10.2,
                        'peso_g': 1.5
                    }
                }, None)
                
                result = process_batch_analysis_task(
                    mock_task,
                    user.id,
                    lote.id,
                    images_data
                )
        
        assert result['status'] == 'success'
        assert 'results' in result

    def test_process_batch_analysis_task_user_not_found(self, lote, tmp_path):
        """Test processing batch analysis when user not found."""
        images_data = [{
            'file_name': 'test.jpg',
            'temp_path': str(tmp_path / 'test.jpg')
        }]
        
        mock_task = MagicMock()
        
        result = process_batch_analysis_task(
            mock_task,
            99999,  # Non-existent user
            lote.id,
            images_data
        )
        
        assert result['status'] == 'error'
        assert 'not found' in result['error'].lower()

    def test_process_batch_analysis_task_lote_not_found(self, user, tmp_path):
        """Test processing batch analysis when lote not found."""
        images_data = [{
            'file_name': 'test.jpg',
            'temp_path': str(tmp_path / 'test.jpg')
        }]
        
        mock_task = MagicMock()
        
        result = process_batch_analysis_task(
            mock_task,
            user.id,
            99999,  # Non-existent lote
            images_data
        )
        
        assert result['status'] == 'error'
        assert 'not found' in result['error'].lower()

    def test_process_batch_analysis_task_predictor_error(self, user, lote, tmp_path):
        """Test processing batch analysis when predictor fails."""
        images_data = [{
            'file_name': 'test.jpg',
            'temp_path': str(tmp_path / 'test.jpg')
        }]
        
        mock_task = MagicMock()
        
        with patch('api.tasks.image_tasks.get_predictor', return_value=(None, {'error': 'Predictor not available'})):
            result = process_batch_analysis_task(
                mock_task,
                user.id,
                lote.id,
                images_data
            )
        
        assert result['status'] == 'error' or 'error' in result


@pytest.mark.django_db
class TestMLTasks:
    """Tests for ML tasks."""

    def test_validate_dataset_task_success(self):
        """Test validating dataset successfully."""
        mock_task = MagicMock()
        mock_task.update_state = MagicMock()
        
        mock_loader = MagicMock()
        mock_loader.get_dataset_stats.return_value = {
            'total_records': 100,
            'valid_records': 95,
            'missing_images': []
        }
        
        with patch('api.tasks.ml_tasks.CacaoDatasetLoader', return_value=mock_loader):
            with patch('api.tasks.ml_tasks.cache') as mock_cache:
                result = validate_dataset_task(mock_task)
        
        assert result['status'] == 'success'
        assert result['valid'] is True
        assert 'stats' in result

    def test_validate_dataset_task_loader_not_available(self):
        """Test validating dataset when loader not available."""
        mock_task = MagicMock()
        
        with patch('api.tasks.ml_tasks.CacaoDatasetLoader', None):
            result = validate_dataset_task(mock_task)
        
        assert result['status'] == 'error'
        assert result['valid'] is False

    def test_validate_dataset_task_exception(self):
        """Test validating dataset when exception occurs."""
        mock_task = MagicMock()
        mock_task.update_state = MagicMock()
        
        mock_loader = MagicMock()
        mock_loader.get_dataset_stats.side_effect = Exception("Test error")
        
        with patch('api.tasks.ml_tasks.CacaoDatasetLoader', return_value=mock_loader):
            result = validate_dataset_task(mock_task)
        
        assert result['status'] == 'error'
        assert result['valid'] is False
        assert 'error' in result


@pytest.mark.django_db
class TestStatsTasks:
    """Tests for statistics tasks."""

    def test_calculate_admin_stats_task_success(self):
        """Test calculating admin stats successfully."""
        mock_task = MagicMock()
        mock_task.update_state = MagicMock()
        
        mock_stats_service = MagicMock()
        mock_stats_service.get_all_stats.return_value = {
            'users': {'total': 10},
            'images': {'total': 100}
        }
        
        with patch('api.tasks.stats_tasks.StatsService', return_value=mock_stats_service):
            result = calculate_admin_stats_task(mock_task)
        
        assert result['status'] == 'completed'
        assert 'stats' in result

    def test_calculate_admin_stats_task_exception(self):
        """Test calculating admin stats when exception occurs."""
        mock_task = MagicMock()
        mock_task.update_state = MagicMock()
        
        mock_stats_service = MagicMock()
        mock_stats_service.get_all_stats.side_effect = Exception("Test error")
        mock_stats_service.get_empty_stats.return_value = {}
        
        with patch('api.tasks.stats_tasks.StatsService', return_value=mock_stats_service):
            result = calculate_admin_stats_task(mock_task)
        
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'stats' in result

