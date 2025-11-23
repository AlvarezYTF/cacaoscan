"""
Email verification views for CacaoScan API.
"""
import logging
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model

from api.serializers import (
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserSerializer,
    ErrorResponseSerializer
)
from core.utils import create_error_response, create_success_response
from api.utils.model_imports import get_model_safely

User = get_user_model()
EmailVerificationToken = get_model_safely('auth_app.models.EmailVerificationToken')
logger = logging.getLogger("cacaoscan.api.auth")


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
                from api.services.email import send_custom_email
                
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

