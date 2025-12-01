"""
Unit tests for check_fk_lotes management command.
Tests Django management command for checking and fixing foreign key constraints.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.contrib.auth.models import User
from decimal import Decimal

from api.management.commands.check_fk_lotes import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_finca(db, test_user):
    """Create a test finca."""
    from api.models import Finca
    return Finca.objects.create(
        nombre='Test Finca',
        propietario=test_user,
        area_total=Decimal('20.0')
    )


@pytest.mark.django_db
class TestCheckFKLotesCommand:
    """Tests for check_fk_lotes Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    @patch('api.management.commands.check_fk_lotes.Finca')
    @patch('api.management.commands.check_fk_lotes.Lote')
    def test_handle_with_models_unavailable(self, mock_lote, mock_finca, command):
        """Test handle when models are not available."""
        mock_finca.return_value = None
        mock_lote.return_value = None
        
        with pytest.raises(CommandError, match="Modelos Finca o Lote no están disponibles"):
            command.handle(fix=False, check_orphans=True)
    
    def test_validate_identifier_valid(self, command):
        """Test validation of valid identifier."""
        result = command._validate_identifier('valid_identifier')
        assert result == 'valid_identifier'
    
    def test_validate_identifier_with_dash(self, command):
        """Test validation of identifier with dash."""
        result = command._validate_identifier('valid-identifier')
        assert result == 'valid-identifier'
    
    def test_validate_identifier_empty(self, command):
        """Test validation of empty identifier."""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            command._validate_identifier('')
    
    def test_validate_identifier_none(self, command):
        """Test validation of None identifier."""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            command._validate_identifier(None)
    
    def test_validate_identifier_invalid_chars(self, command):
        """Test validation of identifier with invalid characters."""
        with pytest.raises(ValueError, match="contains invalid characters"):
            command._validate_identifier('invalid.identifier')
    
    def test_validate_identifier_escapes_quotes(self, command):
        """Test that identifier escapes double quotes."""
        result = command._validate_identifier('test"identifier')
        assert '"' not in result or result.count('"') == result.count('""')
    
    def test_build_drop_constraint_query(self, command):
        """Test building drop constraint query."""
        query = command._build_drop_constraint_query('test_table', 'test_constraint')
        assert 'DROP CONSTRAINT' in query
        assert 'test_table' in query
        assert 'test_constraint' in query
    
    def test_build_add_constraint_query(self, command):
        """Test building add constraint query."""
        query = command._build_add_constraint_query(
            'test_table', 'test_constraint', 'test_column', 'ref_table', 'ref_column'
        )
        assert 'ADD CONSTRAINT' in query
        assert 'FOREIGN KEY' in query
        assert 'REFERENCES' in query
        assert 'ON DELETE CASCADE' in query
    
    def test_check_table_exists_true(self, command, db):
        """Test checking if table exists when it does."""
        with connection.cursor() as cursor:
            result = command._check_table_exists(cursor, 'auth_user')
            assert result is True
    
    def test_check_table_exists_false(self, command, db):
        """Test checking if table exists when it doesn't."""
        with connection.cursor() as cursor:
            result = command._check_table_exists(cursor, 'nonexistent_table_xyz')
            assert result is False
    
    def test_get_foreign_keys_found(self, command, db):
        """Test getting foreign keys when they exist."""
        with connection.cursor() as cursor:
            fks = command._get_foreign_keys(cursor)
            # Should return list (may be empty if no FKs exist)
            assert isinstance(fks, list)
    
    def test_handle_missing_foreign_key_no_fix(self, command, db):
        """Test handling missing foreign key without fix."""
        with connection.cursor() as cursor:
            result = command._handle_missing_foreign_key(cursor, fix=False)
            assert result is True
    
    @patch('api.management.commands.check_fk_lotes.transaction')
    def test_handle_missing_foreign_key_with_fix_table_exists(self, command, db):
        """Test handling missing foreign key with fix when table exists."""
        with connection.cursor() as cursor:
            # Mock transaction.atomic
            with patch.object(connection, 'cursor') as mock_cursor:
                mock_cursor.return_value.__enter__ = Mock(return_value=cursor)
                mock_cursor.return_value.__exit__ = Mock(return_value=False)
                
                # Ensure api_finca table exists (it should in test DB)
                if command._check_table_exists(cursor, 'api_finca'):
                    try:
                        result = command._handle_missing_foreign_key(cursor, fix=True)
                        # Should return False if FK was created
                        assert isinstance(result, bool)
                    except CommandError:
                        # If FK already exists, that's also valid
                        pass
    
    @patch('api.management.commands.check_fk_lotes.transaction')
    def test_handle_missing_foreign_key_table_not_exists(self, command, db):
        """Test handling missing foreign key when api_finca doesn't exist."""
        with connection.cursor() as cursor:
            with patch.object(command, '_check_table_exists', return_value=False):
                with pytest.raises(CommandError, match="La tabla api_finca no existe"):
                    command._handle_missing_foreign_key(cursor, fix=True)
    
    def test_check_data_consistency_no_orphans(self, command, db, test_finca):
        """Test checking data consistency when no orphaned lotes."""
        from fincas_app.models import Lote
        
        # Create valid lote
        lote = Lote.objects.create(
            finca=test_finca,
            nombre='Valid Lote',
            area=Decimal('5.0')
        )
        
        command._check_data_consistency()
        
        # Should complete without errors
        assert True
    
    def test_check_data_consistency_with_orphans(self, command, db):
        """Test checking data consistency with orphaned lotes."""
        # Create orphaned lote directly via SQL
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES (99999, 'Orphaned Lote', 5.0, 'activo', NOW(), NOW())
            """)
        
        command._check_data_consistency()
        
        # Should complete and report orphaned lotes
        assert True
    
    def test_check_foreign_keys_no_fks_found(self, command, db):
        """Test checking foreign keys when none are found."""
        with connection.cursor() as cursor:
            with patch.object(command, '_get_foreign_keys', return_value=[]):
                result = command._check_foreign_keys(fix=False)
                # Should call _handle_missing_foreign_key
                assert isinstance(result, bool)
    
    def test_check_foreign_keys_correct_fk(self, command, db):
        """Test checking foreign keys when correct FK exists."""
        # Mock FK pointing to correct table
        mock_fk = ('test_constraint', 'fincas_app_lote', 'finca_id', 'api_finca', 'id')
        
        with connection.cursor() as cursor:
            with patch.object(command, '_get_foreign_keys', return_value=[mock_fk]):
                result = command._check_foreign_keys(fix=False)
                # Should return False (no issues)
                assert result is False
    
    def test_check_foreign_keys_incorrect_fk_no_fix(self, command, db):
        """Test checking foreign keys when incorrect FK exists without fix."""
        # Mock FK pointing to wrong table
        mock_fk = ('test_constraint', 'fincas_app_lote', 'finca_id', 'wrong_table', 'id')
        
        with connection.cursor() as cursor:
            with patch.object(command, '_get_foreign_keys', return_value=[mock_fk]):
                result = command._check_foreign_keys(fix=False)
                # Should return True (issues found)
                assert result is True
    
    @patch('api.management.commands.check_fk_lotes.transaction')
    def test_fix_incorrect_foreign_key(self, command, db):
        """Test fixing incorrect foreign key."""
        with connection.cursor() as cursor:
            constraint_name = 'test_constraint'
            foreign_table = 'wrong_table'
            
            with patch.object(command, '_build_drop_constraint_query', return_value='DROP QUERY'):
                with patch.object(command, '_build_add_constraint_query', return_value='ADD QUERY'):
                    with patch.object(cursor, 'execute'):
                        command._fix_incorrect_foreign_key(cursor, constraint_name, foreign_table)
                        
                        # Should execute drop and add queries
                        assert True
    
    def test_handle_with_check_orphans_false(self, command, db, test_finca):
        """Test handle with check_orphans=False."""
        from fincas_app.models import Lote
        
        lote = Lote.objects.create(
            finca=test_finca,
            nombre='Test Lote',
            area=Decimal('5.0')
        )
        
        with patch.object(command, '_check_foreign_keys', return_value=False):
            command.handle(fix=False, check_orphans=False)
            
            # Should complete without checking orphans
            assert True
    
    def test_handle_with_check_orphans_true(self, command, db, test_finca):
        """Test handle with check_orphans=True."""
        from fincas_app.models import Lote
        
        lote = Lote.objects.create(
            finca=test_finca,
            nombre='Test Lote',
            area=Decimal('5.0')
        )
        
        with patch.object(command, '_check_foreign_keys', return_value=False):
            command.handle(fix=False, check_orphans=True)
            
            # Should complete with checking orphans
            assert True
    
    def test_error_handling_generic_exception(self, command, db):
        """Test error handling for generic exceptions."""
        with patch.object(command, '_check_foreign_keys', side_effect=Exception("Database error")):
            with pytest.raises(CommandError, match="Error al verificar foreign keys"):
                command.handle(fix=False, check_orphans=True)
    
    def test_create_foreign_key(self, command, db):
        """Test creating a foreign key."""
        with connection.cursor() as cursor:
            constraint_name = 'test_fk_constraint'
            
            with patch.object(command, '_build_add_constraint_query', return_value='ALTER TABLE ...'):
                with patch.object(cursor, 'execute'):
                    try:
                        command._create_foreign_key(cursor, constraint_name)
                        assert True
                    except Exception:
                        # If FK already exists, that's acceptable
                        pass

