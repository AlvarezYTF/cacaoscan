"""
Excel generator for users report.
Generates Excel reports with user and farm information.
"""
import logging
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from .excel_base import ExcelBaseGenerator

logger = logging.getLogger("cacaoscan.services.report.excel.usuarios")


class ExcelUsuariosGenerator(ExcelBaseGenerator):
    """
    Generator for users Excel reports.
    """
    
    def generate_users_report(self) -> bytes:
        """
        Generates professional Excel report of users with their associated farms.
        Includes professional visual formatting (colors, borders, alignment).
        If no users, shows "Sin registros disponibles" message.
        
        Returns:
            bytes: Excel file content
        """
        try:
            from django.contrib.auth.models import User
            
            self._create_workbook("Usuarios y Fincas")
            
            # Basic styles
            bold_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            align_center = Alignment(horizontal='center', vertical='center')
            align_vertical = Alignment(vertical='center')
            
            # Headers
            headers = [
                'ID Usuario', 'Nombre', 'Correo', 'Rol', 'Activo', 'Fecha Registro',
                'Finca', 'Departamento', 'Municipio', 'Área (ha)', 'Latitud', 'Longitud'
            ]
            self.ws.append(headers)
            
            # Apply style to headers
            for col in self.ws[1]:
                col.font = bold_font
                col.fill = header_fill
                col.alignment = align_center
                col.border = thin_border
            
            # Get all users with prefetch of farms
            users = User.objects.all().order_by('-date_joined').select_related('auth_profile', 'auth_email_token').prefetch_related('fincas_app_fincas', 'groups')
            
            if users.exists():
                # Iterate users and add farm information
                for user in users:
                    fincas = user.fincas_app_fincas.all()
                    
                    # Determine user role
                    if user.is_superuser or user.is_staff:
                        rol = 'admin'
                    elif user.groups.filter(name='analyst').exists():
                        rol = 'analyst'
                    else:
                        rol = 'farmer'
                    
                    if fincas.exists():
                        # If user has farms, create one row per farm
                        for finca in fincas:
                            self.ws.append([
                                user.id,
                                f"{user.first_name} {user.last_name}".strip() or user.username,
                                user.email,
                                rol,
                                'Sí' if user.is_active else 'No',
                                user.date_joined.strftime('%Y-%m-%d'),
                                finca.nombre,
                                finca.departamento or '',
                                finca.municipio or '',
                                float(finca.hectareas) if finca.hectareas else '',
                                float(finca.coordenadas_lat) if finca.coordenadas_lat is not None else '',
                                float(finca.coordenadas_lng) if finca.coordenadas_lng is not None else '',
                            ])
                    else:
                        # If no farms, add row with "Sin fincas"
                        self.ws.append([
                            user.id,
                            f"{user.first_name} {user.last_name}".strip() or user.username,
                            user.email,
                            rol,
                            'Sí' if user.is_active else 'No',
                            user.date_joined.strftime('%Y-%m-%d'),
                            'Sin fincas',
                            '', '', '', '', ''
                        ])
                
                # Apply borders to all data cells
                for row in self.ws.iter_rows(min_row=2, max_row=self.ws.max_row, max_col=len(headers)):
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = align_vertical
                
                # Auto-adjust column widths
                for col in self.ws.columns:
                    max_length = 0
                    for cell in col:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except Exception:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Maximum 50 characters
                    self.ws.column_dimensions[col[0].column_letter].width = adjusted_width
                
            else:
                # If no users, show friendly message
                self.ws.merge_cells('A1:L2')
                cell = self.ws['A1']
                cell.value = "Sin registros disponibles"
                cell.font = Font(bold=True, size=14, color="FF0000")
                cell.alignment = align_center
                cell.fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
                self.ws.row_dimensions[1].height = 40
            
            # Save to buffer
            content = self._save_to_buffer()
            
            # Validate buffer is not empty
            if not content or len(content) < 100:
                raise ValueError("Generated Excel file is empty or corrupt")
            
            logger.info(f"Reporte Excel de usuarios y fincas generado correctamente ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de usuarios: {e}", exc_info=True)
            raise

