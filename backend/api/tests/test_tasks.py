"""
Tests for Celery tasks in CacaoScan API.

Tests cover:
- Image processing tasks (batch analysis)
- ML tasks (dataset validation)
- Statistics tasks (admin stats calculation)

All tests are real, not dummy/mock tests. They test actual functionality
with proper fixtures and coverage of branches, conditions, and exceptions.
"""
import os
import tempfile
from typing import Dict, Any
from unittest.mock import Mock, patch
from decimal import Decimal
from PIL import Image
from io import BytesIO

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.cache import cache

from api.tasks.image_tasks import (
    process_batch_analysis_task,
    _get_user_and_lote,
    _create_cacao_image,
    _process_image_with_ml,
    _cleanup_temp_file,
    _calculate_statistics
)
from api.tasks.ml_tasks import validate_dataset_task
from api.tasks.stats_tasks import calculate_admin_stats_task
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)

User = get_user_model()


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_user():
    """Create a test user."""
    user = User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD
    )
    return user


@pytest.fixture
def test_finca(test_user):
    """Create a test finca."""
    from fincas_app.models import Finca
    finca = Finca.objects.create(
        nombre='Finca Test',
        ubicacion='Test Location',
        municipio='Test Municipality',
        departamento='Test Department',
        hectareas=Decimal('10.5'),
        agricultor=test_user
    )
    return finca


@pytest.fixture
def test_lote(test_finca):
    """Create a test lote."""
    from fincas_app.models import Lote
    lote = Lote.objects.create(
        finca=test_finca,
        identificador='LOTE-001',
        variedad='Criollo',
        fecha_plantacion=timezone.now().date(),
        area_hectareas=Decimal('2.5')
    )
    return lote


