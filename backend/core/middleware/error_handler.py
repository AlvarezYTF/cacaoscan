"""
Middleware para estandarizar el formato de errores en CacaoScan.
"""
from django.http import JsonResponse


class StandardErrorMiddleware:
    """
    Middleware que estandariza el formato de errores en toda la aplicación.
    Migrado a patrón nuevo de Django 5.2+ (sin MiddlewareMixin).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """Procesar request y response."""
        response = self.get_response(request)
        return response
    
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



