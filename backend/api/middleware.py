"""
Middleware para auditoría automática en CacaoScan.
"""
import logging
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from audit.models import LoginHistory
try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None

logger = logging.getLogger("cacaoscan.api")


class AuditMiddleware:
    """
    Middleware para registrar automáticamente las actividades de los usuarios.
    Migrado a patrón nuevo de Django 5.2+ (sin MiddlewareMixin).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """Procesar request y response en un solo método."""
        # Procesar request y extraer información de auditoría
        request.audit_info = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'timestamp': timezone.now(),
        }
        
        # Determinar acción basada en el método HTTP y path
        request.audit_action = self.determine_action(request)
        
        # Obtener response
        response = self.get_response(request)
        
        # Procesar response y registrar actividad si es necesario
        try:
            # Solo registrar para usuarios autenticados y respuestas exitosas
            if (hasattr(request, 'user') and 
                request.user.is_authenticated and 
                response.status_code < 400 and
                hasattr(request, 'audit_action') and
                request.audit_action):
                
                self.log_activity(request, response)
                
        except Exception as e:
            logger.error(f"Error en middleware de auditoría: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def determine_action(self, request):
        """Determinar la acción basada en el método HTTP y path."""
        method = request.method
        path = request.path
        
        # Mapeo de acciones basado en patrones de URL
        if method == 'POST':
            if '/login/' in path:
                return 'login'
            elif '/register/' in path:
                return 'create'
            elif '/upload/' in path or '/images/' in path and method == 'POST':
                return 'upload'
            elif '/train/' in path:
                return 'training'
            elif '/report/' in path:
                return 'report'
            else:
                return 'create'
        
        elif method == 'PUT' or method == 'PATCH':
            return 'update'
        
        elif method == 'DELETE':
            return 'delete'
        
        elif method == 'GET':
            if '/download/' in path:
                return 'download'
            elif '/stats/' in path or '/analytics/' in path:
                return 'view'
            else:
                return 'view'
        
        return None
    
    def determine_model(self, request):
        """Determinar el modelo basado en el path."""
        path = request.path
        
        if '/fincas/' in path:
            return 'Finca'
        elif '/lotes/' in path:
            return 'Lote'
        elif '/images/' in path:
            return 'CacaoImage'
        elif '/predictions/' in path:
            return 'CacaoPrediction'
        elif '/train/' in path:
            return 'TrainingJob'
        elif '/notifications/' in path:
            return 'Notification'
        elif '/users/' in path:
            return 'User'
        elif '/auth/' in path:
            return 'User'
        else:
            return 'Unknown'
    
    def log_activity(self, request, response):
        """Registrar la actividad del usuario."""
        try:
            action = request.audit_action
            model = self.determine_model(request)
            
            # Crear descripción de la actividad
            description = self.create_description(request, action, model)
            
            # Extraer ID del objeto si está disponible
            object_id = self.extract_object_id(request)
            
            # Registrar en ActivityLog
            ActivityLog.log_activity(
                usuario=request.user,
                accion=action,
                modelo=model,
                descripcion=description,
                objeto_id=object_id,
                ip_address=request.audit_info['ip_address'],
                user_agent=request.audit_info['user_agent']
            )
            
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error registrando actividad: {e}")
    
    def create_description(self, request, action, model):
        """Crear descripción detallada de la actividad."""
        user = request.user.username
        
        descriptions = {
            'login': f"Usuario {user} inició sesión",
            'logout': f"Usuario {user} cerró sesión",
            'create': f"Usuario {user} creó un nuevo {model}",
            'update': f"Usuario {user} actualizó {model}",
            'delete': f"Usuario {user} eliminó {model}",
            'view': f"Usuario {user} visualizó {model}",
            'download': f"Usuario {user} descargó {model}",
            'upload': f"Usuario {user} subió {model}",
            'analysis': f"Usuario {user} realizó análisis de {model}",
            'training': f"Usuario {user} ejecutó entrenamiento de {model}",
            'report': f"Usuario {user} generó reporte de {model}",
        }
        
        return descriptions.get(action, f"Usuario {user} realizó {action} en {model}")
    
    def extract_object_id(self, request):
        """Extraer ID del objeto de la URL."""
        try:
            # Buscar patrones como /api/modelos/123/
            path_parts = request.path.strip('/').split('/')
            for part in path_parts:
                if part.isdigit():
                    return part
        except Exception:  # noqa: BLE001
            pass
        return None


class LoginAuditMiddleware:
    """
    Middleware específico para auditar inicios y cierres de sesión.
    Migrado a patrón nuevo de Django 5.2+ (sin MiddlewareMixin).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """Procesar request y response en un solo método."""
        # Procesar request para detectar login/logout
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Verificar si es un nuevo login
            if not hasattr(request, '_login_logged'):
                self.log_login(request)
                request._login_logged = True
        
        # Obtener response
        response = self.get_response(request)
        
        # Procesar response para detectar logout
        try:
            # Detectar logout basado en respuesta específica
            if (hasattr(request, 'user') and 
                request.user.is_authenticated and
                response.status_code == 200 and
                '/logout/' in request.path):
                
                self.log_logout(request)
                
        except Exception as e:
            logger.error(f"Error en middleware de login audit: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_login(self, request):
        """Registrar inicio de sesión."""
        try:
            LoginHistory.log_login(
                usuario=request.user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
            
            logger.info(f"Login registrado para usuario {request.user.username}")
            
        except Exception as e:
            logger.error(f"Error registrando login: {e}")
    
    def log_logout(self, request):
        """Registrar cierre de sesión."""
        try:
            LoginHistory.log_logout(
                usuario=request.user,
                ip_address=self.get_client_ip(request)
            )
            
            logger.info(f"Logout registrado para usuario {request.user.username}")
            
        except Exception as e:
            logger.error(f"Error registrando logout: {e}")


def log_custom_activity(user, action, model, description, object_id=None, 
                       ip_address=None, user_agent=None, data_before=None, data_after=None):
    """
    Función helper para registrar actividades personalizadas.
    
    Args:
        user: Usuario que realizó la acción
        action: Tipo de acción
        model: Modelo afectado
        description: Descripción de la acción
        object_id: ID del objeto afectado
        ip_address: Dirección IP
        user_agent: User Agent del navegador
        data_before: Estado antes de la acción
        data_after: Estado después de la acción
    """
    try:
        ActivityLog.log_activity(
            usuario=user,
            accion=action,
            modelo=model,
            descripcion=description,
            objeto_id=object_id,
            ip_address=ip_address,
            user_agent=user_agent,
            datos_antes=data_before,
            datos_despues=data_after
        )
        
        logger.info(f"Actividad personalizada registrada: {user.username} - {action} - {model}")
        
    except Exception as e:
        logger.error(f"Error registrando actividad personalizada: {e}")


def log_failed_login(username, ip_address, user_agent, failure_reason):
    """
    Función helper para registrar intentos de login fallidos.
    
    Args:
        username: Nombre de usuario intentado
        ip_address: Dirección IP
        user_agent: User Agent del navegador
        failure_reason: Razón del fallo
    """
    try:
        # Crear usuario temporal para el log (no se guarda en BD)
        temp_user = User(username=username)
    
        LoginHistory.log_login(
            usuario=temp_user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason=failure_reason
        )
        
        logger.warning(f"Login fallido registrado: {username} - {failure_reason}")
            
    except Exception as e:
        logger.error(f"Error registrando login fallido: {e}")


class TokenCleanupMiddleware:
    """
    Middleware para limpiar tokens JWT expirados automáticamente.
    Migrado a patrón nuevo de Django 5.2+ (sin MiddlewareMixin).
    
    NOTA: La limpieza de tokens está deshabilitada en este middleware.
    Se debe usar la tarea de Celery: api.tasks.token_cleanup.cleanup_expired_tokens
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Procesar request (limpieza de tokens deshabilitada).
        
        TODO: This expensive operation has been disabled in request processing.
        Move token cleanup to a Celery periodic task (see api.tasks.token_cleanup.cleanup_expired_tokens).
        Recommended schedule: Run every hour via Celery Beat.
        """
        # DISABLED: Token cleanup moved to Celery task to avoid performance impact on each request
        # See: api.tasks.token_cleanup.cleanup_expired_tokens
        
        # Obtener response sin procesar limpieza de tokens
        response = self.get_response(request)
        return response

