"""
Vistas refactorizadas usando servicios para CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import auth_service, analysis_service, image_service, finca_service, lote_service, report_service
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    ErrorResponseSerializer
)
from .utils import create_error_response, create_success_response

logger = logging.getLogger("cacaoscan.api")


class LoginView(APIView):
    """
    Endpoint para login de usuario usando servicios.
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
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Autentica un usuario usando el servicio de autenticaciÃ³n.
        """
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                message="Datos de login invÃ¡lidos",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar servicio de autenticaciÃ³n
        result = auth_service.login_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            request=request
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class RegisterView(APIView):
    """
    Endpoint para registro de usuario usando servicios.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registra un nuevo usuario en el sistema",
        operation_summary="Registro de usuario",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Usuario registrado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Registra un nuevo usuario usando el servicio de autenticaciÃ³n.
        """
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                message="Datos de registro invÃ¡lidos",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar servicio de autenticaciÃ³n
        result = auth_service.register_user(
            user_data=serializer.validated_data,
            request=request
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """
    Endpoint para logout de usuario usando servicios.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Cierra sesiÃ³n del usuario actual",
        operation_summary="Logout de usuario",
        responses={
            200: openapi.Response(
                description="Logout exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Cierra sesiÃ³n del usuario usando el servicio de autenticaciÃ³n.
        """
        refresh_token = request.data.get('refresh_token')
        
        result = auth_service.logout_user(
            user=request.user,
            refresh_token=refresh_token
        )
        
        if result.success:
            return create_success_response(
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class RefreshTokenView(APIView):
    """
    Endpoint para refrescar token usando servicios.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Refresca un token de acceso usando el token de refresh",
        operation_summary="Refrescar token",
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
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Refresca un token usando el servicio de autenticaciÃ³n.
        """
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return create_error_response(
                message="Token de refresh requerido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = auth_service.refresh_token(refresh_token)
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmailView(APIView):
    """
    Endpoint para verificar email usando servicios.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica un email usando token de verificaciÃ³n",
        operation_summary="Verificar email",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Email verificado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Verifica un email usando el servicio de autenticaciÃ³n.
        """
        serializer = EmailVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                message="Datos de verificaciÃ³n invÃ¡lidos",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = auth_service.verify_email(
            token=serializer.validated_data['token']
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(APIView):
    """
    Endpoint para reenviar verificaciÃ³n usando servicios.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="ReenvÃ­a token de verificaciÃ³n de email",
        operation_summary="Reenviar verificaciÃ³n",
        request_body=ResendVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Token de verificaciÃ³n reenviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        ReenvÃ­a verificaciÃ³n usando el servicio de autenticaciÃ³n.
        """
        serializer = ResendVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                message="Datos de reenvÃ­o invÃ¡lidos",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = auth_service.resend_verification(
            email=serializer.validated_data['email']
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordView(APIView):
    """
    Endpoint para solicitar restablecimiento de contraseÃ±a usando servicios.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Solicita restablecimiento de contraseÃ±a",
        operation_summary="OlvidÃ© mi contraseÃ±a",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
            },
            required=['email']
        ),
        responses={
            200: openapi.Response(
                description="Instrucciones enviadas",
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
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Solicita restablecimiento usando el servicio de autenticaciÃ³n.
        """
        email = request.data.get('email')
        
        if not email:
            return create_error_response(
                message="Email es requerido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = auth_service.forgot_password(
            email=email,
            request=request
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    """
    Endpoint para restablecer contraseÃ±a usando servicios.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Restablece contraseÃ±a usando token",
        operation_summary="Restablecer contraseÃ±a",
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
                description="ContraseÃ±a restablecida",
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
        tags=['AutenticaciÃ³n']
    )
    def post(self, request):
        """
        Restablece contraseÃ±a usando el servicio de autenticaciÃ³n.
        """
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([token, new_password, confirm_password]):
            return create_error_response(
                message="Token, nueva contraseÃ±a y confirmaciÃ³n son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = auth_service.reset_password(
            token=token,
            new_password=new_password,
            confirm_password=confirm_password
        )
        
        if result.success:
            return create_success_response(
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """
    Endpoint para obtener y actualizar perfil de usuario usando servicios.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el perfil del usuario actual",
        operation_summary="Obtener perfil",
        responses={
            200: openapi.Response(
                description="Perfil obtenido exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Usuario']
    )
    def get(self, request):
        """
        Obtiene el perfil del usuario usando el servicio de autenticaciÃ³n.
        """
        result = auth_service.get_user_profile(user=request.user)
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Actualiza el perfil del usuario actual",
        operation_summary="Actualizar perfil",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
            }
        ),
        responses={
            200: openapi.Response(
                description="Perfil actualizado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Usuario']
    )
    def put(self, request):
        """
        Actualiza el perfil del usuario usando el servicio de autenticaciÃ³n.
        """
        result = auth_service.update_user_profile(
            user=request.user,
            profile_data=request.data
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# VISTAS DE ANÃLISIS REFACTORIZADAS
# ============================================================================

class ScanMeasureView(APIView):
    """
    Endpoint para anÃ¡lisis de granos de cacao usando servicios.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Analiza un grano de cacao desde una imagen",
        operation_summary="Analizar grano de cacao",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Imagen del grano de cacao",
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="AnÃ¡lisis completado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['AnÃ¡lisis']
    )
    def post(self, request):
        """
        Analiza un grano de cacao usando el servicio de anÃ¡lisis.
        """
        image_file = request.FILES.get('image')
        
        if not image_file:
            return create_error_response(
                message="Imagen es requerida",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = analysis_service.analyze_cacao_grain(
            image_file=image_file,
            user=request.user
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class AnalysisHistoryView(APIView):
    """
    Endpoint para obtener historial de anÃ¡lisis usando servicios.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el historial de anÃ¡lisis del usuario",
        operation_summary="Historial de anÃ¡lisis",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="NÃºmero de pÃ¡gina",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="TamaÃ±o de pÃ¡gina",
                type=openapi.TYPE_INTEGER,
                default=20
            ),
            openapi.Parameter(
                'date_from',
                openapi.IN_QUERY,
                description="Fecha de inicio (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'date_to',
                openapi.IN_QUERY,
                description="Fecha de fin (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'min_confidence',
                openapi.IN_QUERY,
                description="Confianza mÃ­nima",
                type=openapi.TYPE_NUMBER,
                format=openapi.FORMAT_FLOAT
            )
        ],
        responses={
            200: openapi.Response(
                description="Historial obtenido exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['AnÃ¡lisis']
    )
    def get(self, request):
        """
        Obtiene el historial de anÃ¡lisis usando el servicio de anÃ¡lisis.
        """
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        filters = {}
        if request.GET.get('date_from'):
            filters['date_from'] = request.GET.get('date_from')
        if request.GET.get('date_to'):
            filters['date_to'] = request.GET.get('date_to')
        if request.GET.get('min_confidence'):
            filters['min_confidence'] = float(request.GET.get('min_confidence'))
        if request.GET.get('max_confidence'):
            filters['max_confidence'] = float(request.GET.get('max_confidence'))
        
        result = analysis_service.get_analysis_history(
            user=request.user,
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class AnalysisDetailView(APIView):
    """
    Endpoint para obtener detalles de un anÃ¡lisis especÃ­fico usando servicios.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene detalles de un anÃ¡lisis especÃ­fico",
        operation_summary="Detalles de anÃ¡lisis",
        responses={
            200: openapi.Response(
                description="Detalles obtenidos exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['AnÃ¡lisis']
    )
    def get(self, request, analysis_id):
        """
        Obtiene detalles de un anÃ¡lisis usando el servicio de anÃ¡lisis.
        """
        result = analysis_service.get_analysis_details(
            analysis_id=int(analysis_id),
            user=request.user
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            status_code = status.HTTP_404_NOT_FOUND if result.error.error_code == 'not_found' else status.HTTP_400_BAD_REQUEST
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status_code
            )


class AnalysisDeleteView(APIView):
    """
    Endpoint para eliminar un anÃ¡lisis usando servicios.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina un anÃ¡lisis especÃ­fico",
        operation_summary="Eliminar anÃ¡lisis",
        responses={
            200: openapi.Response(
                description="AnÃ¡lisis eliminado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['AnÃ¡lisis']
    )
    def delete(self, request, analysis_id):
        """
        Elimina un anÃ¡lisis usando el servicio de anÃ¡lisis.
        """
        result = analysis_service.delete_analysis(
            analysis_id=int(analysis_id),
            user=request.user
        )
        
        if result.success:
            return create_success_response(
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            status_code = status.HTTP_404_NOT_FOUND if result.error.error_code == 'not_found' else status.HTTP_400_BAD_REQUEST
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status_code
            )


class AnalysisStatsView(APIView):
    """
    Endpoint para obtener estadÃ­sticas de anÃ¡lisis usando servicios.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadÃ­sticas de anÃ¡lisis del usuario",
        operation_summary="EstadÃ­sticas de anÃ¡lisis",
        manual_parameters=[
            openapi.Parameter(
                'date_from',
                openapi.IN_QUERY,
                description="Fecha de inicio (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'date_to',
                openapi.IN_QUERY,
                description="Fecha de fin (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            )
        ],
        responses={
            200: openapi.Response(
                description="EstadÃ­sticas obtenidas exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['AnÃ¡lisis']
    )
    def get(self, request):
        """
        Obtiene estadÃ­sticas de anÃ¡lisis usando el servicio de anÃ¡lisis.
        """
        filters = {}
        if request.GET.get('date_from'):
            filters['date_from'] = request.GET.get('date_from')
        if request.GET.get('date_to'):
            filters['date_to'] = request.GET.get('date_to')
        
        result = analysis_service.get_analysis_statistics(
            user=request.user,
            filters=filters
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_400_BAD_REQUEST
            )


