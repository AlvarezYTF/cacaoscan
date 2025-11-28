"""
Django settings for cacaoscan project.
"""

import os
import warnings
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, ".env")

# Crear .env si no existe con valores por defecto (solo en desarrollo)
if not os.path.exists(dotenv_path):
    # Solo generar .env en modo desarrollo para evitar configuraciones inseguras en producción
    is_development = os.environ.get('APP_ENV', '').lower() != 'production'
    
    if is_development:
        # Generar SECRET_KEY segura usando Django
        from django.core.management.utils import get_random_secret_key
        secret_key = get_random_secret_key()
        
        default_env_content = f"""# ===========================
# Configuración de Base de Datos PostgreSQL
# ===========================
DB_NAME=cacaoscan_db
DB_USER=cristian
DB_PASSWORD=123456
DB_HOST=localhost
DB_PORT=5432

# ===========================
# Configuración de Django
# ===========================
# IMPORTANTE: Esta SECRET_KEY fue generada automáticamente. 
# En producción, genera tu propia clave secreta segura.
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ===========================
# Configuración de API
# ===========================
VITE_API_BASE_URL=http://localhost:8000/api/v1

# ===========================
# Configuración de Email (Opcional)
# ===========================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# ===========================
# Configuración de CORS (Desarrollo)
# ===========================
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
AUTO_TRAIN_ENABLED=0
"""
        with open(dotenv_path, 'w', encoding='utf-8') as f:
            f.write(default_env_content)
        print(f"✅ Archivo .env creado automáticamente en: {dotenv_path}")
    else:
        # En producción, requerir que el .env exista y esté configurado correctamente
        raise ValueError(
            "Archivo .env no encontrado y APP_ENV=production. "
            "Crea el archivo .env con las variables necesarias antes de iniciar la aplicación."
        )

# Load .env file with explicit UTF-8 encoding to avoid decode errors
# Try multiple encodings if UTF-8 fails
try:
    load_dotenv(dotenv_path, encoding='utf-8')
except Exception:
    try:
        # Try without BOM
        with open(dotenv_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        # Write back with UTF-8 encoding
        with open(dotenv_path, 'w', encoding='utf-8') as f:
            f.write(content)
        load_dotenv(dotenv_path, encoding='utf-8')
    except Exception as e:
        print("⚠️ Warning: Error loading .env file:", e)
        print("Continuing with environment variables...")
        print("💡 Tip: Recreate .env file with UTF-8 encoding if issues persist")


# Suprimir warnings molestos
warnings.filterwarnings('ignore', message='The parameter.*is deprecated')
warnings.filterwarnings('ignore', message='Arguments other than a weight enum.*are deprecated')
warnings.filterwarnings('ignore', message='Using a target size.*that is different to the input size')
warnings.filterwarnings('ignore', category=UserWarning, module='drf_yasg')
warnings.filterwarnings('ignore', category=UserWarning, module='torchvision')
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

# Configurar PYTHONPATH para evitar escaneo innecesario
if 'PYTHONPATH' not in os.environ:
    os.environ['PYTHONPATH'] = str(BASE_DIR)

# Migrado de pkg_resources (deprecated) a importlib.metadata (Python 3.12+)
# pkg_resources ya no se usa, eliminado para evitar warnings de deprecación

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required. "
        "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# SECURITY WARNING: don't run with debug turned on in production!
# Force DEBUG=False in production environments
APP_ENV = os.environ.get('APP_ENV', '').lower()
if APP_ENV == 'production':
    DEBUG = False
else:
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS configuration
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [
        host.strip()
        for host in allowed_hosts_env.split(',')
        if host.strip()
    ]
else:
    # Development defaults only if DEBUG is True
    if DEBUG:
        ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    else:
        ALLOWED_HOSTS = []

# Validate ALLOWED_HOSTS in production
if not DEBUG and not ALLOWED_HOSTS:
    raise ValueError(
        "ALLOWED_HOSTS must be configured in production. "
        "Set ALLOWED_HOSTS environment variable with comma-separated host names."
    )

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'channels',
    'storages',  # Django storages para AWS S3
    # Core apps (orden importante)
    'core',
    
    # Auth apps
    'auth_app',
    'users.apps.UsersConfig',
    'personas',
    
    # Feature apps
    'fincas_app',
    'images_app',
    'catalogos',
    'notifications',
    'audit',
    'training',
    
    # Existing apps
    'api',  # API principal (ahora sin conflictos de modelos)
    'reports',
    'legal',  # App para documentos legales
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.error_handler.StandardErrorMiddleware',  # Middleware de errores
    'api.middleware.TokenCleanupMiddleware',  # Limpieza automática de tokens
    'api.realtime_middleware.RealtimeAuditMiddleware',  # Auditoría en tiempo real
    'api.realtime_middleware.RealtimeLoginMiddleware',  # Registro de logins
]

ROOT_URLCONF = 'cacaoscan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cacaoscan.wsgi.application'

