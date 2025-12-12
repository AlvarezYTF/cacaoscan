"""
Login views for CacaoScan API.
"""
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import login, logout, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import (
    LoginSerializer,
    UserSerializer,
    ErrorResponseSerializer
)
from core.utils import create_error_response, create_success_response

User = get_user_model()
logger = logging.getLogger("cacaoscan.api.auth")


class LoginView(APIView):
    """
    Endpoint para login de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Autentica un usuario y devuelve un token de acceso",
        operation_summary="Login de usuario",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
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
        Autentica un usuario y devuelve tokens JWT.
        """
        try:
            # Log de datos recibidos (sin password por seguridad)
            login_identifier = request.data.get('email') or request.data.get('username', 'N/A')
            logger.info(f"Intento de login para: {login_identifier}")
            
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                logger.info(f"Login exitoso para usuario: {user.username} (ID: {user.id}, Activo: {user.is_active})")
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Login en la sesión
                login(request, user)
                
                # Incluir has_password, login_provider y password_allowed en la respuesta
                has_password = user.has_usable_password()
                user_data = UserSerializer(user).data
                login_provider = user_data.get('login_provider', 'local')
                password_allowed = login_provider != 'google'
                
                return create_success_response(
                    message='Login exitoso',
                    data={
                        'access': str(access_token),
                        'refresh': str(refresh),
                        'user': user_data,
                        'has_password': has_password,
                        'login_provider': login_provider,
                        'password_allowed': password_allowed,
                        'access_expires_at': access_token['exp'],
                        'refresh_expires_at': refresh['exp']
                    }
                )
            
            # Log de errores de validación para diagnóstico
            logger.warning(f"Login fallido para: {login_identifier}. Errores: {serializer.errors}")
            
            return create_error_response(
                message='Credenciales inválidas',
                error_type='invalid_credentials',
                status_code=status.HTTP_401_UNAUTHORIZED,
                details=serializer.errors
            )
        except Exception as e:
            logger.error(f"Error en LoginView: {str(e)}", exc_info=True)
            return create_error_response(
                message='Error interno del servidor',
                error_type='internal_server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    Endpoint para logout de usuario.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Cierra la sesión del usuario y elimina el token",
        operation_summary="Logout de usuario",
        responses={
            200: openapi.Response(
                description="Logout exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Cierra la sesión del usuario y blacklistea el token de refresh.
        """
        try:
            # Obtener el token de refresh del cuerpo de la petición
            refresh_token = request.data.get('refresh')
            
            if refresh_token:
                # Blacklistear el token de refresh
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Logout de la sesión
            logout(request)
            
            return Response({
                'message': 'Logout exitoso'
            })
        except TokenError:
            return Response({
                'error': 'Token inválido',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Error en logout: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Endpoint para obtener perfil del usuario actual.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la información del perfil del usuario autenticado",
        operation_summary="Perfil de usuario",
        responses={
            200: UserSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request):
        """
        Obtiene el perfil del usuario actual.
        Asegura que UserProfile exista para evitar errores.
        """
        # Asegurar que UserProfile exista (usar get_or_create para evitar errores)
        from auth_app.models import UserProfile
        UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'login_provider': 'local'}
        )
        return Response(UserSerializer(request.user).data)


class RefreshTokenView(APIView):
    """
    Endpoint para refrescar token de acceso JWT.
    """
    permission_classes = [AllowAny]  # Cambiar a AllowAny porque necesitamos el refresh token
    
    @swagger_auto_schema(
        operation_description="Refresca el token de acceso usando el token de refresh",
        operation_summary="Refrescar token JWT",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Token de refresh')
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Token refrescado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access_expires_at': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Refresca el token de acceso usando el token de refresh.
        """
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return create_error_response(
                    message='Token de refresh requerido',
                    error_type='missing_refresh_token',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear nuevo token de acceso usando el refresh token
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
            
            return create_success_response(
                message='Token refrescado exitosamente',
                data={
                    'access': str(new_access_token),
                    'refresh': str(refresh),
                    'access_expires_at': new_access_token['exp']
                }
            )
            
        except TokenError as e:
            return create_error_response(
                message='Token de refresh inválido o expirado',
                error_type='invalid_refresh_token',
                status_code=status.HTTP_400_BAD_REQUEST,
                details={'error': str(e)}
            )
        except Exception as e:
            return create_error_response(
                message='Error refrescando token',
                error_type='refresh_error',
                status_code=status.HTTP_400_BAD_REQUEST,
                details={'error': str(e)}
            )

