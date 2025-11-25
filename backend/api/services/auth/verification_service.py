"""
Email verification service for CacaoScan.
Handles email verification and token resending.
"""
import logging
from typing import Optional
from django.contrib.auth.models import User

from ..base import BaseService, ServiceResult, ValidationServiceError

logger = logging.getLogger("cacaoscan.services.auth.verification")


class VerificationService(BaseService):
    """
    Service for handling email verification.
    """
    
    def __init__(self):
        super().__init__()
    
    def verify_email(self, token: str) -> ServiceResult:
        """
        Verifies email using token.
        
        Args:
            token: Verification token
            
        Returns:
            ServiceResult with verification result
        """
        try:
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
            
            # Verify email
            token_obj.verify()
            
            # Create audit log
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
        Resends email verification token.
        
        Args:
            email: User email
            
        Returns:
            ServiceResult with resend result
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
                # For security, don't reveal if email exists
                return ServiceResult.success(
                    message=f"Si el email existe, se enviará un nuevo token de verificación"
                )
            
            # Create new verification token
            from ...utils.model_imports import get_models_safely
            models = get_models_safely({
                'EmailVerificationToken': 'auth_app.models.EmailVerificationToken'
            })
            EmailVerificationToken = models['EmailVerificationToken']
            token_obj = EmailVerificationToken.create_for_user(user)
            
            # Create audit log
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

