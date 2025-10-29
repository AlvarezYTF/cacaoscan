"""
Vistas para la configuración del sistema.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import SystemSettings
from .serializers import SystemSettingsSerializer


class SystemSettingsView(APIView):
    """
    Vista para obtener y actualizar la configuración del sistema.
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
        Obtener la configuración del sistema.
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
        Actualizar la configuración del sistema.
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
    Vista específica para la configuración general.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Obtener solo la configuración general.
        """
        try:
            settings = SystemSettings.get_singleton()
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
    
    def put(self, request):
        """
        Actualizar la configuración general.
        """
        # Verificar permisos de admin para PUT
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para editar la configuración'},
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
    Vista específica para la configuración de seguridad.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Obtener solo la configuración de seguridad.
        """
        try:
            settings = SystemSettings.get_singleton()
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
    
    def put(self, request):
        """
        Actualizar la configuración de seguridad.
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
    Vista específica para la configuración de modelos ML.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Obtener solo la configuración de ML.
        """
        try:
            settings = SystemSettings.get_singleton()
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
    
    def put(self, request):
        """
        Actualizar la configuración de ML.
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
    Vista para obtener información del sistema.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Obtener información del sistema.
        """
        try:
            import django
            from django.conf import settings
            
            data = {
                'version': '1.0.0',
                'server_status': 'online',
                'backend_version': django.get_version(),
                'frontend_version': '3.5.3',
                'database': 'PostgreSQL 16',
                'active_routes': [
                    '/api/auth/',
                    '/api/fincas/',
                    '/api/analisis/',
                    '/api/config/'
                ]
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

