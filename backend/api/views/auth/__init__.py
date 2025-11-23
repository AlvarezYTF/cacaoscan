"""
Auth views module.
"""
from .otp_views import SendOtpView, VerifyOtpView

__all__ = [
    'SendOtpView',
    'VerifyOtpView',
]

