"""
Generador de reportes avanzado para CacaoScan.
"""
import logging
import io
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

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

try:
    from notifications.models import Notification
except ImportError:
    Notification = None

try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None

from .models import LoginHistory, ReporteGenerado

logger = logging.getLogger("cacaoscan.api")


class CacaoReportPDFGenerator:
    """
    Generador de reportes PDF avanzado para CacaoScan.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados."""
        # TÃ­tulo principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        ))
        
        # SubtÃ­tulo
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
        
        # Texto pequeÃ±o
        self.styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3
        ))
    
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
            
            # TÃ­tulo
            story.append(Paragraph("Reporte de Calidad de Granos de Cacao", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # InformaciÃ³n del reporte
            story.append(Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", self.styles['CustomSmall']))
            story.append(Paragraph(f"Usuario: {user.get_full_name() or user.username}", self.styles['CustomSmall']))
            story.append(Spacer(1, 20))
            
            # Aplicar filtros
            queryset = self._apply_filters(CacaoPrediction.objects.all(), filtros)
            
            # EstadÃ­sticas generales
            stats = self._get_quality_stats(queryset)
            story.extend(self._create_stats_section(stats))
            
            # Tabla de anÃ¡lisis recientes
            recent_analyses = queryset.select_related('image').order_by('-created_at')[:20]
            if recent_analyses:
                story.extend(self._create_recent_analyses_table(recent_analyses))
            
            # GrÃ¡fico de distribuciÃ³n de calidad
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
        Generar reporte especÃ­fico de una finca.
        
        Args:
            finca_id: ID de la finca
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            finca = Finca.objects.get(id=finca_id)
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # TÃ­tulo
            story.append(Paragraph(f"Reporte de Finca: {finca.nombre}", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # InformaciÃ³n de la finca
            story.extend(self._create_finca_info_section(finca))
            
            # EstadÃ­sticas de lotes
            lotes_stats = self._get_lotes_stats(finca)
            story.extend(self._create_lotes_stats_section(lotes_stats))
            
            # AnÃ¡lisis por lote
            story.extend(self._create_lotes_analysis_section(finca))
            
            # Recomendaciones especÃ­ficas
            story.extend(self._create_finca_recommendations_section(finca, lotes_stats))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte de finca: {e}")
            raise
    
    def generate_audit_report(self, user, filtros=None):
        """
        Generar reporte de auditorÃ­a.
        
        Args:
            user: Usuario que solicita el reporte
            filtros: Filtros a aplicar
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # TÃ­tulo
            story.append(Paragraph("Reporte de AuditorÃ­a del Sistema", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # InformaciÃ³n del reporte
            story.append(Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", self.styles['CustomSmall']))
            story.append(Paragraph(f"Administrador: {user.get_full_name() or user.username}", self.styles['CustomSmall']))
            story.append(Spacer(1, 20))
            
            # EstadÃ­sticas de actividad
            activity_stats = self._get_activity_stats(filtros)
            story.extend(self._create_activity_stats_section(activity_stats))
            
            # EstadÃ­sticas de logins
            login_stats = self._get_login_stats(filtros)
            story.extend(self._create_login_stats_section(login_stats))
            
            # Actividades recientes
            recent_activities = ActivityLog.objects.select_related('usuario').order_by('-timestamp')[:50]
            if recent_activities:
                story.extend(self._create_recent_activities_table(recent_activities))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando reporte de auditorÃ­a: {e}")
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
        story = []
        
        story.append(Paragraph("EstadÃ­sticas Generales", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        # Tabla de estadÃ­sticas
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de AnÃ¡lisis', str(stats['total_analyses'])],
            ['Confianza Promedio', f"{stats['avg_confidence']}%"],
            ['Alto Promedio', f"{stats['avg_dimensions']['alto']} mm"],
            ['Ancho Promedio', f"{stats['avg_dimensions']['ancho']} mm"],
            ['Grosor Promedio', f"{stats['avg_dimensions']['grosor']} mm"],
            ['Peso Promedio', f"{stats['avg_weight']} g"],
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_recent_analyses_table(self, analyses):
        """Crear tabla de anÃ¡lisis recientes."""
        story = []
        
        story.append(Paragraph("AnÃ¡lisis Recientes", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        # Encabezados
        data = [['Fecha', 'Usuario', 'Confianza', 'Alto (mm)', 'Ancho (mm)', 'Grosor (mm)', 'Peso (g)']]
        
        # Datos
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
        
        table = Table(data, colWidths=[1*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_quality_distribution_chart(self, queryset):
        """Crear grÃ¡fico de distribuciÃ³n de calidad."""
        story = []
        
        story.append(Paragraph("DistribuciÃ³n de Calidad", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        # Calcular distribuciÃ³n
        distribution = {
            'Excelente (â‰¥90%)': queryset.filter(average_confidence__gte=0.9).count(),
            'Buena (80-89%)': queryset.filter(average_confidence__gte=0.8, average_confidence__lt=0.9).count(),
            'Regular (70-79%)': queryset.filter(average_confidence__gte=0.7, average_confidence__lt=0.8).count(),
            'Baja (<70%)': queryset.filter(average_confidence__lt=0.7).count(),
        }
        
        total = sum(distribution.values())
        if total > 0:
            data = [['CategorÃ­a', 'Cantidad', 'Porcentaje']]
            for category, count in distribution.items():
                percentage = (count / total) * 100
                data.append([category, str(count), f"{percentage:.1f}%"])
            
            table = Table(data, colWidths=[2*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_recommendations_section(self, stats):
        """Crear secciÃ³n de recomendaciones."""
        story = []
        
        story.append(Paragraph("Recomendaciones", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        recommendations = []
        
        if stats['avg_confidence'] < 70:
            recommendations.append("â€¢ La confianza promedio es baja. Considere mejorar la calidad de las imÃ¡genes o el proceso de anÃ¡lisis.")
        
        if stats['avg_dimensions']['alto'] < 15 or stats['avg_dimensions']['alto'] > 25:
            recommendations.append("â€¢ Las dimensiones de los granos estÃ¡n fuera del rango Ã³ptimo. Revise el proceso de cosecha y selecciÃ³n.")
        
        if stats['avg_weight'] < 1.0 or stats['avg_weight'] > 2.5:
            recommendations.append("â€¢ El peso promedio de los granos no estÃ¡ en el rango esperado. Verifique la madurez de los granos.")
        
        if not recommendations:
            recommendations.append("â€¢ Los indicadores de calidad estÃ¡n dentro de rangos aceptables. Mantenga las buenas prÃ¡cticas actuales.")
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_finca_info_section(self, finca):
        """Crear secciÃ³n de informaciÃ³n de finca."""
        story = []
        
        story.append(Paragraph("InformaciÃ³n de la Finca", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        data = [
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
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
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
        story = []
        
        story.append(Paragraph("EstadÃ­sticas de Lotes", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de Lotes', str(stats['total_lotes'])],
            ['Lotes Activos', str(stats['lotes_activos'])],
            ['Ãrea Total', f"{stats['total_area']:.2f} ha"],
            ['Variedades', str(len(stats['variedades']))],
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_lotes_analysis_section(self, finca):
        """Crear secciÃ³n de anÃ¡lisis por lote."""
        story = []
        
        story.append(Paragraph("AnÃ¡lisis por Lote", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        lotes = finca.lotes.all()
        
        if lotes.exists():
            data = [['Lote', 'Variedad', 'Estado', 'Ãrea (ha)', 'AnÃ¡lisis', 'Calidad (%)']]
            
            for lote in lotes:
                data.append([
                    lote.identificador,
                    lote.variedad,
                    lote.get_estado_display(),
                    f"{lote.area_hectareas:.2f}",
                    str(lote.total_analisis),
                    f"{lote.calidad_promedio:.1f}",
                ])
            
            table = Table(data, colWidths=[1*inch, 1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_finca_recommendations_section(self, finca, stats):
        """Crear secciÃ³n de recomendaciones especÃ­ficas para la finca."""
        story = []
        
        story.append(Paragraph("Recomendaciones para la Finca", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        recommendations = []
        
        if stats['total_lotes'] == 0:
            recommendations.append("â€¢ Registre lotes en su finca para poder realizar anÃ¡lisis detallados.")
        
        if stats['lotes_activos'] < stats['total_lotes']:
            recommendations.append("â€¢ Revise los lotes inactivos y considere reactivarlos si es apropiado.")
        
        if len(stats['variedades']) == 1:
            recommendations.append("â€¢ Considere diversificar las variedades de cacao para mejorar la resistencia.")
        
        if finca.calidad_promedio < 70:
            recommendations.append("â€¢ La calidad promedio de la finca es baja. Revise las prÃ¡cticas de cosecha y post-cosecha.")
        
        if not recommendations:
            recommendations.append("â€¢ La finca muestra buenos indicadores. Mantenga las prÃ¡cticas actuales.")
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 20))
        
        return story
    
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
        story = []
        
        story.append(Paragraph("EstadÃ­sticas de Actividad", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de Actividades', str(stats['total_activities'])],
            ['Actividades Hoy', str(stats['activities_today'])],
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
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
        story = []
        
        story.append(Paragraph("EstadÃ­sticas de Logins", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        data = [
            ['MÃ©trica', 'Valor'],
            ['Total de Logins', str(stats['total_logins'])],
            ['Logins Exitosos', str(stats['successful_logins'])],
            ['Logins Fallidos', str(stats['failed_logins'])],
            ['Tasa de Ã‰xito', f"{stats['success_rate']:.1f}%"],
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_recent_activities_table(self, activities):
        """Crear tabla de actividades recientes."""
        story = []
        
        story.append(Paragraph("Actividades Recientes", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        data = [['Fecha', 'Usuario', 'AcciÃ³n', 'Modelo', 'DescripciÃ³n']]
        
        for activity in activities:
            data.append([
                activity.timestamp.strftime('%d/%m/%Y %H:%M'),
                activity.usuario.username if activity.usuario else 'AnÃ³nimo',
                activity.get_accion_display(),
                activity.modelo,
                activity.descripcion[:50] + '...' if len(activity.descripcion) > 50 else activity.descripcion,
            ])
        
        table = Table(data, colWidths=[1*inch, 1*inch, 0.8*inch, 0.8*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story


