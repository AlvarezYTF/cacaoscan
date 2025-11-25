"""
Excel generator for analysis reports.
Generates Excel reports for quality, farm, audit, and custom analysis.
"""
import logging
import io
from django.utils import timezone
from django.db.models import Count, Avg
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.chart import BarChart, Reference

from .excel_base import ExcelBaseGenerator

# Import models safely
from api.utils.model_imports import get_models_safely

models = get_models_safely({
    'CacaoPrediction': 'images_app.models.CacaoPrediction',
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote',
    'ActivityLog': 'audit.models.ActivityLog'
})
CacaoPrediction = models['CacaoPrediction']
Finca = models['Finca']
Lote = models['Lote']
ActivityLog = models['ActivityLog']

from audit.models import LoginHistory

logger = logging.getLogger("cacaoscan.services.report.excel.analisis")


class ExcelAnalisisGenerator(ExcelBaseGenerator):
    """
    Generator for analysis Excel reports (quality, farm, audit, custom).
    """
    
    def generate_quality_report(self, user, filtros=None) -> bytes:
        """
        Generates quality report in Excel.
        
        Args:
            user: User requesting the report
            filtros: Filters to apply
            
        Returns:
            bytes: Excel file content
        """
        try:
            self._create_workbook("Reporte de Calidad")
            
            # Apply filters
            queryset = self._apply_filters(CacaoPrediction.objects.all(), filtros)
            
            # Create header
            self._create_header("Reporte de Calidad de Granos de Cacao", user)
            
            # General statistics
            stats = self._get_quality_stats(queryset)
            self._create_stats_section(stats)
            
            # Detailed analyses table
            self._create_detailed_analyses_table(queryset)
            
            # Quality distribution chart
            self._create_quality_chart(stats)
            
            # Summary sheet
            self._create_summary_sheet(stats, user)
            
            # Save to buffer
            return self._save_to_buffer()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de calidad: {e}")
            raise
    
    def generate_finca_report(self, finca_id, user, filtros=None) -> bytes:
        """
        Generates farm report in Excel.
        
        Args:
            finca_id: Farm ID
            user: User requesting the report
            filtros: Filters to apply
            
        Returns:
            bytes: Excel file content
        """
        try:
            finca = Finca.objects.get(id=finca_id)
            self._create_workbook(f"Finca {finca.nombre}")
            
            # Create header
            self._create_header(f"Reporte de Finca: {finca.nombre}", user)
            
            # Farm information
            self._create_finca_info_section(finca)
            
            # Lot statistics
            lotes_stats = self._get_lotes_stats(finca)
            self._create_lotes_stats_section(lotes_stats)
            
            # Analysis by lot
            self._create_lotes_analysis_section(finca)
            
            # Detailed lots sheet
            self._create_detailed_lotes_sheet(finca)
            
            # Save to buffer
            return self._save_to_buffer()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de finca: {e}")
            raise
    
    def generate_audit_report(self, user, filtros=None) -> bytes:
        """
        Generates audit report in Excel.
        
        Args:
            user: User requesting the report
            filtros: Filters to apply
            
        Returns:
            bytes: Excel file content
        """
        try:
            self._create_workbook("Auditoría")
            
            # Create header
            self._create_header("Reporte de Auditoría del Sistema", user)
            
            # Activity statistics
            activity_stats = self._get_activity_stats(filtros)
            self._create_activity_stats_section(activity_stats)
            
            # Login statistics
            login_stats = self._get_login_stats(filtros)
            self._create_login_stats_section(login_stats)
            
            # Detailed activities sheet
            self._create_detailed_activities_sheet(filtros)
            
            # Detailed logins sheet
            self._create_detailed_logins_sheet(filtros)
            
            # Save to buffer
            return self._save_to_buffer()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel de auditoría: {e}")
            raise
    
    def generate_custom_report(self, user, tipo_reporte, parametros, filtros=None) -> bytes:
        """
        Generates custom report in Excel.
        
        Args:
            user: User requesting the report
            tipo_reporte: Report type
            parametros: Report parameters
            filtros: Filters to apply
            
        Returns:
            bytes: Excel file content
        """
        try:
            self._create_workbook("Reporte Personalizado")
            
            # Create header
            self._create_header(f"Reporte Personalizado: {tipo_reporte}", user)
            
            # Generate according to type
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
            
            # Save to buffer
            return self._save_to_buffer()
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel personalizado: {e}")
            raise
    
    def _apply_filters(self, queryset, filtros):
        """Apply filters to queryset."""
        if not filtros:
            return queryset
        
        # Filter by date
        if filtros.get('fecha_desde'):
            queryset = queryset.filter(created_at__date__gte=filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            queryset = queryset.filter(created_at__date__lte=filtros['fecha_hasta'])
        
        # Filter by user
        if filtros.get('usuario_id'):
            queryset = queryset.filter(image__user_id=filtros['usuario_id'])
        
        # Filter by farm
        if filtros.get('finca_id'):
            queryset = queryset.filter(image__finca=filtros['finca_id'])
        
        # Filter by lot
        if filtros.get('lote_id'):
            queryset = queryset.filter(image__lote_id=filtros['lote_id'])
        
        return queryset
    
    def _get_quality_stats(self, queryset):
        """Get quality statistics."""
        total_analyses = queryset.count()
        
        if total_analyses == 0:
            return {
                'total_analyses': 0,
                'avg_confidence': 0,
                'quality_distribution': {},
                'avg_dimensions': {},
                'avg_weight': 0
            }
        
        # Confidence statistics
        avg_confidence = queryset.aggregate(avg=Avg('average_confidence'))['avg'] or 0
        
        # Quality distribution
        quality_distribution = {
            'Excelente (90%)': queryset.filter(average_confidence__gte=0.9).count(),
            'Buena (80-89%)': queryset.filter(average_confidence__gte=0.8, average_confidence__lt=0.9).count(),
            'Regular (70-79%)': queryset.filter(average_confidence__gte=0.7, average_confidence__lt=0.8).count(),
            'Baja (<70%)': queryset.filter(average_confidence__lt=0.7).count(),
        }
        
        # Average dimensions
        avg_dimensions = queryset.aggregate(
            avg_alto=Avg('alto_mm'),
            avg_ancho=Avg('ancho_mm'),
            avg_grosor=Avg('grosor_mm')
        )
        
        # Average weight
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
        """Create statistics section."""
        # Section title
        self.ws['A8'] = "Estadísticas Generales"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Statistics data
        data = [
            ['Métrica', 'Valor'],
            ['Total de Análisis', stats['total_analyses']],
            ['Confianza Promedio', f"{stats['avg_confidence']}%"],
            ['Alto Promedio', f"{stats['avg_dimensions']['alto']} mm"],
            ['Ancho Promedio', f"{stats['avg_dimensions']['ancho']} mm"],
            ['Grosor Promedio', f"{stats['avg_dimensions']['grosor']} mm"],
            ['Peso Promedio', f"{stats['avg_weight']} g"],
        ]
        
        # Create table
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_detailed_analyses_table(self, queryset):
        """Create detailed analyses table."""
        # Section title
        self.ws['A18'] = "Análisis Detallados"
        self.ws['A18'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Headers
        headers = ['ID', 'Usuario', 'Finca', 'Región', 'Fecha', 'Alto (mm)', 'Ancho (mm)', 'Grosor (mm)', 'Peso (g)', 'Confianza']
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
        
        # Data (limit to 100 records to avoid very large files)
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
        
        # Adjust column widths
        column_widths = [8, 12, 15, 12, 18, 10, 10, 10, 10, 12]
        for i, width in enumerate(column_widths, 1):
            self.ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_quality_chart(self, stats):
        """Create quality distribution chart."""
        if not stats['quality_distribution']:
            return
        
        # Create new sheet for chart
        chart_ws = self.workbook.create_sheet("Distribución de Calidad")
        
        # Chart data
        chart_ws['A1'] = "Categoría"
        chart_ws['B1'] = "Cantidad"
        chart_ws['C1'] = "Porcentaje"
        
        # Style for headers
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
        
        # Create bar chart
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Distribución de Calidad"
        chart.y_axis.title = 'Cantidad'
        chart.x_axis.title = 'Categoría'
        
        data = Reference(chart_ws, min_col=2, min_row=1, max_row=row-1, max_col=2)
        cats = Reference(chart_ws, min_col=1, min_row=2, max_row=row-1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        chart_ws.add_chart(chart, "E2")
        
        # Adjust column widths
        chart_ws.column_dimensions['A'].width = 20
        chart_ws.column_dimensions['B'].width = 12
        chart_ws.column_dimensions['C'].width = 12
    
    def _create_summary_sheet(self, stats, user):
        """Create summary sheet."""
        summary_ws = self.workbook.create_sheet("Resumen")
        
        # Title
        summary_ws['A1'] = "Resumen Ejecutivo"
        summary_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        summary_ws['A1'].alignment = Alignment(horizontal='center')
        summary_ws.merge_cells('A1:D1')
        
        # Report information
        summary_ws['A3'] = f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        summary_ws['A3'].font = Font(size=10, italic=True)
        
        summary_ws['A4'] = f"Usuario: {user.get_full_name() or user.username}"
        summary_ws['A4'].font = Font(size=10, italic=True)
        
        # Key metrics summary
        summary_ws['A6'] = "Métricas Clave"
        summary_ws['A6'].font = Font(size=14, bold=True, color="2F4F4F")
        
        key_metrics = [
            ['Total de Análisis', stats['total_analyses']],
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
        
        # Recommendations
        summary_ws['A15'] = "Recomendaciones"
        summary_ws['A15'].font = Font(size=14, bold=True, color="2F4F4F")
        
        recommendations = []
        if stats['avg_confidence'] < 70:
            recommendations.append("- La confianza promedio es baja. Considere mejorar la calidad de las imágenes.")
        if stats['avg_dimensions']['alto'] < 15 or stats['avg_dimensions']['alto'] > 25:
            recommendations.append("- Las dimensiones están fuera del rango óptimo. Revise el proceso de cosecha.")
        if stats['avg_weight'] < 1.0 or stats['avg_weight'] > 2.5:
            recommendations.append("- El peso promedio no está en el rango esperado. Verifique la madurez.")
        
        if not recommendations:
            recommendations.append("- Los indicadores están dentro de rangos aceptables. Mantenga las buenas prácticas.")
        
        for row_num, rec in enumerate(recommendations, 17):
            summary_ws[f'A{row_num}'] = rec
            summary_ws[f'A{row_num}'].font = Font(size=10)
        
        # Adjust column widths
        summary_ws.column_dimensions['A'].width = 25
        summary_ws.column_dimensions['B'].width = 15
    
    def _create_finca_info_section(self, finca):
        """Create farm information section."""
        # Section title
        self.ws['A8'] = "Información de la Finca"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Farm data
        finca_data = [
            ['Campo', 'Valor'],
            ['Nombre', finca.nombre],
            ['Ubicación', finca.ubicacion_completa],
            ['Hectáreas', f"{finca.hectareas} ha"],
            ['Agricultor', finca.agricultor.get_full_name() or finca.agricultor.username],
            ['Total de Lotes', str(finca.total_lotes)],
            ['Lotes Activos', str(finca.lotes_activos)],
            ['Total de Análisis', str(finca.total_analisis)],
            ['Calidad Promedio', f"{finca.calidad_promedio}%"],
        ]
        
        # Create table
        for row_num, row_data in enumerate(finca_data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='left')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 30
    
    def _get_lotes_stats(self, finca):
        """Get lot statistics for the farm."""
        lotes = finca.lotes.all()
        
        return {
            'total_lotes': lotes.count(),
            'lotes_activos': lotes.filter(activo=True).count(),
            'total_area': sum(float(lote.area_hectareas) for lote in lotes),
            'variedades': list(lotes.values('variedad').distinct()),
            'estados': dict(lotes.values('estado').annotate(count=Count('id')).values_list('estado', 'count')),
        }
    
    def _create_lotes_stats_section(self, stats):
        """Create lot statistics section."""
        # Section title
        self.ws['A20'] = "Estadísticas de Lotes"
        self.ws['A20'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Statistics data
        data = [
            ['Métrica', 'Valor'],
            ['Total de Lotes', str(stats['total_lotes'])],
            ['Lotes Activos', str(stats['lotes_activos'])],
            ['Área Total', f"{stats['total_area']:.2f} ha"],
            ['Variedades', str(len(stats['variedades']))],
        ]
        
        # Create table
        for row_num, row_data in enumerate(data, 22):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 22:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_lotes_analysis_section(self, finca):
        """Create analysis by lot section."""
        # Section title
        self.ws['A28'] = "Análisis por Lote"
        self.ws['A28'].font = Font(size=14, bold=True, color="2F4F4F")
        
        lotes = finca.lotes.all()
        
        if lotes.exists():
            # Headers
            headers = ['Lote', 'Variedad', 'Estado', 'Área (ha)', 'Análisis', 'Calidad (%)']
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
            
            # Lot data
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
            
            # Adjust column widths
            column_widths = [12, 15, 12, 12, 10, 12]
            for i, width in enumerate(column_widths, 1):
                self.ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_detailed_lotes_sheet(self, finca):
        """Create detailed lots sheet."""
        lotes_ws = self.workbook.create_sheet("Lotes Detallados")
        
        # Title
        lotes_ws['A1'] = f"Análisis Detallados - Finca {finca.nombre}"
        lotes_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        lotes_ws['A1'].alignment = Alignment(horizontal='center')
        lotes_ws.merge_cells('A1:H1')
        
        # Headers
        headers = ['Lote', 'Variedad', 'Estado', 'Área (ha)', 'Fecha Plantación', 'Análisis', 'Calidad (%)', 'Observaciones']
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
        
        # Lot data
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
        
        # Adjust column widths
        column_widths = [12, 15, 12, 12, 15, 10, 12, 25]
        for i, width in enumerate(column_widths, 1):
            lotes_ws.column_dimensions[chr(64 + i)].width = width
    
    def _get_activity_stats(self, filtros):
        """Get activity statistics."""
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
        """Create activity statistics section."""
        # Section title
        self.ws['A8'] = "Estadísticas de Actividad"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Statistics data
        data = [
            ['Métrica', 'Valor'],
            ['Total de Actividades', str(stats['total_activities'])],
            ['Actividades Hoy', str(stats['activities_today'])],
        ]
        
        # Create table
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _get_login_stats(self, filtros):
        """Get login statistics."""
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
        """Create login statistics section."""
        # Section title
        self.ws['A14'] = "Estadísticas de Logins"
        self.ws['A14'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Statistics data
        data = [
            ['Métrica', 'Valor'],
            ['Total de Logins', str(stats['total_logins'])],
            ['Logins Exitosos', str(stats['successful_logins'])],
            ['Logins Fallidos', str(stats['failed_logins'])],
            ['Tasa de éxito', f"{stats['success_rate']:.1f}%"],
        ]
        
        # Create table
        for row_num, row_data in enumerate(data, 16):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 16:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_detailed_activities_sheet(self, filtros):
        """Create detailed activities sheet."""
        activities_ws = self.workbook.create_sheet("Actividades Detalladas")
        
        # Title
        activities_ws['A1'] = "Actividades del Sistema"
        activities_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        activities_ws['A1'].alignment = Alignment(horizontal='center')
        activities_ws.merge_cells('A1:F1')
        
        # Headers
        headers = ['Fecha', 'Usuario', 'Acción', 'Modelo', 'Descripción', 'IP']
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
        
        # Activity data (limit to 100 records)
        queryset = ActivityLog.objects.select_related('usuario').order_by('-timestamp')[:100]
        
        if filtros:
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(timestamp__date__gte=filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(timestamp__date__lte=filtros['fecha_hasta'])
        
        for row_num, activity in enumerate(queryset, 4):
            data = [
                activity.timestamp.strftime('%d/%m/%Y %H:%M'),
                activity.usuario.username if activity.usuario else 'Anónimo',
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
        
        # Adjust column widths
        column_widths = [18, 12, 12, 12, 30, 15]
        for i, width in enumerate(column_widths, 1):
            activities_ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_detailed_logins_sheet(self, filtros):
        """Create detailed logins sheet."""
        logins_ws = self.workbook.create_sheet("Logins Detallados")
        
        # Title
        logins_ws['A1'] = "Historial de Logins"
        logins_ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        logins_ws['A1'].alignment = Alignment(horizontal='center')
        logins_ws.merge_cells('A1:F1')
        
        # Headers
        headers = ['Fecha', 'Usuario', 'IP', 'Éxito', 'Duración', 'Razón Fallo']
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
        
        # Login data (limit to 100 records)
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
                'Sí' if login.success else 'No',
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
        
        # Adjust column widths
        column_widths = [18, 12, 15, 8, 12, 20]
        for i, width in enumerate(column_widths, 1):
            logins_ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_custom_quality_section(self, stats, parametros):
        """Create custom quality section."""
        # Section title
        self.ws['A8'] = "Análisis Personalizado de Calidad"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Specific metrics according to parameters
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
        
        # Create custom table
        data = [['Métrica', 'Valor']] + custom_metrics
        
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15
    
    def _create_custom_finca_section(self, finca, parametros):
        """Create custom farm section."""
        # Section title
        self.ws['A8'] = f"Análisis Personalizado - {finca.nombre}"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Specific metrics according to parameters
        custom_metrics = []
        
        if parametros.get('include_basic_info', True):
            custom_metrics.extend([
                ['Nombre', finca.nombre],
                ['Ubicación', finca.ubicacion_completa],
                ['Hectáreas', f"{finca.hectareas} ha"],
            ])
        
        if parametros.get('include_lotes', True):
            custom_metrics.extend([
                ['Total de Lotes', str(finca.total_lotes)],
                ['Lotes Activos', str(finca.lotes_activos)],
            ])
        
        if parametros.get('include_quality', True):
            custom_metrics.extend([
                ['Total de Análisis', str(finca.total_analisis)],
                ['Calidad Promedio', f"{finca.calidad_promedio}%"],
            ])
        
        # Create custom table
        data = [['Campo', 'Valor']] + custom_metrics
        
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='left')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 30
    
    def _create_custom_audit_section(self, stats, parametros):
        """Create custom audit section."""
        # Section title
        self.ws['A8'] = "Análisis Personalizado de Auditoría"
        self.ws['A8'].font = Font(size=14, bold=True, color="2F4F4F")
        
        # Specific metrics according to parameters
        custom_metrics = []
        
        if parametros.get('include_activity', True):
            custom_metrics.extend([
                ['Total de Actividades', str(stats['total_activities'])],
                ['Actividades Hoy', str(stats['activities_today'])],
            ])
        
        if parametros.get('include_top_users', True):
            custom_metrics.append(['Usuarios Más Activos', str(len(stats['top_users']))])
        
        if parametros.get('include_action_types', True):
            custom_metrics.append(['Tipos de Acción', str(len(stats['activities_by_action']))])
        
        # Create custom table
        data = [['Métrica', 'Valor']] + custom_metrics
        
        for row_num, row_data in enumerate(data, 10):
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                # Style for headers
                if row_num == 10:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.alignment = Alignment(horizontal='center')
                
                # Borders
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        self.ws.column_dimensions['A'].width = 20
        self.ws.column_dimensions['B'].width = 15

