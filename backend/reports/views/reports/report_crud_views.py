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
    
    @staticmethod
    def _serialize_reporte(reportes):
        """Serialize report objects to dict."""
        reportes_data = []
        for reporte in reportes:
            # Get codes and names from Parametro ForeignKeys
            tipo_reporte_codigo = reporte.tipo_reporte.codigo if hasattr(reporte.tipo_reporte, 'codigo') else None
            tipo_reporte_nombre = reporte.tipo_reporte.nombre if hasattr(reporte.tipo_reporte, 'nombre') else str(reporte.tipo_reporte)
            
            formato_codigo = reporte.formato.codigo if hasattr(reporte.formato, 'codigo') else None
            formato_nombre = reporte.formato.nombre if hasattr(reporte.formato, 'nombre') else str(reporte.formato)
            
            estado_codigo = reporte.estado.codigo if hasattr(reporte.estado, 'codigo') else None
            estado_nombre = reporte.estado.nombre if hasattr(reporte.estado, 'nombre') else str(reporte.estado)
            
            reportes_data.append({
                'id': reporte.id,
                'tipo_reporte': tipo_reporte_codigo,
                'tipo_reporte_display': tipo_reporte_nombre,
                'formato': formato_codigo,
                'formato_display': formato_nombre,
                'titulo': reporte.titulo,
                'descripcion': reporte.descripcion,
                'estado': estado_codigo,
                'estado_display': estado_nombre,
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
    
    @staticmethod
    def _validate_report_type_and_format(tipo_reporte, formato):
        """Validate report type and format using Parametro catalog."""
        from catalogos.models import Parametro
        
        # Validate tipo_reporte
        try:
            tipo_parametro = Parametro.objects.get(
                tema__codigo='TEMA_TIPO_REPORTE',
                codigo=tipo_reporte.upper(),
                activo=True
            )
        except Parametro.DoesNotExist:
            # Get valid types for error message
            valid_types = list(Parametro.objects.filter(
                tema__codigo='TEMA_TIPO_REPORTE',
                activo=True
            ).values_list('codigo', flat=True))
            return Response({
                'error': f'Tipo de reporte inválido. Opciones válidas: {", ".join(valid_types)}',
                'details': f'Tipo de reporte inválido. Opciones válidas: {", ".join(valid_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate formato
        try:
            formato_parametro = Parametro.objects.get(
                tema__codigo='TEMA_FORMATO_REPORTE',
                codigo=formato.upper(),
                activo=True
            )
        except Parametro.DoesNotExist:
            # Get valid formats for error message
            valid_formats = list(Parametro.objects.filter(
                tema__codigo='TEMA_FORMATO_REPORTE',
                activo=True
            ).values_list('codigo', flat=True))
            return Response({
                'error': f'Formato inválido. Opciones válidas: {", ".join(valid_formats)}',
                'details': f'Formato inválido. Opciones válidas: {", ".join(valid_formats)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return None
    
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
            
            # Apply filters (using Parametro ForeignKeys)
            from catalogos.models import Parametro
            
            tipo_reporte = request.GET.get('tipo_reporte', '').strip()
            if tipo_reporte:
                try:
                    tipo_parametro = Parametro.objects.get(
                        tema__codigo='TEMA_TIPO_REPORTE',
                        codigo=tipo_reporte.upper()
                    )
                    queryset = queryset.filter(tipo_reporte=tipo_parametro)
                except Parametro.DoesNotExist:
                    pass  # Ignore invalid filter
            
            formato = request.GET.get('formato', '').strip()
            if formato:
                try:
                    formato_parametro = Parametro.objects.get(
                        tema__codigo='TEMA_FORMATO_REPORTE',
                        codigo=formato.upper()
                    )
                    queryset = queryset.filter(formato=formato_parametro)
                except Parametro.DoesNotExist:
                    pass  # Ignore invalid filter
            
            estado = request.GET.get('estado', '').strip()
            if estado:
                try:
                    estado_parametro = Parametro.objects.get(
                        tema__codigo='TEMA_ESTADO_REPORTE',
                        codigo=estado.upper()
                    )
                    queryset = queryset.filter(estado=estado_parametro)
                except Parametro.DoesNotExist:
                    pass  # Ignore invalid filter
            
            # Use shared serialization function
            return self.paginate_queryset(
                request,
                queryset,
                serializer_func=self._serialize_reporte
            )
            
            
        except Exception as e:
            logger.error(f"Error listando reportes: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'details': str(e)
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
                    'details': 'Los campos tipo_reporte, formato y titulo son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate report type and format
            validation_error = self._validate_report_type_and_format(tipo_reporte, formato)
            if validation_error:
                return validation_error
            
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
                'success': True,
                'reporte': {
                    'id': reporte.id,
                    'tipo_reporte': reporte.tipo_reporte.codigo if hasattr(reporte.tipo_reporte, 'codigo') else str(reporte.tipo_reporte),
                    'formato': reporte.formato.codigo if hasattr(reporte.formato, 'codigo') else str(reporte.formato),
                    'titulo': reporte.titulo,
                    'estado': reporte.estado.codigo if hasattr(reporte.estado, 'codigo') else str(reporte.estado),
                    'fecha_solicitud': reporte.fecha_solicitud.isoformat(),
                },
                'message': 'Reporte creado exitosamente. Se generará en segundo plano.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando reporte: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_report_async(self, reporte):
        """Generate report asynchronously (simulated)."""
        try:
            start_time = timezone.now()
            user = reporte.usuario
            
            # Get format and type codes from Parametro ForeignKeys
            formato_codigo = reporte.formato.codigo if hasattr(reporte.formato, 'codigo') else None
            tipo_reporte_codigo = reporte.tipo_reporte.codigo if hasattr(reporte.tipo_reporte, 'codigo') else None
            
            # Generate according to type and format
            if formato_codigo == 'PDF':
                from reports.services.report.pdf_generator import CacaoReportPDFGenerator
                pdf_generator = CacaoReportPDFGenerator()
                # TODO: Implement PDF generation based on tipo_reporte_codigo
                raise ValueError("Generación de PDF no implementada aún")
            elif formato_codigo == 'EXCEL':
                excel_service = ExcelAnalisisGenerator()
                # Generate content according to type
                if tipo_reporte_codigo == 'CALIDAD':
                    content = excel_service.generate_quality_report(user, reporte.filtros_aplicados)
                elif tipo_reporte_codigo == 'FINCA':
                    finca_id = reporte.parametros.get('finca_id')
                    if not finca_id:
                        raise ValueError("finca_id es requerido para reportes de finca")
                    content = excel_service.generate_finca_report(finca_id, user, reporte.filtros_aplicados)
                elif tipo_reporte_codigo == 'AUDITORIA':
                    content = excel_service.generate_audit_report(user, reporte.filtros_aplicados)
                elif tipo_reporte_codigo == 'PERSONALIZADO':
                    content = excel_service.generate_custom_report(
                        user, 
                        reporte.parametros.get('tipo_reporte', 'CALIDAD'),
                        reporte.parametros,
                        reporte.filtros_aplicados
                    )
                else:
                    raise ValueError(f"Tipo de reporte no soportado: {tipo_reporte_codigo}")
            else:
                raise ValueError(f"Formato no soportado: {formato_codigo}")
            
            # Create file
            file_content = ContentFile(content)
            
            # Set filename based on format
            formato_codigo = reporte.formato.codigo if hasattr(reporte.formato, 'codigo') else 'EXCEL'
            tipo_reporte_codigo = reporte.tipo_reporte.codigo if hasattr(reporte.tipo_reporte, 'codigo') else 'REPORTE'
            extension = 'xlsx' if formato_codigo == 'EXCEL' else 'pdf' if formato_codigo == 'PDF' else 'csv' if formato_codigo == 'CSV' else 'json'
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{tipo_reporte_codigo.lower()}_{reporte.usuario.username}_{timestamp}.{extension}"
            file_content.name = filename
            
            # Calculate generation time
            end_time = timezone.now()
            tiempo_generacion = end_time - start_time
            
            # Mark as completed
            reporte.marcar_completado(file_content, tiempo_generacion)
            
            # Set nombre_archivo if not already set
            if not reporte.nombre_archivo:
                reporte.nombre_archivo = filename
                reporte.save()
            
            logger.info(f"Reporte {reporte.id} generado exitosamente en {tiempo_generacion.total_seconds():.2f} segundos")
            
        except Exception as e:
            logger.error(f"Error generando reporte {reporte.id}: {e}")
            reporte.marcar_fallido(str(e))


class ReporteDetailView(APIView):
    """
    View for retrieving details of a specific report.
    """
    permission_classes = [IsAuthenticated]
    
    @staticmethod
    def _serialize_reporte(reportes):
        """Serialize report objects to dict."""
        return ReporteListCreateView._serialize_reporte(reportes)
    
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
            
            reporte_data = self._serialize_reporte([reporte])[0]
            reporte_data['parametros'] = reporte.parametros
            reporte_data['filtros_aplicados'] = reporte.filtros_aplicados
            
            return Response(reporte_data, status=status.HTTP_200_OK)
            
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
                'details': 'El reporte solicitado no existe o no tienes permiso para acceder a él'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error eliminando reporte {reporte_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

