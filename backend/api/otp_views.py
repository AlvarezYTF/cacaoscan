"""
Vistas para verificaciÃ³n OTP por email en CacaoScan.
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

from .serializers import SendOtpSerializer, VerifyOtpSerializer, ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.auth")


class SendOtpView(APIView):
    """
    Endpoint para enviar cÃ³digo OTP de verificaciÃ³n de email.
    """
    permission_classes = [AllowAny]
    serializer_class = SendOtpSerializer
    
    @swagger_auto_schema(
        operation_description="EnvÃ­a un cÃ³digo OTP de 6 dÃ­gitos al correo especificado",
        operation_summary="Enviar cÃ³digo OTP",
        request_body=SendOtpSerializer,
        responses={
            200: openapi.Response(description="CÃ³digo OTP enviado exitosamente"),
            400: ErrorResponseSerializer,
            429: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n OTP']
    )
    def post(self, request):
        """EnvÃ­a un cÃ³digo OTP al correo especificado."""
        try:
            serializer = SendOtpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            temp_data = serializer.validated_data.get('temp_data') or request.data
            
            # Importar aquÃ­ para evitar importaciones circulares
            from auth_app.models import PendingEmailVerification
            
            # Control de reenvÃ­o (60 segundos)
            existing = PendingEmailVerification.objects.filter(email=email).first()
            if existing:
                time_since_last_sent = (timezone.now() - existing.last_sent).total_seconds()
                if time_since_last_sent < 60:
                    remaining = int(60 - time_since_last_sent)
                    return Response({
                        'error': f'Espera {remaining} segundos antes de reenviar el cÃ³digo.',
                        'status': 'error'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Generar cÃ³digo OTP
            code = PendingEmailVerification.generate_code()
            
            # Crear o actualizar registro de verificaciÃ³n
            verification, created = PendingEmailVerification.objects.update_or_create(
                email=email,
                defaults={'otp_code': code, 'temp_data': temp_data}
            )
            
            # Enviar email con cÃ³digo OTP usando el servicio de emails
            from api.email_service import email_service
            
            # Enviar email con contenido HTML
            email_result = email_service.send_email(
                to_emails=[email],
                subject='VerificaciÃ³n de cuenta CacaoScan',
                html_content=f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #22c55e;">VerificaciÃ³n de cuenta CacaoScan</h2>
                        <p>Hola ðŸ‘‹,</p>
                        <p>Tu cÃ³digo de verificaciÃ³n es:</p>
                        <div style="background-color: #f3f4f6; border: 2px solid #22c55e; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #22c55e; font-size: 32px; margin: 0; letter-spacing: 5px;">{code}</h1>
                        </div>
                        <p>Este cÃ³digo expirarÃ¡ en <strong>10 minutos</strong>.</p>
                        <p style="color: #6b7280; font-size: 14px;">Si no solicitaste este cÃ³digo, puedes ignorar este email.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">Â© {timezone.now().year} CacaoScan - Sistema de anÃ¡lisis de cacao</p>
                    </div>
                </body>
                </html>
                """,
                text_content=f"Hola, tu cÃ³digo de verificaciÃ³n es: {code}. Este cÃ³digo expirarÃ¡ en 10 minutos."
            )
            
            if email_result['success']:
                logger.info(f"CÃ³digo OTP {code} enviado a {email}")
                return Response({
                    'success': True,
                    'message': 'CÃ³digo enviado con Ã©xito al correo.',
                    'email': email
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error enviando cÃ³digo OTP a {email}: {email_result.get('error')}")
                return Response({
                    'error': 'Error al enviar el cÃ³digo. Por favor intenta de nuevo.',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except serializers.ValidationError as e:
            logger.error(f"Error de validaciÃ³n en send-otp: {e}")
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
    Endpoint para verificar cÃ³digo OTP y activar cuenta de usuario.
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyOtpSerializer
    
    @swagger_auto_schema(
        operation_description="Verifica el cÃ³digo OTP y activa la cuenta del usuario",
        operation_summary="Verificar cÃ³digo OTP",
        request_body=VerifyOtpSerializer,
        responses={
            201: openapi.Response(description="Cuenta verificada y activada exitosamente"),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n OTP']
    )
    def post(self, request):
        """Verifica el cÃ³digo OTP y activa la cuenta."""
        try:
            serializer = VerifyOtpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            # Importar aquÃ­ para evitar importaciones circulares
            from auth_app.models import PendingEmailVerification
            
            # Buscar verificaciÃ³n pendiente
            verification = PendingEmailVerification.objects.filter(email=email).first()
            
            if not verification:
                return Response({
                    'error': 'No se encontrÃ³ un cÃ³digo para este correo.',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar expiraciÃ³n
            if verification.is_expired():
                verification.delete()
                return Response({
                    'error': 'El cÃ³digo ha expirado. Solicita uno nuevo.',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar cÃ³digo
            if verification.otp_code != code:
                return Response({
                    'error': 'CÃ³digo incorrecto.',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            User = get_user_model()

            # Si ya existe, idempotencia: borrar pending y confirmar
            if User.objects.filter(email=email).exists():
                verification.delete()
                return Response({
                    'success': True,
                    'message': 'El email ya estÃ¡ verificado y registrado.'
                }, status=status.HTTP_200_OK)

            # Crear usuario/persona desde temp_data de forma atÃ³mica
            data = verification.temp_data or {}
            password = data.get('password')
            first_name = data.get('primer_nombre') or data.get('first_name') or ''
            last_name = data.get('primer_apellido') or data.get('last_name') or ''

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        is_active=True,
                    )

                    # Marcar verificado si aplica
                    if hasattr(user, 'auth_email_token'):
                        user.auth_email_token.is_verified = True
                        user.auth_email_token.verified_at = timezone.now()
                        user.auth_email_token.save()

                    # Crear Persona si el modelo existe
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

                    # Asignar rol por defecto si existe helper
                    try:
                        from core.utils.responses import assign_default_role  # placeholder si existe
                        assign_default_role(user, role='farmer')
                    except Exception:
                        pass

                    # Limpiar pending
                    verification.delete()

                return Response({
                    'success': True,
                    'message': 'Cuenta verificada y creada. Ahora puedes iniciar sesiÃ³n.',
                    'user': {
                        'email': email,
                        'username': user.username,
                        'is_active': user.is_active
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creando usuario/persona desde OTP: {e}")
                return Response({
                    'error': 'No se pudo crear la cuenta. Intenta nuevamente.',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except serializers.ValidationError as e:
            logger.error(f"Error de validaciÃ³n en verify-otp: {e}")
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



