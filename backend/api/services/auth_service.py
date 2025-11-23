"""
Servicio de autenticación para CacaoScan.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from .base import BaseService, ServiceResult, ValidationServiceError, PermissionServiceError
from ..utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'EmailVerificationToken': 'auth_app.models.EmailVerificationToken',
    'UserProfile': 'auth_app.models.UserProfile',
    'ActivityLog': 'audit.models.ActivityLog'
})
EmailVerificationToken = models['EmailVerificationToken']
UserProfile = models['UserProfile']
ActivityLog = models['ActivityLog']

from ..models import LoginHistory

logger = logging.getLogger("cacaoscan.services.auth")


class AuthenticationService(BaseService):
    """
    Servicio para manejar autenticación de usuarios.
    """
    
    def __init__(self):
        super().__init__()
    
    def login_user(self, username: str, password: str, request=None) -> ServiceResult:
        """
        Autentica un usuario y genera tokens JWT.
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña
            request: Request object para obtener IP y user agent
            
        Returns:
            ServiceResult con tokens y datos del usuario
        """
        try:
            # Validar campos requeridos
            self.validate_required_fields(
                {'username': username, 'password': password},
                ['username', 'password']
            )
            
            # Autenticar usuario
            user = authenticate(username=username, password=password)
            
            if not user:
                return ServiceResult.validation_error(
                    "Credenciales inválidas",
                    details={"field": "credentials"}
                )
            
            if not user.is_active:
                return ServiceResult.validation_error(
                    "Cuenta de usuario desactivada",
                    details={"field": "account_status"}
                )
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Registrar login en historial
            self._log_user_login(user, request)
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="login",
                resource_type="user",
                resource_id=user.id,
                details={"login_method": "password"}
            )
            
            self.log_info(f"Usuario {user.username} autenticado exitosamente")
            
            return ServiceResult.success(
                data={
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'is_active': user.is_active,
                        'date_joined': user.date_joined.isoformat(),
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    },
                    'access_expires_at': access_token['exp'],
                    'refresh_expires_at': refresh['exp']
                },
                message="Login exitoso"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en login: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el login", details={"original_error": str(e)})
            )
    
    def register_user(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Registra un nuevo usuario.
        
        Args:
            user_data: Datos del usuario
            request: Request object para obtener IP y user agent
            
        Returns:
            ServiceResult con datos del usuario creado
        """
        try:
            # Validar campos requeridos
            required_fields = ['username', 'email', 'password', 'password_confirm']
            self.validate_required_fields(user_data, required_fields)
            
            # Validar contraseñas
            if user_data['password'] != user_data['password_confirm']:
                return ServiceResult.validation_error(
                    "Las contraseñas no coinciden",
                    details={"field": "password_confirm"}
                )
            
            # Validar fortaleza de contraseña
            password = user_data['password']
            try:
                from ..utils.validators import validate_password_strength
                validate_password_strength(password, raise_serializer_error=False)
            except Exception as e:
                from ..utils.validators import PasswordValidationError
                if isinstance(e, PasswordValidationError):
                    return ServiceResult.validation_error(
                        e.message,
                        details={"field": "password"}
                    )
                raise
            
            # Validar email único
            if User.objects.filter(email=user_data['email']).exists():
                return ServiceResult.validation_error(
                    "Este email ya está registrado",
                    details={"field": "email"}
                )
            
            # Validar username único
            if User.objects.filter(username=user_data['username']).exists():
                return ServiceResult.validation_error(
                    "Este nombre de usuario ya está en uso",
                    details={"field": "username"}
                )
            
            # Crear usuario
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                is_active=True
            )
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.create_for_user(user)
            
            # Generar tokens JWT automáticamente
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Registrar registro en historial
            self._log_user_registration(user, request)
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="register",
                resource_type="user",
                resource_id=user.id,
                details={"registration_method": "password"}
            )
            
            self.log_info(f"Usuario {user.username} registrado exitosamente")
            
            return ServiceResult.success(
                data={
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'is_active': user.is_active,
                        'date_joined': user.date_joined.isoformat()
                    },
                    'verification_token': str(verification_token.token),
                    'verification_required': True,
                    'access_expires_at': access_token['exp'],
                    'refresh_expires_at': refresh['exp']
                },
                message="Usuario registrado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en registro: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el registro", details={"original_error": str(e)})
            )
    
    def logout_user(self, user: User, refresh_token: str = None) -> ServiceResult:
        """
        Cierra sesión de un usuario.
        
        Args:
            user: Usuario a cerrar sesión
            refresh_token: Token de refresh a invalidar
            
        Returns:
            ServiceResult con resultado del logout
        """
        try:
            # Invalidar token de refresh si se proporciona
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    self.log_warning(f"Error invalidando token: {str(e)}")
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="logout",
                resource_type="user",
                resource_id=user.id
            )
            
            self.log_info(f"Usuario {user.username} cerró sesión")
            
            return ServiceResult.success(
                message="Logout exitoso"
            )
            
        except Exception as e:
            self.log_error(f"Error en logout: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el logout", details={"original_error": str(e)})
            )
    
    def refresh_token(self, refresh_token: str) -> ServiceResult:
        """
        Refresca un token de acceso.
        
        Args:
            refresh_token: Token de refresh
            
        Returns:
            ServiceResult con nuevo token de acceso
        """
        try:
            token = RefreshToken(refresh_token)
            new_access_token = token.access_token
            
            return ServiceResult.success(
                data={
                    'access': str(new_access_token),
                    'access_expires_at': new_access_token['exp']
                },
                message="Token refrescado exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error refrescando token: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Token de refresh inválido", details={"original_error": str(e)})
            )
    
    def verify_email(self, token: str) -> ServiceResult:
        """
        Verifica un email usando token.
        
        Args:
            token: Token de verificación
            
        Returns:
            ServiceResult con resultado de verificación
        """
        try:
            token_obj = EmailVerificationToken.objects.filter(token=token).first()
            
            if not token_obj:
                return ServiceResult.validation_error(
                    "Token inválido o expirado",
                    details={"field": "token"}
                )
            
            if token_obj.is_expired():
                return ServiceResult.validation_error(
                    "Token expirado",
                    details={"field": "token", "expired": True}
                )
            
            # Verificar email
            token_obj.verify()
            
            # Crear log de auditoría
            self.create_audit_log(
                user=token_obj.user,
                action="email_verified",
                resource_type="user",
                resource_id=token_obj.user.id
            )
            
            self.log_info(f"Email verificado para usuario {token_obj.user.username}")
            
            return ServiceResult.success(
                data={
                    'user': {
                        'id': token_obj.user.id,
                        'username': token_obj.user.username,
                        'email': token_obj.user.email,
                        'is_active': token_obj.user.is_active
                    }
                },
                message="Email verificado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error verificando email: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante la verificación", details={"original_error": str(e)})
            )
    
    def resend_verification(self, email: str) -> ServiceResult:
        """
        Reenvía token de verificación de email.
        
        Args:
            email: Email del usuario
            
        Returns:
            ServiceResult con resultado del reenvío
        """
        try:
            if not email:
                return ServiceResult.validation_error(
                    "Email es requerido",
                    details={"field": "email"}
                )
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Por seguridad, no revelar si el email existe
                return ServiceResult.success(
                    message=f"Si el email existe, se enviará un nuevo token de verificación"
                )
            
            # Crear nuevo token de verificación
            token_obj = EmailVerificationToken.create_for_user(user)
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="verification_resent",
                resource_type="user",
                resource_id=user.id
            )
            
            self.log_info(f"Token de verificación reenviado para usuario {user.username}")
            
            return ServiceResult.success(
                data={
                    'token': str(token_obj.token),
                    'expires_at': token_obj.expires_at.isoformat()
                },
                message=f"Token de verificación enviado a {email}"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error reenviando verificación: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el reenvío", details={"original_error": str(e)})
            )
    
    def forgot_password(self, email: str, request=None) -> ServiceResult:
        """
        Solicita restablecimiento de contraseña.
        
        Args:
            email: Email del usuario
            request: Request object para obtener IP y user agent
            
        Returns:
            ServiceResult con resultado de la solicitud
        """
        try:
            if not email:
                return ServiceResult.validation_error(
                    "Email es requerido",
                    details={"field": "email"}
                )
            
            try:
                user = User.objects.get(email=email)
                
                # Crear token de recuperación
                reset_token = EmailVerificationToken.create_for_user(user)
                
                # Enviar email de restablecimiento de contraseña
                try:
                    from django.conf import settings
                    from django.utils import timezone
                    from ..email_service import send_email_notification
                    
                    email_context = {
                        'user_name': user.get_full_name() or user.username,
                        'user_email': user.email,
                        'token': str(reset_token.token),
                        'reset_url': f"{settings.FRONTEND_URL}/auth/reset-password/?token={reset_token.token}",
                        'token_expiry_hours': 24,
                        'current_year': timezone.now().year,
                    }
                    
                    email_result = send_email_notification(
                        user_email=user.email,
                        notification_type='password_reset',
                        context=email_context
                    )
                    
                    if email_result.get("success"):
                        self.log_info(f"[SUCCESS] Email de restablecimiento enviado a {user.email}")
                    else:
                        self.log_error(f"[ERROR] Fallo envio de email: {email_result.get('error')}")
                except Exception as e:
                    self.log_error(f"[EXCEPCION] Error enviando email: {e}", exc_info=True)
                
                # Registrar solicitud en historial
                self._log_password_reset_request(user, request)
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="password_reset_requested",
                    resource_type="user",
                    resource_id=user.id
                )
                
                self.log_info(f"Solicitud de restablecimiento de contraseña para usuario {user.username}")
                
                return ServiceResult.success(
                    data={
                        'token': str(reset_token.token),
                        'expires_at': reset_token.expires_at.isoformat()
                    },
                    message=f"Instrucciones de recuperación enviadas a {email}"
                )
                
            except User.DoesNotExist:
                # Por seguridad, no revelar si el email existe
                return ServiceResult.success(
                    message="Si el email existe, recibirás instrucciones de recuperación"
                )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en solicitud de restablecimiento: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante la solicitud", details={"original_error": str(e)})
            )
    
    def reset_password(self, token: str, new_password: str, confirm_password: str) -> ServiceResult:
        """
        Restablece contraseña usando token.
        
        Args:
            token: Token de recuperación
            new_password: Nueva contraseña
            confirm_password: Confirmación de contraseña
            
        Returns:
            ServiceResult con resultado del restablecimiento
        """
        try:
            # Validar campos requeridos
            self.validate_required_fields(
                {'token': token, 'new_password': new_password, 'confirm_password': confirm_password},
                ['token', 'new_password', 'confirm_password']
            )
            
            # Validar contraseñas
            if new_password != confirm_password:
                return ServiceResult.validation_error(
                    "Las contraseñas no coinciden",
                    details={"field": "confirm_password"}
                )
            
            # Validar fortaleza de contraseña
            try:
                from ..utils.validators import validate_password_strength
                validate_password_strength(new_password, raise_serializer_error=False)
            except Exception as e:
                from ..utils.validators import PasswordValidationError
                if isinstance(e, PasswordValidationError):
                    return ServiceResult.validation_error(
                        e.message,
                        details={"field": "new_password"}
                    )
                raise
            
            # Verificar token
            token_obj = EmailVerificationToken.objects.filter(token=token).first()
            
            if not token_obj:
                return ServiceResult.validation_error(
                    "Token inválido o expirado",
                    details={"field": "token"}
                )
            
            if token_obj.is_expired():
                return ServiceResult.validation_error(
                    "Token expirado",
                    details={"field": "token", "expired": True}
                )
            
            # Restablecer contraseña
            user = token_obj.user
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            token_obj.delete()
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="password_reset",
                resource_type="user",
                resource_id=user.id
            )
            
            self.log_info(f"Contraseña restablecida para usuario {user.username}")
            
            return ServiceResult.success(
                message="Contraseña restablecida exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error restableciendo contraseña: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el restablecimiento", details={"original_error": str(e)})
            )
    
    def get_user_profile(self, user: User) -> ServiceResult:
        """
        Obtiene el perfil de un usuario.
        
        Args:
            user: Usuario
            
        Returns:
            ServiceResult con datos del perfil
        """
        try:
            # Obtener perfil extendido si existe
            user_profile = None
            try:
                user_profile = user.profile
            except UserProfile.DoesNotExist:
                # Si no existe perfil, crear uno vacío
                user_profile = UserProfile.objects.create(user=user)
            
            profile_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name() or user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_verified': self._check_email_verified(user),
                # Datos del perfil extendido
                'phone_number': user_profile.phone_number or '',
                'region': user_profile.region or '',
                'municipality': user_profile.municipality or '',
                'farm_name': user_profile.farm_name or '',
                'years_experience': user_profile.years_experience,
                'farm_size_hectares': float(user_profile.farm_size_hectares) if user_profile.farm_size_hectares else None,
                'preferred_language': user_profile.preferred_language,
                'email_notifications': user_profile.email_notifications,
                'role': user_profile.role
            }
            
            return ServiceResult.success(
                data=profile_data,
                message="Perfil obtenido exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo perfil: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo perfil", details={"original_error": str(e)})
            )
    
    def _check_email_verified(self, user: User) -> bool:
        """Verifica si el email del usuario está verificado."""
        try:
            if hasattr(user, 'auth_email_token'):
                return user.auth_email_token.is_verified
        except:
            pass
        return user.is_active
    
    def update_user_profile(self, user: User, profile_data: Dict[str, Any]) -> ServiceResult:
        """
        Actualiza el perfil de un usuario.
        
        Args:
            user: Usuario
            profile_data: Datos a actualizar
            
        Returns:
            ServiceResult con datos actualizados
        """
        try:
            # Campos permitidos para actualización del modelo User
            user_allowed_fields = ['first_name', 'last_name', 'email']
            
            # Campos del perfil extendido (UserProfile)
            profile_allowed_fields = ['phone_number']
            
            # Separar datos de User y UserProfile
            user_data = {}
            profile_data_dict = {}
            
            for field, value in profile_data.items():
                if field in user_allowed_fields:
                    user_data[field] = value
                elif field in profile_allowed_fields:
                    profile_data_dict[field] = value
                else:
                    return ServiceResult.validation_error(
                        f"Campo '{field}' no permitido para actualización",
                        details={
                            "field": field, 
                            "allowed_fields": user_allowed_fields + profile_allowed_fields
                        }
                    )
            
            # Validar email único si se está cambiando
            if 'email' in user_data and user_data['email'] != user.email:
                if User.objects.filter(email=user_data['email']).exclude(id=user.id).exists():
                    return ServiceResult.validation_error(
                        "Este email ya está registrado",
                        details={"field": "email"}
                    )
            
            # Actualizar campos del modelo User
            for field, value in user_data.items():
                setattr(user, field, value)
            
            user.save()
            
            # Actualizar perfil extendido si existe
            if profile_data_dict:
                profile, created = UserProfile.objects.get_or_create(user=user)
                for field, value in profile_data_dict.items():
                    setattr(profile, field, value)
                profile.save()
            
            # Obtener datos actualizados del usuario
            updated_data = self.get_user_profile(user).data
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="profile_updated",
                resource_type="user",
                resource_id=user.id,
                details={"updated_fields": list(profile_data.keys())}
            )
            
            self.log_info(f"Perfil actualizado para usuario {user.username}")
            
            return ServiceResult.success(
                data=updated_data,
                message="Perfil actualizado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error actualizando perfil: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno actualizando perfil", details={"original_error": str(e)})
            )
    
    def _log_user_login(self, user: User, request=None):
        """Registra login en historial."""
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                login_time=timezone.now(),
                success=True
            )
        except Exception as e:
            self.log_warning(f"Error registrando login: {str(e)}")
    
    def _log_user_registration(self, user: User, request=None):
        """Registra registro en historial."""
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                login_time=timezone.now(),
                success=True,
                is_registration=True
            )
        except Exception as e:
            self.log_warning(f"Error registrando registro: {str(e)}")
    
    def _log_password_reset_request(self, user: User, request=None):
        """Registra solicitud de restablecimiento."""
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                login_time=timezone.now(),
                success=True,
                is_password_reset=True
            )
        except Exception as e:
            self.log_warning(f"Error registrando solicitud de restablecimiento: {str(e)}")
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def register_user_with_email_verification(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Registra un nuevo usuario y envía email de verificación.
        
        Args:
            user_data: Datos del usuario
            request: Request object para obtener IP y user agent
            
        Returns:
            ServiceResult con datos del usuario creado y token de verificación
        """
        try:
            # Validar campos requeridos
            required_fields = ['email', 'password', 'password_confirm']
            self.validate_required_fields(user_data, required_fields)
            
            # Validar contraseñas
            if user_data['password'] != user_data['password_confirm']:
                return ServiceResult.validation_error(
                    "Las contraseñas no coinciden",
                    details={"field": "password_confirm"}
                )
            
            # Validar fortaleza de contraseña
            password = user_data['password']
            try:
                from ..utils.validators import validate_password_strength
                validate_password_strength(password, raise_serializer_error=False)
            except Exception as e:
                from ..utils.validators import PasswordValidationError
                if isinstance(e, PasswordValidationError):
                    return ServiceResult.validation_error(
                        e.message,
                        details={"field": "password"}
                    )
                raise
            
            # Validar email único
            if User.objects.filter(email=user_data['email']).exists():
                return ServiceResult.validation_error(
                    "Este email ya está registrado",
                    details={"field": "email"}
                )
            
            # Crear usuario
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password=password,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                is_active=True
            )
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.create_for_user(user)
            
            # Enviar email de verificación
            email_result = self._send_verification_email(user, verification_token)
            if not email_result.get('success'):
                self.log_warning(f"Error enviando email de verificación: {email_result.get('error')}")
            
            # Registrar registro en historial
            self._log_user_registration(user, request)
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="register",
                resource_type="user",
                resource_id=user.id,
                details={"registration_method": "email_verification"}
            )
            
            self.log_info(f"Usuario {user.username} registrado exitosamente")
            
            return ServiceResult.success(
                data={
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_active': user.is_active,
                        'date_joined': user.date_joined.isoformat()
                    },
                    'verification_token': str(verification_token.token) if settings.DEBUG else None,
                    'verification_required': True,
                    'email': user.email
                },
                message="Usuario registrado exitosamente. Por favor verifica tu correo electrónico para activar tu cuenta."
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en registro: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el registro", details={"original_error": str(e)})
            )
    
    def pre_register_user(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Pre-registra un usuario (crea registro pendiente sin crear usuario final).
        Maneja el caso de registro pendiente existente reenviando el email si no ha expirado.
        
        Args:
            user_data: Datos del usuario
            request: Request object para obtener IP y user agent
            
        Returns:
            ServiceResult con datos del registro pendiente
        """
        try:
            from personas.models import PendingRegistration
            from django.template.loader import render_to_string
            from ..email_service import send_custom_email
            
            # Validar campos requeridos
            email = user_data.get('email')
            password = user_data.get('password')
            
            if not email or not password:
                return ServiceResult.validation_error(
                    "Email y contraseña son requeridos",
                    details={"field": "email" if not email else "password"}
                )
            
            # Validar fortaleza de contraseña
            try:
                from ..utils.validators import validate_password_strength
                validate_password_strength(password, raise_serializer_error=False)
            except Exception as e:
                from ..utils.validators import PasswordValidationError
                if isinstance(e, PasswordValidationError):
                    return ServiceResult.validation_error(
                        e.message,
                        details={"field": "password"}
                    )
                raise
            
            # Validar email único
            if User.objects.filter(email=email).exists():
                return ServiceResult.validation_error(
                    "Este email ya está registrado",
                    details={"field": "email"}
                )
            
            # Verificar si ya existe un registro pendiente
            existing_pending = PendingRegistration.objects.filter(email=email, is_verified=False).first()
            if existing_pending:
                # Si el token no ha expirado, reenviar el email
                if not existing_pending.is_expired():
                    email_result = self._send_pre_registration_verification_email(existing_pending)
                    if email_result.get('success'):
                        return ServiceResult.success(
                            data={'email': email},
                            message="Se ha reenviado el enlace de verificación a tu correo electrónico."
                        )
                else:
                    # Eliminar registro expirado
                    existing_pending.delete()
            
            # Crear nuevo registro pendiente
            pending_reg = PendingRegistration.objects.create(
                email=email,
                data=user_data
            )
            
            # Enviar email de verificación
            email_result = self._send_pre_registration_verification_email(pending_reg)
            if not email_result.get('success'):
                # Eliminar registro pendiente si falla el envío
                pending_reg.delete()
                return ServiceResult.error(
                    ValidationServiceError(
                        "Error al enviar el email de verificación. Por favor intenta nuevamente.",
                        details={"email_error": email_result.get('error')}
                    )
                )
            
            self.log_info(f"Pre-registro creado para {email}")
            
            return ServiceResult.success(
                data={'email': email},
                message="Se ha enviado un enlace de verificación a tu correo electrónico."
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en pre-registro: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el pre-registro", details={"original_error": str(e)})
            )
    
    def verify_pre_registration_and_create_user(self, token: str) -> ServiceResult:
        """
        Verifica token de pre-registro y crea el usuario final.
        
        Args:
            token: Token de verificación
            
        Returns:
            ServiceResult con datos del usuario creado
        """
        try:
            from personas.models import PendingRegistration
            from personas.serializers import PersonaRegistroSerializer
            from django.db import transaction
            import uuid
            
            # Validar formato de token
            try:
                token_uuid = uuid.UUID(str(token))
            except (ValueError, TypeError):
                return ServiceResult.validation_error(
                    "Formato de token inválido",
                    details={"field": "token"}
                )
            
            # Obtener registro pendiente
            try:
                pending_reg = PendingRegistration.objects.get(verification_token=token_uuid)
            except PendingRegistration.DoesNotExist:
                return ServiceResult.validation_error(
                    "Token inválido o expirado",
                    details={"field": "token"}
                )
            
            # Verificar si ya fue verificado
            if pending_reg.is_verified:
                return ServiceResult.validation_error(
                    "Este enlace ya fue utilizado",
                    details={"field": "token", "already_used": True}
                )
            
            # Verificar si expiró
            if pending_reg.is_expired():
                pending_reg.delete()
                return ServiceResult.validation_error(
                    "El enlace de verificación ha expirado. Por favor registrate nuevamente.",
                    details={"field": "token", "expired": True}
                )
            
            # Crear el usuario final con los datos guardados
            with transaction.atomic():
                user_data = pending_reg.data.copy()
                password = user_data.pop('password')
                
                user = User.objects.create_user(
                    username=user_data['email'],
                    email=user_data['email'],
                    password=password,
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=True
                )
                
                # Si hay datos de persona, crear el registro de persona
                if 'tipo_documento' in user_data or 'numero_documento' in user_data:
                    try:
                        persona_data = {k: v for k, v in user_data.items() if k not in ['email', 'password', 'first_name', 'last_name']}
                        persona_data['email'] = user.email
                        persona_data['password'] = password
                        persona_serializer = PersonaRegistroSerializer(data=persona_data)
                        if persona_serializer.is_valid():
                            persona = persona_serializer.save()
                        else:
                            self.log_warning(f"Error creando persona para usuario {user.email}: {persona_serializer.errors}")
                    except Exception as e:
                        self.log_warning(f"Error creando persona: {e}")
                
                # Marcar registro pendiente como verificado
                pending_reg.verify()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="user_created_from_preregistration",
                    resource_type="user",
                    resource_id=user.id
                )
                
                self.log_info(f"Usuario {user.email} creado exitosamente después de verificación")
                
                return ServiceResult.success(
                    data={
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'is_active': user.is_active,
                            'date_joined': user.date_joined.isoformat()
                        }
                    },
                    message="Correo verificado correctamente. Ya puedes iniciar sesión."
                )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error verificando pre-registro: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante la verificación", details={"original_error": str(e)})
            )
    
    def _send_verification_email(self, user: User, verification_token: EmailVerificationToken) -> Dict[str, Any]:
        """
        Envía email de verificación al usuario.
        
        Args:
            user: Usuario
            verification_token: Token de verificación
            
        Returns:
            Dict con resultado del envío
        """
        try:
            from django.conf import settings
            from ..email_service import send_custom_email
            
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"
            
            # Contenido HTML del email
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">¡Bienvenido a CacaoScan, {user.get_full_name() or user.username}!</h2>
                    <p>Gracias por registrarte en nuestra plataforma. Para completar tu registro, por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Verificar mi correo</a>
                    </div>
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; color: #666;">{verification_url}</p>
                    <p style="margin-top: 30px; font-size: 12px; color: #999;">Este enlace expirará en 24 horas.</p>
                    <p style="font-size: 12px; color: #999;">Si no creaste esta cuenta, puedes ignorar este correo.</p>
                </div>
            </body>
            </html>
            """
            
            # Contenido de texto plano
            text_content = f"""
