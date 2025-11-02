"""
Vistas para generaciÃ³n de reportes PDF.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .pdf_generator import CacaoReportPDFGenerator
from api.models import CacaoImage
from api.serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.reports")


class GenerateQualityReportView(APIView):
    """
    Endpoint para generar reporte de calidad en PDF.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Genera un reporte de calidad de cacao en PDF",
        operation_summary="Generar reporte de calidad PDF",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date_from': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha desde (YYYY-MM-DD)"),
                'date_to': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha hasta (YYYY-MM-DD)"),
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por regiÃ³n"),
                'finca': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por finca"),
                'min_confidence': openapi.Schema(type=openapi.TYPE_NUMBER, description="Confianza mÃ­nima"),
                'max_confidence': openapi.Schema(type=openapi.TYPE_NUMBER, description="Confianza mÃ¡xima"),
            }
        ),
        responses={
            200: openapi.Response(
                description="PDF generado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def post(self, request):
        """
        Genera un reporte de calidad de cacao en PDF.
        """
        try:
            # Obtener imÃ¡genes del usuario con predicciones
            images_queryset = CacaoImage.objects.filter(
                user=request.user,
                prediction__isnull=False
            ).select_related('prediction')
            
            # Aplicar filtros
            filters = {}
            if 'date_from' in request.data and request.data['date_from']:
                images_queryset = images_queryset.filter(created_at__date__gte=request.data['date_from'])
                filters['Fecha desde'] = request.data['date_from']
            
            if 'date_to' in request.data and request.data['date_to']:
                images_queryset = images_queryset.filter(created_at__date__lte=request.data['date_to'])
                filters['Fecha hasta'] = request.data['date_to']
            
            if 'region' in request.data and request.data['region']:
                images_queryset = images_queryset.filter(region__icontains=request.data['region'])
                filters['RegiÃ³n'] = request.data['region']
            
            if 'finca' in request.data and request.data['finca']:
                images_queryset = images_queryset.filter(finca__icontains=request.data['finca'])
                filters['Finca'] = request.data['finca']
            
            if 'min_confidence' in request.data and request.data['min_confidence']:
                images_queryset = images_queryset.filter(prediction__average_confidence__gte=request.data['min_confidence'])
                filters['Confianza mÃ­nima'] = f"{request.data['min_confidence']:.2%}"
            
            if 'max_confidence' in request.data and request.data['max_confidence']:
                images_queryset = images_queryset.filter(prediction__average_confidence__lte=request.data['max_confidence'])
                filters['Confianza mÃ¡xima'] = f"{request.data['max_confidence']:.2%}"
            
            # Generar PDF
            generator = CacaoReportPDFGenerator()
            pdf_buffer = generator.generate_quality_report(images_queryset, request.user, filters)
            
            # Preparar nombre del archivo
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_calidad_{request.user.username}_{timestamp}.pdf"
            
            logger.info(f"Reporte de calidad generado para usuario {request.user.username}. "
                       f"ImÃ¡genes incluidas: {images_queryset.count()}")
            
            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=filename,
                content_type='application/pdf'
            )
            
        except Exception as e:
            logger.error(f"Error generando reporte de calidad para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor al generar el reporte',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateDefectsReportView(APIView):
    """
    Endpoint para generar reporte de defectos en PDF.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Genera un reporte de defectos de cacao en PDF",
        operation_summary="Generar reporte de defectos PDF",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date_from': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha desde (YYYY-MM-DD)"),
                'date_to': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha hasta (YYYY-MM-DD)"),
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por regiÃ³n"),
                'finca': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por finca"),
                'confidence_threshold': openapi.Schema(type=openapi.TYPE_NUMBER, description="Umbral de confianza para defectos", default=0.7),
            }
        ),
        responses={
            200: openapi.Response(
                description="PDF generado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def post(self, request):
        """
        Genera un reporte de defectos de cacao en PDF.
        """
        try:
            # Obtener imÃ¡genes del usuario con predicciones
            images_queryset = CacaoImage.objects.filter(
                user=request.user,
                prediction__isnull=False
            ).select_related('prediction')
            
            # Aplicar filtros
            filters = {}
            if 'date_from' in request.data and request.data['date_from']:
                images_queryset = images_queryset.filter(created_at__date__gte=request.data['date_from'])
                filters['Fecha desde'] = request.data['date_from']
            
            if 'date_to' in request.data and request.data['date_to']:
                images_queryset = images_queryset.filter(created_at__date__lte=request.data['date_to'])
                filters['Fecha hasta'] = request.data['date_to']
            
            if 'region' in request.data and request.data['region']:
                images_queryset = images_queryset.filter(region__icontains=request.data['region'])
                filters['RegiÃ³n'] = request.data['region']
            
            if 'finca' in request.data and request.data['finca']:
                images_queryset = images_queryset.filter(finca__icontains=request.data['finca'])
                filters['Finca'] = request.data['finca']
            
            # Generar PDF
            generator = CacaoReportPDFGenerator()
            pdf_buffer = generator.generate_defects_report(images_queryset, request.user, filters)
            
            # Preparar nombre del archivo
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_defectos_{request.user.username}_{timestamp}.pdf"
            
            logger.info(f"Reporte de defectos generado para usuario {request.user.username}. "
                       f"ImÃ¡genes analizadas: {images_queryset.count()}")
            
            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=filename,
                content_type='application/pdf'
            )
            
        except Exception as e:
            logger.error(f"Error generando reporte de defectos para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor al generar el reporte',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GeneratePerformanceReportView(APIView):
    """
    Endpoint para generar reporte de rendimiento en PDF.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Genera un reporte de rendimiento de anÃ¡lisis en PDF",
        operation_summary="Generar reporte de rendimiento PDF",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date_from': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha desde (YYYY-MM-DD)"),
                'date_to': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha hasta (YYYY-MM-DD)"),
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por regiÃ³n"),
                'finca': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por finca"),
            }
        ),
        responses={
            200: openapi.Response(
                description="PDF generado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def post(self, request):
        """
        Genera un reporte de rendimiento de anÃ¡lisis en PDF.
        """
        try:
            # Obtener imÃ¡genes del usuario
            images_queryset = CacaoImage.objects.filter(user=request.user)
            
            # Aplicar filtros
            filters = {}
            if 'date_from' in request.data and request.data['date_from']:
                images_queryset = images_queryset.filter(created_at__date__gte=request.data['date_from'])
                filters['Fecha desde'] = request.data['date_from']
            
            if 'date_to' in request.data and request.data['date_to']:
                images_queryset = images_queryset.filter(created_at__date__lte=request.data['date_to'])
                filters['Fecha hasta'] = request.data['date_to']
            
            if 'region' in request.data and request.data['region']:
                images_queryset = images_queryset.filter(region__icontains=request.data['region'])
                filters['RegiÃ³n'] = request.data['region']
            
            if 'finca' in request.data and request.data['finca']:
                images_queryset = images_queryset.filter(finca__icontains=request.data['finca'])
                filters['Finca'] = request.data['finca']
            
            # Generar PDF
            generator = CacaoReportPDFGenerator()
            pdf_buffer = generator.generate_performance_report(images_queryset, request.user, filters)
            
            # Preparar nombre del archivo
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_rendimiento_{request.user.username}_{timestamp}.pdf"
            
            logger.info(f"Reporte de rendimiento generado para usuario {request.user.username}. "
                       f"PerÃ­odo analizado: {images_queryset.count()} imÃ¡genes")
            
            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=filename,
                content_type='application/pdf'
            )
            
        except Exception as e:
            logger.error(f"Error generando reporte de rendimiento para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor al generar el reporte',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportStatsView(APIView):
    """
    Endpoint para obtener estadÃ­sticas previas a la generaciÃ³n de reportes.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadÃ­sticas para preview de reportes",
        operation_summary="EstadÃ­sticas de reportes",
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta", type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, description="RegiÃ³n", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Finca", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="EstadÃ­sticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request):
        """
        Obtiene estadÃ­sticas para preview de reportes.
        """
        try:
            # Obtener imÃ¡genes del usuario
            images_queryset = CacaoImage.objects.filter(user=request.user)
            
            # Aplicar filtros de query parameters
            if 'date_from' in request.GET:
                images_queryset = images_queryset.filter(created_at__date__gte=request.GET['date_from'])
            
            if 'date_to' in request.GET:
                images_queryset = images_queryset.filter(created_at__date__lte=request.GET['date_to'])
            
            if 'region' in request.GET:
                images_queryset = images_queryset.filter(region__icontains=request.GET['region'])
            
            if 'finca' in request.GET:
                images_queryset = images_queryset.filter(finca__icontains=request.GET['finca'])
            
            # Calcular estadÃ­sticas
            total_images = images_queryset.count()
            processed_images = images_queryset.filter(prediction__isnull=False).count()
            
            # EstadÃ­sticas de confianza
            confidence_stats = images_queryset.filter(
                prediction__isnull=False
            ).aggregate(
                avg_confidence=Avg('prediction__average_confidence'),
                min_confidence=Avg('prediction__average_confidence'),
                max_confidence=Avg('prediction__average_confidence')
            )
            
            # EstadÃ­sticas por regiÃ³n
            region_stats = images_queryset.values('region').annotate(
                count=Count('id')
            ).exclude(region__isnull=True).exclude(region='').order_by('-count')[:5]
            
            # EstadÃ­sticas por finca
            finca_stats = images_queryset.values('finca').annotate(
                count=Count('id')
            ).exclude(finca__isnull=True).exclude(finca='').order_by('-count')[:5]
            
            stats = {
                'total_images': total_images,
                'processed_images': processed_images,
                'processing_rate': round((processed_images / total_images * 100), 2) if total_images > 0 else 0,
                'confidence_stats': {
                    'average': round(float(confidence_stats['avg_confidence'] or 0), 3),
                    'minimum': round(float(confidence_stats['min_confidence'] or 0), 3),
                    'maximum': round(float(confidence_stats['max_confidence'] or 0), 3)
                },
                'top_regions': list(region_stats),
                'top_fincas': list(finca_stats),
                'filters_applied': {
                    'date_from': request.GET.get('date_from'),
                    'date_to': request.GET.get('date_to'),
                    'region': request.GET.get('region'),
                    'finca': request.GET.get('finca')
                }
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadÃ­sticas de reportes para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

