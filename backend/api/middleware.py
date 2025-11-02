"""
Middleware para auditorÃ­a automÃ¡tica en CacaoScan.
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from .models import LoginHistory
try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None

logger = logging.getLogger("cacaoscan.api")


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para registrar automÃ¡ticamente las actividades de los usuarios.
    """
    
    def process_request(self, request):
        """Procesar request y extraer informaciÃ³n de auditorÃ­a."""
        # Extraer informaciÃ³n del request
        request.audit_info = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'timestamp': timezone.now(),
        }
        
        # Determinar acciÃ³n basada en el mÃ©todo HTTP y path
        request.audit_action = self.determine_action(request)
        
        return None
    
    def process_response(self, request, response):
        """Procesar response y registrar actividad si es necesario."""
        try:
            # Solo registrar para usuarios autenticados y respuestas exitosas
            if (hasattr(request, 'user') and 
                request.user.is_authenticated and 
                response.status_code < 400 and
                hasattr(request, 'audit_action') and
                request.audit_action):
                
                self.log_activity(request, response)
                
        except Exception as e:
            logger.error(f"Error en middleware de auditorÃ­a: {e}")
        
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
        """Determinar la acciÃ³n basada en el mÃ©todo HTTP y path."""
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
            
            # Crear descripciÃ³n de la actividad
            description = self.create_description(request, action, model)
            
            # Extraer ID del objeto si estÃ¡ disponible
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
            
        except Exception as e:
            logger.error(f"Error registrando actividad: {e}")
    
    def create_description(self, request, action, model):
        """Crear descripciÃ³n detallada de la actividad."""
        method = request.method
        path = request.path
        user = request.user.username
        
        descriptions = {
            'login': f"Usuario {user} iniciÃ³ sesiÃ³n",
            'logout': f"Usuario {user} cerrÃ³ sesiÃ³n",
            'create': f"Usuario {user} creÃ³ un nuevo {model}",
            'update': f"Usuario {user} actualizÃ³ {model}",
            'delete': f"Usuario {user} eliminÃ³ {model}",
            'view': f"Usuario {user} visualizÃ³ {model}",
            'download': f"Usuario {user} descargÃ³ {model}",
            'upload': f"Usuario {user} subiÃ³ {model}",
            'analysis': f"Usuario {user} realizÃ³ anÃ¡lisis de {model}",
            'training': f"Usuario {user} ejecutÃ³ entrenamiento de {model}",
            'report': f"Usuario {user} generÃ³ reporte de {model}",
        }
        
        return descriptions.get(action, f"Usuario {user} realizÃ³ {action} en {model}")
    
    def extract_object_id(self, request):
        """Extraer ID del objeto de la URL."""
        try:
            # Buscar patrones como /api/modelos/123/
            path_parts = request.path.strip('/').split('/')
            for i, part in enumerate(path_parts):
                if part.isdigit():
                    return part
        except:
            pass
        return None


class LoginAuditMiddleware(MiddlewareMixin):
    """
    Middleware especÃ­fico para auditar inicios y cierres de sesiÃ³n.
    """
    
    def process_request(self, request):
        """Procesar request para detectar login/logout."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Verificar si es un nuevo login
            if not hasattr(request, '_login_logged'):
                self.log_login(request)
                request._login_logged = True
        
        return None
    
    def process_response(self, request, response):
        """Procesar response para detectar logout."""
        try:
            # Detectar logout basado en respuesta especÃ­fica
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
        """Registrar inicio de sesiÃ³n."""
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
        """Registrar cierre de sesiÃ³n."""
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
    FunciÃ³n helper para registrar actividades personalizadas.
    
    Args:
        user: Usuario que realizÃ³ la acciÃ³n
        action: Tipo de acciÃ³n
        model: Modelo afectado
        description: DescripciÃ³n de la acciÃ³n
        object_id: ID del objeto afectado
        ip_address: DirecciÃ³n IP
        user_agent: User Agent del navegador
        data_before: Estado antes de la acciÃ³n
        data_after: Estado despuÃ©s de la acciÃ³n
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
    FunciÃ³n helper para registrar intentos de login fallidos.
    
    Args:
        username: Nombre de usuario intentado
        ip_address: DirecciÃ³n IP
        user_agent: User Agent del navegador
        failure_reason: RazÃ³n del fallo
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


class TokenCleanupMiddleware(MiddlewareMixin):
    """
    Middleware para limpiar tokens JWT expirados automÃ¡ticamente.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Procesar request para limpiar tokens expirados.
        """
        try:
            # Importar aquÃ­ para evitar imports circulares
            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
            from django.utils import timezone
            
            # Limpiar tokens expirados de la blacklist
            expired_blacklisted = BlacklistedToken.objects.filter(
                token__expires_at__lt=timezone.now()
            )
            expired_count = expired_blacklisted.count()
            if expired_count > 0:
                expired_blacklisted.delete()
                logger.debug(f"Limpiados {expired_count} tokens blacklisted expirados")
            
            # Limpiar tokens outstanding expirados
            expired_outstanding = OutstandingToken.objects.filter(
                expires_at__lt=timezone.now()
            )
            outstanding_count = expired_outstanding.count()
            if outstanding_count > 0:
                expired_outstanding.delete()
                logger.debug(f"Limpiados {outstanding_count} tokens outstanding expirados")
                
        except Exception as e:
            # No interrumpir el request si hay error en la limpieza
            logger.warning(f"Error en limpieza de tokens: {e}")
        
        return None