Bienvenido a CacaoScan, {user.get_full_name() or user.username}!

Gracias por registrarte en nuestra plataforma. Para completar tu registro, por favor verifica tu dirección de correo electrónico visitando el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.
            """
            
            send_custom_email(
                to_emails=[user.email],
                subject="Verifica tu correo electrónico - CacaoScan",
                html_content=html_content,
                text_content=text_content
            )
            
            return {'success': True}
            
        except Exception as e:
            self.log_error(f"Error enviando email de verificación: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_pre_registration_verification_email(self, pending_reg) -> Dict[str, Any]:
        """
        Envía email de verificación para pre-registro.
        
        Args:
            pending_reg: Registro pendiente
            
        Returns:
            Dict con resultado del envío
        """
        try:
            from django.template.loader import render_to_string
            from ..email_service import send_custom_email
            
            verification_url = f"{settings.FRONTEND_URL}/auth/verificar/{pending_reg.verification_token}"
            
            user_data = pending_reg.data
            first_name = user_data.get('first_name', '')
            user_name = first_name or pending_reg.email.split('@')[0]
            
            # Intentar usar template si existe
            try:
                html_content = render_to_string('emails/verify_email.html', {
                    'verification_url': verification_url,
                    'user_name': user_name,
                    'frontend_url': settings.FRONTEND_URL
                })
            except:
                # Fallback a HTML simple si no existe el template
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">Verifica tu correo electrónico - CacaoScan</h2>
                        <p>Gracias por registrarte. Para completar tu registro, por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:</p>
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
Bienvenido a CacaoScan, {user_name}!

Gracias por registrarte en nuestra plataforma. Para completar tu registro, verifica tu dirección de correo electrónico visitando el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.

Equipo CacaoScan · Proyecto SENNOVA · SENA Guaviare
            """
            
            send_custom_email(
                to_emails=[pending_reg.email],
                subject="Verifica tu correo electrónico - CacaoScan",
                html_content=html_content,
                text_content=text_content
            )
            
            return {'success': True}
            
        except Exception as e:
            self.log_error(f"Error enviando email de verificación: {e}")
            return {'success': False, 'error': str(e)}


