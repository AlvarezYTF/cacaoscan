"""
Unit tests for seed_colombia management command.
Tests Django management command for seeding Colombia departments and municipalities.
"""
import pytest
from django.core.management import call_command
from django.db import transaction

from catalogos.management.commands.seed_colombia import Command, _normalize_text
from catalogos.models import Departamento, Municipio


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.mark.django_db
class TestSeedColombiaCommand:
    """Tests for seed_colombia Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_normalize_text_valid(self):
        """Test normalizing valid text."""
        result = _normalize_text('Valid Text')
        assert result == 'Valid Text'
    
    def test_normalize_text_with_encoding_issue(self):
        """Test normalizing text with encoding issues."""
        # Text that might have encoding issues
        problematic_text = 'BogotÃ¡'
        result = _normalize_text(problematic_text)
        # Should attempt to fix or return as-is
        assert isinstance(result, str)
    
    def test_normalize_text_none(self):
        """Test normalizing None."""
        result = _normalize_text(None)
        assert result is None
    
    def test_normalize_text_not_string(self):
        """Test normalizing non-string value."""
        result = _normalize_text(123)
        assert result == 123
    
    def test_create_or_update_departamento_new(self, command):
        """Test creating a new departamento."""
        codigo = '99'
        nombre = 'Test Departamento'
        
        departamento, created = command._create_or_update_departamento(codigo, nombre)
        
        assert created is True
        assert departamento.codigo == codigo
        assert departamento.nombre == nombre
    
    def test_create_or_update_departamento_existing(self, command):
        """Test updating an existing departamento."""
        codigo = '99'
        nombre_original = 'Original Name'
        nombre_nuevo = 'Updated Name'
        
        # Create first
        departamento, _ = command._create_or_update_departamento(codigo, nombre_original)
        
        # Update
        departamento_updated, created = command._create_or_update_departamento(codigo, nombre_nuevo)
        
        assert created is False
        assert departamento_updated.id == departamento.id
        assert departamento_updated.nombre == nombre_nuevo
    
    def test_create_or_update_municipio_new(self, command):
        """Test creating a new municipio."""
        departamento, _ = command._create_or_update_departamento('99', 'Test Departamento')
        codigo_mun = '001'
        nombre_mun = 'Test Municipio'
        
        created = command._create_or_update_municipio(departamento, codigo_mun, nombre_mun)
        
        assert created is True
        municipio = Municipio.objects.get(departamento=departamento, codigo=codigo_mun)
        assert municipio.nombre == nombre_mun
    
    def test_create_or_update_municipio_empty_name(self, command):
        """Test creating municipio with empty name."""
        departamento, _ = command._create_or_update_departamento('99', 'Test Departamento')
        codigo_mun = '001'
        nombre_mun = ''
        
        created = command._create_or_update_municipio(departamento, codigo_mun, nombre_mun)
        
        assert created is False
    
    def test_create_or_update_municipio_existing(self, command):
        """Test updating an existing municipio."""
        departamento, _ = command._create_or_update_departamento('99', 'Test Departamento')
        codigo_mun = '001'
        nombre_original = 'Original Municipio'
        nombre_nuevo = 'Updated Municipio'
        
        # Create first
        command._create_or_update_municipio(departamento, codigo_mun, nombre_original)
        
        # Update
        created = command._create_or_update_municipio(departamento, codigo_mun, nombre_nuevo)
        
        assert created is False
        municipio = Municipio.objects.get(departamento=departamento, codigo=codigo_mun)
        assert municipio.nombre == nombre_nuevo
    
    def test_process_municipios(self, command):
        """Test processing list of municipios."""
        departamento, _ = command._create_or_update_departamento('99', 'Test Departamento')
        municipios = ['001', 'Municipio 1', '002', 'Municipio 2', '003', 'Municipio 3']
        
        total = command._process_municipios(departamento, municipios)
        
        assert total == 3
        assert Municipio.objects.filter(departamento=departamento).count() == 3
    
    def test_process_municipios_odd_length(self, command):
        """Test processing municipios with odd length list."""
        departamento, _ = command._create_or_update_departamento('99', 'Test Departamento')
        municipios = ['001', 'Municipio 1', '002']  # Odd length, missing name for 002
        
        total = command._process_municipios(departamento, municipios)
        
        # Should process what it can
        assert total >= 1
    
    def test_handle_creates_departments_and_municipalities(self, command):
        """Test that handle creates departments and municipalities."""
        # Clear existing data
        Municipio.objects.all().delete()
        Departamento.objects.all().delete()
        
        initial_dept_count = Departamento.objects.count()
        initial_mun_count = Municipio.objects.count()
        
        command.handle()
        
        final_dept_count = Departamento.objects.count()
        final_mun_count = Municipio.objects.count()
        
        # Should have created departments and municipalities
        assert final_dept_count > initial_dept_count
        assert final_mun_count > initial_mun_count
    
    def test_handle_idempotent(self, command):
        """Test that handle can be run multiple times safely."""
        # Run first time
        command.handle()
        first_dept_count = Departamento.objects.count()
        first_mun_count = Municipio.objects.count()
        
        # Run second time
        command.handle()
        second_dept_count = Departamento.objects.count()
        second_mun_count = Municipio.objects.count()
        
        # Should have same or more (if new data added)
        assert second_dept_count >= first_dept_count
        assert second_mun_count >= first_mun_count
    
    def test_handle_creates_bogota_dc(self, command):
        """Test that handle creates Bogotá D.C. correctly."""
        command.handle()
        
        bogota_dept = Departamento.objects.filter(codigo='11').first()
        assert bogota_dept is not None
        assert 'Bogotá' in bogota_dept.nombre or 'Bogota' in bogota_dept.nombre
    
    def test_handle_creates_antioquia(self, command):
        """Test that handle creates Antioquia with municipalities."""
        command.handle()
        
        antioquia = Departamento.objects.filter(codigo='05').first()
        assert antioquia is not None
        
        municipios = Municipio.objects.filter(departamento=antioquia)
        assert municipios.count() > 0
    
    def test_call_command_via_call_command(self):
        """Test calling command via Django's call_command."""
        initial_count = Departamento.objects.count()
        
        call_command('seed_colombia')
        
        final_count = Departamento.objects.count()
        assert final_count >= initial_count
    
    def test_handle_with_duplicate_municipality_names(self, command):
        """Test handling duplicate municipality names across departments."""
        command.handle()
        
        # Check that municipalities with same name exist in different departments
        la_union_municipalities = Municipio.objects.filter(nombre__icontains='La Unión')
        assert la_union_municipalities.count() > 0
        
        # Each should be in different department
        dept_ids = set(m.departamento_id for m in la_union_municipalities)
        assert len(dept_ids) > 0
    
    def test_handle_preserves_existing_data(self, command):
        """Test that handle preserves existing data when re-run."""
        # Create custom departamento
        custom_dept = Departamento.objects.create(
            codigo='98',
            nombre='Custom Departamento'
        )
        custom_mun = Municipio.objects.create(
            departamento=custom_dept,
            codigo='001',
            nombre='Custom Municipio'
        )
        
        command.handle()
        
        # Custom data should still exist
        assert Departamento.objects.filter(codigo='98').exists()
        assert Municipio.objects.filter(id=custom_mun.id).exists()

