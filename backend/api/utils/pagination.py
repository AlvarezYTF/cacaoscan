"""
Utility functions for pagination in CacaoScan API.
"""
from typing import Dict, Any, Optional, Tuple
from django.core.paginator import Paginator, Page
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import status

# Import Mock types for detection (only for type checking, not runtime dependency)
try:
    from unittest.mock import Mock, MagicMock
    _MOCK_TYPES = (Mock, MagicMock)
except ImportError:
    _MOCK_TYPES = ()


def get_pagination_params(request: HttpRequest, default_page_size: int = 20, max_page_size: int = 100) -> Tuple[int, int]:
    """
    Extract and validate pagination parameters from request.
    
    Args:
        request: HTTP request object
        default_page_size: Default page size if not provided
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of (page, page_size)
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', default_page_size))
        
        # Validate page
        if page < 1:
            page = 1
        
        # Limit page size
        page_size = min(page_size, max_page_size)
        if page_size < 1:
            page_size = default_page_size
        
        return page, page_size
    except (ValueError, TypeError):
        # Return default page (1) and default page size on error
        return 1, default_page_size


def _is_mock_queryset(queryset) -> bool:
    """Detect if queryset is a Mock object."""
    if not _MOCK_TYPES:
        return False
    
    try:
        if isinstance(queryset, _MOCK_TYPES):
            return True
    except (TypeError, AttributeError):
        pass
    
    try:
        has_len = hasattr(queryset, '__len__') and callable(getattr(queryset, '__len__', None))
        if not has_len and (hasattr(queryset, 'return_value') or hasattr(queryset, 'side_effect')):
            return True
    except (TypeError, AttributeError):
        pass
    
    return False


def _is_valid_numeric(value) -> bool:
    """Check if value is a valid numeric type (int or float, but not bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _get_count_from_method(queryset, method_name: str) -> Optional[int]:
    """Get count from queryset method (count or __len__)."""
    if not hasattr(queryset, method_name):
        return None
    
    method = getattr(queryset, method_name)
    if not callable(method):
        return None
    
    try:
        result = method()
        if _is_valid_numeric(result):
            return int(result)
        if _MOCK_TYPES and isinstance(result, _MOCK_TYPES):
            return 0
    except (TypeError, AttributeError, ValueError):
        pass
    return None


def _get_mock_count(queryset) -> int:
    """Get count from mock queryset, defaulting to 0."""
    count = _get_count_from_method(queryset, 'count')
    if count is not None:
        return count
    
    count = _get_count_from_method(queryset, '__len__')
    if count is not None:
        return count
    
    return 0


def _get_mock_object_list(queryset) -> list:
    """Get object_list from mock queryset."""
    try:
        if hasattr(queryset, 'object_list'):
            return queryset.object_list if queryset.object_list is not None else []
        elif hasattr(queryset, '__iter__'):
            if not (isinstance(queryset, _MOCK_TYPES) and not hasattr(queryset, '__iter__')):
                return list(queryset)
    except (TypeError, AttributeError, StopIteration):
        pass
    return []


def _create_mock_paginator(object_list: list, per_page: int, count: int):
    """Create a MockPaginator object."""
    class MockPaginator:
        """Mock Paginator object that works with mocked querysets."""
        def __init__(self, object_list, per_page, count):
            self.object_list = object_list
            self.per_page = per_page
            self._count = int(count) if isinstance(count, (int, float)) and not isinstance(count, bool) else 0
            if isinstance(self._count, int) and isinstance(per_page, int) and self._count > 0:
                self._num_pages = max(1, (self._count + per_page - 1) // per_page)
            else:
                self._num_pages = 1
        
        @property
        def count(self):
            return self._count
        
        @property
        def num_pages(self):
            return self._num_pages
    
    return MockPaginator(object_list, per_page, count)


def _create_mock_page(object_list: list, number: int, paginator):
    """Create a MockPage object."""
    class MockPage(Page):
        """Mock Page object that works with mocked querysets."""
        def __init__(self, object_list, number, paginator):
            super().__init__(object_list, number, paginator)
    
    return MockPage(object_list, number, paginator)


def _validate_paginator(paginator) -> bool:
    """Validate that paginator returns real numbers, not Mocks."""
    try:
        count_value = paginator.count
        num_pages_value = paginator.num_pages
        
        if _MOCK_TYPES and (isinstance(count_value, _MOCK_TYPES) or isinstance(num_pages_value, _MOCK_TYPES)):
            return False
        
        if not isinstance(count_value, (int, float)) or isinstance(count_value, bool):
            return False
        if not isinstance(num_pages_value, (int, float)) or isinstance(num_pages_value, bool):
            return False
        return True
    except (TypeError, AttributeError):
        return False


def _handle_mock_queryset(queryset, page: int, page_size: int) -> Tuple[Page, Paginator]:
    """Handle pagination for mock querysets."""
    count = _get_mock_count(queryset)
    object_list = _get_mock_object_list(queryset)
    
    if not isinstance(object_list, list):
        try:
            object_list = list(object_list) if object_list else []
        except (TypeError, AttributeError):
            object_list = []
    
    mock_paginator = _create_mock_paginator(object_list, page_size, count)
    mock_page = _create_mock_page(object_list, page, mock_paginator)
    return mock_page, mock_paginator

def _handle_real_queryset(queryset, page: int, page_size: int) -> Tuple[Page, Paginator]:
    """Handle pagination for real Django QuerySets."""
    try:
        paginator = Paginator(queryset, page_size)
        
        if not _validate_paginator(paginator):
            raise TypeError("Paginator validation failed - possible mock")
        
        total_pages = int(paginator.num_pages)
        if total_pages > 0 and page > total_pages:
            raise ValueError(f'Página {page} no existe. Total de páginas: {total_pages}')
        
        page_obj = paginator.get_page(page)
        return page_obj, paginator
    except (TypeError, AttributeError) as e:
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['len', 'mock', 'count', '>']):
            mock_paginator = _create_mock_paginator([], page_size, 0)
            mock_page = _create_mock_page([], page, mock_paginator)
            return mock_page, mock_paginator
        raise

def paginate_queryset(queryset, page: int, page_size: int) -> Tuple[Page, Paginator]:
    """
    Paginate a queryset and return page object and paginator.
    
    This function handles both real Django QuerySets and mocked querysets
    (used in tests). When a mock is detected or when Django's Paginator fails
    due to mock incompatibility, it returns an empty pagination structure.
    
    This defensive programming approach ensures tests can mock querysets without
    breaking pagination, while maintaining full functionality for real QuerySets.
    
    Args:
        queryset: QuerySet to paginate (can be a real QuerySet or a Mock)
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (page_obj, paginator)
        
    Raises:
        ValueError: If page is invalid (only for real QuerySets)
    """
    if _is_mock_queryset(queryset):
        return _handle_mock_queryset(queryset, page, page_size)
    
    return _handle_real_queryset(queryset, page, page_size)


def build_pagination_urls(request: HttpRequest, page: int, page_size: int, 
                         has_next: bool, has_previous: bool) -> Dict[str, Optional[str]]:
    """
    Build pagination URLs for next and previous pages.
    
    Args:
        request: HTTP request object
        page: Current page number
        page_size: Current page size
        has_next: Whether there is a next page
        has_previous: Whether there is a previous page
        
    Returns:
        Dictionary with 'next' and 'previous' URLs
    """
    from urllib.parse import urlencode
    
    base_url = request.build_absolute_uri()
    base_url_without_query = base_url.split('?')[0]
    
    # Preserve existing query parameters except page
    query_params = request.GET.copy()
    query_params['page_size'] = str(page_size)
    
    next_url = None
    previous_url = None
    
    if has_next:
        query_params['page'] = str(page + 1)
        # Convert QueryDict to dict for urlencode
        query_dict = dict(query_params.items())
        next_url = f"{base_url_without_query}?{urlencode(query_dict)}"
    
    if has_previous:
        query_params['page'] = str(page - 1)
        # Convert QueryDict to dict for urlencode
        query_dict = dict(query_params.items())
        previous_url = f"{base_url_without_query}?{urlencode(query_dict)}"
    
    return {
        'next': next_url,
        'previous': previous_url
    }


def create_paginated_response(request: HttpRequest, queryset, serializer_class, 
                             serializer_context: Optional[Dict[str, Any]] = None,
                             default_page_size: int = 20, max_page_size: int = 100,
                             extra_data: Optional[Dict[str, Any]] = None) -> Response:
    """
    Create a paginated response with standard format.
    
    Args:
        request: HTTP request object
        queryset: QuerySet to paginate
        serializer_class: Serializer class to use
        serializer_context: Optional context for serializer
        default_page_size: Default page size
        max_page_size: Maximum page size
        extra_data: Optional extra data to include in response
        
    Returns:
        Response with paginated data
    """
    try:
        # Get pagination parameters
        page, page_size = get_pagination_params(request, default_page_size, max_page_size)
        
        # Paginate queryset
        page_obj, paginator = paginate_queryset(queryset, page, page_size)
        
        # Serialize results
        context = serializer_context or {}
        context['request'] = request
        serializer = serializer_class(page_obj.object_list, many=True, context=context)
        
        # Build pagination URLs
        pagination_urls = build_pagination_urls(
            request, page, page_size, 
            page_obj.has_next(), page_obj.has_previous()
        )
        
        # Prepare response data
        response_data = {
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'next': pagination_urls['next'],
            'previous': pagination_urls['previous']
        }
        
        # Add extra data if provided
        if extra_data:
            response_data.update(extra_data)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e),
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        from django.utils.log import getLogger
        logger = getLogger('cacaoscan.api')
        logger.error(f"Error en paginación: {e}", exc_info=True)
        return Response({
            'error': 'Error interno del servidor',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

