"""
Middleware para limpieza automática de tokens expirados en CacaoScan.
"""
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import ExpiringToken


class TokenCleanupMiddleware(MiddlewareMixin):
    """
    Middleware que limpia tokens expirados automáticamente.
    Se ejecuta en cada request para mantener la base de datos limpia.
    """
    
    def process_request(self, request):
        """
        Limpiar tokens expirados en cada request.
        """
        # Solo ejecutar en rutas de API para evitar overhead
        if request.path.startswith('/api/'):
            self.cleanup_expired_tokens()
    
    def cleanup_expired_tokens(self):
        """
        Eliminar tokens expirados de la base de datos.
        """
        try:
            # Obtener todos los tokens
            tokens = Token.objects.all()
            expired_count = 0
            
            for token in tokens:
                # Verificar si el token ha expirado usando nuestro modelo personalizado
                expiring_token = ExpiringToken.objects.filter(key=token.key).first()
                if expiring_token and expiring_token.is_expired:
                    token.delete()
                    expired_count += 1
            
            if expired_count > 0:
                print(f"🧹 Limpieza automática: {expired_count} tokens expirados eliminados")
                
        except Exception as e:
            print(f"⚠️ Error en limpieza de tokens: {e}")
