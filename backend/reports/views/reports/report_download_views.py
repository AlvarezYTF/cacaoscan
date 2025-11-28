"""
Download views for reports in CacaoScan.
Handles downloading generated reports and special admin reports.
"""
import logging
import json
import traceback
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.encoding import escape_uri_path

from reports.models import ReporteGenerado
from api.utils.model_imports import get_models_safely
from reports.services import ExcelAgricultoresGenerator, ExcelUsuariosGenerator
from api.serializers import ErrorResponseSerializer
from .report_crud_views import ExcelRenderer

# Import models safely
models = get_models_safely({
    'Finca': 'fincas_app.models.Finca'
})
Finca = models['Finca']

User = get_user_model()
logger = logging.getLogger("cacaoscan.api")


class ReporteDownloadView(APIView):
    """
    View for downloading a generated report.
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
        """Download report."""
        try:
            reporte = ReporteGenerado.objects.get(id=reporte_id, usuario=request.user)
            
            # Verify state
            if reporte.estado != 'completado':
                return Response({
                    'error': 'El reporte aún no está listo para descarga',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify if expired
            if reporte.esta_expirado:
                return Response({
                    'error': 'El reporte ha expirado y ya no está disponible',
                    'status': 'error'
                }, status=status.HTTP_410_GONE)
            
            # Verify file exists
            if not reporte.archivo:
                return Response({
                    'error': 'El archivo del reporte no está disponible',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Prepare download response
            response = FileResponse(
                reporte.archivo,
                as_attachment=True,
                filename=reporte.nombre_archivo or f"{reporte.titulo}.{reporte.formato}"
            )
            
            # Configure headers according to format
            if reporte.formato == 'pdf':
                response['Content-Type'] = 'application/pdf'
            elif reporte.formato == 'excel':
                response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif reporte.formato == 'csv':
                response['Content-Type'] = 'text/csv'
            elif reporte.formato == 'json':
                response['Content-Type'] = CONTENT_TYPE_JSON
            
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


class ReporteAgricultoresView(APIView):
    """
    Generates an Excel file with farmer and farm information.
    Requires JWT authentication and admin permissions.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [ExcelRenderer]
    
    def get(self, request, *args, **kwargs):
        """
        Generates and downloads an Excel file with information of all farmers and their farms.
        """
        from io import BytesIO
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
        
        try:
            logger.info("[INFO] Generando reporte de agricultores para %s", request.user.username)
            
            # Validate that Finca model is available
            if Finca is None:
                raise ImportError("El modelo Finca no está disponible")
            
            # Create workbook and sheet
            wb = Workbook()
            ws = wb.active
            ws.title = "Agricultores"
            
            # Corporate colors CacaoScan
            COLOR_VERDE_PRIMITIVO = "166534"
            COLOR_VERDE_CLARO = "A7F3D0"
            COLOR_GRIS_SUAVE = "6B7280"
            
            # Define thin borders
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Main title (Row 1)
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=9)
            title_cell = ws.cell(row=1, column=1, value="Reporte de Agricultores y Fincas - CacaoScan")
            title_cell.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
            title_cell.fill = PatternFill(start_color=COLOR_VERDE_PRIMITIVO, end_color=COLOR_VERDE_PRIMITIVO, fill_type="solid")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 30
            
            # Empty separator row (Row 2)
            ws.row_dimensions[2].height = 10
            
            # Excel headers (Row 3)
            headers = [
                'Agricultor', 'Email', 'Telefono', 'Departamento', 'Municipio',
                'Finca', 'Hectareas', 'Estado Finca', 'Fecha Registro Finca'
            ]
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=3, column=col_idx, value=header)
                cell.font = Font(name="Calibri", size=12, bold=True, color=COLOR_VERDE_PRIMITIVO)
                cell.fill = PatternFill(start_color=COLOR_VERDE_CLARO, end_color=COLOR_VERDE_CLARO, fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border
            ws.row_dimensions[3].height = 25
            
            # Get user IDs that have at least one farm (farmers)
            try:
                agricultores_ids = Finca.objects.values_list("agricultor_id", flat=True).distinct()
                agricultores_ids_list = list(agricultores_ids)
                
                logger.debug("[DEBUG] Encontrados %d agricultores con fincas", len(agricultores_ids_list))
                
                if not agricultores_ids_list:
                    logger.warning("[WARNING] No hay agricultores con fincas en la base de datos")
                    agricultores_list = []
                    # Add row indicating no data (row 4)
                    data_row = 4
                    no_data_row = ["-", "Sin datos", "-", "-", "-", "-", "-", "-", "-"]
                    for col_idx, value in enumerate(no_data_row, start=1):
                        cell = ws.cell(row=data_row, column=col_idx, value=value)
                        cell.font = Font(name="Calibri", size=11)
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        cell.border = thin_border
                else:
                    # Get users with prefetch_related to optimize
                    agricultores = User.objects.filter(id__in=agricultores_ids_list).prefetch_related('fincas_app_fincas')
                    agricultores_list = list(agricultores)
                    logger.info("[INFO] Obtenidos %d agricultores con prefetch", len(agricultores_list))
                    
            except Exception as query_error:
                logger.error("[ERROR] Error obteniendo agricultores: %s", query_error, exc_info=True)
                raise
            
            # Process farmers and add data to Excel
            # Data starts at row 4 (after title, separator and headers)
            data_start_row = 4
            current_row = data_start_row
            rows_added = 0
            
            for agricultor in agricultores_list:
                try:
                    # Basic farmer information
                    nombre = agricultor.get_full_name() or agricultor.username or f"Usuario {agricultor.id}"
                    email = agricultor.email or ""
                    
                    # Get phone safely
                    telefono = ""
                    try:
                        persona = getattr(agricultor, 'persona', None)
                        if persona and hasattr(persona, 'telefono') and persona.telefono:
                            telefono = str(persona.telefono)
                        elif hasattr(agricultor, 'auth_profile') and agricultor.auth_profile:
                            telefono = str(agricultor.auth_profile.phone_number) if agricultor.auth_profile.phone_number else ""
                    except Exception:
                        pass  # Ignore phone errors (not critical)
                    
                    # Get farmer's farms
                    fincas_list = []
                    try:
                        if hasattr(agricultor, 'fincas_app_fincas'):
                            fincas_queryset = agricultor.fincas_app_fincas.all()
                            fincas_list = list(fincas_queryset)
                    except Exception as finca_error:
                        logger.warning("[WARNING] Error obteniendo fincas para usuario %d: %s", agricultor.id, finca_error)
                        fincas_list = []
                    
                    # If farmer has farms, create one row per farm
                    if fincas_list:
                        for finca in fincas_list:
                            try:
                                # Validate and convert values safely
                                depto = str(finca.departamento) if finca.departamento else ""
                                municipio = str(finca.municipio) if finca.municipio else ""
                                finca_nombre = str(finca.nombre) if finca.nombre else "Sin nombre"
                                
                                # Convert hectares
                                hectareas_val = 0.0
                                try:
                                    if finca.hectareas is not None:
                                        hectareas_val = float(finca.hectareas)
                                except (ValueError, TypeError, AttributeError):
                                    hectareas_val = 0.0
                                
                                # Farm status
                                estado_finca = "Activa" if (hasattr(finca, 'activa') and finca.activa) else "Inactiva"
                                
                                # Registration date with format dd/mm/yyyy
                                fecha_registro_str = ""
                                try:
                                    if hasattr(finca, 'fecha_registro') and finca.fecha_registro:
                                        fecha_registro_str = finca.fecha_registro.strftime('%d/%m/%Y')
                                except Exception:
                                    pass
                                
                                # Add row to Excel with styles
                                row_data = [
                                    nombre, email, telefono, depto, municipio,
                                    finca_nombre, hectareas_val, estado_finca, fecha_registro_str
                                ]
                                
                                for col_idx, value in enumerate(row_data, start=1):
                                    cell = ws.cell(row=current_row, column=col_idx, value=value)
                                    cell.font = Font(name="Calibri", size=11)
                                    cell.alignment = Alignment(horizontal="left", vertical="center")
                                    cell.border = thin_border
                                    
                                    # Numbers (hectares) aligned to the right
                                    if col_idx == 7 and isinstance(value, (int, float)):
                                        cell.alignment = Alignment(horizontal="right", vertical="center")
                                
                                current_row += 1
                                rows_added += 1
                                
                            except Exception as finca_row_error:
                                logger.warning("[WARNING] Error procesando finca %s: %s", 
                                             getattr(finca, 'id', 'unknown'), finca_row_error)
                                continue
                    else:
                        # No farms, create row with farmer data only
                        fecha_registro_str = ""
                        try:
                            if agricultor.date_joined:
                                fecha_registro_str = agricultor.date_joined.strftime('%d/%m/%Y')
                        except Exception:
                            pass
                        
                        row_data = [
                            nombre, email, telefono,
                            "", "", "", "", "",  # Departamento, Municipio, Finca, Hectareas, Estado
                            fecha_registro_str
                        ]
                        
                        for col_idx, value in enumerate(row_data, start=1):
                            cell = ws.cell(row=current_row, column=col_idx, value=value)
                            cell.font = Font(name="Calibri", size=11)
                            cell.alignment = Alignment(horizontal="left", vertical="center")
                            cell.border = thin_border
                        
                        current_row += 1
                        rows_added += 1
                    
                except Exception as agricultor_error:
                    logger.warning("[WARNING] Error procesando agricultor %s: %s", 
                                 getattr(agricultor, 'id', 'unknown'), agricultor_error)
                    continue
            
            logger.info("[INFO] Procesados %d filas de datos", rows_added)
            
            # Add footer
            footer_start_row = current_row + 2  # 2 empty rows after data
            
            # Empty row 1
            ws.row_dimensions[footer_start_row - 1].height = 10
            
            # Generated by (next row)
            ws.merge_cells(start_row=footer_start_row, start_column=1, end_row=footer_start_row, end_column=9)
            generated_cell = ws.cell(row=footer_start_row, column=1, value=f"Generado por: {request.user.username}")
            generated_cell.font = Font(name="Calibri", size=10, color=COLOR_GRIS_SUAVE)
            generated_cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Generation date (next row) - format dd/mm/yyyy hh:mm:ss AM/PM (local time)
            now = datetime.now()  # Use local time instead of UTC
            fecha_generacion = now.strftime('%d/%m/%Y %I:%M:%S %p')  # 12 hour format with AM/PM including seconds
            ws.merge_cells(start_row=footer_start_row + 1, start_column=1, end_row=footer_start_row + 1, end_column=9)
            fecha_cell = ws.cell(row=footer_start_row + 1, column=1, value=f"Fecha: {fecha_generacion}")
            fecha_cell.font = Font(name="Calibri", size=10, color=COLOR_GRIS_SUAVE)
            fecha_cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Adjust column widths automatically
            column_widths = {
                'A': 25,  # Agricultor
                'B': 30,  # Email
                'C': 15,  # Telefono
                'D': 18,  # Departamento
                'E': 18,  # Municipio
                'F': 20,  # Finca
                'G': 12,  # Hectareas
                'H': 15,  # Estado Finca
                'I': 18,  # Fecha Registro
            }
            
            for col_letter, width in column_widths.items():
                ws.column_dimensions[col_letter].width = width
            
            # Save file to memory
            output = BytesIO()
            wb.save(output)
            output.seek(0)  # VERY IMPORTANT: reposition pointer to start of file
            
            # Get buffer content
            excel_content = output.getvalue()
            
            # Validate generated content
            if not excel_content or len(excel_content) < 50:
                output.close()
                logger.error("[ERROR] El archivo Excel generado está vacío o demasiado pequeño: %d bytes", 
                           len(excel_content) if excel_content else 0)
                return HttpResponse(
                    "Error interno al generar el reporte Excel: contenido inválido",
                    status=500,
                    content_type='text/plain'
                )
            
            logger.info("[SUCCESS] Reporte generado correctamente (%d bytes) para usuario %s", 
                       len(excel_content), request.user.username)
            
            # File name with safe format
            fecha_actual = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"reporte_agricultores_{fecha_actual}.xlsx"
            
            # Return correctly formatted file
            response = HttpResponse(
                excel_content,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f'attachment; filename="{escape_uri_path(filename)}"'
            response["Content-Length"] = str(output.getbuffer().nbytes)
            
            # Close buffer correctly
            output.close()
            
            # Return HttpResponse directly - DRF will detect it and not try to serialize it
            return response
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error("[ERROR] Error generando reporte de agricultores: %s\n%s", str(e), error_trace)
            
            return HttpResponse(
                f"Error interno al generar el reporte: {str(e)}",
                status=500,
                content_type='text/plain'
            )


class ReporteUsuariosView(APIView):
    """
    View for generating and downloading Excel report of system users.
    Only accessible to administrators.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    # Disable DRF renderers to return binary response directly
    renderer_classes = []
    
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
            # Generate Excel report
            excel_service = ExcelUsuariosGenerator()
            excel_content = excel_service.generate_users_report()
            
            # Validate content is not empty
            if not excel_content or len(excel_content) < 100:
                logger.error("El contenido del reporte Excel está vacío o corrupto")
                return HttpResponse(
                    json.dumps({'error': 'Error al generar el reporte Excel: contenido vacío'}),
                    content_type='application/json',
                    status=500
                )
            
            # Create HTTP response with file (use HttpResponse directly, not DRF Response)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_usuarios_{timestamp}.xlsx'
            
            response = HttpResponse(
                excel_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Configure file name with correct encoding
            response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(filename)}"'
            response['Content-Length'] = len(excel_content)
            
            logger.info(f"Reporte de usuarios generado por {request.user.username} - Tamaño: {len(excel_content)} bytes")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando reporte de usuarios: {e}", exc_info=True)
            # For errors, use HttpResponse with JSON instead of DRF Response
            error_response = HttpResponse(
                json.dumps({
                    'error': 'Error al generar el reporte de usuarios',
                    'detail': str(e)
                }),
                content_type='application/json',
                status=500
            )
            return error_response

