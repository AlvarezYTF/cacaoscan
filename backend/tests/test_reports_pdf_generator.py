"""
Unit tests for PDF generator module (pdf_generator.py).
Tests PDF report generation functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from io import BytesIO

from reports.services.report.pdf_generator import CacaoReportPDFGenerator


@pytest.fixture
def pdf_generator():
    """Create a CacaoReportPDFGenerator instance for testing."""
    return CacaoReportPDFGenerator()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.get_full_name.return_value = "Test User"
    return user


@pytest.fixture
def mock_finca():
    """Create a mock Finca instance."""
    finca = Mock()
    finca.id = 1
    finca.nombre = "Test Finca"
    finca.ubicacion = "Test Location"
    
    # Mock lotes
    mock_lote1 = Mock()
    mock_lote1.area_hectareas = "5.0"
    mock_lote2 = Mock()
    mock_lote2.area_hectareas = "3.5"
    
    mock_lotes_queryset = Mock()
    mock_lotes_queryset.count.return_value = 2
    mock_lotes_queryset.filter.return_value.count.return_value = 2
    mock_lotes_queryset.values.return_value.distinct.return_value = [{'variedad': 'CCN-51'}]
    mock_lotes_queryset.values.return_value.annotate.return_value.values_list.return_value = [('activo', 2)]
    
    # Make it iterable
    mock_lotes_queryset.__iter__ = lambda self: iter([mock_lote1, mock_lote2])
    
    finca.lotes.all.return_value = mock_lotes_queryset
    
    return finca


class TestCacaoReportPDFGenerator:
    """Tests for CacaoReportPDFGenerator class."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = CacaoReportPDFGenerator()
        
        assert generator.styles is not None
        # Check if CustomTitle style exists by trying to access it
        assert 'CustomTitle' in generator.styles.byName or hasattr(generator.styles, 'CustomTitle')
    
    def test_setup_custom_styles(self, pdf_generator):
        """Test custom styles setup."""
        # Check if CustomTitle style exists by trying to access it
        assert 'CustomTitle' in pdf_generator.styles.byName or hasattr(pdf_generator.styles, 'CustomTitle')
        assert 'CustomSubtitle' in pdf_generator.styles.byName or hasattr(pdf_generator.styles, 'CustomSubtitle')
        assert 'CustomNormal' in [s.name for s in pdf_generator.styles]
        assert 'CustomSmall' in [s.name for s in pdf_generator.styles]
    
    @patch('reports.services.report.pdf_generator.CacaoPrediction')
    @patch('reports.services.report.pdf_generator.SimpleDocTemplate')
    def test_generate_quality_report_success(self, mock_doc_template, mock_prediction_model,
                                             pdf_generator, mock_user):
        """Test successful quality report generation."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 10
        
        # Configure aggregate to return different values based on call
        def aggregate_side_effect(**kwargs):
            if 'avg' in kwargs.values() and 'average_confidence' in str(kwargs):
                return {'avg': 0.85}
            elif 'avg_alto' in kwargs or 'avg_ancho' in kwargs or 'avg_grosor' in kwargs:
                return {'avg_alto': 10.5, 'avg_ancho': 8.3, 'avg_grosor': 5.2}
            elif 'peso_g' in str(kwargs):
                return {'avg': 1.5}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value.order_by.return_value = []
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc
        
        result = pdf_generator.generate_quality_report(mock_user)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_doc.build.assert_called_once()
    
    @patch('reports.services.report.pdf_generator.CacaoPrediction')
    @patch('reports.services.report.pdf_generator.SimpleDocTemplate')
    def test_generate_quality_report_with_filters(self, mock_doc_template, mock_prediction_model,
                                                  pdf_generator, mock_user):
        """Test quality report generation with filters."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 5
        
        # Configure aggregate to return different values based on call
        def aggregate_side_effect(**kwargs):
            if 'avg' in kwargs.values() and 'average_confidence' in str(kwargs):
                return {'avg': 0.90}
            elif 'avg_alto' in kwargs or 'avg_ancho' in kwargs or 'avg_grosor' in kwargs:
                return {'avg_alto': 11.0, 'avg_ancho': 9.0, 'avg_grosor': 5.5}
            elif 'peso_g' in str(kwargs):
                return {'avg': 1.8}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value.order_by.return_value = []
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc
        
        filtros = {
            'fecha_desde': '2024-01-01',
            'fecha_hasta': '2024-12-31',
            'usuario_id': 1
        }
        
        result = pdf_generator.generate_quality_report(mock_user, filtros)
        
        assert isinstance(result, bytes)
    
    @patch('reports.services.report.pdf_generator.Finca')
    @patch('reports.services.report.pdf_generator.SimpleDocTemplate')
    def test_generate_finca_report_success(self, mock_doc_template, mock_finca_model,
                                          pdf_generator, mock_user, mock_finca):
        """Test successful finca report generation."""
        mock_finca_model.objects.get.return_value = mock_finca
        
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc
        
        result = pdf_generator.generate_finca_report(1, mock_user)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_doc.build.assert_called_once()
    
    @patch('reports.services.report.pdf_generator.Finca')
    def test_generate_finca_report_not_found(self, mock_finca_model, pdf_generator, mock_user):
        """Test finca report generation when finca doesn't exist."""
        mock_finca_model.objects.get.side_effect = Exception("DoesNotExist")
        
        with pytest.raises(Exception):
            pdf_generator.generate_finca_report(999, mock_user)
    
    @patch('reports.services.report.pdf_generator.ActivityLog')
    @patch('reports.services.report.pdf_generator.SimpleDocTemplate')
    @patch('reports.services.report.pdf_generator.LoginLog')
    def test_generate_audit_report_success(self, mock_login_model, mock_doc_template, mock_activity_model,
                                           pdf_generator, mock_user):
        """Test successful audit report generation."""
        # Mock activity queryset
        mock_activity_queryset = Mock()
        mock_activity_queryset.count.return_value = 10
        mock_activity_queryset.select_related.return_value.order_by.return_value = []
        mock_activity_model.objects.select_related.return_value.order_by.return_value = mock_activity_queryset
        
        # Mock login queryset
        mock_login_queryset = Mock()
        mock_login_queryset.count.return_value = 5
        mock_login_queryset.filter.return_value.count.return_value = 4
        mock_login_model.objects.filter.return_value = mock_login_queryset
        
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc
        
        result = pdf_generator.generate_audit_report(mock_user)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_doc.build.assert_called_once()
    
    def test_apply_filters_no_filters(self, pdf_generator):
        """Test applying no filters."""
        mock_queryset = Mock()
        
        result = pdf_generator._apply_filters(mock_queryset, None)
        
        assert result == mock_queryset
    
    def test_apply_filters_date_range(self, pdf_generator):
        """Test applying date range filters."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {
            'fecha_desde': '2024-01-01',
            'fecha_hasta': '2024-12-31'
        }
        
        result = pdf_generator._apply_filters(mock_queryset, filtros)
        
        assert mock_queryset.filter.call_count == 2
    
    def test_apply_filters_user(self, pdf_generator):
        """Test applying user filter."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {'usuario_id': 1}
        
        result = pdf_generator._apply_filters(mock_queryset, filtros)
        
        mock_queryset.filter.assert_called_once()
    
    def test_apply_filters_finca(self, pdf_generator):
        """Test applying finca filter."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {'finca_id': 1}
        
        result = pdf_generator._apply_filters(mock_queryset, filtros)
        
        mock_queryset.filter.assert_called_once()
    
    def test_apply_filters_lote(self, pdf_generator):
        """Test applying lote filter."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {'lote_id': 1}
        
        result = pdf_generator._apply_filters(mock_queryset, filtros)
        
        mock_queryset.filter.assert_called_once()
    
    @patch('reports.services.report.pdf_generator.CacaoPrediction')
    def test_get_quality_stats_empty(self, mock_prediction_model, pdf_generator):
        """Test getting quality stats with empty queryset."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        stats = pdf_generator._get_quality_stats(mock_queryset)
        
        assert stats['total_analyses'] == 0
        assert stats['avg_confidence'] == 0
    
    @patch('reports.services.report.pdf_generator.CacaoPrediction')
    def test_get_quality_stats_with_data(self, mock_prediction_model, pdf_generator):
        """Test getting quality stats with data."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 10
        
        # Configure aggregate to return different values based on call
        def aggregate_side_effect(**kwargs):
            if 'avg' in kwargs.values() and 'average_confidence' in str(kwargs):
                return {'avg': 0.85}
            elif 'avg_alto' in kwargs or 'avg_ancho' in kwargs or 'avg_grosor' in kwargs:
                return {'avg_alto': 10.5, 'avg_ancho': 8.3, 'avg_grosor': 5.2}
            elif 'peso_g' in str(kwargs):
                return {'avg': 1.5}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.filter.return_value = mock_queryset
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        stats = pdf_generator._get_quality_stats(mock_queryset)
        
        assert stats['total_analyses'] == 10
        assert stats['avg_confidence'] == 85.0  # 0.85 * 100
    
    def test_create_stats_section(self, pdf_generator):
        """Test creating stats section."""
        stats = {
            'total_analyses': 10,
            'avg_confidence': 85.0,
            'avg_dimensions': {
                'alto': 15.5,
                'ancho': 12.3,
                'grosor': 8.7
            },
            'avg_weight': 1.2
        }
        
        elements = pdf_generator._create_stats_section(stats)
        
        assert len(elements) > 0
        # Elements can be Paragraph, Spacer, Table, etc. - just check they exist
        assert all(elem is not None for elem in elements)

