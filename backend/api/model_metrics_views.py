"""
Vistas API para métricas de modelos de CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg, Min, Max
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Dict, List, Any

from .models import ModelMetrics
# Importar desde apps modulares
try:
    from training.models import TrainingJob
except ImportError:
    TrainingJob = None
from .serializers import (
    ModelMetricsSerializer,
    ModelMetricsListSerializer,
    ModelMetricsCreateSerializer,
    ModelMetricsUpdateSerializer,
    ModelMetricsStatsSerializer,
    ModelPerformanceTrendSerializer,
    ModelComparisonSerializer,
    ErrorResponseSerializer
)
from .utils import create_error_response, create_success_response

logger = logging.getLogger("cacaoscan.api")


class ModelMetricsPagination(PageNumberPagination):
    """Paginación para métricas de modelos."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ModelMetricsListView(APIView):
    """
    Endpoint para listar métricas de modelos con filtros y paginación.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ModelMetricsPagination
    
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
        Lista métricas de modelos con filtros opcionales.
        """
        try:
            # Construir queryset base
            queryset = ModelMetrics.objects.all()
            
            # Aplicar filtros
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
            
            # Ordenar por fecha de creación descendente
            queryset = queryset.order_by('-created_at')
            
            # Aplicar paginación
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ModelMetricsListSerializer(page, many=True)
                return paginator.get_paginated_response({
                    'metrics': serializer.data,
                    'total_count': paginator.page.paginator.count,
                    'page_count': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                    'page_size': paginator.page_size
                })
            else:
                serializer = ModelMetricsListSerializer(queryset, many=True)
                return create_success_response(
                    data={
                        'metrics': serializer.data,
                        'total_count': queryset.count()
                    },
                    message="Métricas de modelos obtenidas exitosamente",
                    status_code=status.HTTP_200_OK
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
    Endpoint para obtener detalles de métricas de un modelo específico.
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
        Obtiene detalles completos de métricas de un modelo.
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
    Endpoint para crear nuevas métricas de modelos.
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
        Crea nuevas métricas de modelo.
        """
        try:
            serializer = ModelMetricsCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                # Asignar usuario creador
                metrics = serializer.save(created_by=request.user)
                
                # Si se marca como mejor modelo, actualizar otros modelos
                if metrics.is_best_model:
                    metrics.mark_as_best()
                
                # Si se marca como modelo en producción, actualizar otros modelos
                if metrics.is_production_model:
                    metrics.mark_as_production()
                
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
    Endpoint para actualizar métricas de modelos existentes.
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
        Actualiza métricas de modelo existente.
        """
        try:
            metrics = ModelMetrics.objects.get(id=metrics_id)
            serializer = ModelMetricsUpdateSerializer(metrics, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_metrics = serializer.save()
                
                # Si se marca como mejor modelo, actualizar otros modelos
                if updated_metrics.is_best_model:
                    updated_metrics.mark_as_best()
                
                # Si se marca como modelo en producción, actualizar otros modelos
                if updated_metrics.is_production_model:
                    updated_metrics.mark_as_production()
                
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
    Endpoint para eliminar métricas de modelos.
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
        Elimina métricas de modelo.
        """
        try:
            metrics = ModelMetrics.objects.get(id=metrics_id)
            metrics.delete()
            
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


class ModelMetricsStatsView(APIView):
    """
    Endpoint para obtener estadísticas de métricas de modelos.
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
        Obtiene estadísticas generales de métricas de modelos.
        """
        try:
            # Estadísticas básicas
            total_models = ModelMetrics.objects.count()
            
            # Estadísticas por tipo de modelo
            models_by_type = dict(ModelMetrics.objects.values_list('model_type').annotate(
                count=Count('id')
            ).values_list('model_type', 'count'))
            
            # Estadísticas por target
            models_by_target = dict(ModelMetrics.objects.values_list('target').annotate(
                count=Count('id')
            ).values_list('target', 'count'))
            
            # Mejores modelos y modelos en producción
            best_models_count = ModelMetrics.objects.filter(is_best_model=True).count()
            production_models_count = ModelMetrics.objects.filter(is_production_model=True).count()
            
            # Estadísticas de rendimiento
            performance_stats = ModelMetrics.objects.aggregate(
                average_r2_score=Avg('r2_score'),
                best_r2_score=Max('r2_score'),
                worst_r2_score=Min('r2_score')
            )
            
            # Modelos recientes
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
    Endpoint para obtener tendencia de rendimiento de un modelo específico.
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
        Obtiene tendencia de rendimiento de un modelo específico.
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
            
            # Obtener tendencia de rendimiento
            trend_data = ModelMetrics.get_performance_trend(model_name, target, metric_type)
            
            if not trend_data:
                return create_error_response(
                    message="No se encontraron datos de tendencia para el modelo especificado",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener métricas actuales
            current_metrics = ModelMetrics.objects.filter(
                model_name=model_name,
                target=target,
                metric_type=metric_type
            ).order_by('-created_at').first()
            
            current_performance = None
            if current_metrics:
                current_performance = current_metrics.performance_summary
            
            # Determinar tendencia de mejora
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


class ModelComparisonView(APIView):
    """
    Endpoint para comparar dos modelos específicos.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Compara dos modelos específicos",
        operation_summary="Comparar modelos",
        manual_parameters=[
            openapi.Parameter(
                'model_a_id',
                openapi.IN_QUERY,
                description="ID del primer modelo",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'model_b_id',
                openapi.IN_QUERY,
                description="ID del segundo modelo",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Comparación obtenida exitosamente",
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
            404: openapi.Response(description="Modelos no encontrados"),
            401: openapi.Response(description="No autorizado"),
        },
        tags=['Métricas de Modelos']
    )
    def get(self, request):
        """
        Compara dos modelos específicos.
        """
        try:
            model_a_id = request.GET.get('model_a_id')
            model_b_id = request.GET.get('model_b_id')
            
            if not model_a_id or not model_b_id:
                return create_error_response(
                    message="model_a_id y model_b_id son parámetros requeridos",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                model_a = ModelMetrics.objects.get(id=model_a_id)
                model_b = ModelMetrics.objects.get(id=model_b_id)
            except ModelMetrics.DoesNotExist:
                return create_error_response(
                    message="Uno o ambos modelos no encontrados",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Comparar métricas principales
            comparison_metrics = {
                'mae': {
                    'model_a': model_a.mae,
                    'model_b': model_b.mae,
                    'difference': round(model_a.mae - model_b.mae, 4),
                    'better': 'model_a' if model_a.mae < model_b.mae else 'model_b'
                },
                'rmse': {
                    'model_a': model_a.rmse,
                    'model_b': model_b.rmse,
                    'difference': round(model_a.rmse - model_b.rmse, 4),
                    'better': 'model_a' if model_a.rmse < model_b.rmse else 'model_b'
                },
                'r2_score': {
                    'model_a': model_a.r2_score,
                    'model_b': model_b.r2_score,
                    'difference': round(model_a.r2_score - model_b.r2_score, 4),
                    'better': 'model_a' if model_a.r2_score > model_b.r2_score else 'model_b'
                }
            }
            
            # Determinar ganador general
            model_a_wins = 0
            model_b_wins = 0
            
            for metric, comparison in comparison_metrics.items():
                if comparison['better'] == 'model_a':
                    model_a_wins += 1
                else:
                    model_b_wins += 1
            
            winner = 'model_a' if model_a_wins > model_b_wins else 'model_b'
            
            # Calcular porcentaje de mejora
            if winner == 'model_a':
                improvement_percentage = round(
                    ((model_a.r2_score - model_b.r2_score) / model_b.r2_score) * 100, 2
                )
            else:
                improvement_percentage = round(
                    ((model_b.r2_score - model_a.r2_score) / model_a.r2_score) * 100, 2
                )
            
            comparison_response = {
                'model_a': ModelMetricsSerializer(model_a).data,
                'model_b': ModelMetricsSerializer(model_b).data,
                'comparison_metrics': comparison_metrics,
                'winner': winner,
                'improvement_percentage': improvement_percentage
            }
            
            return create_success_response(
                data=comparison_response,
                message="Comparación de modelos obtenida exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error comparando modelos: {str(e)}")
            return create_error_response(
                message="Error interno comparando modelos",
                details={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BestModelsView(APIView):
    """
    Endpoint para obtener todos los mejores modelos.
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
        Obtiene todos los modelos marcados como mejores.
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
    Endpoint para obtener todos los modelos en producción.
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
        Obtiene todos los modelos marcados como en producción.
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