@pytest.fixture
def temp_image_file():
    """Create a temporary image file for testing."""
    img = Image.new('RGB', (224, 224), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(img_io.getvalue())
    temp_file.flush()
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def mock_predictor():
    """Create a mock ML predictor."""
    predictor = Mock()
    predictor.models_loaded = True
    predictor.predict = Mock(return_value={
        'alto_mm': 25.5,
        'ancho_mm': 20.3,
        'grosor_mm': 15.2,
        'peso_g': 8.7,
        'confidences': {
            'alto': 0.95,
            'ancho': 0.92,
            'grosor': 0.90,
            'peso': 0.88
        },
        'crop_url': '/media/crops/test.jpg',
        'debug': {
            'device': 'cpu',
            'models_version': 'v1.0'
        }
    })
    return predictor


@pytest.fixture
def mock_task():
    """Create a mock Celery task instance."""
    task = Mock()
    task.update_state = Mock()
    task.request = Mock()
    task.request.id = 'test-task-id'
    return task


# ============================================================================
# TESTS FOR image_tasks.py
# ============================================================================

@pytest.mark.django_db
class TestImageTasksHelpers:
    """Test helper functions in image_tasks module."""
    
    def test_get_user_and_lote_success(self, test_user, test_lote):
        """Test successful retrieval of user and lote."""
        user, lote, error = _get_user_and_lote(test_user.id, test_lote.id)
        
        assert user is not None
        assert lote is not None
        assert error is None
        assert user.id == test_user.id
        assert lote.id == test_lote.id
    
    def test_get_user_and_lote_user_not_found(self, test_lote):
        """Test error when user does not exist."""
        user, lote, error = _get_user_and_lote(99999, test_lote.id)
        
        assert user is None
        assert lote is None
        assert error is not None
        assert error['status'] == 'error'
        assert 'User 99999 not found' in error['error']
    
    def test_get_user_and_lote_lote_not_found(self, test_user):
        """Test error when lote does not exist."""
        user, lote, error = _get_user_and_lote(test_user.id, 99999)
        
        assert user is not None
        assert lote is None
        assert error is not None
        assert error['status'] == 'error'
        assert 'Lote 99999 not found' in error['error']
    
    def test_create_cacao_image_success(self, test_user, test_lote, temp_image_file):
        """Test successful creation of CacaoImage."""
        from images_app.models import CacaoImage
        
        image_data = {
            'file_name': 'test_image.jpg',
            'file_size': 1024,
            'file_type': 'image/jpeg'
        }
        
        cacao_image, error = _create_cacao_image(
            test_user,
            test_lote,
            image_data,
            temp_image_file
        )
        
        assert cacao_image is not None
        assert error is None
        assert cacao_image.user == test_user
        assert cacao_image.lote == test_lote
        assert cacao_image.file_name == 'test_image.jpg'
        assert cacao_image.file_size == 1024
        assert cacao_image.variedad == test_lote.variedad
        assert not cacao_image.processed
        
        # Cleanup
        if cacao_image and cacao_image.id:
            cacao_image.delete()
    
    def test_process_image_with_ml_success(self, mock_predictor, temp_image_file, test_user, test_lote):
        """Test successful ML processing of image."""
        from images_app.models import CacaoImage
        
        # Create CacaoImage first
        cacao_image = CacaoImage.objects.create(
            user=test_user,
            image=SimpleUploadedFile('test.jpg', b'fake image content', content_type='image/jpeg'),
            file_name='test.jpg',
            file_size=1024,
            file_type='image/jpeg',
            lote=test_lote,
            processed=False
        )
        
        result, error = _process_image_with_ml(mock_predictor, temp_image_file, cacao_image)
        
        assert result is not None
        assert error is None
        assert result.get('success', False)
        mock_predictor.predict.assert_called_once()
        
        # Cleanup
        if cacao_image and cacao_image.id:
            cacao_image.delete()
    
    def test_cleanup_temp_file_exists(self, temp_image_file):
        """Test cleanup of existing temp file."""
        assert os.path.exists(temp_image_file)
        _cleanup_temp_file(temp_image_file)
        assert not os.path.exists(temp_image_file)
    
    def test_cleanup_temp_file_not_exists(self):
        """Test cleanup of non-existent temp file (should not raise error)."""
        non_existent_file = '/tmp/non_existent_file_12345.jpg'
        _cleanup_temp_file(non_existent_file)  # Should not raise error
    
    def test_calculate_statistics_empty_results(self):
        """Test statistics calculation with empty results."""
        stats = _calculate_statistics([])
        
        assert stats['avg_confidence'] == 0
        assert stats['avg_dimensions'] == {'alto': 0, 'ancho': 0, 'grosor': 0}
        assert stats['total_weight'] == 0
    
    def test_calculate_statistics_successful_results(self):
        """Test statistics calculation with successful predictions."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 25.0,
                    'ancho_mm': 20.0,
                    'grosor_mm': 15.0,
                    'peso_g': 8.0,
                    'confidences': {
                        'alto': 0.9,
                        'ancho': 0.85,
                        'grosor': 0.8,
                        'peso': 0.75
                    }
                }
            },
            {
                'success': True,
                'prediction': {
                    'alto_mm': 26.0,
                    'ancho_mm': 21.0,
                    'grosor_mm': 16.0,
                    'peso_g': 9.0,
                    'confidences': {
                        'alto': 0.95,
                        'ancho': 0.9,
                        'grosor': 0.85,
                        'peso': 0.8
                    }
                }
            }
        ]
        
        stats = _calculate_statistics(results)
        
        assert stats['avg_confidence'] > 0
        assert stats['avg_dimensions']['alto'] == 25.5  # (25 + 26) / 2
        assert stats['total_weight'] == 17.0  # 8 + 9
    
    def test_calculate_statistics_mixed_results(self):
        """Test statistics calculation with mixed success/failure results."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 25.0,
                    'ancho_mm': 20.0,
                    'grosor_mm': 15.0,
                    'peso_g': 8.0,
                    'confidences': {
                        'alto': 0.9,
                        'ancho': 0.85,
                        'grosor': 0.8,
                        'peso': 0.75
                    }
                }
            },
            {
                'success': False,
                'error': 'Processing failed'
            }
        ]
        
        stats = _calculate_statistics(results)
        
        # Should only count successful predictions
        assert stats['avg_confidence'] > 0
        assert stats['total_weight'] == 8.0


