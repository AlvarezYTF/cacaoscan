"""
Utility functions and decorators for CacaoScan API.
Maintains backward compatibility by re-exporting from core.utils.
"""
# Re-export from core.utils for backward compatibility
from core.utils import (
    create_error_response,
    create_success_response,
    validate_password_strength,
    validate_passwords_match,
    validate_password_different,
    validate_latitude,
    validate_longitude,
    validate_coordinates_pair,
    validate_coordinates,
    PasswordValidationError,
    invalidate_cache_pattern,
    invalidate_system_stats_cache,
    invalidate_models_status_cache,
    invalidate_dataset_validation_cache,
    invalidate_latest_metrics_cache,
    invalidate_user_related_cache,
    invalidate_model_metrics_cache,
    get_cache_key,
)
from .decorators import handle_api_errors
from .pagination import (
    get_pagination_params,
    paginate_queryset,
    build_pagination_urls,
    create_paginated_response
)
from .model_imports import get_model_safely, get_models_safely

__all__ = [
    # Response helpers (from core.utils)
    'create_error_response',
    'create_success_response',
    # Validators (from core.utils)
    'validate_password_strength',
    'validate_passwords_match',
    'validate_password_different',
    'validate_latitude',
    'validate_longitude',
    'validate_coordinates_pair',
    'validate_coordinates',
    'PasswordValidationError',
    # Cache helpers (from core.utils)
    'invalidate_cache_pattern',
    'invalidate_system_stats_cache',
    'invalidate_models_status_cache',
    'invalidate_dataset_validation_cache',
    'invalidate_latest_metrics_cache',
    'invalidate_user_related_cache',
    'invalidate_model_metrics_cache',
    'get_cache_key',
    # Local utilities
    'handle_api_errors',
    'get_pagination_params',
    'paginate_queryset',
    'build_pagination_urls',
    'create_paginated_response',
    'get_model_safely',
    'get_models_safely'
]

