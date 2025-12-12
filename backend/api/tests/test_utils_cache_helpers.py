"""
Tests for cache helper utilities.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from core.utils.cache_helpers import (
    invalidate_cache_pattern,
    invalidate_system_stats_cache,
    invalidate_models_status_cache,
    invalidate_dataset_validation_cache,
    invalidate_latest_metrics_cache,
    invalidate_user_related_cache,
    invalidate_model_metrics_cache,
    get_cache_key
)


class TestInvalidateCachePattern:
    """Test cases for invalidate_cache_pattern."""
    
    def test_invalidate_cache_pattern_without_wildcard(self):
        """Test invalidating cache with specific key."""
        with patch.object(cache, 'delete') as mock_delete:
            invalidate_cache_pattern('test_key')
            mock_delete.assert_called_once_with('test_key', version=None)
    
    def test_invalidate_cache_pattern_with_wildcard(self):
        """Test invalidating cache with wildcard pattern."""
        with patch.object(cache, 'delete') as mock_delete:
            with patch('core.utils.cache_helpers.logger') as mock_logger:
                invalidate_cache_pattern('test_key_*')
                mock_logger.info.assert_called()
                # With wildcard, cache.delete should not be called directly
                # (reserved for future Redis implementation)
    
    def test_invalidate_cache_pattern_exception_handling(self):
        """Test exception handling in cache invalidation."""
        with patch.object(cache, 'delete', side_effect=Exception('Cache error')):
            with patch('core.utils.cache_helpers.logger') as mock_logger:
                invalidate_cache_pattern('test_key')
                mock_logger.warning.assert_called_once()
    
    def test_invalidate_cache_pattern_with_wildcard_exception(self):
        """Test exception handling with wildcard pattern."""
        with patch('core.utils.cache_helpers.logger') as mock_logger:
            invalidate_cache_pattern('test_*')
            mock_logger.info.assert_called()


class TestInvalidateSystemStatsCache:
    """Test cases for invalidate_system_stats_cache."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_system_stats_cache(self, mock_invalidate):
        """Test invalidating system stats cache."""
        invalidate_system_stats_cache()
        assert mock_invalidate.call_count == 3
        mock_invalidate.assert_any_call('system_stats_*')
        mock_invalidate.assert_any_call('dashboard_stats_*')
        mock_invalidate.assert_any_call('admin_stats_*')


class TestInvalidateModelsStatusCache:
    """Test cases for invalidate_models_status_cache."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_models_status_cache(self, mock_invalidate):
        """Test invalidating models status cache."""
        invalidate_models_status_cache()
        mock_invalidate.assert_called_once_with('models_status_*')


class TestInvalidateDatasetValidationCache:
    """Test cases for invalidate_dataset_validation_cache."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_dataset_validation_cache(self, mock_invalidate):
        """Test invalidating dataset validation cache."""
        invalidate_dataset_validation_cache()
        mock_invalidate.assert_called_once_with('dataset_validation_*')


class TestInvalidateLatestMetricsCache:
    """Test cases for invalidate_latest_metrics_cache."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_latest_metrics_cache(self, mock_invalidate):
        """Test invalidating latest metrics cache."""
        invalidate_latest_metrics_cache()
        mock_invalidate.assert_called_once_with('latest_metrics_*')


class TestInvalidateUserRelatedCache:
    """Test cases for invalidate_user_related_cache."""
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_user_related_cache_with_user_id(self, mock_invalidate):
        """Test invalidating user-related cache with specific user ID."""
        invalidate_user_related_cache(user_id=123)
        assert mock_invalidate.call_count == 2
        mock_invalidate.assert_any_call('user_stats_123_*')
        mock_invalidate.assert_any_call('user_activity_123_*')
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_user_related_cache_without_user_id(self, mock_invalidate):
        """Test invalidating all user-related cache."""
        invalidate_user_related_cache()
        assert mock_invalidate.call_count == 2
        mock_invalidate.assert_any_call('user_stats_*')
        mock_invalidate.assert_any_call('user_activity_*')
    
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_user_related_cache_with_none(self, mock_invalidate):
        """Test invalidating all user-related cache with None."""
        invalidate_user_related_cache(user_id=None)
        assert mock_invalidate.call_count == 2
        mock_invalidate.assert_any_call('user_stats_*')
        mock_invalidate.assert_any_call('user_activity_*')


class TestInvalidateModelMetricsCache:
    """Test cases for invalidate_model_metrics_cache."""
    
    @patch('core.utils.cache_helpers.invalidate_latest_metrics_cache')
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_model_metrics_cache(self, mock_invalidate, mock_invalidate_latest):
        """Test invalidating model metrics cache."""
        invalidate_model_metrics_cache()
        mock_invalidate_latest.assert_called_once()
        mock_invalidate.assert_called_once_with('model_metrics_*')


class TestGetCacheKey:
    """Test cases for get_cache_key."""
    
    def test_get_cache_key_with_prefix_only(self):
        """Test generating cache key with prefix only."""
        key = get_cache_key('prefix')
        assert key == 'prefix'
    
    def test_get_cache_key_with_positional_args(self):
        """Test generating cache key with positional arguments."""
        key = get_cache_key('prefix', 'arg1', 'arg2', 'arg3')
        assert key == 'prefix:arg1:arg2:arg3'
    
    def test_get_cache_key_with_keyword_args(self):
        """Test generating cache key with keyword arguments."""
        key = get_cache_key('prefix', key1='value1', key2='value2')
        # Keys are sorted in the result
        assert ':key1=value1' in key
        assert ':key2=value2' in key
        assert key.startswith('prefix:')
    
    def test_get_cache_key_with_mixed_args(self):
        """Test generating cache key with both positional and keyword arguments."""
        key = get_cache_key('prefix', 'arg1', 'arg2', key1='value1', key2='value2')
        assert 'prefix:arg1:arg2' in key
        assert ':key1=value1' in key
        assert ':key2=value2' in key
    
    def test_get_cache_key_with_sorted_keywords(self):
        """Test that keyword arguments are sorted in the key."""
        key = get_cache_key('prefix', z='last', a='first', m='middle')
        parts = key.split(':')
        keyword_parts = [p for p in parts if '=' in p]
        assert keyword_parts == sorted(keyword_parts)
    
    def test_get_cache_key_with_none_values(self):
        """Test generating cache key with None values."""
        key = get_cache_key('prefix', None, key=None)
        assert 'None' in key
    
    def test_get_cache_key_with_integer_values(self):
        """Test generating cache key with integer values."""
        key = get_cache_key('prefix', 123, key=456)
        assert '123' in key
        assert '456' in key

