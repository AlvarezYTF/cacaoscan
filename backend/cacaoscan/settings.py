# -*- coding: utf-8 -*-
"""
Django settings for cacaoscan project.
"""

import os
import sys
import warnings
from typing import Optional
from pathlib import Path

# Force UTF-8 encoding for all operations
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "UTF-8"
os.environ["PGCLIENTENCODING"] = "UTF8"

# Django 5.2 eliminó SecurityWarning, así que creamos uno propio
class SecurityWarning(UserWarning):
    """Custom Security Warning compatible with Django 5.x"""
    pass


from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import timedelta

# SecurityWarning fue agregado en Python 3.13
# Para compatibilidad con Python 3.12, crear una clase dummy si no existe
try:
    from warnings import SecurityWarning
except ImportError:
    # Python < 3.13: crear SecurityWarning como subclase de Warning
    class SecurityWarning(Warning):
        """Advertencia de seguridad (compatible con Python 3.12)."""
        pass

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, ".env")
# Si .env no existe, intentar con 'env' (sin punto) como fallback
if not os.path.exists(dotenv_path):
    env_path_alt = os.path.join(BASE_DIR, "env")
    if os.path.exists(env_path_alt):
        dotenv_path = env_path_alt

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
# IMPORTANTE: Cambia estas credenciales por valores seguros
DB_NAME=cacaoscan_db
DB_USER=cacaoscan_user
DB_PASSWORD=CHANGE_THIS_PASSWORD_IN_PRODUCTION
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
EMAIL_HOST_PASSWORD=CHANGE_THIS_EMAIL_PASSWORD

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

# Load .env file - robust UTF-8 handling, remove BOM and invalid bytes
if os.path.exists(dotenv_path):
    try:
        # Read as bytes
        with open(dotenv_path, 'rb') as f:
            raw_content = f.read()
        
        # Remove UTF-8 BOM (0xEF, 0xBB, 0xBF) if present
        if raw_content.startswith(b'\xef\xbb\xbf'):
            raw_content = raw_content[3:]
        
        # Remove problematic bytes that cause UnicodeDecodeError
        # 0xab = « (comillas angulares), 0xbb = », 0xf3, BOM, etc.
        problematic_bytes = [
            b'\xab',  # «
            b'\xbb',  # »
            b'\xf3',  # ó (en algunos encodings)
            b'\xef',  # BOM part 1
            b'\xbf',  # BOM part 3
            b'\x00',  # Null byte
        ]
        for pb in problematic_bytes:
            raw_content = raw_content.replace(pb, b'')
        
        # Decode with UTF-8, fallback to latin-1
        try:
            content = raw_content.decode('utf-8', errors='replace')
        except Exception:
            # If UTF-8 fails, try latin-1 with replacement
            try:
                content = raw_content.decode('latin-1', errors='replace')
            except Exception:
                # Last resort: decode as ASCII
                content = raw_content.decode('ascii', errors='ignore')
        
        # Load environment variables from content
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                # Clean value: remove quotes, invalid chars, BOM, and problematic bytes
                value = value.strip().strip('"\'').rstrip('\r\n')
                # Remove any remaining problematic characters
                problematic_chars = ['\ufeff', '\xf3', '\x00', '\xab', '\xbb', '\xad']
                for char in problematic_chars:
                    value = value.replace(char, '')
                # Remove non-printable ASCII control characters (except space, tab, newline, carriage return)
                value = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
                # Final UTF-8 validation
                try:
                    value.encode('utf-8', errors='strict')
                except UnicodeEncodeError:
                    # Force clean encoding
                    value = value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception as e:
        # Fallback: use load_dotenv
        try:
            load_dotenv(dotenv_path, override=False)
        except Exception:
            pass


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

# Database configuration - simple and clean
def _decode_bytes_to_string(value: bytes) -> str:
    """Decode bytes to string with multiple fallback strategies."""
    try:
        return value.decode('utf-8', errors='replace')
    except Exception:
        try:
            return value.decode('latin-1', errors='replace')
        except Exception:
            return value.decode('utf-8', errors='ignore')

