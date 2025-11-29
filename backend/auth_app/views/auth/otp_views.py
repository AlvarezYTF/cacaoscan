"""
Vistas para verificación OTP por email en CacaoScan.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import SendOtpSerializer, VerifyOtpSerializer, ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.auth")


class SendOtpView(APIView):
    """
    Endpoint para enviar código OTP de verificación de email.
    """
    permission_classes = [AllowAny]
    serializer_class = SendOtpSerializer
    
    @swagger_auto_schema(
        operation_description="Envía un código OTP de 6 dígitos al correo especificado",
        operation_summary="Enviar código OTP",
        request_body=SendOtpSerializer,
        responses={
            200: openapi.Response(description="Código OTP enviado exitosamente"),
            400: ErrorResponseSerializer,
            429: ErrorResponseSerializer,
        },
        tags=['Autenticación OTP']
    )
    def post(self, request):
        """Envía un código OTP al correo especificado."""
        try:
            serializer = SendOtpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            temp_data = serializer.validated_data.get('temp_data') or request.data
            
            # Importar aquí para evitar importaciones circulares
            from auth_app.models import PendingEmailVerification
            
            # Control de reenvío (60 segundos)
            existing = PendingEmailVerification.objects.filter(email=email).first()
            if existing:
                time_since_last_sent = (timezone.now() - existing.last_sent).total_seconds()
                if time_since_last_sent < 60:
                    remaining = int(60 - time_since_last_sent)
                    return Response({
                        'error': f'Espera {remaining} segundos antes de reenviar el código.',
                        'status': 'error'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Generar código OTP
            code = PendingEmailVerification.generate_code()
            
            # Crear o actualizar registro de verificación
            _, _ = PendingEmailVerification.objects.update_or_create(
                email=email,
                defaults={'otp_code': code, 'temp_data': temp_data}
            )
            
            # Enviar email con código OTP usando el servicio de emails
            from api.services.email import email_service
            
            # Enviar email con contenido HTML
            email_result = email_service.send_email(
                to_emails=[email],
                subject='Verificación de cuenta CacaoScan',
                html_content=f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #22c55e;">Verificación de cuenta CacaoScan</h2>
                        <p>Hola ',</p>
                        <p>Tu código de verificación es:</p>
                        <div style="background-color: #f3f4f6; border: 2px solid #22c55e; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #22c55e; font-size: 32px; margin: 0; letter-spacing: 5px;">{code}</h1>
                        </div>
                        <p>Este código expirará en <strong>10 minutos</strong>.</p>
                        <p style="color: #6b7280; font-size: 14px;">Si no solicitaste este código, puedes ignorar este email.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">é {timezone.now().year} CacaoScan - Sistema de análisis de cacao</p>
                    </div>
                </body>
                </html>
                """,
                text_content=f"Hola, tu código de verificación es: {code}. Este código expirará en 10 minutos."
            )
            
            if email_result['success']:
                logger.info(f"Código OTP {code} enviado a {email}")
                return Response({
                    'success': True,
                    'message': 'Código enviado con éxito al correo.',
                    'email': email
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error enviando código OTP a {email}: {email_result.get('error')}")
                return Response({
                    'error': 'Error al enviar el código. Por favor intenta de nuevo.',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except serializers.ValidationError as e:
            logger.error(f"Error de validación en send-otp: {e}")
            return Response({
                'error': str(e),
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado en send-otp: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOtpView(APIView):
    """
    Endpoint para verificar código OTP y activar cuenta de usuario.
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyOtpSerializer
    
    @swagger_auto_schema(
        operation_description="Verifica el código OTP y activa la cuenta del usuario",
        operation_summary="Verificar código OTP",
        request_body=VerifyOtpSerializer,
        responses={
            201: openapi.Response(description="Cuenta verificada y activada exitosamente"),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Autenticación OTP']
    )
    def _validate_otp_request(self, request):
        """Valida la solicitud OTP."""
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['email'], serializer.validated_data['code']
    
    def _get_verification(self, email: str):
        """Obtiene la verificación pendiente."""
        from auth_app.models import PendingEmailVerification
        verification = PendingEmailVerification.objects.filter(email=email).first()
        
        if not verification:
            return None, Response({
                'error': 'No se encontró un código para este correo.',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if verification.is_expired():
            verification.delete()
            return None, Response({
                'error': 'El código ha expirado. Solicita uno nuevo.',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return verification, None
    
    def _verify_otp_code(self, verification, code: str):
        """Verifica el código OTP."""
        if verification.otp_code != code:
            return Response({
                'error': 'Código incorrecto.',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        return None
    
    def _check_existing_user(self, email: str, verification):
        """Verifica si el usuario ya existe."""
        user_model = get_user_model()
        if user_model.objects.filter(email=email).exists():
            verification.delete()
            return Response({
                'success': True,
                'message': 'El email ya está verificado y registrado.'
            }, status=status.HTTP_200_OK)
        return None
    
    def _create_persona(self, user, data: dict):
        """Crea el registro de Persona si el modelo existe."""
        try:
            from personas.models import Persona
            Persona.objects.create(
                user=user,
                tipo_documento=data.get('tipo_documento') or data.get('tipoDocumento'),
                numero_documento=data.get('numero_documento') or data.get('numeroDocumento'),
                genero=data.get('genero'),
                telefono=data.get('telefono') or data.get('phone_number'),
                fecha_nacimiento=data.get('fecha_nacimiento') or data.get('fechaNacimiento'),
                departamento=data.get('departamento') or data.get('departamento_codigo'),
                municipio=data.get('municipio') or data.get('municipio_codigo'),
                direccion=data.get('direccion'),
            )
        except Exception:
            pass
    
    def _assign_default_role(self, user):
        """Asigna el rol por defecto si existe helper."""
        try:
            from users.signals import assign_default_role
            assign_default_role(None, user, created=True)
        except ImportError:
            pass
    
    def _create_user_from_verification(self, verification, email: str):
        """Crea el usuario desde la verificación."""
        user_model = get_user_model()
        data = verification.temp_data or {}
        password = data.get('password')
        first_name = data.get('primer_nombre') or data.get('first_name') or ''
        last_name = data.get('primer_apellido') or data.get('last_name') or ''
        
        with transaction.atomic():
            user = user_model.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
            
            if hasattr(user, 'auth_email_token'):
                user.auth_email_token.is_verified = True
                user.auth_email_token.verified_at = timezone.now()
                user.auth_email_token.save()
            
            self._create_persona(user, data)
            self._assign_default_role(user)
            verification.delete()
            
            return user
    
    def post(self, request):
        """Verifica el código OTP y activa la cuenta."""
        try:
            email, code = self._validate_otp_request(request)
            
            verification, error_response = self._get_verification(email)
            if error_response:
                return error_response
            
            error_response = self._verify_otp_code(verification, code)
            if error_response:
                return error_response
            
            user_model = get_user_model()
            existing_response = self._check_existing_user(email, verification)
            if existing_response:
                return existing_response
            
            user = self._create_user_from_verification(verification, email)

            return Response({
                'success': True,
                'message': 'Cuenta verificada y creada. Ahora puedes iniciar sesión.',
                'user': {
                    'email': email,
                    'username': user.username,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_201_CREATED)
                
        except serializers.ValidationError as e:
            logger.error(f"Error de validación en verify-otp: {e}")
            return Response({
                'error': str(e),
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado en verify-otp: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



