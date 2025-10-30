"""
Vistas para gestión de reportes avanzados en CacaoScan.
"""
import logging
import io
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from django.http import HttpResponse, FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Count  # Importar Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ReporteGenerado
# Importar desde apps modulares
try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    CacaoImage = None
    CacaoPrediction = None

try:
    from fincas_app.models import Finca, Lote
except ImportError:
    Finca = None
    Lote = None
from .report_generator import CacaoReportPDFGenerator
from .excel_generator import CacaoReportExcelGenerator
from .serializers import ErrorResponseSerializer
from rest_framework.permissions import IsAdminUser

logger = logging.getLogger("cacaoscan.api")


class ReporteListCreateView(APIView):
    """
    Vista para listar y crear reportes.
    GET: Lista reportes del usuario
    POST: Crea nuevo reporte
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
        """Listar reportes con filtros."""
        try:
            queryset = ReporteGenerado.objects.filter(usuario=request.user)
            
            # Aplicar filtros
            tipo_reporte = request.GET.get('tipo_reporte', '').strip()
            if tipo_reporte:
                queryset = queryset.filter(tipo_reporte=tipo_reporte)
            
            formato = request.GET.get('formato', '').strip()
            if formato:
                queryset = queryset.filter(formato=formato)
            
            estado = request.GET.get('estado', '').strip()
            if estado:
                queryset = queryset.filter(estado=estado)
            
            # Paginación
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            reportes_data = []
            for reporte in page_obj.object_list:
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
                    'tamaño_archivo_mb': reporte.tamaño_archivo_mb,
                    'archivo_url': reporte.archivo_url,
                    'esta_expirado': reporte.esta_expirado,
                    'mensaje_error': reporte.mensaje_error,
                })
            
            return Response({
                'results': reportes_data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'next': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listando reportes: {e}")
            return Response({
                'error': 'Error interno del servidor',
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
        """Crear nuevo reporte."""
        try:
            # Validar datos de entrada
            tipo_reporte = request.data.get('tipo_reporte')
            formato = request.data.get('formato')
            titulo = request.data.get('titulo')
            
            if not tipo_reporte or not formato or not titulo:
                return Response({
                    'error': 'Los campos tipo_reporte, formato y titulo son requeridos',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar tipo de reporte
            valid_types = [choice[0] for choice in ReporteGenerado.TIPO_REPORTE_CHOICES]
            if tipo_reporte not in valid_types:
                return Response({
                    'error': f'Tipo de reporte inválido. Opciones válidas: {", ".join(valid_types)}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar formato
            valid_formats = [choice[0] for choice in ReporteGenerado.FORMATO_CHOICES]
            if formato not in valid_formats:
                return Response({
                    'error': f'Formato inválido. Opciones válidas: {", ".join(valid_formats)}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear reporte
            reporte = ReporteGenerado.generar_reporte(
                usuario=request.user,
                tipo_reporte=tipo_reporte,
                formato=formato,
                titulo=titulo,
                descripcion=request.data.get('descripcion'),
                parametros=request.data.get('parametros', {}),
                filtros=request.data.get('filtros', {})
            )
            
            # Generar reporte en background (simulado)
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
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_report_async(self, reporte):
        """Generar reporte de forma asíncrona (simulado)."""
        try:
            start_time = timezone.now()
            
            # Generar según tipo y formato
            if reporte.formato == 'pdf':
                generator = CacaoReportPDFGenerator()
            elif reporte.formato == 'excel':
                generator = CacaoReportExcelGenerator()
            else:
                raise ValueError(f"Formato no soportado: {reporte.formato}")
            
            # Generar contenido según tipo
            if reporte.tipo_reporte == 'calidad':
                content = generator.generate_quality_report(request.user, reporte.filtros_aplicados)
            elif reporte.tipo_reporte == 'finca':
                finca_id = reporte.parametros.get('finca_id')
                if not finca_id:
                    raise ValueError("finca_id es requerido para reportes de finca")
                content = generator.generate_finca_report(finca_id, request.user, reporte.filtros_aplicados)
            elif reporte.tipo_reporte == 'auditoria':
                content = generator.generate_audit_report(request.user, reporte.filtros_aplicados)
            elif reporte.tipo_reporte == 'personalizado':
                content = generator.generate_custom_report(
                    request.user, 
                    reporte.parametros.get('tipo_reporte', 'calidad'),
                    reporte.parametros,
                    reporte.filtros_aplicados
                )
            else:
                raise ValueError(f"Tipo de reporte no soportado: {reporte.tipo_reporte}")
            
            # Crear archivo
            filename = f"{reporte.titulo}_{reporte.id}.{reporte.formato}"
            file_content = ContentFile(content)
            
            # Calcular tiempo de generación
            end_time = timezone.now()
            tiempo_generacion = end_time - start_time
            
            # Marcar como completado
            reporte.marcar_completado(file_content, tiempo_generacion)
            
            logger.info(f"Reporte {reporte.id} generado exitosamente en {tiempo_generacion.total_seconds():.2f} segundos")
            
        except Exception as e:
            logger.error(f"Error generando reporte {reporte.id}: {e}")
            reporte.marcar_fallido(str(e))


class ReporteDetailView(APIView):
    """
    Vista para obtener detalles de un reporte específico.
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
        """Obtener detalles de reporte."""
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
                'tamaño_archivo_mb': reporte.tamaño_archivo_mb,
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
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteDownloadView(APIView):
    """
    Vista para descargar un reporte generado.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Descarga un reporte generado",
        operation_summary="Descargar reporte",
        responses={
            200: openapi.Response(description="Archivo descargado exitosamente"),
            404: ErrorResponseSerializer,
            410: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request, reporte_id):
        """Descargar reporte."""
        try:
            reporte = ReporteGenerado.objects.get(id=reporte_id, usuario=request.user)
            
            # Verificar estado
            if reporte.estado != 'completado':
                return Response({
                    'error': 'El reporte aún no está listo para descarga',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si está expirado
            if reporte.esta_expirado:
                return Response({
                    'error': 'El reporte ha expirado y ya no está disponible',
                    'status': 'error'
                }, status=status.HTTP_410_GONE)
            
            # Verificar que existe el archivo
            if not reporte.archivo:
                return Response({
                    'error': 'El archivo del reporte no está disponible',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Preparar respuesta de descarga
            response = FileResponse(
                reporte.archivo,
                as_attachment=True,
                filename=reporte.nombre_archivo or f"{reporte.titulo}.{reporte.formato}"
            )
            
            # Configurar headers según formato
            if reporte.formato == 'pdf':
                response['Content-Type'] = 'application/pdf'
            elif reporte.formato == 'excel':
                response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif reporte.formato == 'csv':
                response['Content-Type'] = 'text/csv'
            elif reporte.formato == 'json':
                response['Content-Type'] = 'application/json'
            
            logger.info(f"Reporte {reporte_id} descargado por usuario {request.user.username}")
            
            return response
            
        except ReporteGenerado.DoesNotExist:
            return Response({
                'error': 'Reporte no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error descargando reporte {reporte_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteDeleteView(APIView):
    """
    Vista para eliminar un reporte.
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
        """Eliminar reporte."""
        try:
            reporte = ReporteGenerado.objects.get(id=reporte_id, usuario=request.user)
            
            # Eliminar archivo físico si existe
            if reporte.archivo:
                try:
                    reporte.archivo.delete(save=False)
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo físico del reporte {reporte_id}: {e}")
            
            # Eliminar registro
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
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteStatsView(APIView):
    """
    Vista para obtener estadísticas de reportes del usuario.
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
        """Obtener estadísticas de reportes."""
        try:
            # Estadísticas básicas
            total_reportes = ReporteGenerado.objects.filter(usuario=request.user).count()
            reportes_completados = ReporteGenerado.objects.filter(usuario=request.user, estado='completado').count()
            reportes_generando = ReporteGenerado.objects.filter(usuario=request.user, estado='generando').count()
            reportes_fallidos = ReporteGenerado.objects.filter(usuario=request.user, estado='fallido').count()
            
            # Reportes por tipo
            reportes_por_tipo = dict(
                ReporteGenerado.objects.filter(usuario=request.user)
                .values('tipo_reporte')
                .annotate(count=Count('id'))
                .values_list('tipo_reporte', 'count')
            )
            
            # Reportes por formato
            reportes_por_formato = dict(
                ReporteGenerado.objects.filter(usuario=request.user)
                .values('formato')
                .annotate(count=Count('id'))
                .values_list('formato', 'count')
            )
            
            # Reportes recientes (últimos 5)
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
            logger.warning(f"⚠️ Error obteniendo estadísticas de reportes: {e}")
            # Retornar datos vacíos en lugar de 500
            return Response({
                'total_reportes': 0,
                'reportes_completados': 0,
                'reportes_generando': 0,
                'reportes_fallidos': 0,
                'reportes_por_tipo': {},
                'reportes_por_formato': {},
                'reportes_recientes': []
            }, status=status.HTTP_200_OK)


class ReporteCleanupView(APIView):
    """
    Vista para limpiar reportes expirados (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    def _is_admin_user(self, user):
        """Verificar si el usuario es administrador."""
        return user.is_superuser or user.is_staff
    
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
        """Limpiar reportes expirados."""
        try:
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para realizar esta acción',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Limpiar reportes expirados
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


class ReporteAgricultoresView(APIView):
    """
    Vista para generar y descargar reporte Excel de agricultores con sus fincas.
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Genera y descarga un archivo Excel con información de todos los agricultores y sus fincas",
        operation_summary="Reporte de agricultores (Excel)",
        responses={
            200: openapi.Response(description="Archivo Excel generado exitosamente"),
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request):
        try:
            # Generar el reporte Excel
            generator = CacaoReportExcelGenerator()
            excel_content = generator.generate_farmers_report()
            
            # Crear respuesta HTTP con el archivo
            response = HttpResponse(
                excel_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Configurar nombre del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_agricultores_{timestamp}.xlsx'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"Reporte de agricultores generado por {request.user.username}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando reporte de agricultores: {e}", exc_info=True)
            return Response({
                'error': 'Error al generar el reporte de agricultores',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteUsuariosView(APIView):
    """
    Vista para generar y descargar reporte Excel de usuarios del sistema.
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Genera y descarga un archivo Excel con información de todos los usuarios del sistema",
        operation_summary="Reporte de usuarios (Excel)",
        responses={
            200: openapi.Response(description="Archivo Excel generado exitosamente"),
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Reportes']
    )
    def get(self, request):
        try:
            # Generar el reporte Excel
            generator = CacaoReportExcelGenerator()
            excel_content = generator.generate_users_report()
            
            # Crear respuesta HTTP con el archivo
            response = HttpResponse(
                excel_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Configurar nombre del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_usuarios_{timestamp}.xlsx'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"Reporte de usuarios generado por {request.user.username}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando reporte de usuarios: {e}", exc_info=True)
            return Response({
                'error': 'Error al generar el reporte de usuarios',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
