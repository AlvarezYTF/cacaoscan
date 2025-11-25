"""
Email services module.
"""
from .email_service import (
    EmailService,
    EmailNotificationService,
    email_service,
    email_notification_service,
    send_email_notification,
    send_bulk_email_notification,
    send_custom_email,
)

__all__ = [
    'EmailService',
    'EmailNotificationService',
    'email_service',
    'email_notification_service',
    'send_email_notification',
    'send_bulk_email_notification',
    'send_custom_email',
]

