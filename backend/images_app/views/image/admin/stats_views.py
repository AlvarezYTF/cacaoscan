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
            
            # Estadísticas básicas del dataset
            basic_stats = self._get_basic_dataset_stats()
            temporal_stats = self._get_temporal_stats()
            
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
            
            # Estadísticas de dimensiones
            avg_dimensions = CacaoPrediction.objects.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            confidence_stats = self._get_confidence_stats()
            model_stats = self._get_model_stats()
            device_stats = self._get_device_stats()
            top_users = self._get_top_users()
            file_stats = self._get_file_stats()
            images_with_metadata = self._get_metadata_completeness()
            
            stats = {
                'dataset_overview': {
                    **basic_stats,
                    'processing_rate': round((basic_stats['processed_images'] / basic_stats['total_images'] * 100), 2) if basic_stats['total_images'] > 0 else 0
                },
                'temporal_stats': temporal_stats,
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
                    'confidence_stats': confidence_stats,
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
                    'total_file_size_mb': round(file_stats['total_size'] / (1024 * 1024), 2),
                    'average_file_size_mb': round(file_stats['avg_size'] / (1024 * 1024), 2),
                    'images_with_metadata': images_with_metadata,
                    'metadata_completeness': round((images_with_metadata / basic_stats['total_images'] * 100), 2) if basic_stats['total_images'] > 0 else 0
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
    
    def _get_basic_dataset_stats(self):
        """Get basic dataset statistics."""
        return {
            'total_images': CacaoImage.objects.count(),
            'processed_images': CacaoImage.objects.filter(processed=True).count(),
            'pending_images': CacaoImage.objects.filter(processed=False).count(),
        }
    
    def _get_temporal_stats(self):
        """Get temporal statistics."""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        return {
            'last_24h': CacaoImage.objects.filter(created_at__gte=last_24h).count(),
            'last_7d': CacaoImage.objects.filter(created_at__gte=last_7d).count(),
            'last_30d': CacaoImage.objects.filter(created_at__gte=last_30d).count(),
        }
    
    def _get_confidence_stats(self):
        """Get confidence statistics."""
        queryset = CacaoPrediction.objects.all()
        return {
            'avg_confidence': round(float(queryset.aggregate(avg=Avg('average_confidence'))['avg'] or 0) * 100, 2),
            'min_confidence': round(float(queryset.aggregate(min=Min('average_confidence'))['min'] or 0) * 100, 2),
            'max_confidence': round(float(queryset.aggregate(max=Max('average_confidence'))['max'] or 0) * 100, 2),
        }
    
    def _get_model_stats(self):
        """Get model statistics."""
        return CacaoPrediction.objects.values('model_version').annotate(
            count=Count('id'),
            avg_confidence=Avg('average_confidence')
        ).order_by('-count')
    
    def _get_device_stats(self):
        """Get device statistics."""
        return CacaoPrediction.objects.values('device_used').annotate(
            count=Count('id'),
            avg_processing_time=Avg('processing_time_ms')
        ).order_by('-count')
    
    def _get_top_users(self):
        """Get top users by activity."""
        return User.objects.annotate(
            image_count=Count('api_cacao_images'),
            processed_count=Count('api_cacao_images', filter=Q(api_cacao_images__processed=True))
        ).order_by('-image_count')[:10]
    
    def _get_file_stats(self):
        """Get file statistics."""
        total_size = CacaoImage.objects.aggregate(total_size=Sum('file_size'))['total_size'] or 0
        avg_size = CacaoImage.objects.aggregate(avg_size=Avg('file_size'))['avg_size'] or 0
        return {'total_size': total_size, 'avg_size': avg_size}
    
    def _get_metadata_completeness(self):
        """Get metadata completeness statistics."""
        return CacaoImage.objects.filter(
            Q(finca__isnull=False) & ~Q(finca='') |
            Q(region__isnull=False) & ~Q(region='') |
            Q(variedad__isnull=False) & ~Q(variedad='')
        ).count()

