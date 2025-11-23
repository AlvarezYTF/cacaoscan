"""
Comparison views for model metrics in CacaoScan.
Handles model comparison operations.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from training.models import ModelMetrics
from api.serializers import (
    ModelMetricsSerializer,
    ModelComparisonSerializer,
    ErrorResponseSerializer
)
from core.utils import create_error_response, create_success_response

logger = logging.getLogger("cacaoscan.api")


class ModelComparisonView(APIView):
    """
    Endpoint for comparing two specific models.
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
        Compares two specific models.
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
            
            # Compare main metrics
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
            
            # Determine overall winner
            model_a_wins = 0
            model_b_wins = 0
            
            for metric, comparison in comparison_metrics.items():
                if comparison['better'] == 'model_a':
                    model_a_wins += 1
                else:
                    model_b_wins += 1
            
            winner = 'model_a' if model_a_wins > model_b_wins else 'model_b'
            
            # Calculate improvement percentage
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