def _normalize_to_string(value) -> str:
    """Normalize value to string, handling bytes and other types."""
    if value is None:
        return ""
    
    # Si es bytes, decodificar primero
    if isinstance(value, bytes):
        return _decode_bytes_to_string(value)
    
    # Si no es string, convertir
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception:
            return ""
    
    # Si el string contiene bytes problemáticos, limpiarlos
    try:
        # Intentar codificar/decodificar para detectar problemas
        value.encode('utf-8', errors='strict')
    except UnicodeEncodeError:
        # Si hay problemas, limpiar
        try:
            # Convertir a bytes y decodificar con replace
            value = value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            # Último recurso: ASCII
            value = value.encode('ascii', errors='ignore').decode('ascii')
    
    return value

def _remove_bom_and_problematic_bytes(value: str) -> str:
    """Remove BOM and problematic bytes from string."""
    if value.startswith('\ufeff'):
        value = value[1:]
    
    try:
        # Primero intentar decodificar si viene como bytes
        if isinstance(value, bytes):
            # Intentar decodificar con diferentes encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    value = value.decode(encoding, errors='replace')
                    break
                except (UnicodeDecodeError, AttributeError):
                    continue
            else:
                # Si todos fallan, usar replace para ignorar bytes inválidos
                value = value.decode('utf-8', errors='replace')
        
        # Convertir a bytes y limpiar bytes problemáticos
        value_bytes = value.encode('utf-8', errors='replace')
        # Remover bytes problemáticos comunes: 0xab («), 0xbb (»), 0xf3, BOM, etc.
        problematic_bytes = [b'\xab', b'\xbb', b'\xf3', b'\xef', b'\xbb', b'\xbf', b'\x00']
        for pb in problematic_bytes:
            value_bytes = value_bytes.replace(pb, b'')
        
        return value_bytes.decode('utf-8', errors='replace')
    except Exception:
        try:
            # Fallback: convertir a ASCII eliminando caracteres no ASCII
            return value.encode('ascii', errors='ignore').decode('ascii')
        except Exception:
            return ""

def _remove_invalid_chars(value: str) -> str:
    """Remove invalid characters from string."""
    # Caracteres inválidos comunes (incluyendo 0xab y 0xbb)
    invalid_chars = ['\x00', '\xef', '\xbb', '\xbf', '\xab', '\xad']
    for char in invalid_chars:
        value = value.replace(char, '')
    return value

def _filter_valid_utf8_chars(value: str) -> str:
    """Filter out invalid UTF-8 characters, keeping only valid ones."""
    cleaned = []
    for char in value:
        ord_val = ord(char)
        if (32 <= ord_val <= 126) or char in '\t\n\r':
            cleaned.append(char)
        elif ord_val > 127:
            try:
                char.encode('utf-8', errors='strict')
                cleaned.append(char)
            except UnicodeEncodeError:
                pass
    return ''.join(cleaned)

def _finalize_utf8_encoding(value: str) -> str:
    """Final validation and encoding fix for UTF-8."""
    try:
        value.encode('utf-8', errors='strict')
        return value
    except UnicodeEncodeError:
        return value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')

def clean_value(value: str) -> str:
    """
    Clean database connection parameter value.
    Removes invalid bytes, BOM, and ensures UTF-8 safe encoding.
    """
    value = _normalize_to_string(value)
    value = _remove_bom_and_problematic_bytes(value)
    value = _remove_invalid_chars(value)
    value = _filter_valid_utf8_chars(value)
    return _finalize_utf8_encoding(value)

# Determinar si estamos en modo test (usado para configuración de logging)
IS_TESTING = (
    'test' in sys.argv or 
    'pytest' in sys.modules or 
    os.environ.get('DJANGO_TEST_MODE') == '1' or
    'pytest' in str(sys.modules.get('__main__', {})) or
    'PYTEST_CURRENT_TEST' in os.environ
)

# TESTING flag for apps to check if running in test mode
TESTING = IS_TESTING

