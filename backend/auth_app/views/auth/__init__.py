"""
Auth views module.
"""
from .login_views import (
    LoginView,
    LogoutView,
    UserProfileView,
    RefreshTokenView,
)
from .registration_views import (
    RegisterView,
    PreRegisterView,
    VerifyEmailPreRegistrationView,
)
from .password_views import (
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)
from .email_verification_views import (
    EmailVerificationView,
    ResendVerificationView,
)
from .otp_views import (
    SendOtpView,
    VerifyOtpView,
)
from .user_views import (
    UserListView,
    UserUpdateView,
    UserDeleteView,
    UserStatsView,
    AdminStatsView,
    UserDetailView,
)

__all__ = [
    # Login views
    'LoginView',
    'LogoutView',
    'UserProfileView',
    'RefreshTokenView',
    # Registration views
    'RegisterView',
    'PreRegisterView',
    'VerifyEmailPreRegistrationView',
    # Password views
    'ChangePasswordView',
    'ForgotPasswordView',
    'ResetPasswordView',
    # Email verification views
    'EmailVerificationView',
    'ResendVerificationView',
    # OTP views
    'SendOtpView',
    'VerifyOtpView',
    # User management views
    'UserListView',
    'UserUpdateView',
    'UserDeleteView',
    'UserStatsView',
    'AdminStatsView',
    'UserDetailView',
]
