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


def _should_catch_exception(e: Exception, exception_types: Optional[Tuple[Type[Exception], ...]]) -> bool:
    """Determina si la excepción debe ser capturada."""
    catch_exceptions = exception_types if exception_types else (Exception,)
    return isinstance(e, catch_exceptions)

def _build_log_message(e: Exception, log_message: Optional[str], func: Callable, self) -> str:
    """Construye el mensaje de log."""
    if log_message:
        return f"{log_message}: {e}"
    
    func_name = func.__name__
    class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'Unknown'
    return f"Error in {class_name}.{func_name}: {e}"

def _log_error(log_msg: str, exc_info: bool):
    """Registra el error."""
    if exc_info:
        logger.error(log_msg, exc_info=True)
    else:
        logger.error(log_msg)

def _get_error_message_and_status(e: Exception, error_message: Optional[str], status_code: int) -> tuple:
    """Obtiene el mensaje de error y el código de estado."""
    if isinstance(e, APIException):
        msg = str(e.detail) if hasattr(e, 'detail') else str(e)
        status_code_override = e.status_code if hasattr(e, 'status_code') else status_code
    else:
        msg = error_message if error_message else 'Error interno del servidor'
        status_code_override = status_code
    
    return msg, status_code_override

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
                if not _should_catch_exception(e, exception_types):
                    raise
                
                log_msg = _build_log_message(e, log_message, func, self)
                _log_error(log_msg, exc_info)
                
                msg, status_code_override = _get_error_message_and_status(e, error_message, status_code)
                
                return create_error_response(
                    message=msg,
                    error_type=type(e).__name__,
                    status_code=status_code_override,
                    details={'error': str(e)} if not isinstance(e, APIException) else None
                )
        
        return wrapper
    return decorator

