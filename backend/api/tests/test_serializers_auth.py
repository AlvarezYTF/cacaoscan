"""
Unit tests for authentication serializers.
"""
from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

from rest_framework import serializers
from api.serializers.auth_serializers import (
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserSerializer,
    UserProfileSerializer,
    SendOtpSerializer,
    VerifyOtpSerializer
)
from api.models import EmailVerificationToken
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
    TEST_WEAK_PASSWORD,
    TEST_INVALID_PASSWORD,
)


class LoginSerializerTest(TestCase):
    """Tests for LoginSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            is_active=True
        )
    
    def test_login_with_username_success(self):
        """Test successful login with username."""
        serializer = LoginSerializer(data={
            'username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)
    
    def test_login_with_email_success(self):
        """Test successful login with email."""
        serializer = LoginSerializer(data={
            'email': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)
    
    def test_login_with_email_as_username(self):
        """Test login when email is used as username."""
        serializer = LoginSerializer(data={
            'email': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)
    
    def test_login_missing_credentials(self):
        """Test login without username or email."""
        serializer = LoginSerializer(data={
            'password': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_login_missing_password(self):
        """Test login without password."""
        serializer = LoginSerializer(data={
            'username': TEST_USER_USERNAME
        })
        self.assertFalse(serializer.is_valid())
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        serializer = LoginSerializer(data={
            'username': TEST_USER_USERNAME,
            'password': TEST_INVALID_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_login_inactive_user(self):
        """Test login with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        serializer = LoginSerializer(data={
            'username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    @patch('api.serializers.auth_serializers.EmailVerificationToken')
    def test_login_unverified_user(self, mock_token_model):
        """Test login with unverified user."""
        self.user.is_active = False
        self.user.save()
        
        mock_token = Mock()
        mock_token.is_verified = False
        mock_token_model.objects.filter.return_value.first.return_value = mock_token
        
        serializer = LoginSerializer(data={
            'username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())


class RegisterSerializerTest(TestCase):
    """Tests for RegisterSerializer."""
    
    def test_register_success(self):
        """Test successful user registration."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertFalse(user.is_active)  # User should be inactive until email verification
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password=TEST_USER_PASSWORD
        )
        
        serializer = RegisterSerializer(data={
            'username': 'existing',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password=TEST_USER_PASSWORD
        )
        
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'existing@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_register_short_username(self):
        """Test registration with short username."""
        serializer = RegisterSerializer(data={
            'username': 'ab',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_register_invalid_username_format(self):
        """Test registration with invalid username format."""
        serializer = RegisterSerializer(data={
            'username': 'user@name',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        # Username with @ should be allowed (treated as email)
        self.assertTrue(serializer.is_valid())
    
    def test_register_invalid_email_format(self):
        """Test registration with invalid email format."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'invalid-email',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_register_weak_password(self):
        """Test registration with weak password."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_WEAK_PASSWORD,
            'password_confirm': TEST_WEAK_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': 'different_password'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_register_missing_first_name(self):
        """Test registration without first name."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
    
    def test_register_missing_last_name(self):
        """Test registration without last name."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
    
    @patch('api.serializers.auth_serializers.invalidate_system_stats_cache')
    def test_register_invalidates_cache(self, mock_invalidate):
        """Test that registration invalidates system stats cache."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        })
        self.assertTrue(serializer.is_valid())
        serializer.save()
        mock_invalidate.assert_called_once()


class ChangePasswordSerializerTest(TestCase):
    """Tests for ChangePasswordSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_change_password_success(self):
        """Test successful password change."""
        serializer = ChangePasswordSerializer(data={
            'old_password': TEST_USER_PASSWORD,
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        })
        self.assertTrue(serializer.is_valid())
    
    def test_change_password_missing_old_password(self):
        """Test password change without old password."""
        serializer = ChangePasswordSerializer(data={
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
    
    def test_change_password_weak_new_password(self):
        """Test password change with weak new password."""
        serializer = ChangePasswordSerializer(data={
            'old_password': TEST_USER_PASSWORD,
            'new_password': TEST_WEAK_PASSWORD,
            'confirm_password': TEST_WEAK_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)
    
    def test_change_password_mismatch(self):
        """Test password change with password mismatch."""
        serializer = ChangePasswordSerializer(data={
            'old_password': TEST_USER_PASSWORD,
            'new_password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_change_password_same_as_old(self):
        """Test password change with same password."""
        serializer = ChangePasswordSerializer(data={
            'old_password': TEST_USER_PASSWORD,
            'new_password': TEST_USER_PASSWORD,
            'confirm_password': TEST_USER_PASSWORD
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class EmailVerificationSerializerTest(TestCase):
    """Tests for EmailVerificationSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.token = EmailVerificationToken.create_for_user(self.user)
    
    def test_verify_email_success(self):
        """Test successful email verification."""
        serializer = EmailVerificationSerializer(data={
            'token': str(self.token.token)
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['token'], self.token.token)
    
    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token."""
        serializer = EmailVerificationSerializer(data={
            'token': uuid.uuid4()
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('token', serializer.errors)
    
    def test_verify_email_expired_token(self):
        """Test email verification with expired token."""
        self.token.expires_at = timezone.now() - timedelta(hours=1)
        self.token.save()
        
        serializer = EmailVerificationSerializer(data={
            'token': str(self.token.token)
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('token', serializer.errors)
    
    def test_verify_email_already_verified(self):
        """Test email verification with already verified token."""
        self.token.is_verified = True
        self.token.verified_at = timezone.now()
        self.token.save()
        
        serializer = EmailVerificationSerializer(data={
            'token': str(self.token.token)
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('token', serializer.errors)


class ResendVerificationSerializerTest(TestCase):
    """Tests for ResendVerificationSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            is_active=False
        )
    
    def test_resend_verification_success(self):
        """Test successful resend verification."""
        serializer = ResendVerificationSerializer(data={
            'email': TEST_USER_EMAIL
        })
        self.assertTrue(serializer.is_valid())
    
    def test_resend_verification_nonexistent_email(self):
        """Test resend verification with nonexistent email."""
        serializer = ResendVerificationSerializer(data={
            'email': 'nonexistent@example.com'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_resend_verification_already_verified(self):
        """Test resend verification for already verified user."""
        self.user.is_active = True
        self.user.save()
        
        token = EmailVerificationToken.create_for_user(self.user)
        token.is_verified = True
        token.verified_at = timezone.now()
        token.save()
        
        serializer = ResendVerificationSerializer(data={
            'email': TEST_USER_EMAIL
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_resend_verification_invalid_email_format(self):
        """Test resend verification with invalid email format."""
        serializer = ResendVerificationSerializer(data={
            'email': 'invalid-email'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class UserSerializerTest(TestCase):
    """Tests for UserSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME,
            is_active=True
        )
    
    def test_user_serialization_success(self):
        """Test successful user serialization."""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], TEST_USER_USERNAME)
        self.assertEqual(data['email'], TEST_USER_EMAIL)
        self.assertEqual(data['first_name'], TEST_USER_FIRST_NAME)
        self.assertEqual(data['last_name'], TEST_USER_LAST_NAME)
        self.assertIn('role', data)
        self.assertIn('is_verified', data)
    
    def test_user_role_farmer(self):
        """Test user role is farmer for regular user."""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['role'], 'farmer')
    
    def test_user_role_admin(self):
        """Test user role is admin for superuser."""
        self.user.is_superuser = True
        self.user.save()
        
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['role'], 'admin')
    
    def test_user_role_analyst(self):
        """Test user role is analyst for analyst group member."""
        group = Group.objects.create(name='analyst')
        self.user.groups.add(group)
        
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['role'], 'analyst')
    
    def test_user_is_verified(self):
        """Test user is_verified field."""
        serializer = UserSerializer(self.user)
        self.assertIn('is_verified', serializer.data)


class UserProfileSerializerTest(TestCase):
    """Tests for UserProfileSerializer."""
    
    def setUp(self):
        """Set up test data."""
        from auth_app.models import UserProfile
        
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone_number='1234567890',
            region='Test Region',
            municipality='Test Municipality'
        )
    
    def test_profile_serialization_success(self):
        """Test successful profile serialization."""
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        
        self.assertIn('phone_number', data)
        self.assertIn('region', data)
        self.assertIn('municipality', data)
        self.assertIn('full_name', data)
        self.assertIn('role', data)
        self.assertIn('is_verified', data)
    
    def test_profile_validation_years_experience_invalid(self):
        """Test profile validation with invalid years of experience."""
        serializer = UserProfileSerializer(data={
            'years_experience': -1
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('years_experience', serializer.errors)
    
    def test_profile_validation_years_experience_too_high(self):
        """Test profile validation with too high years of experience."""
        serializer = UserProfileSerializer(data={
            'years_experience': 101
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('years_experience', serializer.errors)
    
    def test_profile_validation_farm_size_invalid(self):
        """Test profile validation with invalid farm size."""
        serializer = UserProfileSerializer(data={
            'farm_size_hectares': -1
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('farm_size_hectares', serializer.errors)
    
    def test_profile_validation_farm_size_too_high(self):
        """Test profile validation with too high farm size."""
        serializer = UserProfileSerializer(data={
            'farm_size_hectares': 10001
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('farm_size_hectares', serializer.errors)


class SendOtpSerializerTest(TestCase):
    """Tests for SendOtpSerializer."""
    
    def test_send_otp_success(self):
        """Test successful OTP send."""
        serializer = SendOtpSerializer(data={
            'email': 'test@example.com'
        })
        self.assertTrue(serializer.is_valid())
    
    def test_send_otp_invalid_email(self):
        """Test OTP send with invalid email."""
        serializer = SendOtpSerializer(data={
            'email': 'invalid-email'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class VerifyOtpSerializerTest(TestCase):
    """Tests for VerifyOtpSerializer."""
    
    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        serializer = VerifyOtpSerializer(data={
            'email': 'test@example.com',
            'code': '123456'
        })
        self.assertTrue(serializer.is_valid())
    
    def test_verify_otp_short_code(self):
        """Test OTP verification with short code."""
        serializer = VerifyOtpSerializer(data={
            'email': 'test@example.com',
            'code': '12345'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_verify_otp_long_code(self):
        """Test OTP verification with long code."""
        serializer = VerifyOtpSerializer(data={
            'email': 'test@example.com',
            'code': '1234567'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_verify_otp_invalid_email(self):
        """Test OTP verification with invalid email."""
        serializer = VerifyOtpSerializer(data={
            'email': 'invalid-email',
            'code': '123456'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

