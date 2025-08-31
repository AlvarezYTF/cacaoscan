"""
Sistema de throttling personalizado para CacaoScan.

Define clases de throttling específicas por rol y endpoint
para proteger contra abuso de APIs.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
import time


class BaseRoleThrottle(UserRateThrottle):
    """
    Clase base para throttling por rol de usuario.
    """
    
    def get_cache_key(self, request, view):
        """Genera clave de cache específica por rol."""
        if request.user.is_authenticated:
            ident = f"{request.user.role}:{request.user.id}"
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def get_rate(self):
        """Obtiene la tasa de throttling específica del rol."""
        return getattr(self, 'rate', '60/hour')


class FarmerThrottle(BaseRoleThrottle):
    """
    Throttling para agricultores: 60 requests/hora en general.
    """
    scope = 'farmer'
    rate = '60/hour'


class AnalystThrottle(BaseRoleThrottle):
    """
    Throttling para analistas: 120 requests/hora en general.
    """
    scope = 'analyst'
    rate = '120/hour'


class AdminThrottle(BaseRoleThrottle):
    """
    Throttling para administradores: 300 requests/hora en general.
    """
    scope = 'admin'
    rate = '300/hour'


class PredictionThrottle(UserRateThrottle):
    """
    Throttling específico para predicciones ML.
    Límites más restrictivos por el costo computacional.
    """
    scope = 'prediction'
    
    def get_rate(self):
        """Tasa específica según rol del usuario."""
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            role_rates = {
                'farmer': '30/hour',    # 30 predicciones/hora para agricultores
                'analyst': '60/hour',   # 60 predicciones/hora para analistas
                'admin': '120/hour',    # 120 predicciones/hora para administradores
            }
            return role_rates.get(self.request.user.role, '30/hour')
        return '10/hour'  # Usuarios anónimos muy limitados

    def get_cache_key(self, request, view):
        """Clave de cache específica para predicciones."""
        self.request = request  # Guardar referencia para get_rate()
        
        if request.user.is_authenticated:
            ident = f"prediction:{request.user.role}:{request.user.id}"
        else:
            ident = f"prediction:anon:{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class LoginThrottle(AnonRateThrottle):
    """
    Throttling para intentos de login.
    Protege contra ataques de fuerza bruta.
    """
    scope = 'login'
    rate = '5/min'  # 5 intentos por minuto
    
    def get_cache_key(self, request, view):
        """Clave de cache por IP para login."""
        return f"login_throttle:{self.get_ident(request)}"


class RegistrationThrottle(AnonRateThrottle):
    """
    Throttling para registro de usuarios.
    Previene spam de registros.
    """
    scope = 'registration'
    rate = '3/hour'  # 3 registros por hora por IP
    
    def get_cache_key(self, request, view):
        """Clave de cache por IP para registro."""
        return f"registration_throttle:{self.get_ident(request)}"


class PasswordResetThrottle(AnonRateThrottle):
    """
    Throttling para restablecimiento de contraseñas.
    Previene abuso del sistema de emails.
    """
    scope = 'password_reset'
    rate = '3/hour'  # 3 intentos por hora por IP
    
    def get_cache_key(self, request, view):
        """Clave de cache por IP para reset de password."""
        return f"password_reset_throttle:{self.get_ident(request)}"


class UploadThrottle(UserRateThrottle):
    """
    Throttling para subida de archivos.
    Controla la carga del servidor por uploads.
    """
    scope = 'upload'
    
    def get_rate(self):
        """Tasa específica según rol del usuario."""
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            role_rates = {
                'farmer': '50/hour',    # 50 uploads/hora para agricultores
                'analyst': '100/hour',  # 100 uploads/hora para analistas
                'admin': '200/hour',    # 200 uploads/hora para administradores
            }
            return role_rates.get(self.request.user.role, '50/hour')
        return '5/hour'  # Usuarios anónimos muy limitados

    def get_cache_key(self, request, view):
        """Clave de cache específica para uploads."""
        self.request = request  # Guardar referencia para get_rate()
        
        if request.user.is_authenticated:
            ident = f"upload:{request.user.role}:{request.user.id}"
        else:
            ident = f"upload:anon:{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class BurstThrottle(UserRateThrottle):
    """
    Throttling para ráfagas cortas.
    Permite ráfagas pero controla el abuso.
    """
    scope = 'burst'
    rate = '10/min'  # 10 requests por minuto
    
    def get_cache_key(self, request, view):
        """Clave de cache para control de ráfagas."""
        if request.user.is_authenticated:
            ident = f"burst:{request.user.id}"
        else:
            ident = f"burst:anon:{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class SustainedThrottle(UserRateThrottle):
    """
    Throttling para uso sostenido.
    Control de largo plazo.
    """
    scope = 'sustained'
    rate = '1000/day'  # 1000 requests por día
    
    def get_cache_key(self, request, view):
        """Clave de cache para control sostenido."""
        if request.user.is_authenticated:
            ident = f"sustained:{request.user.id}"
        else:
            ident = f"sustained:anon:{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class CustomThrottleWithMessage:
    """
    Mixin para agregar mensajes personalizados a throttles.
    """
    
    custom_message = _("Has excedido el límite de solicitudes.")
    
    def throttle_failure(self):
        """Personaliza el mensaje de throttling."""
        return self.custom_message


class SmartThrottle(UserRateThrottle):
    """
    Throttling inteligente que ajusta límites según comportamiento.
    """
    scope = 'smart'
    
    def __init__(self):
        super().__init__()
        self.base_rates = {
            'farmer': 60,
            'analyst': 120,
            'admin': 300,
            'anonymous': 20
        }
    
    def get_rate(self):
        """Calcula tasa dinámica según historial del usuario."""
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            user = self.request.user
            base_rate = self.base_rates.get(user.role, 60)
            
            # Ajustar según verificación y actividad
            multiplier = 1.0
            
            if user.is_verified:
                multiplier += 0.5  # +50% para usuarios verificados
            
            # Verificar historial de abuso (simplificado)
            abuse_key = f"abuse_score:{user.id}"
            abuse_score = cache.get(abuse_key, 0)
            
            if abuse_score > 5:
                multiplier -= 0.3  # -30% para usuarios con historial de abuso
            
            final_rate = int(base_rate * multiplier)
            return f"{final_rate}/hour"
        
        return "20/hour"
    
    def get_cache_key(self, request, view):
        """Clave de cache para throttling inteligente."""
        self.request = request  # Guardar referencia para get_rate()
        
        if request.user.is_authenticated:
            ident = f"smart:{request.user.id}"
        else:
            ident = f"smart:anon:{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


# Throttles combinados para diferentes escenarios
class CombinedPredictionThrottle:
    """
    Combina throttling burst y sostenido para predicciones.
    """
    
    def __init__(self):
        self.burst_throttle = BurstThrottle()
        self.prediction_throttle = PredictionThrottle()
    
    def allow_request(self, request, view):
        """Verifica ambos throttles."""
        burst_allowed = self.burst_throttle.allow_request(request, view)
        prediction_allowed = self.prediction_throttle.allow_request(request, view)
        
        return burst_allowed and prediction_allowed
    
    def wait(self):
        """Retorna el tiempo de espera más largo."""
        burst_wait = getattr(self.burst_throttle, 'wait', lambda: None)()
        prediction_wait = getattr(self.prediction_throttle, 'wait', lambda: None)()
        
        if burst_wait and prediction_wait:
            return max(burst_wait, prediction_wait)
        elif burst_wait:
            return burst_wait
        elif prediction_wait:
            return prediction_wait
        
        return None


# Configuración de throttles por endpoint
ENDPOINT_THROTTLES = {
    'login': [LoginThrottle],
    'register': [RegistrationThrottle],
    'password_reset': [PasswordResetThrottle],
    'prediction': [PredictionThrottle, BurstThrottle],
    'upload': [UploadThrottle, BurstThrottle],
    'general': [SmartThrottle, SustainedThrottle],
}

# Throttles por rol
ROLE_THROTTLES = {
    'farmer': [FarmerThrottle, BurstThrottle],
    'analyst': [AnalystThrottle, BurstThrottle],
    'admin': [AdminThrottle, BurstThrottle],
    'anonymous': [AnonRateThrottle],
}
