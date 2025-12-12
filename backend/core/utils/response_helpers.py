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
        details: Additional error details (optional, can be dict or string)
    
    Returns:
        Response: Standardized error response with format {"error": "...", "details": "..."}
    """
    # For validation errors (dict), provide both structured format and string for compatibility
    if isinstance(details, dict):
        # Format dict details as string for backward compatibility
        details_str = '; '.join([f"{k}: {', '.join(v) if isinstance(v, list) else str(v)}" for k, v in details.items()])
        response_data = {
            'error': message,
            'details': details_str,  # Keep as string for backward compatibility
            'errors': details  # Also provide structured dict for frontend processing
        }
    elif details is None:
        response_data = {
            'error': message,
            'details': message
        }
    else:
        response_data = {
            'error': message,
            'details': str(details)
        }
    
    if error_type:
        response_data['error_type'] = error_type
    
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

