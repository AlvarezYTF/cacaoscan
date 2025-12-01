"""
Unit tests for API cache_config module.
Tests cache configuration constants and settings.
"""
import pytest
import os
from unittest.mock import patch

from api import cache_config


class TestCacheConfig:
    """Tests for cache configuration."""
    
    def test_redis_cache_backend_constant(self):
        """Test that REDIS_CACHE_BACKEND constant is defined."""
        assert hasattr(cache_config, 'REDIS_CACHE_BACKEND')
        assert cache_config.REDIS_CACHE_BACKEND == 'django_redis.cache.RedisCache'
    
    def test_redis_client_class_constant(self):
        """Test that REDIS_CLIENT_CLASS constant is defined."""
        assert hasattr(cache_config, 'REDIS_CLIENT_CLASS')
        assert cache_config.REDIS_CLIENT_CLASS == 'django_redis.client.DefaultClient'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_redis_host_default(self):
        """Test default Redis host."""
        # Reload module to get default
        import importlib
        importlib.reload(cache_config)
        
        assert cache_config.REDIS_HOST == 'localhost'
    
    @patch.dict(os.environ, {'REDIS_HOST': 'custom-host'}, clear=False)
    def test_redis_host_from_env(self):
        """Test Redis host from environment."""
        import importlib
        importlib.reload(cache_config)
        
        assert cache_config.REDIS_HOST == 'custom-host'
    
    def test_caches_configuration_exists(self):
        """Test that CACHES configuration exists."""
        assert hasattr(cache_config, 'CACHES')
        assert isinstance(cache_config.CACHES, dict)
    
    def test_caches_default_config(self):
        """Test default cache configuration."""
        assert 'default' in cache_config.CACHES
        default_cache = cache_config.CACHES['default']
        
        assert 'BACKEND' in default_cache
        assert 'LOCATION' in default_cache
        assert 'OPTIONS' in default_cache
        assert 'KEY_PREFIX' in default_cache
    
    def test_caches_sessions_config(self):
        """Test sessions cache configuration."""
        assert 'sessions' in cache_config.CACHES
        sessions_cache = cache_config.CACHES['sessions']
        
        assert 'BACKEND' in sessions_cache
        assert 'LOCATION' in sessions_cache
        assert 'KEY_PREFIX' in sessions_cache
    
    def test_caches_api_cache_config(self):
        """Test API cache configuration."""
        assert 'api_cache' in cache_config.CACHES
        api_cache = cache_config.CACHES['api_cache']
        
        assert 'BACKEND' in api_cache
        assert 'LOCATION' in api_cache
        assert 'KEY_PREFIX' in api_cache
    
    def test_api_cache_timeouts_exists(self):
        """Test that API_CACHE_TIMEOUTS exists."""
        assert hasattr(cache_config, 'API_CACHE_TIMEOUTS')
        assert isinstance(cache_config.API_CACHE_TIMEOUTS, dict)
    
    def test_api_cache_timeouts_keys(self):
        """Test that API_CACHE_TIMEOUTS has expected keys."""
        expected_keys = [
            'user_stats',
            'system_stats',
            'finca_list',
            'lote_list',
            'notification_list',
            'activity_logs',
            'reports_list'
        ]
        
        for key in expected_keys:
            assert key in cache_config.API_CACHE_TIMEOUTS
            assert isinstance(cache_config.API_CACHE_TIMEOUTS[key], int)
    
    def test_heavy_query_cache_timeouts_exists(self):
        """Test that HEAVY_QUERY_CACHE_TIMEOUTS exists."""
        assert hasattr(cache_config, 'HEAVY_QUERY_CACHE_TIMEOUTS')
        assert isinstance(cache_config.HEAVY_QUERY_CACHE_TIMEOUTS, dict)
    
    def test_cache_invalidation_patterns_exists(self):
        """Test that CACHE_INVALIDATION_PATTERNS exists."""
        assert hasattr(cache_config, 'CACHE_INVALIDATION_PATTERNS')
        assert isinstance(cache_config.CACHE_INVALIDATION_PATTERNS, dict)
    
    def test_cache_invalidation_patterns_keys(self):
        """Test that CACHE_INVALIDATION_PATTERNS has expected keys."""
        expected_keys = ['user_related', 'finca_related']
        
        for key in expected_keys:
            assert key in cache_config.CACHE_INVALIDATION_PATTERNS
            assert isinstance(cache_config.CACHE_INVALIDATION_PATTERNS[key], list)

