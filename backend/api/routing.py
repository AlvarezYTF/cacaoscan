"""
Routing de WebSockets para CacaoScan.
"""
from django.urls import re_path
from .consumers import NotificationConsumer, SystemStatusConsumer, AuditConsumer, UserStatsConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/system-status/$', SystemStatusConsumer.as_asgi()),
    re_path(r'ws/audit/(?P<user_id>\w+)/$', AuditConsumer.as_asgi()),
    re_path(r'ws/user-stats/$', UserStatsConsumer.as_asgi()),
]


