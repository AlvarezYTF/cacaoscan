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
    def fixed_user(self, db):
        """Create test user with unique username."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f"testuser_{unique_id}",
            email=f"testuser_{unique_id}@example.com",
            password="pass123",
            first_name='Test',
            last_name='User'
        )
        # Store original username for assertions that need it
        user._test_username = f"testuser_{unique_id}"
        return user
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_user_profile_success(self, mock_models, service, fixed_user):
        """Test getting user profile successfully."""
        mock_profile = Mock()
        mock_profile.municipio = None
        mock_profile.years_experience = 5
        mock_profile.farm_size_hectares = 10.0
        mock_profile.preferred_language = 'es'
        mock_profile.email_notifications = True
        mock_profile.role = 'farmer'
        
        fixed_user.auth_profile = mock_profile
        
        mock_models.return_value = {'UserProfile': Mock()}
        
        result = service.get_user_profile(fixed_user)
        
        assert result.success
        assert result.data['username'] == fixed_user.username
        assert result.data['email'] == fixed_user.email
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_get_user_profile_no_profile(self, mock_models, service, fixed_user):
        """Test getting user profile when no profile exists."""
        # Create proper DoesNotExist exception
        class MockDoesNotExist(Exception):
            pass
        
        mock_profile_model = Mock()
        mock_profile_model.DoesNotExist = MockDoesNotExist
        mock_profile = Mock(
            municipio=None,
            years_experience=0,
            farm_size_hectares=None,
            preferred_language='es',
            email_notifications=True,
            role='farmer'
        )
        mock_profile_model.objects.create.return_value = mock_profile
        mock_models.return_value = {'UserProfile': mock_profile_model}
        
        # Simulate DoesNotExist exception when accessing fixed_user.auth_profile
        def get_profile():
            raise MockDoesNotExist()
        
        # Mock fixed_user.auth_profile to raise DoesNotExist
        # The service will catch this and create a new profile using user_profile_model.objects.create
        # We need to mock the property descriptor on the User class
        original_auth_profile_descriptor = getattr(type(fixed_user), 'auth_profile', None)
        
        # Create a property that raises DoesNotExist
        def auth_profile_getter(self):
            raise MockDoesNotExist()
        
        # Replace the auth_profile descriptor temporarily
        type(fixed_user).auth_profile = property(auth_profile_getter)
        
        try:
            result = service.get_user_profile(fixed_user)
        finally:
            # Restore original descriptor
            if original_auth_profile_descriptor:
                type(fixed_user).auth_profile = original_auth_profile_descriptor
            elif hasattr(type(fixed_user), 'auth_profile'):
                delattr(type(fixed_user), 'auth_profile')
        
        assert result.success
        assert result.data['username'] == fixed_user.username
    
    @patch('api.utils.model_imports.get_models_safely')
    def test_update_user_profile_success(self, mock_models, service, fixed_user):
        """Test updating user profile successfully."""
        mock_profile_model = Mock()
        mock_profile = Mock()
        mock_profile_model.objects.get_or_create.return_value = (mock_profile, True)
        mock_models.return_value = {'UserProfile': mock_profile_model}
        
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        with patch.object(service, 'get_user_profile', return_value=ServiceResult.success(data={})):
            result = service.update_user_profile(fixed_user, profile_data)
            
            assert result.success
            fixed_user.refresh_from_db()
            assert fixed_user.first_name == 'Updated'
    
    def test_update_user_profile_duplicate_email(self, service, fixed_user):
        """Test updating profile with duplicate email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        other_user = User.objects.create_user(
            username=f'other_{unique_id}',
            email=f'other_{unique_id}@example.com',
            password='testpass123'
        )
        
        profile_data = {'email': other_user.email}
        
        result = service.update_user_profile(fixed_user, profile_data)
        
        assert not result.success
        fixed_user.refresh_from_db()
    
    def test_update_user_profile_invalid_field(self, service, fixed_user):
        """Test updating profile with invalid field."""
        profile_data = {'invalid_field': 'value'}
        
        result = service.update_user_profile(fixed_user, profile_data)
        
        assert not result.success
        fixed_user.refresh_from_db()
    
    def test_check_email_verified_active_user(self, service, fixed_user):
        """Test checking email verification for active user."""
        fixed_user.is_active = True
        fixed_user.save()
        
        result = service._check_email_verified(fixed_user)
        
        assert result is True
    
    def test_check_email_verified_inactive_user(self, service, fixed_user):
        """Test checking email verification for inactive user."""
        fixed_user.is_active = False
        fixed_user.save()
        
        result = service._check_email_verified(fixed_user)
        
        assert result is False

