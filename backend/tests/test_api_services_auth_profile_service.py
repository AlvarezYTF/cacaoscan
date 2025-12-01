"""
Unit tests for profile service module (profile_service.py).
Tests user profile retrieval and update functionality.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User

from api.services.auth.profile_service import ProfileService
from api.services.base import ServiceResult, ValidationServiceError


@pytest.fixture
def profile_service():
    """Create a ProfileService instance for testing."""
    return ProfileService()


@pytest.fixture
def django_user(db):
    """Create a real Django user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def django_user_with_profile(db):
    """Create a Django user with UserProfile for testing."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    # Try to create UserProfile if model exists
    try:
        from api.utils.model_imports import get_models_safely
        models = get_models_safely({
            'UserProfile': 'auth_app.models.UserProfile'
        })
        user_profile_model = models.get('UserProfile')
        
        if user_profile_model:
            user_profile_model.objects.create(
                user=user,
                phone_number='1234567890',
                region='Test Region',
                municipality='Test Municipality',
                farm_name='Test Farm',
                years_experience=5,
                farm_size_hectares=10.5,
                preferred_language='es',
                email_notifications=True,
                role='farmer'
            )
    except Exception:
        pass  # UserProfile model may not exist
    
    return user


class TestProfileService:
    """Tests for ProfileService class."""
    
    def test_service_initialization(self, profile_service):
        """Test service initialization."""
        assert profile_service is not None
    
    @patch('api.services.auth.profile_service.get_models_safely')
    def test_get_user_profile_success(self, mock_get_models, profile_service, django_user):
        """Test getting user profile successfully."""
        # Mock UserProfile model
        mock_user_profile_model = Mock()
        mock_profile = Mock()
        mock_profile.phone_number = '1234567890'
        mock_profile.region = 'Test Region'
        mock_profile.municipality = 'Test Municipality'
        mock_profile.farm_name = 'Test Farm'
        mock_profile.years_experience = 5
        mock_profile.farm_size_hectares = 10.5
        mock_profile.preferred_language = 'es'
        mock_profile.email_notifications = True
        mock_profile.role = 'farmer'
        
        # Mock DoesNotExist exception
        class DoesNotExist(Exception):
            pass
        mock_user_profile_model.DoesNotExist = DoesNotExist
        
        # Mock user.profile access
        with patch.object(django_user, 'profile', mock_profile, create=True):
            mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
            
            result = profile_service.get_user_profile(django_user)
            
            assert result.success is True
            assert 'id' in result.data
            assert result.data['username'] == 'testuser'
            assert result.data['email'] == 'test@example.com'
            assert result.data['first_name'] == 'Test'
            assert result.data['last_name'] == 'User'
            assert 'full_name' in result.data
    
    @patch('api.services.auth.profile_service.get_models_safely')
    def test_get_user_profile_no_profile_exists(self, mock_get_models, profile_service, django_user):
        """Test getting user profile when profile doesn't exist."""
        mock_user_profile_model = Mock()
        
        class DoesNotExist(Exception):
            pass
        mock_user_profile_model.DoesNotExist = DoesNotExist
        
        # Simulate profile not existing
        def profile_access():
            raise DoesNotExist()
        
        with patch.object(django_user, 'profile', property(profile_access)):
            # Mock creating profile
            mock_new_profile = Mock()
            mock_new_profile.phone_number = None
            mock_new_profile.region = None
            mock_new_profile.municipality = None
            mock_new_profile.farm_name = None
            mock_new_profile.years_experience = None
            mock_new_profile.farm_size_hectares = None
            mock_new_profile.preferred_language = None
            mock_new_profile.email_notifications = False
            mock_new_profile.role = None
            
            mock_user_profile_model.objects.create.return_value = mock_new_profile
            mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
            
            result = profile_service.get_user_profile(django_user)
            
            assert result.success is True
            assert result.data['username'] == 'testuser'
            # Profile should be created
            mock_user_profile_model.objects.create.assert_called_once()
    
    def test_get_user_profile_exception(self, profile_service, django_user):
        """Test getting user profile when exception occurs."""
        with patch('api.services.auth.profile_service.get_models_safely', side_effect=Exception("Error")):
            result = profile_service.get_user_profile(django_user)
            
            assert result.success is False
            assert result.error is not None
    
    @patch('api.services.auth.profile_service.get_models_safely')
    def test_update_user_profile_success(self, mock_get_models, profile_service, django_user):
        """Test updating user profile successfully."""
        mock_user_profile_model = Mock()
        mock_profile = Mock()
        mock_user_profile_model.objects.get_or_create.return_value = (mock_profile, True)
        mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
        
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '9876543210'
        }
        
        result = profile_service.update_user_profile(django_user, profile_data)
        
        assert result.success is True
        assert result.data['first_name'] == 'Updated'
        assert result.data['last_name'] == 'Name'
        django_user.refresh_from_db()
        assert django_user.first_name == 'Updated'
        assert django_user.last_name == 'Name'
    
    def test_update_user_profile_invalid_field(self, profile_service, django_user):
        """Test updating user profile with invalid field."""
        profile_data = {
            'invalid_field': 'value'
        }
        
        result = profile_service.update_user_profile(django_user, profile_data)
        
        assert result.success is False
        assert 'no permitido' in result.error.message
    
    def test_update_user_profile_duplicate_email(self, profile_service, django_user, db):
        """Test updating user profile with duplicate email."""
        # Create another user with different email
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        profile_data = {
            'email': 'other@example.com'  # Try to use existing email
        }
        
        result = profile_service.update_user_profile(django_user, profile_data)
        
        assert result.success is False
        assert 'ya está registrado' in result.error.message
    
    def test_update_user_profile_same_email(self, profile_service, django_user):
        """Test updating user profile with same email (should succeed)."""
        profile_data = {
            'email': django_user.email  # Same email
        }
        
        with patch('api.services.auth.profile_service.get_models_safely') as mock_get_models:
            mock_user_profile_model = Mock()
            mock_profile = Mock()
            mock_user_profile_model.objects.get_or_create.return_value = (mock_profile, False)
            mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
            
            result = profile_service.update_user_profile(django_user, profile_data)
            
            # Should succeed when email is the same
            assert result.success is True
    
    @patch('api.services.auth.profile_service.get_models_safely')
    def test_update_user_profile_only_user_fields(self, mock_get_models, profile_service, django_user):
        """Test updating only User model fields."""
        profile_data = {
            'first_name': 'New First',
            'last_name': 'New Last'
        }
        
        result = profile_service.update_user_profile(django_user, profile_data)
        
        assert result.success is True
        django_user.refresh_from_db()
        assert django_user.first_name == 'New First'
        assert django_user.last_name == 'New Last'
    
    @patch('api.services.auth.profile_service.get_models_safely')
    def test_update_user_profile_only_profile_fields(self, mock_get_models, profile_service, django_user):
        """Test updating only UserProfile fields."""
        mock_user_profile_model = Mock()
        mock_profile = Mock()
        mock_user_profile_model.objects.get_or_create.return_value = (mock_profile, False)
        mock_get_models.return_value = {'UserProfile': mock_user_profile_model}
        
        profile_data = {
            'phone_number': '1234567890'
        }
        
        result = profile_service.update_user_profile(django_user, profile_data)
        
        assert result.success is True
        # Verify profile was updated
        assert mock_profile.phone_number == '1234567890'
        mock_profile.save.assert_called_once()
    
    def test_update_user_profile_exception(self, profile_service, django_user):
        """Test updating user profile when exception occurs."""
        profile_data = {'first_name': 'Updated'}
        
        with patch.object(django_user, 'save', side_effect=Exception("Database error")):
            result = profile_service.update_user_profile(django_user, profile_data)
            
            assert result.success is False
            assert result.error is not None
    
    def test_check_email_verified_with_token(self, profile_service, django_user):
        """Test checking email verification when token exists."""
        mock_token = Mock()
        mock_token.is_verified = True
        
        with patch.object(django_user, 'auth_email_token', mock_token, create=True):
            is_verified = profile_service._check_email_verified(django_user)
            assert is_verified is True
    
    def test_check_email_verified_no_token(self, profile_service, django_user):
        """Test checking email verification when token doesn't exist."""
        is_verified = profile_service._check_email_verified(django_user)
        # Should fallback to is_active
        assert is_verified == django_user.is_active
    
    def test_check_email_verified_exception(self, profile_service, django_user):
        """Test checking email verification when exception occurs."""
        def token_access():
            raise AttributeError()
        
        with patch.object(django_user, 'auth_email_token', property(token_access), create=True):
            is_verified = profile_service._check_email_verified(django_user)
            # Should fallback to is_active
            assert is_verified == django_user.is_active

