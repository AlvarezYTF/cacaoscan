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

        # Validate password using centralized validator
        try:
            from core.utils import validate_password_strength, validate_passwords_match
            validate_password_strength(new_password)
            validate_passwords_match(new_password, confirm_password)
        except serializers.ValidationError as e:
            error_message = str(e) if isinstance(e, str) else (e.detail.get('confirm_password', [str(e)])[0] if hasattr(e, 'detail') else str(e))
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
            send_email_notification(user.email, "password_reset_success", ctx)
        except Exception as e:
            logger.error(f"[ERROR] No se pudo enviar email de confirmación: {e}")

        return Response({
            "success": True,
            "message": "Contraseña restablecida correctamente."
        }, status=200)

