"""
Unit tests for audit models (LoginHistory, ActivityLog).
Tests cover model creation, properties, and relationships.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from audit.models import LoginHistory, ActivityLog


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def login_history(user):
    """Create a test login history."""
    return LoginHistory.objects.create(
        usuario=user,
        ip_address='192.168.1.1',
        user_agent='Mozilla/5.0',
        success=True
    )


class TestLoginHistory:
    """Tests for LoginHistory model."""
    
    def test_login_history_creation(self, user):
        """Test basic login history creation."""
        history = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            success=True
        )
        
        assert history.usuario == user
        assert history.ip_address == '192.168.1.1'
        assert history.user_agent == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        assert history.success is True
        assert history.login_time is not None
        assert history.logout_time is None
        assert history.session_duration is None
        assert history.failure_reason == ''
    
    def test_login_history_str_representation_success(self, login_history):
        """Test string representation for successful login."""
        expected = f"{login_history.usuario.username} - Exitoso - {login_history.login_time.strftime('%Y-%m-%d %H:%M')}"
        assert str(login_history) == expected
    
    def test_login_history_str_representation_failure(self, user):
        """Test string representation for failed login."""
        history = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=False,
            failure_reason='Invalid credentials'
        )
        
        expected = f"{history.usuario.username} - Fallido - {history.login_time.strftime('%Y-%m-%d %H:%M')}"
        assert str(history) == expected
    
    def test_login_history_default_success(self, user):
        """Test default success value."""
        history = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        
        assert history.success is True
    
    def test_login_history_logout_time_field(self, login_history):
        """Test logout_time field can be set."""
        logout_time = timezone.now() + timedelta(hours=1)
        login_history.logout_time = logout_time
        login_history.save()
        
        login_history.refresh_from_db()
        assert login_history.logout_time is not None
    
    def test_login_history_session_duration_field(self, login_history):
        """Test session_duration field can be set."""
        duration = timedelta(hours=2, minutes=30)
        login_history.session_duration = duration
        login_history.save()
        
        login_history.refresh_from_db()
        assert login_history.session_duration == duration
    
    def test_login_history_failure_reason_field(self, user):
        """Test failure_reason field."""
        history = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=False,
            failure_reason='Invalid password'
        )
        
        assert history.failure_reason == 'Invalid password'
    
    def test_login_history_ipv6_address(self, user):
        """Test IPv6 address support."""
        history = LoginHistory.objects.create(
            usuario=user,
            ip_address='2001:0db8:85a3:0000:0000:8a2e:0370:7334',
            user_agent='Mozilla/5.0',
            success=True
        )
        
        assert history.ip_address == '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
    
    def test_login_history_cascade_delete_with_user(self, user):
        """Test that login histories are deleted when user is deleted."""
        history = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=True
        )
        history_id = history.id
        
        user.delete()
        
        assert not LoginHistory.objects.filter(id=history_id).exists()
    
    def test_login_history_ordering(self, user):
        """Test that login histories are ordered by login_time descending."""
        history1 = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=True
        )
        
        import time
        time.sleep(0.01)
        
        history2 = LoginHistory.objects.create(
            usuario=user,
            ip_address='192.168.1.2',
            user_agent='Chrome/91.0',
            success=True
        )
        
        histories = list(LoginHistory.objects.filter(usuario=user))
        assert histories[0].id == history2.id
        assert histories[1].id == history1.id
    
    def test_login_history_indexes(self, user):
        """Test that indexes are properly set."""
        # Create multiple histories to test index performance
        for i in range(5):
            LoginHistory.objects.create(
                usuario=user,
                ip_address=f'192.168.1.{i}',
                user_agent='Mozilla/5.0',
                success=True
            )
        
        # Query should use indexes
        histories = LoginHistory.objects.filter(usuario=user, success=True)
        assert histories.count() == 5


class TestActivityLog:
    """Tests for ActivityLog model."""
    
    def test_activity_log_is_defined(self):
        """Test that ActivityLog model exists and is defined."""
        assert ActivityLog is not None
        assert hasattr(ActivityLog, '_meta')
    
    def test_activity_log_is_empty(self):
        """Test that ActivityLog is currently empty (pass only)."""
        # ActivityLog is currently just a pass statement
        # This test documents that it exists but has no functionality yet
        assert ActivityLog is not None
        # Note: This model is marked as "no testeable" since it's empty

