"""
Admin image statistics views for CacaoScan API.
"""
import logging
from datetime import timedelta
from django.db.models import Q, Count, Avg, Sum, F, Min, Max
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import AdminPermissionMixin
from api.serializers import ErrorResponseSerializer
from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

try:
    from django.contrib.auth.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()

logger = logging.getLogger("cacaoscan.api.images")


class AdminDatasetStatsView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener estadísticas globales del dataset (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas globales detalladas del dataset (solo admins)",
        operation_summary="Estadísticas globales del dataset",
        responses={
            200: openapi.Response(
                description="Estadísticas globales obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request):
        """
        Obtiene estadísticas globales detalladas del dataset.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Estadísticas generales del dataset
            total_images = CacaoImage.objects.count()
            processed_images = CacaoImage.objects.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            users_with_images = User.objects.filter(cacao_images__isnull=False).distinct().count()
            
            # Estadísticas de predicciones
            total_predictions = CacaoPrediction.objects.count()
            
            # Estadísticas por fechas
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            this_year = today - timedelta(days=365)
            
            images_this_week = CacaoImage.objects.filter(created_at__date__gte=this_week).count()
            images_this_month = CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            images_this_year = CacaoImage.objects.filter(created_at__date__gte=this_year).count()
            
            # Estadísticas por región
            region_stats = CacaoImage.objects.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True)),
                unique_users=Count('user', distinct=True)
            ).order_by('-count')[:20]
            
            # Estadísticas por finca
            finca_stats = CacaoImage.objects.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True)),
                unique_users=Count('user', distinct=True)
            ).order_by('-count')[:20]
            
            # Estadísticas por variedad
            variedad_stats = CacaoImage.objects.values('variedad').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:15]
            
            # Estadísticas de dimensiones y confianza
            avg_dimensions = CacaoPrediction.objects.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            # Calcular confidence usando agregaciones SQL
            # average_confidence = (confidence_alto + confidence_ancho + confidence_grosor + confidence_peso) / 4
            avg_confidence_expr = (
                F('confidence_alto') + F('confidence_ancho') + 
                F('confidence_grosor') + F('confidence_peso')
            ) / 4
            
            confidence_stats = CacaoPrediction.objects.aggregate(
                avg_confidence=Avg(avg_confidence_expr),
                min_confidence=Min(avg_confidence_expr),
                max_confidence=Max(avg_confidence_expr)
            )
            
            avg_confidence = float(confidence_stats.get('avg_confidence', 0) or 0)
            min_confidence = float(confidence_stats.get('min_confidence', 0) or 0)
            max_confidence = float(confidence_stats.get('max_confidence', 0) or 0)
            
            # Estadísticas por modelo usando agregaciones SQL
            model_stats = list(
                CacaoPrediction.objects.values('model_version').annotate(
                    count=Count('id'),
                    avg_confidence=Avg(avg_confidence_expr),
                    avg_processing_time=Avg('processing_time_ms')
                ).order_by('-count')
            )
            
            # Convertir a formato esperado
            model_stats = [
                {
                    'model_version': stat['model_version'],
                    'count': stat['count'],
                    'avg_confidence': round(float(stat['avg_confidence'] or 0), 3),
                    'avg_processing_time_ms': round(float(stat['avg_processing_time'] or 0), 0)
                }
                for stat in model_stats
            ]
            
            # Estadísticas por dispositivo
            device_stats = CacaoPrediction.objects.values('device_used').annotate(
                count=Count('id'),
                avg_processing_time=Avg('processing_time_ms')
            ).order_by('-count')
            
            # Top usuarios por actividad
            top_users = User.objects.annotate(
                image_count=Count('api_cacao_images'),
                processed_count=Count('api_cacao_images', filter=Q(api_cacao_images__processed=True))
            ).order_by('-image_count')[:10]
            
            # Estadísticas de archivos
            total_file_size = CacaoImage.objects.aggregate(
                total_size=Sum('file_size')
            )['total_size'] or 0
            
            avg_file_size = CacaoImage.objects.aggregate(
                avg_size=Avg('file_size')
            )['avg_size'] or 0
            
            # Estadísticas de calidad de datos
            images_with_metadata = CacaoImage.objects.filter(
                Q(finca__isnull=False) & ~Q(finca='') |
                Q(region__isnull=False) & ~Q(region='') |
                Q(variedad__isnull=False) & ~Q(variedad='')
            ).count()
            
            # Preparar respuesta
            stats = {
                'dataset_overview': {
                    'total_images': total_images,
                    'processed_images': processed_images,
                    'unprocessed_images': unprocessed_images,
                    'processing_rate': round((processed_images / total_images * 100), 2) if total_images > 0 else 0,
                    'total_users': total_users,
                    'active_users': active_users,
                    'users_with_images': users_with_images,
                    'total_predictions': total_predictions
                },
                'temporal_stats': {
                    'this_week': images_this_week,
                    'this_month': images_this_month,
                    'this_year': images_this_year,
                    'daily_average_this_month': round(images_this_month / 30, 2),
                    'weekly_average_this_year': round(images_this_year / 52, 2)
                },
                'geographic_stats': {
                    'top_regions': list(region_stats),
                    'top_fincas': list(finca_stats),
                    'unique_regions': CacaoImage.objects.values('region').distinct().count(),
                    'unique_fincas': CacaoImage.objects.values('finca').distinct().count()
                },
                'variety_stats': {
                    'top_varieties': list(variedad_stats),
                    'unique_varieties': CacaoImage.objects.values('variedad').distinct().count()
                },
                'quality_stats': {
                    'average_dimensions': {
                        'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                        'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                        'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                        'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                    },
                    'confidence_stats': {
                        'average': round(float(avg_confidence), 3),
                        'minimum': round(float(min_confidence), 3),
                        'maximum': round(float(max_confidence), 3)
                    },
                    'processing_stats': {
                        'average_time_ms': round(float(avg_dimensions['avg_processing_time'] or 0), 0)
                    }
                },
                'model_stats': {
                    'by_version': list(model_stats),
                    'by_device': list(device_stats)
                },
                'user_activity': {
                    'top_users': [
                        {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'image_count': user.image_count,
                            'processed_count': user.processed_count,
                            'processing_rate': round((user.processed_count / user.image_count * 100), 2) if user.image_count > 0 else 0
                        }
                        for user in top_users
                    ]
                },
                'storage_stats': {
                    'total_file_size_mb': round(total_file_size / (1024 * 1024), 2),
                    'average_file_size_mb': round(avg_file_size / (1024 * 1024), 2),
                    'images_with_metadata': images_with_metadata,
                    'metadata_completeness': round((images_with_metadata / total_images * 100), 2) if total_images > 0 else 0
                },
                'generated_at': timezone.now().isoformat(),
                'generated_by': request.user.username
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas globales del dataset: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