# Database
# Helper function to safely decode environment variables as UTF-8 strings
def safe_env_get(key: str, default: str = '') -> str:
    """Safely get and decode environment variable as UTF-8 string."""
    value = os.environ.get(key, default)
    if value is None:
        return default
    if isinstance(value, bytes):
        # Try UTF-8 first, fallback to latin-1 if that fails
        try:
            value = value.decode('utf-8', errors='strict')
        except (UnicodeDecodeError, AttributeError):
            try:
                value = value.decode('latin-1', errors='replace')
            except Exception:
                value = value.decode('utf-8', errors='replace')
    elif not isinstance(value, str):
        value = str(value)
    # Ensure the value is a valid UTF-8 string
    if isinstance(value, str):
        # Re-encode and decode to ensure valid UTF-8
        try:
            value = value.encode('utf-8', errors='strict').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            # If strict encoding fails, use replace to handle problematic characters
            value = value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    return value

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': safe_env_get('DB_NAME', 'cacaoscan_db'),
        'USER': safe_env_get('DB_USER', 'cacaoscan'),
        'PASSWORD': safe_env_get('DB_PASSWORD', ''),
        'HOST': safe_env_get('DB_HOST', 'localhost'),
        'PORT': safe_env_get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Reuse database connections for 10 minutes
        'OPTIONS': {
            'client_encoding': 'UTF8',
            'connect_timeout': 10,
        },
    }
}

# Cache configuration
# Try to import from cache_config, fallback to default if not available
# Use importlib to avoid executing api/__init__.py which imports views
import importlib.util
import sys
try:
    # Import cache_config directly without triggering api/__init__.py
    cache_config_path = BASE_DIR / 'api' / 'cache_config.py'
    if cache_config_path.exists():
        spec = importlib.util.spec_from_file_location("cache_config", str(cache_config_path))
        cache_config = importlib.util.module_from_spec(spec)
        sys.modules["cache_config"] = cache_config
        spec.loader.exec_module(cache_config)
        CACHES = cache_config.CACHES
    else:
        raise ImportError("cache_config.py not found")
    
    # Override cache configuration for DEBUG mode after import to avoid circular dependency
    if DEBUG:
        CACHES['default'] = {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
        }
        CACHES['sessions'] = {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-sessions',
            'TIMEOUT': 86400,
        }
except (ImportError, AttributeError, FileNotFoundError) as e:
    # Default cache configuration (fallback)
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    if DEBUG:
        # Use in-memory cache for development
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
                'TIMEOUT': 300,
            },
            'api_cache': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'api-cache',
                'TIMEOUT': 600,
            }
        }
    else:
        # Use Redis for production
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'PASSWORD': REDIS_PASSWORD,
                    'CONNECTION_POOL_KWARGS': {
                        'max_connections': 50,
                        'retry_on_timeout': True,
                    },
                },
                'KEY_PREFIX': 'cacaoscan',
                'TIMEOUT': 300,
            },
            'api_cache': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/2',
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'PASSWORD': REDIS_PASSWORD,
                },
                'KEY_PREFIX': 'cacaoscan_api',
                'TIMEOUT': 600,
            }
        }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = Path(os.environ.get('DJANGO_STATIC_ROOT', BASE_DIR / 'staticfiles'))
# Usar storage sin manifest en producción si hay problemas, o con manifest si está disponible
# CompressedManifestStaticFilesStorage requiere que collectstatic se ejecute correctamente
if os.environ.get('USE_STATICFILES_MANIFEST', 'True').lower() == 'true':
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))

# AWS S3 Configuration
USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'

if USE_S3:
    # AWS S3 settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'cacaoscan-dataset')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # S3 static files configuration (opcional, solo si quieres servir estticos desde S3)
    # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # S3 media files configuration
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    # Configuración local para desarrollo / entornos sin S3
    MEDIA_URL = '/media/'
    MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS settings
# Never use CORS_ALLOW_ALL_ORIGINS in production - always use explicit CORS_ALLOWED_ORIGINS
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    # Validate that each origin has scheme (http:// or https://)
    valid_origins = []
    for origin in cors_origins.split(','):
        origin = origin.strip()
        if not origin:
            continue
        # Only accept origins with full scheme (http:// or https://)
        if origin.startswith('http://') or origin.startswith('https://'):
            # Validate that it has a valid domain (contains a dot or is localhost)
            if '.' in origin.replace('://', '').split('/')[0] or 'localhost' in origin:
                valid_origins.append(origin)
    
    if valid_origins:
        CORS_ALLOWED_ORIGINS = valid_origins
        CORS_ALLOW_ALL_ORIGINS = False
    else:
        # If no valid origins, default to empty list (no CORS allowed)
        CORS_ALLOW_ALL_ORIGINS = False
        CORS_ALLOWED_ORIGINS = []
else:
    # Default: no CORS allowed (empty list)
    # In development, explicitly set CORS_ALLOWED_ORIGINS in .env if needed
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = []

# Configuración adicional de CORS para desarrollo
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CORS: Permitir métodos HTTP necesarios
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    # HSTS settings (only in production)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'

