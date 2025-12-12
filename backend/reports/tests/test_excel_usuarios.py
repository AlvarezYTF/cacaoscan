"""
Tests for ExcelUsuariosGenerator.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User, Group
from decimal import Decimal

from reports.services.report.excel.excel_usuarios import ExcelUsuariosGenerator


@pytest.fixture
def excel_generator():
    """Create ExcelUsuariosGenerator instance."""
    return ExcelUsuariosGenerator()


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


class TestExcelUsuariosGenerator:
    """Tests for ExcelUsuariosGenerator class."""
    
    def test_get_styles(self, excel_generator):
        """Test _get_styles method."""
        styles = excel_generator._get_styles()
        assert 'bold_font' in styles
        assert 'header_fill' in styles
        assert 'thin_border' in styles
        assert 'align_center' in styles
        assert 'align_vertical' in styles
    
    def test_setup_headers(self, excel_generator):
        """Test _setup_headers method."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        headers = excel_generator._setup_headers(styles)
        
        assert len(headers) == 12
        assert excel_generator.ws['A1'].value == 'ID Usuario'
        assert excel_generator.ws[1][0].font.bold is True
    
    def test_get_user_role_admin(self, excel_generator):
        """Test _get_user_role for admin."""
        user = Mock()
        user.is_superuser = True
        user.is_staff = True
        user.groups.filter.return_value.exists.return_value = False
        
        role = excel_generator._get_user_role(user)
        assert role == 'admin'
    
    def test_get_user_role_analyst(self, excel_generator):
        """Test _get_user_role for analyst."""
        user = Mock()
        user.is_superuser = False
        user.is_staff = False
        user.groups.filter.return_value.exists.return_value = True
        
        role = excel_generator._get_user_role(user)
        assert role == 'analyst'
    
    def test_get_user_role_farmer(self, excel_generator):
        """Test _get_user_role for farmer."""
        user = Mock()
        user.is_superuser = False
        user.is_staff = False
        user.groups.filter.return_value.exists.return_value = False
        
        role = excel_generator._get_user_role(user)
        assert role == 'farmer'
    
    def test_add_user_row_with_finca(self, excel_generator, user, finca):
        """Test _add_user_row with finca."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._setup_headers(styles)
        excel_generator._add_user_row(user, 'farmer', finca)
        
        assert excel_generator.ws['A2'].value == user.id
        assert excel_generator.ws['B2'].value is not None
        assert excel_generator.ws['G2'].value == finca.nombre
    
    def test_add_user_row_without_finca(self, excel_generator, user):
        """Test _add_user_row without finca."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._setup_headers(styles)
        excel_generator._add_user_row(user, 'farmer', None)
        
        assert excel_generator.ws['A2'].value == user.id
        assert excel_generator.ws['G2'].value == 'Sin fincas'
    
    def test_add_user_row_with_none_coordinates(self, excel_generator, user):
        """Test _add_user_row with None coordinates."""
        from fincas_app.models import Finca
        finca = Mock()
        finca.nombre = 'Test Finca'
        finca.departamento = None
        finca.municipio = None
        finca.hectareas = None
        finca.coordenadas_lat = None
        finca.coordenadas_lng = None
        
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._setup_headers(styles)
        excel_generator._add_user_row(user, 'farmer', finca)
        
        assert excel_generator.ws['A2'].value == user.id
    
    def test_add_user_data(self, excel_generator, user, finca):
        """Test _add_user_data method."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._setup_headers(styles)
        excel_generator._add_user_data([user])
        
        assert excel_generator.ws.max_row >= 2
    
    def test_add_user_data_without_fincas(self, excel_generator, user):
        """Test _add_user_data without fincas."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._setup_headers(styles)
        excel_generator._add_user_data([user])
        
        assert excel_generator.ws.max_row >= 2
    
    def test_apply_data_formatting(self, excel_generator, user):
        """Test _apply_data_formatting method."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        headers = excel_generator._setup_headers(styles)
        excel_generator._add_user_data([user])
        excel_generator._apply_data_formatting(styles, headers)
        
        # Should not raise
        assert excel_generator.ws['A2'].border is not None
    
    def test_auto_adjust_columns(self, excel_generator, user):
        """Test _auto_adjust_columns method."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._setup_headers(styles)
        excel_generator._add_user_data([user])
        excel_generator._auto_adjust_columns()
        
        # Should not raise
        assert excel_generator.ws.column_dimensions['A'].width > 0
    
    def test_auto_adjust_columns_with_exception(self, excel_generator):
        """Test _auto_adjust_columns with exception."""
        excel_generator._create_workbook("Test")
        excel_generator.ws['A1'] = 'Test'
        
        # Patch the columns iteration to raise exception
        # Since columns is a property that returns an iterator, we need to patch it at the class level
        original_columns = excel_generator.ws.columns
        
        # Create a mock that raises when iterated
        class MockColumns:
            def __iter__(self):
                raise Exception("Error")
        
        # Replace the columns property temporarily
        with patch.object(type(excel_generator.ws), 'columns', property(lambda self: MockColumns())):
            # The method should handle the exception gracefully
            excel_generator._auto_adjust_columns()
        # Should not raise, just log warning
    
    def test_show_empty_message(self, excel_generator):
        """Test _show_empty_message method."""
        excel_generator._create_workbook("Test")
        styles = excel_generator._get_styles()
        excel_generator._show_empty_message(styles)
        
        assert excel_generator.ws['A1'].value == "Sin registros disponibles"
        assert excel_generator.ws['A1'].font.bold is True
    
    def test_generate_users_report(self, excel_generator, user):
        """Test generate_users_report method."""
        content = excel_generator.generate_users_report()
        assert isinstance(content, bytes)
        assert len(content) > 0
    
    def test_generate_users_report_empty(self, excel_generator):
        """Test generate_users_report with no users."""
        with patch('django.contrib.auth.models.User.objects.all') as mock_all:
            mock_query = Mock()
            mock_query.order_by.return_value.select_related.return_value.prefetch_related.return_value.exists.return_value = False
            mock_all.return_value = mock_query
            
            content = excel_generator.generate_users_report()
            assert isinstance(content, bytes)
            assert len(content) > 0
    
    def test_generate_users_report_with_error(self, excel_generator):
        """Test generate_users_report with error."""
        with patch.object(excel_generator, '_create_workbook', side_effect=Exception("Error")):
            with pytest.raises(Exception):
                excel_generator.generate_users_report()
    
    def test_generate_users_report_empty_content(self, excel_generator):
        """Test generate_users_report with empty content."""
        with patch.object(excel_generator, '_save_to_buffer', return_value=b''):
            with pytest.raises(ValueError):
                excel_generator.generate_users_report()
    
    def test_generate_users_report_small_content(self, excel_generator):
        """Test generate_users_report with small content."""
        with patch.object(excel_generator, '_save_to_buffer', return_value=b'x' * 50):
            with pytest.raises(ValueError):
                excel_generator.generate_users_report()

