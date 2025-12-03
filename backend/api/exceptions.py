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


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.
    
    Expected format: {"error": "...", "details": "..."}
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, it's an unhandled exception
    if response is None:
        # Handle Django-specific exceptions
        if isinstance(exc, Http404):
            response = Response(
                {
                    "error": "Resource not found",
                    "details": str(exc) if str(exc) else "The requested resource does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, PermissionDenied):
            response = Response(
                {
                    "error": "Permission denied",
                    "details": str(exc) if str(exc) else "You do not have permission to perform this action"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        elif isinstance(exc, ValidationError):
            response = Response(
                {
                    "error": "Validation error",
                    "details": str(exc) if str(exc) else "Invalid data provided"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            response = Response(
                {
                    "error": "Database integrity error",
                    "details": str(exc) if str(exc) else "A database constraint was violated"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
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
        # If response.data is already in the correct format, keep it
        if isinstance(response.data, dict):
            # Check if it already has 'error' key
            if 'error' not in response.data:
                # Convert DRF error format to our format
                if 'detail' in response.data:
                    response.data = {
                        "error": response.data.get('detail', 'An error occurred'),
                        "details": response.data.get('detail', 'An error occurred')
                    }
                elif 'non_field_errors' in response.data:
                    errors = response.data['non_field_errors']
                    error_msg = errors[0] if isinstance(errors, list) and errors else str(errors)
                    response.data = {
                        "error": error_msg,
                        "details": error_msg
                    }
                else:
                    # Multiple field errors - combine them
                    error_messages = []
                    for key, value in response.data.items():
                        if isinstance(value, list):
                            error_messages.append(f"{key}: {', '.join(str(v) for v in value)}")
                        else:
                            error_messages.append(f"{key}: {str(value)}")
                    
                    error_msg = "; ".join(error_messages) if error_messages else "Validation error"
                    response.data = {
                        "error": error_msg,
                        "details": error_msg
                    }
            # Ensure 'details' exists
            if 'details' not in response.data:
                response.data['details'] = response.data.get('error', 'An error occurred')
    
    return response

