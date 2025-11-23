"""
CRUD views for model metrics in CacaoScan.
Handles listing, creating, retrieving, updating, and deleting model metrics.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from training.models import ModelMetrics
from api.utils.model_imports import get_model_safely
from api.serializers import (
    ModelMetricsSerializer,
    ModelMetricsListSerializer,
    ModelMetricsCreateSerializer,
    ModelMetricsUpdateSerializer,
    ErrorResponseSerializer
)
from core.utils import create_error_response, create_success_response
from ..mixins import PaginationMixin

TrainingJob = get_model_safely('training.models.TrainingJob')
logger = logging.getLogger("cacaoscan.api")


class ModelMetricsListView(PaginationMixin, APIView):
    """
    Endpoint for listing model metrics with filters and pagination.
    """
    permission_classes = [IsAuthenticated]
    default_page_size = 20
    max_page_size = 100
    
    @swagger_auto_schema(
        operation_description="Lista métricas de modelos con filtros opcionales",
        operation_summary="Listar métricas de modelos",
        manual_parameters=[
            openapi.Parameter(
                'model_name',
                openapi.IN_QUERY,
                description="Filtrar por nombre del modelo",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'model_type',
                openapi.IN_QUERY,
                description="Filtrar por tipo de modelo",
                type=openapi.TYPE_STRING,
                enum=['regression', 'classification', 'segmentation', 'incremental']
            ),
            openapi.Parameter(
                'target',
                openapi.IN_QUERY,
                description="Filtrar por variable objetivo",
                type=openapi.TYPE_STRING,
                enum=['alto', 'ancho', 'grosor', 'peso', 'calidad', 'variedad']
            ),
            openapi.Parameter(
                'metric_type',
                openapi.IN_QUERY,
                description="Filtrar por tipo de métricas",
                type=openapi.TYPE_STRING,
                enum=['training', 'validation', 'test', 'incremental']
            ),
            openapi.Parameter(
                'is_best',
                openapi.IN_QUERY,
                description="Filtrar solo mejores modelos",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'is_production',
                openapi.IN_QUERY,
                description="Filtrar solo modelos en producción",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Número de página",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Tamaño de página",
                type=openapi.TYPE_INTEGER,
                default=20
            ),
        ],
        responses={
            200: openapi.Response(
                description="Lista de métricas obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def get(self, request):
        """
        Lists model metrics with optional filters.
        """
        try:
            # Build base queryset
            queryset = ModelMetrics.objects.all()
            
            # Apply filters
            model_name = request.GET.get('model_name')
            if model_name:
                queryset = queryset.filter(model_name__icontains=model_name)
            
            model_type = request.GET.get('model_type')
            if model_type:
                queryset = queryset.filter(model_type=model_type)
            
            target = request.GET.get('target')
            if target:
                queryset = queryset.filter(target=target)
            
            metric_type = request.GET.get('metric_type')
            if metric_type:
                queryset = queryset.filter(metric_type=metric_type)
            
            is_best = request.GET.get('is_best')
            if is_best is not None:
                queryset = queryset.filter(is_best_model=is_best.lower() == 'true')
            
            is_production = request.GET.get('is_production')
            if is_production is not None:
                queryset = queryset.filter(is_production_model=is_production.lower() == 'true')
            
            # Order by creation date descending
            queryset = queryset.order_by('-created_at')
            
            # Paginate using mixin
            return self.paginate_queryset(
                request,
                queryset,
                ModelMetricsListSerializer,
                extra_data=None
            )
                
        except Exception as e:
            logger.error(f"Error listando métricas de modelos: {str(e)}")
            return create_error_response(
                message="Error interno listando métricas",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelMetricsDetailView(APIView):
    """
    Endpoint for retrieving details of a specific model's metrics.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene detalles completos de métricas de un modelo",
        operation_summary="Detalles de métricas de modelo",
        responses={
            200: openapi.Response(
                description="Detalles obtenidos exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(description="Métricas no encontradas"),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def get(self, request, metrics_id):
        """
        Gets complete details of a model's metrics.
        """
        try:
            metrics = ModelMetrics.objects.get(id=metrics_id)
            serializer = ModelMetricsSerializer(metrics)
            
            return create_success_response(
                data=serializer.data,
                message="Detalles de métricas obtenidos exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except ModelMetrics.DoesNotExist:
            return create_error_response(
                message="Métricas de modelo no encontradas",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error obteniendo detalles de métricas: {str(e)}")
            return create_error_response(
                message="Error interno obteniendo detalles",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelMetricsCreateView(APIView):
    """
    Endpoint for creating new model metrics.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Crea nuevas métricas de modelo",
        operation_summary="Crear métricas de modelo",
        request_body=ModelMetricsCreateSerializer,
        responses={
            201: openapi.Response(
                description="Métricas creadas exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(description="Datos inválidos"),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def post(self, request):
        """
        Creates new model metrics.
        """
        try:
            serializer = ModelMetricsCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                # Assign creator user
                metrics = serializer.save(created_by=request.user)
                
                # If marked as best model, update other models
                if metrics.is_best_model:
                    metrics.mark_as_best()
                
                # If marked as production model, update other models
                if metrics.is_production_model:
                    metrics.mark_as_production()
                
                # Invalidate metrics cache when new metrics are created
                from core.utils import invalidate_latest_metrics_cache
                invalidate_latest_metrics_cache()
                
                response_serializer = ModelMetricsSerializer(metrics)
                
                return create_success_response(
                    data=response_serializer.data,
                    message="Métricas de modelo creadas exitosamente",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return create_error_response(
                    message="Datos de métricas inválidos",
                    details=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error creando métricas de modelo: {str(e)}")
            return create_error_response(
                message="Error interno creando métricas",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelMetricsUpdateView(APIView):
    """
    Endpoint for updating existing model metrics.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza métricas de modelo existente",
        operation_summary="Actualizar métricas de modelo",
        request_body=ModelMetricsUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Métricas actualizadas exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(description="Datos inválidos"),
            404: openapi.Response(description="Métricas no encontradas"),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def put(self, request, metrics_id):
        """
        Updates existing model metrics.
        """
        try:
            metrics = ModelMetrics.objects.get(id=metrics_id)
            serializer = ModelMetricsUpdateSerializer(metrics, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_metrics = serializer.save()
                
                # If marked as best model, update other models
                if updated_metrics.is_best_model:
                    updated_metrics.mark_as_best()
                
                # If marked as production model, update other models
                if updated_metrics.is_production_model:
                    updated_metrics.mark_as_production()
                
                # Invalidate metrics cache when metrics are updated
                from core.utils import invalidate_latest_metrics_cache
                invalidate_latest_metrics_cache()
                
                response_serializer = ModelMetricsSerializer(updated_metrics)
                
                return create_success_response(
                    data=response_serializer.data,
                    message="Métricas de modelo actualizadas exitosamente",
                    status_code=status.HTTP_200_OK
                )
            else:
                return create_error_response(
                    message="Datos de métricas inválidos",
                    details=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        except ModelMetrics.DoesNotExist:
            return create_error_response(
                message="Métricas de modelo no encontradas",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error actualizando métricas de modelo: {str(e)}")
            return create_error_response(
                message="Error interno actualizando métricas",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelMetricsDeleteView(APIView):
    """
    Endpoint for deleting model metrics.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina métricas de modelo",
        operation_summary="Eliminar métricas de modelo",
        responses={
            200: openapi.Response(
                description="Métricas eliminadas exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(description="Métricas no encontradas"),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def delete(self, request, metrics_id):
        """
        Deletes model metrics.
        """
        try:
            metrics = ModelMetrics.objects.get(id=metrics_id)
            metrics.delete()
            
            # Invalidate metrics cache when metrics are deleted
            from core.utils import invalidate_latest_metrics_cache
            invalidate_latest_metrics_cache()
            
            return create_success_response(
                data={},
                message="Métricas de modelo eliminadas exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except ModelMetrics.DoesNotExist:
            return create_error_response(
                message="Métricas de modelo no encontradas",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error eliminando métricas de modelo: {str(e)}")
            return create_error_response(
                message="Error interno eliminando métricas",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