# Database configuration - Force PostgreSQL for ALL environments including tests
# This ensures tests run in the same environment as production
# Clean all database values to ensure UTF-8 encoding
def _get_db_value(env_key: str, alt_key: str = None, default: str = "") -> str:
    """Get database value from environment with proper encoding handling."""
    value = None
    if alt_key:
        value = os.getenv(env_key) or os.getenv(alt_key)
    else:
        value = os.getenv(env_key)
    
    if not value:
        return clean_value(default) if default else ""
    
    # Asegurar que el valor sea string y esté limpio
    return clean_value(value)

_db_name = _get_db_value("POSTGRES_DB", "DB_NAME", "cacaoscan_db")
_db_user = _get_db_value("POSTGRES_USER", "DB_USER", "postgres")
_db_password = _get_db_value("POSTGRES_PASSWORD", "DB_PASSWORD", "postgres")
_db_host = _get_db_value("POSTGRES_HOST", "DB_HOST", "127.0.0.1")
_db_port = _get_db_value("POSTGRES_PORT", "DB_PORT", "5432")
_db_test_name = _get_db_value("POSTGRES_DB_TEST", None, "cacaoscan_db_test")

# Asegurar que todos los valores sean strings válidos UTF-8 antes de crear la configuración
# Convertir explícitamente a string y validar encoding
try:
    _db_name_str = str(_db_name) if _db_name else "cacaoscan_db"
    _db_user_str = str(_db_user) if _db_user else "postgres"
    _db_password_str = str(_db_password) if _db_password else "postgres"
    _db_host_str = str(_db_host) if _db_host else "127.0.0.1"
    _db_port_str = str(_db_port) if _db_port else "5432"
    _db_test_name_str = str(_db_test_name) if _db_test_name else "cacaoscan_db_test"
    
    # Validar y limpiar que todos los valores sean UTF-8 válidos
    # Remover caracteres problemáticos antes de validar
    def _clean_db_value(val: str) -> str:
        """Clean database value removing problematic characters."""
        if not val:
            return val
        # Remover caracteres problemáticos conocidos
        problematic = ['\xab', '\xbb', '\xf3', '\x00', '\xad', '\ufeff']
        for char in problematic:
            val = val.replace(char, '')
        # Validar y limpiar encoding
        try:
            val.encode('utf-8', errors='strict')
            return val
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Forzar limpieza
            return val.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    
    _db_name_str = _clean_db_value(_db_name_str)
    _db_user_str = _clean_db_value(_db_user_str)
    _db_password_str = _clean_db_value(_db_password_str)
    _db_host_str = _clean_db_value(_db_host_str)
    _db_port_str = _clean_db_value(_db_port_str)
    _db_test_name_str = _clean_db_value(_db_test_name_str)
    
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name_str,
            "USER": _db_user_str,
            "PASSWORD": _db_password_str,
            "HOST": _db_host_str,
            "PORT": _db_port_str,
            "CONN_MAX_AGE": 600,
            "OPTIONS": {
                "client_encoding": "UTF8",
                "connect_timeout": 10,
            },
            "TEST": {
                "NAME": _db_test_name_str,
            },
        }
    }
except Exception as e:
    # Fallback a valores por defecto si hay error
    import warnings
    warnings.warn(f"Error procesando configuración de base de datos: {e}. Usando valores por defecto.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "cacaoscan_db",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "127.0.0.1",
            "PORT": "5432",
            "CONN_MAX_AGE": 600,
            "OPTIONS": {
                "client_encoding": "UTF8",
                "connect_timeout": 10,
            },
            "TEST": {
                "NAME": "cacaoscan_db_test",
            },
        }
    }

# No psycopg2 patches needed - database parameters are already cleaned

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
    LOCMEM_CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
    if DEBUG:
        CACHES['default'] = {
            'BACKEND': LOCMEM_CACHE_BACKEND,
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
        }
        CACHES['sessions'] = {
            'BACKEND': LOCMEM_CACHE_BACKEND,
            'LOCATION': 'unique-sessions',
            'TIMEOUT': 86400,
        }
