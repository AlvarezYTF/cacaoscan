"""
Tests for Auth App views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import uuid

from api.models import EmailVerificationToken
from auth_app.models import PendingEmailVerification
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
    TEST_OTHER_USER_USERNAME,
    TEST_USER_EMAIL,
)


class LoginViewTest(APITestCase):
    """Tests for LoginView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password=TEST_USER_PASSWORD,
            is_active=False
        )
        self.url = reverse('auth-login')
    
    def test_login_success(self):
        """Test successful login."""
        login_data = {
            'username': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD
        }
        
        response = self.client.post(self.url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertIn('user', response.data['data'])
    
    def test_login_with_username(self):
        """Test login with username instead of email."""
        login_data = {
            'username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD
        }
        
        response = self.client.post(self.url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            'username': TEST_USER_EMAIL,
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        login_data = {
            'username': TEST_USER_EMAIL
        }
        
        response = self.client.post(self.url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_inactive_user(self):
        """Test login with inactive user."""
        login_data = {
            'username': 'inactive@example.com',
            'password': TEST_USER_PASSWORD
        }
        
        response = self.client.post(self.url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)


class LogoutViewTest(APITestCase):
    """Tests for LogoutView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('auth-logout')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_logout_success(self):
        """Test successful logout."""
        refresh = RefreshToken.for_user(self.user)
        headers = self._get_auth_headers(self.user)
        
        logout_data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(self.url, logout_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_logout_without_refresh_token(self):
        """Test logout without refresh token."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(self.url, {}, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_invalid_token(self):
        """Test logout with invalid refresh token."""
        headers = self._get_auth_headers(self.user)
        
        logout_data = {
            'refresh': 'invalid-token'
        }
        
        response = self.client.post(self.url, logout_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_logout_unauthenticated(self):
        """Test logout without authentication."""
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileViewTest(APITestCase):
    """Tests for UserProfileView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name='Test',
            last_name='User'
        )
        self.url = reverse('auth-profile')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_profile_success(self):
        """Test getting user profile successfully."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], TEST_USER_USERNAME)
        self.assertEqual(response.data['email'], TEST_USER_EMAIL)
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshTokenViewTest(APITestCase):
    """Tests for RefreshTokenView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('auth-refresh-token')
    
    def test_refresh_token_success(self):
        """Test refreshing token successfully."""
        refresh = RefreshToken.for_user(self.user)
        
        refresh_data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(self.url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
    
    def test_refresh_token_missing(self):
        """Test refreshing token without refresh token."""
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_refresh_token_invalid(self):
        """Test refreshing token with invalid refresh token."""
        refresh_data = {
            'refresh': 'invalid-token'
        }
        
        response = self.client.post(self.url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class RegisterViewTest(APITestCase):
    """Tests for RegisterView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('auth-register')
    
    @patch('auth_app.views.auth.registration_views.RegistrationService')
    def test_register_success(self, mock_service):
        """Test successful registration."""
        mock_service_instance = Mock()
        mock_service_instance.register_user_with_email_verification.return_value = Mock(
            success=True,
            message='Usuario registrado exitosamente',
            data={
                'user': {'id': 1},
                'verification_required': True,
                'email': 'newuser@example.com',
                'verification_token': str(uuid.uuid4())
            }
        )
        mock_service.return_value = mock_service_instance
        
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD,
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.url, register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_register_validation_errors(self):
        """Test registration with validation errors."""
        register_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'weak'
        }
        
        response = self.client.post(self.url, register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('auth_app.views.auth.registration_views.RegistrationService')
    def test_register_service_error(self, mock_service):
        """Test registration with service error."""
        mock_service_instance = Mock()
        mock_service_instance.register_user_with_email_verification.return_value = Mock(
            success=False,
            error=Mock(
                message='Email ya existe',
                error_code='email_exists',
                details={}
            )
        )
        mock_service.return_value = mock_service_instance
        
        register_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD
        }
        
        response = self.client.post(self.url, register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class PreRegisterViewTest(APITestCase):
    """Tests for PreRegisterView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('auth-preregister')
    
    @patch('auth_app.views.auth.registration_views.RegistrationService')
    def test_pre_register_success(self, mock_service):
        """Test successful pre-registration."""
        mock_service_instance = Mock()
        mock_service_instance.pre_register_user.return_value = Mock(
            success=True,
            message='Email de verificación enviado',
            data={'email': 'newuser@example.com'}
        )
        mock_service.return_value = mock_service_instance
        
        pre_register_data = {
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.url, pre_register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def test_pre_register_missing_email(self):
        """Test pre-registration with missing email."""
        pre_register_data = {
            'password': TEST_USER_PASSWORD
        }
        
        response = self.client.post(self.url, pre_register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('auth_app.views.auth.registration_views.RegistrationService')
    def test_pre_register_email_exists(self, mock_service):
        """Test pre-registration with existing email."""
        mock_service_instance = Mock()
        mock_service_instance.pre_register_user.return_value = Mock(
            success=False,
            error=Mock(
                message='Email ya existe',
                error_code='email_exists',
                details={}
            )
        )
        mock_service.return_value = mock_service_instance
        
        pre_register_data = {
            'email': 'existing@example.com',
            'password': TEST_USER_PASSWORD
        }
        
        response = self.client.post(self.url, pre_register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class VerifyEmailPreRegistrationViewTest(APITestCase):
    """Tests for VerifyEmailPreRegistrationView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('auth-verify-email-pre-registration', kwargs={'token': 'test-token'})
    
    @patch('auth_app.views.auth.registration_views.RegistrationService')
    def test_verify_pre_registration_success(self, mock_service):
        """Test successful pre-registration verification."""
        mock_service_instance = Mock()
        mock_service_instance.verify_pre_registration_and_create_user.return_value = Mock(
            success=True,
            message='Usuario creado exitosamente',
            data={'user': {'id': 1}}
        )
        mock_service.return_value = mock_service_instance
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_verify_pre_registration_missing_token(self):
        """Test pre-registration verification without token."""
        url = reverse('auth-verify-email-pre-registration', kwargs={'token': None})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('auth_app.views.auth.registration_views.RegistrationService')
    def test_verify_pre_registration_invalid_token(self, mock_service):
        """Test pre-registration verification with invalid token."""
        mock_service_instance = Mock()
        mock_service_instance.verify_pre_registration_and_create_user.return_value = Mock(
            success=False,
            error=Mock(
                message='Token inválido',
                error_code='invalid_token',
                details={}
            )
        )
        mock_service.return_value = mock_service_instance
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ChangePasswordViewTest(APITestCase):
    """Tests for ChangePasswordView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('auth-change-password')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_change_password_success(self):
        """Test changing password successfully."""
        headers = self._get_auth_headers(self.user)
        
        change_data = {
            'old_password': TEST_USER_PASSWORD,
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }
        
        response = self.client.post(self.url, change_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))
    
    def test_change_password_wrong_old_password(self):
        """Test changing password with wrong old password."""
        headers = self._get_auth_headers(self.user)
        
        change_data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }
        
        response = self.client.post(self.url, change_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_change_password_weak_password(self):
        """Test changing password with weak password."""
        headers = self._get_auth_headers(self.user)
        
        change_data = {
            'old_password': TEST_USER_PASSWORD,
            'new_password': 'weak',
            'confirm_password': 'weak'
        }
        
        response = self.client.post(self.url, change_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_change_password_mismatch(self):
        """Test changing password with password mismatch."""
        headers = self._get_auth_headers(self.user)
        
        change_data = {
            'old_password': TEST_USER_PASSWORD,
            'new_password': 'NewPassword123',
            'confirm_password': 'DifferentPassword123'
        }
        
        response = self.client.post(self.url, change_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_change_password_unauthenticated(self):
        """Test changing password without authentication."""
        change_data = {
            'old_password': TEST_USER_PASSWORD,
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }
        
        response = self.client.post(self.url, change_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordViewTest(APITestCase):
    """Tests for ForgotPasswordView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            is_active=True
        )
        self.url = reverse('auth-forgot-password')
    
    @patch('auth_app.views.auth.password_views.send_email_notification')
    def test_forgot_password_success(self, mock_send_email):
        """Test successful forgot password request."""
        mock_send_email.return_value = {'success': True}
        
        forgot_data = {
            'email': TEST_USER_EMAIL
        }
        
        response = self.client.post(self.url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_send_email.assert_called_once()
    
    def test_forgot_password_email_not_found(self):
        """Test forgot password with non-existent email."""
        forgot_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post(self.url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_forgot_password_missing_email(self):
        """Test forgot password without email."""
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_forgot_password_inactive_user(self):
        """Test forgot password with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        forgot_data = {
            'email': TEST_USER_EMAIL
        }
        
        response = self.client.post(self.url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class ResetPasswordViewTest(APITestCase):
    """Tests for ResetPasswordView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.url = reverse('auth-reset-password')
    
    def test_reset_password_success(self):
        """Test successful password reset."""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='password_reset',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        reset_data = {
            'token': str(token.token),
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }
        
        response = self.client.post(self.url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token."""
        reset_data = {
            'token': 'invalid-token',
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }
        
        response = self.client.post(self.url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_reset_password_expired_token(self):
        """Test password reset with expired token."""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='password_reset',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        reset_data = {
            'token': str(token.token),
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }
        
        response = self.client.post(self.url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_reset_password_mismatch(self):
        """Test password reset with password mismatch."""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='password_reset',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        reset_data = {
            'token': str(token.token),
            'new_password': 'NewPassword123',
            'confirm_password': 'DifferentPassword123'
        }
        
        response = self.client.post(self.url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class EmailVerificationViewTest(APITestCase):
    """Tests for EmailVerificationView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            is_active=False
        )
        self.url = reverse('auth-verify-email')
    
    def test_verify_email_post_success(self):
        """Test email verification via POST successfully."""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        verify_data = {
            'token': str(token.token)
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
    
    def test_verify_email_get_success(self):
        """Test email verification via GET successfully."""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        url = reverse('auth-verify-email-token', kwargs={'token': token.token})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token."""
        verify_data = {
            'token': 'invalid-token'
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_email_expired_token(self):
        """Test email verification with expired token."""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='email_verification',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        verify_data = {
            'token': str(token.token)
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_email_already_verified(self):
        """Test email verification for already verified user."""
        self.user.is_active = True
        self.user.save()
        
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token_type='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        verify_data = {
            'token': str(token.token)
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ResendVerificationViewTest(APITestCase):
    """Tests for ResendVerificationView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            is_active=False
        )
        self.url = reverse('auth-resend-verification')
    
    @patch('auth_app.views.auth.email_verification_views.send_email_notification')
    def test_resend_verification_success(self, mock_send_email):
        """Test successful resend verification."""
        mock_send_email.return_value = {'success': True}
        
        resend_data = {
            'email': TEST_USER_EMAIL
        }
        
        response = self.client.post(self.url, resend_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_send_email.assert_called_once()
    
    def test_resend_verification_email_not_found(self):
        """Test resend verification with non-existent email."""
        resend_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post(self.url, resend_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_resend_verification_already_verified(self):
        """Test resend verification for already verified user."""
        self.user.is_active = True
        self.user.save()
        
        resend_data = {
            'email': TEST_USER_EMAIL
        }
        
        response = self.client.post(self.url, resend_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class SendOtpViewTest(APITestCase):
    """Tests for SendOtpView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('auth-send-otp')
    
    @patch('auth_app.views.auth.otp_views.email_service')
    def test_send_otp_success(self, mock_email_service):
        """Test successful OTP sending."""
        mock_email_service.send_email.return_value = {'success': True}
        
        otp_data = {
            'email': 'newuser@example.com'
        }
        
        response = self.client.post(self.url, otp_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(PendingEmailVerification.objects.filter(email='newuser@example.com').exists())
    
    def test_send_otp_rate_limit(self):
        """Test OTP sending with rate limit."""
        PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456',
            last_sent=timezone.now()
        )
        
        otp_data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.url, otp_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.data)
    
    def test_send_otp_invalid_email(self):
        """Test OTP sending with invalid email."""
        otp_data = {
            'email': 'invalid-email'
        }
        
        response = self.client.post(self.url, otp_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class VerifyOtpViewTest(APITestCase):
    """Tests for VerifyOtpView."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('auth-verify-otp')
        self.pending_verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456',
            temp_data={'username': 'testuser', 'password': TEST_USER_PASSWORD}
        )
    
    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        verify_data = {
            'email': 'test@example.com',
            'otp_code': '123456'
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code."""
        verify_data = {
            'email': 'test@example.com',
            'otp_code': '000000'
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_otp_expired_code(self):
        """Test OTP verification with expired code."""
        self.pending_verification.created_at = timezone.now() - timedelta(minutes=11)
        self.pending_verification.save()
        
        verify_data = {
            'email': 'test@example.com',
            'otp_code': '123456'
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_otp_email_not_found(self):
        """Test OTP verification with non-existent email."""
        verify_data = {
            'email': 'nonexistent@example.com',
            'otp_code': '123456'
        }
        
        response = self.client.post(self.url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

