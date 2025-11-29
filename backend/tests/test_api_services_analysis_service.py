"""
Unit tests for analysis service module (analysis_service.py).
Tests analysis orchestration and workflow functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from PIL import Image
import io

from api.services.analysis_service import AnalysisService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_staff = False
    user.is_superuser = False
    return user


@pytest.fixture
def mock_image_file():
    """Create a mock image file for testing."""
    img = Image.new('RGB', (512, 512), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=img_bytes.getvalue(),
        content_type="image/jpeg"
    )


@pytest.fixture
def analysis_service():
    """Create an AnalysisService instance for testing."""
    with patch('api.services.analysis_service.ImageProcessingService') as mock_processing, \
         patch('api.services.analysis_service.ImageStorageService') as mock_storage, \
         patch('api.services.analysis_service.PredictionService') as mock_prediction:
        service = AnalysisService()
        # Configurar los servicios mockeados
        service.processing_service = Mock()
        service.storage_service = Mock()
        service.prediction_service = Mock()
        return service


class TestAnalysisService:
    """Tests for AnalysisService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        with patch('api.services.analysis_service.ImageProcessingService'), \
             patch('api.services.analysis_service.ImageStorageService'), \
             patch('api.services.analysis_service.PredictionService'):
            service = AnalysisService()
            
            assert service.processing_service is not None
            assert service.storage_service is not None
            assert service.prediction_service is not None
    
    def test_process_image_with_segmentation_success(self, analysis_service, mock_user, mock_image_file):
        """Test successful image processing with segmentation."""
        # Mock all service responses
        analysis_service.processing_service.validate_image_file_complete.return_value = ServiceResult.success()
        analysis_service.storage_service.save_uploaded_image_with_segmentation.return_value = ServiceResult.success(
            data={
                'cacao_image': Mock(id=1),
                'processed_png_path': '/tmp/processed.png'
            }
        )
        analysis_service.processing_service.load_image.return_value = ServiceResult.success(
            data=Image.new('RGB', (512, 512))
        )
        analysis_service.prediction_service.predict.return_value = ServiceResult.success(
            data={
                'alto_mm': 25.0,
                'ancho_mm': 15.0,
                'grosor_mm': 8.0,
                'peso_g': 1.5,
                'confidences': {'alto': 0.9, 'ancho': 0.9, 'grosor': 0.9, 'peso': 0.9},
                'crop_url': '/media/crop.png',
                'debug': {},
                'processing_time_ms': 100
            }
        )
        analysis_service.storage_service.save_prediction.return_value = ServiceResult.success(
            data=Mock(id=1)
        )
        
        result = analysis_service.process_image_with_segmentation(mock_image_file, mock_user)
        
        assert result.success is True
        assert 'alto_mm' in result.data
        assert 'ancho_mm' in result.data
        assert 'grosor_mm' in result.data
        assert 'peso_g' in result.data
    
    def test_process_image_validation_failure(self, analysis_service, mock_user, mock_image_file):
        """Test processing when image validation fails."""
        analysis_service.processing_service.validate_image_file_complete.return_value = ServiceResult.validation_error(
            "Invalid image file"
        )
        
        result = analysis_service.process_image_with_segmentation(mock_image_file, mock_user)
        
        assert result.success is False
        assert result.error is not None
    
    def test_process_image_storage_failure(self, analysis_service, mock_user, mock_image_file):
        """Test processing when image storage fails."""
        analysis_service.processing_service.validate_image_file_complete.return_value = ServiceResult.success()
        analysis_service.storage_service.save_uploaded_image_with_segmentation.return_value = ServiceResult.error(
            ValidationServiceError("Storage failed")
        )
        
        result = analysis_service.process_image_with_segmentation(mock_image_file, mock_user)
        
        assert result.success is False
    
    def test_process_image_prediction_failure(self, analysis_service, mock_user, mock_image_file):
        """Test processing when prediction fails."""
        analysis_service.processing_service.validate_image_file_complete.return_value = ServiceResult.success()
        analysis_service.storage_service.save_uploaded_image_with_segmentation.return_value = ServiceResult.success(
            data={'cacao_image': Mock(id=1), 'processed_png_path': '/tmp/processed.png'}
        )
        analysis_service.processing_service.load_image.return_value = ServiceResult.success(
            data=Image.new('RGB', (512, 512))
        )
        analysis_service.prediction_service.predict.return_value = ServiceResult.error(
            ValidationServiceError("Prediction failed")
        )
        
        result = analysis_service.process_image_with_segmentation(mock_image_file, mock_user)
        
        assert result.success is False
    
    def test_get_analysis_history_success(self, analysis_service, mock_user):
        """Test getting analysis history."""
        mock_predictions = [
            Mock(
                id=1,
                image=Mock(id=1, image=Mock(url='/media/image1.jpg')),
                alto_mm=25.0,
                ancho_mm=15.0,
                grosor_mm=8.0,
                peso_g=1.5,
                average_confidence=0.9,
                processing_time_ms=100,
                created_at=Mock(isoformat=lambda: '2024-01-01T00:00:00'),
                crop_url='/media/crop1.png'
            )
        ]
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value.select_related.return_value.order_by.return_value = mock_predictions
        
        mock_model = Mock()
        mock_model.objects = Mock()
        mock_model.objects.filter.return_value.select_related.return_value.order_by.return_value = mock_predictions
        mock_model.DoesNotExist = Exception
        
        with patch('api.utils.model_imports.get_models_safely') as mock_get_models:
            mock_get_models.return_value = {'CacaoPrediction': mock_model}
            with patch.object(analysis_service, 'paginate_results', return_value={
                'results': mock_predictions,
                'pagination': {'page': 1, 'total': 1, 'pages': 1, 'per_page': 20, 'has_next': False, 'has_previous': False}
            }):
                result = analysis_service.get_analysis_history(mock_user, page=1, page_size=20)
                
                assert result.success is True
                assert 'analyses' in result.data
                assert 'pagination' in result.data
    
    def test_get_analysis_details_success(self, analysis_service, mock_user):
        """Test getting analysis details."""
        mock_prediction = Mock(
            id=1,
            image=Mock(
                id=1,
                file_name='test.jpg',
                file_size=1024,
                file_type='image/jpeg',
                image=Mock(url='/media/image1.jpg'),
                processed=True
            ),
            alto_mm=25.0,
            ancho_mm=15.0,
            grosor_mm=8.0,
            peso_g=1.5,
            average_confidence=0.9,
            processing_time_ms=100,
            created_at=Mock(isoformat=lambda: '2024-01-01T00:00:00'),
            updated_at=Mock(isoformat=lambda: '2024-01-01T00:00:00'),
            crop_url='/media/crop1.png',
            debug_info={}
        )
        
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_model = Mock()
            mock_model.objects.select_related.return_value.get.return_value = mock_prediction
            mock_model.DoesNotExist = Exception
            mock_models.return_value = {'CacaoPrediction': mock_model}
            
            result = analysis_service.get_analysis_details(1, mock_user)
            
            assert result.success is True
            assert 'id' in result.data
            assert 'alto_mm' in result.data
            assert 'image' in result.data
    
    def test_get_analysis_details_not_found(self, analysis_service, mock_user):
        """Test getting analysis details when not found."""
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            # Create a proper DoesNotExist exception
            class DoesNotExist(Exception):
                pass
            
            mock_model = Mock()
            mock_model.DoesNotExist = DoesNotExist
            mock_model.objects.select_related.return_value.get.side_effect = DoesNotExist()
            mock_models.return_value = {'CacaoPrediction': mock_model}
            
            result = analysis_service.get_analysis_details(999, mock_user)
            
            assert result.success is False
    
    def test_delete_analysis_success(self, analysis_service, mock_user):
        """Test deleting an analysis."""
        mock_prediction = Mock(
            id=1,
            image=Mock(id=1)
        )
        
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_model = Mock()
            mock_model.objects.select_related.return_value.get.return_value = mock_prediction
            mock_model.DoesNotExist = Exception
            mock_models.return_value = {'CacaoPrediction': mock_model}
            
            result = analysis_service.delete_analysis(1, mock_user)
            
            assert result.success is True
            mock_prediction.delete.assert_called_once()
    
    def test_get_analysis_statistics_success(self, analysis_service, mock_user):
        """Test getting analysis statistics."""
        with patch('api.utils.model_imports.get_models_safely') as mock_models:
            mock_model = Mock()
            mock_queryset = Mock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.count.return_value = 10
            mock_queryset.aggregate.return_value = {'avg': 0.9}
            mock_queryset.filter.return_value.filter.return_value.count.return_value = 5
            mock_model.objects.filter.return_value = mock_queryset
            mock_models.return_value = {'CacaoPrediction': mock_model}
            
            with patch.object(analysis_service, '_calculate_average_dimensions', return_value={
                'alto_mm': 25.0,
                'ancho_mm': 15.0,
                'grosor_mm': 8.0,
                'peso_g': 1.5
            }), \
            patch.object(analysis_service, '_calculate_confidence_distribution', return_value={
                'high': 5,
                'medium': 3,
                'low': 2
            }), \
            patch.object(analysis_service, '_calculate_dimension_ranges', return_value={
                'alto_mm': {'min': 20.0, 'max': 30.0}
            }):
                result = analysis_service.get_analysis_statistics(mock_user)
                
                assert result.success is True
                assert 'total_analyses' in result.data
                assert 'average_dimensions' in result.data
    
    def test_initialize_ml_system_success(self, analysis_service):
        """Test ML system initialization."""
        with patch.object(analysis_service, '_validate_dataset_step', return_value=None), \
             patch.object(analysis_service, '_generate_crops_step'), \
             patch.object(analysis_service, '_train_models_step', return_value=None), \
             patch.object(analysis_service, '_load_models_step', return_value=None):
            result = analysis_service.initialize_ml_system()
            
            assert result.success is True
            assert 'steps_completed' in result.data
            assert result.data['ready_for_predictions'] is True
    
    def test_initialize_ml_system_dataset_validation_failure(self, analysis_service):
        """Test ML system initialization when dataset validation fails."""
        error_result = ServiceResult.error(ValidationServiceError("Dataset invalid"))
        
        with patch.object(analysis_service, '_validate_dataset_step', return_value=error_result):
            result = analysis_service.initialize_ml_system()
            
            assert result.success is False

