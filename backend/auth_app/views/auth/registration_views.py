"""
Registration views for CacaoScan API.
"""
import logging
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model

from api.serializers import (
    RegisterSerializer,
    UserSerializer,
    ErrorResponseSerializer
)
from core.utils import create_error_response, create_success_response
from api.services.auth import RegistrationService

User = get_user_model()
logger = logging.getLogger("cacaoscan.api.auth")


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
            registration_service = RegistrationService()
            result = registration_service.register_user_with_email_verification(
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
        registration_service = RegistrationService()
        result = registration_service.pre_register_user(user_data, request)
        
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
        registration_service = RegistrationService()
        result = registration_service.verify_pre_registration_and_create_user(str(token))
        
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

