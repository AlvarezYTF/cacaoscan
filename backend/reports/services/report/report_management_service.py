"""
Service for managing reports in CacaoScan.
Handles report retrieval, deletion, and statistics.
"""
import logging
from typing import Dict, Any
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Extract

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from reports.models import ReporteGenerado

from django.contrib.auth.models import User

logger = logging.getLogger("cacaoscan.services.reports.management")


class ReportManagementService(BaseService):
    """
    Service for handling report management operations.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_user_reports(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets reports for a user.
        
        Args:
            user: User
            page: Page number
            page_size: Page size
            filters: Additional filters
            
        Returns:
            ServiceResult with paginated reports
        """
        try:
            # Build queryset
            queryset = ReporteGenerado.objects.filter(usuario=user).order_by('-created_at')
            
            # Apply filters
            if filters:
                if 'tipo_reporte' in filters:
                    queryset = queryset.filter(tipo_reporte=filters['tipo_reporte'])
                if 'estado' in filters:
                    queryset = queryset.filter(estado=filters['estado'])
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Paginate results
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Format data
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
        Gets details of a specific report.
        
        Args:
            report_id: Report ID
            user: User
            
        Returns:
            ServiceResult with report details
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
        Deletes a report.
        
        Args:
            report_id: Report ID
            user: User
            
        Returns:
            ServiceResult with deletion result
        """
        try:
            try:
                report = ReporteGenerado.objects.get(id=report_id, usuario=user)
            except ReporteGenerado.DoesNotExist:
                return ServiceResult.not_found_error("Reporte no encontrado")
            
            # Create audit log before deleting
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
            
            # Delete report
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
        Gets report statistics for a user.
        
        Args:
            user: User
            filters: Additional filters
            
        Returns:
            ServiceResult with statistics
        """
        try:
            # Build base queryset
            queryset = ReporteGenerado.objects.filter(usuario=user)
            
            # Apply filters
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Calculate statistics
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
    
    def _get_report_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets a summary of report content.
        
        Args:
            content: Report content
            
        Returns:
            Dictionary with summary
        """
        if 'resumen' in content:
            return content['resumen']
        elif 'resumen_usuario' in content:
            return content['resumen_usuario']
        else:
            return {'total_items': len(content)}
    
    def _calculate_monthly_average(self, queryset) -> float:
        """
        Calculates monthly average of reports.
        
        Args:
            queryset: QuerySet of reports
            
        Returns:
            Monthly average
        """
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
        Gets the most used report type.
        
        Args:
            queryset: QuerySet of reports
            
        Returns:
            Most used report type
        """
        most_used = queryset.values('tipo_reporte').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        return most_used['tipo_reporte'] if most_used else 'N/A'

