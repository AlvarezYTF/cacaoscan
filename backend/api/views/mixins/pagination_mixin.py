"""
Pagination mixin for API views.
"""
"""
Pagination mixin for API views.
"""
from typing import Dict, Any, Optional, Tuple, Callable, Union, Type
from django.core.paginator import Paginator, Page
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import Serializer

from ...utils.pagination import (
    get_pagination_params,
    paginate_queryset,
    build_pagination_urls
)


class PaginationMixin:
    """
    Mixin that provides pagination functionality for API views.
    
    Usage:
        class MyListView(PaginationMixin, APIView):
            def get(self, request):
                queryset = MyModel.objects.all()
                serializer_class = MySerializer
                return self.paginate_queryset(request, queryset, serializer_class)
    """
    
    default_page_size: int = 20
    max_page_size: int = 100
    
    def get_pagination_params(self, request: HttpRequest) -> Tuple[int, int]:
        """
        Get pagination parameters from request.
        
        Args:
            request: HTTP request object
            
        Returns:
            Tuple of (page, page_size)
        """
        return get_pagination_params(
            request, 
            default_page_size=getattr(self, 'default_page_size', 20),
            max_page_size=getattr(self, 'max_page_size', 100)
        )
    
    def paginate_queryset(self, request: HttpRequest, queryset, 
                         serializer_class: Optional[Type[Serializer]] = None,
                         serializer_context: Optional[Dict[str, Any]] = None,
                         serializer_func: Optional[Callable] = None,
                         extra_data: Optional[Dict[str, Any]] = None) -> Response:
        """
        Paginate a queryset and return a paginated response.
        
        Args:
            request: HTTP request object
            queryset: QuerySet to paginate
            serializer_class: Serializer class to use
            serializer_context: Optional context for serializer
            extra_data: Optional extra data to include in response
            
        Returns:
            Response with paginated data
        """
        try:
            # Get pagination parameters
            page, page_size = self.get_pagination_params(request)
            
            # Paginate queryset
            page_obj, paginator = paginate_queryset(queryset, page, page_size)
            
            # Serialize results
            if serializer_func:
                # Use custom serialization function
                serialized_data = serializer_func(page_obj.object_list)
            elif serializer_class:
                # Use serializer class
                context = serializer_context or {}
                context['request'] = request
                serializer = serializer_class(page_obj.object_list, many=True, context=context)
                serialized_data = serializer.data
            else:
                raise ValueError("Either serializer_class or serializer_func must be provided")
            
            # Build pagination URLs
            pagination_urls = build_pagination_urls(
                request, page, page_size,
                page_obj.has_next(), page_obj.has_previous()
            )
            
            # Prepare response data
            response_data = {
                'results': serialized_data,
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
            import logging
            logger = logging.getLogger('cacaoscan.api')
            logger.error(f"Error en paginación: {e}", exc_info=True)
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

