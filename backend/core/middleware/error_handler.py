"""
Middleware para estandarizar el formato de errores en CacaoScan.
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class StandardErrorMiddleware(MiddlewareMixin):
    """
    Middleware que estandariza el formato de errores en toda la aplicación.
    """
    
    def process_exception(self, request, exception):
        """
        Procesa excepciones no manejadas y las convierte al formato estándar.
        """
        # Solo procesar errores en rutas de API
        if request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor',
                'error_type': 'internal_server_error'
            }, status=500)
        
        return None

