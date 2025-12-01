"""
Unit tests for fix_lote_foreign_key management command.
Tests Django management command for fixing lote foreign key constraints.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from decimal import Decimal

from fincas_app.management.commands.fix_lote_foreign_key import Command


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
class TestFixLoteForeignKeyCommand:
    """Tests for fix_lote_foreign_key Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_validate_sql_identifier_valid(self, command):
        """Test validation of valid SQL identifier."""
        result = command._validate_sql_identifier('valid_identifier')
        assert result == 'valid_identifier'
    
    def test_validate_sql_identifier_starts_with_letter(self, command):
        """Test validation of identifier starting with letter."""
        result = command._validate_sql_identifier('validIdentifier')
        assert result == 'validIdentifier'
    
    def test_validate_sql_identifier_starts_with_underscore(self, command):
        """Test validation of identifier starting with underscore."""
        result = command._validate_sql_identifier('_valid_identifier')
        assert result == '_valid_identifier'
    
    def test_validate_sql_identifier_empty(self, command):
        """Test validation of empty identifier."""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            command._validate_sql_identifier('')
    
    def test_validate_sql_identifier_none(self, command):
        """Test validation of None identifier."""
        with pytest.raises(ValueError, match="debe ser una cadena de texto"):
            command._validate_sql_identifier(None)
    
    def test_validate_sql_identifier_too_long(self, command):
        """Test validation of identifier that's too long."""
        long_id = 'a' * 64  # 64 characters, exceeds 63 limit
        with pytest.raises(ValueError, match="demasiado largo"):
            command._validate_sql_identifier(long_id)
    
    def test_validate_sql_identifier_invalid_chars(self, command):
        """Test validation of identifier with invalid characters."""
        with pytest.raises(ValueError, match="inválido"):
            command._validate_sql_identifier('invalid-identifier')
    
    def test_validate_sql_identifier_starts_with_number(self, command):
        """Test validation of identifier starting with number."""
        with pytest.raises(ValueError, match="inválido"):
            command._validate_sql_identifier('123invalid')
    
    def test_find_foreign_keys(self, command, db):
        """Test finding foreign keys."""
        with connection.cursor() as cursor:
            fks = command._find_foreign_keys(cursor)
            # Should return list (may be empty)
            assert isinstance(fks, list)
    
    def test_verify_api_finca_exists_true(self, command, db):
        """Test verifying api_finca exists when it does."""
        with connection.cursor() as cursor:
            result = command._verify_api_finca_exists(cursor)
            assert result is True
    
    def test_verify_api_finca_exists_false(self, command, db):
        """Test verifying api_finca exists when it doesn't."""
        with connection.cursor() as cursor:
            with patch.object(cursor, 'fetchone', return_value=None):
                result = command._verify_api_finca_exists(cursor)
                assert result is False
    
    def test_drop_incorrect_foreign_key_success(self, command, db):
        """Test dropping incorrect foreign key successfully."""
        with connection.cursor() as cursor:
            constraint_name = 'test_constraint'
            
            with patch.object(command, '_validate_sql_identifier', return_value=constraint_name):
                with patch.object(cursor, 'execute'):
                    result = command._drop_incorrect_foreign_key(cursor, constraint_name)
                    assert result is True
    
    def test_drop_incorrect_foreign_key_invalid_name(self, command, db):
        """Test dropping foreign key with invalid name."""
        with connection.cursor() as cursor:
            constraint_name = 'invalid-constraint'
            
            with patch.object(command, '_validate_sql_identifier', side_effect=ValueError("Invalid")):
                result = command._drop_incorrect_foreign_key(cursor, constraint_name)
                assert result is False
    
    def test_drop_incorrect_foreign_key_exception(self, command, db):
        """Test dropping foreign key when exception occurs."""
        with connection.cursor() as cursor:
            constraint_name = 'test_constraint'
            
            with patch.object(command, '_validate_sql_identifier', return_value=constraint_name):
                with patch.object(cursor, 'execute', side_effect=Exception("DB error")):
                    result = command._drop_incorrect_foreign_key(cursor, constraint_name)
                    assert result is False
    
    def test_create_correct_foreign_key_success(self, command, db):
        """Test creating correct foreign key successfully."""
        with connection.cursor() as cursor:
            constraint_name = 'test_fk_constraint'
            
            with patch.object(command, '_validate_sql_identifier', return_value=constraint_name):
                with patch.object(cursor, 'fetchone', return_value=None):  # FK doesn't exist
                    with patch.object(cursor, 'execute'):
                        result = command._create_correct_foreign_key(cursor, constraint_name)
                        assert result is True
    
    def test_create_correct_foreign_key_already_exists(self, command, db):
        """Test creating foreign key when it already exists."""
        with connection.cursor() as cursor:
            constraint_name = 'existing_fk_constraint'
            
            with patch.object(command, '_validate_sql_identifier', return_value=constraint_name):
                with patch.object(cursor, 'fetchone', return_value=('existing_fk_constraint',)):  # FK exists
                    result = command._create_correct_foreign_key(cursor, constraint_name)
                    assert result is False
    
    def test_create_correct_foreign_key_invalid_name(self, command, db):
        """Test creating foreign key with invalid name."""
        with connection.cursor() as cursor:
            constraint_name = 'invalid-constraint'
            
            with patch.object(command, '_validate_sql_identifier', side_effect=ValueError("Invalid")):
                result = command._create_correct_foreign_key(cursor, constraint_name)
                assert result is False
    
    def test_fix_incorrect_foreign_key_wrong_table(self, command, db):
        """Test fixing foreign key pointing to wrong table."""
        with connection.cursor() as cursor:
            constraint_name = 'test_constraint'
            foreign_table = 'wrong_table'  # Not fincas_app_finca
            
            result = command._fix_incorrect_foreign_key(cursor, constraint_name, foreign_table)
            assert result is False
    
    def test_fix_incorrect_foreign_key_correct_table(self, command, db):
        """Test fixing foreign key pointing to fincas_app_finca."""
        with connection.cursor() as cursor:
            constraint_name = 'test_constraint'
            foreign_table = 'fincas_app_finca'
            
            with patch.object(command, '_drop_incorrect_foreign_key', return_value=True):
                with patch.object(command, '_create_correct_foreign_key', return_value=True):
                    result = command._fix_incorrect_foreign_key(cursor, constraint_name, foreign_table)
                    assert result is True
    
    def test_handle_orphaned_lotes_no_orphans(self, command, db, test_finca):
        """Test handling orphaned lotes when none exist."""
        from fincas_app.models import Lote
        
        lote = Lote.objects.create(
            finca=test_finca,
            nombre='Valid Lote',
            area=Decimal('5.0')
        )
        
        with connection.cursor() as cursor:
            command._handle_orphaned_lotes(cursor)
            
            # Should complete without errors
            assert True
    
    def test_handle_orphaned_lotes_with_orphans(self, command, db):
        """Test handling orphaned lotes when they exist."""
        # Create orphaned lote
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, identificador, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES (99999, 'Orphaned Lote', 'L001', 5.0, 'activo', NOW(), NOW())
            """)
        
        with connection.cursor() as cursor:
            command._handle_orphaned_lotes(cursor)
            
            # Should complete and handle orphaned lotes
            assert True
    
    def test_verify_final_state_all_correct(self, command, db):
        """Test verifying final state when all FKs are correct."""
        # Mock FK pointing to correct table
        mock_fk = ('test_constraint', 'api_finca')
        
        with connection.cursor() as cursor:
            with patch.object(cursor, 'fetchall', return_value=[mock_fk]):
                result = command._verify_final_state(cursor)
                assert result is True
    
    def test_verify_final_state_incorrect_fk(self, command, db):
        """Test verifying final state when incorrect FK exists."""
        # Mock FK pointing to wrong table
        mock_fk = ('test_constraint', 'wrong_table')
        
        with connection.cursor() as cursor:
            with patch.object(cursor, 'fetchall', return_value=[mock_fk]):
                result = command._verify_final_state(cursor)
                assert result is False
    
    def test_handle_no_foreign_keys_found(self, command, db):
        """Test handle when no foreign keys are found."""
        with connection.cursor() as cursor:
            with patch.object(command, '_find_foreign_keys', return_value=[]):
                command.handle()
                
                # Should complete with warning
                assert True
    
    def test_handle_api_finca_not_exists(self, command, db):
        """Test handle when api_finca table doesn't exist."""
        mock_fk = ('test_constraint', 'fincas_app_lote', 'finca_id', 'wrong_table', 'id')
        
        with connection.cursor() as cursor:
            with patch.object(command, '_find_foreign_keys', return_value=[mock_fk]):
                with patch.object(command, '_verify_api_finca_exists', return_value=False):
                    command.handle()
                    
                    # Should complete with error message
                    assert True
    
    def test_handle_correct_foreign_key(self, command, db):
        """Test handle when foreign key is already correct."""
        mock_fk = ('test_constraint', 'fincas_app_lote', 'finca_id', 'api_finca', 'id')
        
        with connection.cursor() as cursor:
            with patch.object(command, '_find_foreign_keys', return_value=[mock_fk]):
                with patch.object(command, '_verify_api_finca_exists', return_value=True):
                    with patch.object(command, '_handle_orphaned_lotes'):
                        with patch.object(command, '_verify_final_state', return_value=True):
                            command.handle()
                            
                            # Should complete successfully
                            assert True
    
    def test_handle_incorrect_foreign_key_fixed(self, command, db):
        """Test handle when incorrect foreign key is fixed."""
        mock_fk = ('test_constraint', 'fincas_app_lote', 'finca_id', 'fincas_app_finca', 'id')
        
        with connection.cursor() as cursor:
            with patch.object(command, '_find_foreign_keys', return_value=[mock_fk]):
                with patch.object(command, '_verify_api_finca_exists', return_value=True):
                    with patch.object(command, '_fix_incorrect_foreign_key', return_value=True):
                        with patch.object(command, '_handle_orphaned_lotes'):
                            with patch.object(command, '_verify_final_state', return_value=True):
                                command.handle()
                                
                                # Should complete successfully
                                assert True

