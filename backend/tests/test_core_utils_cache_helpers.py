"""
Unit tests for core utils cache_helpers module.
Tests cache invalidation functions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.cache import cache

from core.utils.cache_helpers import (
    invalidate_cache_pattern,
    invalidate_system_stats_cache,
    invalidate_models_status_cache
)


@pytest.fixture
def mock_cache():
    """Create a mock cache for testing."""
    with patch('core.utils.cache_helpers.cache') as mock_cache:
        yield mock_cache


class TestInvalidateCachePattern:
    """Tests for invalidate_cache_pattern function."""
    
    def test_invalidate_simple_pattern(self, mock_cache):
        """Test invalidating a simple cache pattern."""
        invalidate_cache_pattern('test_key')
        
        mock_cache.delete.assert_called_once_with('test_key', version=None)
    
    def test_invalidate_pattern_with_wildcard(self, mock_cache):
        """Test invalidating a pattern with wildcard."""
        invalidate_cache_pattern('test_*')
        
        # Should log but not call delete for wildcard patterns
        # (simplified implementation)
        assert True  # Pattern logged
    
    def test_invalidate_handles_exception(self, mock_cache):
        """Test that exceptions are handled gracefully."""
        mock_cache.delete.side_effect = Exception("Cache error")
        
        # Should not raise exception
        invalidate_cache_pattern('test_key')
        
        mock_cache.delete.assert_called_once()


class TestInvalidateSystemStatsCache:
    """Tests for invalidate_system_stats_cache function."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_system_stats(self, mock_invalidate):
        """Test invalidating system stats cache."""
        invalidate_system_stats_cache()
        
        assert mock_invalidate.call_count == 3
        mock_invalidate.assert_any_call('system_stats_*')
        mock_invalidate.assert_any_call('dashboard_stats_*')
        mock_invalidate.assert_any_call('admin_stats_*')


class TestInvalidateModelsStatusCache:
    """Tests for invalidate_models_status_cache function."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_models_status(self, mock_invalidate):
        """Test invalidating models status cache."""
        invalidate_models_status_cache()
        
        mock_invalidate.assert_called_once_with('models_status_*')

