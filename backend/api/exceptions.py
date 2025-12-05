"""
Global exception handler for DRF API.
Ensures consistent error response format across all endpoints.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError

logger = logging.getLogger("cacaoscan.api.exceptions")

# Constants for error messages
ERROR_MSG_DEFAULT = "An error occurred"


def _handle_django_exception(exc):
    """Handle Django-specific exceptions."""
    if isinstance(exc, Http404):
        return Response(
            {
                "error": "Resource not found",
                "details": str(exc) if str(exc) else "The requested resource does not exist"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "error": "Permission denied",
                "details": str(exc) if str(exc) else "You do not have permission to perform this action"
            },
            status=status.HTTP_403_FORBIDDEN
        )
    if isinstance(exc, ValidationError):
        return Response(
            {
                "error": "Validation error",
                "details": str(exc) if str(exc) else "Invalid data provided"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if isinstance(exc, IntegrityError):
        return Response(
            {
                "error": "Database integrity error",
                "details": str(exc) if str(exc) else "A database constraint was violated"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    return None


def _convert_drf_error_format(response_data):
    """Convert DRF error format to our standard format."""
    if 'detail' in response_data:
        detail = response_data.get('detail', ERROR_MSG_DEFAULT)
        return {"error": detail, "details": detail}
    
    if 'non_field_errors' in response_data:
        errors = response_data['non_field_errors']
        error_msg = errors[0] if isinstance(errors, list) and errors else str(errors)
        return {"error": error_msg, "details": error_msg}
    
    # Multiple field errors - combine them
    error_messages = []
    for key, value in response_data.items():
        if isinstance(value, list):
            error_messages.append(f"{key}: {', '.join(str(v) for v in value)}")
        else:
            error_messages.append(f"{key}: {str(value)}")
    
    error_msg = "; ".join(error_messages) if error_messages else "Validation error"
    return {"error": error_msg, "details": error_msg}


def _normalize_error_format(response):
    """Ensure response has consistent error format."""
    if not isinstance(response.data, dict):
        return
    
    if 'error' not in response.data:
        response.data = _convert_drf_error_format(response.data)
    
    if 'details' not in response.data:
        response.data['details'] = response.data.get('error', ERROR_MSG_DEFAULT)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.
    
    Expected format: {"error": "...", "details": "..."}
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it's an unhandled exception
    if response is None:
        response = _handle_django_exception(exc)
        if response is None:
            # Unhandled exception - log it but don't expose details
            logger.exception(f"Unhandled exception: {exc}")
            response = Response(
                {
                    "error": "Internal server error",
                    "details": "An unexpected error occurred. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Ensure consistent error format
    if response is not None:
        _normalize_error_format(response)
    
    return response

