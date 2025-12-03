"""
Admin views module.
"""
from .audit_views import (
    ActivityLogListView,
    LoginHistoryListView,
    AuditStatsView,
)
from .config_views import (
    SystemSettingsView,
    SystemGeneralConfigView,
    SystemSecurityConfigView,
    SystemMLConfigView,
    SystemInfoView,
)
from .task_status_views import (
    TaskStatusView,
)
from .email_views import (
    EmailStatusView,
    SendTestEmailView,
    SendBulkNotificationView,
    EmailTemplatePreviewView,
    EmailLogsView,
)

__all__ = [
    'ActivityLogListView',
    'LoginHistoryListView',
    'AuditStatsView',
    'SystemSettingsView',
    'SystemGeneralConfigView',
    'SystemSecurityConfigView',
    'SystemMLConfigView',
    'SystemInfoView',
    'TaskStatusView',
    'EmailStatusView',
    'SendTestEmailView',
    'SendBulkNotificationView',
    'EmailTemplatePreviewView',
    'EmailLogsView',
]

