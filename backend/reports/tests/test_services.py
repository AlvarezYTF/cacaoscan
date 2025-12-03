"""
Tests for Reports Services.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from reports.services.report.report_generation_service import ReportGenerationService
from reports.services.report.report_management_service import ReportManagementService
from reports.services.report.report_stats import (
    apply_prediction_filters,
    get_quality_stats,
    get_lotes_stats,
    get_activity_stats,
    get_login_stats
)
from reports.services.report.pdf_generator import CacaoReportPDFGenerator
from reports.services.report.excel.excel_base import ExcelBaseGenerator
from reports.services.report.excel.excel_agricultores import ExcelAgricultoresGenerator
from reports.services.report.excel.excel_analisis import ExcelAnalisisGenerator
from reports.services.report.excel.excel_usuarios import ExcelUsuariosGenerator
from reports.models import ReporteGenerado


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def report_data():
    """Valid report data."""
    return {
        'tipo_reporte': 'analisis_general',
        'fecha_inicio': (timezone.now() - timedelta(days=30)).isoformat(),
        'fecha_fin': timezone.now().isoformat(),
        'titulo': 'Test Report',
        'descripcion': 'Test Description',
        'formato': 'json'
    }


@pytest.mark.django_db
class TestReportGenerationService:
    """Tests for ReportGenerationService."""

    def test_generate_analysis_report_success(self, user, report_data):
        """Test successful report generation."""
        service = ReportGenerationService()
        
        with patch.object(service, '_generate_general_analysis_report') as mock_generate:
            mock_generate.return_value = {'resumen': {'total_analisis': 10}}
            
            result = service.generate_analysis_report(user, report_data)
        
        assert result.success is True
        assert 'reporte' in result.data
        assert result.data['reporte']['tipo_reporte'] == 'analisis_general'
        
        # Verify report was created
        report = ReporteGenerado.objects.get(usuario=user, tipo_reporte='analisis_general')
        assert report.estado == 'completado'

    def test_generate_analysis_report_missing_fields(self, user):
        """Test report generation with missing required fields."""
        service = ReportGenerationService()
        
        incomplete_data = {'tipo_reporte': 'analisis_general'}
        result = service.generate_analysis_report(user, incomplete_data)
        
        assert result.success is False
        assert 'fecha_inicio' in str(result.error) or 'fecha_fin' in str(result.error)

    def test_generate_analysis_report_invalid_dates(self, user):
        """Test report generation with invalid date range."""
        service = ReportGenerationService()
        
        invalid_data = {
            'tipo_reporte': 'analisis_general',
            'fecha_inicio': timezone.now().isoformat(),
            'fecha_fin': (timezone.now() - timedelta(days=1)).isoformat()  # End before start
        }
        
        result = service.generate_analysis_report(user, invalid_data)
        
        assert result.success is False
        assert 'fecha de inicio' in str(result.error).lower()

    def test_generate_analysis_report_analisis_periodo_alias(self, user, report_data):
        """Test that analisis_periodo is treated as analisis_general."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'analisis_periodo'
        
        with patch.object(service, '_generate_general_analysis_report') as mock_generate:
            mock_generate.return_value = {'resumen': {'total_analisis': 10}}
            
            result = service.generate_analysis_report(user, report_data)
        
        assert result.success is True
        # Verify it was converted to analisis_general
        report = ReporteGenerado.objects.get(usuario=user)
        assert report.tipo_reporte == 'analisis_periodo'  # Original is preserved

    def test_generate_analysis_report_por_finca(self, user, report_data):
        """Test finca-specific report generation."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'analisis_por_finca'
        report_data['finca_id'] = 1
        
        with patch.object(service, '_generate_finca_analysis_report') as mock_generate:
            mock_generate.return_value = {'resumen': {'total_analisis': 5}}
            
            result = service.generate_analysis_report(user, report_data)
        
        assert result.success is True
        mock_generate.assert_called_once()

    def test_generate_analysis_report_por_finca_missing_id(self, user, report_data):
        """Test finca report without finca_id."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'analisis_por_finca'
        # Missing finca_id
        
        result = service.generate_analysis_report(user, report_data)
        
        assert result.success is False
        assert 'finca_id' in str(result.error).lower()

    def test_generate_analysis_report_por_lote(self, user, report_data):
        """Test lote-specific report generation."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'analisis_por_lote'
        report_data['lote_id'] = 1
        
        with patch.object(service, '_generate_lote_analysis_report') as mock_generate:
            mock_generate.return_value = {'resumen': {'total_analisis': 3}}
            
            result = service.generate_analysis_report(user, report_data)
        
        assert result.success is True
        mock_generate.assert_called_once()

    def test_generate_analysis_report_por_lote_missing_id(self, user, report_data):
        """Test lote report without lote_id."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'analisis_por_lote'
        # Missing lote_id
        
        result = service.generate_analysis_report(user, report_data)
        
        assert result.success is False
        assert 'lote_id' in str(result.error).lower()

    def test_generate_analysis_report_estadisticas_usuario(self, user, report_data):
        """Test user statistics report generation."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'estadisticas_usuario'
        
        with patch.object(service, '_generate_user_statistics_report') as mock_generate:
            mock_generate.return_value = {'resumen_usuario': {'total_imagenes': 20}}
            
            result = service.generate_analysis_report(user, report_data)
        
        assert result.success is True
        mock_generate.assert_called_once()

    def test_generate_analysis_report_invalid_type(self, user, report_data):
        """Test report generation with invalid report type."""
        service = ReportGenerationService()
        report_data['tipo_reporte'] = 'invalid_type'
        
        result = service.generate_analysis_report(user, report_data)
        
        assert result.success is False
        assert 'no válido' in str(result.error).lower()

    def test_calculate_dimension_stats(self, user):
        """Test dimension statistics calculation."""
        service = ReportGenerationService()
        
        # Mock queryset with aggregate
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'avg': 10.5, 'min': 5.0, 'max': 15.0}
        mock_queryset.values_list.return_value = [10, 11, 12, 13, 14]
        
        with patch.object(service, '_calculate_std_dev', return_value=1.5):
            stats = service._calculate_dimension_stats(mock_queryset)
        
        assert 'alto_mm' in stats
        assert stats['alto_mm']['promedio'] == 10.5
        assert stats['alto_mm']['minimo'] == 5.0
        assert stats['alto_mm']['maximo'] == 15.0

    def test_calculate_confidence_stats(self, user):
        """Test confidence statistics calculation."""
        service = ReportGenerationService()
        
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'avg': 0.85, 'min': 0.7, 'max': 0.95}
        mock_queryset.filter.return_value.count.return_value = 5
        
        stats = service._calculate_confidence_stats(mock_queryset)
        
        assert stats['promedio'] == 0.85
        assert 'distribucion' in stats
        assert 'alta' in stats['distribucion']

    def test_calculate_std_dev(self, user):
        """Test standard deviation calculation."""
        service = ReportGenerationService()
        
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value = [10, 12, 14, 16, 18]  # Mean = 14
        
        std_dev = service._calculate_std_dev(mock_queryset, 'test_field')
        
        # Approximate std dev for [10, 12, 14, 16, 18] is around 2.83
        assert std_dev > 0
        assert isinstance(std_dev, float)

    def test_calculate_std_dev_empty(self, user):
        """Test standard deviation with empty queryset."""
        service = ReportGenerationService()
        
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value = []
        
        std_dev = service._calculate_std_dev(mock_queryset, 'test_field')
        
        assert std_dev == 0.0


@pytest.mark.django_db
class TestReportManagementService:
    """Tests for ReportManagementService."""

    def test_get_user_reports_success(self, user):
        """Test getting user reports successfully."""
        service = ReportManagementService()
        
        # Create test reports
        ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_general',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        
        result = service.get_user_reports(user, page=1, page_size=20)
        
        assert result.success is True
        assert 'reports' in result.data
        assert len(result.data['reports']) == 1
        assert 'pagination' in result.data

    def test_get_user_reports_with_filters(self, user):
        """Test getting user reports with filters."""
        service = ReportManagementService()
        
        # Create reports with different types
        ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_general',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_por_finca',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        
        filters = {'tipo_reporte': 'analisis_general'}
        result = service.get_user_reports(user, page=1, page_size=20, filters=filters)
        
        assert result.success is True
        assert len(result.data['reports']) == 1
        assert result.data['reports'][0]['tipo_reporte'] == 'analisis_general'

    def test_get_report_details_success(self, user):
        """Test getting report details successfully."""
        service = ReportManagementService()
        
        report = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_general',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now(),
            contenido={'test': 'data'}
        )
        
        result = service.get_report_details(report.id, user)
        
        assert result.success is True
        assert result.data['id'] == report.id
        assert result.data['tipo_reporte'] == 'analisis_general'
        assert 'contenido' in result.data

    def test_get_report_details_not_found(self, user):
        """Test getting non-existent report."""
        service = ReportManagementService()
        
        result = service.get_report_details(99999, user)
        
        assert result.success is False
        assert 'no encontrado' in str(result.error).lower()

    def test_get_report_details_wrong_user(self, user):
        """Test getting report from different user."""
        service = ReportManagementService()
        
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        report = ReporteGenerado.objects.create(
            usuario=other_user,
            tipo_reporte='analisis_general',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        
        result = service.get_report_details(report.id, user)
        
        assert result.success is False
        assert 'no encontrado' in str(result.error).lower()

    def test_delete_report_success(self, user):
        """Test deleting report successfully."""
        service = ReportManagementService()
        
        report = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_general',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        
        result = service.delete_report(report.id, user)
        
        assert result.success is True
        assert not ReporteGenerado.objects.filter(id=report.id).exists()

    def test_delete_report_not_found(self, user):
        """Test deleting non-existent report."""
        service = ReportManagementService()
        
        result = service.delete_report(99999, user)
        
        assert result.success is False
        assert 'no encontrado' in str(result.error).lower()

    def test_get_report_statistics(self, user):
        """Test getting report statistics."""
        service = ReportManagementService()
        
        # Create reports
        ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_general',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis_por_finca',
            estado='completado',
            formato='json',
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now()
        )
        
        result = service.get_report_statistics(user)
        
        assert result.success is True
        assert result.data['total_reports'] == 2
        assert 'reports_by_type' in result.data
        assert 'reports_by_status' in result.data


@pytest.mark.django_db
class TestReportStats:
    """Tests for report_stats utility functions."""

    def test_apply_prediction_filters_no_filters(self):
        """Test applying no filters."""
        from images_app.models import CacaoPrediction
        
        queryset = CacaoPrediction.objects.all()
        filtered = apply_prediction_filters(queryset, None)
        
        assert filtered == queryset

    def test_apply_prediction_filters_by_date(self):
        """Test applying date filters."""
        from images_app.models import CacaoPrediction
        
        queryset = CacaoPrediction.objects.all()
        filtros = {
            'fecha_desde': timezone.now().date() - timedelta(days=10),
            'fecha_hasta': timezone.now().date()
        }
        
        filtered = apply_prediction_filters(queryset, filtros)
        
        # Should return filtered queryset
        assert filtered is not None

    def test_get_quality_stats_empty(self):
        """Test quality stats with empty queryset."""
        from images_app.models import CacaoPrediction
        
        queryset = CacaoPrediction.objects.none()
        stats = get_quality_stats(queryset)
        
        assert stats['total_analyses'] == 0
        assert stats['avg_confidence'] == 0

    def test_get_lotes_stats(self):
        """Test lotes statistics."""
        from fincas_app.models import Finca, Lote
        
        user = User.objects.create_user(
            username='farmer',
            email='farmer@example.com',
            password='pass123'
        )
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            agricultor=user,
            municipio='Test',
            departamento='Test',
            hectareas=10.0
        )
        
        Lote.objects.create(
            finca=finca,
            identificador='L1',
            variedad='Criollo',
            area_hectareas=5.0,
            activo=True
        )
        
        stats = get_lotes_stats(finca)
        
        assert stats['total_lotes'] == 1
        assert stats['lotes_activos'] == 1
        assert stats['total_area'] == 5.0

    def test_get_activity_stats(self):
        """Test activity statistics."""
        from audit.models import ActivityLog
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        ActivityLog.objects.create(
            usuario=user,
            accion='create',
            modelo='TestModel',
            descripcion='Test activity'
        )
        
        stats = get_activity_stats({})
        
        assert stats['total_activities'] >= 1
        assert 'activities_today' in stats

    def test_get_login_stats(self):
        """Test login statistics."""
        from audit.models import LoginHistory
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        LoginHistory.objects.create(
            usuario=user,
            success=True,
            ip_address='127.0.0.1'
        )
        
        stats = get_login_stats({})
        
        assert stats['total_logins'] >= 1
        assert stats['successful_logins'] >= 1
        assert 'success_rate' in stats


@pytest.mark.django_db
class TestPDFGenerator:
    """Tests for CacaoReportPDFGenerator."""

    def test_pdf_generator_init(self):
        """Test PDF generator initialization."""
        generator = CacaoReportPDFGenerator()
        
        assert generator.styles is not None
        assert 'CustomTitle' in [s.name for s in generator.styles]

    def test_generate_quality_report(self, user):
        """Test generating quality PDF report."""
        generator = CacaoReportPDFGenerator()
        
        with patch('reports.services.report.pdf_generator.apply_prediction_filters') as mock_filter:
            with patch('reports.services.report.pdf_generator.get_quality_stats') as mock_stats:
                mock_stats.return_value = {
                    'total_analyses': 10,
                    'avg_confidence': 85.5,
                    'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
                    'avg_weight': 1.5,
                    'quality_distribution': {}
                }
                
                pdf_content = generator.generate_quality_report(user, {})
        
        assert pdf_content is not None
        assert len(pdf_content) > 0
        assert isinstance(pdf_content, bytes)

    def test_generate_finca_report(self, user):
        """Test generating finca PDF report."""
        from fincas_app.models import Finca
        
        generator = CacaoReportPDFGenerator()
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            agricultor=user,
            municipio='Test',
            departamento='Test',
            hectareas=10.0
        )
        
        with patch('reports.services.report.pdf_generator.get_lotes_stats') as mock_stats:
            mock_stats.return_value = {
                'total_lotes': 2,
                'lotes_activos': 2,
                'total_area': 10.0,
                'variedades': []
            }
            
            pdf_content = generator.generate_finca_report(finca.id, user, {})
        
        assert pdf_content is not None
        assert len(pdf_content) > 0

    def test_generate_audit_report(self, user):
        """Test generating audit PDF report."""
        generator = CacaoReportPDFGenerator()
        
        with patch('reports.services.report.pdf_generator.get_activity_stats') as mock_activity:
            with patch('reports.services.report.pdf_generator.get_login_stats') as mock_login:
                mock_activity.return_value = {
                    'total_activities': 10,
                    'activities_today': 2
                }
                mock_login.return_value = {
                    'total_logins': 20,
                    'successful_logins': 18,
                    'failed_logins': 2,
                    'success_rate': 90.0
                }
                
                pdf_content = generator.generate_audit_report(user, {})
        
        assert pdf_content is not None
        assert len(pdf_content) > 0


@pytest.mark.django_db
class TestExcelBaseGenerator:
    """Tests for ExcelBaseGenerator."""

    def test_excel_base_init(self):
        """Test Excel base generator initialization."""
        generator = ExcelBaseGenerator()
        
        assert generator.workbook is None
        assert generator.ws is None

    def test_create_workbook(self):
        """Test creating workbook."""
        generator = ExcelBaseGenerator()
        generator._create_workbook("Test Sheet")
        
        assert generator.workbook is not None
        assert generator.ws is not None
        assert generator.ws.title == "Test Sheet"

    def test_get_thin_border(self):
        """Test getting thin border."""
        generator = ExcelBaseGenerator()
        border = generator._get_thin_border()
        
        assert border is not None

    def test_get_header_fill(self):
        """Test getting header fill."""
        generator = ExcelBaseGenerator()
        fill = generator._get_header_fill()
        
        assert fill is not None

    def test_save_to_buffer(self):
        """Test saving to buffer."""
        generator = ExcelBaseGenerator()
        generator._create_workbook("Test")
        generator.ws['A1'] = "Test"
        
        content = generator._save_to_buffer()
        
        assert content is not None
        assert len(content) > 0
        assert isinstance(content, bytes)


@pytest.mark.django_db
class TestExcelAgricultoresGenerator:
    """Tests for ExcelAgricultoresGenerator."""

    def test_generate_farmers_report(self):
        """Test generating farmers Excel report."""
        generator = ExcelAgricultoresGenerator()
        
        User.objects.create_user(
            username='farmer1',
            email='farmer1@example.com',
            password='pass123'
        )
        
        content = generator.generate_farmers_report()
        
        assert content is not None
        assert len(content) > 0
        assert isinstance(content, bytes)


@pytest.mark.django_db
class TestExcelAnalisisGenerator:
    """Tests for ExcelAnalisisGenerator."""

    def test_generate_quality_report(self, user):
        """Test generating quality Excel report."""
        generator = ExcelAnalisisGenerator()
        
        with patch('reports.services.report.excel.excel_analisis.apply_prediction_filters') as mock_filter:
            with patch('reports.services.report.excel.excel_analisis.get_quality_stats') as mock_stats:
                mock_stats.return_value = {
                    'total_analyses': 10,
                    'avg_confidence': 85.5,
                    'avg_dimensions': {'alto': 20, 'ancho': 15, 'grosor': 10},
                    'avg_weight': 1.5,
                    'quality_distribution': {}
                }
                
                content = generator.generate_quality_report(user, {})
        
        assert content is not None
        assert len(content) > 0

    def test_generate_finca_report(self, user):
        """Test generating finca Excel report."""
        from fincas_app.models import Finca
        
        generator = ExcelAnalisisGenerator()
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            agricultor=user,
            municipio='Test',
            departamento='Test',
            hectareas=10.0
        )
        
        with patch('reports.services.report.excel.excel_analisis.get_lotes_stats') as mock_stats:
            mock_stats.return_value = {
                'total_lotes': 2,
                'lotes_activos': 2,
                'total_area': 10.0,
                'variedades': []
            }
            
            content = generator.generate_finca_report(finca.id, user, {})
        
        assert content is not None
        assert len(content) > 0

    def test_generate_audit_report(self, user):
        """Test generating audit Excel report."""
        generator = ExcelAnalisisGenerator()
        
        with patch('reports.services.report.excel.excel_analisis.get_activity_stats') as mock_activity:
            with patch('reports.services.report.excel.excel_analisis.get_login_stats') as mock_login:
                mock_activity.return_value = {
                    'total_activities': 10,
                    'activities_today': 2
                }
                mock_login.return_value = {
                    'total_logins': 20,
                    'successful_logins': 18,
                    'failed_logins': 2,
                    'success_rate': 90.0
                }
                
                content = generator.generate_audit_report(user, {})
        
        assert content is not None
        assert len(content) > 0


@pytest.mark.django_db
class TestExcelUsuariosGenerator:
    """Tests for ExcelUsuariosGenerator."""

    def test_generate_users_report(self):
        """Test generating users Excel report."""
        generator = ExcelUsuariosGenerator()
        
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        
        content = generator.generate_users_report()
        
        assert content is not None
        assert len(content) > 0
        assert isinstance(content, bytes)

    def test_generate_users_report_empty(self):
        """Test generating users report with no users."""
        generator = ExcelUsuariosGenerator()
        
        # Delete all users except the one created by fixtures
        User.objects.filter(is_superuser=False, is_staff=False).delete()
        
        content = generator.generate_users_report()
        
        assert content is not None
        assert len(content) > 0

