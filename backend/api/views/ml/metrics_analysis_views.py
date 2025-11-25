"""
Analysis views for model metrics in CacaoScan.
Handles statistics, performance trends, and best/production models.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Min, Max
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from training.models import ModelMetrics
from api.serializers import (
    ModelMetricsSerializer,
    ModelMetricsListSerializer,
    ModelMetricsStatsSerializer,
    ModelPerformanceTrendSerializer,
    ErrorResponseSerializer
)
from core.utils import create_error_response, create_success_response

logger = logging.getLogger("cacaoscan.api")


class ModelMetricsStatsView(APIView):
    """
    Endpoint for obtaining model metrics statistics.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas generales de métricas de modelos",
        operation_summary="Estadísticas de métricas de modelos",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
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
        Gets general statistics of model metrics.
        """
        try:
            # Basic statistics
            total_models = ModelMetrics.objects.count()
            
            # Statistics by model type
            models_by_type = dict(ModelMetrics.objects.values_list('model_type').annotate(
                count=Count('id')
            ).values_list('model_type', 'count'))
            
            # Statistics by target
            models_by_target = dict(ModelMetrics.objects.values_list('target').annotate(
                count=Count('id')
            ).values_list('target', 'count'))
            
            # Best models and production models
            best_models_count = ModelMetrics.objects.filter(is_best_model=True).count()
            production_models_count = ModelMetrics.objects.filter(is_production_model=True).count()
            
            # Performance statistics
            performance_stats = ModelMetrics.objects.aggregate(
                average_r2_score=Avg('r2_score'),
                best_r2_score=Max('r2_score'),
                worst_r2_score=Min('r2_score')
            )
            
            # Recent models
            recent_models = ModelMetrics.objects.order_by('-created_at')[:5]
            recent_models_data = ModelMetricsListSerializer(recent_models, many=True).data
            
            stats_data = {
                'total_models': total_models,
                'models_by_type': models_by_type,
                'models_by_target': models_by_target,
                'best_models_count': best_models_count,
                'production_models_count': production_models_count,
                'average_r2_score': round(performance_stats['average_r2_score'] or 0, 4),
                'best_r2_score': round(performance_stats['best_r2_score'] or 0, 4),
                'worst_r2_score': round(performance_stats['worst_r2_score'] or 0, 4),
                'recent_models': recent_models_data
            }
            
            return create_success_response(
                data=stats_data,
                message="Estadísticas de métricas obtenidas exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de métricas: {str(e)}")
            return create_error_response(
                message="Error interno obteniendo estadísticas",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelPerformanceTrendView(APIView):
    """
    Endpoint for obtaining performance trend of a specific model.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene tendencia de rendimiento de un modelo específico",
        operation_summary="Tendencia de rendimiento de modelo",
        manual_parameters=[
            openapi.Parameter(
                'model_name',
                openapi.IN_QUERY,
                description="Nombre del modelo",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'target',
                openapi.IN_QUERY,
                description="Variable objetivo",
                type=openapi.TYPE_STRING,
                enum=['alto', 'ancho', 'grosor', 'peso', 'calidad', 'variedad'],
                required=True
            ),
            openapi.Parameter(
                'metric_type',
                openapi.IN_QUERY,
                description="Tipo de métricas",
                type=openapi.TYPE_STRING,
                enum=['training', 'validation', 'test', 'incremental'],
                default='validation'
            ),
        ],
        responses={
            200: openapi.Response(
                description="Tendencia obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(description="Parámetros inválidos"),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def get(self, request):
        """
        Gets performance trend of a specific model.
        """
        try:
            model_name = request.GET.get('model_name')
            target = request.GET.get('target')
            metric_type = request.GET.get('metric_type', 'validation')
            
            if not model_name or not target:
                return create_error_response(
                    message="model_name y target son parámetros requeridos",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Get performance trend
            trend_data = ModelMetrics.get_performance_trend(model_name, target, metric_type)
            
            if not trend_data:
                return create_error_response(
                    message="No se encontraron datos de tendencia para el modelo especificado",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Get current metrics
            current_metrics = ModelMetrics.objects.filter(
                model_name=model_name,
                target=target,
                metric_type=metric_type
            ).order_by('-created_at').first()
            
            current_performance = None
            if current_metrics:
                current_performance = current_metrics.performance_summary
            
            # Determine improvement trend
            if len(trend_data) >= 2:
                latest_r2 = trend_data[-1]['r2_score']
                previous_r2 = trend_data[-2]['r2_score']
                improvement_trend = "mejorando" if latest_r2 > previous_r2 else "empeorando"
            else:
                improvement_trend = "insuficientes datos"
            
            trend_response = {
                'model_name': model_name,
                'target': target,
                'metric_type': metric_type,
                'trend_data': trend_data,
                'current_performance': current_performance,
                'improvement_trend': improvement_trend
            }
            
            return create_success_response(
                data=trend_response,
                message="Tendencia de rendimiento obtenida exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo tendencia de rendimiento: {str(e)}")
            return create_error_response(
                message="Error interno obteniendo tendencia",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BestModelsView(APIView):
    """
    Endpoint for obtaining all best models.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene todos los modelos marcados como mejores",
        operation_summary="Mejores modelos",
        responses={
            200: openapi.Response(
                description="Mejores modelos obtenidos exitosamente",
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
        Gets all models marked as best.
        """
        try:
            best_models = ModelMetrics.get_best_models()
            serializer = ModelMetricsSerializer(best_models, many=True)
            
            return create_success_response(
                data={
                    'best_models': serializer.data,
                    'count': best_models.count()
                },
                message="Mejores modelos obtenidos exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo mejores modelos: {str(e)}")
            return create_error_response(
                message="Error interno obteniendo mejores modelos",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductionModelsView(APIView):
    """
    Endpoint for obtaining all production models.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene todos los modelos marcados como en producción",
        operation_summary="Modelos en producción",
        responses={
            200: openapi.Response(
                description="Modelos en producción obtenidos exitosamente",
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
        Gets all models marked as in production.
        """
        try:
            production_models = ModelMetrics.get_production_models()
            serializer = ModelMetricsSerializer(production_models, many=True)
            
            return create_success_response(
                data={
                    'production_models': serializer.data,
                    'count': production_models.count()
                },
                message="Modelos en producción obtenidos exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo modelos en producción: {str(e)}")
            return create_error_response(
                message="Error interno obteniendo modelos en producción",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

