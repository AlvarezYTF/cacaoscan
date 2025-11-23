"""
Password service for CacaoScan.
Handles password reset and recovery operations.
"""
import logging
from typing import Optional
from django.contrib.auth.models import User
from django.utils import timezone

from ..base import BaseService, ServiceResult, ValidationServiceError
from audit.models import LoginHistory

logger = logging.getLogger("cacaoscan.services.auth.password")


class PasswordService(BaseService):
    """
    Service for handling password reset and recovery.
    """
    
    def __init__(self):
        super().__init__()
    
    def forgot_password(self, email: str, request=None) -> ServiceResult:
        """
        Requests password reset.
        
        Args:
            email: User email
            request: Request object to get IP and user agent
            
        Returns:
            ServiceResult with request result
        """
        try:
            if not email:
                return ServiceResult.validation_error(
                    "Email es requerido",
                    details={"field": "email"}
                )
            
            try:
                user = User.objects.get(email=email)
                
                # Create reset token
                from ...utils.model_imports import get_models_safely
                models = get_models_safely({
                    'EmailVerificationToken': 'auth_app.models.EmailVerificationToken'
                })
                EmailVerificationToken = models['EmailVerificationToken']
                reset_token = EmailVerificationToken.create_for_user(user)
                
                # Send password reset email
                try:
                    from django.conf import settings
                    from ...email import send_email_notification
                    
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
                
                # Log password reset request
                self._log_password_reset_request(user, request)
                
                # Create audit log
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
                # For security, don't reveal if email exists
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
        Resets password using token.
        
        Args:
            token: Recovery token
            new_password: New password
            confirm_password: Password confirmation
            
        Returns:
            ServiceResult with reset result
        """
        try:
            # Validate required fields
            self.validate_required_fields(
                {'token': token, 'new_password': new_password, 'confirm_password': confirm_password},
                ['token', 'new_password', 'confirm_password']
            )
            
            # Validate passwords
            if new_password != confirm_password:
                return ServiceResult.validation_error(
                    "Las contraseñas no coinciden",
                    details={"field": "confirm_password"}
                )
            
            # Validate password strength
            try:
                from core.utils import validate_password_strength
                validate_password_strength(new_password, raise_serializer_error=False)
            except Exception as e:
                from core.utils import PasswordValidationError
                if isinstance(e, PasswordValidationError):
                    return ServiceResult.validation_error(
                        e.message,
                        details={"field": "new_password"}
                    )
                raise
            
            # Verify token
            from ...utils.model_imports import get_models_safely
            models = get_models_safely({
                'EmailVerificationToken': 'auth_app.models.EmailVerificationToken'
            })
            EmailVerificationToken = models['EmailVerificationToken']
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
            
            # Reset password
            user = token_obj.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            token_obj.delete()
            
            # Create audit log
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
    
    def _log_password_reset_request(self, user: User, request=None):
        """Logs password reset request."""
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
            self.log_warning(f"Error registrando solicitud de restablecimiento: {str(e)}")
    
    def _get_client_ip(self, request):
        """Gets client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

