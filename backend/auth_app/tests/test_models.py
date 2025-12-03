"""
Tests for Auth App Models.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from auth_app.models import EmailVerificationToken, UserProfile


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestEmailVerificationToken:
    """Tests for EmailVerificationToken model."""

    def test_create_email_verification_token(self, user):
        """Test creating an email verification token."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert token.user == user
        assert token.token is not None
        assert token.is_verified is False
        assert token.verified_at is None

    def test_email_verification_token_str_representation(self, user):
        """Test string representation."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert user.email in str(token) or 'Token' in str(token)

    def test_created_alias(self, user):
        """Test created alias for backward compatibility."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert token.created == token.created_at

    def test_is_expired_not_expired(self, user):
        """Test is_expired property when not expired."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert token.is_expired is False

    def test_is_expired_when_verified(self, user):
        """Test is_expired property when verified."""
        token = EmailVerificationToken.objects.create(user=user)
        token.verify()
        
        assert token.is_expired is False

    def test_expires_at_property(self, user):
        """Test expires_at property."""
        token = EmailVerificationToken.objects.create(user=user)
        
        expected_expires = token.created_at + timedelta(hours=24)
        assert abs((token.expires_at - expected_expires).total_seconds()) < 1

    def test_verify_token(self, user):
        """Test verify method."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert token.is_verified is False
        assert token.verified_at is None
        assert user.is_active is True  # User should be active by default
        
        # Make user inactive
        user.is_active = False
        user.save()
        
        token.verify()
        
        assert token.is_verified is True
        assert token.verified_at is not None
        user.refresh_from_db()
        assert user.is_active is True  # Should be activated

    def test_create_for_user_classmethod(self, user):
        """Test create_for_user class method."""
        # Create existing token
        old_token = EmailVerificationToken.objects.create(user=user)
        old_token_id = old_token.id
        
        # Create new token
        new_token = EmailVerificationToken.create_for_user(user)
        
        # Old token should be deleted
        assert not EmailVerificationToken.objects.filter(id=old_token_id).exists()
        assert new_token.user == user
        assert new_token.token != old_token.token

    def test_get_valid_token_classmethod_valid(self, user):
        """Test get_valid_token class method with valid token."""
        token = EmailVerificationToken.objects.create(user=user)
        
        result = EmailVerificationToken.get_valid_token(token.token)
        
        assert result == token

    def test_get_valid_token_classmethod_expired(self, user):
        """Test get_valid_token class method with expired token."""
        token = EmailVerificationToken.objects.create(user=user)
        # Manually set created_at to past
        token.created_at = timezone.now() - timedelta(hours=25)
        token.save()
        
        result = EmailVerificationToken.get_valid_token(token.token)
        
        assert result is None

    def test_get_valid_token_classmethod_not_found(self, user):
        """Test get_valid_token class method with non-existent token."""
        import uuid
        fake_token = uuid.uuid4()
        
        result = EmailVerificationToken.get_valid_token(fake_token)
        
        assert result is None

    def test_unique_token(self, user):
        """Test that token must be unique."""
        token1 = EmailVerificationToken.objects.create(user=user)
        
        # Create another user
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        # Should be able to create token for different user
        token2 = EmailVerificationToken.objects.create(user=other_user)
        
        assert token1.token != token2.token

    def test_one_to_one_relationship(self, user):
        """Test one-to-one relationship with User."""
        token = EmailVerificationToken.objects.create(user=user)
        
        # Should be accessible via related_name
        assert user.auth_email_token == token


@pytest.mark.django_db
class TestUserProfile:
    """Tests for UserProfile model."""

    def test_create_user_profile(self, user):
        """Test creating a user profile."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567',
            region='Antioquia',
            municipality='Medellín',
            farm_name='Finca Test',
            years_experience=10,
            farm_size_hectares=5.5,
            preferred_language='es',
            email_notifications=True
        )
        
        assert profile.user == user
        assert profile.phone_number == '3001234567'
        assert profile.region == 'Antioquia'
        assert profile.farm_name == 'Finca Test'

    def test_user_profile_str_representation(self, user):
        """Test string representation."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        assert user.username in str(profile) or 'Perfil' in str(profile)

    def test_full_name_property(self, user):
        """Test full_name property."""
        user.first_name = 'Juan'
        user.last_name = 'Pérez'
        user.save()
        
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        assert profile.full_name == user.get_full_name()

    def test_full_name_property_fallback(self, user):
        """Test full_name property fallback to username."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        # If no first_name/last_name, should use username
        assert profile.full_name == user.username

    def test_role_property_admin(self, user):
        """Test role property for admin user."""
        user.is_superuser = True
        user.save()
        
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        assert profile.role == 'admin'

    def test_role_property_farmer(self, user):
        """Test role property for regular user."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        assert profile.role == 'farmer'

    def test_preferred_language_default(self, user):
        """Test that preferred_language defaults to 'es'."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        assert profile.preferred_language == 'es'

    def test_email_notifications_default(self, user):
        """Test that email_notifications defaults to True."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        assert profile.email_notifications is True

    def test_one_to_one_relationship(self, user):
        """Test one-to-one relationship with User."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='3001234567'
        )
        
        # Should be accessible via related_name
        assert user.auth_profile == profile

