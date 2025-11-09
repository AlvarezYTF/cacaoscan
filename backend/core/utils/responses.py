"""
Utilidades para crear respuestas estandarizadas de la API.
"""
from rest_framework import status
from rest_framework.response import Response


def create_error_response(message, error_type=None, status_code=400, details=None):
    """
    Función utilitaria para crear respuestas de error estandarizadas.
    
    Args:
        message (str): Mensaje de error descriptivo
        error_type (str, optional): Tipo de error para debugging
        status_code (int): Código de estado HTTP
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
    Función utilitaria para crear respuestas de éxito estandarizadas.
    
    Args:
        message (str): Mensaje de éxito
        data (dict, optional): Datos adicionales
        status_code (int): Código de estado HTTP
    
    Returns:
        Response: Respuesta de éxito estandarizada
    """
    response_data = {
        'success': True,
        'message': message
    }
    
    if data:
        response_data.update(data)
    
    return Response(response_data, status=status_code)



