"""
Service for generating reports in CacaoScan.
Handles report generation logic for different report types.
"""
import logging
from typing import Dict, Any, List
from django.db.models import Q, Count, Avg, Sum, Min, Max
from django.utils import timezone
from datetime import datetime
from django.db.models.functions import Extract

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from api.utils.model_imports import get_models_safely
from reports.models import ReporteGenerado

# Import models safely
models = get_models_safely({
    'CacaoPrediction': 'images_app.models.CacaoPrediction',
    'CacaoImage': 'images_app.models.CacaoImage',
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote'
})
CacaoPrediction = models['CacaoPrediction']
CacaoImage = models['CacaoImage']
Finca = models['Finca']
Lote = models['Lote']

from django.contrib.auth.models import User

logger = logging.getLogger("cacaoscan.services.reports.generation")


class ReportGenerationService(BaseService):
    """
    Service for handling report generation.
    """
    
    def __init__(self):
        super().__init__()
    
    def generate_analysis_report(self, user: User, report_data: Dict[str, Any]) -> ServiceResult:
        """
        Generates an analysis report for cacao grains.
        
        Args:
            user: User requesting the report
            report_data: Report data
            
        Returns:
            ServiceResult with generated report data
        """
        try:
            # Validate required fields
            required_fields = ['tipo_reporte', 'fecha_inicio', 'fecha_fin']
            self.validate_required_fields(report_data, required_fields)
            
            # Validate dates
            fecha_inicio = report_data['fecha_inicio']
            fecha_fin = report_data['fecha_fin']
            
            if fecha_inicio > fecha_fin:
                return ServiceResult.validation_error(
                    "La fecha de inicio debe ser anterior a la fecha de fin",
                    details={"field": "fecha_inicio"}
                )
            
            # Generate report data according to type
            report_type = report_data['tipo_reporte']
            
            if report_type == 'analisis_general':
                report_content = self._generate_general_analysis_report(user, fecha_inicio, fecha_fin)
            elif report_type == 'analisis_por_finca':
                finca_id = report_data.get('finca_id')
                if not finca_id:
                    return ServiceResult.validation_error(
                        "finca_id es requerido para reportes por finca",
                        details={"field": "finca_id"}
                    )
                report_content = self._generate_finca_analysis_report(user, finca_id, fecha_inicio, fecha_fin)
            elif report_type == 'analisis_por_lote':
                lote_id = report_data.get('lote_id')
                if not lote_id:
                    return ServiceResult.validation_error(
                        "lote_id es requerido para reportes por lote",
                        details={"field": "lote_id"}
                    )
                report_content = self._generate_lote_analysis_report(user, lote_id, fecha_inicio, fecha_fin)
            elif report_type == 'estadisticas_usuario':
                report_content = self._generate_user_statistics_report(user, fecha_inicio, fecha_fin)
            else:
                return ServiceResult.validation_error(
                    f"Tipo de reporte no válido: {report_type}",
                    details={"field": "tipo_reporte", "allowed_types": [
                        'analisis_general', 'analisis_por_finca', 'analisis_por_lote', 'estadisticas_usuario'
                    ]}
                )
            
            # Create report record
            reporte = ReporteGenerado(
                usuario=user,
                tipo_reporte=report_type,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                parametros=report_data,
                contenido=report_content,
                formato='json',
                estado='completado'
            )
            
            reporte.save()
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="report_generated",
                resource_type="reporte",
                resource_id=reporte.id,
                details={
                    'tipo_reporte': report_type,
                    'fecha_inicio': fecha_inicio.isoformat(),
                    'fecha_fin': fecha_fin.isoformat()
                }
            )
            
            self.log_info(f"Reporte {reporte.id} generado por usuario {user.username}")
            
            return ServiceResult.success(
                data={
                    'id': reporte.id,
                    'tipo_reporte': reporte.tipo_reporte,
                    'fecha_inicio': reporte.fecha_inicio.isoformat(),
                    'fecha_fin': reporte.fecha_fin.isoformat(),
                    'contenido': reporte.contenido,
                    'created_at': reporte.created_at.isoformat(),
                    'formato': reporte.formato,
                    'estado': reporte.estado
                },
                message="Reporte generado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error generando reporte: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno generando reporte", details={"original_error": str(e)})
            )
    
    def _generate_general_analysis_report(self, user: User, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Generates general analysis report.
        
        Args:
            user: User
            fecha_inicio: Start date
            fecha_fin: End date
            
        Returns:
            Dictionary with report data
        """
        # Get user predictions in date range
        predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        )
        
        # Calculate statistics
        total_analyses = predictions.count()
        
        if total_analyses == 0:
            return {
                'resumen': {
                    'total_analisis': 0,
                    'mensaje': 'No hay análisis en el período seleccionado'
                }
            }
        
        # Dimension statistics
        dimension_stats = {
            'alto_mm': {
                'promedio': float(predictions.aggregate(avg=Avg('alto_mm'))['avg'] or 0),
                'minimo': float(predictions.aggregate(min=Min('alto_mm'))['min'] or 0),
                'maximo': float(predictions.aggregate(max=Max('alto_mm'))['max'] or 0),
                'desviacion': self._calculate_std_dev(predictions, 'alto_mm')
            },
            'ancho_mm': {
                'promedio': float(predictions.aggregate(avg=Avg('ancho_mm'))['avg'] or 0),
                'minimo': float(predictions.aggregate(min=Min('ancho_mm'))['min'] or 0),
                'maximo': float(predictions.aggregate(max=Max('ancho_mm'))['max'] or 0),
                'desviacion': self._calculate_std_dev(predictions, 'ancho_mm')
            },
            'grosor_mm': {
                'promedio': float(predictions.aggregate(avg=Avg('grosor_mm'))['avg'] or 0),
                'minimo': float(predictions.aggregate(min=Min('grosor_mm'))['min'] or 0),
                'maximo': float(predictions.aggregate(max=Max('grosor_mm'))['max'] or 0),
                'desviacion': self._calculate_std_dev(predictions, 'grosor_mm')
            },
            'peso_g': {
                'promedio': float(predictions.aggregate(avg=Avg('peso_g'))['avg'] or 0),
                'minimo': float(predictions.aggregate(min=Min('peso_g'))['min'] or 0),
                'maximo': float(predictions.aggregate(max=Max('peso_g'))['max'] or 0),
                'desviacion': self._calculate_std_dev(predictions, 'peso_g')
            }
        }
        
        # Confidence statistics
        confidence_stats = {
            'promedio': float(predictions.aggregate(avg=Avg('average_confidence'))['avg'] or 0),
            'minimo': float(predictions.aggregate(min=Min('average_confidence'))['min'] or 0),
            'maximo': float(predictions.aggregate(max=Max('average_confidence'))['max'] or 0),
            'distribucion': {
                'alta': predictions.filter(average_confidence__gte=0.8).count(),
                'media': predictions.filter(average_confidence__gte=0.6, average_confidence__lt=0.8).count(),
                'baja': predictions.filter(average_confidence__lt=0.6).count()
            }
        }
        
        # Processing time statistics
        processing_stats = {
            'promedio_ms': float(predictions.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0),
            'minimo_ms': float(predictions.aggregate(min=Min('processing_time_ms'))['min'] or 0),
            'maximo_ms': float(predictions.aggregate(max=Max('processing_time_ms'))['max'] or 0)
        }
        
        # Daily analysis
        daily_analysis = self._get_daily_analysis(predictions)
        
        return {
            'resumen': {
                'total_analisis': total_analyses,
                'fecha_inicio': fecha_inicio.isoformat(),
                'fecha_fin': fecha_fin.isoformat(),
                'periodo_dias': (fecha_fin - fecha_inicio).days + 1
            },
            'estadisticas_dimensiones': dimension_stats,
            'estadisticas_confianza': confidence_stats,
            'estadisticas_procesamiento': processing_stats,
            'analisis_diario': daily_analysis,
            'recomendaciones': self._generate_recommendations(dimension_stats, confidence_stats)
        }
    
    def _generate_finca_analysis_report(self, user: User, finca_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Generates finca analysis report.
        
        Args:
            user: User
            finca_id: Finca ID
            fecha_inicio: Start date
            fecha_fin: End date
            
        Returns:
            Dictionary with report data
        """
        try:
            finca = Finca.objects.get(id=finca_id, agricultor=user)
        except Finca.DoesNotExist:
            return {'error': 'Finca no encontrada'}
        
        # Get predictions from images associated with finca lots
        predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).filter(
            Q(image__metadata__finca_id=finca_id) | 
            Q(image__metadata__finca=finca_id)
        )
        
        # Generate base report
        base_report = self._generate_general_analysis_report(user, fecha_inicio, fecha_fin)
        
        # Add finca-specific information
        base_report['finca'] = {
            'id': finca.id,
            'nombre': finca.nombre,
            'municipio': finca.municipio,
            'departamento': finca.departamento,
            'hectareas': finca.hectareas
        }
        
        # Statistics by lote
        lotes_stats = []
        for lote in finca.lotes.all():
            lote_predictions = predictions.filter(
                Q(image__metadata__lote_id=lote.id) | 
                Q(image__metadata__lote=lote.id)
            )
            
            if lote_predictions.exists():
                lotes_stats.append({
                    'lote_id': lote.id,
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'total_analisis': lote_predictions.count(),
                    'promedio_peso': float(lote_predictions.aggregate(avg=Avg('peso_g'))['avg'] or 0),
                    'promedio_confianza': float(lote_predictions.aggregate(avg=Avg('average_confidence'))['avg'] or 0)
                })
        
        base_report['estadisticas_por_lote'] = lotes_stats
        
        return base_report
    
    def _generate_lote_analysis_report(self, user: User, lote_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Generates lote analysis report.
        
        Args:
            user: User
            lote_id: Lote ID
            fecha_inicio: Start date
            fecha_fin: End date
            
        Returns:
            Dictionary with report data
        """
        try:
            lote = Lote.objects.select_related('finca').get(id=lote_id, finca__agricultor=user)
        except Lote.DoesNotExist:
            return {'error': 'Lote no encontrado'}
        
        # Get predictions from images associated with the lote
        predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).filter(
            Q(image__metadata__lote_id=lote_id) | 
            Q(image__metadata__lote=lote_id)
        )
        
        # Generate base report
        base_report = self._generate_general_analysis_report(user, fecha_inicio, fecha_fin)
        
        # Add lote-specific information
        base_report['lote'] = {
            'id': lote.id,
            'identificador': lote.identificador,
            'variedad': lote.variedad,
            'hectareas': lote.hectareas,
            'edad_plantas': lote.edad_plantas,
            'estado': lote.estado,
            'finca': {
                'id': lote.finca.id,
                'nombre': lote.finca.nombre,
                'municipio': lote.finca.municipio,
                'departamento': lote.finca.departamento
            }
        }
        
        return base_report
    
    def _generate_user_statistics_report(self, user: User, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Generates user statistics report.
        
        Args:
            user: User
            fecha_inicio: Start date
            fecha_fin: End date
            
        Returns:
            Dictionary with report data
        """
        # General user statistics
        total_images = CacaoImage.objects.filter(user=user).count()
        total_predictions = CacaoPrediction.objects.filter(image__user=user).count()
        total_fincas = Finca.objects.filter(agricultor=user).count()
        total_lotes = Lote.objects.filter(finca__agricultor=user).count()
        
        # Statistics in the period
        period_images = CacaoImage.objects.filter(
            user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).count()
        
        period_predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).count()
        
        # Activity analysis
        activity_analysis = self._get_user_activity_analysis(user, fecha_inicio, fecha_fin)
        
        return {
            'resumen_usuario': {
                'total_imagenes': total_images,
                'total_analisis': total_predictions,
                'total_fincas': total_fincas,
                'total_lotes': total_lotes,
                'imagenes_periodo': period_images,
                'analisis_periodo': period_predictions
            },
            'analisis_actividad': activity_analysis,
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat()
        }
    
    def _calculate_std_dev(self, queryset, field: str) -> float:
        """
        Calculates standard deviation of a field.
        
        Args:
            queryset: QuerySet
            field: Field to calculate
            
        Returns:
            Standard deviation
        """
        values = list(queryset.values_list(field, flat=True))
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return float(variance ** 0.5)
    
    def _get_daily_analysis(self, predictions) -> List[Dict[str, Any]]:
        """
        Gets daily analysis.
        
        Args:
            predictions: QuerySet of predictions
            
        Returns:
            List with daily analysis
        """
        daily_data = []
        
        # Group by day
        daily_stats = predictions.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id'),
            avg_confidence=Avg('average_confidence'),
            avg_weight=Avg('peso_g')
        ).order_by('day')
        
        for day_stat in daily_stats:
            daily_data.append({
                'fecha': day_stat['day'],
                'total_analisis': day_stat['count'],
                'promedio_confianza': float(day_stat['avg_confidence'] or 0),
                'promedio_peso': float(day_stat['avg_weight'] or 0)
            })
        
        return daily_data
    
    def _generate_recommendations(self, dimension_stats: Dict, confidence_stats: Dict) -> List[str]:
        """
        Generates recommendations based on statistics.
        
        Args:
            dimension_stats: Dimension statistics
            confidence_stats: Confidence statistics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Recommendations based on confidence
        if confidence_stats['promedio'] < 0.7:
            recommendations.append("La confianza promedio es baja. Considera mejorar la calidad de las imágenes.")
        
        if confidence_stats['distribucion']['baja'] > confidence_stats['distribucion']['alta']:
            recommendations.append("Hay más análisis con baja confianza que alta. Revisa las condiciones de captura.")
        
        # Recommendations based on dimensions
        peso_promedio = dimension_stats['peso_g']['promedio']
        if peso_promedio < 1.0:
            recommendations.append("El peso promedio es bajo. Verifica la calibración del sistema.")
        elif peso_promedio > 3.0:
            recommendations.append("El peso promedio es alto. Verifica la calibración del sistema.")
        
        return recommendations
    
    def _get_user_activity_analysis(self, user: User, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Gets user activity analysis.
        
        Args:
            user: User
            fecha_inicio: Start date
            fecha_fin: End date
            
        Returns:
            Dictionary with activity analysis
        """
        # Activity by day of week
        weekly_activity = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).annotate(
            day_of_week=Extract('created_at', 'dow')
        ).values('day_of_week').annotate(
            count=Count('id')
        ).order_by('day_of_week')
        
        # Activity by hour of day
        hourly_activity = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).annotate(
            hour=Extract('created_at', 'hour')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        return {
            'actividad_semanal': list(weekly_activity),
            'actividad_horaria': list(hourly_activity)
        }

