"""
Statistics service for finca management.
Handles finca statistics calculation.
"""
import logging
from typing import Dict, Any
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'Finca': 'fincas_app.models.Finca'
})
Finca = models['Finca']

logger = logging.getLogger("cacaoscan.services.fincas.stats")


class FincaStatsService(BaseService):
    """
    Service for handling finca statistics.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_finca_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets finca statistics for a user.
        
        Args:
            user: User
            filters: Additional filters
            
        Returns:
            ServiceResult with statistics
        """
        try:
            # Build base queryset (optimized)
            if user.is_superuser or user.is_staff:
                queryset = Finca.objects.all().select_related('agricultor')
            else:
                queryset = Finca.objects.filter(agricultor=user).select_related('agricultor')
            
            # Apply filters
            if filters:
                if 'departamento' in filters:
                    queryset = queryset.filter(departamento=filters['departamento'])
                if 'activa' in filters:
                    queryset = queryset.filter(activa=filters['activa'])
            
            # Calculate statistics
            from decimal import Decimal
            total_hectareas = queryset.aggregate(total=Sum('hectareas'))['total'] or Decimal('0')
            
            stats = {
                'total_fincas': queryset.count(),
                'fincas_activas': queryset.filter(activa=True).count(),
                'fincas_inactivas': queryset.filter(activa=False).count(),
                'total_hectareas': total_hectareas,
                'total_area': total_hectareas,  # Alias for backward compatibility
                'promedio_hectareas': queryset.aggregate(avg=Avg('hectareas'))['avg'] or 0,
                'departamentos': dict(queryset.values('departamento').annotate(count=Count('id')).values_list('departamento', 'count')),
                'municipios': dict(queryset.values('municipio').annotate(count=Count('id')).values_list('municipio', 'count')),
                'recent_fincas': queryset.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(),
                'hectareas_distribution': {
                    'small': queryset.filter(hectareas__lt=5).count(),  # < 5 ha
                    'medium': queryset.filter(hectareas__gte=5, hectareas__lt=20).count(),  # 5-20 ha
                    'large': queryset.filter(hectareas__gte=20).count()  # > 20 ha
                }
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

