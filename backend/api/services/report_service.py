"""
Servicio de reportes para CacaoScan.
"""
import logging
from typing import Dict, Any, Optional, List
from django.db.models import Q, Count, Avg, Sum, Min, Max
from django.utils import timezone
from datetime import timedelta, datetime
import json

from .base import BaseService, ServiceResult, ValidationServiceError, PermissionServiceError, NotFoundServiceError
from ..models import ReporteGenerado
# Importar desde apps modulares
try:
    from images_app.models import CacaoPrediction, CacaoImage
except ImportError:
    CacaoPrediction = None
    CacaoImage = None

try:
    from fincas_app.models import Finca, Lote
except ImportError:
    Finca = None
    Lote = None

from django.contrib.auth.models import User

logger = logging.getLogger("cacaoscan.services.reports")


class ReportService(BaseService):
    """
    Servicio para manejar generación y gestión de reportes.
    """
    
    def __init__(self):
        super().__init__()
    
    def generate_analysis_report(self, user: User, report_data: Dict[str, Any]) -> ServiceResult:
        """
        Genera un reporte de análisis de granos de cacao.
        
        Args:
            user: Usuario que solicita el reporte
            report_data: Datos del reporte
            
        Returns:
            ServiceResult con datos del reporte generado
        """
        try:
            # Validar campos requeridos
            required_fields = ['tipo_reporte', 'fecha_inicio', 'fecha_fin']
            self.validate_required_fields(report_data, required_fields)
            
            # Validar fechas
            fecha_inicio = report_data['fecha_inicio']
            fecha_fin = report_data['fecha_fin']
            
            if fecha_inicio > fecha_fin:
                return ServiceResult.validation_error(
                    "La fecha de inicio debe ser anterior a la fecha de fin",
                    details={"field": "fecha_inicio"}
                )
            
            # Generar datos del reporte según el tipo
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
            
            # Crear registro del reporte
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
            
            # Crear log de auditoría
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
    
    def get_user_reports(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene reportes de un usuario.
        
        Args:
            user: Usuario
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con reportes paginados
        """
        try:
            # Construir queryset
            queryset = ReporteGenerado.objects.filter(usuario=user).order_by('-created_at')
            
            # Aplicar filtros
            if filters:
                if 'tipo_reporte' in filters:
                    queryset = queryset.filter(tipo_reporte=filters['tipo_reporte'])
                if 'estado' in filters:
                    queryset = queryset.filter(estado=filters['estado'])
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Paginar resultados
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Formatear datos
            reports = []
            for report in paginated_data['results']:
                reports.append({
                    'id': report.id,
                    'tipo_reporte': report.tipo_reporte,
                    'fecha_inicio': report.fecha_inicio.isoformat(),
                    'fecha_fin': report.fecha_fin.isoformat(),
                    'formato': report.formato,
                    'estado': report.estado,
                    'created_at': report.created_at.isoformat(),
                    'parametros': report.parametros,
                    'contenido_resumen': self._get_report_summary(report.contenido)
                })
            
            return ServiceResult.success(
                data={
                    'reports': reports,
                    'pagination': paginated_data['pagination']
                },
                message="Reportes obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo reportes: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo reportes", details={"original_error": str(e)})
            )
    
    def get_report_details(self, report_id: int, user: User) -> ServiceResult:
        """
        Obtiene detalles de un reporte específico.
        
        Args:
            report_id: ID del reporte
            user: Usuario
            
        Returns:
            ServiceResult con detalles del reporte
        """
        try:
            try:
                report = ReporteGenerado.objects.get(id=report_id, usuario=user)
            except ReporteGenerado.DoesNotExist:
                return ServiceResult.not_found_error("Reporte no encontrado")
            
            report_data = {
                'id': report.id,
                'tipo_reporte': report.tipo_reporte,
                'fecha_inicio': report.fecha_inicio.isoformat(),
                'fecha_fin': report.fecha_fin.isoformat(),
                'contenido': report.contenido,
                'formato': report.formato,
                'estado': report.estado,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat(),
                'parametros': report.parametros,
                'archivo_url': report.archivo.url if report.archivo else None
            }
            
            return ServiceResult.success(
                data=report_data,
                message="Detalles del reporte obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo detalles: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo detalles", details={"original_error": str(e)})
            )
    
    def delete_report(self, report_id: int, user: User) -> ServiceResult:
        """
        Elimina un reporte.
        
        Args:
            report_id: ID del reporte
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminación
        """
        try:
            try:
                report = ReporteGenerado.objects.get(id=report_id, usuario=user)
            except ReporteGenerado.DoesNotExist:
                return ServiceResult.not_found_error("Reporte no encontrado")
            
            # Crear log de auditoría antes de eliminar
            self.create_audit_log(
                user=user,
                action="report_deleted",
                resource_type="reporte",
                resource_id=report_id,
                details={
                    'tipo_reporte': report.tipo_reporte,
                    'fecha_inicio': report.fecha_inicio.isoformat(),
                    'fecha_fin': report.fecha_fin.isoformat()
                }
            )
            
            # Eliminar reporte
            report.delete()
            
            self.log_info(f"Reporte {report_id} eliminado por usuario {user.username}")
            
            return ServiceResult.success(
                message="Reporte eliminado exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error eliminando reporte: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando reporte", details={"original_error": str(e)})
            )
    
    def get_report_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene estadísticas de reportes de un usuario.
        
        Args:
            user: Usuario
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con estadísticas
        """
        try:
            # Construir queryset base
            queryset = ReporteGenerado.objects.filter(usuario=user)
            
            # Aplicar filtros
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Calcular estadísticas
            stats = {
                'total_reports': queryset.count(),
                'reports_by_type': dict(queryset.values('tipo_reporte').annotate(count=Count('id')).values_list('tipo_reporte', 'count')),
                'reports_by_status': dict(queryset.values('estado').annotate(count=Count('id')).values_list('estado', 'count')),
                'recent_reports': queryset.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(),
                'average_reports_per_month': self._calculate_monthly_average(queryset),
                'most_used_report_type': self._get_most_used_report_type(queryset)
            }
            
            return ServiceResult.success(
                data=stats,
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo estadísticas", details={"original_error": str(e)})
            )
    
    def _generate_general_analysis_report(self, user: User, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Genera reporte de análisis general.
        
        Args:
            user: Usuario
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Diccionario con datos del reporte
        """
        # Obtener predicciones del usuario en el rango de fechas
        predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        )
        
        # Calcular estadísticas
        total_analyses = predictions.count()
        
        if total_analyses == 0:
            return {
                'resumen': {
                    'total_analisis': 0,
                    'mensaje': 'No hay análisis en el período seleccionado'
                }
            }
        
        # Estadísticas de dimensiones
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
        
        # Estadísticas de confianza
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
        
        # Estadísticas de tiempo de procesamiento
        processing_stats = {
            'promedio_ms': float(predictions.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0),
            'minimo_ms': float(predictions.aggregate(min=Min('processing_time_ms'))['min'] or 0),
            'maximo_ms': float(predictions.aggregate(max=Max('processing_time_ms'))['max'] or 0)
        }
        
        # Análisis por día
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
        Genera reporte de análisis por finca.
        
        Args:
            user: Usuario
            finca_id: ID de la finca
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Diccionario con datos del reporte
        """
        try:
            finca = Finca.objects.get(id=finca_id, agricultor=user)
        except Finca.DoesNotExist:
            return {'error': 'Finca no encontrada'}
        
        # Obtener predicciones de imágenes asociadas a lotes de la finca
        predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).filter(
            Q(image__metadata__finca_id=finca_id) | 
            Q(image__metadata__finca=finca_id)
        )
        
        # Generar reporte base
        base_report = self._generate_general_analysis_report(user, fecha_inicio, fecha_fin)
        
        # Agregar información específica de la finca
        base_report['finca'] = {
            'id': finca.id,
            'nombre': finca.nombre,
            'municipio': finca.municipio,
            'departamento': finca.departamento,
            'hectareas': finca.hectareas
        }
        
        # Estadísticas por lote
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
        Genera reporte de análisis por lote.
        
        Args:
            user: Usuario
            lote_id: ID del lote
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Diccionario con datos del reporte
        """
        try:
            lote = Lote.objects.select_related('finca').get(id=lote_id, finca__agricultor=user)
        except Lote.DoesNotExist:
            return {'error': 'Lote no encontrado'}
        
        # Obtener predicciones de imágenes asociadas al lote
        predictions = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).filter(
            Q(image__metadata__lote_id=lote_id) | 
            Q(image__metadata__lote=lote_id)
        )
        
        # Generar reporte base
        base_report = self._generate_general_analysis_report(user, fecha_inicio, fecha_fin)
        
        # Agregar información específica del lote
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
        Genera reporte de estadísticas del usuario.
        
        Args:
            user: Usuario
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Diccionario con datos del reporte
        """
        # Estadísticas generales del usuario
        total_images = CacaoImage.objects.filter(user=user).count()
        total_predictions = CacaoPrediction.objects.filter(image__user=user).count()
        total_fincas = Finca.objects.filter(agricultor=user).count()
        total_lotes = Lote.objects.filter(finca__agricultor=user).count()
        
        # Estadísticas en el período
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
        
        # Análisis de actividad
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
    
    def _get_report_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene un resumen del contenido del reporte.
        
        Args:
            content: Contenido del reporte
            
        Returns:
            Diccionario con resumen
        """
        if 'resumen' in content:
            return content['resumen']
        elif 'resumen_usuario' in content:
            return content['resumen_usuario']
        else:
            return {'total_items': len(content)}
    
    def _calculate_std_dev(self, queryset, field: str) -> float:
        """
        Calcula la desviación estándar de un campo.
        
        Args:
            queryset: QuerySet
            field: Campo a calcular
            
        Returns:
            Desviación estándar
        """
        values = list(queryset.values_list(field, flat=True))
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return float(variance ** 0.5)
    
    def _get_daily_analysis(self, predictions) -> List[Dict[str, Any]]:
        """
        Obtiene análisis por día.
        
        Args:
            predictions: QuerySet de predicciones
            
        Returns:
            Lista con análisis diario
        """
        daily_data = []
        
        # Agrupar por día
        from django.db.models import Count, Avg
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
        Genera recomendaciones basadas en las estadísticas.
        
        Args:
            dimension_stats: Estadísticas de dimensiones
            confidence_stats: Estadísticas de confianza
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones basadas en confianza
        if confidence_stats['promedio'] < 0.7:
            recommendations.append("La confianza promedio es baja. Considera mejorar la calidad de las imágenes.")
        
        if confidence_stats['distribucion']['baja'] > confidence_stats['distribucion']['alta']:
            recommendations.append("Hay más análisis con baja confianza que alta. Revisa las condiciones de captura.")
        
        # Recomendaciones basadas en dimensiones
        peso_promedio = dimension_stats['peso_g']['promedio']
        if peso_promedio < 1.0:
            recommendations.append("El peso promedio es bajo. Verifica la calibración del sistema.")
        elif peso_promedio > 3.0:
            recommendations.append("El peso promedio es alto. Verifica la calibración del sistema.")
        
        return recommendations
    
    def _get_user_activity_analysis(self, user: User, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """
        Obtiene análisis de actividad del usuario.
        
        Args:
            user: Usuario
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Diccionario con análisis de actividad
        """
        # Actividad por día de la semana
        from django.db.models import Count
        from django.db.models.functions import Extract
        
        weekly_activity = CacaoPrediction.objects.filter(
            image__user=user,
            created_at__gte=fecha_inicio,
            created_at__lte=fecha_fin
        ).annotate(
            day_of_week=Extract('created_at', 'dow')
        ).values('day_of_week').annotate(
            count=Count('id')
        ).order_by('day_of_week')
        
        # Actividad por hora del día
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
    
    def _calculate_monthly_average(self, queryset) -> float:
        """
        Calcula el promedio mensual de reportes.
        
        Args:
            queryset: QuerySet de reportes
            
        Returns:
            Promedio mensual
        """
        from django.db.models import Count
        from django.db.models.functions import Extract
        
        monthly_counts = queryset.annotate(
            month=Extract('created_at', 'month'),
            year=Extract('created_at', 'year')
        ).values('year', 'month').annotate(
            count=Count('id')
        )
        
        if not monthly_counts:
            return 0.0
        
        total_months = len(monthly_counts)
        total_reports = sum(item['count'] for item in monthly_counts)
        
        return total_reports / total_months if total_months > 0 else 0.0
    
    def _get_most_used_report_type(self, queryset) -> str:
        """
        Obtiene el tipo de reporte más usado.
        
        Args:
            queryset: QuerySet de reportes
            
        Returns:
            Tipo de reporte más usado
        """
        from django.db.models import Count
        
        most_used = queryset.values('tipo_reporte').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        return most_used['tipo_reporte'] if most_used else 'N/A'
