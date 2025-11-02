"""
Middleware para integrar auditorÃ­a con WebSockets en tiempo real.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import LoginHistory
try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None
from .realtime_service import realtime_service

logger = logging.getLogger("cacaoscan.websockets")


class RealtimeAuditMiddleware(MiddlewareMixin):
    """
    Middleware para enviar eventos de auditorÃ­a en tiempo real.
    """
    
    def process_request(self, request):
        """Procesar request y preparar datos de auditorÃ­a."""
        # Almacenar informaciÃ³n del request para usar en process_response
        request._audit_start_time = timezone.now()
        request._audit_user = getattr(request, 'user', None)
        request._audit_ip = self.get_client_ip(request)
        request._audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return None
    
    def process_response(self, request, response):
        """Procesar response y enviar evento de auditorÃ­a."""
        try:
            # Solo procesar si hay usuario autenticado
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return response
            
            # Determinar el tipo de acciÃ³n basado en el mÃ©todo HTTP
            action_type = self.get_action_type(request.method)
            
            # Determinar el modelo afectado basado en la URL
            model_name = self.get_model_name(request.path)
            
            # Crear descripciÃ³n de la acciÃ³n
            description = self.create_action_description(request, response)
            
            # Crear log de actividad
            activity_data = {
                'usuario': request.user.username,
                'accion': action_type,
                'accion_display': self.get_action_display(action_type),
                'modelo': model_name,
                'descripcion': description,
                'timestamp': timezone.now().isoformat(),
                'ip_address': getattr(request, '_audit_ip', ''),
                'user_agent': getattr(request, '_audit_user_agent', ''),
                'status_code': response.status_code,
                'response_time_ms': self.calculate_response_time(request)
            }
            
            # Enviar en tiempo real a administradores
            realtime_service.send_activity_log(activity_data)
            
        except Exception as e:
            logger.error(f"Error en middleware de auditorÃ­a en tiempo real: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """Obtener IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_action_type(self, method):
        """Determinar tipo de acciÃ³n basado en mÃ©todo HTTP."""
        action_map = {
            'GET': 'view',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return action_map.get(method, 'view')
    
    def get_model_name(self, path):
        """Determinar modelo afectado basado en la URL."""
        path_parts = path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            api_part = path_parts[0]
            if api_part == 'api':
                model_part = path_parts[1]
                model_map = {
                    'images': 'CacaoImage',
                    'predictions': 'CacaoPrediction',
                    'fincas': 'Finca',
                    'lotes': 'Lote',
                    'notifications': 'Notification',
                    'training': 'TrainingJob',
                    'audit': 'ActivityLog',
                    'users': 'User',
                    'reports': 'ReporteGenerado',
                }
                return model_map.get(model_part, 'Unknown')
        
        return 'System'
    
    def create_action_description(self, request, response):
        """Crear descripciÃ³n de la acciÃ³n."""
        method = request.method
        path = request.path
        status_code = response.status_code
        
        if method == 'GET':
            return f"VisualizaciÃ³n de {path}"
        elif method == 'POST':
            return f"CreaciÃ³n en {path}"
        elif method in ['PUT', 'PATCH']:
            return f"ActualizaciÃ³n en {path}"
        elif method == 'DELETE':
            return f"EliminaciÃ³n en {path}"
        else:
            return f"AcciÃ³n {method} en {path}"
    
    def get_action_display(self, action_type):
        """Obtener display name de la acciÃ³n."""
        action_displays = {
            'view': 'VisualizaciÃ³n',
            'create': 'CreaciÃ³n',
            'update': 'ActualizaciÃ³n',
            'delete': 'EliminaciÃ³n',
            'login': 'Inicio de SesiÃ³n',
            'logout': 'Cierre de SesiÃ³n',
            'download': 'Descarga',
            'upload': 'Subida',
            'analysis': 'AnÃ¡lisis',
            'training': 'Entrenamiento',
            'report': 'Reporte',
            'error': 'Error',
        }
        return action_displays.get(action_type, action_type.title())
    
    def calculate_response_time(self, request):
        """Calcular tiempo de respuesta."""
        if hasattr(request, '_audit_start_time'):
            delta = timezone.now() - request._audit_start_time
            return int(delta.total_seconds() * 1000)  # Convertir a milisegundos
        return 0


class RealtimeLoginMiddleware(MiddlewareMixin):
    """
    Middleware para enviar eventos de login en tiempo real.
    """
    
    def process_request(self, request):
        """Procesar request de login."""
        # Detectar intentos de login
        if request.path in ['/api/auth/login/', '/api/auth/register/'] and request.method == 'POST':
            request._is_login_attempt = True
            request._login_ip = self.get_client_ip(request)
            request._login_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return None
    
    def process_response(self, request, response):
        """Procesar response de login."""
        try:
            if hasattr(request, '_is_login_attempt') and request._is_login_attempt:
                # Determinar si el login fue exitoso
                success = response.status_code == 200
                
                # Obtener informaciÃ³n del usuario si el login fue exitoso
                user = None
                if success and hasattr(request, 'user') and request.user.is_authenticated:
                    user = request.user
                
                # Crear datos de login
                login_data = {
                    'usuario': user.username if user else 'Unknown',
                    'ip_address': getattr(request, '_login_ip', ''),
                    'user_agent': getattr(request, '_login_user_agent', ''),
                    'login_time': timezone.now().isoformat(),
                    'success': success,
                    'status_code': response.status_code,
                    'failure_reason': None if success else 'Invalid credentials'
                }
                
                # Enviar en tiempo real a administradores
                realtime_service.send_login_activity(login_data)
                
        except Exception as e:
            logger.error(f"Error en middleware de login en tiempo real: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """Obtener IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


