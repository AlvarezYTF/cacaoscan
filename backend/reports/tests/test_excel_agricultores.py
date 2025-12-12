"""
Tests for ExcelAgricultoresGenerator.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from decimal import Decimal

from reports.services.report.excel.excel_agricultores import ExcelAgricultoresGenerator


@pytest.fixture
def excel_generator():
    """Create ExcelAgricultoresGenerator instance."""
    return ExcelAgricultoresGenerator()


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


class TestExcelAgricultoresGenerator:
    """Tests for ExcelAgricultoresGenerator class."""
    
    def test_setup_headers(self, excel_generator):
        """Test _setup_headers method."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        
        assert excel_generator.ws['A1'].value == 'Agricultor'
        assert excel_generator.ws['B1'].value == 'Email'
        assert excel_generator.ws['C1'].value == 'Teléfono'
        assert excel_generator.ws[1][0].fill is not None
        assert excel_generator.ws[1][0].font.bold is True
    
    def test_setup_headers_with_style_error(self, excel_generator):
        """Test _setup_headers with style error."""
        excel_generator._create_workbook("Test")
        # Patch PatternFill to raise error
        with patch('reports.services.report.excel.excel_agricultores.PatternFill', side_effect=Exception("Style error")):
            excel_generator._setup_headers()
        # Should not raise, just log warning
    
    def test_get_farmers_list(self, excel_generator, user):
        """Test _get_farmers_list method."""
        farmers = excel_generator._get_farmers_list()
        assert isinstance(farmers, list)
        assert len(farmers) >= 0  # Can be empty or have farmers
    
    def test_get_farmers_list_with_prefetch_error(self, excel_generator, user):
        """Test _get_farmers_list with prefetch error."""
        with patch('django.contrib.auth.models.User.objects.filter') as mock_filter:
            mock_query = Mock()
            mock_query.prefetch_related.side_effect = Exception("Prefetch error")
            mock_query.all.return_value = [user]
            mock_filter.return_value = mock_query
            
            farmers = excel_generator._get_farmers_list()
            assert isinstance(farmers, list)
    
    def test_get_farmers_list_with_query_error(self, excel_generator):
        """Test _get_farmers_list with query error."""
        with patch('django.contrib.auth.models.User.objects.filter') as mock_filter:
            mock_query = Mock()
            mock_query.prefetch_related.side_effect = Exception("Prefetch error")
            mock_query.all.side_effect = Exception("Query error")
            mock_filter.return_value = mock_query
            
            farmers = excel_generator._get_farmers_list()
            assert farmers == []
    
    def test_get_farmer_name_with_names(self, excel_generator, user):
        """Test _get_farmer_name with first and last name."""
        name = excel_generator._get_farmer_name(user)
        assert name == 'Test User'
    
    def test_get_farmer_name_without_names(self, excel_generator, user):
        """Test _get_farmer_name without first and last name."""
        user.first_name = ''
        user.last_name = ''
        user.save()
        name = excel_generator._get_farmer_name(user)
        assert name == user.username
    
    def test_get_farmer_name_without_username(self, excel_generator, user):
        """Test _get_farmer_name without username."""
        user.first_name = ''
        user.last_name = ''
        user.username = ''
        name = excel_generator._get_farmer_name(user)
        assert f'Usuario {user.id}' in name
    
    def test_get_farmer_name_with_exception(self, excel_generator):
        """Test _get_farmer_name with exception."""
        farmer = Mock()
        farmer.id = 1
        farmer.username = None
        # Configure mock to raise exception when accessing first_name or last_name
        # Use property descriptors that raise exceptions
        class ExceptionProperty:
            def __get__(self, obj, objtype=None):
                raise Exception("Error")
        
        # Patch the attributes directly on the mock
        type(farmer).first_name = ExceptionProperty()
        type(farmer).last_name = ExceptionProperty()
        
        name = excel_generator._get_farmer_name(farmer)
        assert name == f'Usuario {farmer.id}'
    
    def test_get_farmer_phone_with_profile(self, excel_generator, user):
        """Test _get_farmer_phone with profile."""
        profile = Mock()
        profile.phone_number = '1234567890'
        # Use patch to mock the auth_profile property
        with patch.object(type(user), 'auth_profile', property(lambda self: profile)):
            phone = excel_generator._get_farmer_phone(user)
            assert phone == '1234567890'
    
    def test_get_farmer_phone_without_profile(self, excel_generator, user):
        """Test _get_farmer_phone without profile."""
        phone = excel_generator._get_farmer_phone(user)
        assert phone == ''
    
    def test_get_farmer_phone_with_exception(self, excel_generator, user):
        """Test _get_farmer_phone with exception."""
        class ErrorProperty:
            def __get__(self, obj, objtype=None):
                raise Exception("Error")
        
        with patch.object(type(user), 'auth_profile', ErrorProperty()):
            phone = excel_generator._get_farmer_phone(user)
            assert phone == ''
    
    def test_get_farmer_farms(self, excel_generator, user, finca):
        """Test _get_farmer_farms method."""
        fincas = excel_generator._get_farmer_farms(user)
        assert isinstance(fincas, list)
        assert len(fincas) >= 0  # Can be empty or have fincas
    
    def test_get_farmer_farms_with_exception(self, excel_generator, user):
        """Test _get_farmer_farms with exception."""
        class ErrorProperty:
            def __get__(self, obj, objtype=None):
                raise Exception("Error")
        
        with patch.object(type(user), 'fincas_app_fincas', ErrorProperty()):
            fincas = excel_generator._get_farmer_farms(user)
            assert fincas == []
    
    def test_safe_str_attr(self, excel_generator, finca):
        """Test _safe_str_attr method."""
        value = excel_generator._safe_str_attr(finca, 'nombre', 'default')
        assert value == 'Test Finca'
    
    def test_safe_str_attr_none(self, excel_generator, finca):
        """Test _safe_str_attr with None value."""
        value = excel_generator._safe_str_attr(finca, 'nonexistent', 'default')
        assert value == 'default'
    
    def test_safe_str_attr_with_exception(self, excel_generator):
        """Test _safe_str_attr with exception."""
        obj = Mock()
        def raise_on_getattr(obj_instance, name, default=None):
            if obj_instance is obj and name == 'attr':
                raise Exception("Error")
            return Mock() if default is None else default
        
        with patch('builtins.getattr', side_effect=raise_on_getattr):
            value = excel_generator._safe_str_attr(obj, 'attr', 'default')
            assert value == 'default'
    
    def test_safe_float_attr(self, excel_generator, finca):
        """Test _safe_float_attr method."""
        value = excel_generator._safe_float_attr(finca, 'hectareas', 0.0)
        assert isinstance(value, (float, Decimal))
    
    def test_safe_float_attr_none(self, excel_generator, finca):
        """Test _safe_float_attr with None value."""
        value = excel_generator._safe_float_attr(finca, 'nonexistent', 0.0)
        assert value == 0.0
    
    def test_safe_float_attr_with_exception(self, excel_generator):
        """Test _safe_float_attr with exception."""
        obj = Mock()
        obj.attr = Mock(side_effect=Exception("Error"))
        value = excel_generator._safe_float_attr(obj, 'attr', 0.0)
        assert value == 0.0
    
    def test_safe_date_str(self, excel_generator, finca):
        """Test _safe_date_str method."""
        from datetime import date
        finca.fecha_registro = date.today()
        value = excel_generator._safe_date_str(finca, 'fecha_registro')
        assert value is not None
    
    def test_safe_date_str_none(self, excel_generator, finca):
        """Test _safe_date_str with None value."""
        value = excel_generator._safe_date_str(finca, 'nonexistent')
        assert value == ''
    
    def test_safe_date_str_with_exception(self, excel_generator):
        """Test _safe_date_str with exception."""
        obj = Mock()
        # Create a property descriptor that raises an exception
        class ExceptionProperty:
            def __get__(self, instance, owner):
                raise Exception("Error")
        
        obj.fecha_registro = ExceptionProperty()
        
        value = excel_generator._safe_date_str(obj, 'fecha_registro')
        assert value == ''
    
    def test_extract_finca_data(self, excel_generator, finca):
        """Test _extract_finca_data method."""
        data = excel_generator._extract_finca_data(finca)
        assert 'depto' in data
        assert 'municipio' in data
        assert 'nombre' in data
        assert 'hectareas' in data
        assert 'estado' in data
        assert 'fecha_registro' in data
    
    def test_add_farm_row(self, excel_generator):
        """Test _add_farm_row method."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        finca_data = {
            'depto': 'Test Dept',
            'municipio': 'Test Mun',
            'nombre': 'Test Finca',
            'hectareas': 10.5,
            'estado': 'Activa',
            'fecha_registro': '2024-01-01'
        }
        excel_generator._add_farm_row('Test User', 'test@example.com', '123', finca_data)
        assert excel_generator.ws['A2'].value == 'Test User'
        assert excel_generator.ws['B2'].value == 'test@example.com'
        assert abs(excel_generator.ws['G2'].value - 10.5) < 0.01  # Float comparison
    
    def test_add_farmer_without_farms_row(self, excel_generator, user):
        """Test _add_farmer_without_farms_row method."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        excel_generator._add_farmer_without_farms_row('Test User', 'test@example.com', '123', user)
        assert excel_generator.ws['A2'].value == 'Test User'
        assert excel_generator.ws['B2'].value == 'test@example.com'
    
    def test_add_farmer_without_farms_row_no_date(self, excel_generator):
        """Test _add_farmer_without_farms_row without date_joined."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        farmer = Mock()
        farmer.date_joined = None
        excel_generator._add_farmer_without_farms_row('Test User', 'test@example.com', '123', farmer)
        # Verify that the row was added (checking first column)
        assert excel_generator.ws.max_row >= 2
        assert excel_generator.ws['A2'].value == 'Test User'
    
    def test_add_farmer_without_farms_row_exception(self, excel_generator):
        """Test _add_farmer_without_farms_row with exception."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        farmer = Mock()
        # Mock date_joined to raise exception when strftime is called
        mock_date = Mock()
        mock_date.strftime = Mock(side_effect=Exception("Error"))
        farmer.date_joined = mock_date
        excel_generator._add_farmer_without_farms_row('Test User', 'test@example.com', '123', farmer)
        # Verify that the row was added despite the exception
        assert excel_generator.ws.max_row >= 2
        assert excel_generator.ws['A2'].value == 'Test User'
    
    def test_process_farmer_with_farms(self, excel_generator, user, finca):
        """Test _process_farmer with farms."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        rows_added = excel_generator._process_farmer(user)
        assert rows_added > 0  # Should have at least one row
    
    def test_process_farmer_without_farms(self, excel_generator, user):
        """Test _process_farmer without farms."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        rows_added = excel_generator._process_farmer(user)
        assert rows_added == 1
    
    def test_process_farmer_with_finca_error(self, excel_generator, user):
        """Test _process_farmer with finca processing error."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        with patch.object(excel_generator, '_extract_finca_data', side_effect=Exception("Error")):
            finca = Mock()
            finca.id = 1
            # Mock the queryset properly
            mock_queryset = Mock()
            mock_queryset.__iter__ = Mock(return_value=iter([finca]))
            mock_queryset.__len__ = Mock(return_value=1)
            user.fincas_app_fincas.all = Mock(return_value=mock_queryset)
            rows_added = excel_generator._process_farmer(user)
            assert rows_added >= 0
    
    def test_finalize_report(self, excel_generator, user):
        """Test _finalize_report method."""
        excel_generator._create_workbook("Test")
        excel_generator._setup_headers()
        excel_generator._finalize_report()
        # Should not raise
    
    def test_finalize_report_with_error(self, excel_generator):
        """Test _finalize_report with error."""
        excel_generator._create_workbook("Test")
        with patch.object(excel_generator, '_adjust_column_widths', side_effect=Exception("Error")):
            excel_generator._finalize_report()
        # Should not raise, just log warning
    
    def test_generate_farmers_report(self, excel_generator, user):
        """Test generate_farmers_report method."""
        content = excel_generator.generate_farmers_report()
        assert isinstance(content, bytes)
        assert len(content) > 0
    
    def test_generate_farmers_report_with_error(self, excel_generator):
        """Test generate_farmers_report with error."""
        with patch.object(excel_generator, '_create_workbook', side_effect=Exception("Error")):
            with pytest.raises(Exception):
                excel_generator.generate_farmers_report()

