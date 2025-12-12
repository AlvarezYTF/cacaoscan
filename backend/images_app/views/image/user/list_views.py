"""
User image list views for CacaoScan API.
"""
import logging
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins.pagination_mixin import PaginationMixin
from api.serializers import (
    ErrorResponseSerializer,
    CacaoImageSerializer
)
from api.utils.decorators import handle_api_errors
from ..mixins import ImagePermissionMixin

logger = logging.getLogger("cacaoscan.api.images")


class ImagesListView(PaginationMixin, APIView, ImagePermissionMixin):
    """
    Endpoint para listar imágenes procesadas con paginación y filtros.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de imágenes procesadas por el usuario con paginación y filtros",
        operation_summary="Lista de imágenes",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filtrar por región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_STRING),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas y metadatos", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Lista de imágenes obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    @handle_api_errors(
        error_message="Error obteniendo lista de imágenes",
        log_message="Error obteniendo lista de imágenes"
    )
    def get(self, request):
        """
        Obtiene la lista de imágenes procesadas con paginación y filtros.
        """
        # Obtener parámetros de consulta (paginación se maneja en el mixin)
        region = request.GET.get('region')
        finca = request.GET.get('finca')
        processed = request.GET.get('processed')
        search = request.GET.get('search')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Construir queryset base según permisos
        queryset = self.get_user_images_queryset(request.user)
        
        # Aplicar filtros
        # Note: region filter removed - field doesn't exist in CacaoImage model
        
        if finca:
            queryset = queryset.filter(lote__finca__nombre__icontains=finca)
        
        if processed is not None:
            processed_bool = processed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(processed=processed_bool)
        
        if search:
            queryset = queryset.filter(
                Q(notas__icontains=search) |
                Q(lote__finca__nombre__icontains=search) |
                Q(lote__identificador__icontains=search) |
                Q(lote__variedad__icontains=search)
            )
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Ordenar por fecha de creación (más recientes primero)
        queryset = queryset.order_by('-created_at')
        
        # Paginar usando el mixin
        return self.paginate_queryset(
            request,
            queryset,
            CacaoImageSerializer
        )

