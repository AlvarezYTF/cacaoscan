"""
Vistas para la configuraciÃ³n del sistema.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
try:
    from core.models import SystemSettings
except ImportError:
    SystemSettings = None
from .serializers import SystemSettingsSerializer


class SystemSettingsView(APIView):
    """
    Vista para obtener y actualizar la configuraciÃ³n del sistema.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Solo los administradores pueden acceder a esta vista.
        """
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get(self, request):
        """
        Obtener la configuraciÃ³n del sistema.
        """
        try:
            settings = SystemSettings.get_singleton()
            serializer = SystemSettingsSerializer(settings, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """
        Actualizar la configuraciÃ³n del sistema.
        Solo permite actualizar, no crear (es un singleton).
        """
        try:
            settings = SystemSettings.get_singleton()
            serializer = SystemSettingsSerializer(
                settings,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemGeneralConfigView(APIView):
    """
    Vista especÃ­fica para la configuraciÃ³n general.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Obtener solo la configuraciÃ³n general.
        """
        try:
            settings = SystemSettings.get_singleton()
            
            # Si no hay configuraciÃ³n, retornar valores por defecto
            if not settings:
                return Response({
                    'nombre_sistema': 'CacaoScan',
                    'email_contacto': 'contacto@cacaoscan.com',
                    'lema': 'La mejor plataforma para el control de calidad del cacao',
                    'logo_url': None
                }, status=status.HTTP_200_OK)
            
            data = {
                'nombre_sistema': settings.nombre_sistema or 'CacaoScan',
                'email_contacto': settings.email_contacto or 'contacto@cacaoscan.com',
                'lema': settings.lema or 'La mejor plataforma para el control de calidad del cacao',
                'logo_url': request.build_absolute_uri(settings.logo.url) if settings.logo else None
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            # Retornar valores por defecto en caso de error
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.warning(f"Error cargando configuraciÃ³n general: {e}")
            
            return Response({
                'nombre_sistema': 'CacaoScan',
                'email_contacto': 'contacto@cacaoscan.com',
                'lema': 'La mejor plataforma para el control de calidad del cacao',
                'logo_url': None
            }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Actualizar la configuraciÃ³n general.
        """
        # Verificar permisos de admin para PUT
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para editar la configuraciÃ³n'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            settings = SystemSettings.get_singleton()
            
            # Actualizar campos si vienen en el request
            if 'nombre_sistema' in request.data:
                settings.nombre_sistema = request.data['nombre_sistema']
            if 'email_contacto' in request.data:
                settings.email_contacto = request.data['email_contacto']
            if 'lema' in request.data:
                settings.lema = request.data['lema']
            
            settings.save()
            
            data = {
                'nombre_sistema': settings.nombre_sistema,
                'email_contacto': settings.email_contacto,
                'lema': settings.lema,
                'logo_url': request.build_absolute_uri(settings.logo.url) if settings.logo else None
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemSecurityConfigView(APIView):
    """
    Vista especÃ­fica para la configuraciÃ³n de seguridad.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Obtener solo la configuraciÃ³n de seguridad.
        """
        try:
            settings = SystemSettings.get_singleton()
            
            # Si no hay configuraciÃ³n, retornar valores por defecto
            if not settings:
                return Response({
                    'recaptcha_enabled': True,
                    'session_timeout': 60,
                    'login_attempts': 5,
                    'two_factor_auth': False
                }, status=status.HTTP_200_OK)
            
            data = {
                'recaptcha_enabled': settings.recaptcha_enabled if hasattr(settings, 'recaptcha_enabled') else True,
                'session_timeout': settings.session_timeout if hasattr(settings, 'session_timeout') else 60,
                'login_attempts': settings.login_attempts if hasattr(settings, 'login_attempts') else 5,
                'two_factor_auth': settings.two_factor_auth if hasattr(settings, 'two_factor_auth') else False
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            # Retornar valores por defecto en caso de error
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.warning(f"Error cargando configuraciÃ³n de seguridad: {e}")
            
            return Response({
                'recaptcha_enabled': True,
                'session_timeout': 60,
                'login_attempts': 5,
                'two_factor_auth': False
            }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Actualizar la configuraciÃ³n de seguridad.
        """
        try:
            settings = SystemSettings.get_singleton()
            
            if 'recaptcha_enabled' in request.data:
                settings.recaptcha_enabled = request.data['recaptcha_enabled']
            if 'session_timeout' in request.data:
                settings.session_timeout = request.data['session_timeout']
            if 'login_attempts' in request.data:
                settings.login_attempts = request.data['login_attempts']
            if 'two_factor_auth' in request.data:
                settings.two_factor_auth = request.data['two_factor_auth']
            
            settings.save()
            
            data = {
                'recaptcha_enabled': settings.recaptcha_enabled,
                'session_timeout': settings.session_timeout,
                'login_attempts': settings.login_attempts,
                'two_factor_auth': settings.two_factor_auth
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemMLConfigView(APIView):
    """
    Vista especÃ­fica para la configuraciÃ³n de modelos ML.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Obtener solo la configuraciÃ³n de ML.
        """
        try:
            settings = SystemSettings.get_singleton()
            
            # Si no hay configuraciÃ³n, retornar valores por defecto
            if not settings:
                return Response({
                    'active_model': 'yolov8',
                    'last_training': None
                }, status=status.HTTP_200_OK)
            
            data = {
                'active_model': settings.active_model if hasattr(settings, 'active_model') else 'yolov8',
                'last_training': settings.last_training.isoformat() if hasattr(settings, 'last_training') and settings.last_training else None
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            # Retornar valores por defecto en caso de error
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.warning(f"Error cargando configuraciÃ³n ML: {e}")
            
            return Response({
                'active_model': 'yolov8',
                'last_training': None
            }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Actualizar la configuraciÃ³n de ML.
        """
        try:
            settings = SystemSettings.get_singleton()
            
            if 'active_model' in request.data:
                settings.active_model = request.data['active_model']
            if 'last_training' in request.data:
                settings.last_training = timezone.now()
            
            settings.save()
            
            data = {
                'active_model': settings.active_model,
                'last_training': settings.last_training.isoformat() if settings.last_training else None
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemInfoView(APIView):
    """
    Vista para obtener informaciÃ³n del sistema.
    Accesible pÃºblicamente para verificar estado del servidor.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Obtener informaciÃ³n del sistema.
        """
        try:
            import django
            from django.conf import settings
            
            data = {
                'system': 'CacaoScan',
                'version': '1.0.0',
                'status': 'ok',
                'server_status': 'online',
                'backend_version': django.get_version(),
                'frontend_version': '3.5.3',
                'database': 'PostgreSQL 16',
                'active_routes': [
                    '/api/v1/auth/',
                    '/api/v1/fincas/',
                    '/api/v1/images/',
                    '/api/v1/config/'
                ],
                'author': 'Equipo SENA Guaviare'
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            # Retornar datos mÃ­nimos incluso si hay error
            return Response({
                'system': 'CacaoScan',
                'version': '1.0.0',
                'status': 'ok',
                'server_status': 'online',
                'author': 'Equipo SENA Guaviare',
                'error': 'Error al obtener detalles completos'
            }, status=status.HTTP_200_OK)



