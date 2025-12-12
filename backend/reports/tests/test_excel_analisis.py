"""
Tests for ExcelAnalisisGenerator.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

from reports.services.report.excel.excel_analisis import ExcelAnalisisGenerator


@pytest.fixture
def excel_generator():
    """Create ExcelAnalisisGenerator instance."""
    return ExcelAnalisisGenerator()


@pytest.fixture
def user(db):
    """Create test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def finca(user):
    """Create test finca."""
    from fincas_app.models import Finca
    return Finca.objects.create(
        nombre='Test Finca',
        ubicacion='Test Location',
        municipio='Test Municipio',
        departamento='Test Departamento',
        hectareas=Decimal('10.5'),
        agricultor=user,
        activa=True
    )


class TestExcelAnalisisGenerator:
    """Tests for ExcelAnalisisGenerator class."""
    
    def test_generate_quality_report(self, excel_generator, user):
        """Test generate_quality_report method."""
        with patch('reports.services.report.excel.excel_analisis.apply_prediction_filters') as mock_filter, \
             patch('reports.services.report.excel.excel_analisis.get_quality_stats') as mock_stats:
            # Create a mock queryset that supports chaining and slicing
            mock_slice = Mock()
            mock_slice.__iter__ = Mock(return_value=iter([]))
            mock_slice.__len__ = Mock(return_value=0)
            
            mock_order_by = Mock()
            mock_order_by.__getitem__ = Mock(return_value=mock_slice)
            
            mock_select_related = Mock()
            mock_select_related.order_by = Mock(return_value=mock_order_by)
            
            mock_queryset = Mock()
            mock_queryset.select_related = Mock(return_value=mock_select_related)
            
            mock_filter.return_value = mock_queryset
            mock_stats.return_value = {
                'total_analyses': 10,
                'avg_confidence': 85.5,
                'quality_distribution': {'Excelente (90%)': 5},
                'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
                'avg_weight': 1.5
            }
            
            content = excel_generator.generate_quality_report(user, None)
            assert isinstance(content, bytes)
            assert len(content) > 0
    
    def test_generate_quality_report_with_error(self, excel_generator, user):
        """Test generate_quality_report with error."""
        with patch.object(excel_generator, '_create_workbook', side_effect=Exception("Error")):
            with pytest.raises(Exception):
                excel_generator.generate_quality_report(user, None)
    
    def test_generate_finca_report(self, excel_generator, user, finca):
        """Test generate_finca_report method."""
        with patch('reports.services.report.excel.excel_analisis.get_lotes_stats') as mock_stats:
            mock_stats.return_value = {
                'total_lotes': 5,
                'lotes_activos': 3,
                'total_area': 10.5,
                'variedades': []
            }
            
            content = excel_generator.generate_finca_report(finca.id, user, None)
            assert isinstance(content, bytes)
            assert len(content) > 0
    
    def test_generate_finca_report_not_found(self, excel_generator, user):
        """Test generate_finca_report with finca not found."""
        with pytest.raises(Exception):
            excel_generator.generate_finca_report(99999, user, None)
    
    def test_generate_audit_report(self, excel_generator, user):
        """Test generate_audit_report method."""
        from audit.models import ActivityLog, LoginHistory
        
        mock_activity_instance = Mock()
        mock_timestamp = Mock()
        mock_timestamp.strftime = Mock(return_value='2024-01-01 10:00:00')
        mock_activity_instance.timestamp = mock_timestamp
        mock_activity_instance.user = user
        mock_activity_instance.action = 'CREATE'
        mock_activity_instance.resource_type = 'Finca'
        mock_activity_instance.details = {}
        mock_activity_instance.ip_address = '127.0.0.1'
        
        mock_login_instance = Mock()
        mock_login_time = Mock()
        mock_login_time.strftime = Mock(return_value='2024-01-01 10:00:00')
        mock_login_instance.login_time = mock_login_time
        mock_login_instance.usuario = user
        mock_login_instance.ip_address = '127.0.0.1'
        mock_login_instance.success = True
        mock_login_instance.session_duration_formatted = '1h 30m'
        mock_login_instance.failure_reason = None
        
        mock_activity_sliced = Mock()
        mock_activity_sliced.__iter__ = Mock(return_value=iter([mock_activity_instance]))
        mock_activity_ordered = Mock()
        mock_activity_ordered.__getitem__ = Mock(return_value=mock_activity_sliced)
        mock_activity_selected = Mock()
        mock_activity_selected.order_by = Mock(return_value=mock_activity_ordered)
        
        mock_login_sliced = Mock()
        mock_login_sliced.__iter__ = Mock(return_value=iter([mock_login_instance]))
        mock_login_ordered = Mock()
        mock_login_ordered.__getitem__ = Mock(return_value=mock_login_sliced)
        mock_login_selected = Mock()
        mock_login_selected.order_by = Mock(return_value=mock_login_ordered)
        
        with patch('reports.services.report.excel.excel_analisis.get_activity_stats') as mock_activity_stats, \
             patch('reports.services.report.excel.excel_analisis.get_login_stats') as mock_login_stats, \
             patch.object(ActivityLog, 'objects') as mock_activity_objects, \
             patch.object(LoginHistory, 'objects') as mock_login_objects:
            mock_activity_objects.select_related = Mock(return_value=mock_activity_selected)
            mock_login_objects.select_related = Mock(return_value=mock_login_selected)
            
            mock_activity_stats.return_value = {
                'total_activities': 100,
                'activities_today': 10
            }
            mock_login_stats.return_value = {
                'total_logins': 50,
                'successful_logins': 45,
                'failed_logins': 5,
                'success_rate': 90.0
            }
            
            content = excel_generator.generate_audit_report(user, None)
            assert isinstance(content, bytes)
            assert len(content) > 0
    
    def test_generate_custom_report_calidad(self, excel_generator, user):
        """Test generate_custom_report with calidad type."""
        with patch('reports.services.report.excel.excel_analisis.apply_prediction_filters') as mock_filter, \
             patch('reports.services.report.excel.excel_analisis.get_quality_stats') as mock_stats:
            mock_query = Mock()
            mock_filter.return_value = mock_query
            mock_stats.return_value = {
                'total_analyses': 10,
                'avg_confidence': 85.5,
                'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
                'avg_weight': 1.5
            }
            
            parametros = {
                'include_dimensions': True,
                'include_weight': True,
                'include_confidence': True
            }
            content = excel_generator.generate_custom_report(user, 'calidad', parametros, None)
            assert isinstance(content, bytes)
    
    def test_generate_custom_report_finca(self, excel_generator, user, finca):
        """Test generate_custom_report with finca type."""
        parametros = {
            'finca_id': finca.id,
            'include_basic_info': True,
            'include_lotes': True,
            'include_quality': True
        }
        content = excel_generator.generate_custom_report(user, 'finca', parametros, None)
        assert isinstance(content, bytes)
    
    def test_generate_custom_report_auditoria(self, excel_generator, user):
        """Test generate_custom_report with auditoria type."""
        with patch('reports.services.report.excel.excel_analisis.get_activity_stats') as mock_stats:
            mock_stats.return_value = {
                'total_activities': 100,
                'activities_today': 10,
                'top_users': [],
                'activities_by_action': {}
            }
            
            parametros = {
                'include_activity': True,
                'include_top_users': True,
                'include_action_types': True
            }
            content = excel_generator.generate_custom_report(user, 'auditoria', parametros, None)
            assert isinstance(content, bytes)
    
    def test_create_stats_section(self, excel_generator):
        """Test _create_stats_section method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_analyses': 10,
            'avg_confidence': 85.5,
            'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
            'avg_weight': 1.5
        }
        excel_generator._create_stats_section(stats)
        assert excel_generator.ws['A8'].value is not None
    
    def test_create_detailed_analyses_table(self, excel_generator):
        """Test _create_detailed_analyses_table method."""
        excel_generator._create_workbook("Test")
        prediction = Mock()
        prediction.id = 1
        prediction.created_at = Mock()
        prediction.created_at.strftime = Mock(return_value='2024-01-01')
        prediction.alto_mm = 20.5
        prediction.ancho_mm = 15.3
        prediction.grosor_mm = 10.2
        prediction.peso_g = 1.5
        prediction.average_confidence = 0.85
        prediction.image = Mock()
        prediction.image.user = Mock()
        prediction.image.user.username = 'testuser'
        prediction.image.finca = 'Test Finca'
        prediction.image.region = 'Test Region'
        
        queryset = Mock()
        queryset.select_related.return_value.order_by.return_value.__getitem__ = Mock(return_value=[prediction])
        queryset.select_related.return_value.order_by.return_value.__len__ = Mock(return_value=1)
        
        excel_generator._create_detailed_analyses_table(queryset)
        # Should not raise
    
    def test_create_quality_chart(self, excel_generator):
        """Test _create_quality_chart method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_analyses': 8,
            'quality_distribution': {'Excelente (90%)': 5, 'Buena (80-89%)': 3}
        }
        excel_generator._create_quality_chart(stats)
        # Should not raise
    
    def test_create_quality_chart_empty(self, excel_generator):
        """Test _create_quality_chart with empty distribution."""
        excel_generator._create_workbook("Test")
        stats = {'quality_distribution': {}}
        excel_generator._create_quality_chart(stats)
        # Should not raise
    
    def test_create_summary_sheet(self, excel_generator, user):
        """Test _create_summary_sheet method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_analyses': 10,
            'avg_confidence': 85.5,
            'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
            'avg_weight': 1.5
        }
        excel_generator._create_summary_sheet(stats, user)
        # Should not raise
    
    def test_create_finca_info_section(self, excel_generator, finca):
        """Test _create_finca_info_section method."""
        excel_generator._create_workbook("Test")
        excel_generator._create_finca_info_section(finca)
        assert excel_generator.ws['A8'].value is not None
    
    def test_create_lotes_stats_section(self, excel_generator):
        """Test _create_lotes_stats_section method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_lotes': 5,
            'lotes_activos': 3,
            'total_area': 10.5,
            'variedades': []
        }
        excel_generator._create_lotes_stats_section(stats)
        assert excel_generator.ws['A20'].value is not None
    
    def test_create_lotes_analysis_section(self, excel_generator, finca):
        """Test _create_lotes_analysis_section method."""
        excel_generator._create_workbook("Test")
        excel_generator._create_lotes_analysis_section(finca)
        # Should not raise
    
    def test_create_lotes_analysis_section_empty(self, excel_generator, finca):
        """Test _create_lotes_analysis_section with no lotes."""
        excel_generator._create_workbook("Test")
        mock_queryset = Mock()
        mock_queryset.exists.return_value = False
        with patch.object(finca.lotes, 'all', return_value=mock_queryset):
            excel_generator._create_lotes_analysis_section(finca)
        # Should not raise
    
    def test_create_detailed_lotes_sheet(self, excel_generator, finca):
        """Test _create_detailed_lotes_sheet method."""
        excel_generator._create_workbook("Test")
        excel_generator._create_detailed_lotes_sheet(finca)
        # Should not raise
    
    def test_create_activity_stats_section(self, excel_generator):
        """Test _create_activity_stats_section method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_activities': 100,
            'activities_today': 10
        }
        excel_generator._create_activity_stats_section(stats)
        assert excel_generator.ws['A8'].value is not None
    
    def test_create_login_stats_section(self, excel_generator):
        """Test _create_login_stats_section method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_logins': 50,
            'successful_logins': 45,
            'failed_logins': 5,
            'success_rate': 90.0
        }
        excel_generator._create_login_stats_section(stats)
        assert excel_generator.ws['A14'].value is not None
    
    def test_create_detailed_activities_sheet(self, excel_generator):
        """Test _create_detailed_activities_sheet method."""
        excel_generator._create_workbook("Test")
        excel_generator._create_detailed_activities_sheet(None)
        # Should not raise
    
    def test_create_detailed_logins_sheet(self, excel_generator):
        """Test _create_detailed_logins_sheet method."""
        excel_generator._create_workbook("Test")
        excel_generator._create_detailed_logins_sheet(None)
        # Should not raise
    
    def test_create_custom_quality_section(self, excel_generator):
        """Test _create_custom_quality_section method."""
        excel_generator._create_workbook("Test")
        stats = {
            'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
            'avg_weight': 1.5,
            'avg_confidence': 85.5
        }
        parametros = {
            'include_dimensions': True,
            'include_weight': True,
            'include_confidence': True
        }
        excel_generator._create_custom_quality_section(stats, parametros)
        assert excel_generator.ws['A8'].value is not None
    
    def test_create_custom_finca_section(self, excel_generator, finca):
        """Test _create_custom_finca_section method."""
        excel_generator._create_workbook("Test")
        parametros = {
            'include_basic_info': True,
            'include_lotes': True,
            'include_quality': True
        }
        excel_generator._create_custom_finca_section(finca, parametros)
        assert excel_generator.ws['A8'].value is not None
    
    def test_create_custom_audit_section(self, excel_generator):
        """Test _create_custom_audit_section method."""
        excel_generator._create_workbook("Test")
        stats = {
            'total_activities': 100,
            'activities_today': 10,
            'top_users': [],
            'activities_by_action': {}
        }
        parametros = {
            'include_activity': True,
            'include_top_users': True,
            'include_action_types': True
        }
        excel_generator._create_custom_audit_section(stats, parametros)
        assert excel_generator.ws['A8'].value is not None

