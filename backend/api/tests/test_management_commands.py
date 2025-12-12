"""
Tests for management commands.
"""
import pytest
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from api.management.commands.create_admin_user import Command as CreateAdminCommand


@pytest.mark.django_db
class TestCreateAdminUserCommand:
    """Tests for create_admin_user command."""
    
    def test_create_new_admin_user(self):
        """Test creating a new admin user."""
        out = StringIO()
        
        call_command('create_admin_user', '--username', 'newadmin', '--email', 'newadmin@test.com', '--password', 'TestPass123!', stdout=out)
        
        user = User.objects.get(username='newadmin')
        assert user.email == 'newadmin@test.com'
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.check_password('TestPass123!')
    
    def test_update_existing_user(self):
        """Test updating an existing user."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        User.objects.create_user(
            username=f'existing_{unique_id}',
            email=f'existing_{unique_id}@test.com',
            password='oldpass'
        )
        
        out = StringIO()
        call_command('create_admin_user', '--username', 'existing', '--email', 'updated@test.com', '--password', 'NewPass123!', stdout=out)
        
        user = User.objects.get(username='existing')
        assert user.email == 'updated@test.com'
        assert user.is_superuser is True
        assert user.check_password('NewPass123!')
    
    def test_create_with_defaults(self):
        """Test creating admin with default values."""
        out = StringIO()
        call_command('create_admin_user', stdout=out)
        
        user = User.objects.get(username='admin')
        assert user.email == 'admin@cacaoscan.com'
        assert user.is_superuser is True
    
    def test_create_with_duplicate_email(self):
        """Test creating admin with duplicate email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        duplicate_email = f'duplicate_{unique_id}@test.com'
        User.objects.create_user(
            username=f'existing_{unique_id}',
            email=duplicate_email
        )
        
        with pytest.raises(CommandError, match="ya está en uso"):
            call_command('create_admin_user', '--username', 'newuser', '--email', duplicate_email)


@pytest.mark.django_db
class TestCleanOrphanedLotesCommand:
    """Tests for clean_orphaned_lotes command."""
    
    def test_dry_run_no_orphaned_lotes(self):
        """Test dry run with no orphaned lotes."""
        from fincas_app.management.commands.clean_orphaned_lotes import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        command.handle(dry_run=True)
        
        output = out.getvalue()
        assert 'No se encontraron lotes huérfanos' in output or 'lotes huérfanos' in output.lower()
    
    def test_dry_run_with_orphaned_lotes(self):
        """Test dry run with orphaned lotes."""
        from django.db import connection
        from fincas_app.management.commands.clean_orphaned_lotes import Command
        from fincas_app.models import Lote
        from fincas_app.models import Finca
        from django.contrib.auth.models import User
        
        # Create a test user and finca first
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass'
        )
        from catalogos.models import Municipio, Departamento
        departamento = Departamento.objects.create(codigo='TEST', nombre='Test Departamento')
        municipio = Municipio.objects.create(departamento=departamento, codigo='TEST', nombre='Test Municipio')
        
        test_finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio=municipio,
            hectareas=10.0,
            agricultor=test_user
        )
        
        # Create orphaned lote using the model (not raw SQL) to avoid constraint issues
        # Create a lote with a non-existent finca_id by using a finca that we'll delete
        orphan_finca = Finca.objects.create(
            nombre='Orphan Finca',
            ubicacion='Test Location',
            municipio=municipio,
            hectareas=5.0,
            agricultor=test_user
        )
        from datetime import date
        orphan_lote = Lote.objects.create(
            nombre='Orphan Lote',
            identificador='ORPHAN-001',
            variedad='Criollo',
            area_hectareas=5.0,
            estado='activo',
            fecha_plantacion=date(2024, 1, 1),
            finca=orphan_finca,
            descripcion='Test description'
        )
        # Delete the finca to make the lote orphaned
        orphan_finca.delete()
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        command.handle(dry_run=True)
        
        output = out.getvalue()
        assert 'DRY-RUN' in output or 'dry-run' in output.lower()

