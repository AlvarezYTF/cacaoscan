"""
Tests for ImagesExportView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.contrib.auth.models import User

from images_app.views.image.export.export_views import ImagesExportView


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def user(db):
    """Create test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


class TestImagesExportView:
    """Tests for ImagesExportView class."""
    
    def test_validate_export_format_csv(self, request_factory, user):
        """Test _validate_export_format with CSV format."""
        view = ImagesExportView()
        response = view._validate_export_format('csv')
        assert response is None
    
    def test_validate_export_format_invalid(self, request_factory, user):
        """Test _validate_export_format with invalid format."""
        view = ImagesExportView()
        response = view._validate_export_format('json')
        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_apply_export_filters(self, request_factory, user):
        """Test _apply_export_filters method."""
        view = ImagesExportView()
        queryset = Mock()
        queryset.filter = Mock(return_value=queryset)
        
        result = view._apply_export_filters(
            queryset,
            date_from='2024-01-01',
            date_to='2024-12-31',
            region='Test Region',
            finca='Test Finca',
            processed_only=True
        )
        assert result is not None
    
    def test_apply_export_filters_no_filters(self, request_factory, user):
        """Test _apply_export_filters with no filters."""
        view = ImagesExportView()
        queryset = Mock()
        
        result = view._apply_export_filters(
            queryset,
            date_from=None,
            date_to=None,
            region=None,
            finca=None,
            processed_only=False
        )
        assert result == queryset
    
    def test_build_csv_headers_images_only(self, request_factory, user):
        """Test _build_csv_headers with images only."""
        view = ImagesExportView()
        headers = view._build_csv_headers(include_images=True, include_predictions=False)
        assert len(headers) > 0
        assert 'image_id' in headers
    
    def test_build_csv_headers_predictions_only(self, request_factory, user):
        """Test _build_csv_headers with predictions only."""
        view = ImagesExportView()
        headers = view._build_csv_headers(include_images=False, include_predictions=True)
        assert len(headers) > 0
        assert 'prediction_id' in headers
    
    def test_build_csv_headers_both(self, request_factory, user):
        """Test _build_csv_headers with both images and predictions."""
        view = ImagesExportView()
        headers = view._build_csv_headers(include_images=True, include_predictions=True)
        assert len(headers) > 0
        assert 'image_id' in headers
        assert 'prediction_id' in headers
    
    def test_build_image_row(self, request_factory, user):
        """Test _build_image_row method."""
        view = ImagesExportView()
        image = Mock()
        image.id = 1
        image.file_name = 'test.jpg'
        image.file_size_mb = 1.5
        image.finca = 'Test Finca'
        image.region = 'Test Region'
        image.lote_id = 1
        image.variedad = 'Test Variedad'
        image.fecha_cosecha = None
        image.notas = 'Test Notes'
        image.processed = True
        image.created_at = Mock()
        image.created_at.isoformat = Mock(return_value='2024-01-01')
        image.user = Mock()
        image.user.username = 'testuser'
        
        row = view._build_image_row(image)
        assert len(row) > 0
        assert row[0] == 1
    
    def test_build_prediction_row(self, request_factory, user):
        """Test _build_prediction_row method."""
        view = ImagesExportView()
        prediction = Mock()
        prediction.id = 1
        prediction.alto_mm = 20.5
        prediction.ancho_mm = 15.3
        prediction.grosor_mm = 10.2
        prediction.peso_g = 1.5
        prediction.confidence_alto = 0.95
        prediction.confidence_ancho = 0.92
        prediction.confidence_grosor = 0.88
        prediction.confidence_peso = 0.90
        prediction.average_confidence = 0.91
        prediction.volume_cm3 = 3.14
        prediction.density_g_cm3 = 0.48
        prediction.processing_time_ms = 150
        prediction.model_version = 'v1.0'
        prediction.device_used = 'CPU'
        prediction.created_at = Mock()
        prediction.created_at.isoformat = Mock(return_value='2024-01-01')
        
        row = view._build_prediction_row(prediction)
        assert len(row) > 0
        assert row[0] == 1
    
    def test_write_csv_data(self, request_factory, user):
        """Test _write_csv_data method."""
        view = ImagesExportView()
        writer = Mock()
        queryset = Mock()
        image = Mock()
        image.prediction = None
        queryset.select_related.return_value = [image]
        
        view._write_csv_data(writer, queryset, include_images=True, include_predictions=True)
        assert writer.writerow.called
    
    def test_create_csv_response(self, request_factory, user):
        """Test _create_csv_response method."""
        view = ImagesExportView()
        output = Mock()
        output.getvalue.return_value = b'test,data\n1,2\n'
        queryset = Mock()
        queryset.count.return_value = 1
        
        response = view._create_csv_response(output, queryset)
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']
    
    def test_post_export_csv(self, request_factory, user):
        """Test POST export CSV."""
        view_instance = ImagesExportView()
        view = ImagesExportView.as_view()
        data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True
        }
        request = request_factory.post('/api/images/export/', data, format='json')
        force_authenticate(request, user=user)
        
        with patch.object(ImagesExportView, 'get_user_images_queryset') as mock_queryset_method:
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.select_related.return_value = []
            mock_query.count.return_value = 0
            mock_queryset_method.return_value = mock_query
            
            response = view(request)
            assert response.status_code == status.HTTP_200_OK
    
    def test_post_export_csv_invalid_format(self, request_factory, user):
        """Test POST export with invalid format."""
        view = ImagesExportView.as_view()
        data = {'format': 'json'}
        request = request_factory.post('/api/images/export/', data, format='json')
        force_authenticate(request, user=user)
        
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_post_export_csv_with_filters(self, request_factory, user):
        """Test POST export CSV with filters."""
        view = ImagesExportView.as_view()
        data = {
            'format': 'csv',
            'include_images': True,
            'include_predictions': True,
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
            'region': 'Test Region',
            'finca': 'Test Finca',
            'processed_only': True
        }
        request = request_factory.post('/api/images/export/', data, format='json')
        force_authenticate(request, user=user)
        
        with patch.object(ImagesExportView, 'get_user_images_queryset') as mock_queryset_method:
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.select_related.return_value = []
            mock_query.count.return_value = 0
            mock_queryset_method.return_value = mock_query
            
            response = view(request)
            assert response.status_code == status.HTTP_200_OK
    
    def test_post_export_csv_error(self, request_factory, user):
        """Test POST export CSV with error."""
        view = ImagesExportView.as_view()
        data = {'format': 'csv'}
        request = request_factory.post('/api/images/export/', data, format='json')
        force_authenticate(request, user=user)
        
        with patch.object(ImagesExportView, 'get_user_images_queryset', side_effect=Exception("Error")):
            response = view(request)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


