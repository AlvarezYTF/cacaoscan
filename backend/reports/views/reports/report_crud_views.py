"""
CRUD views for report management in CacaoScan.
Handles listing, creating, retrieving, and deleting reports.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import PaginationMixin
from reports.models import ReporteGenerado
from reports.services import ExcelAnalisisGenerator
from api.serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api")

# Error message constants
ERROR_INTERNAL_SERVER = 'Error interno del servidor'


class ExcelRenderer(BaseRenderer):
    """
    Custom renderer for binary Excel files.
    Prevents DRF from trying to serialize binary content as JSON.
    """
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'
    charset = None
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders binary data directly without processing.
        If data is HttpResponse, return content as is.
        If data is bytes, return directly.
        """
        from django.http import HttpResponse
        if isinstance(data, HttpResponse):
            return data.content
        if isinstance(data, bytes):
            return data
        return data


class ReporteListCreateView(PaginationMixin, APIView):
    """
    View for listing and creating reports.
    GET: Lists user reports
    POST: Creates new report
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista todos los reportes del usuario autenticado",
        operation_summary="Listar reportes",
        manual_parameters=[
            openapi.Parameter('tipo_reporte', openapi.IN_QUERY, description="Filtrar por tipo de reporte", type=openapi.TYPE_STRING),
            openapi.Parameter('formato', openapi.IN_QUERY, description="Filtrar por formato", type=openapi.TYPE_STRING),
            openapi.Parameter('estado', openapi.IN_QUERY, description="Filtrar por estado", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Lista de reportes obtenida exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request):
        """List reports with filters."""
        try:
            queryset = ReporteGenerado.objects.filter(usuario=request.user)
            
            # Apply filters
            tipo_reporte = request.GET.get('tipo_reporte', '').strip()
            if tipo_reporte:
                queryset = queryset.filter(tipo_reporte=tipo_reporte)
            
            formato = request.GET.get('formato', '').strip()
            if formato:
                queryset = queryset.filter(formato=formato)
            
            estado = request.GET.get('estado', '').strip()
            if estado:
                queryset = queryset.filter(estado=estado)
            
            # Custom serialization function
            def serialize_reportes(reportes):
                reportes_data = []
                for reporte in reportes:
                    reportes_data.append({
                        'id': reporte.id,
                        'tipo_reporte': reporte.tipo_reporte,
                        'tipo_reporte_display': reporte.get_tipo_reporte_display(),
                        'formato': reporte.formato,
                        'formato_display': reporte.get_formato_display(),
                        'titulo': reporte.titulo,
                        'descripcion': reporte.descripcion,
                        'estado': reporte.estado,
                        'estado_display': reporte.get_estado_display(),
                        'fecha_solicitud': reporte.fecha_solicitud.isoformat(),
                        'fecha_generacion': reporte.fecha_generacion.isoformat() if reporte.fecha_generacion else None,
                        'fecha_expiracion': reporte.fecha_expiracion.isoformat() if reporte.fecha_expiracion else None,
                        'tiempo_generacion_segundos': reporte.tiempo_generacion_segundos,
                        'tamano_archivo_mb': reporte.tamano_archivo_mb,
                        'archivo_url': reporte.archivo_url,
                        'esta_expirado': reporte.esta_expirado,
                        'mensaje_error': reporte.mensaje_error,
                    })
                return reportes_data
            
            # Paginate using mixin with custom serialization
            return self.paginate_queryset(
                request,
                queryset,
                serializer_func=serialize_reportes
            )
            
        except Exception as e:
            logger.error(f"Error listando reportes: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Crea un nuevo reporte",
        operation_summary="Crear reporte",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tipo_reporte': openapi.Schema(type=openapi.TYPE_STRING, description="Tipo de reporte"),
                'formato': openapi.Schema(type=openapi.TYPE_STRING, description="Formato del reporte"),
                'titulo': openapi.Schema(type=openapi.TYPE_STRING, description="Título del reporte"),
                'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción del reporte"),
                'parametros': openapi.Schema(type=openapi.TYPE_OBJECT, description="Parámetros del reporte"),
                'filtros': openapi.Schema(type=openapi.TYPE_OBJECT, description="Filtros a aplicar"),
            },
            required=['tipo_reporte', 'formato', 'titulo']
        ),
        responses={
            201: openapi.Response(description="Reporte creado exitosamente"),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def post(self, request):
        """Create new report."""
        try:
            # Validate input data
            tipo_reporte = request.data.get('tipo_reporte')
            formato = request.data.get('formato')
            titulo = request.data.get('titulo')
            
            if not tipo_reporte or not formato or not titulo:
                return Response({
                    'error': 'Los campos tipo_reporte, formato y titulo son requeridos',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate report type
            valid_types = [choice[0] for choice in ReporteGenerado.TIPO_REPORTE_CHOICES]
            if tipo_reporte not in valid_types:
                return Response({
                    'error': f'Tipo de reporte inválido. Opciones válidas: {", ".join(valid_types)}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate format
            valid_formats = [choice[0] for choice in ReporteGenerado.FORMATO_CHOICES]
            if formato not in valid_formats:
                return Response({
                    'error': f'Formato inválido. Opciones válidas: {", ".join(valid_formats)}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create report
            reporte = ReporteGenerado.generar_reporte(
                usuario=request.user,
                tipo_reporte=tipo_reporte,
                formato=formato,
                titulo=titulo,
                descripcion=request.data.get('descripcion'),
                parametros=request.data.get('parametros', {}),
                filtros=request.data.get('filtros', {})
            )
            
            # Generate report in background (simulated)
            self._generate_report_async(reporte)
            
            logger.info(f"Reporte '{titulo}' creado por usuario {request.user.username}")
            
            return Response({
                'id': reporte.id,
                'tipo_reporte': reporte.tipo_reporte,
                'formato': reporte.formato,
                'titulo': reporte.titulo,
                'estado': reporte.estado,
                'fecha_solicitud': reporte.fecha_solicitud.isoformat(),
                'message': 'Reporte creado exitosamente. Se generará en segundo plano.',
                'status': 'success'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando reporte: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_report_async(self, reporte):
        """Generate report asynchronously (simulated)."""
        try:
            start_time = timezone.now()
            user = reporte.usuario
            
            # Generate according to type and format
            if reporte.formato == 'pdf':
                from reports.services import CacaoReportPDFGenerator
                generator = CacaoReportPDFGenerator()
                raise ValueError("Generación de PDF no implementada aún")
            elif reporte.formato == 'excel':
                excel_service = ExcelAnalisisGenerator()
                # Generate content according to type
                if reporte.tipo_reporte == 'calidad':
                    content = excel_service.generate_quality_report(user, reporte.filtros_aplicados)
                elif reporte.tipo_reporte == 'finca':
                    finca_id = reporte.parametros.get('finca_id')
                    if not finca_id:
                        raise ValueError("finca_id es requerido para reportes de finca")
                    content = excel_service.generate_finca_report(finca_id, user, reporte.filtros_aplicados)
                elif reporte.tipo_reporte == 'auditoria':
                    content = excel_service.generate_audit_report(user, reporte.filtros_aplicados)
                elif reporte.tipo_reporte == 'personalizado':
                    content = excel_service.generate_custom_report(
                        user, 
                        reporte.parametros.get('tipo_reporte', 'calidad'),
                        reporte.parametros,
                        reporte.filtros_aplicados
                    )
                else:
                    raise ValueError(f"Tipo de reporte no soportado: {reporte.tipo_reporte}")
            else:
                raise ValueError(f"Formato no soportado: {reporte.formato}")
            
            # Create file
            filename = f"{reporte.titulo}_{reporte.id}.{reporte.formato}"
            file_content = ContentFile(content)
            
            # Calculate generation time
            end_time = timezone.now()
            tiempo_generacion = end_time - start_time
            
            # Mark as completed
            reporte.marcar_completado(file_content, tiempo_generacion)
            
            logger.info(f"Reporte {reporte.id} generado exitosamente en {tiempo_generacion.total_seconds():.2f} segundos")
            
        except Exception as e:
            logger.error(f"Error generando reporte {reporte.id}: {e}")
            reporte.marcar_fallido(str(e))


class ReporteDetailView(APIView):
    """
    View for retrieving details of a specific report.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles de un reporte específico",
        operation_summary="Detalles de reporte",
        responses={
            200: openapi.Response(description="Detalles de reporte obtenidos exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request, reporte_id):
        """Get report details."""
        try:
            reporte = ReporteGenerado.objects.get(id=reporte_id, usuario=request.user)
            
            return Response({
                'id': reporte.id,
                'tipo_reporte': reporte.tipo_reporte,
                'tipo_reporte_display': reporte.get_tipo_reporte_display(),
                'formato': reporte.formato,
                'formato_display': reporte.get_formato_display(),
                'titulo': reporte.titulo,
                'descripcion': reporte.descripcion,
                'estado': reporte.estado,
                'estado_display': reporte.get_estado_display(),
                'fecha_solicitud': reporte.fecha_solicitud.isoformat(),
                'fecha_generacion': reporte.fecha_generacion.isoformat() if reporte.fecha_generacion else None,
                'fecha_expiracion': reporte.fecha_expiracion.isoformat() if reporte.fecha_expiracion else None,
                'tiempo_generacion_segundos': reporte.tiempo_generacion_segundos,
                'tamano_archivo_mb': reporte.tamano_archivo_mb,
                'archivo_url': reporte.archivo_url,
                'esta_expirado': reporte.esta_expirado,
                'mensaje_error': reporte.mensaje_error,
                'parametros': reporte.parametros,
                'filtros_aplicados': reporte.filtros_aplicados,
            }, status=status.HTTP_200_OK)
            
        except ReporteGenerado.DoesNotExist:
            return Response({
                'error': 'Reporte no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo detalles de reporte {reporte_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteDeleteView(APIView):
    """
    View for deleting a report.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina un reporte específico",
        operation_summary="Eliminar reporte",
        responses={
            204: "Reporte eliminado exitosamente",
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def delete(self, request, reporte_id):
        """Delete report."""
        try:
            reporte = ReporteGenerado.objects.get(id=reporte_id, usuario=request.user)
            
            # Delete physical file if exists
            if reporte.archivo:
                try:
                    reporte.archivo.delete(save=False)
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo físico del reporte {reporte_id}: {e}")
            
            # Delete record
            reporte.delete()
            
            logger.info(f"Reporte {reporte_id} eliminado por usuario {request.user.username}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except ReporteGenerado.DoesNotExist:
            return Response({
                'error': 'Reporte no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error eliminando reporte {reporte_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

