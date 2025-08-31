"""
Middleware de seguridad para el sistema CacaoScan.

Este módulo contiene middleware personalizado para manejar seguridad,
logging, rate limiting y validaciones adicionales.
"""

import time
import logging
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import status
from .models import User

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de seguridad a todas las respuestas.
    """
    
    def process_response(self, request, response):
        """Agrega headers de seguridad estándar."""
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        # Otros headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'speaker=()'
        )
        
        # Solo HTTPS en producción
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware para logging detallado de requests de API.
    """
    
    def process_request(self, request):
        """Registra información del request entrante."""
        request.start_time = time.time()
        
        # Solo loggear APIs, no archivos estáticos
        if request.path.startswith('/api/'):
            user_info = "Anonymous"
            if request.user.is_authenticated:
                user_info = f"{request.user.email} (role: {request.user.role})"
            
            logger.info(
                f"API Request: {request.method} {request.path} "
                f"by {user_info} from IP: {self._get_client_ip(request)}"
            )
    
    def process_response(self, request, response):
        """Registra información del response."""
        if hasattr(request, 'start_time') and request.path.startswith('/api/'):
            duration = time.time() - request.start_time
            
            user_info = "Anonymous"
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"{request.user.email}"
            
            logger.info(
                f"API Response: {request.method} {request.path} "
                f"returned {response.status_code} "
                f"in {duration:.3f}s for {user_info}"
            )
        
        return response
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware para rate limiting basado en IP y usuario.
    """
    
    # Límites por defecto (requests por minuto)
    DEFAULT_LIMITS = {
        'anonymous': 20,  # 20 requests por minuto para anónimos
        'farmer': 60,     # 60 requests por minuto para agricultores
        'analyst': 120,   # 120 requests por minuto para analistas
        'admin': 300,     # 300 requests por minuto para administradores
    }
    
    # Endpoints sensibles con límites más estrictos
    SENSITIVE_ENDPOINTS = {
        '/api/auth/login/': {'anonymous': 5, 'authenticated': 10},
        '/api/auth/register/': {'anonymous': 3, 'authenticated': 5},
        '/api/auth/password-reset/': {'anonymous': 3, 'authenticated': 5},
        '/api/images/predict/': {'farmer': 30, 'analyst': 60, 'admin': 120},
    }
    
    def process_request(self, request):
        """Verifica rate limits antes de procesar el request."""
        
        # Skip rate limiting en desarrollo local
        if settings.DEBUG and self._get_client_ip(request) in ['127.0.0.1', 'localhost']:
            return None
        
        # Solo aplicar a endpoints API
        if not request.path.startswith('/api/'):
            return None
        
        # Obtener identificador único para el rate limit
        identifier = self._get_rate_limit_identifier(request)
        
        # Obtener límite aplicable
        limit = self._get_applicable_limit(request)
        
        # Verificar rate limit
        if self._is_rate_limited(identifier, limit):
            logger.warning(
                f"Rate limit exceeded for {identifier} "
                f"on {request.method} {request.path}"
            )
            
            return JsonResponse({
                'error': _('Demasiadas solicitudes. Intenta de nuevo más tarde.'),
                'detail': f'Límite: {limit} requests por minuto',
                'retry_after': 60
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return None
    
    def _get_rate_limit_identifier(self, request):
        """Obtiene el identificador para rate limiting."""
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            return f"ip:{self._get_client_ip(request)}"
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_applicable_limit(self, request):
        """Determina el límite aplicable para el request."""
        
        # Verificar endpoints sensibles
        for endpoint, limits in self.SENSITIVE_ENDPOINTS.items():
            if request.path.startswith(endpoint):
                if request.user.is_authenticated:
                    user_role = request.user.role
                    return limits.get(user_role, limits.get('authenticated', 10))
                else:
                    return limits.get('anonymous', 5)
        
        # Usar límites por defecto
        if request.user.is_authenticated:
            return self.DEFAULT_LIMITS.get(request.user.role, self.DEFAULT_LIMITS['farmer'])
        else:
            return self.DEFAULT_LIMITS['anonymous']
    
    def _is_rate_limited(self, identifier, limit):
        """Verifica si se ha excedido el rate limit."""
        cache_key = f"rate_limit:{identifier}"
        
        # Obtener contador actual
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return True
        
        # Incrementar contador
        cache.set(cache_key, current_count + 1, 60)  # Expira en 60 segundos
        
        return False


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware para trackear actividad de usuarios autenticados.
    """
    
    def process_request(self, request):
        """Actualiza la última actividad del usuario."""
        if request.user.is_authenticated and hasattr(request.user, 'last_login'):
            # Solo actualizar cada 5 minutos para evitar demasiadas escrituras en BD
            cache_key = f"last_activity:{request.user.id}"
            
            if not cache.get(cache_key):
                # Actualizar timestamp de actividad
                User.objects.filter(id=request.user.id).update(
                    last_login=datetime.now()
                )
                
                # Cachear por 5 minutos
                cache.set(cache_key, True, 300)
                
                logger.debug(f"Updated last activity for user {request.user.email}")
        
        return None