except (ImportError, AttributeError, FileNotFoundError) as e:
    # Default cache configuration (fallback)
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    LOCMEM_CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
    if DEBUG:
        # Use in-memory cache for development
        CACHES = {
            'default': {
                'BACKEND': LOCMEM_CACHE_BACKEND,
                'LOCATION': 'unique-snowflake',
                'TIMEOUT': 300,
            },
            'api_cache': {
                'BACKEND': LOCMEM_CACHE_BACKEND,
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
# Handle empty string from env file - treat as None to use default
_static_root_env = os.environ.get('DJANGO_STATIC_ROOT', '').strip()
STATIC_ROOT = Path(_static_root_env) if _static_root_env else (BASE_DIR / 'staticfiles')
# Usar storage sin manifest en producción si hay problemas, o con manifest si está disponible
# CompressedManifestStaticFilesStorage requiere que collectstatic se ejecute correctamente
if os.environ.get('USE_STATICFILES_MANIFEST', 'True').lower() == 'true':
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
# Handle empty string from env file - treat as None to use default
_media_root_env = os.environ.get('DJANGO_MEDIA_ROOT', '').strip()
MEDIA_ROOT = Path(_media_root_env) if _media_root_env else (BASE_DIR / 'media')

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
    # MEDIA_ROOT ya está definido arriba, no necesita redefinirse aquí
    # Solo asegurarse de que no se sobrescriba si ya está configurado

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
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

# CORS settings
# Never use CORS_ALLOW_ALL_ORIGINS in production - always use explicit CORS_ALLOWED_ORIGINS
# SECURITY: HTTP is insecure for sensitive data transmission (S5332)
# Only allow HTTP in development for localhost/127.0.0.1
# In production, enforce HTTPS for all origins

# Helper function to check if origin is localhost (safe for HTTP only in development)
def _is_localhost_origin(hostname: Optional[str]) -> bool:
    """Check if hostname is localhost or 127.0.0.1 (safe for HTTP only in development)."""
    if not hostname:
        return False
    host_lower = hostname.lower()
    return host_lower in {'localhost', '127.0.0.1'}

# Helper function to validate and filter CORS origins
def _validate_cors_origin(origin: str, is_debug: bool):
    """
    Validate CORS origin and enforce HTTPS security.
    
    Args:
        origin: CORS origin to validate
        is_debug: Whether running in DEBUG mode
        
    Returns:
        Tuple of (is_valid, reason) where is_valid indicates if origin should be allowed
    """
    origin = origin.strip()
    if not origin:
        return False, "Empty origin"
    
    parsed = urlparse(origin)
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname
    
    if scheme not in {'http', 'https'}:
        return False, "Origin must include scheme (http or https)"
    
    if not hostname:
        return False, "Origin must include a valid hostname"
    
    # SECURITY: S5332 - Using HTTP is insecure for sensitive data transmission
    if scheme == 'http':
        if not is_debug:
            return False, "HTTP is not allowed in production. Use HTTPS instead (S5332)."
        if not _is_localhost_origin(hostname):
            return False, "HTTP is only allowed for localhost/127.0.0.1 in development. Use HTTPS for other origins (S5332)."
        return True, "Valid HTTP origin for localhost in development"
    
    # HTTPS is always allowed
    return True, "Valid HTTPS origin"

cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    # Validate that each origin has scheme (http:// or https://)
    valid_origins = []
    for origin in cors_origins.split(','):
        origin = origin.strip()
        if not origin:
            continue
        
        is_valid, reason = _validate_cors_origin(origin, DEBUG)
        if is_valid:
            valid_origins.append(origin)
        else:
            # Log warning for rejected origins
            warnings.warn(
                f"CORS origin '{origin}' rejected: {reason}",
                SecurityWarning
            )
    
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

LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Logging configuration
# Crear directorio de logs si no existe (necesario para tests y desarrollo)
LOGS_DIR = BASE_DIR / 'logs'
try:
    LOGS_DIR.mkdir(exist_ok=True)
except OSError as e:
    # Si no se puede crear el directorio (permisos, etc.), usar solo console handler
    # OSError incluye PermissionError (subclase de OSError en Python 3)
    import warnings
    warnings.warn(f"No se pudo crear el directorio de logs: {e}. Usando solo console handler.")
    LOGS_DIR = None

# IS_TESTING ya está definido arriba para la configuración de DATABASES

# Configurar handlers según disponibilidad
handlers_config = {
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
}

# Solo agregar file handler si el directorio de logs está disponible y NO estamos en modo test
# En modo test, usar solo console para evitar ResourceWarnings y problemas con archivos
if LOGS_DIR and LOGS_DIR.exists() and not IS_TESTING:
    handlers_config['file'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': str(LOGS_DIR / 'django.log'),
        'formatter': 'verbose',
    }
    root_handlers = ['console', 'file']
    django_handlers = ['console', 'file']
else:
    # En modo test o si no hay directorio de logs, usar solo console
    root_handlers = ['console']
    django_handlers = ['console']

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
    'handlers': handlers_config,
    'root': {
        'handlers': root_handlers,
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': django_handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'cacaoscan.api': {
            'handlers': django_handlers,
            'level': 'DEBUG',
            'propagate': False,
        },
        'cacaoscan.ml': {
            'handlers': django_handlers,
            'level': 'DEBUG',
            'propagate': False,
        },
        # Suprimir warnings de pkg_resources
        'pkg_resources': {
            'handlers': root_handlers,
            'level': 'ERROR',
            'propagate': False,
        },
        # Suprimir warnings de drf_yasg
        'drf_yasg': {
            'handlers': root_handlers,
            'level': 'ERROR',
            'propagate': False,
        },
        # Suprimir warnings de torchvision
        'torchvision': {
            'handlers': root_handlers,
            'level': 'ERROR',
            'propagate': False,
        },
        # Suprimir warnings de torch
        'torch': {
            'handlers': root_handlers,
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

DEFAULT_DEV_FRONTEND_URL = 'https://localhost:5173'


def _validated_frontend_url(url_value: str, is_debug: bool) -> str:
    """Validate FRONTEND_URL enforcing HTTPS outside local development."""
    sanitized_value = url_value.strip()
    if not sanitized_value:
        raise ValueError("FRONTEND_URL cannot be empty.")

    is_valid, reason = _validate_cors_origin(sanitized_value, is_debug)
    if not is_valid:
        warnings.warn(
            f"FRONTEND_URL '{sanitized_value}' rejected: {reason}",
            SecurityWarning
        )
        raise ValueError(
            f"FRONTEND_URL must be a valid origin. Reason: {reason}. "
            f"Current value: {sanitized_value}."
        )

    return sanitized_value


# FRONTEND_URL: Use HTTPS in production, HTTP only allowed for localhost in development
# SECURITY: HTTP is insecure for sensitive data transmission (S5332)
frontend_url_env = os.environ.get('FRONTEND_URL', '').strip()
if frontend_url_env:
    FRONTEND_URL = _validated_frontend_url(frontend_url_env, DEBUG)
else:
    if DEBUG:
        FRONTEND_URL = _validated_frontend_url(DEFAULT_DEV_FRONTEND_URL, True)
    else:
        FRONTEND_URL = ''
        warnings.warn(
            "FRONTEND_URL is not set in production. "
            "Set FRONTEND_URL to an HTTPS URL (S5332).",
            SecurityWarning
        )
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
    'reset_request',    # Restablecimiento de credenciales
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

# Configuración de Celery
# Si Redis no está disponible, usar broker en memoria (solo para desarrollo)
USE_CELERY_REDIS = os.environ.get('USE_CELERY_REDIS', 'True').lower() == 'true'

if USE_CELERY_REDIS:
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
else:
    # Broker en memoria para desarrollo sin Redis (NO usar en producción)
    # Nota: Estos valores se usan solo si Celery se inicializa, pero si USE_CELERY_REDIS=False,
    # Celery no se inicializará en absoluto (ver cacaoscan/__init__.py)
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
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