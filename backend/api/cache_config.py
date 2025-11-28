"""
Configuración de caché y Redis para optimización de performance.
"""
import os

# Redis cache backend constants
REDIS_CACHE_BACKEND = 'django_redis.cache.RedisCache'
REDIS_CLIENT_CLASS = 'django_redis.client.DefaultClient'

# Configuración de Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Get DEBUG from environment (defaults to False for production)
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': REDIS_CACHE_BACKEND,
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': REDIS_CLIENT_CLASS,
            'PASSWORD': REDIS_PASSWORD,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'cacaoscan',
        'TIMEOUT': 300,  # 5 minutos por defecto
        'VERSION': 1,
    },
    'sessions': {
        'BACKEND': REDIS_CACHE_BACKEND,
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': REDIS_CLIENT_CLASS,
            'PASSWORD': REDIS_PASSWORD,
        },
        'KEY_PREFIX': 'cacaoscan_sessions',
        'TIMEOUT': 86400,  # 24 horas
    },
    'api_cache': {
        'BACKEND': REDIS_CACHE_BACKEND,
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/2',
        'OPTIONS': {
            'CLIENT_CLASS': REDIS_CLIENT_CLASS,
            'PASSWORD': REDIS_PASSWORD,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'cacaoscan_api',
        'TIMEOUT': 600,  # 10 minutos
    }
}

# Configuración de sesiones con Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Configuración de caché para APIs específicas
API_CACHE_TIMEOUTS = {
    'user_stats': 600,  # 10 minutos
    'system_stats': 300,  # 5 minutos
    'finca_list': 300,  # 5 minutos
    'lote_list': 300,  # 5 minutos
    'notification_list': 60,  # 1 minuto
    'activity_logs': 300,  # 5 minutos
    'reports_list': 300,  # 5 minutos
}

# Configuración de caché para consultas pesadas
HEAVY_QUERY_CACHE_TIMEOUTS = {
    'dashboard_stats': 300,  # 5 minutos
    'user_activity_summary': 600,  # 10 minutos
    'finca_analytics': 900,  # 15 minutos
    'report_generation': 1800,  # 30 minutos
}

# Configuración de invalidación de caché
CACHE_INVALIDATION_PATTERNS = {
    'user_related': [
        'user_stats_{user_id}_*',
        'user_activity_{user_id}_*',
        'user_notifications_{user_id}_*',
        'user_reports_{user_id}_*',
    ],
    'finca_related': [
        'finca_list_*',
        'finca_stats_{finca_id}_*',
        'finca_analytics_{finca_id}_*',
    ],
    'lote_related': [
        'lote_list_*',
        'lote_stats_{lote_id}_*',
    ],
    'system_wide': [
        'system_stats_*',
        'dashboard_stats_*',
    ]
}

# Configuración de monitoreo de performance
PERFORMANCE_MONITORING = {
    'slow_query_threshold': 1.0,  # segundos
    'cache_hit_ratio_threshold': 0.8,  # 80%
    'enable_query_logging': not DEBUG,
    'enable_cache_logging': DEBUG,
}

# Configuración de compresión
CACHE_COMPRESSION = {
    'enabled': True,
    'algorithm': 'zlib',
    'level': 6,  # Balance entre compresión y velocidad
}

# Configuración de conexión Redis
REDIS_CONNECTION_CONFIG = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
    'password': REDIS_PASSWORD,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True,
    'health_check_interval': 30,
}

# Configuración de cluster Redis (para producción)
REDIS_CLUSTER_CONFIG = {
    'enabled': os.getenv('REDIS_CLUSTER_ENABLED', 'False').lower() == 'true',
    'startup_nodes': [
        {'host': REDIS_HOST, 'port': REDIS_PORT}
    ],
    'skip_full_coverage_check': True,
    'health_check_interval': 30,
}

# Configuración de caché para desarrollo
# Esta lógica se manejará en settings.py para evitar dependencias circulares
# El DEBUG check se hace usando variables de entorno aquí


