"""
User image statistics views for CacaoScan API.
"""
import logging
from datetime import timedelta
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import ErrorResponseSerializer
from api.utils.model_imports import get_models_safely
from ..mixins import ImagePermissionMixin

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

logger = logging.getLogger("cacaoscan.api.images")


class ImagesStatsView(APIView, ImagePermissionMixin):
    """
    Endpoint para obtener estadísticas detalladas de imágenes procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas detalladas de imágenes procesadas por el usuario",
        operation_summary="Estadísticas de imágenes",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request):
        """
        Obtiene estadísticas detalladas de imágenes procesadas.
        """
        try:
            # Obtener queryset base según permisos
            user_images = self.get_user_images_queryset(request.user)
            
            # Estadísticas básicas
            total_images = user_images.count()
            processed_images = user_images.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por fecha
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            processed_today = user_images.filter(
                created_at__date=today, 
                processed=True
            ).count()
            
            processed_this_week = user_images.filter(
                created_at__date__gte=this_week,
                processed=True
            ).count()
            
            processed_this_month = user_images.filter(
                created_at__date__gte=this_month,
                processed=True
            ).count()
            
            # Estadísticas de predicciones
            # Use SQL aggregation to calculate average_confidence
            # average_confidence = (confidence_alto + confidence_ancho + confidence_grosor + confidence_peso) / 4
            avg_confidence_expr = (
                F('confidence_alto') + F('confidence_ancho') + 
                F('confidence_grosor') + F('confidence_peso')
            ) / 4
            
            predictions = CacaoPrediction.objects.filter(image__user_id=request.user.id)
            
            prediction_stats = predictions.aggregate(
                avg_confidence=Avg(avg_confidence_expr),
                avg_time=Avg('processing_time_ms')
            )
            
            avg_confidence = float(prediction_stats.get('avg_confidence', 0) or 0)
            avg_processing_time = float(prediction_stats.get('avg_time', 0) or 0)
            
            # Estadísticas por región (a través de lote -> finca -> municipio -> departamento)
            # Solo si las relaciones existen
            try:
                region_stats = user_images.filter(
                    lote__finca__municipio__departamento__isnull=False
                ).values('lote__finca__municipio__departamento__nombre').annotate(
                    count=Count('id'),
                    processed_count=Count('id', filter=Q(processed=True))
                ).order_by('-count')
            except Exception:
                region_stats = []
            
            # Estadísticas por finca (a través de lote)
            # Solo si las relaciones existen
            try:
                finca_stats = user_images.filter(
                    lote__finca__isnull=False
                ).values('lote__finca__id', 'lote__finca__nombre').annotate(
                    count=Count('id'),
                    processed_count=Count('id', filter=Q(processed=True))
                ).order_by('-count')[:10]  # Top 10 fincas
            except Exception:
                finca_stats = []
            
            # Estadísticas de dimensiones promedio
            avg_dimensions = predictions.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g')
            )
            
            # Calcular processing_rate
            processing_rate = (processed_images / total_images * 100) if total_images > 0 else 0
            
            # Preparar respuesta
            stats = {
                'total_images': total_images,
                'processed_images': processed_images,
                'unprocessed_images': unprocessed_images,
                'processing_rate': round(float(processing_rate), 2),
                'processed_today': processed_today,
                'processed_this_week': processed_this_week,
                'processed_this_month': processed_this_month,
                'average_confidence': round(float(avg_confidence), 3),
                'average_processing_time_ms': round(float(avg_processing_time), 0),
                'region_stats': list(region_stats),
                'top_fincas': list(finca_stats),
                'average_dimensions': {
                    'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                    'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                    'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                    'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                }
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo estadísticas de imágenes: {e}", exc_info=True)
            # Retornar datos vacíos en lugar de 500 para evitar romper el frontend
            return Response({
                'total_images': 0,
                'processed_images': 0,
                'unprocessed_images': 0,
                'processing_rate': 0,
                'processed_today': 0,
                'processed_this_week': 0,
                'processed_this_month': 0,
                'average_confidence': 0,
                'average_processing_time_ms': 0,
                'region_stats': [],
                'top_fincas': [],
                'average_dimensions': {
                    'alto_mm': 0,
                    'ancho_mm': 0,
                    'grosor_mm': 0,
                    'peso_g': 0
                }
            }, status=status.HTTP_200_OK)

