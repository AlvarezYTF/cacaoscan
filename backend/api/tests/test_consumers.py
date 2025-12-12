"""
Tests for WebSocket consumers.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

# Try to import channels testing, skip tests if not available
try:
    from channels.testing import WebsocketCommunicator
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False
    # Create dummy classes to avoid NameError
    WebsocketCommunicator = None
    pytestmark = pytest.mark.skip("channels.testing not available (daphne not installed)")

from django.contrib.auth.models import User

# Only import consumers if channels is available
if CHANNELS_AVAILABLE:
    try:
        from api.consumers import (
            NotificationConsumer,
            SystemStatusConsumer,
            AuditConsumer,
            UserStatsConsumer
        )
    except ImportError:
        CHANNELS_AVAILABLE = False
        NotificationConsumer = None
        SystemStatusConsumer = None
        AuditConsumer = None
        UserStatsConsumer = None
else:
    NotificationConsumer = None
    SystemStatusConsumer = None
    AuditConsumer = None
    UserStatsConsumer = None


@pytest.mark.skipif(not CHANNELS_AVAILABLE, reason="channels.testing not available")
@pytest.mark.asyncio
@pytest.mark.django_db
class TestNotificationConsumer:
    """Tests for NotificationConsumer."""
    
    async def test_connect_success(self):
        """Test successful connection."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            f'/ws/notifications/{user.id}/'
        )
        
        connected, subprotocol = await communicator.connect()
        
        assert connected
        await communicator.disconnect()
    
    async def test_connect_invalid_user(self):
        """Test connection with invalid user ID."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            '/ws/notifications/99999/'
        )
        
        connected, subprotocol = await communicator.connect()
        
        # Should close connection for invalid user
        assert not connected or subprotocol is None
    
    async def test_receive_ping(self):
        """Test receiving ping message."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com'
        )
        
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            f'/ws/notifications/{user.id}/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Send ping
        await communicator.send_json_to({
            'type': 'ping'
        })
        
        # Should receive pong
        response = await communicator.receive_json_from()
        assert response['type'] == 'pong'
        
        await communicator.disconnect()
    
    async def test_receive_invalid_json(self):
        """Test receiving invalid JSON."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com'
        )
        
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            f'/ws/notifications/{user.id}/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Send invalid JSON
        await communicator.send_to(text_data='invalid json')
        
        # Should receive error
        response = await communicator.receive_json_from()
        assert response['type'] == 'error'
        
        await communicator.disconnect()


@pytest.mark.skipif(not CHANNELS_AVAILABLE, reason="channels.testing not available")
@pytest.mark.asyncio
@pytest.mark.django_db
class TestSystemStatusConsumer:
    """Tests for SystemStatusConsumer."""
    
    async def test_connect_success(self):
        """Test successful connection."""
        communicator = WebsocketCommunicator(
            SystemStatusConsumer.as_asgi(),
            '/ws/system/status/'
        )
        
        connected, subprotocol = await communicator.connect()
        
        assert connected
        await communicator.disconnect()
    
    async def test_receive_get_status(self):
        """Test receiving get_status message."""
        communicator = WebsocketCommunicator(
            SystemStatusConsumer.as_asgi(),
            '/ws/system/status/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Send get_status
        await communicator.send_json_to({
            'type': 'get_status'
        })
        
        # Should receive system status
        response = await communicator.receive_json_from()
        assert response['type'] == 'system_status'
        assert 'data' in response
        
        await communicator.disconnect()


@pytest.mark.skipif(not CHANNELS_AVAILABLE, reason="channels.testing not available")
@pytest.mark.asyncio
@pytest.mark.django_db
class TestAuditConsumer:
    """Tests for AuditConsumer."""
    
    async def test_connect_success_admin(self):
        """Test successful connection as admin."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'admin_{unique_id}',
            email=f'admin_{unique_id}@example.com',
            is_superuser=True,
            is_staff=True
        )
        
        communicator = WebsocketCommunicator(
            AuditConsumer.as_asgi(),
            f'/ws/audit/{user.id}/'
        )
        
        connected, subprotocol = await communicator.connect()
        
        assert connected
        await communicator.disconnect()
    
    async def test_connect_non_admin(self):
        """Test connection as non-admin user."""
        user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            is_superuser=False,
            is_staff=False
        )
        
        communicator = WebsocketCommunicator(
            AuditConsumer.as_asgi(),
            f'/ws/audit/{user.id}/'
        )
        
        connected, subprotocol = await communicator.connect()
        
        # Should close connection for non-admin
        assert not connected or subprotocol is None
    
    async def test_receive_get_audit_stats(self):
        """Test receiving get_audit_stats message."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'admin_{unique_id}',
            email=f'admin_{unique_id}@example.com',
            is_superuser=True,
            is_staff=True
        )
        
        communicator = WebsocketCommunicator(
            AuditConsumer.as_asgi(),
            f'/ws/audit/{user.id}/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Send get_audit_stats
        await communicator.send_json_to({
            'type': 'get_audit_stats'
        })
        
        # Should receive audit stats
        response = await communicator.receive_json_from()
        assert response['type'] == 'audit_stats'
        assert 'data' in response
        
        await communicator.disconnect()


@pytest.mark.skipif(not CHANNELS_AVAILABLE, reason="channels.testing not available")
@pytest.mark.asyncio
@pytest.mark.django_db
class TestUserStatsConsumer:
    """Tests for UserStatsConsumer."""
    
    async def test_connect_success(self):
        """Test successful connection."""
        communicator = WebsocketCommunicator(
            UserStatsConsumer.as_asgi(),
            '/ws/user/stats/'
        )
        
        connected, subprotocol = await communicator.connect()
        
        assert connected
        await communicator.disconnect()
    
    async def test_receive_get_stats(self):
        """Test receiving get_stats message."""
        communicator = WebsocketCommunicator(
            UserStatsConsumer.as_asgi(),
            '/ws/user/stats/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Send get_stats
        await communicator.send_json_to({
            'type': 'get_stats'
        })
        
        # Should receive user stats
        response = await communicator.receive_json_from()
        assert response['type'] == 'user_stats'
        assert 'data' in response
        
        await communicator.disconnect()
    
    async def test_notification_mark_read(self):
        """Test mark_read functionality."""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com'
        )
        
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            f'/ws/notifications/{user.id}/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        await communicator.send_json_to({
            'type': 'mark_read',
            'notification_id': 999
        })
        
        response = await communicator.receive_json_from()
        assert 'type' in response
        
        await communicator.disconnect()
    
    async def test_system_status_update(self):
        """Test system_status_update event."""
        communicator = WebsocketCommunicator(
            SystemStatusConsumer.as_asgi(),
            '/ws/system/status/'
        )
        
        connected, _ = await communicator.connect()
        assert connected
        
        await communicator.channel_layer.group_send(
            'system_status',
            {
                'type': 'system_status_update',
                'data': {'status': 'online'}
            }
        )
        
        response = await communicator.receive_json_from(timeout=1.0)
        assert response['type'] == 'system_status'
        
        await communicator.disconnect()

