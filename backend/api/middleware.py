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
        # Solo asignar audit_action si el usuario está autenticado
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.audit_action = self.determine_action(request)
        else:
            request.audit_action = None
        
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
                
                self.log_activity(request)
                
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
    
    def _determine_post_action(self, path: str) -> str:
        """Determina la acción para métodos POST."""
        if '/login/' in path:
            return 'login'
        if '/register/' in path:
            return 'create'
        if '/upload/' in path or '/images/' in path:
            return 'upload'
        if '/train/' in path:
            return 'training'
        if '/report/' in path:
            return 'report'
        return 'create'
    
    def _determine_get_action(self, path: str) -> str:
        """Determina la acción para métodos GET."""
        if '/download/' in path:
            return 'download'
        if '/stats/' in path or '/analytics/' in path:
            return 'view'
        return 'view'
    
    def determine_action(self, request):
        """Determinar la acción basada en el método HTTP y path."""
        method = request.method
        path = request.path
        
        if method == 'POST':
            return self._determine_post_action(path)
        if method in ('PUT', 'PATCH'):
            return 'update'
        if method == 'DELETE':
            return 'delete'
        if method == 'GET':
            return self._determine_get_action(path)
        
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
    
    def log_activity(self, request):
        """Registrar la actividad del usuario."""
        try:
            action = request.audit_action
            model = self.determine_model(request)
            
            # Crear descripción de la actividad
            description = self.create_description(request, action, model)
            
            # Extraer ID del objeto si está disponible
            object_id = self.extract_object_id(request)
            
            # Registrar en ActivityLog usando ContentType para integridad referencial avanzada
            from django.contrib.contenttypes.models import ContentType
            
            # Try to get content_object if object_id and model are available
            content_type = None
            content_object = None
            
            if model and object_id:
                try:
                    # Try to get ContentType from model string (e.g., "fincas_app.finca")
                    if '.' in model:
                        app_label, model_name = model.split('.', 1)
                        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                        # Try to get the actual object
                        try:
                            model_class = content_type.model_class()
                            if model_class:
                                content_object = model_class.objects.filter(pk=object_id).first()
                        except Exception:
                            pass
                except ContentType.DoesNotExist:
                    pass
            
            # Create ActivityLog with ContentType fields (flexible audit pattern)
            details = {}
            if description:
                details['description'] = description
            if request.audit_info.get('data_before'):
                details['before'] = request.audit_info.get('data_before')
            if request.audit_info.get('data_after'):
                details['after'] = request.audit_info.get('data_after')
            
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                content_type=content_type,
                object_id=object_id if content_type else None,
                resource_type=model or "",  # Legacy field
                resource_id=int(object_id) if object_id else None,  # Legacy field
                details=details,
                ip_address=request.audit_info['ip_address'],
                user_agent=request.audit_info['user_agent'],
                timestamp=timezone.now()
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
                       ip_address=None, user_agent=None, data_before=None, data_after=None,
                       content_object=None):
    """
    Función helper para registrar actividades personalizadas.
    Normalizado: Usa ContentType para integridad referencial.
    
    Args:
        user: Usuario que realizó la acción
        action: Tipo de acción
        model: Modelo afectado (string, formato: "app_label.model_name")
        description: Descripción de la acción
        object_id: ID del objeto afectado (usar content_object en su lugar si es posible)
        ip_address: Dirección IP
        user_agent: User Agent del navegador
        data_before: Estado antes de la acción
        data_after: Estado después de la acción
        content_object: Objeto relacionado (recomendado - normalizado con ContentType)
    """
    if ActivityLog is None:
        return
    
    try:
        from django.contrib.contenttypes.models import ContentType
        
        content_type = None
        obj_id = None
        
        # Use content_object if provided (normalized approach)
        if content_object is not None:
            content_type = ContentType.objects.get_for_model(content_object)
            obj_id = content_object.pk
        elif model and object_id:
            # Try to get ContentType from model string
            try:
                if '.' in model:
                    app_label, model_name = model.split('.', 1)
                    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                    obj_id = int(object_id) if object_id else None
            except ContentType.DoesNotExist:
                pass
        
        # Create details dict
        details = {}
        if description:
            details['description'] = description
        if data_before:
            details['before'] = data_before
        if data_after:
            details['after'] = data_after
        
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=obj_id,
            resource_type=model or "",  # Legacy field
            resource_id=int(object_id) if object_id else None,  # Legacy field
            details=details,
            ip_address=ip_address,
            user_agent=user_agent or "",
            timestamp=timezone.now()
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

