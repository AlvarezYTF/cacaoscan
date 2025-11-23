"""
Response helper functions for CacaoScan API.
"""
from rest_framework import status
from rest_framework.response import Response


def create_error_response(message: str, error_type: str = None, status_code: int = 400, details: dict = None) -> Response:
    """
    Utility function to create standardized error responses.
    
    Args:
        message: Descriptive error message
        error_type: Error type for debugging (optional)
        status_code: HTTP status code
        details: Additional error details (optional)
    
    Returns:
        Response: Standardized error response
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


def create_success_response(message: str, data: dict = None, status_code: int = 200) -> Response:
    """
    Utility function to create standardized success responses.
    
    Args:
        message: Success message
        data: Additional data (optional)
        status_code: HTTP status code
    
    Returns:
        Response: Standardized success response
    """
    response_data = {
        'success': True,
        'message': message
    }
    
    if data:
        response_data.update(data)
    
    return Response(response_data, status=status_code)

