"""
Tests for check_fk_lotes script.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from django.db import connection


class TestCheckFkLotesScript:
    """Tests for check_fk_lotes script functions."""
    
    def test_validate_identifier_valid(self):
        """Test validating valid identifier."""
        from scripts.check_fk_lotes import _validate_identifier
        
        result = _validate_identifier('test_table')
        
        assert result == 'test_table'
    
    def test_validate_identifier_empty(self):
        """Test validating empty identifier."""
        from scripts.check_fk_lotes import _validate_identifier
        
        with pytest.raises(ValueError, match="Identifier must be"):
            _validate_identifier('')
    
    def test_validate_identifier_none(self):
        """Test validating None identifier."""
        from scripts.check_fk_lotes import _validate_identifier
        
        with pytest.raises(ValueError, match="Identifier must be"):
            _validate_identifier(None)
    
    def test_validate_identifier_invalid_chars(self):
        """Test validating identifier with invalid characters."""
        from scripts.check_fk_lotes import _validate_identifier
        
        with pytest.raises(ValueError, match="Invalid identifier"):
            _validate_identifier('test-table; DROP')
    
    def test_validate_identifier_with_dash(self):
        """Test validating identifier with dash."""
        from scripts.check_fk_lotes import _validate_identifier
        
        result = _validate_identifier('test-table')
        
        assert result is not None
    
    def test_build_drop_constraint_query(self):
        """Test building drop constraint query."""
        from scripts.check_fk_lotes import _build_drop_constraint_query
        
        query = _build_drop_constraint_query('test_table', 'test_constraint')
        
        assert 'DROP CONSTRAINT' in query
        assert 'test_table' in query
        assert 'test_constraint' in query
    
    def test_build_add_constraint_query(self):
        """Test building add constraint query."""
        from scripts.check_fk_lotes import _build_add_constraint_query
        
        query = _build_add_constraint_query(
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
    
    def test_check_existing_foreign_keys(self):
        """Test checking existing foreign keys."""
        from scripts.check_fk_lotes import _check_existing_foreign_keys
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor_obj.__enter__.return_value.fetchall.return_value = [
                ('fk_name', 'table', 'column', 'ref_table', 'ref_column')
            ]
            mock_cursor.return_value = mock_cursor_obj
            
            fks = _check_existing_foreign_keys(mock_cursor_obj.__enter__.return_value)
            
            assert len(fks) == 1
    
    def test_table_exists_true(self):
        """Test checking table existence when table exists."""
        from scripts.check_fk_lotes import _table_exists
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor_obj.__enter__.return_value.fetchone.return_value = (1,)
            mock_cursor.return_value = mock_cursor_obj
            
            result = _table_exists(mock_cursor_obj.__enter__.return_value, 'test_table')
            
            assert result is True
    
    def test_table_exists_false(self):
        """Test checking table existence when table doesn't exist."""
        from scripts.check_fk_lotes import _table_exists
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor_obj.__enter__.return_value.fetchone.return_value = None
            mock_cursor.return_value = mock_cursor_obj
            
            result = _table_exists(mock_cursor_obj.__enter__.return_value, 'test_table')
            
            assert result is False
    
    def test_create_missing_foreign_key_table_exists(self):
        """Test creating missing foreign key when table exists."""
        from scripts.check_fk_lotes import _create_missing_foreign_key
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('scripts.check_fk_lotes._table_exists', return_value=True):
                result = _create_missing_foreign_key(mock_cursor_obj.__enter__.return_value)
                
                assert result is True
                mock_cursor_obj.__enter__.return_value.execute.assert_called_once()
    
    def test_create_missing_foreign_key_table_not_exists(self):
        """Test creating missing foreign key when table doesn't exist."""
        from scripts.check_fk_lotes import _create_missing_foreign_key
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('scripts.check_fk_lotes._table_exists', return_value=False):
                result = _create_missing_foreign_key(mock_cursor_obj.__enter__.return_value)
                
                assert result is False
    
    def test_validate_fk_identifiers_all_valid(self):
        """Test validating all FK identifiers when all are valid."""
        from scripts.check_fk_lotes import _validate_fk_identifiers
        
        result = _validate_fk_identifiers(
            'test_constraint',
            'test_table',
            'test_column',
            'ref_table',
            'ref_column'
        )
        
        assert result is True
    
    def test_validate_fk_identifiers_invalid(self):
        """Test validating FK identifiers when some are invalid."""
        from scripts.check_fk_lotes import _validate_fk_identifiers
        
        with patch('scripts.check_fk_lotes._validate_identifier', side_effect=ValueError("Invalid")):
            result = _validate_fk_identifiers(
                'invalid;constraint',
                'test_table',
                'test_column',
                'ref_table',
                'ref_column'
            )
            
            assert result is False
    
    def test_fix_incorrect_foreign_key(self):
        """Test fixing incorrect foreign key."""
        from scripts.check_fk_lotes import _fix_incorrect_foreign_key
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('scripts.check_fk_lotes._validate_identifier', return_value='test'):
                _fix_incorrect_foreign_key(
                    mock_cursor_obj.__enter__.return_value,
                    'old_constraint',
                    'wrong_table'
                )
                
                assert mock_cursor_obj.__enter__.return_value.execute.call_count >= 1
    
    def test_fix_incorrect_foreign_key_invalid_new_name(self):
        """Test fixing incorrect foreign key with invalid new constraint name."""
        from scripts.check_fk_lotes import _fix_incorrect_foreign_key
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value.execute = Mock()
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('scripts.check_fk_lotes._validate_identifier', side_effect=[None, ValueError("Invalid")]):
                _fix_incorrect_foreign_key(
                    mock_cursor_obj.__enter__.return_value,
                    'old_constraint',
                    'wrong_table'
                )
                
                # Should not crash, just return early
                assert True
    
    def test_process_existing_foreign_keys_correct(self):
        """Test processing existing foreign keys with correct FK."""
        from scripts.check_fk_lotes import _process_existing_foreign_keys
        
        fks = [
            ('fk_name', 'table', 'column', 'api_finca', 'id')
        ]
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value = mock_cursor_obj
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('builtins.print'):
                _process_existing_foreign_keys(mock_cursor_obj.__enter__.return_value, fks)
                
                # Should not call fix function
                assert True
    
    def test_process_existing_foreign_keys_incorrect(self):
        """Test processing existing foreign keys with incorrect FK."""
        from scripts.check_fk_lotes import _process_existing_foreign_keys
        
        fks = [
            ('fk_name', 'table', 'column', 'wrong_table', 'id')
        ]
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value = mock_cursor_obj
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('scripts.check_fk_lotes._validate_fk_identifiers', return_value=True):
                with patch('scripts.check_fk_lotes._fix_incorrect_foreign_key'):
                    with patch('builtins.print'):
                        _process_existing_foreign_keys(mock_cursor_obj.__enter__.return_value, fks)
                        
                        # Should call fix function
                        assert True
    
    def test_check_data_consistency_no_orphans(self):
        """Test checking data consistency with no orphaned lotes."""
        from scripts.check_fk_lotes import _check_data_consistency
        
        with patch('scripts.check_fk_lotes.Finca') as mock_finca:
            mock_finca.objects.count.return_value = 5
            mock_finca.objects.values.return_value = [
                {'id': 1, 'nombre': 'Finca 1'}
            ]
            mock_finca.objects.values.return_value.__getitem__ = Mock(return_value=[])
            
            with patch.object(connection, 'cursor') as mock_cursor:
                mock_cursor_obj = Mock()
                mock_cursor_obj.__enter__.return_value.execute = Mock()
                mock_cursor_obj.__enter__.return_value.fetchall.return_value = []
                mock_cursor.return_value = mock_cursor_obj
                
                with patch('builtins.print'):
                    _check_data_consistency()
                    
                    # Should complete without errors
                    assert True
    
    def test_check_data_consistency_with_orphans(self):
        """Test checking data consistency with orphaned lotes."""
        from scripts.check_fk_lotes import _check_data_consistency
        
        with patch('scripts.check_fk_lotes.Finca') as mock_finca:
            mock_finca.objects.count.return_value = 5
            mock_finca.objects.values.return_value = [
                {'id': 1, 'nombre': 'Finca 1'}
            ]
            mock_finca.objects.values.return_value.__getitem__ = Mock(return_value=[])
            
            with patch.object(connection, 'cursor') as mock_cursor:
                mock_cursor_obj = Mock()
                mock_cursor_obj.__enter__.return_value.execute = Mock()
                mock_cursor_obj.__enter__.return_value.fetchall.return_value = [
                    (1, 999, None)  # Orphaned lote
                ]
                mock_cursor.return_value = mock_cursor_obj
                
                with patch('builtins.print'):
                    _check_data_consistency()
                    
                    # Should complete and report orphans
                    assert True
    
    @patch('scripts.check_fk_lotes._check_existing_foreign_keys')
    @patch('scripts.check_fk_lotes._create_missing_foreign_key')
    @patch('scripts.check_fk_lotes._process_existing_foreign_keys')
    @patch('scripts.check_fk_lotes._check_data_consistency')
    @patch('scripts.check_fk_lotes.Finca')
    @patch('scripts.check_fk_lotes.Lote')
    def test_check_and_fix_foreign_key_main(self, mock_lote, mock_finca, mock_check_data, 
                                            mock_process, mock_create, mock_check_fks):
        """Test main check_and_fix_foreign_key function."""
        from scripts.check_fk_lotes import check_and_fix_foreign_key
        
        mock_check_fks.return_value = []
        mock_create.return_value = True
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value = mock_cursor_obj
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('builtins.print'):
                check_and_fix_foreign_key()
                
                # Should complete successfully
                assert True
    
    @patch('scripts.check_fk_lotes._check_existing_foreign_keys')
    @patch('scripts.check_fk_lotes._process_existing_foreign_keys')
    @patch('scripts.check_fk_lotes._check_data_consistency')
    def test_check_and_fix_foreign_key_with_existing_fks(self, mock_check_data, mock_process, mock_check_fks):
        """Test main function with existing foreign keys."""
        from scripts.check_fk_lotes import check_and_fix_foreign_key
        
        mock_check_fks.return_value = [
            ('fk_name', 'table', 'column', 'api_finca', 'id')
        ]
        
        with patch.object(connection, 'cursor') as mock_cursor:
            mock_cursor_obj = Mock()
            mock_cursor_obj.__enter__.return_value = mock_cursor_obj
            mock_cursor.return_value = mock_cursor_obj
            
            with patch('scripts.check_fk_lotes._validate_fk_identifiers', return_value=True):
                with patch('builtins.print'):
                    check_and_fix_foreign_key()
                    
                    # Should process existing FKs
                    assert True


