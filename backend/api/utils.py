"""
Middleware para estandarizar el formato de errores en CacaoScan.
"""
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response


class StandardErrorMiddleware(MiddlewareMixin):
    """
    Middleware que estandariza el formato de errores en toda la aplicaciÃ³n.
    """
    
    def process_exception(self, request, exception):
        """
        Procesa excepciones no manejadas y las convierte al formato estÃ¡ndar.
        """
        # Solo procesar errores en rutas de API
        if request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor',
                'error_type': 'internal_server_error'
            }, status=500)
        
        return None


def create_error_response(message, error_type=None, status_code=400, details=None):
    """
    FunciÃ³n utilitaria para crear respuestas de error estandarizadas.
    
    Args:
        message (str): Mensaje de error descriptivo
        error_type (str, optional): Tipo de error para debugging
        status_code (int): CÃ³digo de estado HTTP
        details (dict, optional): Detalles adicionales del error
    
    Returns:
        Response: Respuesta de error estandarizada
    """
    response_data = {
        'success': False,
        'message': message
    }
    
    if error_type:
        response_data['error_type'] = error_type
    
    if details:
        response_data['details'] = details
    
    return Response(response_data, status=status_code)


def create_success_response(message, data=None, status_code=200):
    """
    FunciÃ³n utilitaria para crear respuestas de Ã©xito estandarizadas.
    
    Args:
        message (str): Mensaje de Ã©xito
        data (dict, optional): Datos adicionales
        status_code (int): CÃ³digo de estado HTTP
    
    Returns:
        Response: Respuesta de Ã©xito estandarizada
    """
    response_data = {
        'success': True,
        'message': message
    }
    
    if data:
        response_data.update(data)
    
    return Response(response_data, status=status_code)


