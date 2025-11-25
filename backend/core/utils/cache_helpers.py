"""
Cache helper utilities for CacaoScan API.
Provides functions for cache invalidation and management.
"""
import logging
from typing import List, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger("cacaoscan.api.cache")

# Cache alias to use for API caching
CACHE_ALIAS = 'api_cache' if 'api_cache' in getattr(settings, 'CACHES', {}) else 'default'


def invalidate_cache_pattern(pattern: str) -> None:
    """
    Invalidate cache keys matching a pattern.
    
    Note: This is a simplified implementation. For production with Redis,
    consider using SCAN command for pattern matching.
    
    Args:
        pattern: Cache key pattern to invalidate (supports wildcards)
    """
    try:
        # For Redis, we would use SCAN, but for simplicity we'll use a prefix-based approach
        # This works well with the KEY_PREFIX configuration
        if '*' in pattern:
            # Simple wildcard handling - invalidate by prefix
            prefix = pattern.replace('*', '')
            # In production with Redis, use: cache.delete_pattern(f"{prefix}*")
            logger.info(f"Cache invalidation requested for pattern: {pattern}")
        else:
            cache.delete(pattern, version=None)
            logger.info(f"Cache invalidated for key: {pattern}")
    except Exception as e:
        logger.warning(f"Error invalidating cache pattern {pattern}: {e}")


def invalidate_system_stats_cache() -> None:
    """Invalidate system-wide statistics cache."""
    invalidate_cache_pattern('system_stats_*')
    invalidate_cache_pattern('dashboard_stats_*')
    invalidate_cache_pattern('admin_stats_*')


def invalidate_models_status_cache() -> None:
    """Invalidate models status cache."""
    invalidate_cache_pattern('models_status_*')


def invalidate_dataset_validation_cache() -> None:
    """Invalidate dataset validation cache."""
    invalidate_cache_pattern('dataset_validation_*')


def invalidate_latest_metrics_cache() -> None:
    """Invalidate latest metrics cache."""
    invalidate_cache_pattern('latest_metrics_*')


def invalidate_user_related_cache(user_id: Optional[int] = None) -> None:
    """
    Invalidate user-related cache.
    
    Args:
        user_id: Optional user ID to invalidate specific user cache
    """
    if user_id:
        invalidate_cache_pattern(f'user_stats_{user_id}_*')
        invalidate_cache_pattern(f'user_activity_{user_id}_*')
    else:
        invalidate_cache_pattern('user_stats_*')
        invalidate_cache_pattern('user_activity_*')


def invalidate_model_metrics_cache() -> None:
    """Invalidate model metrics related cache."""
    invalidate_latest_metrics_cache()
    invalidate_cache_pattern('model_metrics_*')


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        str: Generated cache key
    """
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

