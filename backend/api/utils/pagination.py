"""
Utility functions for pagination in CacaoScan API.
"""
from typing import Dict, Any, Optional, Tuple
from django.core.paginator import Paginator, Page
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import status


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
        return default_page_size, default_page_size


def paginate_queryset(queryset, page: int, page_size: int) -> Tuple[Page, Paginator]:
    """
    Paginate a queryset and return page object and paginator.
    
    Args:
        queryset: QuerySet to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (page_obj, paginator)
        
    Raises:
        ValueError: If page is invalid
    """
    paginator = Paginator(queryset, page_size)
    total_pages = paginator.num_pages
    
    # Validate page
    if page > total_pages and total_pages > 0:
        raise ValueError(f'Página {page} no existe. Total de páginas: {total_pages}')
    
    page_obj = paginator.get_page(page)
    return page_obj, paginator


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
    base_url = request.build_absolute_uri()
    
    # Preserve existing query parameters except page
    query_params = request.GET.copy()
    query_params['page_size'] = str(page_size)
    
    next_url = None
    previous_url = None
    
    if has_next:
        query_params['page'] = str(page + 1)
        next_url = f"{base_url.split('?')[0]}?{query_params.urlencode()}"
    
    if has_previous:
        query_params['page'] = str(page - 1)
        previous_url = f"{base_url.split('?')[0]}?{query_params.urlencode()}"
    
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

