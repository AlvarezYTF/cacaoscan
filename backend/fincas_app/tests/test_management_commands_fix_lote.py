"""
Tests for fix_lote_foreign_key management command.
"""
import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.db import connection


@pytest.mark.django_db
class TestFixLoteForeignKeyCommand:
    """Tests for fix_lote_foreign_key command."""
    
    def test_validate_sql_identifier_valid(self):
        """Test _validate_sql_identifier with valid identifiers."""
        from fincas_app.management.commands.fix_lote_foreign_key import Command
        
        command = Command()
        
        # Valid identifiers
        assert command._validate_sql_identifier('test_table') == 'test_table'
        assert command._validate_sql_identifier('test_123') == 'test_123'
        assert command._validate_sql_identifier('_test') == '_test'
    
    def test_validate_sql_identifier_invalid(self):
        """Test _validate_sql_identifier with invalid identifiers."""
        from fincas_app.management.commands.fix_lote_foreign_key import Command
        
        command = Command()
        
        # Invalid identifiers
        with pytest.raises(ValueError, match="no puede estar vacío"):
            command._validate_sql_identifier('')
        
        with pytest.raises(ValueError, match="debe ser una cadena"):
            command._validate_sql_identifier(None)
        
        with pytest.raises(ValueError, match="demasiado largo"):
            command._validate_sql_identifier('a' * 64)
        
        with pytest.raises(ValueError, match=".*inválido.*"):
            command._validate_sql_identifier('test-table')
        
        with pytest.raises(ValueError, match=".*inválido.*"):
            command._validate_sql_identifier('123test')
    
    @patch('fincas_app.management.commands.fix_lote_foreign_key.connection')
    def test_handle_no_foreign_keys(self, mock_connection):
        """Test command with no foreign keys found."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        out = StringIO()
        call_command('fix_lote_foreign_key', stdout=out)
        
        output = out.getvalue()
        assert 'foreign key' in output.lower() or 'no se encontró' in output.lower()
    
    @patch('fincas_app.management.commands.fix_lote_foreign_key.connection')
    def test_handle_correct_foreign_key(self, mock_connection):
        """Test command when foreign key is already correct."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock correct foreign key
        # fetchall is called 3 times: _find_foreign_keys, _handle_orphaned_lotes, _verify_final_state
        fetchall_results = [
            [('fk_name', 'finca_id', 'api_finca')],  # Found FKs
            [],  # Orphaned lotes
            [('fk_name', 'api_finca')]  # Final verification
        ]
        fetchall_iterator = iter(fetchall_results)
        def fetchall_side_effect():
            return next(fetchall_iterator, [])
        mock_cursor.fetchall = MagicMock(side_effect=fetchall_side_effect)
        
        # Use a list that can be consumed multiple times - provide enough values
        fetchone_results = [
            (1,),  # api_finca exists
            None,  # Additional None to prevent StopIteration
            None,  # Additional None to prevent StopIteration
            None,  # Additional None to prevent StopIteration
        ]
        fetchone_iterator = iter(fetchone_results)
        def fetchone_side_effect():
            return next(fetchone_iterator, None)
        mock_cursor.fetchone = MagicMock(side_effect=fetchone_side_effect)
        
        out = StringIO()
        call_command('fix_lote_foreign_key', stdout=out)
        
        output = out.getvalue()
        assert 'correcta' in output.lower() or 'correcto' in output.lower() or 'api_finca' in output.lower()
    
    @patch('fincas_app.management.commands.fix_lote_foreign_key.connection')
    def test_handle_incorrect_foreign_key(self, mock_connection):
        """Test command when foreign key is incorrect."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_connection.cursor.return_value = mock_cursor
        
        # Mock incorrect foreign key
        fetchall_results = [
            [('fk_name', 'finca_id', 'fincas_app_finca')],  # Incorrect FK
            [],  # Orphaned lotes
            [('fincas_app_lote_finca_id_api_finca_fk', 'api_finca')]  # Final verification
        ]
        mock_cursor.fetchall = MagicMock(side_effect=lambda: fetchall_results.pop(0) if fetchall_results else [])
        
        # Use a list that can be consumed multiple times
        fetchone_results = [
            (1,),  # api_finca exists
            None,  # FK doesn't exist (in _create_correct_foreign_key check)
            None,  # No orphaned lotes
            None,  # Additional None to prevent StopIteration
            None,  # Additional None to prevent StopIteration
            None,  # Additional None to prevent StopIteration
        ]
        fetchone_call_count = [0]
        def fetchone_side_effect():
            if fetchone_call_count[0] < len(fetchone_results):
                result = fetchone_results[fetchone_call_count[0]]
                fetchone_call_count[0] += 1
                return result
            return None
        mock_cursor.fetchone = MagicMock(side_effect=fetchone_side_effect)
        
        out = StringIO()
        call_command('fix_lote_foreign_key', stdout=out)
        
        output = out.getvalue()
        assert 'corrigiendo' in output.lower() or 'corregida' in output.lower() or 'eliminada' in output.lower()

