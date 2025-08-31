"""
Vistas adicionales de autenticación para CacaoScan.

Incluye funcionalidades de restablecimiento de contraseña,
verificación de email y gestión avanzada de usuarios.
"""

import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User

# Configurar logging
logger = logging.getLogger(__name__)


class UserPasswordResetView(APIView):
    """
    Vista para solicitar restablecimiento de contraseña.
    
    Permite que usuarios olviden su contraseña y reciban
    un enlace de restablecimiento por email.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Solicitar restablecimiento de contraseña por email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')
            }
        ),
        responses={
            200: openapi.Response("Email de restablecimiento enviado"),
            400: openapi.Response("Email no encontrado")
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """Envía email de restablecimiento de contraseña."""
        try:
            email = request.data.get('email')
            
            if not email:
                return Response({
                    'success': False,
                    'error': 'Email requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                # Por seguridad, siempre respondemos success
                return Response({
                    'success': True,
                    'message': 'Si el email existe, recibirás instrucciones de restablecimiento'
                })
            
            # Generar token de restablecimiento
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # TODO: Enviar email con enlace de restablecimiento
            # Por ahora solo registramos la solicitud
            logger.info(f"Password reset solicitado para: {email}")
            
            return Response({
                'success': True,
                'message': 'Si el email existe, recibirás instrucciones de restablecimiento',
                'reset_info': {  # Solo para desarrollo
                    'uid': uid,
                    'token': token
                }
            })
            
        except Exception as e:
            logger.error(f"Error en password reset: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPasswordResetConfirmView(APIView):
    """
    Vista para confirmar restablecimiento de contraseña.
    
    Permite que usuarios establezcan nueva contraseña
    usando token de restablecimiento.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Confirmar restablecimiento con nueva contraseña",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['uid', 'token', 'new_password'],
            properties={
                'uid': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("Contraseña restablecida exitosamente"),
            400: openapi.Response("Token inválido o expirado")
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """Confirma restablecimiento de contraseña."""
        try:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_str
            from django.utils.http import urlsafe_base64_decode
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError
            
            uid = request.data.get('uid')
            token = request.data.get('token')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            
            if not all([uid, token, new_password]):
                return Response({
                    'success': False,
                    'error': 'UID, token y nueva contraseña son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if new_password != confirm_password:
                return Response({
                    'success': False,
                    'error': 'Las contraseñas no coinciden'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar contraseña
            try:
                validate_password(new_password)
            except ValidationError as e:
                return Response({
                    'success': False,
                    'errors': list(e.messages)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Decodificar UID y obtener usuario
            try:
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'success': False,
                    'error': 'Token inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar token
            if not default_token_generator.check_token(user, token):
                return Response({
                    'success': False,
                    'error': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Establecer nueva contraseña
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Password reset confirmado para: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Contraseña restablecida exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error en password reset confirm: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserEmailVerificationView(APIView):
    """
    Vista para verificación de email de usuario.
    
    Permite que usuarios verifiquen su cuenta
    usando token enviado por email.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verificar email de usuario con token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['uid', 'token'],
            properties={
                'uid': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("Email verificado exitosamente"),
            400: openapi.Response("Token inválido o expirado")
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """Verifica email del usuario."""
        try:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_str
            from django.utils.http import urlsafe_base64_decode
            
            uid = request.data.get('uid')
            token = request.data.get('token')
            
            if not all([uid, token]):
                return Response({
                    'success': False,
                    'error': 'UID y token son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Decodificar UID y obtener usuario
            try:
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'success': False,
                    'error': 'Token inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar token
            if not default_token_generator.check_token(user, token):
                return Response({
                    'success': False,
                    'error': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar usuario
            if user.is_verified:
                return Response({
                    'success': True,
                    'message': 'El email ya estaba verificado'
                })
            
            user.is_verified = True
            user.save()
            
            logger.info(f"Email verificado para: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Email verificado exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error en email verification: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendVerificationEmailView(APIView):
    """
    Vista para reenviar email de verificación.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Reenviar email de verificación",
        responses={
            200: openapi.Response("Email de verificación reenviado"),
            400: openapi.Response("Email ya verificado")
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """Reenvía email de verificación al usuario autenticado."""
        try:
            user = request.user
            
            if user.is_verified:
                return Response({
                    'success': False,
                    'error': 'El email ya está verificado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar token de verificación
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # TODO: Enviar email de verificación
            # Por ahora solo registramos la solicitud
            logger.info(f"Verification email reenviado para: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Email de verificación enviado',
                'verification_info': {  # Solo para desarrollo
                    'uid': uid,
                    'token': token
                }
            })
            
        except Exception as e:
            logger.error(f"Error en resend verification: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStatsView(APIView):
    """
    Vista para estadísticas de usuarios (solo administradores).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas de usuarios (solo admin)",
        responses={
            200: openapi.Response(
                "Estadísticas de usuarios",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'by_role': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'recent_registrations': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            403: openapi.Response("Permisos insuficientes")
        },
        tags=['Usuario']
    )
    def get(self, request):
        """Obtiene estadísticas de usuarios (solo administradores)."""
        if not request.user.is_admin_user:
            return Response({
                'error': 'Permisos insuficientes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Estadísticas básicas
        total_users = User.objects.count()
        
        # Por rol
        by_role = {}
        for role_code, role_name in User.ROLE_CHOICES:
            by_role[role_code] = User.objects.filter(role=role_code).count()
        
        # Registros recientes (última semana)
        week_ago = timezone.now() - timedelta(days=7)
        recent_registrations = User.objects.filter(
            date_joined__gte=week_ago
        ).count()
        
        # Usuarios activos
        active_users = User.objects.filter(is_active=True).count()
        
        # Usuarios verificados
        verified_users = User.objects.filter(is_verified=True).count()
        
        # Por región
        from django.db.models import Count
        by_region = dict(
            User.objects.select_related('profile')
            .exclude(profile__region='')
            .values('profile__region')
            .annotate(count=Count('id'))
            .values_list('profile__region', 'count')
        )
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'by_role': by_role,
            'by_region': by_region,
            'recent_registrations': recent_registrations,
            'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0,
            'activity_rate': (active_users / total_users * 100) if total_users > 0 else 0,
        })


class UserBulkActionsView(APIView):
    """
    Vista para acciones masivas de usuarios (solo administradores).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Realizar acciones masivas en usuarios",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_ids', 'action'],
            properties={
                'user_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                ),
                'action': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['activate', 'deactivate', 'verify', 'unverify']
                ),
            }
        ),
        responses={
            200: openapi.Response("Acción realizada exitosamente"),
            403: openapi.Response("Permisos insuficientes")
        },
        tags=['Usuario']
    )
    def post(self, request):
        """Realiza acciones masivas en usuarios."""
        if not request.user.is_admin_user:
            return Response({
                'error': 'Permisos insuficientes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_ids = request.data.get('user_ids', [])
            action = request.data.get('action')
            
            if not user_ids or not action:
                return Response({
                    'success': False,
                    'error': 'user_ids y action son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar acción
            valid_actions = ['activate', 'deactivate', 'verify', 'unverify']
            if action not in valid_actions:
                return Response({
                    'success': False,
                    'error': f'Acción inválida. Válidas: {valid_actions}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener usuarios
            users = User.objects.filter(id__in=user_ids)
            
            if not users.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron usuarios'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Aplicar acción
            count = 0
            for user in users:
                # No permitir acciones en superusuarios
                if user.is_superuser and user.id != request.user.id:
                    continue
                
                if action == 'activate':
                    user.is_active = True
                elif action == 'deactivate':
                    user.is_active = False
                elif action == 'verify':
                    user.is_verified = True
                elif action == 'unverify':
                    user.is_verified = False
                
                user.save()
                count += 1
            
            logger.info(f"Acción masiva '{action}' aplicada a {count} usuarios por {request.user.email}")
            
            return Response({
                'success': True,
                'message': f'Acción "{action}" aplicada a {count} usuarios',
                'affected_users': count
            })
            
        except Exception as e:
            logger.error(f"Error en bulk actions: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
