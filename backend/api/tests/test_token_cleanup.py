"""
Tests for token cleanup task.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone
from django.db import OperationalError, ProgrammingError

from api.tasks.token_cleanup import cleanup_expired_tokens


@pytest.mark.django_db
class TestTokenCleanup:
    """Tests for token cleanup task."""
    
    def test_cleanup_expired_tokens_success(self):
        """Test successful cleanup of expired tokens."""
        with patch('rest_framework_simplejwt.token_blacklist.models.BlacklistedToken') as mock_blacklisted:
            with patch('rest_framework_simplejwt.token_blacklist.models.OutstandingToken') as mock_outstanding:
                mock_blacklisted_qs = Mock()
                mock_blacklisted.objects.filter.return_value = mock_blacklisted_qs
                mock_blacklisted_qs.count.return_value = 10
                
                mock_outstanding_qs = Mock()
                mock_outstanding.objects.filter.return_value = mock_outstanding_qs
                mock_outstanding_qs.count.return_value = 5
                
                result = cleanup_expired_tokens()
                
                assert result['success'] is True
                assert result['blacklisted_deleted'] == 10
                assert result['outstanding_deleted'] == 5
                assert mock_blacklisted_qs.delete.called
                assert mock_outstanding_qs.delete.called
    
    def test_cleanup_expired_tokens_no_tokens(self):
        """Test cleanup when no expired tokens exist."""
        with patch('rest_framework_simplejwt.token_blacklist.models.BlacklistedToken') as mock_blacklisted:
            with patch('rest_framework_simplejwt.token_blacklist.models.OutstandingToken') as mock_outstanding:
                mock_blacklisted_qs = Mock()
                mock_blacklisted.objects.filter.return_value = mock_blacklisted_qs
                mock_blacklisted_qs.count.return_value = 0
                
                mock_outstanding_qs = Mock()
                mock_outstanding.objects.filter.return_value = mock_outstanding_qs
                mock_outstanding_qs.count.return_value = 0
                
                result = cleanup_expired_tokens()
                
                assert result['success'] is True
                assert result['blacklisted_deleted'] == 0
                assert result['outstanding_deleted'] == 0
                assert not mock_blacklisted_qs.delete.called
                assert not mock_outstanding_qs.delete.called
    
    def test_cleanup_expired_tokens_table_not_exists(self):
        """Test cleanup when tables don't exist yet."""
        with patch('rest_framework_simplejwt.token_blacklist.models.BlacklistedToken') as mock_blacklisted:
            mock_blacklisted.objects.filter.side_effect = OperationalError("relation does not exist")
            
            result = cleanup_expired_tokens()
            
            assert result['success'] is True
            assert 'error' not in result or result.get('error') is None
    
    def test_cleanup_expired_tokens_programming_error(self):
        """Test cleanup with programming error."""
        with patch('rest_framework_simplejwt.token_blacklist.models.BlacklistedToken') as mock_blacklisted:
            mock_blacklisted.objects.filter.side_effect = ProgrammingError("table does not exist")
            
            result = cleanup_expired_tokens()
            
            assert result['success'] is True
    
    def test_cleanup_expired_tokens_generic_error(self):
        """Test cleanup with generic error."""
        # Patch BlacklistedToken.objects.filter to raise a generic exception
        with patch('rest_framework_simplejwt.token_blacklist.models.BlacklistedToken') as mock_blacklisted:
            # Make filter() raise a generic exception (not OperationalError or ProgrammingError)
            mock_blacklisted.objects.filter.side_effect = Exception("Unexpected error")
            
            result = cleanup_expired_tokens()
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error'] == 'Unexpected error'

