"""
Registration service for CacaoScan.
Handles user registration and pre-registration.
"""
import logging
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db import transaction
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from ..base import BaseService, ServiceResult, ValidationServiceError
from audit.models import LoginHistory

logger = logging.getLogger("cacaoscan.services.auth.registration")

# Error message constants
ERROR_EMAIL_ALREADY_REGISTERED = "Este email ya está registrado"


class RegistrationService(BaseService):
    """
    Service for handling user registration.
    """
    
    def __init__(self):
        super().__init__()
    
    def register_user(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Registers a new user.
        
        Args:
            user_data: User data
            request: Request object to get IP and user agent
            
        Returns:
            ServiceResult with created user data
        """
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'password_confirm']
            self.validate_required_fields(user_data, required_fields)
            
            # Validate user data
            validation_result = self._validate_user_registration_data(user_data, check_username=True)
            if validation_result:
                return validation_result
            
            # Create user
            user = self._create_user_from_data(user_data, use_email_as_username=False)
            
            # Create email verification token
            from ...utils.model_imports import get_models_safely
            models = get_models_safely({
                'EmailVerificationToken': 'auth_app.models.EmailVerificationToken'
            })
            email_verification_token_model = models['EmailVerificationToken']
            verification_token = email_verification_token_model.create_for_user(user)
            
            # Generate JWT tokens automatically
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Log user registration
            self._log_user_registration(user, request)
            
            # Create audit log
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
    
    def register_user_with_email_verification(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Registers a new user and sends verification email.
        
        Args:
            user_data: User data
            request: Request object to get IP and user agent
            
        Returns:
            ServiceResult with created user data and verification token
        """
        try:
            # Validate required fields
            required_fields = ['email', 'password', 'password_confirm']
            self.validate_required_fields(user_data, required_fields)
            
            # Validate user data
            validation_result = self._validate_user_registration_data(user_data, check_username=False)
            if validation_result:
                return validation_result
            
            # Create user
            user = self._create_user_from_data(user_data, use_email_as_username=True)
            
            # Create email verification token
            from ...utils.model_imports import get_models_safely
            models = get_models_safely({
                'EmailVerificationToken': 'auth_app.models.EmailVerificationToken'
            })
            email_verification_token_model = models['EmailVerificationToken']
            verification_token = email_verification_token_model.create_for_user(user)
            
            # Send verification email
            email_result = self._send_verification_email(user, verification_token)
            if not email_result.get('success'):
                self.log_warning(f"Error enviando email de verificación: {email_result.get('error')}")
            
            # Log user registration
            self._log_user_registration(user, request)
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="register",
                resource_type="user",
                resource_id=user.id,
                details={"registration_method": "email_verification"}
            )
            
            self.log_info(f"Usuario {user.username} registrado exitosamente")
            
            from django.conf import settings
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
    
    def _validate_pre_registration_data(self, user_data: Dict[str, Any]) -> ServiceResult:
        """Valida los datos de pre-registro."""
        email = user_data.get('email')
        password = user_data.get('password')
        
        if not email or not password:
            return ServiceResult.validation_error(
                "Email y contraseña son requeridos",
                details={"field": "email" if not email else "password"}
            )
        
        try:
            from core.utils import validate_password_strength
            validate_password_strength(password, raise_serializer_error=False)
        except Exception as e:
            from core.utils import PasswordValidationError
            if isinstance(e, PasswordValidationError):
                return ServiceResult.validation_error(
                    e.message,
                    details={"field": "password"}
                )
            raise
        
        if User.objects.filter(email=email).exists():
            return ServiceResult.validation_error(
                ERROR_EMAIL_ALREADY_REGISTERED,
                details={"field": "email"}
            )
        
        return ServiceResult.success()
    
    def _handle_existing_pending_registration(self, existing_pending, email: str) -> Optional[ServiceResult]:
        """Maneja un registro pendiente existente."""
        if not existing_pending.is_expired():
            email_result = self._send_pre_registration_verification_email(existing_pending)
            if email_result.get('success'):
                return ServiceResult.success(
                    data={'email': email},
                    message="Se ha reenviado el enlace de verificación a tu correo electrónico."
                )
        else:
            existing_pending.delete()
        return None
    
    def pre_register_user(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Pre-registers a user (creates pending registration without creating final user).
        Handles existing pending registration by resending email if not expired.
        
        Args:
            user_data: User data
            request: Request object to get IP and user agent (no usado actualmente)
            
        Returns:
            ServiceResult with pending registration data
        """
        _ = request
        try:
            from personas.models import PendingRegistration
            
            validation_error = self._validate_pre_registration_data(user_data)
            if validation_error:
                return validation_error
            
            email = user_data.get('email')
            
            existing_pending = PendingRegistration.objects.filter(email=email, is_verified=False).first()
            if existing_pending:
                result = self._handle_existing_pending_registration(existing_pending, email)
                if result:
                    return result
            
            pending_reg = PendingRegistration.objects.create(
                email=email,
                data=user_data
            )
            
            email_result = self._send_pre_registration_verification_email(pending_reg)
            if not email_result.get('success'):
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
        Verifies pre-registration token and creates final user.
        
        Args:
            token: Verification token
            
        Returns:
            ServiceResult with created user data
        """
        try:
            from personas.models import PendingRegistration
            from personas.serializers import PersonaRegistroSerializer
            import uuid
            
            # Validate token format
            try:
                token_uuid = uuid.UUID(str(token))
            except (ValueError, TypeError):
                return ServiceResult.validation_error(
                    "Formato de token inválido",
                    details={"field": "token"}
                )
            
            # Get pending registration
            try:
                pending_reg = PendingRegistration.objects.get(verification_token=token_uuid)
            except PendingRegistration.DoesNotExist:
                return ServiceResult.validation_error(
                    "Token inválido o expirado",
                    details={"field": "token"}
                )
            
            # Check if already verified
            if pending_reg.is_verified:
                return ServiceResult.validation_error(
                    "Este enlace ya fue utilizado",
                    details={"field": "token", "already_used": True}
                )
            
            # Check if expired
            if pending_reg.is_expired():
                pending_reg.delete()
                return ServiceResult.validation_error(
                    "El enlace de verificación ha expirado. Por favor registrate nuevamente.",
                    details={"field": "token", "expired": True}
                )
            
            # Create final user with saved data
            with transaction.atomic():
                user_data = pending_reg.data.copy()
                password = user_data.pop('password')
                
                user = self._create_user_from_data(user_data, use_email_as_username=True)
                
                # If there's persona data, create persona record
                if 'tipo_documento' in user_data or 'numero_documento' in user_data:
                    try:
                        persona_data = {k: v for k, v in user_data.items() if k not in ['email', 'password', 'first_name', 'last_name']}
                        persona_data['email'] = user.email
                        persona_data['password'] = password
                        persona_serializer = PersonaRegistroSerializer(data=persona_data)
                        if persona_serializer.is_valid():
                            _ = persona_serializer.save()  # Persona created but not used here
                        else:
                            self.log_warning(f"Error creando persona para usuario {user.email}: {persona_serializer.errors}")
                    except Exception as e:
                        self.log_warning(f"Error creando persona: {e}")
                
                # Mark pending registration as verified
                pending_reg.verify()
                
                # Invalidate cache when new users are created
                try:
                    from core.utils import invalidate_system_stats_cache
                    invalidate_system_stats_cache()
                except Exception as e:
                    self.log_warning(f"Error invalidating cache after user creation: {e}")
                
                # Create audit log
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
    
    def _log_user_registration(self, user: User, request=None):
        """Logs user registration in history."""
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginHistory.objects.create(
                usuario=user,
                ip_address=ip_address,
                user_agent=user_agent,
                login_time=timezone.now(),
                success=True
            )
        except Exception as e:
            self.log_warning(f"Error registrando registro: {str(e)}")
    
    def _send_verification_email(self, user: User, verification_token) -> Dict[str, Any]:
        """
        Sends verification email to user.
        
        Args:
            user: User
            verification_token: Verification token
            
        Returns:
            Dict with sending result
        """
        try:
            from django.conf import settings
            from ...email import send_custom_email
            
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"
            
            # HTML email content
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
            
            # Plain text content
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
        Sends verification email for pre-registration.
        
        Args:
            pending_reg: Pending registration
            
        Returns:
            Dict with sending result
        """
        try:
            from django.template.loader import render_to_string
            from ...email import send_custom_email
            from django.conf import settings
            
            verification_url = f"{settings.FRONTEND_URL}/auth/verificar/{pending_reg.verification_token}"
            
            user_data = pending_reg.data
            first_name = user_data.get('first_name', '')
            user_name = first_name or pending_reg.email.split('@')[0]
            
            # Try to use template if exists
            try:
                html_content = render_to_string('emails/verify_email.html', {
                    'verification_url': verification_url,
                    'user_name': user_name,
                    'frontend_url': settings.FRONTEND_URL
                })
            except (TemplateDoesNotExist, TemplateSyntaxError, Exception):
                # Fallback to simple HTML if template doesn't exist
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
    
    def _validate_user_registration_data(self, user_data: Dict[str, Any], check_username: bool = False) -> Optional[ServiceResult]:
        """Validate user registration data."""
        # Validate passwords match
        if user_data.get('password') != user_data.get('password_confirm'):
            return ServiceResult.validation_error(
                "Las contraseñas no coinciden",
                details={"field": "password_confirm"}
            )
        
        # Validate password strength
        password = user_data.get('password')
        if password:
            try:
                from core.utils import validate_password_strength
                validate_password_strength(password, raise_serializer_error=False)
            except Exception as e:
                from core.utils import PasswordValidationError
                if isinstance(e, PasswordValidationError):
                    return ServiceResult.validation_error(
                        e.message,
                        details={"field": "password"}
                    )
                raise
        
        # Validate unique email
        if User.objects.filter(email=user_data.get('email')).exists():
            return ServiceResult.validation_error(
                ERROR_EMAIL_ALREADY_REGISTERED,
                details={"field": "email"}
            )
        
        # Validate unique username if required
        if check_username and user_data.get('username'):
            if User.objects.filter(username=user_data['username']).exists():
                return ServiceResult.validation_error(
                    "Este nombre de usuario ya está en uso",
                    details={"field": "username"}
                )
        
        return None
    
    def _create_user_from_data(self, user_data: Dict[str, Any], use_email_as_username: bool = False) -> User:
        """Create user from data dictionary."""
        username = user_data['email'] if use_email_as_username else user_data['username']
        password = user_data.get('password') or user_data.get('password_confirm')
        
        return User.objects.create_user(
            username=username,
            email=user_data['email'],
            password=password,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            is_active=True
        )
    
    def _get_client_ip(self, request):
        """Gets client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def register(self, user_data: Dict[str, Any], request=None) -> ServiceResult:
        """
        Alias for register_user for backward compatibility with tests.
        
        Args:
            user_data: User data
            request: Request object to get IP and user agent
            
        Returns:
            ServiceResult with created user data
        """
        return self.register_user(user_data, request)