# Logging de CORS para debugging (solo en desarrollo)
if DEBUG:
    import logging
    cors_logger = logging.getLogger('corsheaders')
    cors_logger.setLevel(logging.DEBUG)

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024  # 8MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024  # 8MB

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'method',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'SHOW_COMMON_EXTENSIONS': True,
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'cacaoscan.api': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cacaoscan.ml': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Suprimir warnings de pkg_resources
        'pkg_resources': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Suprimir warnings de drf_yasg
        'drf_yasg': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Suprimir warnings de torchvision
        'torchvision': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Suprimir warnings de torch
        'torch': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Configuración de Email con fallback TLS/SSL
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
# Credenciales Gmail con App Password
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '30'))
# Configuración de fallback para SSL
EMAIL_USE_SSL_FALLBACK = os.environ.get('EMAIL_USE_SSL_FALLBACK', 'True').lower() == 'true'

# Configuración de SendGrid (alternativa)
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@cacaoscan.com')

# Configuración de emails del sistema
# Usar el mismo email que el usuario autenticado en SMTP para evitar bloqueos de Gmail
# Gmail requiere que el remitente coincida con EMAIL_HOST_USER para entregar a otros correos
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL', 
    f"CacaoScan <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else 'CacaoScan <noreply@cacaoscan.com>'
)
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = os.environ.get('EMAIL_SUBJECT_PREFIX', '[CacaoScan] ')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
ADMINS = [
    ('Admin CacaoScan', os.environ.get('ADMIN_EMAIL', 'admin@cacaoscan.com')),
]
MANAGERS = ADMINS

# Configuración de templates de email
EMAIL_TEMPLATES_DIR = BASE_DIR / 'api' / 'templates' / 'emails'

# Configuración de notificaciones por email
EMAIL_NOTIFICATIONS_ENABLED = os.environ.get('EMAIL_NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
EMAIL_NOTIFICATION_TYPES = [
    'welcome',           # Email de bienvenida
    'password_reset',    # Restablecimiento de contraseña
    'analysis_complete', # Análisis completado
    'report_ready',      # Reporte listo
    'training_complete', # Entrenamiento completado
    'defect_alert',      # Alerta de defectos
    'system_alert',      # Alertas del sistema
    'weekly_summary',    # Resumen semanal
]

# Configuración de cola de emails (para producción)
EMAIL_QUEUE_ENABLED = os.environ.get('EMAIL_QUEUE_ENABLED', 'False').lower() == 'true'
EMAIL_BATCH_SIZE = int(os.environ.get('EMAIL_BATCH_SIZE', '50'))
EMAIL_RETRY_ATTEMPTS = int(os.environ.get('EMAIL_RETRY_ATTEMPTS', '3'))

# Configuración de JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Token de acceso válido por 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Token de refresh válido por 7 días
    'ROTATE_REFRESH_TOKENS': True,                   # Rotar tokens de refresh
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklistear tokens antiguos
    'UPDATE_LAST_LOGIN': True,                       # Actualizar último login
    
    'ALGORITHM': 'HS256',                            # Algoritmo de firma
    'SIGNING_KEY': SECRET_KEY,                       # Clave de firma
    'VERIFYING_KEY': None,                           # Clave de verificación
    'AUDIENCE': None,                                # Audiencia
    'ISSUER': None,                                  # Emisor
    
    'AUTH_HEADER_TYPES': ('Bearer',),               # Tipo de header de autorización
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',        # Nombre del header
    'USER_ID_FIELD': 'id',                           # Campo de ID de usuario
    'USER_ID_CLAIM': 'user_id',                     # Claim de ID de usuario
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',                              # Claim de JTI
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Configuración de Django Channels
ASGI_APPLICATION = 'cacaoscan.asgi.application'

# Configuración de Channels
# Para desarrollo sin Redis, usa InMemoryChannelLayer
# Para producción, usa Redis: 'channels_redis.core.RedisChannelLayer'
USE_REDIS = os.environ.get('USE_REDIS', 'False').lower() == 'true'

if USE_REDIS:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('127.0.0.1', 6379)],
                'capacity': 1500,
                'expiry': 60,
            },
        },
    }
else:
    # Channel layer in-memory para desarrollo sin Redis
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Configuración de WebSockets
WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL', 'ws://localhost:8000/ws/')
WEBSOCKET_HEARTBEAT_INTERVAL = int(os.environ.get('WEBSOCKET_HEARTBEAT_INTERVAL', '30'))
WEBSOCKET_MAX_CONNECTIONS = int(os.environ.get('WEBSOCKET_MAX_CONNECTIONS', '1000'))

# Configuración de notificaciones en tiempo real
REALTIME_NOTIFICATIONS_ENABLED = os.environ.get('REALTIME_NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
NOTIFICATION_BROADCAST_ENABLED = os.environ.get('NOTIFICATION_BROADCAST_ENABLED', 'True').lower() == 'true'
NOTIFICATION_PERSISTENCE_ENABLED = os.environ.get('NOTIFICATION_PERSISTENCE_ENABLED', 'True').lower() == 'true'

# Configuracin de Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1
# Configuracin para evitar warnings de deprecacin en Celery 6.0+
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10