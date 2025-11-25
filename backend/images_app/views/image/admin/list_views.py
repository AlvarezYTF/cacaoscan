"""
Admin image list views for CacaoScan API.
"""
import logging
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import PaginationMixin, AdminPermissionMixin
from api.serializers import (
    ErrorResponseSerializer,
    CacaoImageDetailSerializer
)
from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

logger = logging.getLogger("cacaoscan.api.images")


class AdminImagesListView(PaginationMixin, AdminPermissionMixin, APIView):
    """
    Endpoint para listar todas las imágenes del sistema con filtros avanzados (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista completa de imágenes del sistema con filtros avanzados (solo admins)",
        operation_summary="Lista global de imágenes",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY, description="Filtrar por ID de usuario", type=openapi.TYPE_INTEGER),
            openapi.Parameter('username', openapi.IN_QUERY, description="Filtrar por nombre de usuario", type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filtrar por región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_STRING),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('has_prediction', openapi.IN_QUERY, description="Filtrar por existencia de predicción", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas y metadatos", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('model_version', openapi.IN_QUERY, description="Filtrar por versión del modelo", type=openapi.TYPE_STRING),
            openapi.Parameter('min_confidence', openapi.IN_QUERY, description="Confianza mínima", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_confidence', openapi.IN_QUERY, description="Confianza máxima", type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description="Lista global de imágenes obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request):
        """
        Obtiene la lista completa de imágenes del sistema con filtros avanzados.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener parámetros de consulta (paginación se maneja en el mixin)
            user_id = request.GET.get('user_id')
            username = request.GET.get('username')
            region = request.GET.get('region')
            finca = request.GET.get('finca')
            processed = request.GET.get('processed')
            has_prediction = request.GET.get('has_prediction')
            search = request.GET.get('search')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            model_version = request.GET.get('model_version')
            min_confidence = request.GET.get('min_confidence')
            max_confidence = request.GET.get('max_confidence')
            
            # Construir queryset base con todas las imágenes
            # Optimizado: select_related para ForeignKeys, prefetch_related para OneToOne reverso
            queryset = CacaoImage.objects.all().select_related(
                'user',
                'finca',
                'finca__agricultor',
                'lote',
                'lote__finca',
                'lote__finca__agricultor'
            ).prefetch_related('prediction')
            
            # Aplicar filtros
            filters_applied = {}
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
                filters_applied['user_id'] = user_id
            
            if username:
                queryset = queryset.filter(user__username__icontains=username)
                filters_applied['username'] = username
            
            if region:
                queryset = queryset.filter(region__icontains=region)
                filters_applied['region'] = region
            
            if finca:
                queryset = queryset.filter(finca__icontains=finca)
                filters_applied['finca'] = finca
            
            if processed is not None:
                processed_bool = processed.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(processed=processed_bool)
                filters_applied['processed'] = processed_bool
            
            if has_prediction is not None:
                has_pred_bool = has_prediction.lower() in ['true', '1', 'yes']
                if has_pred_bool:
                    queryset = queryset.filter(prediction__isnull=False)
                else:
                    queryset = queryset.filter(prediction__isnull=True)
                filters_applied['has_prediction'] = has_pred_bool
            
            if search:
                queryset = queryset.filter(
                    Q(notas__icontains=search) |
                    Q(finca__icontains=search) |
                    Q(region__icontains=search) |
                    Q(lote_id__icontains=search) |
                    Q(variedad__icontains=search) |
                    Q(user__username__icontains=search)
                )
                filters_applied['search'] = search
            
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
                filters_applied['date_from'] = date_from
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
                filters_applied['date_to'] = date_to
            
            if model_version:
                queryset = queryset.filter(prediction__model_version=model_version)
                filters_applied['model_version'] = model_version
            
            if min_confidence is not None:
                queryset = queryset.filter(prediction__average_confidence__gte=min_confidence)
                filters_applied['min_confidence'] = float(min_confidence)
            
            if max_confidence is not None:
                queryset = queryset.filter(prediction__average_confidence__lte=max_confidence)
                filters_applied['max_confidence'] = float(max_confidence)
            
            # Ordenar por fecha de creación (más recientes primero)
            queryset = queryset.order_by('-created_at')
            
            # Paginar usando el mixin con datos extra
            return self.paginate_queryset(
                request,
                queryset,
                CacaoImageDetailSerializer,
                extra_data={'filters_applied': filters_applied}
            )
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista global de imágenes: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

