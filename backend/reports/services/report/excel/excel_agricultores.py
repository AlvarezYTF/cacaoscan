"""
Excel generator for farmers report.
Generates Excel reports with farmer and farm information.
"""
import logging
from typing import Optional
from openpyxl.styles import Font, Alignment, PatternFill

from .excel_base import ExcelBaseGenerator

logger = logging.getLogger("cacaoscan.services.report.excel.agricultores")


class ExcelAgricultoresGenerator(ExcelBaseGenerator):
    """
    Generator for farmers Excel reports.
    """
    
    def generate_farmers_report(self) -> bytes:
        """
        Generates Excel report of farmers with their farms.
        
        Returns:
            bytes: Excel file content
        """
        try:
            from django.contrib.auth.models import User
            
            logger.info("[INFO] Iniciando generación de reporte Excel de agricultores")
            
            # Create workbook
            self._create_workbook("Agricultores")
            
            # Configure columns
            columns = [
                'Agricultor', 'Email', 'Teléfono', 'Departamento', 'Municipio',
                'Finca', 'Hectáreas', 'Estado Finca', 'Fecha Registro Finca'
            ]
            self.ws.append(columns)
            
            # Apply header style
            try:
                header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in self.ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            except Exception as style_error:
                logger.warning(f"Error applying header styles (non-critical): {style_error}")
            
            # Get farmers (users who are not superusers or staff)
            farmers_query = User.objects.filter(is_superuser=False, is_staff=False)
            
            try:
                # Try with prefetch for optimization
                farmers = farmers_query.prefetch_related('fincas_app_fincas')
                farmers_list = list(farmers)
                logger.info(f"[INFO] Obtenidos {len(farmers_list)} agricultores con prefetch")
            except Exception as prefetch_error:
                logger.warning(f"Error with prefetch_related, trying without prefetch: {prefetch_error}")
                try:
                    farmers = farmers_query
                    farmers_list = list(farmers)
                    logger.info(f"Obtenidos {len(farmers_list)} agricultores sin prefetch")
                except Exception as query_error:
                    logger.error(f"Error getting users: {query_error}")
                    farmers_list = []
            
            # Process farmers
            rows_added = 0
            for farmer in farmers_list:
                try:
                    # Basic farmer information
                    name = ''
                    try:
                        if farmer.first_name or farmer.last_name:
                            name = f"{farmer.first_name or ''} {farmer.last_name or ''}".strip()
                        if not name:
                            name = str(farmer.username) if farmer.username else f'Usuario {farmer.id}'
                    except Exception:
                        name = f'Usuario {farmer.id}'
                    
                    email = str(farmer.email) if farmer.email else ''
                    
                    # Get phone safely
                    phone = ''
                    try:
                        if hasattr(farmer, 'auth_profile'):
                            profile = getattr(farmer, 'auth_profile', None)
                            if profile and hasattr(profile, 'phone_number'):
                                phone = str(profile.phone_number) if profile.phone_number else ''
                    except Exception:
                        pass
                    
                    # Get farmer's farms
                    fincas_list = []
                    try:
                        if hasattr(farmer, 'fincas_app_fincas'):
                            fincas_queryset = farmer.fincas_app_fincas.all()
                            fincas_list = list(fincas_queryset)
                    except Exception as finca_error:
                        logger.warning(f"Error getting farms for user {farmer.id}: {finca_error}")
                        fincas_list = []
                    
                    # Process farms or create row without farms
                    if fincas_list:
                        for finca in fincas_list:
                            try:
                                # Validate and convert all values safely
                                depto = ''
                                try:
                                    if finca.departamento:
                                        depto = str(finca.departamento)
                                except Exception:
                                    pass
                                
                                municipio = ''
                                try:
                                    if finca.municipio:
                                        municipio = str(finca.municipio)
                                except Exception:
                                    pass
                                
                                finca_nombre = 'Sin nombre'
                                try:
                                    if finca.nombre:
                                        finca_nombre = str(finca.nombre)
                                except Exception:
                                    pass
                                
                                # Convert hectares
                                hectareas_val = 0.0
                                try:
                                    if hasattr(finca, 'hectareas') and finca.hectareas is not None:
                                        hectareas_val = float(finca.hectareas)
                                except (ValueError, TypeError, AttributeError):
                                    hectareas_val = 0.0
                                
                                # Farm status
                                estado_finca = "Activa"
                                try:
                                    if hasattr(finca, 'activa'):
                                        estado_finca = "Activa" if finca.activa else "Inactiva"
                                except Exception:
                                    pass
                                
                                # Registration date
                                fecha_registro_str = ''
                                try:
                                    if hasattr(finca, 'fecha_registro') and finca.fecha_registro:
                                        fecha_registro_str = finca.fecha_registro.strftime('%Y-%m-%d')
                                except Exception:
                                    pass
                                
                                # Add row to Excel
                                self.ws.append([
                                    name,
                                    email,
                                    phone,
                                    depto,
                                    municipio,
                                    finca_nombre,
                                    hectareas_val,
                                    estado_finca,
                                    fecha_registro_str
                                ])
                                rows_added += 1
                                
                            except Exception as finca_row_error:
                                logger.warning(f"Error processing farm {getattr(finca, 'id', 'unknown')}: {finca_row_error}")
                                continue
                    else:
                        # No farms, create row with farmer data only
                        fecha_registro_str = ''
                        try:
                            if farmer.date_joined:
                                fecha_registro_str = farmer.date_joined.strftime('%Y-%m-%d')
                        except Exception:
                            pass
                        
                        self.ws.append([
                            name,
                            email,
                            phone,
                            '',  # Departamento
                            '',  # Municipio
                            '',  # Finca
                            '',  # Hectáreas
                            '',  # Estado
                            fecha_registro_str
                        ])
                        rows_added += 1
                        
                except Exception as farmer_error:
                    logger.warning(f"Error processing farmer {getattr(farmer, 'id', 'unknown')}: {farmer_error}")
                    continue
            
            logger.info(f"[INFO] Procesados {rows_added} filas de datos")
            
            # Adjust column widths
            try:
                column_widths = {
                    'A': 25,  # Agricultor
                    'B': 30,  # Email
                    'C': 15,  # Teléfono
                    'D': 20,  # Departamento
                    'E': 20,  # Municipio
                    'F': 20,  # Finca
                    'G': 12,  # Hectáreas
                    'H': 15,  # Estado
                    'I': 18,  # Fecha Registro
                }
                self._adjust_column_widths(column_widths)
            except Exception as col_error:
                logger.warning(f"Error adjusting column widths (non-critical): {col_error}")
            
            # Center headers
            try:
                for row in self.ws.iter_rows(min_row=1, max_row=1):
                    for cell in row:
                        cell.alignment = Alignment(horizontal='center', vertical='center')
            except Exception as align_error:
                logger.warning(f"Error centering headers (non-critical): {align_error}")
            
            # Save to buffer
            content = self._save_to_buffer()
            
            logger.info(f"[INFO] Reporte Excel de agricultores generado exitosamente - {len(content)} bytes, {rows_added} filas")
            return content
            
        except Exception as e:
            logger.error(f"[ERROR] Error generando reporte Excel de agricultores: {e}", exc_info=True)
            raise

