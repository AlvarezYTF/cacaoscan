"""
Google OAuth login views for CacaoScan API.
"""
import logging
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model, login
from google.oauth2 import id_token
from google.auth.transport import requests

from api.serializers import UserSerializer, ErrorResponseSerializer
from core.utils import create_error_response, create_success_response

User = get_user_model()
logger = logging.getLogger("cacaoscan.api.auth")

# Cliente HTTP para validación de tokens de Google
GOOGLE_REQUEST = requests.Request()


class GoogleLoginView(APIView):
    """
    Endpoint para login con Google OAuth.
    Valida el ID Token de Google y crea/autentica al usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Autentica un usuario usando Google OAuth (ID Token)",
        operation_summary="Login con Google",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'credential': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='ID Token de Google (JWT)'
                )
            },
            required=['credential']
        ),
        responses={
            200: openapi.Response(
                description="Login exitoso con Google",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'picture': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Valida el ID Token de Google y crea/autentica al usuario.
        
        Args:
            request.data['credential']: ID Token JWT de Google
            
        Returns:
            JSON con tokens JWT, email, name y picture
        """
        try:
            credential = request.data.get('credential')
            
            if not credential:
                return create_error_response(
                    message='Credential token requerido',
                    error_type='missing_credential',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar el ID Token de Google
            try:
                idinfo = id_token.verify_oauth2_token(
                    credential,
                    GOOGLE_REQUEST,
                    None  # No se requiere CLIENT_ID aquí, Google lo valida automáticamente
                )
            except ValueError as e:
                logger.warning(f"Token de Google inválido: {str(e)}")
                return create_error_response(
                    message='Token de Google inválido',
                    error_type='invalid_google_token',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    details={'error': str(e)}
                )
            
            # Extraer información del usuario de Google
            email = idinfo.get('email')
            if not email:
                return create_error_response(
                    message='El token de Google no contiene email',
                    error_type='missing_email',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Normalizar email a lowercase
            email = email.lower().strip()
            
            name = idinfo.get('name', '')
            given_name = idinfo.get('given_name', '')
            family_name = idinfo.get('family_name', '')
            picture = idinfo.get('picture', '')
            
            # Buscar o crear usuario
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,  # Usar email como username
                    'first_name': given_name or name.split()[0] if name else '',
                    'last_name': family_name or ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                    'is_active': True,  # Usuarios de Google se activan automáticamente
                }
            )
            
            if created:
                logger.info(f"Usuario creado desde Google OAuth: {email}")
                
                # Marcar contraseña como no usable (solo puede entrar con Google)
                user.set_unusable_password()
                user.save()
                
                # 🔥 FIX: Crear o actualizar UserProfile con login_provider = "google"
                from auth_app.models import UserProfile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'login_provider': 'google'}
                )
                # 🔥 SIEMPRE establecer login_provider = "google" para nuevos usuarios Google
                if not created:
                    profile.login_provider = 'google'
                    profile.save()
                
                # Asegurar que user.auth_profile esté sincronizado
                if hasattr(user, 'auth_profile'):
                    user.auth_profile.login_provider = 'google'
                    user.auth_profile.save()
                
                # Marcar como verificado automáticamente (viene de Google)
                from auth_app.models import EmailVerification
                EmailVerification.objects.create(
                    user=user,
                    email=email,
                    verification_type=EmailVerification.VERIFICATION_TYPE_REGISTRATION,
                    is_verified=True
                )
            else:
                # Si el usuario ya existe, actualizar información si es necesario
                updated = False
                if given_name and not user.first_name:
                    user.first_name = given_name
                    updated = True
                if family_name and not user.last_name:
                    user.last_name = family_name
                    updated = True
                if updated:
                    user.save()
                
                # 🔥 FIX: Asegurar que el UserProfile tenga login_provider = "google"
                from auth_app.models import UserProfile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'login_provider': 'google'}
                )
                # 🔥 SIEMPRE establecer login_provider = "google" para usuarios existentes que usan Google
                if not created:
                    profile.login_provider = 'google'
                    profile.save()
                
                # Asegurar que user.auth_profile esté sincronizado
                if hasattr(user, 'auth_profile'):
                    user.auth_profile.login_provider = 'google'
                    user.auth_profile.save()
                
                logger.info(f"Usuario autenticado desde Google OAuth: {email}")
            
            # Asegurar que el usuario esté activo
            if not user.is_active:
                user.is_active = True
                user.save()
            
            # Generar tokens JWT del sistema
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Login en la sesión
            login(request, user)
            
            # Verificar si el usuario tiene contraseña usable
            has_password = user.has_usable_password()
            user_data = UserSerializer(user).data
            login_provider = user_data.get('login_provider', 'google')  # Google login siempre es 'google'
            password_allowed = False  # Usuarios Google no pueden usar contraseñas
            
            return create_success_response(
                message='Login exitoso con Google',
                data={
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'user': user_data,
                    'email': email,
                    'name': name or f"{user.first_name} {user.last_name}".strip() or email,
                    'picture': picture,
                    'has_password': has_password,
                    'login_provider': login_provider,
                    'password_allowed': password_allowed,
                    'access_expires_at': access_token['exp'],
                    'refresh_expires_at': refresh['exp']
                }
            )
            
        except Exception as e:
            logger.error(f"Error en GoogleLoginView: {str(e)}", exc_info=True)
            return create_error_response(
                message='Error al procesar login con Google',
                error_type='internal_server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={'error': str(e)}
            )

