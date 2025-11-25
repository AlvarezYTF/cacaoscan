"""
Statistics and cleanup views for reports in CacaoScan.
Handles report statistics and cleanup operations.
"""
import logging
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import AdminPermissionMixin
from reports.models import ReporteGenerado
from api.serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api")


class ReporteStatsView(APIView):
    """
    View for obtaining user report statistics.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de reportes del usuario",
        operation_summary="Estadísticas de reportes",
        responses={
            200: openapi.Response(description="Estadísticas obtenidas exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request):
        """Get report statistics."""
        try:
            # Basic statistics
            total_reportes = ReporteGenerado.objects.filter(usuario=request.user).count()
            reportes_completados = ReporteGenerado.objects.filter(usuario=request.user, estado='completado').count()
            reportes_generando = ReporteGenerado.objects.filter(usuario=request.user, estado='generando').count()
            reportes_fallidos = ReporteGenerado.objects.filter(usuario=request.user, estado='fallido').count()
            
            # Reports by type
            reportes_por_tipo = dict(
                ReporteGenerado.objects.filter(usuario=request.user)
                .values('tipo_reporte')
                .annotate(count=Count('id'))
                .values_list('tipo_reporte', 'count')
            )
            
            # Reports by format
            reportes_por_formato = dict(
                ReporteGenerado.objects.filter(usuario=request.user)
                .values('formato')
                .annotate(count=Count('id'))
                .values_list('formato', 'count')
            )
            
            # Recent reports (last 5)
            reportes_recientes = ReporteGenerado.objects.filter(usuario=request.user).order_by('-fecha_solicitud')[:5]
            reportes_recientes_data = []
            for reporte in reportes_recientes:
                reportes_recientes_data.append({
                    'id': reporte.id,
                    'titulo': reporte.titulo,
                    'tipo_reporte': reporte.tipo_reporte,
                    'formato': reporte.formato,
                    'estado': reporte.estado,
                    'fecha_solicitud': reporte.fecha_solicitud.isoformat(),
                })
            
            stats = {
                'total_reportes': total_reportes,
                'reportes_completados': reportes_completados,
                'reportes_generando': reportes_generando,
                'reportes_fallidos': reportes_fallidos,
                'reportes_por_tipo': reportes_por_tipo,
                'reportes_por_formato': reportes_por_formato,
                'reportes_recientes': reportes_recientes_data,
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"[WARNING] Error obteniendo estadísticas de reportes: {e}")
            # Return empty data instead of 500
            return Response({
                'total_reportes': 0,
                'reportes_completados': 0,
                'reportes_generando': 0,
                'reportes_fallidos': 0,
                'reportes_por_tipo': {},
                'reportes_por_formato': {},
                'reportes_recientes': []
            }, status=status.HTTP_200_OK)


class ReporteCleanupView(AdminPermissionMixin, APIView):
    """
    View for cleaning expired reports (administrators only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Limpia reportes expirados del sistema (solo administradores)",
        operation_summary="Limpiar reportes expirados",
        responses={
            200: openapi.Response(description="Limpieza completada exitosamente"),
            403: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def post(self, request):
        """Clean expired reports."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Clean expired reports
            cleaned_count = ReporteGenerado.limpiar_expirados()
            
            logger.info(f"Limpieza de reportes expirados completada por {request.user.username}: {cleaned_count} reportes eliminados")
            
            return Response({
                'message': f'Se limpiaron {cleaned_count} reportes expirados',
                'cleaned_count': cleaned_count,
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error limpiando reportes expirados: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

