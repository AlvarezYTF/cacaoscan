"""
Tests for analysis service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from api.services import AnalysisService
from api.services.base import ServiceResult


@pytest.mark.django_db
class TestAnalysisService:
    """Tests for AnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return AnalysisService()
    
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
    def image_file(self):
        """Create test image file."""
        return SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
    
    def test_process_image_with_segmentation_success(
        self, service, user, image_file
    ):
        """Test successful image processing with segmentation."""
        # Setup mocks directly on service instance (services are created in __init__)
        mock_processing_instance = Mock()
        mock_processing_instance.validate_image_file_complete.return_value = ServiceResult.success()
        mock_processing_instance.load_image.return_value = ServiceResult.success(data=Mock())
        service.processing_service = mock_processing_instance
        
        mock_storage_instance = Mock()
        mock_image = Mock()
        mock_image.id = 1
        mock_storage_instance.save_uploaded_image_with_segmentation.return_value = ServiceResult.success(
            data={'cacao_image': mock_image, 'processed_png_path': '/path/to/image.png'}
        )
        mock_storage_instance.save_prediction.return_value = ServiceResult.success(
            data=Mock(id=1)
        )
        service.storage_service = mock_storage_instance
        
        mock_prediction_instance = Mock()
        mock_prediction_instance.predict.return_value = ServiceResult.success(
            data={
                'alto_mm': 10.0,
                'ancho_mm': 20.0,
                'grosor_mm': 5.0,
                'peso_g': 100.0,
                'confidences': {'alto': 0.9, 'ancho': 0.8},
                'crop_url': '/crop/url',
                'debug': {},
                'processing_time_ms': 100
            }
        )
        service.prediction_service = mock_prediction_instance
        
        result = service.process_image_with_segmentation(image_file, user)
        
        assert result.success
        assert result.data['alto_mm'] == 10.0
        assert result.data['image_id'] == 1
    
    def test_process_image_validation_failure(self, service, user, image_file):
        """Test image processing with validation failure."""
        mock_processing_instance = Mock()
        mock_processing_instance.validate_image_file_complete.return_value = ServiceResult.validation_error(
            "Invalid image"
        )
        service.processing_service = mock_processing_instance
        
        result = service.process_image_with_segmentation(image_file, user)
        
        assert not result.success
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_analysis_history(self, mock_get_models, service, user):
        """Test getting analysis history."""
        mock_prediction = Mock()
        mock_prediction.objects.filter.return_value.select_related.return_value.order_by.return_value = []
        mock_get_models.return_value = {'CacaoPrediction': mock_prediction}
        
        result = service.get_analysis_history(user, page=1, page_size=20)
        
        assert result.success
        assert 'analyses' in result.data
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_analysis_history_with_filters(self, mock_get_models, service, user):
        """Test getting analysis history with filters."""
        mock_prediction = Mock()
        queryset = Mock()
        # Configure queryset chain: filter().select_related().order_by()
        queryset.filter.return_value = queryset
        queryset.select_related.return_value = queryset
        queryset.order_by.return_value = queryset
        mock_prediction.objects.filter.return_value = queryset
        
        # Mock paginate_results to return expected structure
        with patch.object(service, 'paginate_results') as mock_paginate:
            mock_paginate.return_value = {
                'results': [],
                'pagination': {
                    'page': 1,
                    'page_size': 20,
                    'total': 0,
                    'total_pages': 0
                }
            }
            mock_get_models.return_value = {'CacaoPrediction': mock_prediction}
            
            filters = {'date_from': '2024-01-01', 'min_confidence': 0.5}
            result = service.get_analysis_history(user, page=1, page_size=20, filters=filters)
            
            assert result.success
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_analysis_details(self, mock_get_models, service, user):
        """Test getting analysis details."""
        mock_prediction = Mock()
        mock_prediction_instance = Mock()
        mock_prediction_instance.id = 1
        mock_prediction_instance.alto_mm = 10.0
        mock_prediction_instance.image = Mock(id=1, file_name='test.jpg')
        mock_prediction.objects.select_related.return_value.get.return_value = mock_prediction_instance
        mock_get_models.return_value = {'CacaoPrediction': mock_prediction}
        
        result = service.get_analysis_details(1, user)
        
        assert result.success
        assert result.data['id'] == 1
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_analysis_details_not_found(self, mock_get_models, service, user):
        """Test getting analysis details when not found."""
        mock_prediction = Mock()
        mock_prediction.DoesNotExist = Exception
        mock_prediction.objects.select_related.return_value.get.side_effect = mock_prediction.DoesNotExist()
        mock_get_models.return_value = {'CacaoPrediction': mock_prediction}
        
        result = service.get_analysis_details(999, user)
        
        assert not result.success
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_delete_analysis(self, mock_get_models, service, user):
        """Test deleting analysis."""
        mock_prediction = Mock()
        mock_prediction_instance = Mock()
        mock_prediction_instance.id = 1
        mock_prediction_instance.image = Mock(id=1)
        mock_prediction.objects.select_related.return_value.get.return_value = mock_prediction_instance
        mock_get_models.return_value = {'CacaoPrediction': mock_prediction}
        
        result = service.delete_analysis(1, user)
        
        assert result.success
        mock_prediction_instance.delete.assert_called_once()
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_analysis_statistics(self, mock_get_models, service, user):
        """Test getting analysis statistics."""
        mock_prediction = Mock()
        queryset = Mock()
        
        # Configure queryset chain
        mock_prediction.objects.filter.return_value = queryset
        queryset.filter.return_value = queryset  # For date filters
        queryset.exclude.return_value = queryset
        queryset.exclude.return_value.values_list.return_value = []
        
        # Configure count and aggregate
        queryset.count = Mock(return_value=10)
        queryset.aggregate = Mock(return_value={'avg': 0.8})
        
        mock_get_models.return_value = {'CacaoPrediction': mock_prediction}
        
        # Mock helper methods
        with patch.object(service, '_apply_date_filters', return_value=queryset):
            with patch.object(service, '_calculate_average_dimensions', return_value={'alto_mm': 10.0, 'ancho_mm': 20.0}):
                with patch.object(service, '_calculate_confidence_distribution', return_value={'high': 5, 'medium': 3, 'low': 2}):
                    with patch.object(service, '_calculate_dimension_ranges', return_value={}):
                        result = service.get_analysis_statistics(user)
                        
                        assert result.success
                        assert 'total_analyses' in result.data
    
    def test_apply_date_filters(self, service):
        """Test applying date filters."""
        queryset = Mock()
        filters = {'date_from': '2024-01-01', 'date_to': '2024-12-31'}
        
        result = service._apply_date_filters(queryset, filters)
        
        assert queryset.filter.called
    
    def test_calculate_average_dimensions(self, service):
        """Test calculating average dimensions."""
        queryset = Mock()
        queryset.aggregate.return_value = {'avg': 10.0}
        
        result = service._calculate_average_dimensions(queryset)
        
        assert 'alto_mm' in result
        assert 'ancho_mm' in result
    
    def test_calculate_confidence_distribution(self, service):
        """Test calculating confidence distribution."""
        queryset = Mock()
        queryset.filter.return_value.count.return_value = 5
        
        result = service._calculate_confidence_distribution(queryset)
        
        assert 'high' in result
        assert 'medium' in result
        assert 'low' in result
    
    @patch('ml.data.dataset_loader.CacaoDatasetLoader')
    def test_validate_dataset_step(self, mock_loader, service):
        """Test validating dataset step."""
        mock_loader_instance = Mock()
        mock_loader_instance.get_dataset_stats.return_value = {'valid_records': 100}
        mock_loader.return_value = mock_loader_instance
        
        steps_completed = []
        result = service._validate_dataset_step(steps_completed)
        
        assert result is None
        assert len(steps_completed) > 0
    
    @patch('ml.utils.paths.get_crops_dir')
    def test_generate_crops_step(self, mock_get_crops, service, tmp_path):
        """Test generating crops step."""
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        mock_get_crops.return_value = crops_dir
        
        steps_completed = []
        service._generate_crops_step(steps_completed)
        
        assert len(steps_completed) > 0

