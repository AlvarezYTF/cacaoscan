"""
Tests para el sistema de autenticación de CacaoScan.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

from api.models import EmailVerificationToken, UserProfile


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
            'password': 'TestPass123',
            'password_confirm': 'TestPass123'
        }
        
        # Usuario existente para tests de login
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123',
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
        invalid_data['password_confirm'] = 'DifferentPass123'
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Contraseña débil
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'weak'
        invalid_data['password_confirm'] = 'weak'
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_login_success(self):
        """Test de login exitoso."""
        login_data = {
            'username': 'existing@example.com',
            'password': 'ExistingPass123'
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
            'password': 'WrongPassword'
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
        user = User.objects.create_user(
            username='verifyuser',
            email='verify@example.com',
            password='VerifyPass123'
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
        user = User.objects.create_user(
            username='expireduser',
            email='expired@example.com',
            password='ExpiredPass123'
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
        user = User.objects.create_user(
            username='resenduser',
            email='resend@example.com',
            password='ResendPass123'
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
        self.user = User.objects.create_user(
            username='cleanupuser',
            email='cleanup@example.com',
            password='CleanupPass123'
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
        user = User.objects.create_user(
            username='farmeruser',
            email='farmer@example.com',
            password='FarmerPass123'
        )
        
        # Verificar que se asignó el rol farmer
        self.assertTrue(user.groups.filter(name='farmer').exists())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_admin_role_no_auto_assignment(self):
        """Test de que usuarios staff no reciben rol farmer."""
        user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='AdminPass123',
            is_staff=True
        )
        
        # Verificar que NO se asignó el rol farmer
        self.assertFalse(user.groups.filter(name='farmer').exists())
        self.assertTrue(user.is_staff)
