"""
Generador de reportes PDF para CacaoScan.
"""
import logging
import io
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Importar desde apps modulares
from api.utils.model_imports import get_models_safely
from .report_stats import (
    apply_prediction_filters,
    get_quality_stats,
    get_lotes_stats,
    get_activity_stats,
    get_login_stats
)

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction',
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote',
    'Notification': 'notifications.models.Notification',
    'ActivityLog': 'audit.models.ActivityLog'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']
Finca = models['Finca']
Lote = models['Lote']
Notification = models['Notification']
ActivityLog = models['ActivityLog']

from audit.models import LoginHistory
from reports.models import ReporteGenerado

logger = logging.getLogger("cacaoscan.services.report.pdf")

# PDF column constants
PDF_COL_METRIC = 'Métrica'
PDF_COL_VALUE = 'Valor'


class CacaoReportPDFGenerator:
    """
    Generador de reportes PDF avanzado para CacaoScan.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Texto pequeño
        self.styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3
        ))
    
    def _create_table_with_style(
        self,
        data: list[list[str]],
        col_widths: list[float],
        header_font_size: int = 10,
        body_font_size: int = 10,
        alignment: str = 'CENTER'
    ) -> Table:
        """Crear tabla con estilo estándar."""
        table = Table(data, colWidths=col_widths)
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), alignment),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), header_font_size),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
        
        if body_font_size != header_font_size:
            table_style.append(('FONTSIZE', (0, 1), (-1, -1), body_font_size))
        
        table.setStyle(TableStyle(table_style))
        return table
    
    def _create_section_with_table(
        self,
        title: str,
        data: list[list[str]],
        col_widths: list[float],
        header_font_size: int = 10,
        body_font_size: int = 10,
        alignment: str = 'CENTER'
    ) -> list:
        """Crear sección con título y tabla."""
        story = []
        story.append(Paragraph(title, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        table = self._create_table_with_style(data, col_widths, header_font_size, body_font_size, alignment)
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    
    def generate_quality_report(self, user, filtros=None):
        """
        Generar reporte de calidad de granos.
        
        Args:
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph("Reporte de Calidad de Granos de Cacao", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            story.append(Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", self.styles['CustomSmall']))
            story.append(Paragraph(f"Usuario: {user.get_full_name() or user.username}", self.styles['CustomSmall']))
            story.append(Spacer(1, 20))
            
            # Aplicar filtros
            queryset = apply_prediction_filters(CacaoPrediction.objects.all(), filtros)
            
            # Estadísticas generales
            stats = get_quality_stats(queryset)
            story.extend(self._create_stats_section(stats))
            
            # Tabla de análisis recientes
            recent_analyses = queryset.select_related('image').order_by('-created_at')[:20]
            if recent_analyses:
                story.extend(self._create_recent_analyses_table(recent_analyses))
            
            # Gráfico de distribución de calidad
            story.extend(self._create_quality_distribution_chart(queryset))
            
            # Recomendaciones
            story.extend(self._create_recommendations_section(stats))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte de calidad: {e}")
            raise
    
    def generate_finca_report(self, finca_id, user, filtros=None):
        """
        Generar reporte específico de una finca.
        
        Args:
            finca_id: ID de la finca
            user: Usuario que solicita el reporte (reservado para uso futuro)
            filtros: Filtros a aplicar (reservado para uso futuro)
        """
        # Suppress unused parameter warnings - reserved for future use
        _ = user
        _ = filtros
        
        try:
            finca = Finca.objects.get(id=finca_id)
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph(f"Reporte de Finca: {finca.nombre}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Información de la finca
            story.extend(self._create_finca_info_section(finca))
            
            # Estadísticas de lotes
            lotes_stats = get_lotes_stats(finca)
            story.extend(self._create_lotes_stats_section(lotes_stats))
            
            # Análisis por lote
            story.extend(self._create_lotes_analysis_section(finca))
            
            # Recomendaciones específicas
            story.extend(self._create_finca_recommendations_section(finca, lotes_stats))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte de finca: {e}")
            raise
    
    def generate_audit_report(self, user, filtros=None):
        """
        Generar reporte de auditoría.
        
        Args:
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph("Reporte de Auditoría del Sistema", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            story.append(Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", self.styles['CustomSmall']))
            story.append(Paragraph(f"Administrador: {user.get_full_name() or user.username}", self.styles['CustomSmall']))
            story.append(Spacer(1, 20))
            
            # Estadísticas de actividad
            activity_stats = get_activity_stats(filtros)
            story.extend(self._create_activity_stats_section(activity_stats))
            
            # Estadísticas de logins
            login_stats = get_login_stats(filtros)
            story.extend(self._create_login_stats_section(login_stats))
            
            # Actividades recientes
            recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:50]
            if recent_activities:
                story.extend(self._create_recent_activities_table(recent_activities))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte de auditoría: {e}")
            raise
    
    
    def _create_stats_section(self, stats):
        """Crear sección de estadísticas."""
        data = [
            [PDF_COL_METRIC, PDF_COL_VALUE],
            ['Total de Análisis', str(stats['total_analyses'])],
            ['Confianza Promedio', f"{stats['avg_confidence']}%"],
            ['Alto Promedio', f"{stats['avg_dimensions']['alto']} mm"],
            ['Ancho Promedio', f"{stats['avg_dimensions']['ancho']} mm"],
            ['Grosor Promedio', f"{stats['avg_dimensions']['grosor']} mm"],
            ['Peso Promedio', f"{stats['avg_weight']} g"],
        ]
        return self._create_section_with_table(
            "Estadísticas Generales",
            data,
            [2*inch, 2*inch],
            header_font_size=12
        )
    
    def _create_recent_analyses_table(self, analyses):
        """Crear tabla de análisis recientes."""
        data = [['Fecha', 'Usuario', 'Confianza', 'Alto (mm)', 'Ancho (mm)', 'Grosor (mm)', 'Peso (g)']]
        
        for analysis in analyses:
            data.append([
                analysis.created_at.strftime('%d/%m/%Y %H:%M'),
                analysis.image.user.username,
                f"{analysis.average_confidence:.1%}",
                f"{analysis.alto_mm:.1f}",
                f"{analysis.ancho_mm:.1f}",
                f"{analysis.grosor_mm:.1f}",
                f"{analysis.peso_g:.1f}",
            ])
        
        return self._create_section_with_table(
            "Análisis Recientes",
            data,
            [1*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch],
            header_font_size=8,
            body_font_size=7
        )
    
    def _create_quality_distribution_chart(self, queryset):
        """Crear gráfico de distribución de calidad."""
        story = []
        story.append(Paragraph("Distribución de Calidad", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        distribution = {
            'Excelente (90%)': queryset.filter(average_confidence__gte=0.9).count(),
            'Buena (80-89%)': queryset.filter(average_confidence__gte=0.8, average_confidence__lt=0.9).count(),
            'Regular (70-79%)': queryset.filter(average_confidence__gte=0.7, average_confidence__lt=0.8).count(),
            'Baja (<70%)': queryset.filter(average_confidence__lt=0.7).count(),
        }
        
        total = sum(distribution.values())
        if total > 0:
            data = [['Categoría', 'Cantidad', 'Porcentaje']]
            for category, count in distribution.items():
                percentage = (count / total) * 100
                data.append([category, str(count), f"{percentage:.1f}%"])
            
            table = self._create_table_with_style(data, [2*inch, 1*inch, 1*inch])
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_recommendations_section(self, stats):
        """Crear sección de recomendaciones."""
        story = []
        
        story.append(Paragraph("Recomendaciones", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        recommendations = []
        
        if stats['avg_confidence'] < 70:
            recommendations.append("- La confianza promedio es baja. Considere mejorar la calidad de las imágenes o el proceso de análisis.")
        
        if stats['avg_dimensions']['alto'] < 15 or stats['avg_dimensions']['alto'] > 25:
            recommendations.append("- Las dimensiones de los granos están fuera del rango óptimo. Revise el proceso de cosecha y selección.")
        
        if stats['avg_weight'] < 1.0 or stats['avg_weight'] > 2.5:
            recommendations.append("- El peso promedio de los granos no está en el rango esperado. Verifique la madurez de los granos.")
        
        if not recommendations:
            recommendations.append("- Los indicadores de calidad están dentro de rangos aceptables. Mantenga las buenas prácticas actuales.")
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_finca_info_section(self, finca):
        """Crear sección de información de finca."""
        data = [
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
        return self._create_section_with_table(
            "Información de la Finca",
            data,
            [2*inch, 3*inch],
            alignment='LEFT'
        )
    
    
    def _create_lotes_stats_section(self, stats):
        """Crear sección de estadísticas de lotes."""
        data = [
            [PDF_COL_METRIC, PDF_COL_VALUE],
            ['Total de Lotes', str(stats['total_lotes'])],
            ['Lotes Activos', str(stats['lotes_activos'])],
            ['Área Total', f"{stats['total_area']:.2f} ha"],
            ['Variedades', str(len(stats['variedades']))],
        ]
        return self._create_section_with_table(
            "Estadísticas de Lotes",
            data,
            [2*inch, 2*inch]
        )
    
    def _create_lotes_analysis_section(self, finca):
        """Crear sección de análisis por lote."""
        story = []
        story.append(Paragraph("Análisis por Lote", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        lotes = finca.lotes.all()
        
        if lotes.exists():
            data = [['Lote', 'Variedad', 'Estado', 'Área (ha)', 'Análisis', 'Calidad (%)']]
            
            for lote in lotes:
                data.append([
                    lote.identificador,
                    lote.variedad,
                    lote.get_estado_display(),
                    f"{float(lote.area_hectareas):.2f}",
                    str(lote.total_analisis),
                    f"{lote.calidad_promedio:.1f}",
                ])
            
            table = self._create_table_with_style(
                data,
                [1*inch, 1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch],
                header_font_size=8,
                body_font_size=7
            )
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_finca_recommendations_section(self, finca, stats):
        """Crear sección de recomendaciones específicas para la finca."""
        story = []
        
        story.append(Paragraph("Recomendaciones para la Finca", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        recommendations = []
        
        if stats['total_lotes'] == 0:
            recommendations.append("- Registre lotes en su finca para poder realizar análisis detallados.")
        
        if stats['lotes_activos'] < stats['total_lotes']:
            recommendations.append("- Revise los lotes inactivos y considere reactivarlos si es apropiado.")
        
        if len(stats['variedades']) == 1:
            recommendations.append("- Considere diversificar las variedades de cacao para mejorar la resistencia.")
        
        if finca.calidad_promedio < 70:
            recommendations.append("- La calidad promedio de la finca es baja. Revise las prácticas de cosecha y post-cosecha.")
        
        if not recommendations:
            recommendations.append("- La finca muestra buenos indicadores. Mantenga las prácticas actuales.")
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    
    def _create_activity_stats_section(self, stats):
        """Crear sección de estadísticas de actividad."""
        data = [
            [PDF_COL_METRIC, PDF_COL_VALUE],
            ['Total de Actividades', str(stats['total_activities'])],
            ['Actividades Hoy', str(stats['activities_today'])],
        ]
        return self._create_section_with_table(
            "Estadísticas de Actividad",
            data,
            [2*inch, 2*inch]
        )
    
    
    def _create_login_stats_section(self, stats):
        """Crear sección de estadísticas de logins."""
        data = [
            [PDF_COL_METRIC, PDF_COL_VALUE],
            ['Total de Logins', str(stats['total_logins'])],
            ['Logins Exitosos', str(stats['successful_logins'])],
            ['Logins Fallidos', str(stats['failed_logins'])],
            ['Tasa de xito', f"{stats['success_rate']:.1f}%"],
        ]
        return self._create_section_with_table(
            "Estadísticas de Logins",
            data,
            [2*inch, 2*inch]
        )
    
    def _create_recent_activities_table(self, activities):
        """Crear tabla de actividades recientes."""
        data = [['Fecha', 'Usuario', 'Acción', 'Tipo Recurso', 'Detalles']]
        
        for activity in activities:
            details_str = ''
            if isinstance(activity.details, dict):
                details_str = activity.details.get('description', str(activity.details))
            else:
                details_str = str(activity.details)
            
            if len(details_str) > 50:
                details_str = details_str[:50] + '...'
            
            data.append([
                activity.timestamp.strftime('%d/%m/%Y %H:%M'),
                activity.user.username if activity.user else 'Anónimo',
                activity.action,
                activity.resource_type or 'N/A',
                details_str,
            ])
        
        return self._create_section_with_table(
            "Actividades Recientes",
            data,
            [1*inch, 1*inch, 0.8*inch, 0.8*inch, 2*inch],
            header_font_size=8,
            body_font_size=7
        )

