"""
Authentication views for CacaoScan API.
"""
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import login, logout, get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    ErrorResponseSerializer
)
from ..utils import create_error_response, create_success_response
from ..email_service import send_email_notification
from ..utils.decorators import handle_api_errors
from ..services.auth_service import AuthenticationService

User = get_user_model()

from ..utils.model_imports import get_model_safely

EmailVerificationToken = get_model_safely('auth_app.models.EmailVerificationToken')

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
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Login en la sesión
                login(request, user)
                
                return create_success_response(
                    message='Login exitoso',
                    data={
                        'access': str(access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data,
                        'access_expires_at': access_token['exp'],
                        'refresh_expires_at': refresh['exp']
                    }
                )
            
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


class RegisterView(APIView):
    """
    Endpoint para registro de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registra un nuevo usuario en el sistema",
        operation_summary="Registro de usuario",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Usuario creado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Registra un nuevo usuario y genera tokens JWT automáticamente.
        """
        # Crear una copia de los datos y eliminar el campo 'role' si viene del frontend
        data = request.data.copy()
        data.pop('role', None)  # Elimina si viene en la solicitud
        
        serializer = RegisterSerializer(data=data)
        
        if serializer.is_valid():
            # Usar servicio de autenticación para registrar usuario
            auth_service = AuthenticationService()
            result = auth_service.register_user_with_email_verification(
                serializer.validated_data,
                request
            )
            
            if result.success:
                return create_success_response(
                    message=result.message,
                    data={
                        'user': UserSerializer(User.objects.get(id=result.data['user']['id'])).data,
                        'verification_required': result.data.get('verification_required', True),
                        'email': result.data.get('email'),
                        'verification_token': result.data.get('verification_token')
                    },
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return create_error_response(
                    message=result.error.message,
                    error_type='validation_error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details=result.error.details
                )
        
        return create_error_response(
            message='Error en los datos proporcionados',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
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
        """
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


class ChangePasswordView(APIView):
    """
    Endpoint para cambiar la contraseña del usuario autenticado.
    Requiere autenticación y validación de la contraseña actual.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Cambiar la contraseña del usuario autenticado.
        
        Requiere:
        - old_password: Contraseña actual
        - new_password: Nueva contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)
        - confirm_password: Confirmación de la nueva contraseña
        """
        from ..serializers import ChangePasswordSerializer
        
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Verificar que la contraseña actual sea correcta
            if not user.check_password(old_password):
                return create_error_response(
                    message='La contraseña actual es incorrecta',
                    error_type='invalid_old_password',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={'old_password': ['La contraseña actual no es correcta.']}
                )
            
            # Cambiar la contraseña
            try:
                user.set_password(new_password)
                user.save()
                
                # Log de auditoría si está disponible
                try:
                    from audit.models import ActivityLog
                    ActivityLog.objects.create(
                        user=user,
                        action='change_password',
                        resource_type='user',
                        resource_id=str(user.id),
                        details={'timestamp': timezone.now().isoformat()},
                        timestamp=timezone.now()
                    )
                except Exception:
                    pass  # Si no hay módulo de auditoría, continuar
                
                return create_success_response(
                    message='Contraseña cambiada exitosamente',
                    data={'user_id': user.id}
                )
                
            except Exception as e:
                logger.error(f"Error cambiando contraseña para usuario {user.id}: {str(e)}")
                return create_error_response(
                    message='Error al cambiar la contraseña',
                    error_type='password_change_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Si hay errores de validación, devolverlos
        return create_error_response(
            message='Errores de validación',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


# Vistas de verificación de email
class EmailVerificationView(APIView):
    """
    Endpoint para verificar email con token.
    Soporta tanto POST (con token en body) como GET (con token en URL).
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica un email usando el token enviado por correo (POST con token en body)",
        operation_summary="Verificar email (POST)",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Email verificado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Verificar email con token (POST con token en body).
        """
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            token_uuid = serializer.validated_data['token']
            return self._verify_token(token_uuid)
        
        return create_error_response(
            message='Datos de verificación inválidos',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )
    
    @swagger_auto_schema(
        operation_description="Verifica un email usando el token desde la URL (GET con token en path)",
        operation_summary="Verificar email (GET)",
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_PATH, description="Token de verificación", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        ],
        responses={
            200: openapi.Response(
                description="Email verificado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request, token=None):
        """
        Verificar email con token (GET con token en URL).
        """
        if not token:
            return create_error_response(
                message='Token de verificación requerido',
                error_type='missing_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return self._verify_token(token)
    
    def _verify_token(self, token_uuid):
        """Método helper para verificar el token."""
        try:
            import uuid
            token_obj = EmailVerificationToken.get_valid_token(str(token_uuid))
        except (ValueError, TypeError):
            return create_error_response(
                message='Formato de token inválido',
                error_type='invalid_token_format',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if token_obj:
            if token_obj.is_verified:
                return create_error_response(
                    message='Este enlace ya fue utilizado',
                    error_type='token_already_used',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if token_obj.is_expired:
                return create_error_response(
                    message='El enlace de verificación ha expirado',
                    error_type='token_expired',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar el token (activa el usuario)
            token_obj.verify()
            
            return create_success_response(
                message='Correo verificado correctamente. Ya puedes iniciar sesión.',
                data={
                    'user': UserSerializer(token_obj.user).data
                }
            )
        else:
            return create_error_response(
                message='Token inválido o expirado',
                error_type='invalid_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(APIView):
    """
    Endpoint para reenviar verificación de email.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Reenvía el token de verificación de email",
        operation_summary="Reenviar verificación",
        request_body=ResendVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Token de verificación reenviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Reenviar token de verificación de email.
        """
        serializer = ResendVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Crear nuevo token de verificación
            token_obj = EmailVerificationToken.create_for_user(user)
            
            # Enviar email de verificación
            try:
                from ..email_service import send_custom_email
                
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{token_obj.token}"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">Verifica tu correo electrónico - CacaoScan</h2>
                        <p>Hola {user.get_full_name() or user.username},</p>
                        <p>Has solicitado un nuevo enlace de verificación. Por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Verificar mi correo</a>
                        </div>
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; color: #666;">{verification_url}</p>
                        <p style="margin-top: 30px; font-size: 12px; color: #999;">Este enlace expirará en 24 horas.</p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
Verifica tu correo electrónico - CacaoScan

Hola {user.get_full_name() or user.username},

Has solicitado un nuevo enlace de verificación. Por favor verifica tu dirección de correo electrónico visitando el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.
                """
                
                send_custom_email(
                    to_emails=[user.email],
                    subject="Verifica tu correo electrónico - CacaoScan",
                    html_content=html_content,
                    text_content=text_content
                )
                
                logger.info(f"Email de verificación reenviado a {user.email}")
            except Exception as e:
                logger.error(f"Error reenviando email de verificación: {e}")
            
            return create_success_response(
                message=f'Token de verificación enviado a {email}',
                data={
                    'expires_at': token_obj.expires_at.isoformat()
                }
            )
        
        return create_error_response(
            message='Email inválido',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


# Vistas de pre-registro (verificación previa)
class PreRegisterView(APIView):
    """
    Endpoint para pre-registro: guarda datos sin crear usuario hasta verificar correo.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Guarda datos de registro pendientes de verificación de correo",
        operation_summary="Pre-registro de usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password']
        ),
        responses={
            201: openapi.Response(
                description="Registro pendiente creado, email de verificación enviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Crea un registro pendiente y envía email de verificación.
        El usuario NO se crea hasta que verifique el correo.
        """
        # Preparar datos para el servicio
        user_data = {
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            **{k: v for k, v in request.data.items() if k not in ['email', 'password', 'first_name', 'last_name']}
        }
        
        # Usar servicio de autenticación para pre-registro
        auth_service = AuthenticationService()
        result = auth_service.pre_register_user(user_data, request)
        
        if result.success:
            status_code = status.HTTP_201_CREATED if 'enviado' in result.message else status.HTTP_200_OK
            return create_success_response(
                message=result.message,
                data=result.data,
                status_code=status_code
            )
        else:
            error_type_map = {
                'email_exists': 'email_exists',
                'validation_error': 'validation_error'
            }
            error_type = error_type_map.get(result.error.error_code, 'validation_error')
            
            return create_error_response(
                message=result.error.message,
                error_type=error_type,
                status_code=status.HTTP_400_BAD_REQUEST,
                details=result.error.details
            )


class VerifyEmailPreRegistrationView(APIView):
    """
    Endpoint para verificar email y crear el usuario final después de pre-registro.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica el email y crea el usuario final a partir del registro pendiente",
        operation_summary="Verificar email y crear usuario",
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_PATH, description="Token de verificación", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        ],
        responses={
            200: openapi.Response(
                description="Usuario creado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request, token=None):
        """
        Verifica el token y crea el usuario final.
        """
        if not token:
            return create_error_response(
                message='Token de verificación requerido',
                error_type='missing_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar servicio de autenticación para verificar pre-registro y crear usuario
        auth_service = AuthenticationService()
        result = auth_service.verify_pre_registration_and_create_user(str(token))
        
        if result.success:
            return create_success_response(
                message=result.message,
                data={
                    'user': UserSerializer(User.objects.get(id=result.data['user']['id'])).data
                }
            )
        else:
            error_type_map = {
                'invalid_token_format': 'invalid_token_format',
                'invalid_token': 'invalid_token',
                'token_already_used': 'token_already_used',
                'token_expired': 'token_expired'
            }
            error_type = error_type_map.get(result.error.error_code, 'validation_error')
            
            return create_error_response(
                message=result.error.message,
                error_type=error_type,
                status_code=status.HTTP_400_BAD_REQUEST,
                details=result.error.details
            )


# Vistas de recuperación de contraseña
class ForgotPasswordView(APIView):
    """
    Paso 1: Solicitud de recuperación.
    Verifica si el correo existe, genera token y envía email.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Envía un email con token para recuperar contraseña",
        operation_summary="Recuperar contraseña",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')
            },
            required=['email']
        ),
        responses={
            200: openapi.Response(
                description="Email de recuperación enviado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            404: openapi.Response(
                description="Correo no registrado en el sistema",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Solicitar recuperación de contraseña.
        Valida que el correo exista antes de generar token o enviar correo.
        """
        try:
            email = request.data.get("email", "").strip().lower()

            if not email:
                return Response(
                    {"success": False, "message": "Debe proporcionar un correo electrónico."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            #  Verificar si el correo existe en la base de datos
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                logger.warning(f"[FORGOT_PASSWORD] Intento con correo inexistente: {email}")
                return Response(
                    {
                        "success": False,
                        "message": "El correo ingresado no está registrado en el sistema."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            #  Crear token de recuperación
            reset_token = EmailVerificationToken.create_for_user(user)

            reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/?token={reset_token.token}"

            # Contexto para el template del email
            email_context = {
                "user_name": user.get_full_name() or user.username,
                "user_email": user.email,
                "token": str(reset_token.token),
                "reset_url": reset_url,
                "token_expiry_hours": 24,
                "current_year": timezone.now().year,
            }

            # Enviar correo
            email_result = send_email_notification(
                user_email=user.email,
                notification_type="password_reset",
                context=email_context,
            )

            if email_result.get("success"):
                logger.info(f"[FORGOT_PASSWORD] Email de recuperación enviado a {email}")
                return Response(
                    {
                        "success": True,
                        "message": f"Se enviaron instrucciones de recuperación a {email}."
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                logger.error(f"[FORGOT_PASSWORD] Fallo envío a {email}: {email_result.get('error')}")
                return Response(
                    {
                        "success": False,
                        "message": "Error al enviar el correo. Intente nuevamente más tarde."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            logger.error(f"[FORGOT_PASSWORD] Error interno: {e}", exc_info=True)
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordView(APIView):
    """
    Paso 2: Restablecer la contraseña con el token recibido.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Restablece la contraseña usando el token de recuperación",
        operation_summary="Restablecer contraseña",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['token', 'new_password', 'confirm_password']
        ),
        responses={
            200: openapi.Response(
                description="Contraseña restablecida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Restablecer contraseña con token.
        """
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all([token, new_password, confirm_password]):
            return Response({"success": False, "message": "Datos incompletos."}, status=400)

        if new_password != confirm_password:
            return Response({"success": False, "message": "Las contraseñas no coinciden."}, status=400)

        if len(new_password) < 8:
            return Response({"success": False, "message": "La contraseña debe tener al menos 8 caracteres."}, status=400)

        # Validar token
        token_obj = EmailVerificationToken.get_valid_token(token)
        if not token_obj:
            return Response({"success": False, "message": "El enlace no es válido o ha expirado."}, status=400)

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        # Eliminar token para evitar reutilización
        token_obj.delete()

        # Enviar correo de confirmación
        ctx = {
            "user_name": user.get_full_name() or user.username,
            "user_email": user.email,
            "reset_url": f"{settings.FRONTEND_URL}/auth/login",
            "current_year": timezone.now().year,
        }
        
        # Enviar email de confirmación (no bloquea si falla)
        try:
            send_email_notification(user.email, "password_reset_success", ctx)
        except Exception as e:
            logger.error(f"[ERROR] No se pudo enviar email de confirmación: {e}")

        return Response({
            "success": True,
            "message": "Contraseña restablecida correctamente."
        }, status=200)

