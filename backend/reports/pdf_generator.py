"""
Generador de reportes PDF para CacaoScan.
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import FileResponse
from django.utils import timezone
from django.db.models import Q
import io
import os
from datetime import datetime


class CacaoReportPDFGenerator:
    """
    Generador de reportes PDF para anÃ¡lisis de cacao.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados."""
        # Estilo para tÃ­tulo principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        ))
        
        # Estilo para subtÃ­tulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_quality_report(self, images_queryset, user, filters=None):
        """
        Generar reporte de calidad de cacao.
        
        Args:
            images_queryset: QuerySet de CacaoImage con predicciones
            user: Usuario que solicita el reporte
            filters: Diccionario con filtros aplicados
            
        Returns:
            BytesIO buffer con el PDF generado
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        # TÃ­tulo principal
        title = Paragraph(f"Reporte de Calidad de Cacao", self.styles['CustomTitle'])
        elements.append(title)
        
        # InformaciÃ³n del usuario y fecha
        user_info = f"<b>Usuario:</b> {user.get_full_name() or user.username}<br/>"
        user_info += f"<b>Email:</b> {user.email}<br/>"
        user_info += f"<b>Fecha de generaciÃ³n:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        
        if filters:
            user_info += "<br/><b>Filtros aplicados:</b><br/>"
            for key, value in filters.items():
                if value:
                    user_info += f"â€¢ {key}: {value}<br/>"
        
        user_paragraph = Paragraph(user_info, self.styles['CustomNormal'])
        elements.append(user_paragraph)
        elements.append(Spacer(1, 20))
        
        # EstadÃ­sticas generales
        stats = self._calculate_statistics(images_queryset)
        elements.extend(self._add_statistics_section(stats))
        
        # Tabla de datos detallados
        elements.extend(self._add_data_table(images_queryset))
        
        # GrÃ¡fico de distribuciÃ³n (si hay datos)
        if images_queryset.exists():
            elements.extend(self._add_distribution_chart(images_queryset))
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_defects_report(self, images_queryset, user, filters=None):
        """
        Generar reporte de defectos de cacao.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        # TÃ­tulo
        title = Paragraph("Reporte de Defectos de Cacao", self.styles['CustomTitle'])
        elements.append(title)
        
        # InformaciÃ³n del usuario
        user_info = f"<b>Usuario:</b> {user.get_full_name() or user.username}<br/>"
        user_info += f"<b>Fecha:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(user_info, self.styles['CustomNormal']))
        elements.append(Spacer(1, 20))
        
        # AnÃ¡lisis de defectos por confianza baja
        low_confidence_images = images_queryset.filter(
            prediction__average_confidence__lt=0.7
        ).select_related('prediction')
        
        if low_confidence_images.exists():
            elements.append(Paragraph("AnÃ¡lisis de Defectos Detectados", self.styles['CustomHeading']))
            
            # Tabla de defectos
            defect_data = [['ID', 'Finca', 'Confianza Promedio', 'Problema Detectado']]
            for image in low_confidence_images:
                pred = image.prediction
                problem = self._identify_defect_type(pred)
                defect_data.append([
                    str(image.id),
                    image.finca or 'N/A',
                    f"{pred.average_confidence:.2%}",
                    problem
                ])
            
            defect_table = Table(defect_data)
            defect_table.setStyle(self._get_table_style())
            elements.append(defect_table)
        else:
            elements.append(Paragraph("No se detectaron defectos significativos en el perÃ­odo analizado.", 
                                    self.styles['CustomNormal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_performance_report(self, images_queryset, user, filters=None):
        """
        Generar reporte de rendimiento por perÃ­odo.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        # TÃ­tulo
        title = Paragraph("Reporte de Rendimiento", self.styles['CustomTitle'])
        elements.append(title)
        
        # InformaciÃ³n del usuario
        user_info = f"<b>Usuario:</b> {user.get_full_name() or user.username}<br/>"
        user_info += f"<b>Fecha:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(user_info, self.styles['CustomNormal']))
        elements.append(Spacer(1, 20))
        
        # MÃ©tricas de rendimiento
        performance_stats = self._calculate_performance_metrics(images_queryset)
        elements.extend(self._add_performance_metrics(performance_stats))
        
        # AnÃ¡lisis temporal
        elements.extend(self._add_temporal_analysis(images_queryset))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _calculate_statistics(self, images_queryset):
        """Calcular estadÃ­sticas generales."""
        images_with_predictions = images_queryset.filter(prediction__isnull=False)
        
        if not images_with_predictions.exists():
            return {
                'total_images': images_queryset.count(),
                'processed_images': 0,
                'avg_dimensions': {},
                'avg_confidence': 0,
                'regions': [],
                'fincas': []
            }
        
        # EstadÃ­sticas de dimensiones
        predictions = [img.prediction for img in images_with_predictions]
        
        avg_alto = sum(p.alto_mm for p in predictions) / len(predictions)
        avg_ancho = sum(p.ancho_mm for p in predictions) / len(predictions)
        avg_grosor = sum(p.grosor_mm for p in predictions) / len(predictions)
        avg_peso = sum(p.peso_g for p in predictions) / len(predictions)
        avg_confidence = sum(p.average_confidence for p in predictions) / len(predictions)
        
        # Regiones y fincas mÃ¡s comunes
        regions = images_queryset.values_list('region', flat=True).exclude(region__isnull=True).exclude(region='')
        fincas = images_queryset.values_list('finca', flat=True).exclude(finca__isnull=True).exclude(finca='')
        
        return {
            'total_images': images_queryset.count(),
            'processed_images': images_with_predictions.count(),
            'avg_dimensions': {
                'alto': avg_alto,
                'ancho': avg_ancho,
                'grosor': avg_grosor,
                'peso': avg_peso
            },
            'avg_confidence': avg_confidence,
            'regions': list(set(regions))[:5],  # Top 5
            'fincas': list(set(fincas))[:5]     # Top 5
        }
    
    def _add_statistics_section(self, stats):
        """Agregar secciÃ³n de estadÃ­sticas."""
        elements = []
        
        elements.append(Paragraph("EstadÃ­sticas Generales", self.styles['CustomHeading']))
        
        # Tabla de estadÃ­sticas
        stats_data = [
            ['MÃ©trica', 'Valor'],
            ['Total de imÃ¡genes', str(stats['total_images'])],
            ['ImÃ¡genes procesadas', str(stats['processed_images'])],
            ['Tasa de procesamiento', f"{(stats['processed_images']/stats['total_images']*100):.1f}%" if stats['total_images'] > 0 else "0%"],
            ['Confianza promedio', f"{stats['avg_confidence']:.2%}"],
            ['', ''],
            ['Dimensiones Promedio', ''],
            ['Alto (mm)', f"{stats['avg_dimensions'].get('alto', 0):.2f}"],
            ['Ancho (mm)', f"{stats['avg_dimensions'].get('ancho', 0):.2f}"],
            ['Grosor (mm)', f"{stats['avg_dimensions'].get('grosor', 0):.2f}"],
            ['Peso (g)', f"{stats['avg_dimensions'].get('peso', 0):.2f}"]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(self._get_table_style())
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_data_table(self, images_queryset):
        """Agregar tabla de datos detallados."""
        elements = []
        
        elements.append(Paragraph("Datos Detallados", self.styles['CustomHeading']))
        
        # Preparar datos de la tabla
        table_data = [['ID', 'Finca', 'RegiÃ³n', 'Alto (mm)', 'Ancho (mm)', 'Grosor (mm)', 'Peso (g)', 'Confianza']]
        
        images_with_predictions = images_queryset.filter(prediction__isnull=False).select_related('prediction')[:50]  # Limitar a 50 registros
        
        for image in images_with_predictions:
            pred = image.prediction
            table_data.append([
                str(image.id),
                image.finca or 'N/A',
                image.region or 'N/A',
                f"{pred.alto_mm:.2f}",
                f"{pred.ancho_mm:.2f}",
                f"{pred.grosor_mm:.2f}",
                f"{pred.peso_g:.2f}",
                f"{pred.average_confidence:.2%}"
            ])
        
        if len(table_data) > 1:  # Si hay datos ademÃ¡s del header
            data_table = Table(table_data)
            data_table.setStyle(self._get_table_style())
            elements.append(data_table)
        else:
            elements.append(Paragraph("No hay datos de predicciones disponibles.", self.styles['CustomNormal']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _add_distribution_chart(self, images_queryset):
        """Agregar anÃ¡lisis de distribuciÃ³n."""
        elements = []
        
        elements.append(Paragraph("AnÃ¡lisis de DistribuciÃ³n", self.styles['CustomHeading']))
        
        # AnÃ¡lisis por regiÃ³n
        region_stats = images_queryset.values('region').annotate(
            count=models.Count('id')
        ).exclude(region__isnull=True).exclude(region='').order_by('-count')[:5]
        
        if region_stats:
            region_data = [['RegiÃ³n', 'Cantidad de ImÃ¡genes']]
            for stat in region_stats:
                region_data.append([stat['region'] or 'Sin regiÃ³n', str(stat['count'])])
            
            region_table = Table(region_data)
            region_table.setStyle(self._get_table_style())
            elements.append(region_table)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _add_performance_metrics(self, performance_stats):
        """Agregar mÃ©tricas de rendimiento."""
        elements = []
        
        elements.append(Paragraph("MÃ©tricas de Rendimiento", self.styles['CustomHeading']))
        
        perf_data = [
            ['MÃ©trica', 'Valor'],
            ['ImÃ¡genes procesadas hoy', str(performance_stats.get('today', 0))],
            ['ImÃ¡genes procesadas esta semana', str(performance_stats.get('this_week', 0))],
            ['ImÃ¡genes procesadas este mes', str(performance_stats.get('this_month', 0))],
            ['Tiempo promedio de procesamiento', f"{performance_stats.get('avg_processing_time', 0):.0f} ms"],
            ['Confianza promedio', f"{performance_stats.get('avg_confidence', 0):.2%}"]
        ]
        
        perf_table = Table(perf_data)
        perf_table.setStyle(self._get_table_style())
        elements.append(perf_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_temporal_analysis(self, images_queryset):
        """Agregar anÃ¡lisis temporal."""
        elements = []
        
        elements.append(Paragraph("AnÃ¡lisis Temporal", self.styles['CustomHeading']))
        
        # Agrupar por fecha
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        daily_stats = images_queryset.filter(
            created_at__date__gte=week_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        if daily_stats:
            temporal_data = [['Fecha', 'ImÃ¡genes Procesadas']]
            for stat in daily_stats:
                temporal_data.append([stat['day'].strftime('%d/%m/%Y'), str(stat['count'])])
            
            temporal_table = Table(temporal_data)
            temporal_table.setStyle(self._get_table_style())
            elements.append(temporal_table)
        
        return elements
    
    def _calculate_performance_metrics(self, images_queryset):
        """Calcular mÃ©tricas de rendimiento."""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        images_with_predictions = images_queryset.filter(prediction__isnull=False)
        
        return {
            'today': images_queryset.filter(created_at__date=today).count(),
            'this_week': images_queryset.filter(created_at__date__gte=week_ago).count(),
            'this_month': images_queryset.filter(created_at__date__gte=month_ago).count(),
            'avg_processing_time': images_with_predictions.aggregate(
                avg_time=models.Avg('prediction__processing_time_ms')
            )['avg_time'] or 0,
            'avg_confidence': images_with_predictions.aggregate(
                avg_conf=models.Avg('prediction__average_confidence')
            )['avg_conf'] or 0
        }
    
    def _identify_defect_type(self, prediction):
        """Identificar tipo de defecto basado en confidencias."""
        confidences = [
            prediction.confidence_alto,
            prediction.confidence_ancho,
            prediction.confidence_grosor,
            prediction.confidence_peso
        ]
        
        min_confidence = min(confidences)
        
        if min_confidence < 0.5:
            return "Defecto severo - mediciÃ³n poco confiable"
        elif min_confidence < 0.7:
            return "Defecto moderado - mediciÃ³n con dudas"
        else:
            return "Sin defectos detectados"
    
    def _get_table_style(self):
        """Obtener estilo para tablas."""
        from reportlab.platypus import TableStyle
        
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ])


# Importar modelos necesarios
from django.db import models