class FileUploadSecurityMiddleware(MiddlewareMixin):
    """
    Middleware para validaciones adicionales de seguridad en uploads.
    """
    
    ALLOWED_UPLOAD_TYPES = {
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/webp'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def process_request(self, request):
        """Valida archivos subidos."""
        
        # Solo validar requests con archivos
        if not request.FILES:
            return None
        
        # Verificar cada archivo
        for field_name, uploaded_file in request.FILES.items():
            
            # Verificar tamaño
            if uploaded_file.size > self.MAX_FILE_SIZE:
                logger.warning(
                    f"File too large uploaded by {getattr(request.user, 'email', 'anonymous')}: "
                    f"{uploaded_file.size} bytes"
                )
                
                return JsonResponse({
                    'error': _('Archivo demasiado grande.'),
                    'detail': f'Tamaño máximo permitido: {self.MAX_FILE_SIZE // (1024*1024)}MB',
                    'file_size': uploaded_file.size
                }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            
            # Verificar tipo MIME
            if uploaded_file.content_type not in self.ALLOWED_UPLOAD_TYPES:
                logger.warning(
                    f"Invalid file type uploaded by {getattr(request.user, 'email', 'anonymous')}: "
                    f"{uploaded_file.content_type}"
                )
                
                return JsonResponse({
                    'error': _('Tipo de archivo no permitido.'),
                    'detail': f'Tipos permitidos: {", ".join(self.ALLOWED_UPLOAD_TYPES)}',
                    'file_type': uploaded_file.content_type
                }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            
            # Verificar nombre de archivo
            if not self._is_safe_filename(uploaded_file.name):
                logger.warning(
                    f"Unsafe filename uploaded by {getattr(request.user, 'email', 'anonymous')}: "
                    f"{uploaded_file.name}"
                )
                
                return JsonResponse({
                    'error': _('Nombre de archivo no válido.'),
                    'detail': 'El nombre de archivo contiene caracteres no permitidos.',
                    'filename': uploaded_file.name
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return None
    
    def _is_safe_filename(self, filename):
        """Verifica que el nombre de archivo sea seguro."""
        import re
        
        # Permitir solo caracteres alfanuméricos, puntos, guiones y espacios
        safe_pattern = re.compile(r'^[a-zA-Z0-9._\-\s]+$')
        
        # Verificar longitud
        if len(filename) > 255:
            return False
        
        # Verificar patrón
        if not safe_pattern.match(filename):
            return False
        
        # Verificar extensiones peligrosas
        dangerous_extensions = {'.exe', '.bat', '.cmd', '.scr', '.pif', '.js', '.vbs'}
        file_extension = '.' + filename.split('.')[-1].lower()
        
        if file_extension in dangerous_extensions:
            return False
        
        return True


class CorsMiddleware(MiddlewareMixin):
    """
    Middleware CORS personalizado para mayor control.
    """
    
    def process_response(self, request, response):
        """Agrega headers CORS según configuración."""
        
        # Solo para endpoints API
        if request.path.startswith('/api/'):
            
            # Obtener origin del request
            origin = request.META.get('HTTP_ORIGIN')
            
            # Lista de orígenes permitidos
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [
                'http://localhost:3000',   # Vue.js dev
                'http://localhost:8080',   # Vue.js dev alternativo
                'http://127.0.0.1:3000',
                'http://127.0.0.1:8080',
            ])
            
            # Verificar origin
            if origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
            
            # Headers permitidos
            response['Access-Control-Allow-Headers'] = (
                'Authorization, Content-Type, Accept, X-Requested-With'
            )
            
            # Métodos permitidos
            response['Access-Control-Allow-Methods'] = (
                'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            )
            
            # Cache de preflight requests
            response['Access-Control-Max-Age'] = '86400'  # 24 horas
        
        return response


class RequestSizeMiddleware(MiddlewareMixin):
    """
    Middleware para limitar el tamaño de requests.
    """
    
    MAX_REQUEST_SIZE = 15 * 1024 * 1024  # 15MB para requests con imágenes
    
    def process_request(self, request):
        """Verifica el tamaño del request."""
        
        # Obtener tamaño del request
        content_length = request.META.get('CONTENT_LENGTH')
        
        if content_length:
            try:
                content_length = int(content_length)
                
                if content_length > self.MAX_REQUEST_SIZE:
                    logger.warning(
                        f"Request too large from {getattr(request.user, 'email', 'anonymous')}: "
                        f"{content_length} bytes"
                    )
                    
                    return JsonResponse({
                        'error': _('Request demasiado grande.'),
                        'detail': f'Tamaño máximo: {self.MAX_REQUEST_SIZE // (1024*1024)}MB',
                        'request_size': content_length
                    }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
                    
            except ValueError:
                pass
        
        return None
