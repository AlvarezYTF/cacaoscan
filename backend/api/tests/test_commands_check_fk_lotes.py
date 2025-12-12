"""
Tests for check_fk_lotes management command.
"""
import pytest
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from django.core.management.base import CommandError
from django.db import connection

from api.management.commands.check_fk_lotes import Command


@pytest.mark.django_db
class TestCheckFkLotesCommand:
    """Tests for check_fk_lotes command."""
    
    def test_handle_models_not_available(self):
        """Test when models are not available."""
        with patch('api.management.commands.check_fk_lotes.Finca', None):
            command = Command()
            
            with pytest.raises(CommandError, match="no están disponibles"):
                command.handle()
    
    def test_validate_identifier_valid(self):
        """Test validating valid identifier."""
        command = Command()
        
        result = command._validate_identifier('test_table')
        
        assert result == 'test_table'
    
    def test_validate_identifier_empty(self):
        """Test validating empty identifier."""
        command = Command()
        
        with pytest.raises(ValueError, match="Identifier must be"):
            command._validate_identifier('')
    
    def test_validate_identifier_none(self):
        """Test validating None identifier."""
        command = Command()
        
        with pytest.raises(ValueError, match="Identifier must be"):
            command._validate_identifier(None)
    
    def test_validate_identifier_invalid_chars(self):
        """Test validating identifier with invalid characters."""
        command = Command()
        
        with pytest.raises(ValueError, match="Invalid identifier"):
            command._validate_identifier('test-table; DROP')
    
    def test_validate_identifier_quotes(self):
        """Test validating identifier with quotes."""
        command = Command()
        
        # Quotes are invalid characters (checked before escaping), should raise ValueError
        with pytest.raises(ValueError, match="Invalid identifier"):
            command._validate_identifier('test"table')
    
    def test_build_drop_constraint_query(self):
        """Test building drop constraint query."""
        command = Command()
        
        query = command._build_drop_constraint_query('test_table', 'test_constraint')
        
        assert 'DROP CONSTRAINT' in query
        assert 'test_table' in query
        assert 'test_constraint' in query
    
    def test_build_add_constraint_query(self):
        """Test building add constraint query."""
        command = Command()
        
        query = command._build_add_constraint_query(
            'test_table',
            'test_constraint',
            'test_column',
            'ref_table',
            'ref_column'
        )
        
        assert 'ADD CONSTRAINT' in query
        assert 'FOREIGN KEY' in query
        assert 'test_table' in query
        assert 'ref_table' in query
    
    def test_check_table_exists_true(self):
        """Test checking table existence when table exists."""
        command = Command()
        
        mock_cursor_obj = Mock()
        mock_cursor_obj.execute = Mock()
        mock_cursor_obj.fetchone.return_value = (1,)
        
        result = command._check_table_exists(mock_cursor_obj, 'test_table')
        
        assert result is True
        mock_cursor_obj.execute.assert_called_once()
    
    def test_check_table_exists_false(self):
        """Test checking table existence when table doesn't exist."""
        command = Command()
        
        mock_cursor_obj = Mock()
        mock_cursor_obj.execute = Mock()
        mock_cursor_obj.fetchone.return_value = None
        
        result = command._check_table_exists(mock_cursor_obj, 'test_table')
        
        assert result is False
        mock_cursor_obj.execute.assert_called_once()
    
    def test_get_foreign_keys(self):
        """Test getting foreign keys."""
        command = Command()
        
        mock_cursor_obj = Mock()
        mock_cursor_obj.execute = Mock()
        mock_cursor_obj.fetchall.return_value = [
            ('fk_name', 'table', 'column', 'ref_table', 'ref_column')
        ]
        
        fks = command._get_foreign_keys(mock_cursor_obj)
        
        assert len(fks) == 1
        mock_cursor_obj.execute.assert_called_once()
    
    def test_create_foreign_key(self):
        """Test creating foreign key."""
        command = Command()
        
        mock_cursor_obj = Mock()
        mock_cursor_obj.execute = Mock()
        
        command._create_foreign_key(mock_cursor_obj, 'test_constraint')
        
        mock_cursor_obj.execute.assert_called_once()
    
    def test_handle_missing_foreign_key_no_fix(self):
        """Test handling missing foreign key without fix."""
        command = Command()
        command.stdout = StringIO()
        
        mock_cursor = Mock()
        mock_cursor.execute = Mock()
        
        result = command._handle_missing_foreign_key(mock_cursor, fix=False)
        
        assert result is True
    
    def test_handle_missing_foreign_key_with_fix_table_exists(self):
        """Test handling missing foreign key with fix when table exists."""
        command = Command()
        command.stdout = StringIO()
        
        mock_cursor = Mock()
        mock_cursor.execute = Mock()
        
        with patch.object(command, '_check_table_exists', return_value=True):
            with patch.object(command, '_create_foreign_key'):
                result = command._handle_missing_foreign_key(mock_cursor, fix=True)
                
                assert result is False
    
    def test_handle_missing_foreign_key_with_fix_table_not_exists(self):
        """Test handling missing foreign key with fix when table doesn't exist."""
        command = Command()
        command.stdout = StringIO()
        
        mock_cursor = Mock()
        mock_cursor.execute = Mock()
        
        with patch.object(command, '_check_table_exists', return_value=False):
            with pytest.raises(CommandError, match="no existe"):
                command._handle_missing_foreign_key(mock_cursor, fix=True)
    
    def test_fix_incorrect_foreign_key(self):
        """Test fixing incorrect foreign key."""
        command = Command()
        command.stdout = StringIO()
        
        mock_cursor = Mock()
        mock_cursor.execute = Mock()
        
        with patch.object(command, '_validate_identifier'):
            with patch.object(command, '_create_foreign_key'):
                command._fix_incorrect_foreign_key(
                    mock_cursor,
                    'old_constraint',
                    'wrong_table'
                )
                
                assert mock_cursor.execute.call_count >= 1
    
    def test_process_incorrect_fk_no_fix(self):
        """Test processing incorrect FK without fix."""
        command = Command()
        command.stdout = StringIO()
        
        mock_cursor = Mock()
        
        result = command._process_incorrect_fk(
            mock_cursor,
            'constraint_name',
            'wrong_table',
            fix=False
        )
        
        assert result is True
    
    def test_process_incorrect_fk_with_fix(self):
        """Test processing incorrect FK with fix."""
        command = Command()
        command.stdout = StringIO()
        
        mock_cursor = Mock()
        
        with patch.object(command, '_fix_incorrect_foreign_key'):
            result = command._process_incorrect_fk(
                mock_cursor,
                'constraint_name',
                'wrong_table',
                fix=True
            )
            
            assert result is False
    
    def test_check_foreign_keys_no_fks(self):
        """Test checking foreign keys when none exist."""
        command = Command()
        command.stdout = StringIO()
        
        with patch.object(command, '_get_foreign_keys', return_value=[]):
            with patch.object(command, '_handle_missing_foreign_key', return_value=True):
                with patch.object(connection, 'cursor') as mock_cursor:
                    mock_cursor_obj = Mock()
                    mock_cursor_obj.__enter__ = Mock(return_value=mock_cursor_obj)
                    mock_cursor_obj.__exit__ = Mock(return_value=None)
                    mock_cursor.return_value = mock_cursor_obj
                    
                    result = command._check_foreign_keys(fix=False)
                    
                    assert result is True
    
    def test_check_foreign_keys_correct_fk(self):
        """Test checking foreign keys with correct FK."""
        command = Command()
        command.stdout = StringIO()
        
        fks = [
            ('fk_name', 'table', 'column', 'api_finca', 'id')
        ]
        
        with patch.object(command, '_get_foreign_keys', return_value=fks):
            with patch.object(connection, 'cursor') as mock_cursor:
                mock_cursor_obj = Mock()
                mock_cursor_obj.__enter__ = Mock(return_value=mock_cursor_obj)
                mock_cursor_obj.__exit__ = Mock(return_value=None)
                mock_cursor.return_value = mock_cursor_obj
                
                result = command._check_foreign_keys(fix=False)
                
                assert result is False
    
    def test_check_foreign_keys_incorrect_fk(self):
        """Test checking foreign keys with incorrect FK."""
        command = Command()
        command.stdout = StringIO()
        
        fks = [
            ('fk_name', 'table', 'column', 'wrong_table', 'id')
        ]
        
        with patch.object(command, '_get_foreign_keys', return_value=fks):
            with patch.object(command, '_process_incorrect_fk', return_value=True):
                with patch.object(connection, 'cursor') as mock_cursor:
                    mock_cursor_obj = Mock()
                    mock_cursor_obj.__enter__ = Mock(return_value=mock_cursor_obj)
                    mock_cursor_obj.__exit__ = Mock(return_value=None)
                    mock_cursor.return_value = mock_cursor_obj
                    
                    result = command._check_foreign_keys(fix=False)
                    
                    assert result is True
    
    def test_check_data_consistency(self):
        """Test checking data consistency."""
        command = Command()
        command.stdout = StringIO()
        
        with patch('api.management.commands.check_fk_lotes.Finca') as mock_finca:
            mock_finca.objects.count.return_value = 5
            fincas_list = [{'id': 1, 'nombre': 'Finca 1'}]
            # Mock values() to return a queryset that supports slicing
            # The code does: list(Finca.objects.values('id', 'nombre')[:10])
            mock_queryset = Mock()
            # Make slicing return the list directly (list() will work on it)
            mock_queryset.__getitem__ = Mock(return_value=fincas_list)
            mock_finca.objects.values.return_value = mock_queryset
            
            with patch.object(connection, 'cursor') as mock_cursor:
                mock_cursor_obj = Mock()
                mock_cursor_obj.__enter__ = Mock(return_value=mock_cursor_obj)
                mock_cursor_obj.__exit__ = Mock(return_value=None)
                mock_cursor_obj.execute = Mock()
                mock_cursor_obj.fetchall.return_value = []
                mock_cursor.return_value = mock_cursor_obj
                
                command._check_data_consistency()
                
                output = command.stdout.getvalue()
                assert len(output) > 0
    
    def test_check_data_consistency_with_orphans(self):
        """Test checking data consistency with orphaned lotes."""
        command = Command()
        command.stdout = StringIO()
        
        with patch('api.management.commands.check_fk_lotes.Finca') as mock_finca:
            mock_finca.objects.count.return_value = 5
            fincas_list = [{'id': 1, 'nombre': 'Finca 1'}]
            # Mock values() to return a queryset that supports slicing
            # The code does: list(Finca.objects.values('id', 'nombre')[:10])
            mock_queryset = Mock()
            # Make slicing return the list directly (list() will work on it)
            mock_queryset.__getitem__ = Mock(return_value=fincas_list)
            mock_finca.objects.values.return_value = mock_queryset
            
            with patch.object(connection, 'cursor') as mock_cursor:
                mock_cursor_obj = Mock()
                mock_cursor_obj.__enter__ = Mock(return_value=mock_cursor_obj)
                mock_cursor_obj.__exit__ = Mock(return_value=None)
                mock_cursor_obj.execute = Mock()
                mock_cursor_obj.fetchall.return_value = [
                    (1, 999, None)  # Orphaned lote
                ]
                mock_cursor.return_value = mock_cursor_obj
                
                command._check_data_consistency()
                
                output = command.stdout.getvalue()
                assert 'huérfanos' in output.lower() or 'orphaned' in output.lower()
    
    def test_handle_with_options(self):
        """Test handling command with options."""
        with patch('api.management.commands.check_fk_lotes.Finca') as mock_finca:
            with patch('api.management.commands.check_fk_lotes.Lote') as mock_lote:
                mock_finca.objects.count.return_value = 0
                mock_lote.objects.count.return_value = 0
                
                command = Command()
                command.stdout = StringIO()
                
                with patch.object(command, '_check_foreign_keys', return_value=False):
                    with patch.object(command, '_check_data_consistency'):
                        command.handle(fix=False, check_orphans=True)
                        
                        output = command.stdout.getvalue()
                        assert len(output) > 0


