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

__all__ = [
    'ActivityLogListView',
    'LoginHistoryListView',
    'AuditStatsView',
    'SystemSettingsView',
    'SystemGeneralConfigView',
    'SystemSecurityConfigView',
    'SystemMLConfigView',
    'SystemInfoView',
]

