"""
Shared statistics and filtering utilities for report generators.
Contains common functions for calculating statistics and applying filters.
"""
import logging
from django.utils import timezone
from django.db.models import Count, Avg
from api.utils.model_imports import get_models_safely

logger = logging.getLogger("cacaoscan.services.report.stats")

# Import models safely
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


def apply_prediction_filters(queryset, filtros):
    """
    Apply filters to CacaoPrediction queryset.
    
    Args:
        queryset: CacaoPrediction queryset
        filtros: Dictionary with filter parameters
        
    Returns:
        Filtered queryset
    """
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


def get_quality_stats(queryset):
    """
    Get quality statistics from CacaoPrediction queryset.
    
    Args:
        queryset: CacaoPrediction queryset
        
    Returns:
        Dictionary with quality statistics
    """
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
            'alto': round(float(avg_dimensions.get('avg_alto') or 0), 2),
            'ancho': round(float(avg_dimensions.get('avg_ancho') or 0), 2),
            'grosor': round(float(avg_dimensions.get('avg_grosor') or 0), 2),
        },
        'avg_weight': round(float(avg_weight), 2)
    }


def get_lotes_stats(finca):
    """
    Get lot statistics for a farm.
    
    Args:
        finca: Finca instance
        
    Returns:
        Dictionary with lot statistics
    """
    lotes = finca.lotes.all()
    
    return {
        'total_lotes': lotes.count(),
        'lotes_activos': lotes.filter(activo=True).count(),
        'total_area': sum(float(lote.area_hectareas) for lote in lotes),
        'variedades': list(lotes.values('variedad').distinct()),
        'estados': dict(lotes.values('estado').annotate(count=Count('id')).values_list('estado', 'count')),
    }


def get_activity_stats(filtros):
    """
    Get activity statistics.
    
    Args:
        filtros: Dictionary with filter parameters
        
    Returns:
        Dictionary with activity statistics
    """
    queryset = ActivityLog.objects.all()
    
    if filtros:
        if filtros.get('fecha_desde'):
            queryset = queryset.filter(timestamp__date__gte=filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            queryset = queryset.filter(timestamp__date__lte=filtros['fecha_hasta'])
    
    return {
        'total_activities': queryset.count(),
        'activities_today': queryset.filter(timestamp__date=timezone.now().date()).count(),
        'activities_by_action': dict(queryset.values('action').annotate(count=Count('id')).values_list('action', 'count')),
        'top_users': list(queryset.values('user__username').annotate(count=Count('id')).order_by('-count')[:10]),
    }


def get_login_stats(filtros):
    """
    Get login statistics.
    
    Args:
        filtros: Dictionary with filter parameters
        
    Returns:
        Dictionary with login statistics
    """
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

