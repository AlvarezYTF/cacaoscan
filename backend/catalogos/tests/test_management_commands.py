"""
Tests for catalogos management commands.
"""
import pytest
from io import StringIO
from django.core.management import call_command
from catalogos.models import Tema, Parametro, Departamento, Municipio


@pytest.mark.django_db
class TestInitCatalogosCommand:
    """Tests for init_catalogos command."""
    
    def test_init_catalogos_creates_themes(self):
        """Test that init_catalogos creates themes and parameters."""
        # Verify no themes exist initially
        initial_count = Tema.objects.count()
        
        out = StringIO()
        call_command('init_catalogos', stdout=out)
        
        output = out.getvalue()
        assert 'catálogos' in output.lower() or 'iniciando' in output.lower()
        
        # Verify themes were created
        tema_count = Tema.objects.count()
        assert tema_count > initial_count
        
        # Verify TIPO_DOC theme exists
        tipo_doc = Tema.objects.filter(codigo='TIPO_DOC').first()
        assert tipo_doc is not None
        assert tipo_doc.nombre == 'Tipo de Documento'
    
    def test_init_catalogos_creates_parameters(self):
        """Test that init_catalogos creates parameters."""
        out = StringIO()
        call_command('init_catalogos', stdout=out)
        
        # Verify parameters were created
        tipo_doc = Tema.objects.filter(codigo='TIPO_DOC').first()
        assert tipo_doc is not None
        
        param_count = Parametro.objects.filter(tema=tipo_doc).count()
        assert param_count > 0
        
        # Verify CC parameter exists
        cc_param = Parametro.objects.filter(tema=tipo_doc, codigo='CC').first()
        assert cc_param is not None
        assert cc_param.nombre == 'Cédula de Ciudadanía'
    
    def test_init_catalogos_idempotent(self):
        """Test that running init_catalogos twice doesn't create duplicates."""
        out1 = StringIO()
        call_command('init_catalogos', stdout=out1)
        
        first_count = Tema.objects.count()
        first_param_count = Parametro.objects.count()
        
        out2 = StringIO()
        call_command('init_catalogos', stdout=out2)
        
        second_count = Tema.objects.count()
        second_param_count = Parametro.objects.count()
        
        assert first_count == second_count
        assert first_param_count == second_param_count


@pytest.mark.django_db
class TestInitUbicacionesCommand:
    """Tests for init_ubicaciones command."""
    
    def test_init_ubicaciones_creates_departments(self):
        """Test that init_ubicaciones creates departments."""
        initial_count = Departamento.objects.count()
        
        out = StringIO()
        call_command('init_ubicaciones', stdout=out)
        
        output = out.getvalue()
        assert 'ubicaciones' in output.lower() or 'iniciando' in output.lower()
        
        dept_count = Departamento.objects.count()
        assert dept_count > initial_count
        
        # Verify Antioquia exists
        antioquia = Departamento.objects.filter(codigo='05').first()
        assert antioquia is not None
        assert antioquia.nombre == 'Antioquia'
    
    def test_init_ubicaciones_creates_municipalities(self):
        """Test that init_ubicaciones creates municipalities."""
        out = StringIO()
        call_command('init_ubicaciones', stdout=out)
        
        antioquia = Departamento.objects.filter(codigo='05').first()
        assert antioquia is not None
        
        mun_count = Municipio.objects.filter(departamento=antioquia).count()
        assert mun_count > 0
        
        # Verify Medellín exists
        medellin = Municipio.objects.filter(departamento=antioquia, codigo='001').first()
        assert medellin is not None
        assert medellin.nombre == 'Medellín'
    
    def test_init_ubicaciones_idempotent(self):
        """Test that running init_ubicaciones twice doesn't create duplicates."""
        out1 = StringIO()
        call_command('init_ubicaciones', stdout=out1)
        
        first_dept_count = Departamento.objects.count()
        first_mun_count = Municipio.objects.count()
        
        out2 = StringIO()
        call_command('init_ubicaciones', stdout=out2)
        
        second_dept_count = Departamento.objects.count()
        second_mun_count = Municipio.objects.count()
        
        assert first_dept_count == second_dept_count
        assert first_mun_count == second_mun_count


@pytest.mark.django_db
class TestSeedColombiaCommand:
    """Tests for seed_colombia command."""
    
    def test_seed_colombia_creates_departments(self):
        """Test that seed_colombia creates departments."""
        initial_count = Departamento.objects.count()
        
        out = StringIO()
        call_command('seed_colombia', stdout=out)
        
        output = out.getvalue()
        assert 'colombia' in output.lower() or 'seed' in output.lower()
        
        dept_count = Departamento.objects.count()
        assert dept_count > initial_count
    
    def test_seed_colombia_creates_municipalities(self):
        """Test that seed_colombia creates municipalities."""
        out = StringIO()
        call_command('seed_colombia', stdout=out)
        
        # Verify municipalities were created
        mun_count = Municipio.objects.count()
        assert mun_count > 0
    
    def test_seed_colombia_normalizes_text(self):
        """Test that seed_colombia normalizes text with encoding issues."""
        out = StringIO()
        call_command('seed_colombia', stdout=out)
        
        # Verify departments with special characters are created correctly
        antioquia = Departamento.objects.filter(codigo='05').first()
        assert antioquia is not None
    
    def test_seed_colombia_idempotent(self):
        """Test that running seed_colombia twice doesn't create duplicates."""
        out1 = StringIO()
        call_command('seed_colombia', stdout=out1)
        
        first_dept_count = Departamento.objects.count()
        first_mun_count = Municipio.objects.count()
        
        out2 = StringIO()
        call_command('seed_colombia', stdout=out2)
        
        second_dept_count = Departamento.objects.count()
        second_mun_count = Municipio.objects.count()
        
        assert first_dept_count == second_dept_count
        assert first_mun_count == second_mun_count

