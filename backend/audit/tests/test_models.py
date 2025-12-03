"""
Tests for Audit Models.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from audit.models import ActivityLog, LoginHistory


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestActivityLog:
    """Tests for ActivityLog model."""

    def test_create_activity_log(self, user):
        """Test creating an activity log."""
        log = ActivityLog.objects.create(
            user=user,
            action='image_uploaded',
            resource_type='image',
            resource_id=123,
            details={'filename': 'test.jpg'},
            ip_address='192.168.1.1'
        )
        
        assert log.user == user
        assert log.action == 'image_uploaded'
        assert log.resource_type == 'image'
        assert log.resource_id == 123
        assert log.details == {'filename': 'test.jpg'}

    def test_activity_log_str_representation(self, user):
        """Test string representation."""
        log = ActivityLog.objects.create(
            user=user,
            action='image_uploaded'
        )
        
        assert user.username in str(log)
        assert 'image_uploaded' in str(log)

    def test_details_json_field(self, user):
        """Test details JSON field."""
        details = {'key1': 'value1', 'key2': 123, 'key3': [1, 2, 3]}
        log = ActivityLog.objects.create(
            user=user,
            action='test_action',
            details=details
        )
        
        assert log.details == details

    def test_timestamp_auto_now_add(self, user):
        """Test that timestamp is automatically set."""
        before = timezone.now()
        log = ActivityLog.objects.create(
            user=user,
            action='test_action'
        )
        after = timezone.now()
        
        assert before <= log.timestamp <= after


@pytest.mark.django_db
class TestLoginHistory:
    """Tests for LoginHistory model."""

    def test_create_login_history(self, user):
        """Test creating a login history."""
        history = LoginHistory.objects.create(
            user=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            login_successful=True
        )
        
        assert history.user == user
        assert history.ip_address == '192.168.1.1'
        assert history.login_successful is True

    def test_login_history_str_representation(self, user):
        """Test string representation."""
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True
        )
        
        assert user.username in str(history) or 'Login' in str(history)

    def test_success_alias(self, user):
        """Test success alias for backward compatibility."""
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True
        )
        
        assert history.success is True
        assert history.login_successful is True
        
        history.success = False
        assert history.login_successful is False

    def test_usuario_alias(self, user):
        """Test usuario alias for backward compatibility."""
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True
        )
        
        assert history.usuario == user
        assert history.user == user

    def test_login_time_auto_now_add(self, user):
        """Test that login_time is automatically set."""
        before = timezone.now()
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True
        )
        after = timezone.now()
        
        assert before <= history.login_time <= after

    def test_logout_time(self, user):
        """Test logout_time field."""
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True
        )
        
        assert history.logout_time is None
        
        logout_time = timezone.now()
        history.logout_time = logout_time
        history.save()
        
        assert history.logout_time == logout_time

    def test_session_duration(self, user):
        """Test session_duration field."""
        login_time = timezone.now() - timedelta(hours=2)
        logout_time = timezone.now()
        duration = timedelta(hours=2)
        
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True,
            login_time=login_time,
            logout_time=logout_time,
            session_duration=duration
        )
        
        assert history.session_duration == duration

    def test_login_successful_true(self, user):
        """Test login_successful when True."""
        history = LoginHistory.objects.create(
            user=user,
            login_successful=True
        )
        
        assert history.login_successful is True
        assert history.failure_reason is None or history.failure_reason == ''

    def test_login_successful_false(self, user):
        """Test login_successful when False."""
        history = LoginHistory.objects.create(
            user=user,
            login_successful=False,
            failure_reason='Invalid credentials'
        )
        
        assert history.login_successful is False
        assert history.failure_reason == 'Invalid credentials'

