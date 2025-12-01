"""
Unit tests for Excel analysis generator module (excel_analisis.py).
Tests Excel report generation functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User

from reports.services.report.excel.excel_analisis import ExcelAnalisisGenerator


@pytest.fixture
def excel_generator():
    """Create an ExcelAnalisisGenerator instance for testing."""
    return ExcelAnalisisGenerator()


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


class TestExcelAnalisisGenerator:
    """Tests for ExcelAnalisisGenerator class."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = ExcelAnalisisGenerator()
        assert generator is not None
    
    @patch('reports.services.report.excel.excel_analisis.CacaoPrediction')
    @patch.object(ExcelAnalisisGenerator, '_create_workbook')
    @patch.object(ExcelAnalisisGenerator, '_create_header')
    @patch.object(ExcelAnalisisGenerator, '_create_stats_section')
    @patch.object(ExcelAnalisisGenerator, '_create_detailed_analyses_table')
    @patch.object(ExcelAnalisisGenerator, '_create_quality_chart')
    @patch.object(ExcelAnalisisGenerator, '_create_summary_sheet')
    @patch.object(ExcelAnalisisGenerator, '_save_to_buffer')
    def test_generate_quality_report_success(self, mock_save, mock_summary, mock_chart,
                                             mock_table, mock_stats, mock_header, mock_workbook,
                                             mock_prediction_model, excel_generator, mock_user):
        """Test successful quality report generation."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 10
        
        # Configure aggregate to return different values based on call
        call_count = [0]
        def aggregate_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'avg': 0.85}
            elif call_count[0] == 2:
                return {'avg_alto': 10.5, 'avg_ancho': 8.3, 'avg_grosor': 5.2}
            elif call_count[0] == 3:
                return {'avg': 1.5}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.filter.return_value = mock_queryset
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        mock_save.return_value = b"excel_content"
        
        result = excel_generator.generate_quality_report(mock_user)
        
        assert isinstance(result, bytes)
        assert result == b"excel_content"
        mock_workbook.assert_called_once()
        mock_header.assert_called_once()
        mock_stats.assert_called_once()
        mock_table.assert_called_once()
    
    @patch('reports.services.report.excel.excel_analisis.CacaoPrediction')
    @patch.object(ExcelAnalisisGenerator, '_create_workbook')
    @patch.object(ExcelAnalisisGenerator, '_create_header')
    @patch.object(ExcelAnalisisGenerator, '_create_stats_section')
    @patch.object(ExcelAnalisisGenerator, '_create_detailed_analyses_table')
    @patch.object(ExcelAnalisisGenerator, '_create_quality_chart')
    @patch.object(ExcelAnalisisGenerator, '_create_summary_sheet')
    @patch.object(ExcelAnalisisGenerator, '_save_to_buffer')
    def test_generate_quality_report_with_filters(self, mock_save, mock_summary, mock_chart,
                                                  mock_table, mock_stats, mock_header, mock_workbook,
                                                  mock_prediction_model, excel_generator, mock_user):
        """Test quality report generation with filters."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 5
        
        # Configure aggregate to return different values based on call
        call_count = [0]
        def aggregate_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'avg': 0.90}
            elif call_count[0] == 2:
                return {'avg_alto': 11.0, 'avg_ancho': 9.0, 'avg_grosor': 5.5}
            elif call_count[0] == 3:
                return {'avg': 1.8}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.filter.return_value = mock_queryset
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        mock_save.return_value = b"excel_content"
        
        filtros = {
            'fecha_desde': '2024-01-01',
            'fecha_hasta': '2024-12-31'
        }
        
        result = excel_generator.generate_quality_report(mock_user, filtros)
        
        assert isinstance(result, bytes)
    
    @patch('reports.services.report.excel.excel_analisis.Finca')
    @patch.object(ExcelAnalisisGenerator, '_create_workbook')
    @patch.object(ExcelAnalisisGenerator, '_create_header')
    @patch.object(ExcelAnalisisGenerator, '_create_finca_info_section')
    @patch.object(ExcelAnalisisGenerator, '_create_lotes_stats_section')
    @patch.object(ExcelAnalisisGenerator, '_create_lotes_analysis_section')
    @patch.object(ExcelAnalisisGenerator, '_create_detailed_lotes_sheet')
    @patch.object(ExcelAnalisisGenerator, '_save_to_buffer')
    def test_generate_finca_report_success(self, mock_save, mock_lotes_sheet, mock_lotes_analysis,
                                           mock_lotes_stats, mock_finca_info, mock_header, mock_workbook,
                                           mock_finca_model, excel_generator, mock_user, mock_finca):
        """Test successful finca report generation."""
        mock_finca_model.objects.get.return_value = mock_finca
        
        mock_save.return_value = b"excel_content"
        
        result = excel_generator.generate_finca_report(1, mock_user)
        
        assert isinstance(result, bytes)
        assert result == b"excel_content"
        mock_workbook.assert_called_once()
        mock_header.assert_called_once()
        mock_finca_info.assert_called_once()
    
    @patch('reports.services.report.excel.excel_analisis.Finca')
    def test_generate_finca_report_not_found(self, mock_finca_model, excel_generator, mock_user):
        """Test finca report generation when finca doesn't exist."""
        mock_finca_model.objects.get.side_effect = Exception("DoesNotExist")
        
        with pytest.raises(Exception):
            excel_generator.generate_finca_report(999, mock_user)
    
    @patch('reports.services.report.excel.excel_analisis.LoginHistory')
    @patch('reports.services.report.excel.excel_analisis.ActivityLog')
    @patch.object(ExcelAnalisisGenerator, '_create_workbook')
    @patch.object(ExcelAnalisisGenerator, '_create_header')
    @patch.object(ExcelAnalisisGenerator, '_create_activity_stats_section')
    @patch.object(ExcelAnalisisGenerator, '_create_login_stats_section')
    @patch.object(ExcelAnalisisGenerator, '_save_to_buffer')
    def test_generate_audit_report_success(self, mock_save, mock_login_stats,
                                         mock_activity_stats, mock_header, mock_workbook,
                                         mock_activity_model, mock_login_model, excel_generator, mock_user):
        """Test successful audit report generation."""
        # Mock workbook to be created
        from openpyxl import Workbook
        mock_wb = Workbook()
        excel_generator.workbook = mock_wb
        
        # Mock activity queryset
        mock_activity_queryset = Mock()
        # Make queryset subscriptable for [:100]
        mock_activity_queryset_subset = []
        mock_activity_queryset.__getitem__ = Mock(return_value=mock_activity_queryset_subset)
        mock_activity_queryset.__iter__ = Mock(return_value=iter([]))
        mock_activity_queryset.select_related.return_value.order_by.return_value = mock_activity_queryset
        mock_activity_model.objects.select_related.return_value.order_by.return_value = mock_activity_queryset
        
        # Mock login queryset
        mock_login_queryset = Mock()
        mock_login_queryset.count.return_value = 5
        mock_login_queryset.filter.return_value.count.return_value = 4
        mock_login_model.objects.all.return_value = mock_login_queryset
        mock_login_model.objects.select_related.return_value.order_by.return_value = []
        
        mock_save.return_value = b"excel_content"
        
        result = excel_generator.generate_audit_report(mock_user)
        
        assert isinstance(result, bytes)
        assert result == b"excel_content"
        mock_workbook.assert_called_once()
        mock_header.assert_called_once()
    
    @patch('reports.services.report.excel.excel_analisis.CacaoPrediction')
    def test_get_quality_stats_empty(self, mock_prediction_model, excel_generator):
        """Test getting quality stats with empty queryset."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        stats = excel_generator._get_quality_stats(mock_queryset)
        
        assert stats['total_analyses'] == 0
        assert stats['avg_confidence'] == 0
    
    @patch('reports.services.report.excel.excel_analisis.CacaoPrediction')
    def test_get_quality_stats_with_data(self, mock_prediction_model, excel_generator):
        """Test getting quality stats with data."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 10
        
        # Configure aggregate to return different values based on call
        call_count = [0]
        def aggregate_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'avg': 0.85}
            elif call_count[0] == 2:
                return {'avg_alto': 10.5, 'avg_ancho': 8.3, 'avg_grosor': 5.2}
            elif call_count[0] == 3:
                return {'avg': 1.5}
            return {}
        
        mock_queryset.aggregate.side_effect = aggregate_side_effect
        mock_queryset.filter.return_value = mock_queryset
        mock_prediction_model.objects.all.return_value = mock_queryset
        
        stats = excel_generator._get_quality_stats(mock_queryset)
        
        assert stats['total_analyses'] == 10
        assert stats['avg_confidence'] == 85.0  # 0.85 * 100
    
    def test_apply_filters_no_filters(self, excel_generator):
        """Test applying no filters."""
        mock_queryset = Mock()
        
        result = excel_generator._apply_filters(mock_queryset, None)
        
        assert result == mock_queryset
    
    def test_apply_filters_date_range(self, excel_generator):
        """Test applying date range filters."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {
            'fecha_desde': '2024-01-01',
            'fecha_hasta': '2024-12-31'
        }
        
        result = excel_generator._apply_filters(mock_queryset, filtros)
        
        assert mock_queryset.filter.call_count == 2
    
    def test_apply_filters_user(self, excel_generator):
        """Test applying user filter."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {'usuario_id': 1}
        
        result = excel_generator._apply_filters(mock_queryset, filtros)
        
        mock_queryset.filter.assert_called_once()
    
    def test_apply_filters_finca(self, excel_generator):
        """Test applying finca filter."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {'finca_id': 1}
        
        result = excel_generator._apply_filters(mock_queryset, filtros)
        
        mock_queryset.filter.assert_called_once()
    
    def test_apply_filters_lote(self, excel_generator):
        """Test applying lote filter."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        filtros = {'lote_id': 1}
        
        result = excel_generator._apply_filters(mock_queryset, filtros)
        
        mock_queryset.filter.assert_called_once()

