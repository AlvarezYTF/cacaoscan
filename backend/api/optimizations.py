"""
Optimizaciones de performance para consultas de base de datos.
"""
from django.db.models import Prefetch, Q, Count, Avg, Sum, Max, Min
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Clase para optimizar consultas de base de datos."""
    
    @staticmethod
    def optimize_cacao_images_query(queryset):
        """Optimiza consultas de CacaoImage con relaciones."""
        return queryset.select_related(
            'usuario',
            'lote',
            'lote__finca'
        ).prefetch_related(
            'predicciones',
            'predicciones__modelo'
        )
    
    @staticmethod
    def optimize_fincas_query(queryset):
        """Optimiza consultas de Finca con relaciones."""
        return queryset.select_related(
            'propietario'
        ).prefetch_related(
            Prefetch(
                'lotes',
                queryset=Lote.objects.select_related('finca').prefetch_related('imagenes')
            )
        )
    
    @staticmethod
    def optimize_lotes_query(queryset):
        """Optimiza consultas de Lote con relaciones."""
        return queryset.select_related(
            'finca',
            'finca__propietario'
        ).prefetch_related(
            'imagenes',
            'imagenes__predicciones'
        )
    
    @staticmethod
    def optimize_notifications_query(queryset):
        """Optimiza consultas de Notification con relaciones."""
        return queryset.select_related(
            'usuario'
        )
    
    @staticmethod
    def optimize_activity_logs_query(queryset):
        """Optimiza consultas de ActivityLog con relaciones."""
        return queryset.select_related(
            'usuario'
        )
    
    @staticmethod
    def optimize_reports_query(queryset):
        """Optimiza consultas de ReporteGenerado con relaciones."""
        return queryset.select_related(
            'usuario'
        )

class CacheManager:
    """Gestor de caché para optimizar consultas frecuentes."""
    
    CACHE_TIMEOUT = 300  # 5 minutos por defecto
    
    @classmethod
    def get_or_set(cls, key, callable_func, timeout=None):
        """Obtiene del caché o ejecuta función y guarda resultado."""
        timeout = timeout or cls.CACHE_TIMEOUT
        
        # Intentar obtener del caché
        result = cache.get(key)
        if result is not None:
            logger.debug(f"Cache hit for key: {key}")
            return result
        
        # Ejecutar función y guardar en caché
        logger.debug(f"Cache miss for key: {key}")
        result = callable_func()
        cache.set(key, result, timeout)
        return result
    
    @classmethod
    def invalidate_pattern(cls, pattern):
        """Invalida todas las claves que coincidan con el patrón."""
        try:
            # En producción usar Redis con SCAN
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
            else:
                # Fallback para desarrollo
                logger.warning("Pattern-based cache invalidation not available")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
    
    @classmethod
    def invalidate_user_cache(cls, user_id):
        """Invalida caché relacionado con un usuario específico."""
        patterns = [
            f"user_stats_{user_id}_*",
            f"user_activity_{user_id}_*",
            f"user_notifications_{user_id}_*",
            f"user_reports_{user_id}_*"
        ]
        
        for pattern in patterns:
            cls.invalidate_pattern(pattern)

class PaginationOptimizer:
    """Optimizador para paginación eficiente."""
    
    @staticmethod
    def optimize_pagination(queryset, page, page_size, max_page_size=100):
        """Optimiza la paginación con límites y validaciones."""
        # Limitar tamaño de página
        page_size = min(page_size, max_page_size)
        
        # Calcular offset
        offset = (page - 1) * page_size
        
        # Usar slicing para paginación eficiente
        return queryset[offset:offset + page_size]
    
    @staticmethod
    def get_pagination_info(queryset, page, page_size):
        """Obtiene información de paginación optimizada."""
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }

class DatabaseOptimizer:
    """Optimizador general de base de datos."""
    
    @staticmethod
    def add_database_indexes():
        """Sugiere índices para optimizar consultas."""
        indexes = [
            # CacaoImage indexes
            ('api_cacaoimage', 'usuario_id'),
            ('api_cacaoimage', 'lote_id'),
            ('api_cacaoimage', 'fecha_subida'),
            ('api_cacaoimage', 'estado'),
            
            # Finca indexes
            ('api_finca', 'propietario_id'),
            ('api_finca', 'ubicacion'),
            ('api_finca', 'fecha_registro'),
            
            # Lote indexes
            ('api_lote', 'finca_id'),
            ('api_lote', 'variedad'),
            ('api_lote', 'fecha_siembra'),
            
            # Notification indexes
            ('api_notification', 'usuario_id'),
            ('api_notification', 'tipo'),
            ('api_notification', 'leida'),
            ('api_notification', 'fecha_creacion'),
            
            # ActivityLog indexes
            ('api_activitylog', 'usuario_id'),
            ('api_activitylog', 'accion'),
            ('api_activitylog', 'fecha_accion'),
            
            # ReporteGenerado indexes
            ('api_reportegenerado', 'usuario_id'),
            ('api_reportegenerado', 'tipo_reporte'),
            ('api_reportegenerado', 'estado'),
            ('api_reportegenerado', 'fecha_solicitud'),
        ]
        
        return indexes
    
    @staticmethod
    def optimize_queryset_for_list(queryset, model_name):
        """Optimiza queryset para listados según el modelo."""
        optimizers = {
            'CacaoImage': QueryOptimizer.optimize_cacao_images_query,
            'Finca': QueryOptimizer.optimize_fincas_query,
            'Lote': QueryOptimizer.optimize_lotes_query,
            'Notification': QueryOptimizer.optimize_notifications_query,
            'ActivityLog': QueryOptimizer.optimize_activity_logs_query,
            'ReporteGenerado': QueryOptimizer.optimize_reports_query,
        }
        
        optimizer = optimizers.get(model_name)
        if optimizer:
            return optimizer(queryset)
        
        return queryset
    
    @staticmethod
    def get_optimized_stats_query(model_class, user_id=None):
        """Obtiene consulta optimizada para estadísticas."""
        base_query = model_class.objects.all()
        
        if user_id:
            base_query = base_query.filter(usuario_id=user_id)
        
        return base_query.aggregate(
            total=Count('id'),
            # Agregar más agregaciones según el modelo
        )

class PerformanceMonitor:
    """Monitor de performance para consultas."""
    
    @staticmethod
    def log_slow_query(query, execution_time, threshold=1.0):
        """Registra consultas lentas."""
        if execution_time > threshold:
            logger.warning(f"Slow query detected: {execution_time:.2f}s - {query}")
    
    @staticmethod
    def get_query_stats():
        """Obtiene estadísticas de consultas."""
        # En producción, esto se conectaría con herramientas de monitoreo
        return {
            'total_queries': 0,
            'slow_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

# Funciones de utilidad para uso en vistas
def get_cached_user_stats(user_id):
    """Obtiene estadísticas de usuario desde caché."""
    cache_key = f"user_stats_{user_id}_{timezone.now().date()}"
    
    def calculate_stats():
        from .models import CacaoImage, Finca, Lote, Notification, ActivityLog
        
        return {
            'total_images': CacaoImage.objects.filter(usuario_id=user_id).count(),
            'total_fincas': Finca.objects.filter(propietario_id=user_id).count(),
            'total_lotes': Lote.objects.filter(finca__propietario_id=user_id).count(),
            'unread_notifications': Notification.objects.filter(
                usuario_id=user_id, leida=False
            ).count(),
            'recent_activity': ActivityLog.objects.filter(
                usuario_id=user_id
            ).order_by('-fecha_accion')[:5].values(
                'accion', 'fecha_accion', 'detalles'
            )
        }
    
    return CacheManager.get_or_set(cache_key, calculate_stats, timeout=600)

def get_cached_system_stats():
    """Obtiene estadísticas del sistema desde caché."""
    cache_key = f"system_stats_{timezone.now().date()}"
    
    def calculate_system_stats():
        from .models import CacaoImage, Finca, Lote, User, Notification
        
        return {
            'total_users': User.objects.count(),
            'total_images': CacaoImage.objects.count(),
            'total_fincas': Finca.objects.count(),
            'total_lotes': Lote.objects.count(),
            'pending_notifications': Notification.objects.filter(leida=False).count(),
            'images_today': CacaoImage.objects.filter(
                fecha_subida__date=timezone.now().date()
            ).count(),
        }
    
    return CacheManager.get_or_set(cache_key, calculate_system_stats, timeout=300)

def invalidate_user_related_cache(user_id):
    """Invalida caché relacionado con un usuario."""
    CacheManager.invalidate_user_cache(user_id)


