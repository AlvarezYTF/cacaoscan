"""
Tests for user signals.
"""
import pytest
import os
import sys
from unittest.mock import patch, Mock
from django.contrib.auth.models import User, Group
from django.db.models.signals import pre_save, post_save

from users import signals


@pytest.mark.django_db
class TestUserSignals:
    """Tests for user signals."""
    
    def test_ensure_user_active_during_normal_operation(self):
        """Test that new users are marked as active during normal operation."""
        # Temporarily disable test mode detection
        with patch('users.signals._is_testing', return_value=False):
            user = User(username='testuser', email='test@example.com', is_active=False)
            user._state.adding = True
            
            signals.ensure_user_active(sender=User, instance=user)
            
            assert user.is_active is True
    
    def test_ensure_user_active_during_tests(self):
        """Test that is_active is not forced during tests."""
        with patch('users.signals._is_testing', return_value=True):
            user = User(username='testuser', email='test@example.com', is_active=False)
            user._state.adding = True
            
            signals.ensure_user_active(sender=User, instance=user)
            
            # Should remain False during tests
            assert user.is_active is False
    
    def test_ensure_user_active_existing_user(self):
        """Test that existing users are not modified."""
        with patch('users.signals._is_testing', return_value=False):
            user = User(username='testuser', email='test@example.com', is_active=False)
            user._state.adding = False
            
            signals.ensure_user_active(sender=User, instance=user)
            
            # Should remain False for existing users
            assert user.is_active is False
    
    def test_ensure_user_active_already_active(self):
        """Test that already active users are not modified."""
        with patch('users.signals._is_testing', return_value=False):
            user = User(username='testuser', email='test@example.com', is_active=True)
            user._state.adding = True
            
            signals.ensure_user_active(sender=User, instance=user)
            
            assert user.is_active is True
    
    def test_assign_default_role_new_user(self):
        """Test that new non-staff users are assigned farmer role."""
        # Ensure farmer group exists
        farmer_group, _ = Group.objects.get_or_create(name='farmer')
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123',
            is_staff=False,
            is_superuser=False
        )
        
        # Signal should have been triggered
        assert farmer_group in user.groups.all()
    
    def test_assign_default_role_staff_user(self):
        """Test that staff users are not assigned farmer role."""
        farmer_group, _ = Group.objects.get_or_create(name='farmer')
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'staffuser_{unique_id}',
            email=f'staff_{unique_id}@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=False
        )
        
        # Staff users should not be in farmer group
        assert farmer_group not in user.groups.all()
    
    def test_assign_default_role_superuser(self):
        """Test that superusers are not assigned farmer role."""
        farmer_group, _ = Group.objects.get_or_create(name='farmer')
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_superuser(
            username=f'superuser_{unique_id}',
            email=f'super_{unique_id}@example.com',
            password='testpass123'
        )
        
        # Superusers should not be in farmer group
        assert farmer_group not in user.groups.all()
    
    def test_assign_default_role_existing_user(self):
        """Test that existing users are not assigned farmer role."""
        farmer_group, _ = Group.objects.get_or_create(name='farmer')
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'existinguser_{unique_id}',
            email=f'existing_{unique_id}@example.com',
            password='testpass123',
            is_staff=False,
            is_superuser=False
        )
        
        # Clear groups
        user.groups.clear()
        
        # Update user (not creating)
        user.first_name = 'Updated'
        user.save()
        
        # Should not be assigned farmer role on update
        assert farmer_group not in user.groups.all()
    
    def test_assign_default_role_error_handling(self):
        """Test that errors in role assignment are handled gracefully."""
        with patch('users.signals.Group.objects.get_or_create', side_effect=Exception("Database error")):
            # Should not raise exception
            try:
                import uuid
                unique_id = str(uuid.uuid4())[:8]
                user = User.objects.create_user(
                    username=f'erroruser_{unique_id}',
                    email=f'error_{unique_id}@example.com',
                    password='testpass123',
                    is_staff=False,
                    is_superuser=False
                )
                # If we get here, error was handled
                assert user is not None
            except Exception:
                pytest.fail("Signal should handle errors gracefully")


@pytest.mark.django_db
class TestIsTestingFunction:
    """Tests for _is_testing function."""
    
    def test_is_testing_with_test_in_argv(self):
        """Test _is_testing detects test in sys.argv."""
        original_argv = sys.argv[:]
        try:
            sys.argv = ['manage.py', 'test']
            assert signals._is_testing() is True
        finally:
            sys.argv = original_argv
    
    def test_is_testing_with_pytest_in_modules(self):
        """Test _is_testing detects pytest in modules."""
        with patch('sys.modules', {'pytest': Mock()}):
            assert signals._is_testing() is True
    
    def test_is_testing_with_django_test_mode(self):
        """Test _is_testing detects DJANGO_TEST_MODE environment variable."""
        with patch.dict(os.environ, {'DJANGO_TEST_MODE': '1'}):
            assert signals._is_testing() is True
    
    def test_is_testing_with_pytest_current_test(self):
        """Test _is_testing detects PYTEST_CURRENT_TEST environment variable."""
        with patch.dict(os.environ, {'PYTEST_CURRENT_TEST': 'test_file.py::test_function'}):
            assert signals._is_testing() is True
    
    def test_is_testing_normal_operation(self):
        """Test _is_testing returns False during normal operation."""
        with patch('sys.argv', ['manage.py', 'runserver']):
            with patch('sys.modules', {}):
                with patch.dict(os.environ, {}, clear=True):
                    assert signals._is_testing() is False


