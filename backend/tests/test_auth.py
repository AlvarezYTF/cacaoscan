"""
Tests para el sistema de autenticación de CacaoScan.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


# Helper class for compatibility with old ExpiringToken tests
class ExpiringToken:
    """Wrapper for Token to maintain compatibility with old tests."""
    objects = Token.objects
    
    @staticmethod
    def create_for_user(user):
        """Create or get token for user."""
        token, _ = Token.objects.get_or_create(user=user)
        return token
from django.utils import timezone
from datetime import timedelta

from api.models import EmailVerificationToken, UserProfile
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_EXISTING_USER_PASSWORD,
    TEST_VERIFY_PASSWORD,
    TEST_EXPIRED_PASSWORD,
    TEST_RESEND_PASSWORD,
    TEST_CLEANUP_PASSWORD,
    TEST_FARMER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_INVALID_PASSWORD,
    TEST_WEAK_PASSWORD,
    TEST_DIFFERENT_PASSWORD,
)


class AuthenticationTestCase(APITestCase):
    """
    Tests para el sistema de autenticación.
    """
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.logout_url = reverse('auth-logout')
        self.profile_url = reverse('auth-profile')
        self.verify_email_url = reverse('auth-verify-email')
        self.resend_verification_url = reverse('auth-resend-verification')
        
        # Datos de usuario de prueba
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,  # noqa: S106  # NOSONAR - Test credential from test_constants
            'password_confirm': TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from test_constants
        }
        
        # Usuario existente para tests de login
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        existing_user_credential = TEST_EXISTING_USER_PASSWORD
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password=existing_user_credential,
            first_name='Existing',
            last_name='User'
        )
    
    def test_registration_success(self):
        """Test de registro exitoso."""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertIn('verification_token', response.data)
        
        # Verificar que el usuario fue creado
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        
        # Verificar que se creó el token de verificación
        self.assertTrue(hasattr(user, 'email_verification_token'))
        
        # Verificar que se asignó el rol farmer
        self.assertTrue(user.groups.filter(name='farmer').exists())
    
    def test_registration_validation_errors(self):
        """Test de errores de validación en registro."""
        # Email duplicado
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'existing@example.com'
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Contraseñas que no coinciden
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = TEST_DIFFERENT_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Contraseña débil
        invalid_data = self.user_data.copy()
        invalid_data['password'] = TEST_WEAK_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        invalid_data['password_confirm'] = TEST_WEAK_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_login_success(self):
        """Test de login exitoso."""
        login_data = {
            'username': 'existing@example.com',
            'password': TEST_EXISTING_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertIn('expires_at', response.data)
    
    def test_login_invalid_credentials(self):
        """Test de login con credenciales inválidas."""
        login_data = {
            'username': 'existing@example.com',
            'password': TEST_INVALID_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Credenciales inválidas')
    
    def test_protected_endpoint_access(self):
        """Test de acceso a endpoints protegidos."""
        # Sin autenticación
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Con autenticación
        token = ExpiringToken.create_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_expiration(self):
        """Test de expiración de tokens."""
        # Crear token
        token = ExpiringToken.create_for_user(self.existing_user)
        
        # Simular token expirado
        token.created = timezone.now() - timedelta(hours=25)
        token.save()
        
        # Intentar usar token expirado
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_email_verification(self):
        """Test de verificación de email."""
        # Crear usuario y token de verificación
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        verify_user_credential = TEST_VERIFY_PASSWORD
        user = User.objects.create_user(
            username='verifyuser',
            email='verify@example.com',
            password=verify_user_credential
        )
        verification_token = EmailVerificationToken.create_for_user(user)
        
        # Verificar email
        verify_data = {'token': str(verification_token.token)}
        response = self.client.post(self.verify_email_url, verify_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el token fue marcado como verificado
        verification_token.refresh_from_db()
        self.assertTrue(verification_token.is_verified)
    
    def test_email_verification_expired_token(self):
        """Test de verificación con token expirado."""
        # Crear usuario y token de verificación
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        expired_user_credential = TEST_EXPIRED_PASSWORD
        user = User.objects.create_user(
            username='expireduser',
            email='expired@example.com',
            password=expired_user_credential
        )
        verification_token = EmailVerificationToken.create_for_user(user)
        
        # Simular token expirado
        verification_token.created = timezone.now() - timedelta(hours=25)
        verification_token.save()
        
        # Intentar verificar con token expirado
        verify_data = {'token': str(verification_token.token)}
        response = self.client.post(self.verify_email_url, verify_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_resend_verification(self):
        """Test de reenvío de verificación."""
        # Crear usuario
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        resend_user_credential = TEST_RESEND_PASSWORD
        User.objects.create_user(
            username='resenduser',
            email='resend@example.com',
            password=resend_user_credential
        )
        
        # Solicitar reenvío
        resend_data = {'email': 'resend@example.com'}
        response = self.client.post(self.resend_verification_url, resend_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)
    
    def test_logout(self):
        """Test de logout."""
        # Crear token y autenticar
        token = ExpiringToken.create_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        
        # Hacer logout
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el token fue eliminado
        self.assertFalse(ExpiringToken.objects.filter(key=token.key).exists())


class TokenCleanupTestCase(TestCase):
    """
    Tests para la limpieza automática de tokens.
    """
    
    def setUp(self):
        """Configuración inicial."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_CLEANUP_PASSWORD
        self.user = User.objects.create_user(
            username='cleanupuser',
            email='cleanup@example.com',
            password=user_credential
        )
    
    def test_token_cleanup(self):
        """Test de limpieza de tokens expirados."""
        # Crear tokens
        token1 = ExpiringToken.create_for_user(self.user)
        token2 = ExpiringToken.create_for_user(self.user)
        
        # Simular token expirado
        token1.created = timezone.now() - timedelta(hours=25)
        token1.save()
        
        # Verificar que hay tokens en la base de datos
        self.assertEqual(ExpiringToken.objects.count(), 2)
        
        # Simular limpieza (en producción esto se hace automáticamente)
        expired_tokens = ExpiringToken.objects.filter(
            created__lt=timezone.now() - timedelta(hours=24)
        )
        expired_tokens.delete()
        
        # Verificar que solo queda el token válido
        self.assertEqual(ExpiringToken.objects.count(), 1)
        self.assertEqual(ExpiringToken.objects.first(), token2)


class UserRoleTestCase(TestCase):
    """
    Tests para la asignación automática de roles.
    """
    
    def test_farmer_role_assignment(self):
        """Test de asignación automática del rol farmer."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_FARMER_PASSWORD
        user = User.objects.create_user(
            username='farmeruser',
            email='farmer@example.com',
            password=user_credential
        )
        
        # Verificar que se asignó el rol farmer
        self.assertTrue(user.groups.filter(name='farmer').exists())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_admin_role_no_auto_assignment(self):
        """Test de que usuarios staff no reciben rol farmer."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        admin_user_credential = TEST_ADMIN_PASSWORD
        user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password=admin_user_credential,
            is_staff=True
        )
        
        # Verificar que NO se asignó el rol farmer
        self.assertFalse(user.groups.filter(name='farmer').exists())
        self.assertTrue(user.is_staff)



        self.assertTrue(user.is_staff)


