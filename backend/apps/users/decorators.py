"""
Decoradores de validación y guards para el sistema CacaoScan.

Este módulo proporciona decoradores para validar permisos, roles y
condiciones específicas antes de ejecutar vistas y métodos.
"""

from functools import wraps
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)


def require_role(allowed_roles):
    """
    Decorador que requiere uno de los roles especificados.
    
    Args:
        allowed_roles: Lista de roles permitidos ['admin', 'farmer', 'analyst']
    
    Usage:
        @require_role(['admin', 'analyst'])
        def my_view(request):
            # Solo administradores y analistas pueden acceder
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': _('Autenticación requerida.')},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if request.user.role not in allowed_roles:
                logger.warning(
                    f"User {request.user.email} (role: {request.user.role}) "
                    f"attempted to access view requiring roles: {allowed_roles}"
                )
                return JsonResponse(
                    {'error': _('No tienes permisos para acceder a este recurso.')},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_verified_user(view_func):
    """
    Decorador que requiere que el usuario esté verificado.
    
    Usage:
        @require_verified_user
        def upload_image(request):
            # Solo usuarios verificados pueden subir imágenes
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': _('Autenticación requerida.')},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.is_verified:
            logger.info(
                f"Unverified user {request.user.email} attempted to access verified-only resource"
            )
            return JsonResponse(
                {'error': _('Tu cuenta debe estar verificada para realizar esta acción.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_ownership(get_object_func):
    """
    Decorador que requiere que el usuario sea propietario del objeto.
    
    Args:
        get_object_func: Función que retorna el objeto a verificar
    
    Usage:
        def get_image(image_id):
            return CacaoImage.objects.get(id=image_id)
        
        @require_ownership(get_image)
        def delete_image(request, image_id):
            # Solo el propietario puede eliminar su imagen
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': _('Autenticación requerida.')},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            try:
                obj = get_object_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error getting object for ownership check: {e}")
                return JsonResponse(
                    {'error': _('Objeto no encontrado.')},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Administradores pueden acceder a todo
            if request.user.role == 'admin':
                return view_func(request, *args, **kwargs)
            
            # Verificar propiedad
            is_owner = False
            if hasattr(obj, 'uploaded_by'):
                is_owner = obj.uploaded_by == request.user
            elif hasattr(obj, 'user'):
                is_owner = obj.user == request.user
            elif hasattr(obj, 'created_by'):
                is_owner = obj.created_by == request.user
            
            if not is_owner:
                logger.warning(
                    f"User {request.user.email} attempted to access object "
                    f"owned by different user"
                )
                return JsonResponse(
                    {'error': _('Solo puedes acceder a tus propios recursos.')},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_file_upload(allowed_extensions=None, max_size_mb=10):
    """
    Decorador para validar subidas de archivos.
    
    Args:
        allowed_extensions: Lista de extensiones permitidas ['jpg', 'png', 'jpeg']
        max_size_mb: Tamaño máximo en MB
    
    Usage:
        @validate_file_upload(['jpg', 'png'], max_size_mb=5)
        def upload_image(request):
            # Validar archivos antes de procesar
            pass
    """
    if allowed_extensions is None:
        allowed_extensions = ['jpg', 'jpeg', 'png']
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'image' not in request.FILES:
                return JsonResponse(
                    {'error': _('No se ha proporcionado ningún archivo.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            file = request.FILES['image']
            
            # Validar extensión
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                return JsonResponse(
                    {
                        'error': _(
                            f'Formato de archivo no permitido. '
                            f'Extensiones permitidas: {", ".join(allowed_extensions)}'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar tamaño
            max_size_bytes = max_size_mb * 1024 * 1024
            if file.size > max_size_bytes:
                return JsonResponse(
                    {
                        'error': _(
                            f'El archivo es demasiado grande. '
                            f'Tamaño máximo permitido: {max_size_mb}MB'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_api_access(view_func):
    """
    Decorador para registrar accesos a APIs sensibles.
    
    Usage:
        @log_api_access
        def sensitive_endpoint(request):
            # Registra automáticamente el acceso
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_info = "Anonymous"
        if request.user.is_authenticated:
            user_info = f"{request.user.email} (role: {request.user.role})"
        
        logger.info(
            f"API Access: {request.method} {request.path} "
            f"by {user_info} from IP: {get_client_ip(request)}"
        )
        
        try:
            response = view_func(request, *args, **kwargs)
            logger.info(
                f"API Response: {request.method} {request.path} "
                f"returned status {getattr(response, 'status_code', 'unknown')}"
            )
            return response
        except Exception as e:
            logger.error(
                f"API Error: {request.method} {request.path} "
                f"by {user_info} - Error: {str(e)}"
            )
            raise
    
    return wrapper


def rate_limit_by_role(farmer_limit=60, analyst_limit=120, admin_limit=300):
    """
    Decorador para limitar velocidad según el rol.
    
    Args:
        farmer_limit: Requests por hora para agricultores
        analyst_limit: Requests por hora para analistas
        admin_limit: Requests por hora para administradores
    
    Usage:
        @rate_limit_by_role(farmer_limit=30, analyst_limit=60)
        def prediction_endpoint(request):
            # Límites diferentes por rol
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Obtener límite según rol
            role_limits = {
                'farmer': farmer_limit,
                'analyst': analyst_limit,
                'admin': admin_limit
            }
            
            user_limit = role_limits.get(request.user.role, farmer_limit)
            
            # Implementar lógica de rate limiting aquí
            # Por ahora solo logeamos, en producción usar Redis/Memcached
            logger.debug(
                f"Rate limit check for {request.user.email}: "
                f"limit={user_limit}/hour"
            )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_content_type(content_type='application/json'):
    """
    Decorador que requiere un tipo de contenido específico.
    
    Args:
        content_type: Tipo de contenido requerido
    
    Usage:
        @require_content_type('application/json')
        def api_endpoint(request):
            # Solo acepta JSON
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                request_content_type = request.content_type.split(';')[0]
                if request_content_type != content_type:
                    return JsonResponse(
                        {
                            'error': _(
                                f'Content-Type debe ser {content_type}. '
                                f'Recibido: {request_content_type}'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_prediction_data(view_func):
    """
    Decorador específico para validar datos de predicción.
    
    Usage:
        @validate_prediction_data
        def predict_endpoint(request):
            # Datos ya validados
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Validar que hay una imagen
        if 'image' not in request.FILES:
            return JsonResponse(
                {'error': _('Se requiere una imagen para la predicción.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image = request.FILES['image']
        
        # Validar tipo MIME de imagen
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if image.content_type not in allowed_types:
            return JsonResponse(
                {
                    'error': _(
                        'Tipo de imagen no válido. '
                        'Tipos permitidos: JPEG, JPG, PNG'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar dimensiones mínimas (opcional)
        try:
            from PIL import Image
            pil_image = Image.open(image)
            width, height = pil_image.size
            
            if width < 100 or height < 100:
                return JsonResponse(
                    {
                        'error': _(
                            'La imagen debe tener al menos 100x100 píxeles. '
                            f'Dimensiones actuales: {width}x{height}'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error validating image dimensions: {e}")
            return JsonResponse(
                {'error': _('Error procesando la imagen. Verifica que sea válida.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    """Obtiene la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Combinaciones comunes de decoradores
def farmer_upload_endpoint(view_func):
    """
    Decorador combinado para endpoints de subida de agricultores.
    
    Combina: autenticación, rol farmer, verificación, validación de archivo
    """
    @wraps(view_func)
    @require_role(['farmer', 'admin'])
    @require_verified_user
    @validate_file_upload(['jpg', 'jpeg', 'png'], max_size_mb=10)
    @log_api_access
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_management_endpoint(view_func):
    """
    Decorador combinado para endpoints de administración.
    
    Combina: autenticación, rol admin, logging
    """
    @wraps(view_func)
    @require_role(['admin'])
    @log_api_access
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper


def analyst_readonly_endpoint(view_func):
    """
    Decorador combinado para endpoints de solo lectura para analistas.
    
    Combina: autenticación, rol analyst/admin, logging
    """
    @wraps(view_func)
    @require_role(['analyst', 'admin'])
    @log_api_access
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
