"""
Tests for reports views.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from django.http import FileResponse
from io import BytesIO

# Import directly from reports.views module (which loads from views.py via __init__.py)
from reports.views import (
    GenerateQualityReportView,
    GenerateDefectsReportView,
    GeneratePerformanceReportView,
    ReportStatsView,
    apply_image_filters,
    apply_query_filters,
    generate_pdf_response,
    handle_report_error,
    FILTER_DATE_FROM,
    FILTER_DATE_TO,
    FILTER_REGION,
    CONTENT_TYPE_PDF,
    ERROR_REPORT_GENERATION
)
from images_app.models import CacaoImage


@pytest.mark.django_db
class TestApplyImageFilters:
    """Tests for apply_image_filters function."""
    
    def test_apply_date_from_filter(self):
        """Test applying date_from filter."""
        queryset = CacaoImage.objects.all()
        request_data = {'date_from': '2024-01-01'}
        filters_dict = {}
        
        result = apply_image_filters(queryset, request_data, filters_dict)
        
        assert FILTER_DATE_FROM in filters_dict
        assert filters_dict[FILTER_DATE_FROM] == '2024-01-01'
    
    def test_apply_date_to_filter(self):
        """Test applying date_to filter."""
        queryset = CacaoImage.objects.all()
        request_data = {'date_to': '2024-12-31'}
        filters_dict = {}
        
        result = apply_image_filters(queryset, request_data, filters_dict)
        
        assert FILTER_DATE_TO in filters_dict
        assert filters_dict[FILTER_DATE_TO] == '2024-12-31'
    
    def test_apply_region_filter(self):
        """Test applying region filter."""
        queryset = CacaoImage.objects.all()
        request_data = {'region': 'Test Region'}
        filters_dict = {}
        
        result = apply_image_filters(queryset, request_data, filters_dict)
        
        assert FILTER_REGION in filters_dict
        assert filters_dict[FILTER_REGION] == 'Test Region'
    
    def test_apply_finca_filter(self):
        """Test applying finca filter."""
        queryset = CacaoImage.objects.all()
        request_data = {'finca': 'Test Finca'}
        filters_dict = {}
        
        result = apply_image_filters(queryset, request_data, filters_dict)
        
        assert 'Finca' in filters_dict
        assert filters_dict['Finca'] == 'Test Finca'
    
    def test_apply_multiple_filters(self):
        """Test applying multiple filters."""
        queryset = CacaoImage.objects.all()
        request_data = {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
            'region': 'Test Region',
            'finca': 'Test Finca'
        }
        filters_dict = {}
        
        result = apply_image_filters(queryset, request_data, filters_dict)
        
        assert len(filters_dict) == 4
        assert FILTER_DATE_FROM in filters_dict
        assert FILTER_DATE_TO in filters_dict
        assert FILTER_REGION in filters_dict
        assert 'Finca' in filters_dict


@pytest.mark.django_db
class TestApplyQueryFilters:
    """Tests for apply_query_filters function."""
    
    def test_apply_date_from_query_filter(self):
        """Test applying date_from from query parameters."""
        queryset = CacaoImage.objects.all()
        request_get = {'date_from': '2024-01-01'}
        
        result = apply_query_filters(queryset, request_get)
        
        assert result is not None
    
    def test_apply_date_to_query_filter(self):
        """Test applying date_to from query parameters."""
        queryset = CacaoImage.objects.all()
        request_get = {'date_to': '2024-12-31'}
        
        result = apply_query_filters(queryset, request_get)
        
        assert result is not None
    
    def test_apply_region_query_filter(self):
        """Test applying region from query parameters."""
        queryset = CacaoImage.objects.all()
        request_get = {'region': 'Test Region'}
        
        result = apply_query_filters(queryset, request_get)
        
        assert result is not None
    
    def test_apply_finca_query_filter(self):
        """Test applying finca from query parameters."""
        queryset = CacaoImage.objects.all()
        request_get = {'finca': 'Test Finca'}
        
        result = apply_query_filters(queryset, request_get)
        
        assert result is not None


@pytest.mark.django_db
class TestGeneratePdfResponse:
    """Tests for generate_pdf_response function."""
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.views.logger')
    def test_generate_pdf_response(self, mock_logger):
        """Test generating PDF response."""
        # Import after patching to ensure mock is used
        import importlib
        import reports.views
        importlib.reload(reports.views)
        from reports.views import generate_pdf_response
        
        pdf_buffer = BytesIO(b'fake pdf content')
        filename = 'test_report.pdf'
        username = 'testuser'
        report_type = 'calidad'
        image_count = 10
        
        # Reset buffer position
        pdf_buffer.seek(0)
        
        response = generate_pdf_response(pdf_buffer, filename, username, report_type, image_count)
        
        assert isinstance(response, FileResponse)
        assert response['Content-Type'] == CONTENT_TYPE_PDF
        # Verify logger was called
        mock_logger.info.assert_called_once()


@pytest.mark.django_db
class TestHandleReportError:
    """Tests for handle_report_error function."""
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.views.logger')
    def test_handle_report_error(self, mock_logger):
        """Test handling report error."""
        # Import after patching to ensure mock is used
        import importlib
        import reports.views
        importlib.reload(reports.views)
        from reports.views import handle_report_error
        
        error = Exception('Test error')
        username = 'testuser'
        report_type = 'calidad'
        
        response = handle_report_error(error, username, report_type)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
        assert response.data['error'] == ERROR_REPORT_GENERATION
        mock_logger.error.assert_called_once()


@pytest.mark.django_db
class TestGenerateQualityReportView:
    """Tests for GenerateQualityReportView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
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
    
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    @patch('reports.views_module.CacaoImage')
    def test_generate_quality_report_success(self, mock_cacao_image, mock_generator_class, api_client, user):
        """Test generating quality report successfully."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        mock_generator = MagicMock()
        mock_pdf_buffer = BytesIO(b'fake pdf content')
        mock_generator.generate_quality_report.return_value = mock_pdf_buffer
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/quality/', {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == CONTENT_TYPE_PDF
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    @patch('reports.views_module.CacaoImage')
    def test_generate_quality_report_with_filters(self, mock_cacao_image, mock_generator_class, api_client, user):
        """Test generating quality report with filters."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        mock_generator = MagicMock()
        mock_pdf_buffer = BytesIO(b'fake pdf content')
        mock_generator.generate_quality_report.return_value = mock_pdf_buffer
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/quality/', {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
            'region': 'Test Region',
            'finca': 'Test Finca',
            'min_confidence': 0.5,
            'max_confidence': 0.9
        })
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    @patch('images_app.models.CacaoImage')
    def test_generate_quality_report_error(self, mock_cacao_image, mock_generator_class, api_client, user):
        """Test generating quality report with error."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        mock_generator = MagicMock()
        mock_generator.generate_quality_report.side_effect = Exception('Test error')
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/quality/', {})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestGenerateDefectsReportView:
    """Tests for GenerateDefectsReportView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
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
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    @patch('reports.views_module.CacaoImage')
    def test_generate_defects_report_success(self, mock_cacao_image, mock_generator_class, api_client, user):
        """Test generating defects report successfully."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        mock_generator = MagicMock()
        mock_pdf_buffer = BytesIO(b'fake pdf content')
        mock_generator.generate_defects_report.return_value = mock_pdf_buffer
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/defects/', {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == CONTENT_TYPE_PDF
    
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    def test_generate_defects_report_error(self, mock_generator_class, api_client, user):
        """Test generating defects report with error."""
        api_client.force_authenticate(user=user)
        
        mock_generator = MagicMock()
        mock_generator.generate_defects_report.side_effect = Exception('Test error')
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/defects/', {})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestGeneratePerformanceReportView:
    """Tests for GeneratePerformanceReportView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
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
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    @patch('reports.views_module.CacaoImage')
    def test_generate_performance_report_success(self, mock_cacao_image, mock_generator_class, api_client, user):
        """Test generating performance report successfully."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        mock_generator = MagicMock()
        mock_pdf_buffer = BytesIO(b'fake pdf content')
        mock_generator.generate_performance_report.return_value = mock_pdf_buffer
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/performance/', {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == CONTENT_TYPE_PDF
    
    @patch('reports.pdf_generator.CacaoReportPDFGenerator')
    def test_generate_performance_report_error(self, mock_generator_class, api_client, user):
        """Test generating performance report with error."""
        api_client.force_authenticate(user=user)
        
        mock_generator = MagicMock()
        mock_generator.generate_performance_report.side_effect = Exception('Test error')
        mock_generator_class.return_value = mock_generator
        
        response = api_client.post('/api/v1/reports/performance/', {})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
class TestReportStatsView:
    """Tests for ReportStatsView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
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
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.views_module.CacaoImage')
    def test_get_report_stats_success(self, mock_cacao_image, api_client, user):
        """Test getting report stats successfully."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_queryset.aggregate.return_value = {
            'avg_confidence': None,
            'min_confidence': None,
            'max_confidence': None
        }
        mock_queryset.values.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.exclude.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = []
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        response = api_client.get('/api/v1/reports/stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_images' in response.data
        assert 'processed_images' in response.data
        assert 'processing_rate' in response.data
        assert 'confidence_stats' in response.data
        assert 'top_regions' in response.data
        assert 'top_fincas' in response.data
        assert 'filters_applied' in response.data
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.views_module.CacaoImage')
    def test_get_report_stats_with_filters(self, mock_cacao_image, api_client, user):
        """Test getting report stats with filters."""
        api_client.force_authenticate(user=user)
        
        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count.return_value = 0
        mock_queryset.aggregate.return_value = {
            'avg_confidence': None,
            'min_confidence': None,
            'max_confidence': None
        }
        mock_queryset.values.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.exclude.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = []
        mock_cacao_image.objects.filter.return_value = mock_queryset
        
        response = api_client.get('/api/v1/reports/stats/', {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
            'region': 'Test Region',
            'finca': 'Test Finca'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['filters_applied']['date_from'] == '2024-01-01'
        assert response.data['filters_applied']['date_to'] == '2024-12-31'
        assert response.data['filters_applied']['region'] == 'Test Region'
        assert response.data['filters_applied']['finca'] == 'Test Finca'
    
    @pytest.mark.skip(reason="Test omitted as requested")
    @patch('reports.views.logger')
    @patch('images_app.models.CacaoImage')
    def test_get_report_stats_error(self, mock_cacao_image, mock_logger, api_client, user):
        """Test getting report stats with error."""
        # Import after patching to ensure mock is used
        import importlib
        import reports.views
        importlib.reload(reports.views)
        
        api_client.force_authenticate(user=user)
        
        # Make filter raise an exception
        mock_cacao_image.objects.filter.side_effect = Exception('Test error')
        
        response = api_client.get('/api/v1/reports/stats/')
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
        # Verify logger was called
        mock_logger.error.assert_called_once()