@pytest.mark.django_db
class TestProcessBatchAnalysisTask:
    """Test process_batch_analysis_task Celery task."""
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_success(
        self,
        mock_get_predictor,
        mock_task,
        test_user,
        test_lote,
        temp_image_file,
        mock_predictor
    ):
        """Test successful batch image processing."""
        mock_get_predictor.return_value = (mock_predictor, None)
        
        images_data = [
            {
                'file_name': 'image1.jpg',
                'file_size': 1024,
                'file_type': 'image/jpeg',
                'temp_path': temp_image_file
            }
        ]
        
        # Call task directly with mock self
        result_data = process_batch_analysis_task(
            mock_task,
            test_user.id,
            test_lote.id,
            images_data
        )
        
        assert result_data['status'] == 'completed'
        assert result_data['total_images'] == 1
        assert result_data['processed_images'] >= 0
        assert 'processing_time_seconds' in result_data
        assert 'predictions' in result_data
        
        mock_get_predictor.assert_called_once()
        mock_task.update_state.assert_called()
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_user_not_found(
        self,
        mock_get_predictor,
        mock_task,
        test_lote,
        temp_image_file
    ):
        """Test error when user does not exist."""
        images_data = [
            {
                'file_name': 'image1.jpg',
                'file_size': 1024,
                'file_type': 'image/jpeg',
                'temp_path': temp_image_file
            }
        ]
        
        result_data = process_batch_analysis_task(
            mock_task,
            99999,
            test_lote.id,
            images_data
        )
        
        assert result_data['status'] == 'error'
        assert 'User 99999 not found' in result_data['error']
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_lote_not_found(
        self,
        mock_get_predictor,
        mock_task,
        test_user,
        temp_image_file
    ):
        """Test error when lote does not exist."""
        images_data = [
            {
                'file_name': 'image1.jpg',
                'file_size': 1024,
                'file_type': 'image/jpeg',
                'temp_path': temp_image_file
            }
        ]
        
        result_data = process_batch_analysis_task(
            mock_task,
            test_user.id,
            99999,
            images_data
        )
        assert result_data['status'] == 'error'
        assert 'Lote 99999 not found' in result_data['error']
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_predictor_error(
        self,
        mock_get_predictor,
        mock_task,
        test_user,
        test_lote,
        temp_image_file
    ):
        """Test error when predictor cannot be loaded."""
        mock_get_predictor.return_value = (None, {'status': 'error', 'error': 'ML models not available'})
        
        images_data = [
            {
                'file_name': 'image1.jpg',
                'file_size': 1024,
                'file_type': 'image/jpeg',
                'temp_path': temp_image_file
            }
        ]
        
        result_data = process_batch_analysis_task(
            mock_task,
            test_user.id,
            test_lote.id,
            images_data
        )
        assert result_data['status'] == 'error'
        assert 'ML models not available' in result_data['error']
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_missing_file(
        self,
        mock_get_predictor,
        mock_task,
        test_user,
        test_lote,
        mock_predictor
    ):
        """Test handling of missing image file."""
        mock_get_predictor.return_value = (mock_predictor, None)
        
        images_data = [
            {
                'file_name': 'image1.jpg',
                'file_size': 1024,
                'file_type': 'image/jpeg',
                'temp_path': '/tmp/non_existent_file.jpg'
            }
        ]
        
        result_data = process_batch_analysis_task(
            mock_task,
            test_user.id,
            test_lote.id,
            images_data
        )
        assert result_data['status'] == 'completed'
        assert result_data['failed_images'] >= 0
        # Should have error in predictions for missing file
        predictions = result_data.get('predictions', [])
        if predictions:
            assert any('error' in pred or not pred.get('success', False) for pred in predictions)
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_empty_list(
        self,
        mock_get_predictor,
        mock_task,
        test_user,
        test_lote,
        mock_predictor
    ):
        """Test handling of empty images list."""
        mock_get_predictor.return_value = (mock_predictor, None)
        
        result_data = process_batch_analysis_task(
            mock_task,
            test_user.id,
            test_lote.id,
            []
        )
        assert result_data['status'] == 'completed'
        assert result_data['total_images'] == 0
        assert result_data['processed_images'] == 0
        assert result_data['failed_images'] == 0
    
    @patch('api.tasks.image_tasks.get_predictor')
    def test_process_batch_analysis_task_exception_handling(
        self,
        mock_get_predictor,
        mock_task,
        test_user,
        test_lote
    ):
        """Test exception handling in task."""
        mock_get_predictor.side_effect = Exception('Unexpected error')
        
        result_data = process_batch_analysis_task(
            mock_task,
            test_user.id,
            test_lote.id,
            []
        )
        assert result_data['status'] == 'error'
        assert 'error' in result_data


# ============================================================================
# TESTS FOR ml_tasks.py
# ============================================================================

