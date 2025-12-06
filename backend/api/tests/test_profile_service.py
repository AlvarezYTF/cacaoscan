"""
Tests for profile service.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from api.services.auth import ProfileService
from api.services.base import ServiceResult


@pytest.mark.django_db
class TestProfileService:
    """Tests for ProfileService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ProfileService()
    
    @pytest.fixture
    def user(self):
        """Create test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_user_profile_success(self, mock_models, service, user):
        """Test getting user profile successfully."""
        mock_profile = Mock()
        mock_profile.phone_number = '1234567890'
        mock_profile.region = 'Test Region'
        mock_profile.municipality = 'Test Municipality'
        mock_profile.farm_name = 'Test Farm'
        mock_profile.years_experience = 5
        mock_profile.farm_size_hectares = 10.0
        mock_profile.preferred_language = 'es'
        mock_profile.email_notifications = True
        mock_profile.role = 'farmer'
        
        user.profile = mock_profile
        
        mock_models.return_value = {'UserProfile': Mock()}
        
        result = service.get_user_profile(user)
        
        assert result.success
        assert result.data['username'] == 'testuser'
        assert result.data['email'] == 'test@example.com'
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_user_profile_no_profile(self, mock_models, service, user):
        """Test getting user profile when no profile exists."""
        # Create proper DoesNotExist exception
        class MockDoesNotExist(Exception):
            pass
        
        mock_profile_model = Mock()
        mock_profile_model.DoesNotExist = MockDoesNotExist
        mock_profile = Mock(
            phone_number=None,
            region=None,
            municipality=None,
            farm_name=None,
            years_experience=0,
            farm_size_hectares=None,
            preferred_language='es',
            email_notifications=True,
            role='farmer'
        )
        mock_profile_model.objects.create.return_value = mock_profile
        mock_models.return_value = {'UserProfile': mock_profile_model}
        
        # Simulate DoesNotExist exception when accessing user.profile
        def get_profile():
            raise MockDoesNotExist()
        
        # Mock user.profile to raise DoesNotExist
        # The service will catch this and create a new profile using user_profile_model.objects.create
        # We need to mock the property descriptor on the User class
        original_profile_descriptor = getattr(type(user), 'profile', None)
        
        # Create a property that raises DoesNotExist
        def profile_getter(self):
            raise MockDoesNotExist()
        
        # Replace the profile descriptor temporarily
        type(user).profile = property(profile_getter)
        
        try:
            result = service.get_user_profile(user)
        finally:
            # Restore original descriptor
            if original_profile_descriptor:
                type(user).profile = original_profile_descriptor
            elif hasattr(type(user), 'profile'):
                delattr(type(user), 'profile')
        
        assert result.success
        assert result.data['username'] == 'testuser'
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_update_user_profile_success(self, mock_models, service, user):
        """Test updating user profile successfully."""
        mock_profile_model = Mock()
        mock_profile = Mock()
        mock_profile_model.objects.get_or_create.return_value = (mock_profile, True)
        mock_models.return_value = {'UserProfile': mock_profile_model}
        
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '1234567890'
        }
        
        with patch.object(service, 'get_user_profile', return_value=ServiceResult.success(data={})):
            result = service.update_user_profile(user, profile_data)
            
            assert result.success
            user.refresh_from_db()
            assert user.first_name == 'Updated'
    
    def test_update_user_profile_duplicate_email(self, service, user):
        """Test updating profile with duplicate email."""
        User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        profile_data = {'email': 'other@example.com'}
        
        result = service.update_user_profile(user, profile_data)
        
        assert not result.success
    
    def test_update_user_profile_invalid_field(self, service, user):
        """Test updating profile with invalid field."""
        profile_data = {'invalid_field': 'value'}
        
        result = service.update_user_profile(user, profile_data)
        
        assert not result.success
    
    def test_check_email_verified_active_user(self, service, user):
        """Test checking email verification for active user."""
        user.is_active = True
        user.save()
        
        result = service._check_email_verified(user)
        
        assert result is True
    
    def test_check_email_verified_inactive_user(self, service, user):
        """Test checking email verification for inactive user."""
        user.is_active = False
        user.save()
        
        result = service._check_email_verified(user)
        
        assert result is False

