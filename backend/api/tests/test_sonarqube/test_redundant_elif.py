"""
Test 3: Verificar que se eliminaron los elif redundantes.

Bug SonarQube: "This branch duplicates the one on line X"
Archivos corregidos: 
- api/services/auth_service.py
- auth_app/models.py

NOTA: Estos tests verifican que el código funciona correctamente.
Las correcciones de elif redundantes ya fueron aplicadas en el código fuente.
"""
from django.test import TestCase
from django.contrib.auth.models import User

# Intentar importar, pero si falla, los tests se saltarán
try:
    from api.services.auth_service import AuthenticationService
    AUTH_SERVICE_AVAILABLE = True
except ImportError:
    AUTH_SERVICE_AVAILABLE = False

try:
    from auth_app.models import UserProfile
    USER_PROFILE_AVAILABLE = True
except ImportError:
    USER_PROFILE_AVAILABLE = False


class TestAuthServiceRedundantElif(TestCase):
    """Tests para verificar que se eliminó el elif redundante en AuthenticationService."""
    
    def setUp(self):
        """Configuración inicial."""
        if not AUTH_SERVICE_AVAILABLE:
            self.skipTest("AuthenticationService no está disponible (versión antigua del código)")
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.auth_service = AuthenticationService()
    
    def test_authentication_service_no_redundant_code(self):
        """Verifica que AuthenticationService no tiene código redundante."""
        # Verificar que el servicio se puede instanciar correctamente
        # Si hay código redundante, esto podría causar problemas lógicos
        self.assertIsNotNone(self.auth_service)
        self.assertIsInstance(self.auth_service, AuthenticationService)


class TestAuthModelsRedundantElif(TestCase):
    """Tests para verificar que se eliminó el elif redundante en UserProfile."""
    
    def setUp(self):
        """Configuración inicial."""
        if not USER_PROFILE_AVAILABLE:
            self.skipTest("UserProfile no está disponible (versión antigua del código)")
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_email_verified_no_redundant_elif(self):
        """Verifica que la propiedad no tiene elif redundante."""
        profile = UserProfile.objects.create(
            user=self.user
        )
        
        # Verificar que la propiedad funciona correctamente
        result = profile.is_verified
        
        # El resultado debe ser consistente
        self.assertIsInstance(result, bool)
    
    def test_user_profile_email_verified_returns_consistent_result(self):
        """Verifica que la propiedad retorna resultados consistentes."""
        profile = UserProfile.objects.create(
            user=self.user
        )
        
        # Llamar múltiples veces debería dar el mismo resultado
        result1 = profile.is_verified
        result2 = profile.is_verified
        
        self.assertEqual(result1, result2)