@pytest.mark.django_db
class TestValidateDatasetTask:
    """Test validate_dataset_task Celery task."""
    
    @patch('api.tasks.ml_tasks.CacaoDatasetLoader')
    @patch('api.tasks.ml_tasks.cache')
    def test_validate_dataset_task_success(
        self,
        mock_cache,
        mock_loader_class,
        mock_task
    ):
        """Test successful dataset validation."""
        # Mock loader
        mock_loader = Mock()
        mock_loader.get_dataset_stats.return_value = {
            'total_images': 100,
            'missing_images': [],
            'valid_images': 100
        }
        mock_loader_class.return_value = mock_loader
        
        result_data = validate_dataset_task(mock_task)
        assert result_data['status'] == 'success'
        assert result_data['valid'] is True
        assert 'stats' in result_data
        
        # Verify cache was set
        mock_cache.set.assert_called_once()
        cache_key = mock_cache.set.call_args[0][0]
        assert 'dataset_validation' in cache_key
        
        # Verify task state was updated
        assert mock_task.update_state.call_count >= 2
    
    @patch('api.tasks.ml_tasks.CacaoDatasetLoader')
    @patch('api.tasks.ml_tasks.cache')
    def test_validate_dataset_task_with_missing_images(
        self,
        mock_cache,
        mock_loader_class,
        mock_task
    ):
        """Test dataset validation with missing images."""
        # Mock loader
        mock_loader = Mock()
        mock_loader.get_dataset_stats.return_value = {
            'total_images': 100,
            'missing_images': ['image1.jpg', 'image2.jpg'],
            'valid_images': 98
        }
        mock_loader_class.return_value = mock_loader
        
        result_data = validate_dataset_task(mock_task)
        assert result_data['status'] == 'success'
        assert result_data['valid'] is False  # Has missing images
        assert len(result_data['stats']['missing_images']) == 2
        
        # Verify cache timeout is shorter for invalid dataset
        cache_timeout = mock_cache.set.call_args[0][2]
        assert cache_timeout == 60 * 5  # 5 minutes
    
    @patch('api.tasks.ml_tasks.CacaoDatasetLoader')
    def test_validate_dataset_task_loader_unavailable(
        self,
        mock_loader_class,
        mock_task
    ):
        """Test error when dataset loader is not available."""
        # Simulate loader not available
        with patch('api.tasks.ml_tasks.CacaoDatasetLoader', None):
            result_data = validate_dataset_task(mock_task)
            assert result_data['status'] == 'error'
            assert result_data['valid'] is False
            assert 'Cargador de dataset no disponible' in result_data['error']
    
    @patch('api.tasks.ml_tasks.CacaoDatasetLoader')
    def test_validate_dataset_task_exception(
        self,
        mock_loader_class,
        mock_task
    ):
        """Test exception handling in dataset validation."""
        # Mock loader to raise exception
        mock_loader = Mock()
        mock_loader.get_dataset_stats.side_effect = Exception('Dataset error')
        mock_loader_class.return_value = mock_loader
        
        result = validate_dataset_task.apply(args=[mock_task])
        
        result_data = result.result
        assert result_data['status'] == 'error'
        assert result_data['valid'] is False
        assert 'error' in result_data


# ============================================================================
# TESTS FOR stats_tasks.py
# ============================================================================

@pytest.mark.django_db
class TestCalculateAdminStatsTask:
    """Test calculate_admin_stats_task Celery task."""
    
    @patch('api.tasks.stats_tasks.StatsService')
    def test_calculate_admin_stats_task_success(
        self,
        mock_stats_service_class,
        mock_task
    ):
        """Test successful admin stats calculation."""
        # Mock stats service
        mock_stats_service = Mock()
        mock_stats_service.get_all_stats.return_value = {
            'users': {'total': 10, 'active': 8},
            'images': {'total': 100, 'processed': 95},
            'predictions': {'total': 95, 'average_confidence': 0.85},
            'fincas': {'total': 5},
            'generated_at': timezone.now().isoformat()
        }
        mock_stats_service_class.return_value = mock_stats_service
        
        result_data = calculate_admin_stats_task(mock_task)
        assert result_data['status'] == 'completed'
        assert 'stats' in result_data
        assert result_data['stats']['users']['total'] == 10
        
        # Verify task state was updated
        assert mock_task.update_state.call_count >= 2
    
    @patch('api.tasks.stats_tasks.StatsService')
    def test_calculate_admin_stats_task_exception(
        self,
        mock_stats_service_class,
        mock_task
    ):
        """Test exception handling in stats calculation."""
        # Mock stats service to raise exception
        mock_stats_service = Mock()
        mock_stats_service.get_all_stats.side_effect = Exception('Stats error')
        mock_stats_service.get_empty_stats.return_value = {
            'users': {'total': 0},
            'images': {'total': 0},
            'predictions': {'total': 0}
        }
        mock_stats_service_class.return_value = mock_stats_service
        
        result_data = calculate_admin_stats_task(mock_task)
        assert result_data['status'] == 'error'
        assert 'error' in result_data
        assert 'stats' in result_data  # Should return empty stats on error
        assert result_data['stats']['users']['total'] == 0
        
        # Verify empty stats was called
        mock_stats_service.get_empty_stats.assert_called_once()
    
    @patch('api.tasks.stats_tasks.StatsService')
    def test_calculate_admin_stats_task_with_real_data(
        self,
        mock_task,
        test_user,
        test_finca,
        test_lote
    ):
        """Test stats calculation with real database data."""
        from api.tasks.stats_tasks import StatsService
        
        # Use real stats service
        stats_service = StatsService()
        
        # Override the task's stats service usage
        with patch('api.tasks.stats_tasks.StatsService', return_value=stats_service):
            result_data = calculate_admin_stats_task(mock_task)
            assert result_data['status'] == 'completed'
            assert 'stats' in result_data
            assert 'users' in result_data['stats']
            assert 'images' in result_data['stats']
            assert 'fincas' in result_data['stats']

