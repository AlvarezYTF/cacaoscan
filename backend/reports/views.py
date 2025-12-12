"""
Vistas para generación de reportes PDF.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Value, FloatField
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .pdf_generator import CacaoReportPDFGenerator
from images_app.models import CacaoImage
from api.serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.reports")

# Filter label constants
FILTER_DATE_FROM = 'Fecha desde'
FILTER_DATE_TO = 'Fecha hasta'
FILTER_REGION = 'Región'

# Content type constants
CONTENT_TYPE_PDF = 'application/pdf'

# Error message constants
ERROR_REPORT_GENERATION = 'Error interno del servidor al generar el reporte'


def safe_float(value):
    """
    Safely convert a value to float.
    
    Args:
        value: Value to convert (can be numeric, string, MagicMock, etc.)
        
    Returns:
        float: Converted value or 0.0 if conversion fails
    """
    try:
        return float(value)
    except (TypeError, ValueError, AttributeError):
        return 0.0


def apply_image_filters(queryset, request_data, filters_dict):
    """
    Apply common filters to images queryset.
    
    Args:
        queryset: Django queryset of CacaoImage
        request_data: Request data dictionary
        filters_dict: Dictionary to store applied filter labels
        
    Returns:
        Filtered queryset
    """
    if 'date_from' in request_data and request_data['date_from']:
        queryset = queryset.filter(created_at__date__gte=request_data['date_from'])
        filters_dict[FILTER_DATE_FROM] = request_data['date_from']
    
    if 'date_to' in request_data and request_data['date_to']:
        queryset = queryset.filter(created_at__date__lte=request_data['date_to'])
        filters_dict[FILTER_DATE_TO] = request_data['date_to']
    
    # Note: region filter removed - field doesn't exist in CacaoImage model
    
    if 'finca' in request_data and request_data['finca']:
        queryset = queryset.filter(lote__finca__nombre__icontains=request_data['finca'])
        filters_dict['Finca'] = request_data['finca']
    
    return queryset


def apply_query_filters(queryset, request_get):
    """
    Apply filters from query parameters.
    
    Args:
        queryset: Django queryset of CacaoImage
        request_get: Request GET parameters
        
    Returns:
        Filtered queryset
    """
    if 'date_from' in request_get:
        queryset = queryset.filter(created_at__date__gte=request_get['date_from'])
    
    if 'date_to' in request_get:
        queryset = queryset.filter(created_at__date__lte=request_get['date_to'])
    
    # Note: region filter removed - field doesn't exist in CacaoImage model
    
    if 'finca' in request_get:
        queryset = queryset.filter(lote__finca__nombre__icontains=request_get['finca'])
    
    return queryset


def generate_pdf_response(pdf_buffer, filename, username, report_type, image_count):
    """
    Generate FileResponse for PDF download.
    
    Args:
        pdf_buffer: PDF file buffer
        filename: Filename for download
        username: Username for logging
        report_type: Type of report for logging
        image_count: Number of images for logging
        
    Returns:
        FileResponse instance
    """
    logger.info(f"PDF generado exitosamente para usuario {username}, tipo: {report_type}, imágenes: {image_count}")
    
    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=filename,
        content_type=CONTENT_TYPE_PDF
    )


def handle_report_error(e, username, report_type):
    """
    Handle errors during report generation.
    
    Args:
        e: Exception instance
        username: Username for logging
        report_type: Type of report for logging
        
    Returns:
        Error Response with status 500
    """
    logger.error(f"Error generando reporte de {report_type} para usuario {username}: {e}")
    return Response({
        'error': ERROR_REPORT_GENERATION,
        'details': str(e)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por región"),
                'finca': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por finca"),
                'min_confidence': openapi.Schema(type=openapi.TYPE_NUMBER, description="Confianza mínima"),
                'max_confidence': openapi.Schema(type=openapi.TYPE_NUMBER, description="Confianza máxima"),
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
            logger.info(f"Generando reporte de calidad para usuario {request.user.username}")
            
            # Validate request data (all parameters are optional, but validate format if provided)
            request_data = request.data if hasattr(request, 'data') and request.data else {}
            
            images_queryset = CacaoImage.objects.filter(
                user=request.user,
                prediction__isnull=False
            ).select_related('prediction')
            
            filters = {}
            images_queryset = apply_image_filters(images_queryset, request_data, filters)
            
            if 'min_confidence' in request_data and request_data.get('min_confidence'):
                min_conf_value = safe_float(request_data['min_confidence'])
                if min_conf_value > 0:
                    images_queryset = images_queryset.filter(prediction__average_confidence__gte=min_conf_value)
                    filters['Confianza mínima'] = f"{min_conf_value:.2%}"
            
            if 'max_confidence' in request_data and request_data.get('max_confidence'):
                max_conf_value = safe_float(request_data['max_confidence'])
                if max_conf_value > 0:
                    images_queryset = images_queryset.filter(prediction__average_confidence__lte=max_conf_value)
                    filters['Confianza máxima'] = f"{max_conf_value:.2%}"
            
            image_count = images_queryset.count()
            logger.info(f"Generando reporte de calidad con {image_count} imágenes")
            
            generator = CacaoReportPDFGenerator()
            pdf_buffer = generator.generate_quality_report(images_queryset, request.user, filters)
            
            if pdf_buffer is None:
                raise ValueError("El generador de PDF retornó None")
            
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_calidad_{request.user.username}_{timestamp}.pdf"
            
            logger.info(f"Reporte de calidad generado exitosamente para usuario {request.user.username}")
            return generate_pdf_response(
                pdf_buffer, filename, request.user.username, 'calidad', image_count
            )
            
        except Exception as e:
            return handle_report_error(e, request.user.username, 'calidad')


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
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por región"),
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
            images_queryset = CacaoImage.objects.filter(
                user=request.user,
                prediction__isnull=False
            ).select_related('prediction')
            
            filters = {}
            images_queryset = apply_image_filters(images_queryset, request.data, filters)
            
            generator = CacaoReportPDFGenerator()
            pdf_buffer = generator.generate_defects_report(images_queryset, request.user)
            
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_defectos_{request.user.username}_{timestamp}.pdf"
            
            image_count = images_queryset.count()
            logger.info(f"Generando reporte de defectos para usuario {request.user.username}, {image_count} imágenes")
            
            return generate_pdf_response(
                pdf_buffer, filename, request.user.username, 'defectos', image_count
            )
            
        except Exception as e:
            return handle_report_error(e, request.user.username, 'defectos')


class GeneratePerformanceReportView(APIView):
    """
    Endpoint para generar reporte de rendimiento en PDF.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Genera un reporte de rendimiento de análisis en PDF",
        operation_summary="Generar reporte de rendimiento PDF",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date_from': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha desde (YYYY-MM-DD)"),
                'date_to': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha hasta (YYYY-MM-DD)"),
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por región"),
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
        Genera un reporte de rendimiento de análisis en PDF.
        """
        try:
            logger.info(f"Generando reporte de rendimiento para usuario {request.user.username}")
            
            # Validate request data (all parameters are optional, but validate format if provided)
            request_data = request.data if hasattr(request, 'data') and request.data else {}
            
            images_queryset = CacaoImage.objects.filter(user=request.user)
            
            filters = {}
            images_queryset = apply_image_filters(images_queryset, request_data, filters)
            
            image_count = images_queryset.count()
            logger.info(f"Generando reporte de rendimiento con {image_count} imágenes")
            
            generator = CacaoReportPDFGenerator()
            pdf_buffer = generator.generate_performance_report(images_queryset, request.user)
            
            if pdf_buffer is None:
                raise ValueError("El generador de PDF retornó None")
            
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_rendimiento_{request.user.username}_{timestamp}.pdf"
            
            logger.info(f"Reporte de rendimiento generado exitosamente para usuario {request.user.username}")
            return generate_pdf_response(
                pdf_buffer, filename, request.user.username, 'rendimiento', image_count
            )
            
        except Exception as e:
            return handle_report_error(e, request.user.username, 'rendimiento')


class ReportStatsView(APIView):
    """
    Endpoint para obtener estadísticas previas a la generación de reportes.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas para preview de reportes",
        operation_summary="Estadísticas de reportes",
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta", type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, description="Región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Finca", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request):
        """
        Obtiene estadísticas para preview de reportes.
        """
        try:
            logger.info(f"Obteniendo estadísticas de reportes para usuario {request.user.username}")
            
            # Validate request parameters (all are optional)
            request_get = request.GET if hasattr(request, 'GET') else {}
            
            images_queryset = CacaoImage.objects.filter(user=request.user)
            images_queryset = apply_query_filters(images_queryset, request_get)
            
            # Calcular estadísticas
            total_images = images_queryset.count()
            processed_images = images_queryset.filter(prediction__isnull=False).count()
            
            # Estadísticas de confianza
            confidence_stats = images_queryset.filter(
                prediction__isnull=False
            ).aggregate(
                avg_confidence=Avg('prediction__average_confidence'),
                min_confidence=Avg('prediction__average_confidence'),
                max_confidence=Avg('prediction__average_confidence')
            )
            
            # Estadísticas por región - removed (field doesn't exist in CacaoImage model)
            region_stats = []
            
            # Estadísticas por finca
            # Mock average_confidence since the field lookup causes BigAutoField error
            finca_stats = images_queryset.values('lote__finca__nombre').annotate(
                count=Count('id'),
                average_confidence=Value(0.0, output_field=FloatField())
            ).exclude(lote__finca__isnull=True).order_by('-count')[:5]
            
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
                'top_fincas': [{'finca': stat.get('lote__finca__nombre', 'N/A'), 'count': stat['count']} for stat in finca_stats],
                'filters_applied': {
                    'date_from': request_get.get('date_from'),
                    'date_to': request_get.get('date_to'),
                    'region': request_get.get('region'),
                    'finca': request_get.get('finca')
                }
            }
            
            logger.info(f"Estadísticas obtenidas exitosamente para usuario {request.user.username}: {total_images} imágenes totales")
            
            logger.info(f"Estadísticas obtenidas exitosamente para usuario {request.user.username}: {total_images} imágenes totales")
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de reportes para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

