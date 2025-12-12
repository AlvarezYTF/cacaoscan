"""
Password views for CacaoScan API.
"""
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import ErrorResponseSerializer
from core.utils import create_error_response, create_success_response
from api.services.email import send_email_notification
from api.utils.model_imports import get_model_safely

User = get_user_model()
EmailVerificationToken = get_model_safely('auth_app.models.EmailVerificationToken')
logger = logging.getLogger("cacaoscan.api.auth")


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
        from api.serializers import ChangePasswordSerializer
        
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Verificar si el usuario es Google-only (no permite contraseñas locales)
            login_provider = 'local'
            try:
                if hasattr(user, 'auth_profile') and user.auth_profile:
                    login_provider = user.auth_profile.login_provider
            except Exception:
                pass
            
            if login_provider == 'google':
                return create_error_response(
                    message='Tu cuenta solo permite inicio de sesión con Google.',
                    error_type='google_account_no_password',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={'old_password': ['Esta cuenta solo permite autenticación con Google.']}
                )
            
            # Verificar que el usuario tenga una contraseña usable antes de validar la actual
            if not user.has_usable_password():
                return create_error_response(
                    message='Esta cuenta fue creada mediante Google. Debes crear una contraseña antes de poder cambiarla.',
                    error_type='no_usable_password',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={'old_password': ['Esta cuenta no tiene contraseña local. Usa el endpoint de crear contraseña.']}
                )
            
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
            try:
                email_result = send_email_notification(
                    user_email=user.email,
                    notification_type="reset_request",
                    context=email_context,
                )

                if email_result and email_result.get("success"):
                    logger.info(f"[FORGOT_PASSWORD] Email de recuperación enviado a {email}")
                    return Response(
                        {
                            "success": True,
                            "message": f"Se enviaron instrucciones de recuperación a {email}."
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    error_msg = email_result.get('error', 'Error desconocido') if email_result else 'No se recibió respuesta del servicio de email'
                    logger.error(f"[FORGOT_PASSWORD] Fallo envío a {email}: {error_msg}")
                    return Response(
                        {
                            "success": False,
                            "message": "Error al enviar el correo. Verifique la configuración del servidor de correo o intente nuevamente más tarde.",
                            "error_details": error_msg if settings.DEBUG else None
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            except Exception as email_error:
                logger.error(f"[FORGOT_PASSWORD] Excepción al enviar email a {email}: {email_error}", exc_info=True)
                return Response(
                    {
                        "success": False,
                        "message": "Error al enviar el correo. Verifique la configuración del servidor de correo.",
                        "error_details": str(email_error) if settings.DEBUG else None
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

        # Validate password using centralized validator
        try:
            from core.utils import validate_password_strength, validate_passwords_match
            validate_password_strength(new_password)
            validate_passwords_match(new_password, confirm_password)
        except serializers.ValidationError as e:
            if isinstance(e, str):
                error_message = str(e)
            elif hasattr(e, 'detail'):
                error_message = e.detail.get('confirm_password', [str(e)])[0]
            else:
                error_message = str(e)
            return Response({"success": False, "message": error_message}, status=400)

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
            send_email_notification(user.email, "reset_confirmation", ctx)
        except Exception as e:
            logger.error(f"[ERROR] No se pudo enviar email de confirmación: {e}")

        return Response({
            "success": True,
            "message": "Contraseña restablecida correctamente."
        }, status=200)


class SetPasswordView(APIView):
    """
    Endpoint para crear una contraseña local para usuarios creados con Google.
    Solo usuarios autenticados pueden usarlo.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Crea una contraseña local para usuarios creados con Google OAuth",
        operation_summary="Crear contraseña local",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Nueva contraseña (mínimo 8 caracteres)'
                ),
                'confirm_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Confirmación de la nueva contraseña'
                )
            },
            required=['password', 'confirm_password']
        ),
        responses={
            200: openapi.Response(
                description="Contraseña creada exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'has_password': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Crea una contraseña local para el usuario autenticado.
        
        Solo funciona si el usuario NO tiene contraseña usable actualmente.
        """
        user = request.user
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        # Verificar si el usuario es Google-only (no permite contraseñas locales)
        login_provider = 'local'
        try:
            if hasattr(user, 'auth_profile') and user.auth_profile:
                login_provider = user.auth_profile.login_provider
        except Exception:
            pass
        
        if login_provider == 'google':
            return create_error_response(
                message='Tu cuenta solo permite inicio de sesión con Google.',
                error_type='google_account_no_password',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el usuario no tenga contraseña usable
        if user.has_usable_password():
            return create_error_response(
                message='Este usuario ya tiene una contraseña configurada. Use el endpoint de cambio de contraseña si desea actualizarla.',
                error_type='password_already_set',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Validar campos requeridos
        if not password or not confirm_password:
            return create_error_response(
                message='Se requieren los campos password y confirm_password',
                error_type='missing_fields',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar fortaleza de contraseña
        try:
            from core.utils import validate_password_strength, validate_passwords_match
            validate_password_strength(password)
            validate_passwords_match(password, confirm_password)
        except serializers.ValidationError as e:
            error_message = str(e)
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                # Extraer primer mensaje de error
                for field, messages in e.detail.items():
                    if messages:
                        error_message = messages[0] if isinstance(messages, list) else str(messages)
                        break
            return create_error_response(
                message=error_message,
                error_type='password_validation_error',
                status_code=status.HTTP_400_BAD_REQUEST,
                details={'field': 'password'}
            )
        except Exception as e:
            return create_error_response(
                message=f'Error al validar contraseña: {str(e)}',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Establecer la contraseña
        try:
            user.set_password(password)
            user.save()
            logger.info(f"Contraseña creada para usuario {user.username} (ID: {user.id})")
            
            return create_success_response(
                message='Password created successfully',
                data={
                    'status': 'success',
                    'has_password': True
                }
            )
        except Exception as e:
            logger.error(f"Error al crear contraseña para usuario {user.username}: {str(e)}", exc_info=True)
            return create_error_response(
                message='Error al crear la contraseña',
                error_type='internal_server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={'error': str(e)}
            )