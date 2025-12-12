"""
Auth views module.
"""
from .login_views import (
    LoginView,
    LogoutView,
    UserProfileView,
    RefreshTokenView,
)
from .google_login_views import (
    GoogleLoginView,
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
    SetPasswordView,
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
    'GoogleLoginView',
    # Registration views
    'RegisterView',
    'PreRegisterView',
    'VerifyEmailPreRegistrationView',
    # Password views
    'ChangePasswordView',
    'ForgotPasswordView',
    'ResetPasswordView',
    'SetPasswordView',
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
