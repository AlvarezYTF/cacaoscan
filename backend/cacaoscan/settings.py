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
load_dotenv(dotenv_path)
print(f"ðŸ“‚ .env cargado desde: {dotenv_path}")


# Suprimir warnings molestos
warnings.filterwarnings('ignore', message='pkg_resources is deprecated')
warnings.filterwarnings('ignore', message='The parameter.*is deprecated')
warnings.filterwarnings('ignore', message='Arguments other than a weight enum.*are deprecated')
warnings.filterwarnings('ignore', message='Using a target size.*that is different to the input size')
warnings.filterwarnings('ignore', category=UserWarning, module='drf_yasg')
warnings.filterwarnings('ignore', category=UserWarning, module='torchvision')
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

# Optimizar pkg_resources para evitar escaneo excesivo
# Esto reduce significativamente el uso de memoria con volúmenes montados
import pkg_resources
import os

# Limitar el escaneo de pkg_resources
pkg_resources_cache_dir = os.environ.get('PKG_RESOURCES_CACHE_DIR', '/tmp/pkg_resources_cache')
os.makedirs(pkg_resources_cache_dir, exist_ok=True)

# Configurar PYTHONPATH para evitar escaneo innecesario
if 'PYTHONPATH' not in os.environ:
    os.environ['PYTHONPATH'] = str(BASE_DIR)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with someone turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.9', '*', '10.7.53.137']

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.error_handler.StandardErrorMiddleware',  # Middleware de errores
    'api.middleware.TokenCleanupMiddleware',  # Limpieza automÃ¡tica de tokens
    'api.realtime_middleware.RealtimeAuditMiddleware',  # AuditorÃ­a en tiempo real
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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cacaoscan_db'),
        'USER': os.environ.get('DB_USER', 'jeferson'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'J3Fers0n272003@'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
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
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
    
    # S3 static files configuration (opcional, solo si quieres servir estáticos desde S3)
    # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # S3 media files configuration
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    # Configuración local para desarrollo
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

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
# Para desarrollo: permitir todas las conexiones desde cualquier IP
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Alternativo para otros dev servers
        "http://127.0.0.1:3000",
    ]

# ConfiguraciÃ³n adicional de CORS para desarrollo
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

# ConfiguraciÃ³n de Email con fallback TLS/SSL
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
# Credenciales Gmail con App Password
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ch4130949@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'scdtfcpicnqjmiyo')  # Nueva App Password sin espacios
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '30'))
# ConfiguraciÃ³n de fallback para SSL
EMAIL_USE_SSL_FALLBACK = os.environ.get('EMAIL_USE_SSL_FALLBACK', 'True').lower() == 'true'

# ConfiguraciÃ³n de SendGrid (alternativa)
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@cacaoscan.com')

# ConfiguraciÃ³n de emails del sistema
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

# ConfiguraciÃ³n de templates de email
EMAIL_TEMPLATES_DIR = BASE_DIR / 'api' / 'templates' / 'emails'

# ConfiguraciÃ³n de notificaciones por email
EMAIL_NOTIFICATIONS_ENABLED = os.environ.get('EMAIL_NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
EMAIL_NOTIFICATION_TYPES = [
    'welcome',           # Email de bienvenida
    'password_reset',    # Restablecimiento de contraseÃ±a
    'analysis_complete', # AnÃ¡lisis completado
    'report_ready',      # Reporte listo
    'training_complete', # Entrenamiento completado
    'defect_alert',      # Alerta de defectos
    'system_alert',      # Alertas del sistema
    'weekly_summary',    # Resumen semanal
]

# ConfiguraciÃ³n de cola de emails (para producciÃ³n)
EMAIL_QUEUE_ENABLED = os.environ.get('EMAIL_QUEUE_ENABLED', 'False').lower() == 'true'
EMAIL_BATCH_SIZE = int(os.environ.get('EMAIL_BATCH_SIZE', '50'))
EMAIL_RETRY_ATTEMPTS = int(os.environ.get('EMAIL_RETRY_ATTEMPTS', '3'))

# ConfiguraciÃ³n de JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Token de acceso vÃ¡lido por 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Token de refresh vÃ¡lido por 7 dÃ­as
    'ROTATE_REFRESH_TOKENS': True,                   # Rotar tokens de refresh
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklistear tokens antiguos
    'UPDATE_LAST_LOGIN': True,                       # Actualizar Ãºltimo login
    
    'ALGORITHM': 'HS256',                            # Algoritmo de firma
    'SIGNING_KEY': SECRET_KEY,                       # Clave de firma
    'VERIFYING_KEY': None,                           # Clave de verificaciÃ³n
    'AUDIENCE': None,                                # Audiencia
    'ISSUER': None,                                  # Emisor
    
    'AUTH_HEADER_TYPES': ('Bearer',),               # Tipo de header de autorizaciÃ³n
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

# ConfiguraciÃ³n de Django Channels
ASGI_APPLICATION = 'cacaoscan.asgi.application'

# ConfiguraciÃ³n de Channels
# Para desarrollo sin Redis, usa InMemoryChannelLayer
# Para producciÃ³n, usa Redis: 'channels_redis.core.RedisChannelLayer'
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

# ConfiguraciÃ³n de WebSockets
WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL', 'ws://localhost:8000/ws/')
WEBSOCKET_HEARTBEAT_INTERVAL = int(os.environ.get('WEBSOCKET_HEARTBEAT_INTERVAL', '30'))
WEBSOCKET_MAX_CONNECTIONS = int(os.environ.get('WEBSOCKET_MAX_CONNECTIONS', '1000'))

# ConfiguraciÃ³n de notificaciones en tiempo real
REALTIME_NOTIFICATIONS_ENABLED = os.environ.get('REALTIME_NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
NOTIFICATION_BROADCAST_ENABLED = os.environ.get('NOTIFICATION_BROADCAST_ENABLED', 'True').lower() == 'true'
NOTIFICATION_PERSISTENCE_ENABLED = os.environ.get('NOTIFICATION_PERSISTENCE_ENABLED', 'True').lower() == 'true'

# Configuración de Celery
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
# Configuración para evitar warnings de deprecación en Celery 6.0+
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10