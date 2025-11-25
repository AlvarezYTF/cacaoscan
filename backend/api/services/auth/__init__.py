"""
Authentication services module for CacaoScan.
"""
from .login_service import LoginService
from .registration_service import RegistrationService
from .password_service import PasswordService
from .verification_service import VerificationService
from .profile_service import ProfileService

# Backward compatibility: Create a combined service that delegates to individual services
from ..base import BaseService, ServiceResult


class AuthenticationService(BaseService):
    """
    Combined authentication service for backward compatibility.
    Delegates to individual specialized services.
    """
    
    def __init__(self):
        super().__init__()
        self.login_service = LoginService()
        self.registration_service = RegistrationService()
        self.password_service = PasswordService()
        self.verification_service = VerificationService()
        self.profile_service = ProfileService()
    
    # Login methods
    def login_user(self, username: str, password: str, request=None) -> ServiceResult:
        """Delegates to LoginService."""
        return self.login_service.login_user(username, password, request)
    
    def logout_user(self, user, refresh_token: str = None) -> ServiceResult:
        """Delegates to LoginService."""
        return self.login_service.logout_user(user, refresh_token)
    
    def refresh_token(self, refresh_token: str) -> ServiceResult:
        """Delegates to LoginService."""
        return self.login_service.refresh_token(refresh_token)
    
    # Registration methods
    def register_user(self, user_data, request=None) -> ServiceResult:
        """Delegates to RegistrationService."""
        return self.registration_service.register_user(user_data, request)
    
    def register_user_with_email_verification(self, user_data, request=None) -> ServiceResult:
        """Delegates to RegistrationService."""
        return self.registration_service.register_user_with_email_verification(user_data, request)
    
    def pre_register_user(self, user_data, request=None) -> ServiceResult:
        """Delegates to RegistrationService."""
        return self.registration_service.pre_register_user(user_data, request)
    
    def verify_pre_registration_and_create_user(self, token: str) -> ServiceResult:
        """Delegates to RegistrationService."""
        return self.registration_service.verify_pre_registration_and_create_user(token)
    
    # Password methods
    def forgot_password(self, email: str, request=None) -> ServiceResult:
        """Delegates to PasswordService."""
        return self.password_service.forgot_password(email, request)
    
    def reset_password(self, token: str, new_password: str, confirm_password: str) -> ServiceResult:
        """Delegates to PasswordService."""
        return self.password_service.reset_password(token, new_password, confirm_password)
    
    # Verification methods
    def verify_email(self, token: str) -> ServiceResult:
        """Delegates to VerificationService."""
        return self.verification_service.verify_email(token)
    
    def resend_verification(self, email: str) -> ServiceResult:
        """Delegates to VerificationService."""
        return self.verification_service.resend_verification(email)
    
    # Profile methods
    def get_user_profile(self, user) -> ServiceResult:
        """Delegates to ProfileService."""
        return self.profile_service.get_user_profile(user)
    
    def update_user_profile(self, user, profile_data) -> ServiceResult:
        """Delegates to ProfileService."""
        return self.profile_service.update_user_profile(user, profile_data)

__all__ = [
    'LoginService',
    'RegistrationService',
    'PasswordService',
    'VerificationService',
    'ProfileService',
    'AuthenticationService',  # For backward compatibility
]

