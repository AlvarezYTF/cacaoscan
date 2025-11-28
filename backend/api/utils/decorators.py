"""
Decorators for API error handling in CacaoScan.
"""
import logging
from functools import wraps
from typing import Callable, Optional, Type, Tuple, Any
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from core.utils import create_error_response

logger = logging.getLogger("cacaoscan.api.decorators")


def handle_api_errors(
    error_message: Optional[str] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    log_message: Optional[str] = None,
    exc_info: bool = True,
    exception_types: Optional[Tuple[Type[Exception], ...]] = None
) -> Callable:
    """
    Decorator that centralizes error handling for API views.
    
    Automatically catches exceptions, logs them, and returns a standardized error response.
    
    Args:
        error_message: Custom error message to return. If None, uses a default message.
        status_code: HTTP status code for the error response. Defaults to 500.
        log_message: Custom log message prefix. If None, uses the function name.
        exc_info: Whether to include exception traceback in logs. Defaults to True.
        exception_types: Tuple of exception types to catch. If None, catches all Exception.
    
    Usage:
        @handle_api_errors(
            error_message="Error procesando imagen",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        def get(self, request):
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Response:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Determine which exceptions to catch
                catch_exceptions = exception_types if exception_types else (Exception,)
                
                # Check if this exception should be caught
                if not isinstance(e, catch_exceptions):
                    raise
                
                # Determine log message
                if log_message:
                    log_msg = f"{log_message}: {e}"
                else:
                    func_name = func.__name__
                    class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'Unknown'
                    log_msg = f"Error in {class_name}.{func_name}: {e}"
                
                # Log the error
                if exc_info:
                    logger.error(log_msg, exc_info=True)
                else:
                    logger.error(log_msg)
                
                # Determine error message
                if error_message:
                    msg = error_message
                else:
                    msg = 'Error interno del servidor'
                
                # If it's an APIException from DRF, use its message and status
                if isinstance(e, APIException):
                    msg = str(e.detail) if hasattr(e, 'detail') else str(e)
                    status_code_override = e.status_code if hasattr(e, 'status_code') else status_code
                else:
                    status_code_override = status_code
                
                # Return standardized error response
                return create_error_response(
                    message=msg,
                    error_type=type(e).__name__,
                    status_code=status_code_override,
                    details={'error': str(e)} if not isinstance(e, APIException) else None
                )
        
        return wrapper
    return decorator

