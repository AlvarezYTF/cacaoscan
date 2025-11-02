"""
Generador de reportes Excel para CacaoScan.
"""
import logging
import io
from datetime import datetime
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from django.http import HttpResponse
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference, PieChart

# Importar desde apps modulares
try:
    from notifications.models import Notification
except ImportError:
    Notification = None

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

try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None

from .models import LoginHistory, ReporteGenerado

logger = logging.getLogger("cacaoscan.api")


class CacaoReportExcelGenerator:
    """
    Generador de reportes Excel avanzado para CacaoScan.
    """
    
    def __init__(self):
        self.workbook = None
        self.ws = None
    
    def generate_farmers_report(self):
        """
        Generar reporte Excel de agricultores con sus fincas.
        
        Returns:
            bytes: Contenido del archivo Excel
        """
        try:
            from django.contrib.auth.models import User
            
            logger.info("[INFO] Iniciando generaciÃ³n de reporte Excel de agricultores")
            print("[DEBUG] Iniciando generaciÃ³n de reporte Excel de agricultores")
            
            # Crear workbook
            self.workbook = Workbook()
            self.ws = self.workbook.active
            self.ws.title = "Agricultores"
            print("[DEBUG] Workbook creado correctamente")
            
            # Configurar columnas
            columns = [
                'Agricultor', 'Email', 'TelÃ©fono', 'Departamento', 'Municipio',
                'Finca', 'HectÃ¡reas', 'Estado Finca', 'Fecha Registro Finca'
            ]
            self.ws.append(columns)
            
            # Estilo de encabezado (opcional, no crÃ­tico)
            try:
                header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in self.ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            except Exception as style_error:
                logger.warning(f"Error aplicando estilos al encabezado (no crÃ­tico): {style_error}")
            
            # Obtener agricultores (usuarios que no son superusuarios ni staff)
            # Intentar con prefetch, si falla, hacer sin prefetch
            farmers_query = User.objects.filter(is_superuser=False, is_staff=False)
            
            try:
                # Intentar con prefetch para optimizar
                farmers = farmers_query.prefetch_related('fincas_app_fincas')
                farmers_list = list(farmers)  # Evaluar query para detectar errores temprano
                logger.info(f"[INFO] Obtenidos {len(farmers_list)} agricultores con prefetch")
                print(f"[DEBUG] Obtenidos {len(farmers_list)} agricultores con prefetch")
            except Exception as prefetch_error:
                logger.warning(f"Error con prefetch_related, intentando sin prefetch: {prefetch_error}")
                try:
                    # Sin prefetch, mÃ¡s lento pero seguro
                    farmers = farmers_query
                    farmers_list = list(farmers)
                    logger.info(f"Obtenidos {len(farmers_list)} agricultores sin prefetch")
                except Exception as query_error:
                    logger.error(f"Error obteniendo usuarios: {query_error}")
                    farmers_list = []
            
            # Procesar agricultores
            rows_added = 0
            for farmer in farmers_list:
                try:
                    # InformaciÃ³n bÃ¡sica del agricultor
                    name = ''
                    try:
                        if farmer.first_name or farmer.last_name:
                            name = f"{farmer.first_name or ''} {farmer.last_name or ''}".strip()
                        if not name:
                            name = str(farmer.username) if farmer.username else f'Usuario {farmer.id}'
                    except Exception:
                        name = f'Usuario {farmer.id}'
                    
                    email = str(farmer.email) if farmer.email else ''
                    
                    # Obtener telÃ©fono de forma segura
                    phone = ''
                    try:
                        if hasattr(farmer, 'auth_profile'):
                            profile = getattr(farmer, 'auth_profile', None)
                            if profile and hasattr(profile, 'phone_number'):
                                phone = str(profile.phone_number) if profile.phone_number else ''
                    except Exception:
                        pass
                    
                    # Obtener fincas del agricultor
                    fincas_list = []
                    try:
                        if hasattr(farmer, 'fincas_app_fincas'):
                            fincas_queryset = farmer.fincas_app_fincas.all()
                            fincas_list = list(fincas_queryset)
                    except Exception as finca_error:
                        logger.warning(f"Error obteniendo fincas para usuario {farmer.id}: {finca_error}")
                        fincas_list = []
                    
                    # Procesar fincas o crear fila sin fincas
                    if fincas_list:
                        for finca in fincas_list:
                            try:
                                # Validar y convertir todos los valores de forma segura
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
                                
                                # Convertir hectÃ¡reas
                                hectareas_val = 0.0
                                try:
                                    if hasattr(finca, 'hectareas') and finca.hectareas is not None:
                                        hectareas_val = float(finca.hectareas)
                                except (ValueError, TypeError, AttributeError):
                                    hectareas_val = 0.0
                                
                                # Estado de finca
                                estado_finca = "Activa"
                                try:
                                    if hasattr(finca, 'activa'):
                                        estado_finca = "Activa" if finca.activa else "Inactiva"
                                except Exception:
                                    pass
                                
                                # Fecha de registro
                                fecha_registro_str = ''
                                try:
                                    if hasattr(finca, 'fecha_registro') and finca.fecha_registro:
                                        fecha_registro_str = finca.fecha_registro.strftime('%Y-%m-%d')
                                except Exception:
                                    pass
                                
                                # Agregar fila al Excel
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
                                logger.warning(f"Error procesando finca {getattr(finca, 'id', 'unknown')}: {finca_row_error}")
                                continue
                    else:
                        # Sin fincas, crear fila con datos del agricultor solamente
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
                            '',  # HectÃ¡reas
                            '',  # Estado
                            fecha_registro_str
                        ])
                        rows_added += 1
                        
                except Exception as farmer_error:
                    logger.warning(f"Error procesando agricultor {getattr(farmer, 'id', 'unknown')}: {farmer_error}")
                    continue
            
            logger.info(f"[INFO] Procesados {rows_added} filas de datos")
            print(f"[DEBUG] Procesados {rows_added} filas de datos")
            
            # Ajustar ancho de columnas (opcional, no crÃ­tico)
            try:
                column_widths = {
                    'A': 25,  # Agricultor
                    'B': 30,  # Email
                    'C': 15,  # TelÃ©fono
                    'D': 20,  # Departamento
                    'E': 20,  # Municipio
                    'F': 20,  # Finca
                    'G': 12,  # HectÃ¡reas
                    'H': 15,  # Estado
                    'I': 18,  # Fecha Registro
                }
                
                for col, width in column_widths.items():
                    self.ws.column_dimensions[col].width = width
            except Exception as col_error:
                logger.warning(f"Error ajustando ancho de columnas (no crÃ­tico): {col_error}")
            
            # Centrar encabezados (opcional, no crÃ­tico)
            try:
                for row in self.ws.iter_rows(min_row=1, max_row=1):
                    for cell in row:
                        cell.alignment = Alignment(horizontal='center', vertical='center')
            except Exception as align_error:
                logger.warning(f"Error centrando encabezados (no crÃ­tico): {align_error}")
            
            # Guardar en buffer
            buffer = io.BytesIO()
            try:
                self.workbook.save(buffer)
            except Exception as save_error:
                logger.error(f"Error guardando workbook: {save_error}", exc_info=True)
                raise
            
            buffer.seek(0)
            content = buffer.getvalue()
            print(f"[DEBUG] Excel guardado en buffer - TamaÃ±o: {len(content)} bytes")
            
            # Validar contenido generado
            if not content:
                logger.error("[ERROR] El archivo Excel generado estÃ¡ vacÃ­o")
                print("[ERROR] El archivo Excel generado estÃ¡ vacÃ­o")
                raise ValueError("El archivo Excel generado estÃ¡ vacÃ­o")
            
            # Un Excel vÃ¡lido debe tener al menos algunos bytes (encabezado mÃ­nimo)
            if len(content) < 50:
                logger.warning(f"[WARNING] El archivo Excel generado es muy pequeÃ±o: {len(content)} bytes. Puede estar incompleto.")
                print(f"[WARNING] El archivo Excel generado es muy pequeÃ±o: {len(content)} bytes")
                # No lanzar error, permitir que continÃºe si solo tiene encabezado
            
            logger.info(f"[INFO] Reporte Excel de agricultores generado exitosamente - {len(content)} bytes, {rows_added} filas")
            print(f"[DEBUG] Reporte Excel de agricultores generado exitosamente - {len(content)} bytes, {rows_added} filas")
            return content
            
        except Exception as e:
            logger.error(f"[ERROR] Error generando reporte Excel de agricultores: {e}", exc_info=True)
            raise
    
    def generate_users_report(self):
        """
        Generar reporte Excel profesional de usuarios con sus fincas asociadas.
        Incluye formato visual profesional (colores, bordes, alineaciÃ³n).
        Si no hay usuarios, muestra mensaje "Sin registros disponibles".
        
        Returns:
            bytes: Contenido del archivo Excel
        """
        try:
            from django.contrib.auth.models import User
            from openpyxl.styles import Border, Side
            
            self.workbook = Workbook()
            self.ws = self.workbook.active
            self.ws.title = "Usuarios y Fincas"
            
            # === Estilos bÃ¡sicos ===
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
            
            # === Encabezados ===
            headers = [
                'ID Usuario', 'Nombre', 'Correo', 'Rol', 'Activo', 'Fecha Registro',
                'Finca', 'Departamento', 'Municipio', 'Ãrea (ha)', 'Latitud', 'Longitud'
            ]
            self.ws.append(headers)
            
            # Aplicar estilo a encabezados
            for col in self.ws[1]:
                col.font = bold_font
                col.fill = header_fill
                col.alignment = align_center
                col.border = thin_border
            
            # Obtener todos los usuarios con prefetch de fincas
            users = User.objects.all().order_by('-date_joined').select_related('auth_profile', 'auth_email_token').prefetch_related('fincas_app_fincas', 'groups')
            
            if users.exists():
                # Iterar usuarios y agregar informaciÃ³n de fincas
                for user in users:
                    fincas = user.fincas_app_fincas.all()
                    
                    # Determinar rol del usuario
                    if user.is_superuser or user.is_staff:
                        rol = 'admin'
                    elif user.groups.filter(name='analyst').exists():
                        rol = 'analyst'
                    else:
                        rol = 'farmer'
                    
                    if fincas.exists():
                        # Si el usuario tiene fincas, crear una fila por cada finca
                        for finca in fincas:
                            self.ws.append([
                                user.id,
                                f"{user.first_name} {user.last_name}".strip() or user.username,
                                user.email,
                                rol,
                                'SÃ­' if user.is_active else 'No',
                                user.date_joined.strftime('%Y-%m-%d'),
                                finca.nombre,
                                finca.departamento or 'â€”',
                                finca.municipio or 'â€”',
                                float(finca.hectareas),
                                float(finca.coordenadas_lat) if finca.coordenadas_lat is not None else 'â€”',
                                float(finca.coordenadas_lng) if finca.coordenadas_lng is not None else 'â€”',
                            ])
                    else:
                        # Si no tiene fincas, agregar fila con "Sin fincas"
                        self.ws.append([
                            user.id,
                            f"{user.first_name} {user.last_name}".strip() or user.username,
                            user.email,
                            rol,
                            'SÃ­' if user.is_active else 'No',
                            user.date_joined.strftime('%Y-%m-%d'),
                            'Sin fincas',
                            'â€”', 'â€”', 'â€”', 'â€”', 'â€”'
                        ])
                
                # Aplicar bordes a todas las celdas con datos
                for row in self.ws.iter_rows(min_row=2, max_row=self.ws.max_row, max_col=len(headers)):
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = align_vertical
                
                # Ajustar ancho de columnas automÃ¡ticamente
                for col in self.ws.columns:
                    max_length = 0
                    for cell in col:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # MÃ¡ximo 50 caracteres
                    self.ws.column_dimensions[col[0].column_letter].width = adjusted_width
                
            else:
                # Si no hay usuarios, mostrar mensaje amigable
                self.ws.merge_cells('A1:L2')
                cell = self.ws['A1']
                cell.value = "Sin registros disponibles"
                cell.font = Font(bold=True, size=14, color="FF0000")
                cell.alignment = align_center
                cell.fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
                self.ws.row_dimensions[1].height = 40
            
            # Guardar en buffer de memoria (binario)
            buffer = io.BytesIO()
            self.workbook.save(buffer)
            buffer.seek(0)
            
            # Validar que el buffer no estÃ© vacÃ­o
            content = buffer.getvalue()
            if not content or len(content) < 100:
                raise ValueError("El archivo Excel generado estÃ¡ vacÃ­o o corrupto")
            
            logger.info(f"Reporte Excel de usuarios y fincas generado correctamente ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de usuarios: {e}", exc_info=True)
            raise
    
    def generate_quality_report(self, user, filtros=None):
        """
        Generar reporte de calidad en Excel.
        
        Args:
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            self.workbook = Workbook()
            self.ws = self.workbook.active
            self.ws.title = "Reporte de Calidad"
            
            # Aplicar filtros
            queryset = self._apply_filters(CacaoPrediction.objects.all(), filtros)
            
            # Crear encabezado
            self._create_header("Reporte de Calidad de Granos de Cacao", user)
            
            # EstadÃ­sticas generales
            stats = self._get_quality_stats(queryset)
            self._create_stats_section(stats)
            
            # Tabla de anÃ¡lisis detallados
            self._create_detailed_analyses_table(queryset)
            
            # GrÃ¡fico de distribuciÃ³n de calidad
            self._create_quality_chart(stats)
            
            # Hoja de resumen
            self._create_summary_sheet(stats, user)
            
            # Guardar en buffer
            buffer = io.BytesIO()
            self.workbook.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de calidad: {e}")
            raise
    
    def generate_finca_report(self, finca_id, user, filtros=None):
        """
        Generar reporte de finca en Excel.
        
        Args:
            finca_id: ID de la finca
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            finca = Finca.objects.get(id=finca_id)
            self.workbook = Workbook()
            self.ws = self.workbook.active
            self.ws.title = f"Finca {finca.nombre}"
            
            # Crear encabezado
            self._create_header(f"Reporte de Finca: {finca.nombre}", user)
            
            # InformaciÃ³n de la finca
            self._create_finca_info_section(finca)
            
            # EstadÃ­sticas de lotes
            lotes_stats = self._get_lotes_stats(finca)
            self._create_lotes_stats_section(lotes_stats)
            
            # AnÃ¡lisis por lote
            self._create_lotes_analysis_section(finca)
            
            # Hoja de anÃ¡lisis detallados
            self._create_detailed_lotes_sheet(finca)
            
            # Guardar en buffer
            buffer = io.BytesIO()
            self.workbook.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de finca: {e}")
            raise
    
    def generate_audit_report(self, user, filtros=None):
        """
        Generar reporte de auditorÃ­a en Excel.
        
        Args:
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            self.workbook = Workbook()
            self.ws = self.workbook.active
            self.ws.title = "AuditorÃ­a"
            
            # Crear encabezado
            self._create_header("Reporte de AuditorÃ­a del Sistema", user)
            
            # EstadÃ­sticas de actividad
            activity_stats = self._get_activity_stats(filtros)
            self._create_activity_stats_section(activity_stats)
            
            # EstadÃ­sticas de logins
            login_stats = self._get_login_stats(filtros)
            self._create_login_stats_section(login_stats)
            
            # Hoja de actividades detalladas
            self._create_detailed_activities_sheet(filtros)
            
            # Hoja de logins detallados
            self._create_detailed_logins_sheet(filtros)
            
            # Guardar en buffer
            buffer = io.BytesIO()
            self.workbook.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de auditorÃ­a: {e}")
            raise
    
    def generate_custom_report(self, user, tipo_reporte, parametros, filtros=None):
        """
        Generar reporte personalizado en Excel.
        
        Args:
            user: Usuario que solicita el reporte
            tipo_reporte: Tipo de reporte
            parametros: ParÃ¡metros del reporte
            filtros: Filtros a aplicar
        """
        try:
            self.workbook = Workbook()
            self.ws = self.workbook.active
            self.ws.title = "Reporte Personalizado"
            
            # Crear encabezado
            self._create_header(f"Reporte Personalizado: {tipo_reporte}", user)
            
            # Generar segÃºn tipo
            if tipo_reporte == 'calidad':
                queryset = self._apply_filters(CacaoPrediction.objects.all(), filtros)
                stats = self._get_quality_stats(queryset)
                self._create_custom_quality_section(stats, parametros)
            elif tipo_reporte == 'finca':
                if parametros.get('finca_id'):
                    finca = Finca.objects.get(id=parametros['finca_id'])
                    self._create_custom_finca_section(finca, parametros)
            elif tipo_reporte == 'auditoria':
                activity_stats = self._get_activity_stats(filtros)
                self._create_custom_audit_section(activity_stats, parametros)
            
            # Guardar en buffer
            buffer = io.BytesIO()
            self.workbook.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel personalizado: {e}")
            raise
    
    def _apply_filters(self, queryset, filtros):
        """Aplicar filtros al queryset."""
        if not filtros:
            return queryset
        
        # Filtro por fecha
        if filtros.get('fecha_desde'):
            queryset = queryset.filter(created_at__date__gte=filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            queryset = queryset.filter(created_at__date__lte=filtros['fecha_hasta'])
        
        # Filtro por usuario
        if filtros.get('usuario_id'):
            queryset = queryset.filter(image__user_id=filtros['usuario_id'])
        
        # Filtro por finca
        if filtros.get('finca_id'):
            queryset = queryset.filter(image__finca=filtros['finca_id'])
        
        # Filtro por lote
        if filtros.get('lote_id'):
            queryset = queryset.filter(image__lote_id=filtros['lote_id'])
        
        return queryset
    
    def _create_header(self, title, user):
        """Crear encabezado del reporte."""
        # TÃ­tulo principal
        self.ws['A1'] = title
        self.ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        self.ws['A1'].alignment = Alignment(horizontal='center')
        self.ws.merge_cells('A1:F1')
        
        # InformaciÃ³n del reporte
        self.ws['A3'] = f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        self.ws['A3'].font = Font(size=10, italic=True)
        
        self.ws['A4'] = f"Usuario: {user.get_full_name() or user.username}"
        self.ws['A4'].font = Font(size=10, italic=True)
        
        # Espacio
        self.ws['A6'] = ""
    
    def _get_quality_stats(self, queryset):
        """Obtener estadÃ­sticas de calidad."""
        total_analyses = queryset.count()
        
        if total_analyses == 0:
            return {
                'total_analyses': 0,
                'avg_confidence': 0,
                'quality_distribution': {},
                'avg_dimensions': {},
                'avg_weight': 0
            }
        
        # EstadÃ­sticas de confianza
        avg_confidence = queryset.aggregate(avg=Avg('average_confidence'))['avg'] or 0
        
        # DistribuciÃ³n de calidad
        quality_distribution = {
            'Excelente (â‰¥90%)': queryset.filter(average_confidence__gte=0.9).count(),
            'Buena (80-89%)': queryset.filter(average_confidence__gte=0.8, average_confidence__lt=0.9).count(),
            'Regular (70-79%)': queryset.filter(average_confidence__gte=0.7, average_confidence__lt=0.8).count(),
            'Baja (<70%)': queryset.filter(average_confidence__lt=0.7).count(),
        }
        
        # Dimensiones promedio
        avg_dimensions = queryset.aggregate(
            avg_alto=Avg('alto_mm'),
            avg_ancho=Avg('ancho_mm'),
            avg_grosor=Avg('grosor_mm')
        )
        
        # Peso promedio
        avg_weight = queryset.aggregate(avg=Avg('peso_g'))['avg'] or 0
        
        return {
            'total_analyses': total_analyses,
            'avg_confidence': round(float(avg_confidence) * 100, 2),
            'quality_distribution': quality_distribution,
            'avg_dimensions': {
                'alto': round(float(avg_dimensions['avg_alto'] or 0), 2),
                'ancho': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                'grosor': round(float(avg_dimensions['avg_grosor'] or 0), 2),
            },
            'avg_weight': round(float(avg_weight), 2)
        }
    
    def _create_stats_section(self, stats):
        """Crear secciÃ³n de estadÃ­sticas."""
        # TÃ­tulo de secciÃ³n
        self.ws['A8'] = "EstadÃ­sticas Generales"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Datos de estadÃ­sticas
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de AnÃ¡lisis', stats['total_analyses']],
            ['Confianza Promedio', f"{stats['avg_confidence']}%"],
            ['Alto Promedio', f"{stats['avg_dimensions']['alto']} mm"],
            ['Ancho Promedio', f"{stats['avg_dimensions']['ancho']} mm"],
            ['Grosor Promedio', f"{stats['avg_dimensions']['grosor']} mm"],
            ['Peso Promedio', f"{stats['avg_weight']} g"],
        ]
        
        # Crear tabla
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_detailed_analyses_table(self, queryset):
        """Crear tabla de anÃ¡lisis detallados."""
        # TÃ­tulo de secciÃ³n
        self.ws['A18'] = "AnÃ¡lisis Detallados"
        self.ws['A18'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Encabezados
        headers = ['ID', 'Usuario', 'Finca', 'RegiÃ³n', 'Fecha', 'Alto (mm)', 'Ancho (mm)', 'Grosor (mm)', 'Peso (g)', 'Confianza']
        for col_num, header in enumerate(headers, 1):
            cell = self.ws.cell(row=20, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Datos (limitar a 100 registros para evitar archivos muy grandes)
        analyses = queryset.select_related('image', 'image__user').order_by('-created_at')[:100]
        
        for row_num, analysis in enumerate(analyses, 21):
            data = [
                analysis.id,
                analysis.image.user.username,
                analysis.image.finca or 'N/A',
                analysis.image.region or 'N/A',
                analysis.created_at.strftime('%d/%m/%Y %H:%M'),
                round(float(analysis.alto_mm), 2),
                round(float(analysis.ancho_mm), 2),
                round(float(analysis.grosor_mm), 2),
                round(float(analysis.peso_g), 2),
                f"{analysis.average_confidence:.2%}"
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal='center')
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        column_widths = [8, 12, 15, 12, 18, 10, 10, 10, 10, 12]
        for i, width in enumerate(column_widths, 1):
            self.ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_quality_chart(self, stats):
        """Crear grÃ¡fico de distribuciÃ³n de calidad."""
        if not stats['quality_distribution']:
            return
        
        # Crear nueva hoja para el grÃ¡fico
        chart_ws = self.workbook.create_sheet("DistribuciÃ³n de Calidad")
        
        # Datos para el grÃ¡fico
        chart_ws['A1'] = "CategorÃ­a"
        chart_ws['B1'] = "Cantidad"
        chart_ws['C1'] = "Porcentaje"
        
        # Estilo para encabezados
        for col in ['A', 'B', 'C']:
            cell = chart_ws[f'{col}1']
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
        
        row = 2
        total = stats['total_analyses']
        for category, count in stats['quality_distribution'].items():
            percentage = (count / total * 100) if total > 0 else 0
            chart_ws[f'A{row}'] = category
            chart_ws[f'B{row}'] = count
            chart_ws[f'C{row}'] = f"{percentage:.1f}%"
            row += 1
        
        # Crear grÃ¡fico de barras
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "DistribuciÃ³n de Calidad"
        chart.y_axis.title = 'Cantidad'
        chart.x_axis.title = 'CategorÃ­a'
        
        data = Reference(chart_ws, min_col=2, min_row=1, max_row=row-1, max_col=2)
        cats = Reference(chart_ws, min_col=1, min_row=2, max_row=row-1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        chart_ws.add_chart(chart, "E2")
        
        # Ajustar ancho de columnas
        chart_ws.column_dimensions['A'].width = 20
        chart_ws.column_dimensions['B'].width = 12
        chart_ws.column_dimensions['C'].width = 12
    
    def _create_summary_sheet(self, stats, user):
        """Crear hoja de resumen."""
        summary_ws = self.workbook.create_sheet("Resumen")
        
        # TÃ­tulo
        summary_ws['A1'] = "Resumen Ejecutivo"
        summary_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        summary_ws['A1'].alignment = Alignment(horizontal='center')
        summary_ws.merge_cells('A1:D1')
        
        # InformaciÃ³n del reporte
        summary_ws['A3'] = f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        summary_ws['A3'].font = Font(size=10, italic=True)
        
        summary_ws['A4'] = f"Usuario: {user.get_full_name() or user.username}"
        summary_ws['A4'].font = Font(size=10, italic=True)
        
        # Resumen de mÃ©tricas clave
        summary_ws['A6'] = "MÃ©tricas Clave"
        summary_ws['A6'].font = Font(size=14, bold=True, color="2F4F4F")
        
        key_metrics = [
            ['Total de AnÃ¡lisis', stats['total_analyses']],
            ['Confianza Promedio', f"{stats['avg_confidence']}%"],
            ['Alto Promedio', f"{stats['avg_dimensions']['alto']} mm"],
            ['Ancho Promedio', f"{stats['avg_dimensions']['ancho']} mm"],
            ['Grosor Promedio', f"{stats['avg_dimensions']['grosor']} mm"],
            ['Peso Promedio', f"{stats['avg_weight']} g"],
        ]
        
        for row_num, (metric, value) in enumerate(key_metrics, 8):
            summary_ws[f'A{row_num}'] = metric
            summary_ws[f'B{row_num}'] = value
            summary_ws[f'A{row_num}'].font = Font(bold=True)
            summary_ws[f'B{row_num}'].alignment = Alignment(horizontal='center')
        
        # Recomendaciones
        summary_ws['A15'] = "Recomendaciones"
        summary_ws['A15'].font = Font(size=14, bold=True, color="2F4F4F")
        
        recommendations = []
        if stats['avg_confidence'] < 70:
            recommendations.append("â€¢ La confianza promedio es baja. Considere mejorar la calidad de las imÃ¡genes.")
        if stats['avg_dimensions']['alto'] < 15 or stats['avg_dimensions']['alto'] > 25:
            recommendations.append("â€¢ Las dimensiones estÃ¡n fuera del rango Ã³ptimo. Revise el proceso de cosecha.")
        if stats['avg_weight'] < 1.0 or stats['avg_weight'] > 2.5:
            recommendations.append("â€¢ El peso promedio no estÃ¡ en el rango esperado. Verifique la madurez.")
        
        if not recommendations:
            recommendations.append("â€¢ Los indicadores estÃ¡n dentro de rangos aceptables. Mantenga las buenas prÃ¡cticas.")
        
        for row_num, rec in enumerate(recommendations, 17):
            summary_ws[f'A{row_num}'] = rec
            summary_ws[f'A{row_num}'].font = Font(size=10)
        
        # Ajustar ancho de columnas
        summary_ws.column_dimensions['A'].width = 25
        summary_ws.column_dimensions['B'].width = 15
    
    def _create_finca_info_section(self, finca):
        """Crear secciÃ³n de informaciÃ³n de finca."""
        # TÃ­tulo de secciÃ³n
        self.ws['A8'] = "InformaciÃ³n de la Finca"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Datos de la finca
        finca_data = [
            ['Campo', 'Valor'],
            ['Nombre', finca.nombre],
            ['UbicaciÃ³n', finca.ubicacion_completa],
            ['HectÃ¡reas', f"{finca.hectareas} ha"],
            ['Agricultor', finca.agricultor.get_full_name() or finca.agricultor.username],
            ['Total de Lotes', str(finca.total_lotes)],
            ['Lotes Activos', str(finca.lotes_activos)],
            ['Total de AnÃ¡lisis', str(finca.total_analisis)],
            ['Calidad Promedio', f"{finca.calidad_promedio}%"],
        ]
        
        # Crear tabla
        for row_num, row_data in enumerate(finca_data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='left')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 30
    
    def _get_lotes_stats(self, finca):
        """Obtener estadÃ­sticas de lotes de la finca."""
        lotes = finca.lotes.all()
        
        return {
            'total_lotes': lotes.count(),
            'lotes_activos': lotes.filter(activo=True).count(),
            'total_area': sum(float(lote.area_hectareas) for lote in lotes),
            'variedades': list(lotes.values('variedad').distinct()),
            'estados': dict(lotes.values('estado').annotate(count=Count('id')).values_list('estado', 'count')),
        }
    
    def _create_lotes_stats_section(self, stats):
        """Crear secciÃ³n de estadÃ­sticas de lotes."""
        # TÃ­tulo de secciÃ³n
        self.ws['A20'] = "EstadÃ­sticas de Lotes"
        self.ws['A20'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Datos de estadÃ­sticas
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de Lotes', str(stats['total_lotes'])],
            ['Lotes Activos', str(stats['lotes_activos'])],
            ['Ãrea Total', f"{stats['total_area']:.2f} ha"],
            ['Variedades', str(len(stats['variedades']))],
        ]
        
        # Crear tabla
        for row_num, row_data in enumerate(data, 22):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 22:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_lotes_analysis_section(self, finca):
        """Crear secciÃ³n de anÃ¡lisis por lote."""
        # TÃ­tulo de secciÃ³n
        self.ws['A28'] = "AnÃ¡lisis por Lote"
        self.ws['A28'].font = Font(size=14, bold=True, color="2F4F4F")
        
        lotes = finca.lotes.all()
        
        if lotes.exists():
            # Encabezados
            headers = ['Lote', 'Variedad', 'Estado', 'Ãrea (ha)', 'AnÃ¡lisis', 'Calidad (%)']
            for col_num, header in enumerate(headers, 1):
                cell = self.ws.cell(row=30, column=col_num, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                cell.alignment = Alignment(horizontal='center')
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
            
            # Datos de lotes
            for row_num, lote in enumerate(lotes, 31):
                data = [
                    lote.identificador,
                    lote.variedad,
                    lote.get_estado_display(),
                    f"{lote.area_hectareas:.2f}",
                    str(lote.total_analisis),
                    f"{lote.calidad_promedio:.1f}",
                ]
                
                for col_num, value in enumerate(data, 1):
                    cell = self.ws.cell(row=row_num, column=col_num, value=value)
                    cell.alignment = Alignment(horizontal='center')
                    cell.border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )
            
            # Ajustar ancho de columnas
            column_widths = [12, 15, 12, 12, 10, 12]
            for i, width in enumerate(column_widths, 1):
                self.ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_detailed_lotes_sheet(self, finca):
        """Crear hoja detallada de lotes."""
        lotes_ws = self.workbook.create_sheet("Lotes Detallados")
        
        # TÃ­tulo
        lotes_ws['A1'] = f"AnÃ¡lisis Detallados - Finca {finca.nombre}"
        lotes_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        lotes_ws['A1'].alignment = Alignment(horizontal='center')
        lotes_ws.merge_cells('A1:H1')
        
        # Encabezados
        headers = ['Lote', 'Variedad', 'Estado', 'Ãrea (ha)', 'Fecha PlantaciÃ³n', 'AnÃ¡lisis', 'Calidad (%)', 'Observaciones']
        for col_num, header in enumerate(headers, 1):
            cell = lotes_ws.cell(row=3, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Datos de lotes
        lotes = finca.lotes.all()
        for row_num, lote in enumerate(lotes, 4):
            data = [
                lote.identificador,
                lote.variedad,
                lote.get_estado_display(),
                f"{lote.area_hectareas:.2f}",
                lote.fecha_plantacion.strftime('%d/%m/%Y'),
                str(lote.total_analisis),
                f"{lote.calidad_promedio:.1f}",
                lote.descripcion or 'Sin observaciones',
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = lotes_ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal='center')
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        column_widths = [12, 15, 12, 12, 15, 10, 12, 25]
        for i, width in enumerate(column_widths, 1):
            lotes_ws.column_dimensions[chr(64 + i)].width = width
    
    def _get_activity_stats(self, filtros):
        """Obtener estadÃ­sticas de actividad."""
        queryset = ActivityLog.objects.all()
        
        if filtros:
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(timestamp__date__gte=filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(timestamp__date__lte=filtros['fecha_hasta'])
        
        return {
            'total_activities': queryset.count(),
            'activities_today': queryset.filter(timestamp__date=timezone.now().date()).count(),
            'activities_by_action': dict(queryset.values('accion').annotate(count=Count('id')).values_list('accion', 'count')),
            'top_users': list(queryset.values('usuario__username').annotate(count=Count('id')).order_by('-count')[:10]),
        }
    
    def _create_activity_stats_section(self, stats):
        """Crear secciÃ³n de estadÃ­sticas de actividad."""
        # TÃ­tulo de secciÃ³n
        self.ws['A8'] = "EstadÃ­sticas de Actividad"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Datos de estadÃ­sticas
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de Actividades', str(stats['total_activities'])],
            ['Actividades Hoy', str(stats['activities_today'])],
        ]
        
        # Crear tabla
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _get_login_stats(self, filtros):
        """Obtener estadÃ­sticas de logins."""
        queryset = LoginHistory.objects.all()
        
        if filtros:
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(login_time__date__gte=filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(login_time__date__lte=filtros['fecha_hasta'])
        
        return {
            'total_logins': queryset.count(),
            'successful_logins': queryset.filter(success=True).count(),
            'failed_logins': queryset.filter(success=False).count(),
            'success_rate': (queryset.filter(success=True).count() / queryset.count() * 100) if queryset.count() > 0 else 0,
        }
    
    def _create_login_stats_section(self, stats):
        """Crear secciÃ³n de estadÃ­sticas de logins."""
        # TÃ­tulo de secciÃ³n
        self.ws['A14'] = "EstadÃ­sticas de Logins"
        self.ws['A14'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Datos de estadÃ­sticas
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de Logins', str(stats['total_logins'])],
            ['Logins Exitosos', str(stats['successful_logins'])],
            ['Logins Fallidos', str(stats['failed_logins'])],
            ['Tasa de Ã‰xito', f"{stats['success_rate']:.1f}%"],
        ]
        
        # Crear tabla
        for row_num, row_data in enumerate(data, 16):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 16:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_detailed_activities_sheet(self, filtros):
        """Crear hoja detallada de actividades."""
        activities_ws = self.workbook.create_sheet("Actividades Detalladas")
        
        # TÃ­tulo
        activities_ws['A1'] = "Actividades del Sistema"
        activities_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        activities_ws['A1'].alignment = Alignment(horizontal='center')
        activities_ws.merge_cells('A1:F1')
        
        # Encabezados
        headers = ['Fecha', 'Usuario', 'AcciÃ³n', 'Modelo', 'DescripciÃ³n', 'IP']
        for col_num, header in enumerate(headers, 1):
            cell = activities_ws.cell(row=3, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Datos de actividades (limitar a 100 registros)
        queryset = ActivityLog.objects.select_related('usuario').order_by('-timestamp')[:100]
        
        if filtros:
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(timestamp__date__gte=filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(timestamp__date__lte=filtros['fecha_hasta'])
        
        for row_num, activity in enumerate(queryset, 4):
            data = [
                activity.timestamp.strftime('%d/%m/%Y %H:%M'),
                activity.usuario.username if activity.usuario else 'AnÃ³nimo',
                activity.get_accion_display(),
                activity.modelo,
                activity.descripcion[:50] + '...' if len(activity.descripcion) > 50 else activity.descripcion,
                activity.ip_address or 'N/A',
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = activities_ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal='center')
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        column_widths = [18, 12, 12, 12, 30, 15]
        for i, width in enumerate(column_widths, 1):
            activities_ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_detailed_logins_sheet(self, filtros):
        """Crear hoja detallada de logins."""
        logins_ws = self.workbook.create_sheet("Logins Detallados")
        
        # TÃ­tulo
        logins_ws['A1'] = "Historial de Logins"
        logins_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        logins_ws['A1'].alignment = Alignment(horizontal='center')
        logins_ws.merge_cells('A1:F1')
        
        # Encabezados
        headers = ['Fecha', 'Usuario', 'IP', 'Ã‰xito', 'DuraciÃ³n', 'RazÃ³n Fallo']
        for col_num, header in enumerate(headers, 1):
            cell = logins_ws.cell(row=3, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Datos de logins (limitar a 100 registros)
        queryset = LoginHistory.objects.select_related('usuario').order_by('-login_time')[:100]
        
        if filtros:
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(login_time__date__gte=filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(login_time__date__lte=filtros['fecha_hasta'])
        
        for row_num, login in enumerate(queryset, 4):
            duration = login.session_duration_formatted if hasattr(login, 'session_duration_formatted') else 'N/A'
            data = [
                login.login_time.strftime('%d/%m/%Y %H:%M'),
                login.usuario.username,
                login.ip_address,
                'SÃ­' if login.success else 'No',
                duration,
                login.failure_reason or 'N/A',
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = logins_ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal='center')
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        column_widths = [18, 12, 15, 8, 12, 20]
        for i, width in enumerate(column_widths, 1):
            logins_ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_custom_quality_section(self, stats, parametros):
        """Crear secciÃ³n personalizada de calidad."""
        # TÃ­tulo de secciÃ³n
        self.ws['A8'] = "AnÃ¡lisis Personalizado de Calidad"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # MÃ©tricas especÃ­ficas segÃºn parÃ¡metros
        custom_metrics = []
        
        if parametros.get('include_dimensions', True):
            custom_metrics.extend([
                ['Alto Promedio', f"{stats['avg_dimensions']['alto']} mm"],
                ['Ancho Promedio', f"{stats['avg_dimensions']['ancho']} mm"],
                ['Grosor Promedio', f"{stats['avg_dimensions']['grosor']} mm"],
            ])
        
        if parametros.get('include_weight', True):
            custom_metrics.append(['Peso Promedio', f"{stats['avg_weight']} g"])
        
        if parametros.get('include_confidence', True):
            custom_metrics.append(['Confianza Promedio', f"{stats['avg_confidence']}%"])
        
        # Crear tabla personalizada
        data = [['MÃ©trica', 'Valor']] + custom_metrics
        
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_custom_finca_section(self, finca, parametros):
        """Crear secciÃ³n personalizada de finca."""
        # TÃ­tulo de secciÃ³n
        self.ws['A8'] = f"AnÃ¡lisis Personalizado - {finca.nombre}"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # MÃ©tricas especÃ­ficas segÃºn parÃ¡metros
        custom_metrics = []
        
        if parametros.get('include_basic_info', True):
            custom_metrics.extend([
                ['Nombre', finca.nombre],
                ['UbicaciÃ³n', finca.ubicacion_completa],
                ['HectÃ¡reas', f"{finca.hectareas} ha"],
            ])
        
        if parametros.get('include_lotes', True):
            custom_metrics.extend([
                ['Total de Lotes', str(finca.total_lotes)],
                ['Lotes Activos', str(finca.lotes_activos)],
            ])
        
        if parametros.get('include_quality', True):
            custom_metrics.extend([
                ['Total de AnÃ¡lisis', str(finca.total_analisis)],
                ['Calidad Promedio', f"{finca.calidad_promedio}%"],
            ])
        
        # Crear tabla personalizada
        data = [['Campo', 'Valor']] + custom_metrics
        
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='left')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 30
    
    def _create_custom_audit_section(self, stats, parametros):
        """Crear secciÃ³n personalizada de auditorÃ­a."""
        # TÃ­tulo de secciÃ³n
        self.ws['A8'] = "AnÃ¡lisis Personalizado de AuditorÃ­a"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # MÃ©tricas especÃ­ficas segÃºn parÃ¡metros
        custom_metrics = []
        
        if parametros.get('include_activity', True):
            custom_metrics.extend([
                ['Total de Actividades', str(stats['total_activities'])],
                ['Actividades Hoy', str(stats['activities_today'])],
            ])
        
        if parametros.get('include_top_users', True):
            custom_metrics.append(['Usuarios MÃ¡s Activos', str(len(stats['top_users']))])
        
        if parametros.get('include_action_types', True):
            custom_metrics.append(['Tipos de AcciÃ³n', str(len(stats['activities_by_action']))])
        
        # Crear tabla personalizada
        data = [['MÃ©trica', 'Valor']] + custom_metrics
        
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Estilo para encabezados
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Bordes
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Ajustar ancho de columnas
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15

